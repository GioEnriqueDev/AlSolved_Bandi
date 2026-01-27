import logging
import random
import time
import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class HtmlScraper:
    """
    Modulo per scaricare e analizzare pagine HTML quando non è disponibile un feed RSS.
    Include rotazione User-Agent per evitare blocchi.
    """
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]

    def __init__(self):
        self.session = requests.Session()

    def _get_random_header(self) -> Dict:
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7"
        }

    def fetch_page(self, url: str, retries: int = 3) -> Optional[str]:
        """Scarica l'HTML raw di una pagina con logica di retry."""
        for attempt in range(retries):
            try:
                headers = self._get_random_header()
                response = self.session.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                wait_time = (attempt + 1) * 2
                logger.warning(f"Errore download {url} (Tentativo {attempt+1}/{retries}): {e}. Attendo {wait_time}s...")
                time.sleep(wait_time)
        
        logger.error(f"Download fallito dopo {retries} tentativi: {url}")
        return None

    def extract_links(self, html: str, base_url: str, selector: str) -> List[Dict]:
        """
        Estrae link e titoli da una pagina usando un selettore CSS.
        Ritorna una lista di dizionari {'url': ..., 'title': ...}
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        elements = soup.select(selector)
        for el in elements:
            # Logica generica: cerca un tag <a> dentro l'elemento o l'elemento stesso
            link_tag = el if el.name == 'a' else el.find('a')
            
            if link_tag and link_tag.get('href'):
                href = link_tag['href']
                if not href.startswith('http'):
                    href = base_url.rstrip('/') + '/' + href.lstrip('/')
                
                title = link_tag.get_text(strip=True)
                if title:
                    results.append({'url': href, 'title': title})
        
        return results
