# Integrazione HubSpot

**Obiettivo**: Creare un Deal o una Nota quando viene rilevato un bando pertinente.

## Mappatura Campi (JSON -> HubSpot Property)

| Bando JSON Field | HubSpot Property Name | Tipo |
| :--- | :--- | :--- |
| `title` | `dealname` | String |
| `budget` | `amount` | Number/String |
| `expiration_date` | `closedate` | Date |
| `url` | `bando_url_source` (Custom) | URL |
| `description` | `description` | Multi-line Text |

## Logica "Targeting"
1. Il sistema interroga HubSpot Search API (`POST /crm/v3/objects/companies/search`).
2. Filtri:
   - `industry` IN `bando.beneficiaries`
   - `region` IN `bando.regions` (se disponibile)
3. Per ogni match:
   - Creare un Deal associato all'azienda.
   - Stage: "Nuova Opportunità" (Pipeline ID: `default`).
