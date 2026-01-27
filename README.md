# AlSolved - Sistema Cacciatore di Bandi AI

## Obiettivo
Trasformare la ricerca di incentivi pubblici da una ricerca manuale e lenta a un servizio proattivo, istantaneo e automatizzato.

## Il Flusso Logico
1.  **Monitoraggio (The Scraper)**: Monitoraggio periodico dei portali istituzionali (Ministeri, Regioni, Incentivi.gov).
2.  **Analisi Intelligente (The Brain)**: Analisi dei bandi (testo/PDF) tramite AI (GPT-4o) per estrarre dati chiave (Budget, Scadenza, Beneficiari, Spese ammissibili).
3.  **Customer Match**: Confronto con il database clienti HubSpot per identificare le migliori opportunità.
4.  **Delivery (The Output)**: Generazione report HTML/PDF, notifica cliente e apertura Deal su HubSpot.

## Struttura del Progetto
- `scraper/`: Script e configurazioni per il monitoraggio dei portali.
- `analysis/`: Logica di estrazione dati e prompt AI.
- `hubspot_integration/`: Integrazione con HubSpot CRM.
- `delivery/`: Template e logica per la generazione dei report e notifiche.
- `docs/`: Documentazione tecnica e architettonica.
