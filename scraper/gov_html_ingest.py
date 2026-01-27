import logging
import time
from playwright.sync_api import sync_playwright
from scraper.bi_ingest import Ingestor
from scraper.models import Bando, get_session, get_engine

logger = logging.getLogger(__name__)

class GovHtmlIngestor:
    def __init__(self):
        self.url = "https://www.incentivi.gov.it/it/catalogo"
        self.bi_ingestor = Ingestor() 
        self.engine = get_engine()
        self.session = get_session(self.engine)

    def run_import(self):
        logger.info(f"🇮🇹 Starting GovHtmlIngestor on {self.url}")
        
        with sync_playwright() as p:
            # Launch headless browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                logger.info(f"Connecting to {self.url}...")
                page.goto(self.url, timeout=60000)
                
                # COOKIE BANNER HANDLING
                try:
                    # Look for RIFIUTO button - generic or specific text
                    # Screenshot showed "RIFIUTO" in uppercase inside a button or link
                    cookie_btn = page.get_by_text("RIFIUTO", exact=True)
                    if cookie_btn.count() > 0:
                        logger.info("🍪 Found Cookie Banner. Clicking RIFIUTO...")
                        cookie_btn.click()
                        time.sleep(2) # Wait for banner to disappear
                    else:
                        # Fallback for "Rifiuto" or partial match
                        cookie_btn = page.locator("button:has-text('Rifiuto')")
                        if cookie_btn.count() > 0:
                            cookie_btn.click()
                            time.sleep(2)
                except Exception as e:
                    logger.warning(f"Cookie banner handling failed (might not exist): {e}")

                # Wait for content
                try:
                    page.wait_for_selector(".view-content", timeout=15000)
                except:
                    logger.warning("⚠️ Timeout waiting for .view-content. Attempting to scrape anyway.")
                
                # Wait for content
                try:
                    page.wait_for_selector(".view-content", timeout=15000)
                except:
                    logger.warning("⚠️ Timeout waiting for .view-content. Attempting to scrape anyway.")
                
                # SCROLL TO LOAD
                logger.info("Scrolling down to trigger potential lazy load...")
                page.mouse.wheel(0, 3000)
                time.sleep(3)
                
                # DEBUG SCREENSHOT (Post-Scroll)
                page.screenshot(path="debug_gov_scrape_3.png")

                # PAGINATION LOOP
                max_clicks = 50 
                clicks = 0
                seen_urls = set()
                
                while clicks < max_clicks:
                    logger.info(f"📄 Processing Page/Chunk {clicks + 1}...")
                    
                    # Locate Cards (Refresh elements)
                    # Note: "VAI ALLA" parent method is robust for finding the CONTAINER
                    cards = page.locator(".card").all()
                    if not cards:
                         btns = page.locator("a:has-text('VAI ALLA')").all()
                         cards = [btn.locator("xpath=../../..") for btn in btns]

                    logger.info(f"🔍 Found {len(cards)} total cards visible.")
                    
                    count_chunk = 0
                    for i, card in enumerate(cards):
                        try:
                            # Extract Link (VAI ALLA...)
                            link_el = card.locator("a:has-text('VAI ALLA')").first
                            if not link_el.count(): link_el = card.locator("h3 a").first
                            
                            if not link_el.count(): continue

                            relative_link = link_el.get_attribute("href")
                            link = f"https://www.incentivi.gov.it{relative_link}" if relative_link and relative_link.startswith("/") else relative_link
                            
                            if not link: continue
                            
                            if link in seen_urls:
                                continue
                            seen_urls.add(link)

                            # Extract Title (Robust Search)
                            title = ""
                            # 1. Drupal Views Title
                            t_el = card.locator(".views-field-title").first
                            if t_el.count():
                                title = t_el.inner_text().strip()
                            
                            # 2. Generic Headers
                            if not title:
                                for tag in ["h3", "h4", "h5", ".card-title"]:
                                    t_el = card.locator(tag).first
                                    if t_el.count():
                                        title = t_el.inner_text().strip()
                                        break
                                        
                            # 3. Fallback: Use the text of the link itself
                            if not title:
                                # Look for ANY 'a' that is NOT "VAI ALLA" and NOT "Load More"
                                links = card.locator("a").all()
                                for l in links:
                                    txt = l.inner_text().strip()
                                    if len(txt) > 10 and "VAI ALLA" not in txt and "MOSTRA" not in txt:
                                        title = txt
                                        break
                            
                            if not title:
                                 title = "Bando Senza Titolo"

                            # SAVE / UPDATE LOGIC
                            existing = self.bi_ingestor.session.query(Bando).filter(Bando.url == link).first()
                            if existing:
                                # Fix bad titles from previous run
                                if existing.title == "Bando Senza Titolo" and title != "Bando Senza Titolo":
                                     existing.title = title
                                     self.bi_ingestor.session.commit()
                                     logger.info(f"🔧 Fixed Title: {title}")
                                continue
                            
                            logger.info(f"Deep Fetching: {title}")
                            full_text = self.bi_ingestor.fetch_full_text(link)
                            
                            if self.bi_ingestor.save_bando(link, title, full_text or "No content", "Incentivi.gov.it"):
                                count_chunk += 1
                                
                        except Exception as e:
                            logger.error(f"Error scraping card: {e}")
                    
                    if count_chunk > 0:
                        logger.info(f"✅ Chunk {clicks+1}: Imported {count_chunk} new grants.")
                    else:
                        logger.info(f"Chunk {clicks+1}: No new grants found (duplicates).")

                    # CLICK LOAD MORE
                    load_more = page.locator("text=MOSTRA ALTRI INCENTIVI") # Case insensitive usually works or exact
                    if load_more.count() > 0 and load_more.is_visible():
                        logger.info("🖱️ Clicking 'MOSTRA ALTRI INCENTIVI'...")
                        load_more.click()
                        time.sleep(4) # Wait for content
                        clicks += 1
                    else:
                        logger.info("⏹️ No 'Load More' button found. Reached end of catalog.")
                        break

                logger.info(f"🇮🇹 GovHtmlIngestor Cycle Complete. Total Scanned: {len(seen_urls)} items.")

            except Exception as e:
                logger.error(f"GovHtmlIngestor Failed: {e}")
            finally:
                browser.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ingestor = GovHtmlIngestor()
    ingestor.run_import()
