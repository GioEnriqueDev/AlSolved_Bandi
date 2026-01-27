
from scraper.models import init_db, Bando

def inspect():
    session = init_db()
    bandi = session.query(Bando).limit(3).all()
    
    with open("raw_inspection.txt", "w", encoding="utf-8") as f:
        for b in bandi:
            f.write(f"ID: {b.id}\n")
            f.write(f"Title: {b.title}\n")
            f.write(f"Raw Content (Start): {b.raw_content[:200] if b.raw_content else 'None'}\n")
            f.write(f"AI Analysis: {b.ai_analysis}\n")
            f.write("-" * 50 + "\n")

    print("Inspection written to raw_inspection.txt")

if __name__ == "__main__":
    inspect()
