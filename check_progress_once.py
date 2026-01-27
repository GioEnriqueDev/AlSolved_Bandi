import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scraper.models import Bando, ProcessingStatus
import json

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

engine = create_engine('sqlite:///bandi.db')
Session = sessionmaker(bind=engine)
session = Session()

def show_progress():
    total = session.query(Bando).count()
    analyzed = session.query(Bando).filter(Bando.status == ProcessingStatus.ANALYZED).count()
    
    # Check V2 specific fields (e.g., ai_analysis has 'is_expired')
    # Use simple string check for speed or json load
    # Let's check how many have 'is_expired' in the JSON string
    v2_completed = session.query(Bando).filter(Bando.ai_analysis.like('%"is_expired"%')).count()

    print(f"Total Bandi:    {total}")
    print(f"Analyzed:       {analyzed} ({(analyzed/total)*100:.1f}%)")
    print(f"V2 Cleaned:     {v2_completed} ({(v2_completed/total)*100:.1f}%)")
    
    # Get latest
    recent = session.query(Bando).filter(Bando.status == ProcessingStatus.ANALYZED).order_by(Bando.id.desc()).limit(3).all()
    print("\n Latest V2 Updates:")
    for b in recent:
        title = b.title[:50]
        try:
            if b.ai_analysis:
                d = json.loads(b.ai_analysis) if isinstance(b.ai_analysis, str) else b.ai_analysis
                reg = d.get('regions', ['?'])[0] if d.get('regions') else '?'
                exp = "EXPIRED" if d.get('is_expired') else "ACTIVE"
                print(f" - [{exp}] [{reg}] {title}...")
        except:
            print(f" - [Error parsing] {title}...")

if __name__ == "__main__":
    show_progress()
