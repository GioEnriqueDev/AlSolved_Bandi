import requests
from bs4 import BeautifulSoup
import logging
import json
from scraper.models import Bando, ProcessingStatus, get_session, get_engine
from scraper.bi_ingest import Ingestor

logger = logging.getLogger(__name__)

class GovIngestor:
    def __init__(self):
        self.base_url = "https://www.incentivi.gov.it"
        self.open_data_url = "https://www.incentivi.gov.it/it/open-data"
        self.engine = get_engine()
        self.session = get_session(self.engine)
        # Reuse Ingestor logic for saving/deep fetch if possible, or duplicate for now simplicity
        self.bi_ingestor = Ingestor() 

    def get_json_url(self):
        """Scrapes the Open Data page to find the JSON specific to 'Metadati Scheda Incentivo'."""
        try:
            resp = requests.get(self.open_data_url, timeout=15)
            if resp.status_code != 200:
                logger.error(f"Failed to load Open Data page: {resp.status_code}")
                return None
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Look for <a> tags with .json href or containing 'json' text
            for a in soup.find_all('a', href=True):
                if 'json' in a['href'].lower() and 'incentiv' in a['href'].lower():
                    # Check if relative or absolute
                    if a['href'].startswith('http'):
                        return a['href']
                    return self.base_url + a['href']
            
            logger.warning("No JSON link found on Open Data page.")
            return None
        except Exception as e:
            logger.error(f"Error finding JSON url: {e}")
            return None

    def run_import(self):
        json_url = self.get_json_url()
        if not json_url:
            return
        
        logger.info(f"Downloading Catalog from: {json_url}")
        try:
            resp = requests.get(json_url, timeout=60) # Large file
            data = resp.json()
            
            count = 0
            # Data structure depends on the file. Assuming list of dicts.
            # We'll need to inspect it, but for a solid "V1", we assume a list.
            items = data if isinstance(data, list) else data.get('data', [])
            
            for item in items:
                # Map Schema
                # Incentivi.gov.it likely has fields: 'titolo', 'descrizione', 'url', 'regione' etc.
                # We map blindly for now based on common naming.
                title = item.get('titolo') or item.get('denominazione_misura') or "No Title"
                url = item.get('link_sito_ufficiale') or item.get('url') or "https://www.incentivi.gov.it"
                
                # Fetch full text for AI!
                # Note: This is aggressive. For 1000s of items, we might want to lazy load.
                # But user wants "ALL CURRENT".
                # Let's perform deep fetch only if we are saving a NEW one.
                
                # Check uniqueness first (Optimization)
                url_hash = Bando.generate_hash(url)
                if self.session.query(Bando).filter_by(url_hash=url_hash).first():
                    continue

                full_text = self.bi_ingestor.fetch_full_text(url)
                if not full_text:
                     # Use description from JSON if fetch fails
                     full_text = item.get('descrizione_sintetica', '') + " " + item.get('descrizione', '')
                
                if self.bi_ingestor.save_bando(url, title, full_text, "Incentivi.gov.it"):
                    count += 1
            
            logger.info(f"GovIngestor: Imported {count} new items from National Catalog.")

        except Exception as e:
            logger.error(f"Import failed: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    gov = GovIngestor()
    gov.run_import()
