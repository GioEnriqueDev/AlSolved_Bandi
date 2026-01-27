"""
generate_marketing.py - AI Marketing Text Generator
====================================================
Genera testi persuasivi per i bandi arricchiti.

Strategia:
- Priorità ai 120 bandi "Gold" (con ATECO codes)
- Template dinamico che evidenzia importo + settore
- Salva in marketing_text senza toccare raw_content
"""

import json
import logging
from scraper.models import Bando, init_db

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def format_currency(value):
    """Formatta un valore numerico in euro leggibile."""
    if value is None:
        return None
    try:
        num = float(value)
        if num >= 1_000_000:
            return f"€{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"€{num/1_000:.0f}K"
        else:
            return f"€{num:.0f}"
    except (ValueError, TypeError):
        return None


def extract_sector_name(ateco_codes: str) -> str:
    """Estrae un nome settore leggibile dai codici ATECO."""
    if not ateco_codes:
        return None
    
    # Mapping codici ATECO -> settori leggibili
    ATECO_SECTORS = {
        "10": "Alimentare",
        "11": "Bevande",
        "13": "Tessile",
        "14": "Abbigliamento",
        "15": "Pelletteria",
        "16": "Legno",
        "20": "Chimica",
        "21": "Farmaceutica",
        "22": "Plastica",
        "23": "Materiali da costruzione",
        "24": "Metallurgia",
        "25": "Metalmeccanica",
        "26": "Elettronica",
        "27": "Apparecchiature elettriche",
        "28": "Macchinari",
        "29": "Automotive",
        "30": "Trasporti",
        "31": "Mobili",
        "32": "Manifattura",
        "41": "Edilizia",
        "42": "Ingegneria civile",
        "43": "Costruzioni specializzate",
        "45": "Commercio auto",
        "46": "Commercio ingrosso",
        "47": "Commercio dettaglio",
        "49": "Trasporto terrestre",
        "50": "Trasporto marittimo",
        "51": "Trasporto aereo",
        "52": "Logistica",
        "55": "Alloggio",
        "56": "Ristorazione",
        "58": "Editoria",
        "59": "Audiovisivo",
        "61": "Telecomunicazioni",
        "62": "Software e IT",
        "63": "Servizi informatici",
        "64": "Servizi finanziari",
        "68": "Immobiliare",
        "69": "Servizi legali e contabili",
        "70": "Consulenza aziendale",
        "71": "Architettura e ingegneria",
        "72": "Ricerca e sviluppo",
        "73": "Pubblicità e marketing",
        "74": "Design",
        "75": "Veterinaria",
        "77": "Noleggio",
        "79": "Turismo",
        "80": "Vigilanza",
        "81": "Facility management",
        "82": "Servizi alle imprese",
        "85": "Istruzione",
        "86": "Sanità",
        "87": "Assistenza sociale",
        "90": "Arte e spettacolo",
        "91": "Biblioteche e musei",
        "93": "Sport e intrattenimento",
        "95": "Riparazioni",
        "96": "Servizi alla persona",
    }
    
    sectors_found = []
    codes = ateco_codes.replace(";", " ").replace(",", " ").split()
    
    for code in codes[:3]:  # Max 3 settori
        code_prefix = code[:2] if len(code) >= 2 else code
        if code_prefix in ATECO_SECTORS:
            sector = ATECO_SECTORS[code_prefix]
            if sector not in sectors_found:
                sectors_found.append(sector)
    
    if sectors_found:
        return ", ".join(sectors_found[:2])  # Max 2 settori nel testo
    return None


def generate_marketing_text(bando, analysis: dict) -> str:
    """
    Genera un testo marketing persuasivo basato sui dati disponibili.
    """
    parts = []
    
    # 1. Vantaggio economico (priorità massima)
    financial_max = analysis.get('financial_max')
    financial_min = analysis.get('financial_min')
    
    if financial_max:
        max_str = format_currency(financial_max)
        if max_str:
            parts.append(f"💰 Ottieni fino a {max_str} per la tua impresa")
    elif financial_min:
        min_str = format_currency(financial_min)
        if min_str:
            parts.append(f"💰 Finanziamento a partire da {min_str}")
    
    # 2. Forma agevolazione
    forma = analysis.get('forma_agevolazione') or analysis.get('support_form', [])
    if isinstance(forma, list) and forma:
        forma_str = forma[0] if isinstance(forma[0], str) else str(forma[0])
        if 'fondo' in forma_str.lower() or 'perduto' in forma_str.lower():
            parts.append("✅ Contributo a fondo perduto")
        elif 'garanzia' in forma_str.lower():
            parts.append("🛡️ Garanzia statale inclusa")
        elif 'credito' in forma_str.lower() or 'fisc' in forma_str.lower():
            parts.append("📊 Credito d'imposta")
    
    # 3. Settore target
    ateco = analysis.get('ateco_codes', '')
    sector = extract_sector_name(ateco)
    if sector:
        parts.append(f"🏭 Ideale per: {sector}")
    
    # 4. Urgenza / Scadenza
    close_date = analysis.get('close_date') or analysis.get('data_chiusura')
    if close_date and close_date != 'N/A':
        parts.append(f"⏰ Scadenza: {close_date[:10] if len(close_date) > 10 else close_date}")
    
    # 5. Regione
    regione = analysis.get('regione')
    if regione and isinstance(regione, str):
        parts.append(f"📍 {regione}")
    
    # Costruisci il testo finale
    if parts:
        return " | ".join(parts)
    else:
        # Fallback generico persuasivo
        return "💡 Opportunità di finanziamento per PMI - Richiedi una consulenza gratuita per verificare i requisiti"


def run_marketing_generation(limit: int = None, dry_run: bool = False):
    """
    Main function to generate marketing text for enriched bandi.
    """
    print("=" * 70)
    print("🎯 MARKETING TEXT GENERATOR")
    print("=" * 70)
    
    session = init_db()
    
    # Query bandi arricchiti (con ATECO codes = "Gold")
    query = session.query(Bando).filter(
        Bando.ai_analysis.like('%ateco%')
    )
    
    if limit:
        query = query.limit(limit)
    
    bandi = query.all()
    logger.info(f"📊 Trovati {len(bandi)} bandi 'Gold' da processare")
    
    processed = 0
    updated = 0
    
    for bando in bandi:
        try:
            # Parse ai_analysis
            analysis = {}
            if bando.ai_analysis:
                if isinstance(bando.ai_analysis, str):
                    analysis = json.loads(bando.ai_analysis)
                elif isinstance(bando.ai_analysis, dict):
                    analysis = bando.ai_analysis
            
            # Generate marketing text
            marketing_text = generate_marketing_text(bando, analysis)
            
            if marketing_text:
                if not dry_run:
                    bando.marketing_text = marketing_text
                
                updated += 1
                
                # Log sample
                if updated <= 5:
                    print(f"\n📝 [{updated}] {bando.title[:50]}...")
                    print(f"   ➡️ {marketing_text}")
            
            processed += 1
            
        except Exception as e:
            logger.error(f"Error processing bando {bando.id}: {e}")
    
    # Commit
    if not dry_run:
        session.commit()
        logger.info("💾 Modifiche salvate nel database")
    
    # Report
    print("\n" + "=" * 70)
    print("📊 REPORT FINALE")
    print("=" * 70)
    print(f"   📥 Bandi processati:  {processed}")
    print(f"   ✅ Testi generati:    {updated}")
    print("=" * 70)
    
    if dry_run:
        print("⚠️ DRY RUN - Nessuna modifica salvata")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Genera testi marketing per bandi")
    parser.add_argument("--limit", type=int, help="Limita numero di bandi")
    parser.add_argument("--dry-run", action="store_true", help="Non salvare modifiche")
    
    args = parser.parse_args()
    
    run_marketing_generation(limit=args.limit, dry_run=args.dry_run)
