"""
analyze_all_v2.py - Massive Clean & Re-Analyze using Gemini 1.5 Flash (SDK Version)
===================================================================================
Iterates through ALL bandi in the database to clean structured data.
Strict Rate Limiting applied to avoid 429/404 errors.
"""

import json
import logging
import asyncio
import os
import sys
import warnings
import time
from typing import Dict, Any
from scraper.models import init_db, Bando, ProcessingStatus
import google.generativeai as genai
from dotenv import load_dotenv

# Suppress warnings
warnings.simplefilter('ignore')

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
# STRICT LIMIT: Free tier is often ~15 RPM. 
# We set concurrency to 1 and sleep 4s to stay safe (~12 RPM).
CONCURRENCY_LIMIT = 1 

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# STRICT: Use standard Flash first, then fallback to Pro if needed.
# User requested: "gemini-1.5-flash" forced.
CANDIDATE_MODELS = ["gemini-1.5-flash", "gemini-1.0-pro"]

async def analyze_bando_v2(bando_data: Dict[str, Any], semaphore: asyncio.Semaphore) -> Dict[str, Any]:
    """Analyzes a single bando using Gemini SDK."""
    async with semaphore:
        # RATE LIMIT ENFORCEMENT: 4 seconds sleep = Max 15 requests per minute
        await asyncio.sleep(4.0)
        
        context = f"Titolo: {bando_data['title']}\n"
        context += f"Descrizione: {str(bando_data['description'])[:3500]}\n"
        context += f"HTML Content (Partial): {str(bando_data['html'])[:3500]}\n"

        prompt = """
        Analizza questo bando. Estrai in formato JSON puro.
        
        INPUT:
        Vedi sopra.
        
        OUTPUT OBBLIGATORIO (JSON):
        {
            "regions": ["Lombardia", "Lazio"] o ["Nazionale"],
            "ateco_codes": ["56.10", "Agricoltura"] (o []),
            "is_expired": true/false (True se la data di scadenza nel testo è passata rispetto a oggi, 16 Gennaio 2026),
            "marketing_text": "Riassunto persuasivo di 2 righe (Vantaggio + Call to Action). Usa emoji.",
            "search_tags": ["Start-up", "Fondo Perduto", "Giovani"],
            "sintesi": "Breve descrizione max 40 parole",
            "scadenza": "YYYY-MM-DD" o "N/A"
        }
        """
        
        full_prompt = prompt + "\nDATI:\n" + context
        
        last_error = None

        for model_name in CANDIDATE_MODELS:
            try:
                # DEBUG PRINT
                # print(f"DEBUG: Analyzing Bando {bando_data['id']} with {model_name}...")

                model = genai.GenerativeModel(model_name)
                
                # Run blocking SDK call in executor
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: model.generate_content(full_prompt, generation_config={"response_mime_type": "application/json"})
                )
                
                # Parse JSON
                result_json = json.loads(response.text)
                return {"id": bando_data["id"], "success": True, "data": result_json}
                
            except Exception as e:
                last_error = str(e)
                # print(f"WARN: Model {model_name} failed for {bando_data['id']}: {e}")
                
                if "429" in last_error or "quota" in last_error.lower():
                    print(f"WARN: Quota hit for {bando_data['id']}. Sleeping 30s...")
                    await asyncio.sleep(30)
                    continue 

                # If 404 (Model not found) or 500, try next model
                continue
        
        print(f"ERROR Bando {bando_data['id']} failed all models. Last: {last_error}")
        return {"id": bando_data["id"], "success": False, "error": last_error}

async def process_batch(session, bandi_batch):
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    batch_data = []
    for b in bandi_batch:
        # Get description from existing analysis or raw content
        desc = ""
        if b.ai_analysis:
            try:
                if isinstance(b.ai_analysis, str):
                    d = json.loads(b.ai_analysis)
                else: 
                    d = b.ai_analysis
                desc = d.get('sintesi') or d.get('body') or ""
            except: 
                pass
        
        batch_data.append({
            "id": b.id,
            "title": b.title,
            "description": desc,
            "html": b.raw_content or ""
        })

    results = await asyncio.gather(*[analyze_bando_v2(b, semaphore) for b in batch_data])
    
    updated_count = 0
    for res in results:
        if res["success"]:
            bando = session.query(Bando).get(res["id"])
            if bando:
                data = res["data"]
                
                # Merge logic
                current_analysis = {}
                if bando.ai_analysis:
                    if isinstance(bando.ai_analysis, str):
                        try: current_analysis = json.loads(bando.ai_analysis)
                        except: pass
                    else:
                        current_analysis = dict(bando.ai_analysis)
                
                # Update critical fields
                current_analysis['regions'] = data.get('regions', [])
                current_analysis['ateco_codes'] = data.get('ateco_codes', [])
                current_analysis['is_expired'] = data.get('is_expired', False)
                current_analysis['search_tags'] = data.get('search_tags', [])
                current_analysis['marketing_text'] = data.get('marketing_text', "")
                current_analysis['sintesi'] = data.get('sintesi', current_analysis.get('sintesi', '')) 
                if data.get('scadenza'):
                     current_analysis['scadenza'] = data.get('scadenza')

                bando.ai_analysis = current_analysis
                bando.marketing_text = data.get('marketing_text') 
                bando.status = ProcessingStatus.ANALYZED
                updated_count += 1
    
    session.commit()
    logger.info(f"Batch processed. Updated: {updated_count}/{len(bandi_batch)}")

def run_v2_analysis(limit: int = 100000):
    print("Starting Gemini Flash V2 CLEANUP Analysis (SDK Version)...")
    print(f"Models: {CANDIDATE_MODELS}")
    session = init_db()
    
    query = session.query(Bando).order_by(Bando.id.desc())
    total_count = query.count()
    print(f"Total Bandi in DB: {total_count}")
    
    BATCH_SIZE = 50 # Process limit logic chunks
    process_limit = min(total_count, limit)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    for offset in range(0, process_limit, BATCH_SIZE):
        batch = query.offset(offset).limit(BATCH_SIZE).all()
        if not batch: break
        
        print(f"Processing batch {offset}-{offset+len(batch)} of {process_limit}...")
        loop.run_until_complete(process_batch(session, batch))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100000, help="Max items to process")
    args = parser.parse_args()
    
    run_v2_analysis(limit=args.limit)
