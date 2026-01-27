from typing import List, Optional
from pydantic import BaseModel, Field

class BandoAnalysis(BaseModel):
    """
    Modello strutturato per l'analisi approfondita di un bando.
    L'AI DEVE restituire dati conformi a questo schema.
    """
    titolo_riassuntivo: str = Field(..., description="Un titolo breve ed efficace per il bando.")
    sintesi: str = Field(..., description="Riassunto strutturato del bando (max 300 caratteri).")
    
    scadenza: Optional[str] = Field(None, description="Data di scadenza in formato YYYY-MM-DD o 'A sportello'.")
    scadenza_descrizione: Optional[str] = Field(None, description="Dettagli sulla scadenza (es. 'Fino a esaurimento fondi').")
    
    budget_totale: Optional[str] = Field(None, description="Budget totale stanziato per il bando.")
    max_finanziamento: Optional[str] = Field(None, description="Contributo massimo ottenibile per singola impresa.")
    percentuale_contributo: Optional[str] = Field(None, description="Percentuale di copertura (es. '50% a fondo perduto').")
    
    beneficiari: List[str] = Field(..., description="Lista precisa dei beneficiari (es. ['PMI', 'Startup', 'Grandi Imprese']).")
    settori_ammessi: List[str] = Field(..., description="Settori specifici ammessi (es. ['Agricoltura', 'Turismo', 'Manifatturiero']).")
    spese_ammissibili: List[str] = Field(..., description="Lista delle spese finanziabili (es. ['Hardware', 'Consulenza', 'Marketing']).")
    
    punteggio_complessita: str = Field(..., description="Stima complessità burocratica (es. 'Alto', '5/10', 'Basso').")
    
    regione: Optional[str] = Field(None, description="Regione o area geografica di riferimento (es. 'Lombardia', 'Nazionale', 'Sicilia').")
    
    match_keywords: List[str] = Field(..., description="Parole chiave per il matching (es. 'digitalizzazione', 'green', 'femminile').")
