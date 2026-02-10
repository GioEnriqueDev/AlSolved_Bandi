import json
import sqlite3
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "db" / "bandi.db"
OUTPUT_PATH = BASE_DIR / "frontend" / "public" / "bandi.json"

def export_to_json():
    print(f"Reading from database: {DB_PATH}")
    if not DB_PATH.exists():
        print("❌ Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query all processed bandi
    cursor.execute("""
        SELECT id, url, title, ai_analysis, marketing_text, status, ingested_at
        FROM bandi
        WHERE status IN ('ANALYZED', 'MATCHED', 'analyzed', 'matched')
        ORDER BY ingested_at DESC
        LIMIT 200
    """)
    
    rows = cursor.fetchall()
    bandi = []
    
    for row in rows:
        bando = dict(row)
        
        # Parse JSON fields
        if bando['ai_analysis']:
            try:
                bando['ai_analysis'] = json.loads(bando['ai_analysis'])
            except:
                bando['ai_analysis'] = {}
        
        bandi.append(bando)
        
    conn.close()
    
    # Save to JSON
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(bandi, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Exported {len(bandi)} bandi to {OUTPUT_PATH}")

if __name__ == "__main__":
    export_to_json()
