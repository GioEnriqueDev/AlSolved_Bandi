import time
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from scraper.models import Bando, ProcessingStatus

# Connect to DB
engine = create_engine('sqlite:///bandi.db')
Session = sessionmaker(bind=engine)
session = Session()

def show_progress():
    total = session.query(Bando).count()
    analyzed = session.query(Bando).filter(Bando.status == ProcessingStatus.ANALYZED).count()
    gold = session.query(Bando).filter(Bando.marketing_text.isnot(None)).count()
    
    # Get last 5 analyzed
    recent = session.query(Bando).filter(Bando.status == ProcessingStatus.ANALYZED).order_by(Bando.id.desc()).limit(5).all()
    
    print("\n" + "="*50)
    print(f"📊 GEMINI ANALYSIS PROGRESS")
    print("="*50)
    print(f"Total Bandi:    {total}")
    print(f"Analyzed:       {analyzed} ({(analyzed/total)*100:.1f}%)")
    print(f"Gold/Marketing: {gold}")
    print("-" * 50)
    print("Latest Analyzed:")
    for b in recent:
        title = b.ai_analysis.get('titolo_riassuntivo', b.title[:30]) if b.ai_analysis else b.title[:30]
        print(f" - [ID {b.id}] {title}")
    print("="*50 + "\n")

if __name__ == "__main__":
    while True:
        show_progress()
        time.sleep(5)
