"""
import_bulk_v3.py - API Endpoint Discovery & Testing
=====================================================
Il page_dump_v2.html mostra che i bandi NON sono nell'HTML iniziale.
<div class="views-element-container" data-incentivi-list> è VUOTO!

Strategia:
1. Prova endpoint REST standard di Drupal
2. Intercetta il vero endpoint usato dal frontend
3. Testa diversi format (json_api, hal_json, etc.)
"""

import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/html, */*",
    "X-Requested-With": "XMLHttpRequest",
}

# Lista di possibili endpoint da testare
ENDPOINTS_TO_TRY = [
    # Standard Views REST export
    ("REST Views JSON", "https://www.incentivi.gov.it/api/incentivi?page=0"),
    ("REST Views JSON Alt", "https://www.incentivi.gov.it/jsonapi/incentivi"),
    ("REST Views JSON Alt 2", "https://www.incentivi.gov.it/it/api/incentivi"),
    
    # Drupal JSON:API standard paths
    ("JSON:API Node", "https://www.incentivi.gov.it/jsonapi/node/incentivo"),
    ("JSON:API Node IT", "https://www.incentivi.gov.it/it/jsonapi/node/incentivo"),
    
    # Views AJAX con parametri diversi
    ("Views AJAX view_name", "https://www.incentivi.gov.it/views/ajax?view_name=catalogo&view_display_id=block_1"),  
    ("Views AJAX page 0", "https://www.incentivi.gov.it/views/ajax?view_name=catalogo&page=0"),
    
    # Ricerca semantica
    ("Search API", "https://www.incentivi.gov.it/api/search?q=*"),
    
    # Direct node listing
    ("Node List", "https://www.incentivi.gov.it/it/catalogo?_format=json"),
    ("Node List API", "https://www.incentivi.gov.it/it/catalogo?format=json"),
    
    # GraphQL (less likely but possible)
    ("GraphQL", "https://www.incentivi.gov.it/graphql"),
]

def test_endpoint(name, url, method="GET"):
    """Test a single endpoint and report results."""
    print(f"\n🔍 Testing: {name}")
    print(f"   URL: {url}")
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=HEADERS, timeout=10)
        else:
            resp = requests.post(url, headers=HEADERS, timeout=10)
            
        print(f"   Status: {resp.status_code}")
        print(f"   Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
        print(f"   Size: {len(resp.content)} bytes")
        
        # Check if it's JSON
        content_type = resp.headers.get('Content-Type', '')
        
        if 'json' in content_type.lower():
            try:
                data = resp.json()
                if isinstance(data, list):
                    print(f"   ✅ JSON ARRAY with {len(data)} items!")
                    if len(data) > 0:
                        print(f"   First item keys: {list(data[0].keys())[:5] if isinstance(data[0], dict) else 'not a dict'}")
                elif isinstance(data, dict):
                    print(f"   ✅ JSON OBJECT with keys: {list(data.keys())[:8]}")
                    # Check for common pagination patterns
                    if 'data' in data:
                        print(f"   └─ 'data' field has {len(data['data'])} items" if isinstance(data['data'], list) else f"   └─ 'data' type: {type(data['data'])}")
                    if 'results' in data:
                        print(f"   └─ 'results' field has {len(data['results'])} items")
                    if 'rows' in data:
                        print(f"   └─ 'rows' field has {len(data['rows'])} items")
                return resp.status_code == 200 and len(resp.content) > 500
            except json.JSONDecodeError:
                print(f"   ⚠️ Content-Type says JSON but parsing failed")
        else:
            # Check if HTML contains grant-like content
            if resp.status_code == 200:
                text = resp.text[:2000]
                if 'incentivo' in text.lower() or 'bando' in text.lower():
                    print(f"   ⚠️ HTML response but contains 'incentivo'/'bando' keywords")
                    # Save for inspection
                    with open(f"endpoint_test_{name.replace(' ', '_').replace('/', '_')}.html", "w", encoding="utf-8") as f:
                        f.write(resp.text[:50000])
                        
    except requests.RequestException as e:
        print(f"   ❌ Request Error: {e}")
        
    return False


def discover_real_api():
    """Try multiple approaches to find the real data endpoint."""
    print("=" * 70)
    print("🕵️ ENDPOINT DISCOVERY MODE")
    print("=" * 70)
    
    found = []
    
    for name, url in ENDPOINTS_TO_TRY:
        if test_endpoint(name, url):
            found.append((name, url))
    
    # Also try POST endpoints
    print("\n--- POST Endpoints ---")
    post_endpoints = [
        ("POST views/ajax", "https://www.incentivi.gov.it/views/ajax"),
    ]
    
    for name, url in post_endpoints:
        # Try with form data
        try:
            form_data = {
                "view_name": "catalogo",
                "view_display_id": "block_1",
                "page": "0",
            }
            resp = requests.post(url, data=form_data, headers=HEADERS, timeout=10)
            print(f"\n🔍 Testing: {name} (POST with form_data)")
            print(f"   Status: {resp.status_code}, Size: {len(resp.content)} bytes")
            
            if resp.status_code == 200 and len(resp.content) > 500:
                # Save for inspection
                with open("views_ajax_post_response.json", "w", encoding="utf-8") as f:
                    f.write(resp.text[:100000])
                print(f"   💾 Saved to views_ajax_post_response.json")
                
                # Try to parse
                try:
                    data = resp.json()
                    print(f"   JSON parsed. Type: {type(data).__name__}")
                    if isinstance(data, list):
                        print(f"   Commands: {len(data)}")
                        for cmd in data[:5]:
                            if isinstance(cmd, dict):
                                print(f"      - command: {cmd.get('command')}, data length: {len(str(cmd.get('data', '')))}")
                except:
                    pass
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 70)
    if found:
        print("✅ PROMISING ENDPOINTS FOUND:")
        for name, url in found:
            print(f"   • {name}: {url}")
    else:
        print("❌ No direct API endpoints found. Data is likely loaded via JS frontend.")
        print("   💡 Consider using browser automation (Playwright/Selenium) or")
        print("      inspecting the actual network requests in browser DevTools.")
    print("=" * 70)


if __name__ == "__main__":
    discover_real_api()
