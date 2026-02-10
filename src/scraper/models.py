import hashlib
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum
import os

Base = declarative_base()

class ProcessingStatus(enum.Enum):
    NEW = "new"
    ANALYZED = "analyzed"
    MATCHED = "matched"
    ERROR = "error"

class Bando(Base):
    __tablename__ = 'bandi'

    id = Column(Integer, primary_key=True)
    
    # Core Identification
    url = Column(String, nullable=False)
    url_hash = Column(String(64), unique=True, nullable=False, index=True) # SHA256 of URL for deduplication
    
    # Content
    title = Column(String)
    raw_content = Column(Text) # HTML or Text content
    source_name = Column(String) # e.g., "MIMIT", "Lombardia"
    
    # Metadata
    ingested_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.NEW)
    
    # AI Extractions (JSONB for flexibility)
    ai_analysis = Column(JSON, nullable=True)
    
    # Marketing Layer - Testo persuasivo per conversione
    marketing_text = Column(Text, nullable=True) 

    def __repr__(self):
        return f"<Bando(title='{self.title}', source='{self.source_name}')>"

    @staticmethod
    def generate_hash(url):
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

# Database Connection
# Use SQLite for local testing if no env var is set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/db/bandi.db")

def get_engine():
    return create_engine(DATABASE_URL)

def create_tables(engine):
    Base.metadata.create_all(engine)

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    engine = get_engine()
    create_tables(engine)
    return get_session(engine)
