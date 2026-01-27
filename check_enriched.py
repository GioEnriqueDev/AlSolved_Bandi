"""Quick check enriched data."""
from scraper.models import init_db, Bando
import json

session = init_db()

# Count enriched records
with_ateco = session.query(Bando).filter(Bando.ai_analysis.like('%ateco%')).count()
with_financial = session.query(Bando).filter(Bando.ai_analysis.like('%financial%')).count()

print(f"Bandi con ATECO codes: {with_ateco}")
print(f"Bandi con dati finanziari: {with_financial}")

# Sample
sample = session.query(Bando).filter(Bando.ai_analysis.like('%ateco%')).first()
if sample:
    print(f"\n📋 Esempio arricchito:")
    print(f"   Titolo: {sample.title[:60]}...")
    try:
        data = json.loads(sample.ai_analysis) if isinstance(sample.ai_analysis, str) else sample.ai_analysis
        print(f"   ATECO: {data.get('ateco_codes', 'N/A')[:100]}")
        print(f"   Min: {data.get('financial_min', 'N/A')}")
        print(f"   Max: {data.get('financial_max', 'N/A')}")
    except:
        print(f"   Raw: {str(sample.ai_analysis)[:200]}")
