from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel

# Schema for the AI Analysis part (nested)
class AnalysisSchema(BaseModel):
    titolo_riassuntivo: Optional[str] = None
    sintesi: Optional[str] = None
    scadenza: Optional[str] = None
    scadenza_descrizione: Optional[str] = None
    budget_totale: Optional[str] = None
    max_finanziamento: Optional[str] = None
    percentuale_contributo: Optional[str] = None
    beneficiari: List[str] = []
    settori_ammessi: List[str] = []
    spese_ammissibili: List[str] = []
    punteggio_complessita: Optional[str] = None
    match_keywords: List[str] = []

# Schema for the full Bando response
class BandoResponse(BaseModel):
    id: int
    url: str
    title: str
    source_name: str
    status: Any
    ingested_at: datetime
    raw_content: Optional[str] = None
    # The analysis might be null if not yet processed
    # Using Any to support both legacy analysis schema and new Solr metadata
    ai_analysis: Optional[Any] = None
    # Marketing text for sales conversion
    marketing_text: Optional[str] = None

    class Config:
        from_attributes = True
