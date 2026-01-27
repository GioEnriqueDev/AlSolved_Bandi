import requests
import json

urls = [
    "https://www.incentivi.gov.it/index.php/api/v1/incentivi",
    "https://www.incentivi.gov.it/api/v1/incentivi"
]

for url in urls:
    try:
        print(f"Testing {url}...")
        resp = requests.get(url, params={"page": 0}, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            try:
                data = resp.json()
                print("JSON Valid!")
                print(str(data)[:500])
                break
            except:
                print("Not JSON Content")
    except Exception as e:
        print(f"Error: {e}")
