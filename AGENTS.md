
# Confydex - Agent Guide

## Project Overview

Confydex is a proof-of-concept web application for searching clinical trial documents. Currently focused on the **API/backend only** - the frontend and PDF crawling are placeholders.

**Current Priority**: Get a working search API with mock/synthetic data.

## Architecture

- **Backend**: FastAPI (Python) with SQLAlchemy ORM and SQLite
- **CLI**: Python CLI using argparse (confydex.py)
- **Frontend**: React + Vite + Tailwind (NOT currently working, skip for now)

## Database

- **Location**: `confydex.db` (SQLite)
- **Tables**: `trials`, `documents`
- **Initialize**: `python confydex.py init`

## Virtualenv

The virtualenv should exist at `./venv`. Use it for all Python commands:

```bash
./venv/Scripts/python.exe confydex.py <command>
./venv/Scripts/pip.exe install <package>
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `python confydex.py init` | Initialize database |
| `python confydex.py crawl --limit N` | Crawl clinicaltrials.gov (WIP - API issues) |
| `python confydex.py ingest` | Process PDFs with docling (needs PDFs first) |
| `python confydex.py embed` | Generate vector embeddings |
| `python confydex.py serve-api` | Run FastAPI backend (port 8000) |
| `python confydex.py status` | Show index statistics |

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/stats` - Index statistics  
- `GET /api/search?q=query&method=hybrid` - Search (keyword/semantic/hybrid)
- `GET /api/docs/{nct_id}` - Get trial documents
- `GET /api/docs/{nct_id}/text/{doc_id}` - Get document text

## Current Focus

**Reset**: Skip PDF crawling for now. Focus on getting the search API working.

### Immediate Goals

1. **Seed mock data** - Add some synthetic trial/document data to SQLite directly
2. **Test search API** - Verify keyword and semantic search work
3. **Test embedding** - Verify vector similarity works

### How to Seed Mock Data

Run a quick script to insert test data:

```python
./venv/Scripts/python.exe -c "
import json
from db import SessionLocal, Trial, Document

db = SessionLocal()

# Add a test trial
trial = Trial(
    nct_id='NCT00000001',
    title='Test Trial for Diabetes Treatment',
    status='COMPLETED',
    conditions='[\"Diabetes Type 2\"]',
    interventions='[\"Metformin\", \"Placebo\"]',
    sponsor='Test University'
)
db.add(trial)
db.commit()

# Add a test document with text
doc = Document(
    trial_id=trial.id,
    nct_id='NCT00000001',
    doc_type='protocol',
    file_path='/data/test.pdf',
    file_hash='abc123',
    raw_text='This is a clinical trial protocol for testing diabetes treatment. The study enrolled 100 patients with Type 2 diabetes. Results showed significant improvement in HbA1c levels.'
)
db.add(doc)
db.commit()
print('Added test data')
db.close()
"
```

### Testing the API

1. Start the server:
```bash
./venv/Scripts/python.exe confydex.py serve-api
```

2. Test search:
```bash
curl "http://localhost:8000/api/search?q=diabetes&method=keyword"
curl "http://localhost:8000/api/search?q=diabetes&method=semantic"
curl "http://localhost:8000/api/search?q=diabetes&method=hybrid"
```

## Known Issues

- **PDF Crawling**: clinicaltrials.gov v2 API doesn't return document URLs. Skip for now.
- **Frontend**: Not connected/tested. Focus on API first.

## File Locations

```
confydex/
├── confydex.py          # CLI entry
├── config.py             # Settings
├── db.py                 # Database models
├── backend/
│   ├── main.py          # FastAPI app
│   ├── routes/
│   │   ├── search.py    # Search endpoint
│   │   └── docs.py      # Documents endpoint
│   └── services/
│       ├── embed.py     # Vector embeddings
│       └── crawler.py   # (WIP) Crawler
└── confydex.db          # SQLite database
```
