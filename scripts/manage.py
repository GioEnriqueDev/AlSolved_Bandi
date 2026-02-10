import sys
import os
from pathlib import Path

# Add root to path so src is accessible
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/manage.py [command]")
        print("Commands: fetch, enrich, analyze, api")
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "fetch":
        from src.scraper.fetcher import run_bulk_import
        # Parse args manually or better yet, just forward them if complex
        limit = None
        dry_run = False
        if "--limit" in args:
            try:
                idx = args.index("--limit")
                limit = int(args[idx+1])
            except: pass
        if "--dry-run" in args:
            dry_run = True
            
        run_bulk_import(dry_run=dry_run, limit=limit)
        
    elif command == "enrich":
        from src.scraper.enricher import run_enrichment
        dry_run = "--dry-run" in args
        run_enrichment(dry_run=dry_run)
        
    elif command == "analyze":
        from src.analysis.analyzer import run_v2_analysis
        limit = 100000
        if "--limit" in args:
            try:
                idx = args.index("--limit")
                limit = int(args[idx+1])
            except: pass
        run_v2_analysis(limit=limit)
        
    elif command == "api":
        import uvicorn
        uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True, app_dir=str(root_path))
        
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
