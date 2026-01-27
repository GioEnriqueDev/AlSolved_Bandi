"""
analyze_gemini.py - High-Speed Grant Analysis using Gemini 1.5 Flash
====================================================================
Leverages Google Gemini 1.5 Flash for massive parallel processing of grant data.

Key Advantages:
- Extremely fast (processing 30-50 concurrent requests)
- Large context window
- Cost-effective (Free tier available)
"""

import json
import logging
import asyncio
import os
import re
import sys
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from scraper.models import init_db, Bando, ProcessingStatus
import google.generativeai as genai
from dotenv import load_dotenv

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

# Load Env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("GEMINI_API_KEY not found in .env file")
    sys.exit(1)

genai.configure(api_key=API_KEY)

# Configuration
MODEL_NAME = "gemini-1.5-flash"
CONCURRENCY_LIMIT = 50 

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Models to try in order of preference/speed
MODELS = ["gemini-1.5-flash", "gemini-1.5-flash-001", "gemini-1.5-flash-002", "gemini-2.0-flash-exp"]

async def analyze_bando_async(bando_data: Dict[str, Any], semaphore: asyncio.Semaphore) -> Dict[str, Any]:
    """Analyzes a single bando using Gemini Async API."""
    async with semaphore:
        # Try models until one works
        last_error = None
        for model_name in MODELS:
            try:
                model = genai.GenerativeModel(model_name)
                
                # Safe ascii handling for logging
                title_log = bando_data['title'].encode('ascii', 'ignore').decode('ascii')
                
                context = f"Titolo: {bando_data['title']}\n"
                context += f"Descrizione: {str(bando_data['description'])[:3000]}\n"
                context += f"HTML: {str(bando_data['html'])[:3000]}\n"

                # Prompt totally in simple ASCII text to avoid source code encoding issues
                prompt = """
                Sei un analista finanziario AI. Analizza questo bando e restituisci JSON puro.
                
                INPUT:
                See above context.
                
                OUTPUT OBBLIGATORIO (JSON):
                {
                    "marketing_text": "Frase persuasiva max 20 parole (usa emoji se appropriato) e vantaggio economico",
                    "titolo_riassuntivo": "Titolo breve per card (max 10 parole)",
                    "sintesi": "Descrizione sintetica chiara (max 40 parole)",
                    "regioni": ["Italia", "Lombardia"], 
                    "scadenza": "YYYY-MM-DD" o "A sportello" or "N/A",
                    "financial_max": 50000 (intero, null se non trovato),
                    "is_gold": true (se fondo perduto o importo > 10k),
                    "ateco_codes": "codici se presenti o null"
                }
                """
                
                full_prompt = prompt + "\nDATI:\n" + context

                # Using run_in_executor for standard blocking generation if async not native 
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: model.generate_content(full_prompt, generation_config={"response_mime_type": "application/json"})
                )
                
                result_json = json.loads(response.text)
                return {"id": bando_data["id"], "success": True, "data": result_json}
                
            except Exception as e:
                # If it's a 4xx error (model not found), try next. If 429 (Resource Exhausted), maybe also wait/next?
                # We'll log and continue
                # logger.warning(f"Model {model_name} failed for {bando_data['id']}: {e}")
                last_error = str(e)
                if "429" in last_error: # Rate Limit
                    await asyncio.sleep(2)
                    continue # Retry same model? No, loop logic tries next. 
                    # Ideally we should retry same model for 429. 
                    # But for simplicity, let's just try next model or fail.
        
        # If all models failed
        logger.error(f"All models failed for {bando_data['id']}. Last error: {last_error}")
        return {"id": bando_data["id"], "success": False, "error": last_error}

async def process_batch(session, bandi_batch):
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    # Prepare data dicts
    batch_data = []
    for b in bandi_batch:
        solr_data = {}
        if b.ai_analysis:
            if isinstance(b.ai_analysis, str):
                try: solr_data = json.loads(b.ai_analysis)
                except: pass
            else:
                solr_data = b.ai_analysis
        
        batch_data.append({
            "id": b.id,
            "title": b.title,
            "description": solr_data.get('sintesi') or solr_data.get('body') or "",
            "html": solr_data.get('html') or b.raw_content or ""
        })

    results = await asyncio.gather(*[analyze_bando_async(b, semaphore) for b in batch_data])
    
    # Update DB
    updated = 0
    for res in results:
        if res["success"]:
            bando = session.query(Bando).get(res["id"])
            if bando:
                data = res["data"]
                
                # Update Marketing Text
                bando.marketing_text = data.get("marketing_text")
                
                # Update AI Analysis
                current_analysis = {}
                if bando.ai_analysis:
                    if isinstance(bando.ai_analysis, str):
                        try: current_analysis = json.loads(bando.ai_analysis)
                        except: pass
                    else:
                        current_analysis = dict(bando.ai_analysis)
                
                current_analysis.update(data)
                bando.ai_analysis = current_analysis
                bando.status = ProcessingStatus.ANALYZED
                updated += 1
    
    session.commit()
    logger.info(f"Batch processed. Updated: {updated}/{len(bandi_batch)}")

def run_gemini_analysis(limit: Optional[int] = None):
    print("Starting Gemini Flash Analysis...")
    session = init_db()
    
    # Prefer unprocessed
    query = session.query(Bando).filter(Bando.marketing_text.is_(None))
    
    if limit:
        bandi = query.limit(limit).all()
    else:
        bandi = query.all()
    
    total = len(bandi)
    print(f"Targeting {total} bandi.")
    
    BATCH_SIZE = 50
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Process in batches
    for i in range(0, total, BATCH_SIZE):
        batch = bandi[i : i + BATCH_SIZE]
        print(f"Processing batch {i}-{min(i+BATCH_SIZE, total)}...")
        loop.run_until_complete(process_batch(session, batch))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="Limit number of bandi")
    args = parser.parse_args()
    
    run_gemini_analysis(limit=args.limit)
