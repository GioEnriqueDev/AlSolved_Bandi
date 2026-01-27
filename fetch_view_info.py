import requests
import re
import sys

# Fake header to look like a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

url = "https://www.incentivi.gov.it/it/catalogo"
try:
    resp = requests.get(url, headers=headers, timeout=30)
    content = resp.text
    
    print(f"Status: {resp.status_code}")
    print(f"Length: {len(content)}")
    
    print("--- SNIPPET ---")
    print(content[:1000].encode('utf-8', errors='ignore').decode('utf-8'))
    print("--- END SNIPPET ---")

    # Relaxed Regex
    view_ids = re.findall(r'view-id-([a-zA-Z0-9_\-]+)', content)
    display_ids = re.findall(r'view-display-id-([a-zA-Z0-9_\-]+)', content)
    
    print(f"View IDs: {set(view_ids)}")
    print(f"Display IDs: {set(display_ids)}")

except Exception as e:
    print(f"Error: {e}")
