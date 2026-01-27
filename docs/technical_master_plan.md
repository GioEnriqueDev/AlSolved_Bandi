# AlSolved: Definitive Master Plan

**Strategia**: Architettura Enterprise (Python + Docker + AI Locale) su VPS.
**Obiettivo**: Scalare da 1 a 100.000 utenti con privacy totale e costi fissi bassi.

---

## 🛠️ Lo Stack Tecnologico (Il Motore)

| Livello | Tecnologia | Funzione |
| :--- | :--- | :--- |
| **Infrastruttura** | Docker & Docker Compose | Contenitori isolati per gestire tutto il software. |
| **Backend & Logic** | Python 3.11+ | Il cervello. Gestisce scraping, logica di matching e API. |
| **AI Engine** | Ollama (Llama 3 / Mistral) | L'intelligenza locale. Analizza testi, riassume e calcola punteggi. |
| **Database** | PostgreSQL | La memoria blindata. Salva bandi, utenti e match. |
| **Data Validation** | Pydantic | Il poliziotto. Assicura che l'AI non sbagli mai il formato dei dati. |
| **API Layer** | FastAPI | Il cameriere. Espone i dati dal backend al sito web in millisecondi. |
| **Frontend** | Next.js (React) | L'interfaccia utente moderna. Veloce e SEO-friendly. |
| **UI Library** | Tailwind CSS + Shadcn/UI | I mattoncini grafici per un design professionale. |
| **Integrazione** | HubSpot API | Il ponte commerciale. Sincronizza lead e deal in tempo reale. |

---

## 🗺️ LA ROADMAP OPERATIVA (4 Fasi)

### 📍 FASE 1: THE INGESTION (Il Collettore Dati)
**Obiettivo**: Creare un database che si riempie automaticamente di bandi "grezzi" 24/7.
**Focus**: Stabilità e Pulizia Dati.

*   **Setup VPS**: Configurazione ambiente Linux (Ubuntu), Firewall UFW, Docker Engine.
*   **Sviluppo Scraper (Python)**:
    *   **Modulo RSS**: `feedparser` per monitorare MIMIT e Regioni (tempo reale).
    *   **Modulo HTML**: `requests` + `BeautifulSoup` (con rotazione User-Agent) per i siti ostici.
*   **Deduplicazione**: Hashing (MD5/SHA) sul link per evitare duplicati.
*   **Database Schema**: Tabella SQL `raw_grants` (Titolo, Link, Fonte, Data, HTML_Grezzo).

**✅ Output F1**: Un server che accumula dati silenziosamente ogni ora.

### 🧠 FASE 2: THE REFINERY (L'Analisi AI)
**Obiettivo**: Trasformare l'HTML burocratico in dati strutturati e leggibili.
**Focus**: Eliminazione errori JSON e generazione "One-Pager".

*   **Ollama Integration**: Script Python che invia i bandi all'LLM locale.
*   **Validazione Pydantic**: Definizione della classe `BandoModel`.
*   **Analisi Semantica**: Estrazione automatica (Scadenza, Budget, ATECO).
*   **Generazione Sintesi**: "Spiegato a un bambino di 5 anni".
*   **PDF Generator**: Creazione automatica PDF brandizzato (WeasyPrint).

**✅ Output F2**: Database `clean_grants` con dati perfetti e PDF pronti.

### 🎯 FASE 3: THE MATCHMAKER (Il Cuore del Business)
**Obiettivo**: Creare il sistema che incrocia Aziende <-> Bandi.
**Focus**: Algoritmo di Raccomandazione.

*   **API Backend**: Endpoint FastAPI per ricevere dati utente.
*   **Logica di Matching a Imbuto**:
    1.  **SQL Hard Filter**: Regione Azienda == Regione Bando?
    2.  **Keyword/Vector**: Matching parole chiave/vettoriale.
    3.  **AI Scoring**: Ollama valuta compatibilità (0-100%) e motiva.
*   **HubSpot Sync**:
    *   Match > 80% -> Crea Deal su HubSpot e notifica commerciale.

**✅ Output F3**: Un motore intelligente che qualifica i lead mentre dormi.

### 🌐 FASE 4: THE PLATFORM (L'Esperienza Utente)
**Obiettivo**: L'interfaccia pubblica dove le aziende si registrano e vedono i risultati.
**Focus**: UX/UI e Conversione.

*   **Sviluppo Frontend (Next.js)**:
    *   **Landing Page**: "Scopri i fondi per la tua impresa".
    *   **Smart Form**: Wizard di registrazione.
    *   **Dashboard Personale**: Design con "semaforo" verde/giallo/rosso.
*   **Deploy Finale**: Container Frontend su VPS (Nginx + SSL).

**✅ Output F4**: Il prodotto finito, lanciabile sul mercato.

---

## 🚀 Strategia di Deploy (Migrazione Locale -> VPS)

Il passaggio al server di produzione sarà **indolore** e veloce, grazie all'architettura Docker-first.

### **Perché è facile?**
Non dovremo reinstallare Python, librerie o database manualmente. Spostiamo i "container" (pacchetti chiusi) dal tuo PC al server.

### **La Procedura in 4 Step:**
1.  **Git Clone**: Scarichiamo tutto il codice sul VPS in 3 secondi.
2.  **Environment Setup**: Copiamo il file `.env` con le password sicure.
3.  **Docker Up**: Un solo comando (`docker-compose up -d --build`) avvia Database, Backend, Frontend e AI simultaneamente.
4.  **AI Download**: Al primo avvio, Ollama scaricherà il modello (Llama 3) automaticamente.

**Requisiti VPS:**
- **RAM**: Almeno 16GB (per far girare l'AI fluidamente).
- **CPU**: 4+ vCPU.
- **GPU**: Opzionale ma consigliata per velocità (es. NVIDIA T4), altrimenti useremo la CPU (più lento ma funzionante).
