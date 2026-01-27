"""Quick check of imported bandi."""
from scraper.models import init_db, Bando

session = init_db()

# Total count
total = session.query(Bando).count()
print(f"Total bandi in DB: {total}")

# From Solr import
solr_count = session.query(Bando).filter(Bando.source_name.like('%Solr%')).count()
print(f"From Solr import: {solr_count}")

# Sample entries
print("\n📋 Sample Bandi from Solr import:")
bandi = session.query(Bando).filter(Bando.source_name.like('%Solr%')).limit(10).all()

for i, b in enumerate(bandi, 1):
    print(f"\n{i}. {b.title[:70]}...")
    print(f"   URL: {b.url}")
    print(f"   Status: {b.status}")
