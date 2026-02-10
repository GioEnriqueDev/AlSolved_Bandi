
import sys
print("Python executable:", sys.executable)
try:
    print("Importing google.generativeai...")
    import google.generativeai as genai
    print("Success.")
    
    print("Importing scraper.models...")
    from scraper.models import init_db
    print("Success.")
    
    print("Importing sqlalchemy...")
    import sqlalchemy
    print("Success.")
    
except Exception as e:
    import traceback
    traceback.print_exc()
