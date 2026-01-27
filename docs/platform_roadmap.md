# AlSolved Vision: "The AI Grant Hunter"

## Competitor Analysis: Contributi Europa
Il modello attuale (es. Contributi Europa) è una **Directory Passiva**:
- ❌ L'utente deve cercare manualmente.
- ❌ I dati chiave sono nascosti (Paywall).
- ❌ L'UX è datata (liste, filtri statici).
- ❌ Nessuna integrazione diretta con il CRM aziendale.

## AlSolved Vision: Piattaforma Proattiva
Noi costruiremo un **Motore Attivo**:
- ✅ **Push, non Pull**: Il sistema notifica automaticamente quando esce un bando perfetto per un cliente.
- ✅ **AI-First**: Riassunti esecutivi generati da GPT-4o, non muri di testo. "Chat with Data".
- ✅ **Semantic Search**: "Trovami bandi per startup green in Lombardia" invece di selezionare 4 filtri.
- ✅ **HubSpot Native**: Creazione automatica di Deal pronti per la vendita.

---

## Technical Stack (La "Better Backend")

### 1. Backend: Python FastAPI
- **Perché**: Prestazioni elevate, supporto nativo per asincronia (utile per scraper multipli), ecosistema AI (LangChain, OpenAI SDK).
- **Ruolo**: API REST, Orchestratore Scraper, Gestore Utenti.

### 2. Database: PostgreSQL + Vector
- **Dati Relazionali**: Utenti, Aziende, Bandi standard.
- **Search Vectoriale (pgvector)**: Per permettere la ricerca semantica ("finanziamenti per capannoni") e il matching intelligente aziende-bandi.

### 3. Frontend: Next.js + Tailwind CSS
- **Design**: "Premium & Cinematic" (come da stile AlSolved).
- **Features**: Dashboard interattiva, Card animate, rendering server-side per SEO.

### 4. Infrastructure
- **Docker**: Containerizzazione per deployment facile.
- **Celery/Redis**: Coda di task per lo scraping massivo e l'analisi AI in background.

---

## Implementazione Roadmap

### Fase 1: Foundation (Backend Core)
- Setup FastAPI project structure.
- Setup PostgreSQL con Docker.
- Definizione Modelli DB (SQLAlchemy/Pydantic).

### Fase 2: The Scraper Engine (Python)
- Migrazione logica da Make.com a Python scripts.
- Scheduler (es. APScheduler) per esecuzione h24.

### Fase 3: The Brain (AI Integration)
- API per ricevere testo RAW e restituire JSON pulito.
- Integrazione Vector Store per matching.

### Fase 4: Frontend "Wow"
- Dashboard "Mission Control" per i consulenti.
- Report interattivi per i clienti.
