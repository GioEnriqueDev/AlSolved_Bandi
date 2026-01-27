"""
import_bulk_v2.py - AGNOSTIC Drupal AJAX Parser
===============================================
Strategia "a maglie larghe":
1. Non ci fidiamo del nome del comando ('insert')
2. Cerchiamo QUALSIASI campo 'data' con lunghezza > 1000 chars
3. Estraiamo link che contengono 'catalogo' nel href
4. Risaliamo al parent per trovare il titolo
"""

import requests
import json
from bs4 import BeautifulSoup

# Config
AJAX_URL = "https://www.incentivi.gov.it/it/catalogo"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

def find_large_html_blocks(json_data, min_length=1000):
    """
    Recursively search JSON for any string field > min_length chars.
    Returns a list of all large strings found (likely HTML content).
    """
    large_blocks = []
    
    def recurse(obj, path=""):
        if isinstance(obj, str):
            if len(obj) > min_length:
                large_blocks.append({
                    "path": path,
                    "length": len(obj),
                    "content": obj
                })
        elif isinstance(obj, dict):
            for key, value in obj.items():
                recurse(value, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                recurse(item, f"{path}[{i}]")
    
    recurse(json_data)
    return large_blocks


def extract_grants_from_html(html_content):
    """
    Estrazione Robusta:
    - Cerca tutti i tag <a> con href che contiene 'catalogo'
    - Risale al parent per trovare il contesto (titolo, descrizione)
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    grants = []
    seen_urls = set()
    
    # Strategy 1: Find all links containing 'catalogo' in href (grant detail pages)
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        href = link.get('href', '')
        
        # Filter: Only links to grant detail pages
        # Typical pattern: /it/catalogo/dettaglio-di-un-bando
        if '/it/catalogo/' not in href:
            continue
        if href == '/it/catalogo':  # Skip main catalog link
            continue
        if href in seen_urls:
            continue
            
        seen_urls.add(href)
        
        # Build full URL
        full_url = f"https://www.incentivi.gov.it{href}" if href.startswith('/') else href
        
        # Extract title from the link text or nearby elements
        title = link.get_text(strip=True)
        
        # If link text is empty or too short, try to find title from parent
        if not title or len(title) < 5:
            parent = link.find_parent(['div', 'article', 'li', 'section'])
            if parent:
                # Look for heading elements
                heading = parent.find(['h2', 'h3', 'h4', 'h5', 'strong'])
                if heading:
                    title = heading.get_text(strip=True)
                else:
                    # Fallback: first meaningful text in parent
                    title = parent.get_text(strip=True)[:150]
        
        if title and len(title) > 3:
            grants.append({
                'title': title[:200],  # Cap title length
                'url': full_url
            })
    
    return grants


def run_bulk_import(max_pages=50):
    """
    Main import loop - fetches all pages from the AJAX API.
    """
    print("=" * 60)
    print("🚀 BULK IMPORT V2 - Agnostic Drupal Parser")
    print("=" * 60)
    
    all_grants = []
    consecutive_empty = 0
    
    for page in range(max_pages):
        print(f"\n📄 Fetching Page {page}...")
        
        params = {
            "page": page,
            "_wrapper_format": "drupal_ajax"
        }
        
        try:
            resp = requests.post(AJAX_URL, params=params, headers=HEADERS, timeout=20)
            
            if resp.status_code != 200:
                print(f"   ❌ HTTP Error: {resp.status_code}")
                break
            
            # Parse JSON
            try:
                json_data = resp.json()
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON Parse Error: {e}")
                # Dump raw response for debug
                with open("ajax_response_debug.txt", "w", encoding="utf-8") as f:
                    f.write(resp.text[:10000])
                break
            
            # DEBUG: Show JSON structure on first page
            if page == 0:
                print(f"   📊 JSON Response: {len(json_data)} items (type: {type(json_data).__name__})")
                if isinstance(json_data, list):
                    for i, item in enumerate(json_data[:5]):
                        if isinstance(item, dict):
                            print(f"      [{i}] keys: {list(item.keys())[:5]}")
            
            # EURISTICA: Find all large HTML blocks (> 1000 chars)
            large_blocks = find_large_html_blocks(json_data, min_length=1000)
            
            print(f"   🔍 Found {len(large_blocks)} large HTML blocks")
            
            if not large_blocks:
                # Try with smaller threshold
                large_blocks = find_large_html_blocks(json_data, min_length=200)
                print(f"   🔍 (Retry with 200 chars): Found {len(large_blocks)} blocks")
            
            # Combine all HTML blocks
            combined_html = ""
            for block in large_blocks:
                print(f"      - Path: {block['path']}, Length: {block['length']} chars")
                combined_html += block['content'] + "\n"
            
            # Dump HTML to file on first page for inspection
            if page == 0 and combined_html:
                with open("page_dump_v2.html", "w", encoding="utf-8") as f:
                    f.write(combined_html)
                print(f"   💾 Dumped HTML to page_dump_v2.html ({len(combined_html)} chars)")
            
            # Extract grants from HTML
            grants = extract_grants_from_html(combined_html)
            
            print(f"   ✅ Extracted {len(grants)} grants from page {page}")
            
            # Print found grants
            for g in grants[:5]:  # Show first 5
                print(f"      • {g['title'][:60]}...")
            if len(grants) > 5:
                print(f"      ... and {len(grants) - 5} more")
            
            if not grants:
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    print("\n⚠️ 3 consecutive empty pages. Stopping.")
                    break
            else:
                consecutive_empty = 0
                all_grants.extend(grants)
                
        except requests.RequestException as e:
            print(f"   ❌ Request Error: {e}")
            break
    
    # Final summary
    print("\n" + "=" * 60)
    print(f"🏁 IMPORT COMPLETE")
    print(f"   Total Grants Found: {len(all_grants)}")
    print("=" * 60)
    
    # Deduplicate by URL
    seen = set()
    unique_grants = []
    for g in all_grants:
        if g['url'] not in seen:
            seen.add(g['url'])
            unique_grants.append(g)
    
    print(f"   Unique Grants: {len(unique_grants)}")
    
    return unique_grants


if __name__ == "__main__":
    # Run and print results
    grants = run_bulk_import(max_pages=3)  # Start with 3 pages for testing
    
    print("\n📋 SAMPLE OUTPUT (First 10):")
    for i, g in enumerate(grants[:10], 1):
        print(f"{i:2}. {g['title'][:70]}")
        print(f"    URL: {g['url']}")
