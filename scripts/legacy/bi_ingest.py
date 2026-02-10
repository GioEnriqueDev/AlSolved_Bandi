import logging
import feedparser
import requests
from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError
from scraper.models import Bando, ProcessingStatus, get_engine, create_tables, get_session

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

from apscheduler.schedulers.blocking import BlockingScheduler
from scraper.html_module import HtmlScraper

# ... imports remains same ...

class Ingestor:
    def __init__(self):
        self.engine = get_engine()
        create_tables(self.engine)
        self.session = get_session(self.engine)
        self.html_scraper = HtmlScraper() # Initialize HTML Module

    def save_bando(self, url, title, content, source):
        """Saves bando to DB if it doesn't exist."""
        url_hash = Bando.generate_hash(url)
        
        # Check existence check logic could be here, but DB unique constraint handles it too.
        # However, checking first saves id generation and error handling overhead.
        existing = self.session.query(Bando).filter_by(url_hash=url_hash).first()
        if existing:
            logger.info(f"SKIPPING: {title} (Already exists)")
            return False

        try:
            new_bando = Bando(
                url=url,
                url_hash=url_hash,
                title=title,
                raw_content=content,
                source_name=source,
                status=ProcessingStatus.NEW
            )
            self.session.add(new_bando)
            self.session.commit()
            logger.info(f"SAVED: {title}")
            return True
        except IntegrityError:
            self.session.rollback()
            logger.warning(f"DUPLICATE DETECTED during commit: {url}")
            return False
        except Exception as e:
            self.session.rollback()
            logger.error(f"ERROR saving {url}: {e}")
            return False

    def fetch_full_text(self, url):
        """Visits the URL and extracts real page text for AI."""
        try:
            # Skip PDF files for now (need OCR/PDF parsing, maybe later)
            if url.lower().endswith('.pdf'):
                return "PDF Content - Download required"

            resp = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Cleanup common junk
                for garbage in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    garbage.decompose()
                
                # Get text
                text = soup.get_text(separator=' ', strip=True)
                
                # Simple check to avoid empty pages or soft blocks
                if len(text) < 200: 
                    return None
                    
                return text[:50000] # Cap at 50k chars for DB
        except Exception as e:
            logger.warning(f"Deep Fetch failed for {url}: {e}")
        return None

    def fetch_rss(self, feed_url, source_name):
        """Ingests from an RSS feed with Deep Fetch."""
        logger.info(f"Fetching RSS: {feed_url}")
        feed = feedparser.parse(feed_url)
        count = 0
        for entry in feed.entries:
            url = entry.get('link')
            title = entry.get('title')
            
            # DEEP FETCH STRATEGY
            # 1. Try to get full text from the link
            full_text = self.fetch_full_text(url)
            
            # 2. Fallback to RSS description if fetch fails
            if not full_text:
                rss_desc = entry.get('description', '') + " " + entry.get('content', [{'value': ''}])[0]['value']
                full_text = f"[RSS ONLY] {rss_desc}"
                
            if self.save_bando(url, title, full_text, source_name):
                count += 1
        logger.info(f"RSS {source_name}: Imported {count} new items.")

    # ... existing fetch_html_portal ...
    def fetch_html_portal(self, url, source_name, selector):
        """Ingests from an HTML page using CSS selectors."""
        logger.info(f"Scraping HTML: {url}")
        html = self.html_scraper.fetch_page(url)
        if not html:
            return

        items = self.html_scraper.extract_links(html, url, selector)
        count = 0
        for item in items:
            # Deep Fetch for HTML items too
            full_text = self.fetch_full_text(item['url'])
            if not full_text:
                 full_text = "HTML Scraped Link (Content Fetch Failed)"

            if self.save_bando(item['url'], item['title'], full_text, source_name):
                count += 1
        logger.info(f"HTML {source_name}: Imported {count} new items.")

    def run_cycle(self):
        """Single execution cycle."""
        logger.info("Starting Ingestion Cycle...")
        
        # 1. RSS Sources (REAL DATA)
        sources_rss = [
            ("https://www.mimit.gov.it/it/notizie-stampa?format=feed&type=rss", "MIMIT (News)"),
            ("https://www.invitalia.it/xml/rss/notizie", "Invitalia (News)"), # Real Source
        ]
        for url, name in sources_rss:
            self.fetch_rss(url, name)
            
        logger.info("Ingestion Cycle Complete.")

    def start_scheduler(self):
        """Starts the scheduler to run every hour."""
        scheduler = BlockingScheduler()
        # Run immediately on start
        self.run_cycle()
        # Schedule every hour
        scheduler.add_job(self.run_cycle, 'interval', hours=1)
        logger.info("Scheduler started (Interval: 1 hour). Press Ctrl+C to exit.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass

if __name__ == "__main__":
    ingestor = Ingestor()
    ingestor.run_cycle()
