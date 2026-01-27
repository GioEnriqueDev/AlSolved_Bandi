from playwright.sync_api import sync_playwright
import logging

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("🕵️ Sniffing Network for API calls...")
        
        # Capture API calls
        page.on("request", lambda request: print(f"REQ: {request.url}") if "api" in request.url or "json" in request.url else None)
        
        page.goto("https://www.incentivi.gov.it/it/catalogo")
        
        # Wait a bit for async calls
        page.wait_for_timeout(5000)
        
        browser.close()

if __name__ == "__main__":
    run()
