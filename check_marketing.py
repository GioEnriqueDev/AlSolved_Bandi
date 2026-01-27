"""Check marketing text results."""
from scraper.models import init_db, Bando

session = init_db()

# Count with marketing text
with_mkt = session.query(Bando).filter(Bando.marketing_text.isnot(None)).count()
print(f"Bandi con marketing text: {with_mkt}")

# Sample
samples = session.query(Bando).filter(Bando.marketing_text.isnot(None)).limit(5).all()
print("\n📋 Esempi di testi marketing:")
for i, b in enumerate(samples, 1):
    print(f"\n{i}. {b.title[:50]}...")
    print(f"   ➡️ {b.marketing_text}")
