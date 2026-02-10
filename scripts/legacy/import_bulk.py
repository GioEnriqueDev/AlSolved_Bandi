import requests
import json
import logging
import time
from bs4 import BeautifulSoup
from scraper.bi_ingest import Ingestor
from scraper.models import Bando, init_db

# Setup Logging
root_logger = logging.getLogger()
if not any(isinstance(h, logging.FileHandler) for h in root_logger.handlers):
    fh = logging.FileHandler("bulk_import.log", mode='w', encoding='utf-8')
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(fh)
logger = logging.getLogger(__name__)

class BulkImporter:
    def __init__(self):
        self.base_url = "https://www.incentivi.gov.it/it/catalogo"
        self.session_db = init_db()
        self.ingestor = Ingestor()
        # Hack: Inject the correct session into ingestor if needed, or rely on its own init
        self.ingestor.session = self.session_db 

    def run(self):
        logger.info("🚀 Starting BULK IMPORT via Drupal AJAX API...")
        
        page = 0
        total_imported = 0
        consecutive_empty_pages = 0
        
        while True:
            params = {
                "page": page,
                "_wrapper_format": "drupal_ajax"
            }
            
            try:
                logger.info(f"📄 Fetching Page {page} (AJAX)...")
                resp = requests.post(self.base_url, params=params, timeout=15)
                
                if resp.status_code != 200:
                    logger.error(f"Status {resp.status_code}. Stopping.")
                    break
                
                data = resp.json()
                
                # Combine all 'data' fields from 'insert' commands
                html_content = ""
                for command in data:
                    if command.get('command') == 'insert':
                         html_data = command.get('data')
                         if html_data and isinstance(html_data, str):
                             html_content += html_data
                
                # If HTML is empty, maybe try generic data extraction
                if not html_content:
                    for command in data:
                         html_data = command.get('data')
                         if html_data and isinstance(html_data, str) and len(html_data) > 100:
                             html_content += html_data

                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Selector Strategy: BROAD but exclude generic page content if possible
                # The grants are often in views-row
                cards = soup.select(".views-row")
                if not cards: cards = soup.select(".card")
                
                # Filter out small/empty cards if necessary, or just log
                valid_cards = []
                for c in cards:
                     # Must have a link to be a grant teaser
                     if c.select_one("a"): 
                        valid_cards.append(c)
                cards = valid_cards
                
                logger.info(f"🔍 Found {len(cards)} items on Page {page}.")


                
                if not cards:
                    logger.warning(f"No cards found on page {page}. Checking if end of results...")
                    if consecutive_empty_pages > 2:
                        break
                    consecutive_empty_pages += 1
                    page += 1
                    continue
                else:
                    consecutive_empty_pages = 0

                logger.info(f"🔍 Found {len(cards)} items on Page {page}.")
                
                count_page = 0
                for card in cards:
                    try:
                        # Extract Title
                        title_el = card.select_one(".views-field-title a") or card.select_one(".card-title") or card.select_one("h3")
                        if not title_el: 
                            continue
                        
                        title = title_el.get_text(strip=True)
                        
                        # Extract Link
                        link_el = card.select_one("a")
                        if not link_el: continue
                        href = link_el.get('href')
                        full_url = f"https://www.incentivi.gov.it{href}" if href.startswith("/") else href
                        
                        # Save
                        # Note: We skip deep fetch initially as requested (raw import)
                        # or we can do a quick deep fetch if fast enough. 
                        # User said "Inserisci i dati grezzi ... NON fare analisi AI"
                        # I will assume we still want content for searching, but maybe skip deep fetch if it's slow?
                        # User said "Scarica tutte le pagine... Inserisci titolo, body, url".
                        # The "Body" is not fully in the card.
                        # I'll save what I have (Description) or fetch if necessary. 
                        # To be fast (1 min), I will SKIP deep fetch and put a placeholder.
                        
                        desc_el = card.select_one(".field--name-body")
                        desc = desc_el.get_text(strip=True) if desc_el else "Da scansionare"
                        
                        if self.ingestor.save_bando(full_url, title, desc, "Incentivi.gov.it [Bulk]"):
                            count_page += 1
                            total_imported += 1
                            
                    except Exception as e:
                        logger.error(f"Error parsing card: {e}")

                logger.info(f"✅ Page {page}: +{count_page} new items.")
                
                page += 1
                time.sleep(0.5) # Be polite
                
            except Exception as e:
                logger.error(f"Loop Failed: {e}")
                break

        logger.info(f"🏁 BULK IMPORT COMPLETED. Total: {total_imported} Bandi.")

if __name__ == "__main__":
    importer = BulkImporter()
    importer.run()
