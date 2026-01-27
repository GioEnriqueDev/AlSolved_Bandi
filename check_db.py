from scraper.models import get_session, Bando, init_db
s = init_db()
print(f"Total Bandi: {s.query(Bando).count()}")
print(f"Gov Bandi: {s.query(Bando).filter(Bando.source_name=='Incentivi.gov.it').count()}")
