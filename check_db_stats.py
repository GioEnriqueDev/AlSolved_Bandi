
import sys
import os
from sqlalchemy import func
from scraper.models import init_db, Bando, ProcessingStatus

def check_stats():
    session = init_db()
    
    total = session.query(Bando).count()
    new = session.query(Bando).filter(Bando.status == ProcessingStatus.NEW).count()
    analyzed = session.query(Bando).filter(Bando.status == ProcessingStatus.ANALYZED).count()
    error = session.query(Bando).filter(Bando.status == ProcessingStatus.ERROR).count()
    
    # Check for empty analysis even if status is ANALYZED
    empty_analysis = session.query(Bando).filter(Bando.status == ProcessingStatus.ANALYZED, Bando.ai_analysis == None).count()
    
    print("-" * 30)
    print("DATABASE STATISTICS")
    print("-" * 30)
    print(f"Total Bandi:    {total}")
    print(f"Status NEW:     {new}")
    print(f"Status ANALYZED:{analyzed}")
    print(f"Status ERROR:   {error}")
    print(f"Analyzed but NULL content: {empty_analysis}")
    print("-" * 30)
    
    # Sample logic
    if analyzed > 0:
        sample = session.query(Bando).filter(Bando.status == ProcessingStatus.ANALYZED).first()
        print("\nSAMPLE ANALYZED BANDO:")
        print(f"ID: {sample.id}")
        print(f"Title: {sample.title}")
        print(f"Marketing Text: {sample.marketing_text}")
        print(f"AI Analysis JSON: {sample.ai_analysis}")

if __name__ == "__main__":
    check_stats()
