"""
import_bulk_v4.py - SOLR API Direct Access (DEFINITIVO)
========================================================
SCOPERTA: I dati non sono in Drupal AJAX ma in Solr!
Endpoint: https://www.incentivi.gov.it/solr/coredrupal/select

Il sito carica 8000 bandi in una singola chiamata GET.
La risposta JSON contiene:
- response.numFound: numero totale di bandi (~4700)
- response.docs[]: array con tutti i bandi

Ogni doc contiene:
- nid: ID del nodo
- page_title: Titolo del bando
- open_date, close_date: Date apertura/chiusura
- html (zs_rendered_item): HTML della card (contiene il link)
- regions, activity_sector, etc.: Metadati strutturati
"""

import requests
import json
import logging
import re
from bs4 import BeautifulSoup
from src.scraper.models import Bando, ProcessingStatus, init_db

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Solr API Configuration
SOLR_URL = "https://www.incentivi.gov.it/solr/coredrupal/select"

# Campi da richiedere (ottimizzato per estrazione dati)
SOLR_FIELDS = ",".join([
    "nid:zs_nid",
    "page_title:zs_title",
    "open_date:zs_field_open_date",
    "close_date:zs_field_close_date",
    "regions:zm_field_regions",
    "activity_sector:zm_field_activity_sector",
    "subject_type:zm_field_subject_type",
    "support_form:zm_field_support_form",
    "scopes:zm_field_scopes",
    "html:zs_rendered_item",
])

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}


def fetch_all_grants(max_rows=10000):
    """Fetch all grants from Solr API in one request."""
    
    params = {
        "q": "index_id:incentivi",
        "q.op": "OR",
        "wt": "json",
        "rows": max_rows,
        "fl": SOLR_FIELDS,
        "sort": "ds_last_update desc",
    }
    
    logger.info(f"📡 Calling Solr API: {SOLR_URL}")
    logger.info(f"   Requesting up to {max_rows} rows...")
    
    try:
        resp = requests.get(SOLR_URL, params=params, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        
        data = resp.json()
        response = data.get("response", {})
        
        num_found = response.get("numFound", 0)
        docs = response.get("docs", [])
        
        logger.info(f"✅ Solr Response: {num_found} total grants, {len(docs)} returned")
        
        return docs
        
    except requests.RequestException as e:
        logger.error(f"❌ Solr Request Failed: {e}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON Parse Error: {e}")
        return []


def extract_url_from_html(html_snippet):
    """Extract grant detail URL from the rendered HTML card."""
    if not html_snippet:
        return None
        
    soup = BeautifulSoup(html_snippet, 'html.parser')
    
    # Find the main link (usually the first <a> with href containing /it/catalogo/)
    link = soup.find('a', href=re.compile(r'/it/catalogo/'))
    if link:
        href = link.get('href', '')
        if href.startswith('/'):
            return f"https://www.incentivi.gov.it{href}"
        return href
    
    return None


def extract_description_from_html(html_snippet):
    """Extract a text description from the HTML card."""
    if not html_snippet:
        return "No description available"
        
    soup = BeautifulSoup(html_snippet, 'html.parser')
    
    # Try to find description elements
    desc_el = soup.find(class_=re.compile(r'(description|body|summary|subtitle)'))
    if desc_el:
        return desc_el.get_text(strip=True)[:500]
    
    # Fallback: just get all text
    text = soup.get_text(separator=' ', strip=True)
    return text[:500] if text else "No description available"


def run_bulk_import(dry_run=False, limit=None):
    """Main import function."""
    print("=" * 70)
    print("🚀 BULK IMPORT V4 - SOLR DIRECT API")
    print("=" * 70)
    
    # Initialize DB
    if not dry_run:
        session = init_db()
    
    # Fetch all grants from Solr
    docs = fetch_all_grants()
    
    if not docs:
        print("❌ No grants fetched. Aborting.")
        return
    
    # Apply limit if specified
    if limit:
        docs = docs[:limit]
        print(f"⚠️ Limited to {limit} grants for testing")
    
    total_saved = 0
    total_skipped = 0
    total_errors = 0
    
    print(f"\n📊 Processing {len(docs)} grants...")
    print("-" * 70)
    
    for i, doc in enumerate(docs):
        try:
            # Extract data from Solr doc
            title = doc.get("page_title", "Untitled")
            html_snippet = doc.get("html", "")
            
            # Extract URL from HTML card
            url = extract_url_from_html(html_snippet)
            
            if not url:
                # Fallback: construct URL from nid if available
                nid = doc.get("nid")
                if nid:
                    # Try to get URL from title (slugified)
                    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
                    url = f"https://www.incentivi.gov.it/it/catalogo/{slug}"
                else:
                    logger.warning(f"Skipping doc without URL: {title[:50]}...")
                    total_errors += 1
                    continue
            
            # Extract description
            description = extract_description_from_html(html_snippet)
            
            # Add structured metadata to description
            meta_parts = []
            if doc.get("open_date"):
                meta_parts.append(f"Apertura: {doc['open_date']}")
            if doc.get("close_date"):
                meta_parts.append(f"Chiusura: {doc['close_date']}")
            
            if meta_parts:
                description = f"{' | '.join(meta_parts)}\n\n{description}"
            
            # Print progress
            if (i + 1) % 100 == 0 or i < 5:
                print(f"[{i+1:4}/{len(docs)}] {title[:60]}...")
            
            if dry_run:
                total_saved += 1
                continue
            
            # Save to database
            url_hash = Bando.generate_hash(url)
            
            # Check if exists
            existing = session.query(Bando).filter_by(url_hash=url_hash).first()
            if existing:
                total_skipped += 1
                continue
            
            # Create new bando
            new_bando = Bando(
                url=url,
                url_hash=url_hash,
                title=title,
                raw_content=description,
                source_name="Incentivi.gov.it [Solr]",
                status=ProcessingStatus.NEW,
                ai_analysis=json.dumps({
                    "regions": doc.get("regions", []),
                    "activity_sector": doc.get("activity_sector", []),
                    "subject_type": doc.get("subject_type", []),
                    "support_form": doc.get("support_form", []),
                    "scopes": doc.get("scopes", []),
                    "open_date": doc.get("open_date"),
                    "close_date": doc.get("close_date"),
                }) if doc.get("regions") else None
            )
            
            session.add(new_bando)
            total_saved += 1
            
            # Commit in batches of 100
            if total_saved % 100 == 0:
                session.commit()
                logger.info(f"💾 Committed {total_saved} records...")
                
        except Exception as e:
            logger.error(f"Error processing doc: {e}")
            total_errors += 1
    
    # Final commit
    if not dry_run:
        session.commit()
    
    print("-" * 70)
    print(f"\n🏁 IMPORT COMPLETE!")
    print(f"   ✅ Saved: {total_saved}")
    print(f"   ⏭️ Skipped (duplicates): {total_skipped}")
    print(f"   ❌ Errors: {total_errors}")
    print("=" * 70)
    
    return total_saved


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Bulk import grants from Incentivi.gov.it via Solr API")
    parser.add_argument("--dry-run", action="store_true", help="Don't save to DB, just print")
    parser.add_argument("--limit", type=int, help="Limit number of grants to process")
    
    args = parser.parse_args()
    
    run_bulk_import(dry_run=args.dry_run, limit=args.limit)
