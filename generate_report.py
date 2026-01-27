
from scraper.models import init_db, Bando, ProcessingStatus
import json
from collections import Counter

def generate_report():
    session = init_db()
    
    # metrics
    total_analyzed = session.query(Bando).filter(Bando.status == ProcessingStatus.ANALYZED).count()
    
    # Fetch recent ones (assuming we just ran it, let's grab last 100 analyzed)
    recent_bandi = session.query(Bando).filter(Bando.status == ProcessingStatus.ANALYZED).order_by(Bando.id.desc()).limit(50).all()
    
    real_bandi_count = 0
    news_count = 0
    gold_count = 0
    
    regions_counter = Counter()
    types_counter = Counter()
    
    print("="*60)
    print("📊 REPORT ANALISI BANDI (ULTIMI 50)")
    print("="*60)
    
    for b in recent_bandi:
        if not b.ai_analysis:
            continue
            
        data = b.ai_analysis
        if isinstance(data, str):
            try: data = json.loads(data)
            except: continue
        
        # Check is_bando
        is_bando = data.get("is_bando", False)
        
        if is_bando:
            real_bandi_count += 1
            if data.get("is_gold"):
                gold_count += 1
                
            # Count regions
            regs = data.get("regioni", [])
            if isinstance(regs, list):
                for r in regs: regions_counter[r] += 1
            elif isinstance(regs, str):
                regions_counter[regs] += 1
                
            # Count Types
            t = data.get("tipo_agevolazione", "N/D")
            types_counter[t] += 1
        else:
            news_count += 1

    print(f"Total processed in this batch check: {len(recent_bandi)}")
    print(f"✅ Bandi Reali (Fondi disponibili): {real_bandi_count}")
    print(f"📰 News/Comunicati: {news_count}")
    print(f"🏆 Bandi GOLD (Alta priorità): {gold_count}")
    print("-" * 30)
    print("TOP REGIONI:")
    for reg, count in regions_counter.most_common(5):
        print(f"  - {reg}: {count}")
    print("-" * 30)
    print("TIPOLOGIA AGEVOLAZIONE:")
    for t, count in types_counter.most_common(5):
        print(f"  - {t}: {count}")
    print("="*60)

if __name__ == "__main__":
    generate_report()
