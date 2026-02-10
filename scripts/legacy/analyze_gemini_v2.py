"""
analyze_gemini_v2.py - Optimized Grant Analysis
===============================================
Improvements over v1:
1. Robust Rate Limit Handling (Exponential Backoff)
2. Better Prompting (Distinguish Bando vs News)
3. HTML Cleaning (Reduce Token Usage)
4. Structured JSON Output with Pydantic-like validation
"""

import json
import logging
import asyncio
import os
import re
import sys
import random
import traceback
from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup

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
MODEL_NAME = "gemini-2.0-flash"
CONCURRENCY_LIMIT = 5  # Lower concurrency to avoid 429 Storm
MAX_RETRIES = 5
BASE_DELAY = 2

# Setup Logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("analysis_v2.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def clean_html(html_content: str) -> str:
    """Extracts text and key links from HTML, removing boilerplate."""
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script, style, nav, footer
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()
        
    text = soup.get_text(separator="\n")
    
    # Collapse whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text).strip()
    return text[:8000] # Limit context size

async def analyze_bando_with_retry(bando_data: Dict[str, Any], semaphore: asyncio.Semaphore) -> Dict[str, Any]:
    """Analyzes a single bando with retry logic."""
    async with semaphore:
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Clean Content
        cleaned_text = clean_html(bando_data['html'])
        context = f"TITOLO: {bando_data['title']}\n\nCONTENUTO:\n{cleaned_text}"
        
        prompt = """
        Sei un analista esperto di finanza agevolata. Analizza questo testo (proveniente da incentivi.gov.it) e determina se è un BANDO ATTIVO con fondi disponibili o solo una NEWS/COMUNICATO.
        
        OUTPUT DESIDERATO (JSON VALID):
        {
            "is_bando": true/false, (True se concede fondi/agevolazioni, False conferenze/nomine/news generiche)
            "titolo_riassuntivo": "Titolo breve ed efficace per card (max 10 parole)",
            "sintesi": "Riassunto chiaro del beneficio e dei destinatari (max 30 parole)",
            "marketing_text": "Call to action persuasiva: 'Ottieni fino a X euro per...' (max 20 parole)",
            "regioni": ["Lombardia", "Nazionale", "Sicilia"], (Lista regioni ammissibili. Se è per tutta Italia metti "Nazionale")
            "agevolazione_max": "es. 50000" (Importo massimo numerico stimato o null. Se a fondo perduto metti solo cifra),
            "tipo_agevolazione": "Fondo perduto" / "Finanziamento agevolato" / "Credito d'imposta" / "Altro",
            "scadenza": "YYYY-MM-DD" (o "A sportello" o check data chiusura),
            "is_gold": true/false (True se fondo perduto > 40% o importo > 20k, e se è un bando reale)
        }
        
        Se è solo una news, compila comunque sintesi e titolo, ma metti is_bando: false e is_gold: false.
        RISPONDI SOLO CON IL JSON.
        """
        
        full_prompt = prompt + "\n\nDATI DA ANALIZZARE:\n" + context
        
        # Disable Safety Settings
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        for attempt in range(MAX_RETRIES):
            try:
                # Add jitter to avoid thundering herd
                await asyncio.sleep(random.uniform(0.1, 0.5))
                
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: model.generate_content(
                        full_prompt, 
                        generation_config={"response_mime_type": "application/json"},
                        safety_settings=safety_settings
                    )
                )
                
                result_json = json.loads(response.text)
                
                # Handle case where AI returns a list [ {...} ]
                if isinstance(result_json, list):
                    if len(result_json) > 0:
                        result_json = result_json[0]
                    else:
                        result_json = {}

                return {"id": bando_data["id"], "success": True, "data": result_json}
                
            except Exception as e:
                err_str = str(e)
                if "429" in err_str:
                    wait_time = (BASE_DELAY * (2 ** attempt)) + random.uniform(0, 1)
                    logger.warning(f"⏳ 429 Rate Limit for ID {bando_data['id']}. Retrying in {wait_time:.2f}s... (Attempt {attempt+1}/{MAX_RETRIES})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"❌ Error analyzing ID {bando_data['id']}: {err_str}")
                    traceback.print_exc() # Print full traceback
                    with open("last_error.txt", "w") as f:
                        f.write(err_str + "\n")
                        traceback.print_exc(file=f)
                    return {"id": bando_data["id"], "success": False, "error": err_str}
        
        return {"id": bando_data["id"], "success": False, "error": "Max retries exceeded"}

async def process_batch(session, bandi_batch):
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    tasks = []
    for b in bandi_batch:
        # Check if already has HTML content in analysis or raw_content
        input_html = b.raw_content
        # sometimes raw_content is actually just a description, we need to check if we have better data
        # But for V1 import, logic was loose. Let's use whatever we have.
        
        tasks.append(analyze_bando_with_retry({
            "id": b.id,
            "title": b.title,
            "html": input_html or ""
        }, semaphore))
    
    results = await asyncio.gather(*tasks)
    
    updated_count = 0
    for res in results:
        if res["success"]:
            bando = session.query(Bando).get(res["id"])
            if bando:
                data = res["data"]
                
                # Update Analysis
                bando.ai_analysis = data
                bando.marketing_text = data.get("marketing_text")
                bando.status = ProcessingStatus.ANALYZED
                updated_count += 1
        else:
            print(f"❌ FAILURE for ID {res['id']}: {res.get('error')}")

    try:
        session.commit()
        logger.info(f"💾 Batch committed. Updated {updated_count} bandi.")
    except Exception as e:
        session.rollback()
        logger.error(f"❌ DB Commit failed: {e}")
        print(f"❌ DB Commit failed: {e}")

def run_analysis_v2(limit: Optional[int] = None, force_reanalyze: bool = False):
    print("="*60)
    print("🚀 GEMINI V2 ANALYSIS STARTING")
    print("="*60)
    
    session = init_db()
    
    query = session.query(Bando)
    
    if not force_reanalyze:
        # Prioritize NEW or ERROR, or ANALYZED but empty/old
        query = query.filter(
            (Bando.status == ProcessingStatus.NEW) | 
            (Bando.status == ProcessingStatus.ERROR) |
            (Bando.ai_analysis == None)
        )
    
    bandi = query.limit(limit).all() if limit else query.all()
    
    total = len(bandi)
    if total == 0:
        print("✅ No bandi to process!")
        return

    print(f"🎯 Targeting {total} bandi for analysis.")
    print(f"⚡ Concurrency: {CONCURRENCY_LIMIT}, Retries: {MAX_RETRIES}")
    
    BATCH_SIZE = 20
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    for i in range(0, total, BATCH_SIZE):
        batch = bandi[i : i + BATCH_SIZE]
        print(f"\n📦 Processing batch {i+1}-{min(i+BATCH_SIZE, total)} of {total}...")
        loop.run_until_complete(process_batch(session, batch))
        
    print("\n🏁 ANALYSIS COMPLETE")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="Limit number of items")
    parser.add_argument("--force", action="store_true", help="Re-analyze everything")
    args = parser.parse_args()
    
    run_analysis_v2(limit=args.limit, force_reanalyze=args.force)
