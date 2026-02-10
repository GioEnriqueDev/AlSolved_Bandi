import sys
import os
from sqlalchemy.orm import Session
from fastapi import HTTPException

# Add current dir to path
sys.path.append(os.getcwd())

from scraper.models import get_engine, get_session, Bando
from api.main import get_bandi

# Mock DB session
engine = get_engine()
db = get_session(engine)

try:
    print("Attempting to fetch bandi...")
    # Call the function directly, mocking params
    results = get_bandi(
        skip=0, 
        limit=1, 
        status=None, 
        search=None, 
        regione=None, 
        db=db
    )
    print(f"Success! Retrieved {len(results)} bandi.")
    print(results[0])
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
