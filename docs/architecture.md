# Architettura del Sistema

## 1. Monitoraggio (The Scraper)
**Obiettivo**: Intercettare nuovi bandi appena vengono pubblicati.

### Logica Prototipo (Make.com)
1.  **Trigger**: HTTP Request (Scansione della pagina catalogo/feed RSS).
2.  **Parsing**: Text Parser (Isolamento della lista bandi dal codice HTML).
3.  **Brain**: OpenAI (Analisi e generazione del riassunto/estrazione dati).
4.  **Action**: HubSpot (Creazione Deal o Nota sul cliente).

### Target Futuro (Python)
- Script Python schedulati h24.
- **Output**: Oggetto JSON grezzo del bando o link al PDF/Pagina Web.

## 2. Analisi Intelligente (The Brain)
**Obiettivo**: Convertire burocratese in dati strutturati.
**Tecnologia**: Ollama
**Input**: Testo bando o PDF.
**Processo**:
- OCR/Text Extraction (se necessario).
- Prompt Engineering per estrazione campi specifici.
**Output**: Oggetto JSON standardizzato (Schema `Bando`).

## 3. Customer Match
**Obiettivo**: Matchare il bando con i clienti ideali.
**Tecnologia**: HubSpot API / Python Logic.
**Processo**:
- Query su database aziende HubSpot.
- Scoring di affinità (Settore, Fatturato, Regione).
**Output**: Lista di `Deal` potenziali.

## 4. Delivery (The Output)
**Obiettivo**: Comunicare l'opportunità.
**Canali**:
- Report HTML/PDF "Bando Lampo".
- Email di notifica.
- Creazione (Deal) in pipeline HubSpot per il consulente.
