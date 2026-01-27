import requests
import json

url = "https://www.incentivi.gov.it/it/catalogo"
params = {
    "page": 1,
    "_wrapper_format": "drupal_ajax"
}

try:
    print(f"Testing {url} with params {params}...")
    resp = requests.post(url, params=params, timeout=10) # Drupal sometimes needs POST for ajax
    print(f"Status: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('Content-Type')}")
    
    if resp.status_code == 200:
        data = resp.json()
        print("JSON Valid!")
        print(json.dumps(data, indent=2)[:1000])
    else:
        print(f"Failed. Text: {resp.text[:200]}")
        
except Exception as e:
    print(f"Error: {e}")
