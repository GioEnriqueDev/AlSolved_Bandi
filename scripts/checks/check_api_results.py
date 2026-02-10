
import requests
import json

try:
    response = requests.get("http://localhost:8000/bandi", params={"status": "analyzed", "size": 3})
    response.raise_for_status()
    data = response.json()
    
    with open("api_verification.txt", "w", encoding="utf-8") as f:
        f.write("-" * 50 + "\n")
        f.write(f"✅ API returned {len(data)} items\n")
        f.write("-" * 50 + "\n")
        
        for b in data:
            f.write(f"ID: {b['id']}\n")
            f.write(f"Status: {b.get('status')}\n")
            f.write(f"Title: {b['title']}\n")
            f.write(f"Marketing Text: {b['marketing_text']}\n")
            
            analysis = b.get('ai_analysis')
            if analysis:
                if isinstance(analysis, str):
                    import json
                    try: analysis = json.loads(analysis)
                    except: analysis = {}
                f.write(f"Regions: {analysis.get('regioni')}\n")
            else:
                f.write("Regions: N/A\n")
            
            f.write("-" * 50 + "\n")
            
        print("Output written to api_verification.txt")
        
except Exception as e:
    print(f"❌ Error fetching from API: {e}")
