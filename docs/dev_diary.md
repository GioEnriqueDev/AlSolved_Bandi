# Diario di Sviluppo (Dev Diary)

Questo documento traccia ogni singola implementazione tecnica, decisione architetturale e libreria utilizzata. Servirà come base per la "Documentazione Assurda" finale.

## 📅 14 Gennaio 2026 - FASE 1: THE INGESTION

### 1. Infrastruttura (Docker)
- Creato `docker-compose.yml` con due servizi:
  - **db**: PostgreSQL 15 Alpine (leggero e robusto).
  - **scraper**: Container Python 3.10 custom.
- Volume persistente `postgres_data` per non perdere i bandi al riavvio.

### 2. Database (SQLAlchemy)
- Definito modello `Bando` in `scraper/models.py`.
- **Deduplicazione**: Implementata tramite colonna `url_hash` (SHA256 dell'URL). Questo garantisce l'idempotenza (possiamo lanciare lo scraper 100 volte, salverà il bando solo la prima volta).
- **Stati**: Enum `ProcessingStatus` (NEW, ANALYZED, MATCHED, ERROR) per gestire il ciclo di vita del dato.

### 3. Ingestione (The Scraper)
- **RSS**: Utilizzato `feedparser` per fonti strutturate (es. MIMIT).
- **HTML**: Creato modulo `HtmlScraper` (`scraper/html_module.py`) che simula un browser reale.
  - **Anti-Bot**: Implementata rotazione randomica di 4 User-Agent diversi.
  - **Resilienza**: Logica di `retry` (3 tentativi) con attesa esponenziale in caso di errore.
- **Scheduler**: Utilizzato `APScheduler` (`BlockingScheduler`) per eseguire il ciclo di scansione ogni **60 minuti**.

### 🔧 Stack Tecnico Implementato
- `sqlalchemy` + `psycopg2-binary`: ORM Database.
- `feedparser`: Parsing RSS/Atom.
- `requests` + `beautifulsoup4`: Scraping HTML.
- `apscheduler`: Scheduling task periodici.
