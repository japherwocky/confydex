#!/usr/bin/env python
"""
Confydex - Clinical Trial Document Search

Usage:
    python confydex.py init                         # Initialize database
    python confydex.py crawl --limit 10             # Crawl clinicaltrials.gov
    python confydex.py ingest                       # Process PDFs with docling
    python confydex.py embed                        # Generate vector embeddings
    python confydex.py serve-api                    # Run FastAPI backend
    python confydex.py serve                        # Full stack (frontend + API)
    python confydex.py status                       # Show index statistics
"""
import argparse
import sys
import subprocess
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config


def cmd_init(args=None):
    """Initialize database tables."""
    from db import init_db, Base, engine
    
    init_db()
    print("Database initialized.")
    
    # List tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables created:")
    for table in tables:
        print(f"  - {table}")


def cmd_crawl(args):
    """Crawl clinicaltrials.gov for PDFs."""
    from backend.services.crawler import crawl_trials
    
    print(f"Crawling clinicaltrials.gov (limit: {args.limit})...")
    try:
        results = crawl_trials(limit=args.limit, conditions=args.conditions)
        print(f"Crawl complete!")
        print(f"  Trials found: {results.get('trials_found', 0)}")
        print(f"  New PDFs: {results.get('new_pdfs', 0)}")
        print(f"  Updated: {results.get('updated', 0)}")
    except Exception as e:
        print(f"Crawl failed: {e}")
        sys.exit(1)


def cmd_ingest(args):
    """Ingest PDFs: extract text with docling."""
    from backend.services.docling_ingest import ingest_documents
    
    print("Ingesting documents with docling...")
    try:
        if args.nct_id:
            results = ingest_documents(nct_id=args.nct_id)
        else:
            results = ingest_documents()
        print(f"Ingestion complete!")
        print(f"  Documents processed: {results.get('processed', 0)}")
        print(f"  Errors: {results.get('errors', 0)}")
    except Exception as e:
        print(f"Ingestion failed: {e}")
        sys.exit(1)


def cmd_embed(args):
    """Generate vector embeddings."""
    from backend.services.embed import generate_embeddings
    
    print("Generating embeddings...")
    try:
        results = generate_embeddings(force=args.force)
        print(f"Embedding complete!")
        print(f"  Documents embedded: {results.get('embedded', 0)}")
        print(f"  Skipped (already exists): {results.get('skipped', 0)}")
        print(f"  Errors: {results.get('errors', 0)}")
    except Exception as e:
        print(f"Embedding failed: {e}")
        sys.exit(1)


def cmd_serve_api(args):
    """Run FastAPI backend only."""
    cmd = [sys.executable, "-m", "uvicorn", "backend.main:app"]
    
    cmd.extend(["--host", args.host])
    cmd.extend(["--port", str(args.port)])
    
    if args.reload:
        cmd.append("--reload")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Starting API server at http://{args.host}:{args.port}")
    if args.reload:
        print("Reload enabled.")
    
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nServer stopped.")


def cmd_serve(args):
    """Serve full stack (frontend + API)."""
    # For now, just run the API - frontend will be separate
    # In production, would use a proxy or serve static files
    print("Note: Frontend not yet set up. Running API only.")
    cmd_serve_api(args)


def cmd_status(args=None):
    """Show index statistics."""
    from db import SessionLocal, Trial, Document
    from pathlib import Path
    import config
    
    db = SessionLocal()
    try:
        trials_count = db.query(Trial).count()
        docs_count = db.query(Document).count()
        docs_with_embed = db.query(Document).filter(Document.embedding.isnot(None)).count()
        
        # Calculate storage
        data_dir = Path(config.DATA_DIR)
        total_size = 0
        if data_dir.exists():
            for f in data_dir.glob("*.pdf"):
                total_size += f.stat().st_size
        
        mb = total_size / (1024 * 1024)
        
        print("Index Statistics:")
        print(f"  Trials indexed: {trials_count}")
        print(f"  Documents indexed: {docs_count}")
        print(f"  Documents with embeddings: {docs_with_embed}")
        print(f"  Storage used: {mb:.1f} MB")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        prog="python confydex.py",
        description="Confydex - Clinical Trial Document Search"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # init
    sp_init = subparsers.add_parser("init", help="Initialize database")
    sp_init.set_defaults(func=cmd_init)
    
    # crawl
    sp_crawl = subparsers.add_parser("crawl", help="Crawl clinicaltrials.gov for PDFs")
    sp_crawl.add_argument("--limit", type=int, default=10, help="Max trials to fetch")
    sp_crawl.add_argument("--conditions", nargs="*", help="Filter by conditions")
    sp_crawl.set_defaults(func=cmd_crawl)
    
    # ingest
    sp_ingest = subparsers.add_parser("ingest", help="Ingest PDFs with docling")
    sp_ingest.add_argument("--nct-id", type=str, help="Process specific trial only")
    sp_ingest.set_defaults(func=cmd_ingest)
    
    # embed
    sp_embed = subparsers.add_parser("embed", help="Generate vector embeddings")
    sp_embed.add_argument("--force", action="store_true", help="Regenerate even if exists")
    sp_embed.set_defaults(func=cmd_embed)
    
    # serve-api
    sp_api = subparsers.add_parser("serve-api", help="Run FastAPI backend")
    sp_api.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    sp_api.add_argument("--port", type=int, default=8000, help="Port to bind to")
    sp_api.add_argument("--reload", action="store_true", default=True, help="Enable auto-reload")
    sp_api.add_argument("--no-reload", dest="reload", action="store_false", help="Disable auto-reload")
    sp_api.set_defaults(func=cmd_serve_api)
    
    # serve
    sp_serve = subparsers.add_parser("serve", help="Serve full stack")
    sp_serve.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    sp_serve.add_argument("--port", type=int, default=8000, help="Port to bind to")
    sp_serve.add_argument("--reload", action="store_true", default=True, help="Enable auto-reload")
    sp_serve.add_argument("--no-reload", dest="reload", action="store_false", help="Disable auto-reload")
    sp_serve.set_defaults(func=cmd_serve)
    
    # status
    sp_status = subparsers.add_parser("status", help="Show index statistics")
    sp_status.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        print("\nCommands:")
        print("  init          Initialize database")
        print("  crawl         Crawl clinicaltrials.gov")
        print("  ingest        Process PDFs with docling")
        print("  embed         Generate vector embeddings")
        print("  serve-api     Run FastAPI backend")
        print("  serve         Serve full stack")
        print("  status        Show index statistics")
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
