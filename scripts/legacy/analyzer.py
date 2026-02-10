import logging
import json
import ollama
from sqlalchemy.orm import Session
from scraper.models import Bando, ProcessingStatus, get_engine, get_session
from analysis.models import BandoAnalysis

# Setup Logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Analyzer:
    def __init__(self, model_name="llama3"):
        self.engine = get_engine()
        self.session = get_session(self.engine)
        self.model_name = model_name

    def analyze_pending(self):
        """Fetch 'new' bandi from DB and analyze them."""
        # Get pending bandi
        pending_bandi = self.session.query(Bando).filter(Bando.status == ProcessingStatus.NEW).all()
        
        logger.info(f"Found {len(pending_bandi)} bandi to analyze.")
        
        for bando in pending_bandi:
            self.process_bando(bando)

    def process_bando(self, bando: Bando):
        logger.info(f"Analyzing Bando ID {bando.id}: {bando.title[:30]}...")
        
        # Construct Prompt
        # Note: We provide the clean JSON schema instruction implicitly via Pydantic schema in system prompt or user prompt
        # Newer Ollama versions support format="json" or even schema enforcement.
        # For wide compatibility, we'll ask for JSON and parse it.
        
        schema_desc = BandoAnalysis.model_json_schema()
        
        prompt = f"""
        Analizza il seguente TESTO DI BANDO e estrai le informazioni richieste in formato JSON rigoroso.
        
        OBIETTIVO: Sei un Consulente Senior di AlSolved. Il tuo compito è analizzare questo bando e spiegare a un imprenditore perché è un'opportunità imperdibile (o se non lo è).
        La 'sintesi' deve essere chiara, diretta e orientata al business (niente burocratese).
        IDENTIFICA CON PRECISIONE LA REGIONE: Se il bando è nazionale, scrivi "Nazionale". Se è per una regione specifica (es. Lombardia), scrivilo.
        
        SCHEMA RICHIESTO:
        {json.dumps(schema_desc, indent=2)}
        
        TESTO BANDO (Titolo: {bando.title}):
        {bando.raw_content[:7000]}  # Increased context window for deep fetch text
        
        Rispondi ESCLUSIVAMENTE con il JSON.
        """

        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'system', 'content': 'Sei AI-Solved, un assistente esperto in finanza agevolata. Estrai dati strategici per le aziende. Rispondi solo in JSON.'},
                {'role': 'user', 'content': prompt},
            ], format='json') # Force JSON mode if supported by local Ollama

            raw_json = response['message']['content']
            
            # Validation with Pydantic
            validated_data = BandoAnalysis.model_validate_json(raw_json)
            
            # Save to DB
            bando.ai_analysis = validated_data.model_dump()
            bando.status = ProcessingStatus.ANALYZED
            self.session.commit()
            
            logger.info(f"SUCCESS: Analyzed Bando {bando.id}")
            
        except Exception as e:
            logger.error(f"FAILED to analyze Bando {bando.id}: {e}")
            if 'raw_json' in locals():
                logger.error(f"RAW RESPONSE: {raw_json}")
            # bando.status = ProcessingStatus.ERROR # Optional: mark as error to avoid infinite retry loop
            # self.session.commit()

if __name__ == "__main__":
    # Ensure you strictly use the model name available on output user machine
    # e.g. "llama3" or "mistral"
    analyzer = Analyzer(model_name="llama3.2") # Updated to user's model
    analyzer.analyze_pending()
