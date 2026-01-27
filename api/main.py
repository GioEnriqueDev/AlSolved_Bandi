from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from scraper.models import get_engine, get_session, Bando, ProcessingStatus
from api.schemas import BandoResponse

app = FastAPI(
    title="AlSolved API",
    description="Backend API for AlSolved Grant Hunter Platform",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    engine = get_engine()
    db = get_session(engine)
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to AlSolved API. Go to /docs for Swagger UI."}

@app.get("/bandi", response_model=List[BandoResponse])
def get_bandi(
    page: int = Query(1, description="Page number", ge=1),
    size: int = Query(20, description="Items per page", le=100),
    status: Optional[str] = Query(None, description="Filter by status (new, analyzed)"),
    search: Optional[str] = Query(None, description="Search text in Title or Summary"),
    regione: Optional[str] = Query(None, description="Filter by Region (e.g. Lombardia)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of grants with advanced filtering and pagination.
    """

    from sqlalchemy import or_, func, case, literal_column
    
    query = db.query(Bando)
    
    # 1. Status Filter
    if status:
        try:
            # Try to map 'analyzed' -> ProcessingStatus.ANALYZED
            # Assumes the input string matches the Enum value ('new', 'analyzed', etc.)
            status_enum = ProcessingStatus(status.lower()) 
            query = query.filter(Bando.status == status_enum)
        except ValueError:
            # If invalid status passed, ignore or return empty?
            # Let's return empty to indicate no matches for invalid status
            return []
    
    # 2. Text Search (Title OR Summary OR Marketing Text)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Bando.title.ilike(search_term),
                Bando.marketing_text.ilike(search_term),
                func.json_extract(Bando.ai_analysis, '$.titolo_riassuntivo').ilike(search_term),
                func.json_extract(Bando.ai_analysis, '$.sintesi').ilike(search_term),
                # New V2 search tags
                 func.json_extract(Bando.ai_analysis, '$.search_tags').ilike(search_term)
            )
        )

    # 3. Region Filter (New V2 Array Check)
    if regione:
        # SQLite: Check if regione is overlapping with the valid regions
        # Simple string-in-string check works because JSON array is stored as string '["Lombardia"]'
        # For more robustness we useLIKE %"Regione"%
        
        # Normalize: search "Lombardia"
        target_region = regione.strip()
        
        # Check standard regions array OR legacy string field
        query = query.filter(
            or_(
                # New V2: "regions": ["Lombardia", "Nazionale"] -> matches %"Lombardia"%
                func.json_extract(Bando.ai_analysis, '$.regions').ilike(f'%"{target_region}"%'),
                # Legacy fallback
                func.lower(func.json_extract(Bando.ai_analysis, '$.regione')) == target_region.lower()
            )
        )
        
    # 4. Sorting Logic
    # Priority: Active > Expired. Then by Date.
    
    from datetime import date
    today = date.today().isoformat()
    
    # Extract deadline
    deadline_expr = func.coalesce(
        func.json_extract(Bando.ai_analysis, '$.scadenza'), 
        func.json_extract(Bando.ai_analysis, '$.close_date'),
        func.json_extract(Bando.ai_analysis, '$.data_chiusura')
    )
    
    # Expired Flag: stored in JSON (V2) or calculated (Legacy)
    # Check V2 first: $.is_expired == true
    is_expired_v2 = func.json_extract(Bando.ai_analysis, '$.is_expired')
    
    # Calculation for Legacy
    is_expired_calc = case(
        (deadline_expr < today, 1),
        else_=0
    )
    
    # Combined Expired Logic (1 = Expired, 0 = Active)
    # If is_expired_v2 is not null, use it (cast to int), else use calc
    final_is_expired = func.coalesce(
        case((is_expired_v2 == 'true', 1), (is_expired_v2 == True, 1), else_=None),
        is_expired_calc
    )

    # Secondary Sort: Open Date (descending)
    open_date_expr = func.coalesce(
        func.json_extract(Bando.ai_analysis, '$.open_date'),
        func.json_extract(Bando.ai_analysis, '$.data_apertura'),
        Bando.ingested_at
    )

    try:
        skip = (page - 1) * size
        bandi = query.order_by(
            final_is_expired.asc(), # 0 (Active) before 1 (Expired)
            open_date_expr.desc(),  # Newest first
            Bando.id.desc()
        ).offset(skip).limit(size).all()
        return bandi
    except Exception as e:
        import traceback
        with open("error_log.txt", "w") as f:
            f.write(str(e) + "\n")
            traceback.print_exc(file=f)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bandi/{bando_id}", response_model=BandoResponse)
def get_bando(bando_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific grant.
    """
    bando = db.query(Bando).filter(Bando.id == bando_id).first()
    if not bando:
        raise HTTPException(status_code=404, detail="Bando not found")
    return bando


@app.get("/regioni", response_model=List[str])
def get_regioni(db: Session = Depends(get_db)):
    """
    Get list of unique regions from all bandi.
    Maps Solr IDs to human-readable region names.
    """
    import json
    
    # Mapping Solr IDs to Italian region names (from incentivi.gov.it)
    SOLR_ID_TO_REGION = {
        "218": "Abruzzo",
        "219": "Basilicata",
        "220": "Calabria",
        "221": "Campania",
        "222": "Emilia-Romagna",
        "223": "Friuli-Venezia Giulia",
        "224": "Lazio",
        "225": "Liguria",
        "226": "Lombardia",
        "227": "Marche",
        "228": "Molise",
        "229": "Piemonte",
        "230": "Puglia",
        "231": "Sardegna",
        "232": "Sicilia",
        "233": "Toscana",
        "234": "Trentino-Alto Adige",
        "235": "Umbria",
        "236": "Valle d'Aosta",
        "237": "Veneto",
        "587": "Estero",
    }
    
    # Standard Italian regions fallback
    REGIONI_ITALIANE = [
        "Nazionale", "Lombardia", "Lazio", "Campania", "Veneto", 
        "Piemonte", "Emilia-Romagna", "Sicilia", "Toscana", "Puglia"
    ]
    
    # Query all bandi with ai_analysis
    bandi = db.query(Bando).filter(Bando.ai_analysis.isnot(None)).all()
    
    regions_set = set()
    
    for bando in bandi:
        try:
            analysis = bando.ai_analysis
            if isinstance(analysis, str):
                analysis = json.loads(analysis)
            
            # Try different field names for regions
            regions = analysis.get('regions') or analysis.get('regione') or []
            
            if isinstance(regions, list):
                for r in regions:
                    if r:
                        r_str = str(r).strip()
                        # Map ID to name if it's a numeric ID
                        if r_str in SOLR_ID_TO_REGION:
                            regions_set.add(SOLR_ID_TO_REGION[r_str])
                        elif not r_str.isdigit():
                            # It's already a name
                            regions_set.add(r_str)
            elif isinstance(regions, str) and regions:
                r_str = regions.strip()
                if r_str in SOLR_ID_TO_REGION:
                    regions_set.add(SOLR_ID_TO_REGION[r_str])
                elif not r_str.isdigit():
                    regions_set.add(r_str)
                
        except (json.JSONDecodeError, AttributeError, TypeError):
            continue
    
    # Sort alphabetically
    # Remove "Nazionale" if present to avoid duplication when we add it at the start
    if "Nazionale" in regions_set:
        regions_set.remove("Nazionale")
        
    sorted_regions = sorted(regions_set)
    
    # Add "Nazionale" at the beginning if we have results
    if sorted_regions:
        sorted_regions.insert(0, "Nazionale")
    else:
        return REGIONI_ITALIANE
    
    return sorted_regions

