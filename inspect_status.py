
from scraper.models import init_db, Bando, ProcessingStatus
from sqlalchemy import func

def inspect_status():
    session = init_db()
    # Get distinct statuses
    statuses = session.query(Bando.status).distinct().all()
    print("Distinct Statuses found in DB:")
    for s in statuses:
        print(f" - {s[0]} (Type: {type(s[0])})")
        if hasattr(s[0], 'value'):
             print(f"   Value: {s[0].value}")

    # Count analyzed
    count = session.query(Bando).filter(Bando.status == ProcessingStatus.ANALYZED).count()
    print(f"Count via Enum: {count}")
    
    count_str = session.query(Bando).filter(Bando.status == "analyzed").count()
    print(f"Count via String 'analyzed': {count_str}")

if __name__ == "__main__":
    inspect_status()
