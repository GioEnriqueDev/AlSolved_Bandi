"""
analyze_ollama.py - Deep Grant Analysis with Local AI
=====================================================
Uses local Ollama (Llama 3.2) to analyze grants and extract high-quality structured data.

Targets:
- Marketing Text (Persuasive "Gold" copy)
- Regions (Clean list for filtering)
- Deadlines (Normalized YYYY-MM-DD)
- Financial Data (Max Amount)
- ATECO Codes (If inferable)

Usage:
    python -m analysis.analyze_ollama --limit 10
    python -m analysis.analyze_ollama --all
"""

import json
import logging
import requests
import re
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from scraper.models import init_db, Bando, ProcessingStatus

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"  # Ensure this model is pulled: ollama pull llama3.2

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_json_response(response_text: str) -> Optional[Dict[str, Any]]:
    """Extracts and parses JSON from LLM response."""
    try:
        # Find JSON block
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        return json.loads(response_text)
    except Exception as e:
        logger.error(f"Failed to parse JSON: {e}")
        return None

def analyze_bando_with_ollama(bando: Bando) -> Optional[Dict[str, Any]]:
    """Sends bando data to Ollama for analysis."""
    
    # Prepare context
    context = f"Titolo: {bando.title}\n"
    
    # Extract info from existing analysis if available
    solr_data = {}
    if bando.ai_analysis:
        if isinstance(bando.ai_analysis, str):
            try:
                solr_data = json.loads(bando.ai_analysis)
            except:
                pass
        else:
            solr_data = bando.ai_analysis
            
    # Add Solr description/html text if available
    description = solr_data.get('sintesi') or solr_data.get('body') or ""
    html_content = solr_data.get('html', '') or bando.raw_content or ""
    
    context += f"Descrizione: {description[:2000]}\n" # Truncate to avoid context limit
    context += f"HTML/Contenuto: {html_content[:2000]}\n"

    prompt = f"""
    Sei un analista esperto di bandi e finanza agevolata. Analizza questo bando e estrai i dati chiave in formato JSON.
    
    DATI BANDO:
    {context}
    
    COMPITO:
    Restituisci ESCLUSIVAMENTE un oggetto JSON con questi campi:
    1. "marketing_text": Una frase breve e persuasiva (max 20 parole) che evidenzia il vantaggio economico (es. "Fondo perduto 50%") e il target. Usa emoji.
    2. "titolo_riassuntivo": Un titolo pulito e chiaro (max 10 parole).
    3. "sintesi": Una descrizione sintetica del bando (max 50 parole).
    4. "regioni": Lista delle regioni italiane coinvolte (es. ["Lombardia", "Nazionale"]). Se nazionale, scrivi ["Nazionale"].
    5. "scadenza": Data di scadenza nel formato "YYYY-MM-DD" o "A sportello" o "N/A".
    6. "financial_max": Importo massimo agevolazione (numero intero) o null.
    7. "is_gold": true se il bando è molto interessante (fondo perduto o importi alti), false altrimenti.

    RISPOSTA (Solo JSON):
    """

    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json" 
    }

    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        return json.loads(result['response'])
    except Exception as e:
        logger.error(f"Ollama Request Error: {e}")
        return None

def run_analysis(limit: Optional[int] = None, force: bool = False):
    session = init_db()
    
    # Query logic
    query = session.query(Bando)
    if not force:
        # Prefer new bandi or those without decent analysis
        query = query.filter(Bando.marketing_text.is_(None))
    
    total_count = query.count()
    if limit:
        bandi = query.limit(limit).all()
        logger.info(f"Processing {limit} bandi (Total available: {total_count})")
    else:
        bandi = query.all()
        logger.info(f"Processing ALL {total_count} bandi")

    success_count = 0
    
    for i, bando in enumerate(bandi, 1):
        logger.info(f"[{i}/{len(bandi)}] Analyzing: {bando.title[:50]}...")
        
        analysis_result = analyze_bando_with_ollama(bando)
        
        if analysis_result:
            # Update fields
            bando.marketing_text = analysis_result.get("marketing_text")
            
            # Merge with existing ai_analysis
            current_analysis = {}
            if bando.ai_analysis:
                if isinstance(bando.ai_analysis, str):
                    try:
                        current_analysis = json.loads(bando.ai_analysis)
                    except:
                        pass
                else:
                    current_analysis = dict(bando.ai_analysis)
            
            # Update/Overwrite keys
            current_analysis.update({
                "titolo_riassuntivo": analysis_result.get("titolo_riassuntivo"),
                "sintesi": analysis_result.get("sintesi"),
                "regioni": analysis_result.get("regioni"), # This fixes the ID issue!
                "scadenza": analysis_result.get("scadenza"),
                "financial_max": analysis_result.get("financial_max"),
                "is_gold": analysis_result.get("is_gold")
            })
            
            bando.ai_analysis = current_analysis  # SQLAlchemy handles JSON serialization if type is JSON
            bando.status = ProcessingStatus.ANALYZED
            
            success_count += 1
            if i % 10 == 0:
                session.commit()
                logger.info(f"Saved batch. Success so far: {success_count}")
        else:
            logger.warning(f"Skipped {bando.id} due to analysis failure.")

    session.commit()
    logger.info(f"Analysis Complete. Processed: {len(bandi)}, Success: {success_count}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="Limit number of bandi")
    parser.add_argument("--all", action="store_true", help="Process all bandi")
    parser.add_argument("--force", action="store_true", help="Re-analyze even if already done")
    args = parser.parse_args()
    
    limit = args.limit if args.limit else (None if args.all else 10) # Default 10
    run_analysis(limit=limit, force=args.force)
