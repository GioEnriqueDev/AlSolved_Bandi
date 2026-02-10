"""
enrich_data.py - Open Data Enrichment
======================================
Arricchisce i record del database con dati strutturati dall'Open Data ufficiale.

Campi arricchiti:
- ateco_codes: Codici ATECO (settori economici)
- financial_min: Importo minimo agevolazione/spesa
- financial_max: Importo massimo agevolazione/spesa

Matching Strategy:
- Normalizza URL (rimuove www., https://, trailing slashes)
- Confronta Link_istituzionale (Open Data) con url (DB)
"""

import json
import re
import logging
from pathlib import Path
from src.scraper.models import Bando, init_db

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Path to Open Data JSON (existing file in project root)
OPENDATA_PATH = Path(__file__).parent.parent.parent / "data" / "input" / "opendata-export.json"


def normalize_url(url: str) -> str:
    """
    Normalizza un URL per matching:
    - Rimuove protocollo (http://, https://)
    - Rimuove www.
    - Rimuove trailing slash
    - Converte in lowercase
    """
    if not url:
        return ""
    
    url = url.lower().strip()
    
    # Rimuovi protocollo
    url = re.sub(r'^https?://', '', url)
    
    # Rimuovi www.
    url = re.sub(r'^www\.', '', url)
    
    # Rimuovi trailing slash
    url = url.rstrip('/')
    
    return url


def extract_financial_values(item: dict) -> tuple:
    """
    Estrae i valori finanziari min/max dal record Open Data.
    Priorità: Agevolazione_Concedibile > Spesa_Ammessa
    """
    financial_min = None
    financial_max = None
    
    # Prova prima Agevolazione_Concedibile
    if item.get('Agevolazione_Concedibile_min'):
        try:
            financial_min = float(item['Agevolazione_Concedibile_min'])
        except (ValueError, TypeError):
            pass
    
    if item.get('Agevolazione_Concedibile_max'):
        try:
            financial_max = float(item['Agevolazione_Concedibile_max'])
        except (ValueError, TypeError):
            pass
    
    # Fallback a Spesa_Ammessa se Agevolazione non presente
    if financial_min is None and item.get('Spesa_Ammessa_min'):
        try:
            financial_min = float(item['Spesa_Ammessa_min'])
        except (ValueError, TypeError):
            pass
    
    if financial_max is None and item.get('Spesa_Ammessa_max'):
        try:
            financial_max = float(item['Spesa_Ammessa_max'])
        except (ValueError, TypeError):
            pass
    
    return financial_min, financial_max


def run_enrichment(dry_run: bool = False):
    """
    Main enrichment function.
    Carica Open Data JSON e arricchisce i record nel database.
    """
    print("=" * 70)
    print("🔄 DATA ENRICHMENT - Open Data Merge")
    print("=" * 70)
    
    # 1. Load Open Data JSON
    if not OPENDATA_PATH.exists():
        logger.error(f"❌ File non trovato: {OPENDATA_PATH}")
        logger.info("   Incolla i dati Open Data in: data/incentivi_opendata.json")
        return
    
    with open(OPENDATA_PATH, 'r', encoding='utf-8') as f:
        try:
            opendata = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON non valido: {e}")
            return
    
    if not opendata:
        logger.warning("⚠️ File JSON vuoto. Incolla i dati Open Data.")
        return
    
    total_opendata = len(opendata)
    logger.info(f"📊 Caricati {total_opendata} record Open Data")
    
    # 2. Connect to Database
    session = init_db()
    
    # 3. Build URL index from DB for fast lookup
    logger.info("🔍 Costruendo indice URL dal database...")
    
    all_bandi = session.query(Bando).all()
    url_to_bando = {}
    
    for bando in all_bandi:
        normalized = normalize_url(bando.url)
        url_to_bando[normalized] = bando
    
    logger.info(f"   Indicizzati {len(url_to_bando)} bandi dal database")
    
    # 4. Process each Open Data record
    matches_found = 0
    records_enriched = 0
    
    for i, item in enumerate(opendata):
        # Estrai Link_istituzionale (campo URL nel JSON Open Data)
        link = item.get('Link_istituzionale') or item.get('link_istituzionale') or item.get('url', '')
        
        if not link:
            continue
        
        normalized_link = normalize_url(link)
        
        # Cerca match nel DB
        bando = url_to_bando.get(normalized_link)
        
        if not bando:
            # Prova match parziale (suffix match)
            for db_url, db_bando in url_to_bando.items():
                if normalized_link.endswith(db_url.split('/')[-1]) or db_url.endswith(normalized_link.split('/')[-1]):
                    bando = db_bando
                    break
        
        if bando:
            matches_found += 1
            
            # Estrai dati da arricchire
            ateco_codes = item.get('Codici_ATECO') or item.get('codici_ateco') or item.get('ateco', '')
            financial_min, financial_max = extract_financial_values(item)
            
            # Prepara aggiornamento ai_analysis
            current_analysis = {}
            if bando.ai_analysis:
                if isinstance(bando.ai_analysis, str):
                    try:
                        current_analysis = json.loads(bando.ai_analysis)
                    except:
                        current_analysis = {}
                elif isinstance(bando.ai_analysis, dict):
                    current_analysis = bando.ai_analysis
            
            # Aggiungi nuovi campi (solo se non già presenti o se Open Data ha dati migliori)
            updated = False
            
            if ateco_codes and not current_analysis.get('ateco_codes'):
                current_analysis['ateco_codes'] = ateco_codes
                updated = True
            
            if financial_min is not None and not current_analysis.get('financial_min'):
                current_analysis['financial_min'] = financial_min
                updated = True
            
            if financial_max is not None and not current_analysis.get('financial_max'):
                current_analysis['financial_max'] = financial_max
                updated = True
            
            # Aggiungi altri campi utili se presenti
            extra_fields = [
                ('Beneficiari', 'beneficiari'),
                ('Forma_Agevolazione', 'forma_agevolazione'),
                ('Settore_Attivita', 'settore_attivita'),
                ('Obiettivo_Finalita', 'obiettivo_finalita'),
                ('Regione', 'regione'),
                ('Data_Apertura', 'data_apertura'),
                ('Data_Chiusura', 'data_chiusura'),
            ]
            
            for json_key, db_key in extra_fields:
                value = item.get(json_key) or item.get(json_key.lower())
                if value and not current_analysis.get(db_key):
                    current_analysis[db_key] = value
                    updated = True
            
            if updated and not dry_run:
                bando.ai_analysis = json.dumps(current_analysis, ensure_ascii=False)
                records_enriched += 1
            elif updated:
                records_enriched += 1
        
        # Progress log
        if (i + 1) % 500 == 0:
            logger.info(f"   Processati {i + 1}/{total_opendata} record...")
    
    # 5. Commit changes
    if not dry_run:
        session.commit()
        logger.info("💾 Modifiche salvate nel database")
    
    # 6. Final Report
    print("\n" + "=" * 70)
    print("📊 REPORT FINALE")
    print("=" * 70)
    print(f"   📥 Totale Open Data:     {total_opendata}")
    print(f"   🔗 Match Trovati nel DB: {matches_found}")
    print(f"   ✅ Record Arricchiti:    {records_enriched}")
    print("=" * 70)
    
    if dry_run:
        print("⚠️ DRY RUN - Nessuna modifica salvata")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Arricchisce i bandi con dati Open Data")
    parser.add_argument("--dry-run", action="store_true", help="Simula senza salvare")
    
    args = parser.parse_args()
    
    run_enrichment(dry_run=args.dry_run)
