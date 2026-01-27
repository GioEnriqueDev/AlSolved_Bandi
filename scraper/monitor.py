"""
Background Worker - AlSolved Band
Questo script orchestra il ciclo continuo di:
1. Ingestion (Scarico nuovi bandi)
2. Analisi AI (Processamento con Ollama)
"""

import time
import logging
from scraper.bi_ingest import Ingestor
from scraper.gov_html_ingest import GovHtmlIngestor
from scraper.models import init_db
from analysis.analyzer import Analyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_worker():
    logger.info("🚀 AlSolved Background Worker STARTED")
    
    session = init_db()
    ingestor = Ingestor() 
    gov_ingestor = GovHtmlIngestor() # Playwright Scraper
    analyzer = Analyzer(session)

    
    while True:
        try:
            logger.info("--- INIZIO CICLO ---")
            
            # 1. INGESTION PHASE (RSS + National Catalog HTML)
            logger.info("📡 Fase 1: Ingestion RSS & Portals...")
            ingestor.run_cycle()
            
            logger.info("🇮🇹 Fase 1b: National Gov Catalog Import (Playwright)...")
            gov_ingestor.run_import()
            
            # 2. ANALYSIS PHASE
            logger.info("🧠 Fase 2: AI Analysis...")
            analyzer.run_analysis_cycle()
            
            logger.info("--- CICLO COMPLETATO - Attesa 60 secondi ---")
            time.sleep(60)
            
        except KeyboardInterrupt:
            logger.info("🛑 Worker fermato dall'utente.")
            break
        except Exception as e:
            logger.error(f"❌ ERRORE CRITICO NEL WORKER: {e}")
            time.sleep(60) # Attendi prima di riprovare

if __name__ == "__main__":
    run_worker()
