# Confydex - Clinical Trial Document Search

## Overview

**Confydex** is a proof-of-concept web application that:
1. Crawls clinicaltrials.gov for PDF documents
2. Ingests and extracts text from those PDFs using docling
3. Generates vector embeddings for semantic search
4. Provides a React frontend for searching indexed documents

## Goals

- Demonstrate hybrid search (keyword + semantic/vector-based ranking)
- Evaluate docling for PDF parsing
- Keep architecture simple: SQLite for all storage, local file storage for PDFs
- Support incremental crawling and re-indexing

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                      │
│   Search bar, filters, results list, document preview          │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP
┌─────────────────────────────▼───────────────────────────────────┐
│                      FastAPI Backend                           │
│  /api/search    - Search documents                             │
│  /api/docs/{id} - Get document details / text                 │
│  /api/crawl     - Trigger a new crawl                         │
│  /api/stats     - Index statistics                             │
└─────────────────────────────┬───────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Crawler       │  │  PDF Ingestion │  │  Embeddings    │
│   (httpx +      │  │  (docling)     │  │  (sentence-    │
│    clinical-    │  │  → SQLite      │  │   transformers)│
│    trials.gov)  │  │                │  │  → SQLite      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌───────────────────────────────────────────────────────────────┐
│                    /data/ directory                           │
│    Raw PDFs stored by NCT ID (e.g., NCT00000001.pdf)        │
└───────────────────────────────────────────────────────────────┘
```

## CLI Commands (confydex.py)

```bash
# Initialize database
python confydex.py init

# Crawl clinicaltrials.gov for PDFs
python confydex.py crawl --limit 10        # First 10 trials
python confydex.py crawl                   # All trials (or use --limit)

# Ingest PDFs: extract text with docling, store in SQLite
python confydex.py ingest                  # Process all PDFs in /data/
python confydex.py ingest --nct-id NCT00001 # Process specific trial

# Generate vector embeddings
python confydex.py embed                   # Generate for all documents
python confydex.py embed --force           # Regenerate even if exists

# Serve the application
python confydex.py serve-api                # FastAPI backend only (port 8000)
python confydex.py serve                    # Full stack (frontend + API)

# Development
python confydex.py status                   # Show index stats
```

## Database Schema (SQLite)

### Table: trials
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| nct_id | TEXT | ClinicalTrials.gov ID (e.g., NCT00000001) |
| title | TEXT | Trial title |
| status | TEXT | Trial status (RECRUITING, COMPLETED, etc.) |
| conditions | TEXT | JSON array of conditions |
| interventions | TEXT | JSON array of interventions |
| sponsor | TEXT | Lead sponsor |
| created_at | DATETIME | When first indexed |
| updated_at | DATETIME | Last update |

### Table: documents
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| trial_id | INTEGER | FK to trials |
| nct_id | TEXT | Copy for convenience |
| doc_type | TEXT | "protocol", "results", "protocol_sap", etc. |
| file_path | TEXT | Path to PDF in /data/ |
| file_hash | TEXT | SHA256 of PDF (for deduplication) |
| page_count | INTEGER | Number of pages |
| raw_text | TEXT | Extracted text (may be truncated for very large docs) |
| embedding | BLOB | Vector embedding (JSON serialized, stored as binary) |
| ingested_at | DATETIME | When docling ran |
| updated_at | DATETIME | Last update |

### Indexes
- `trials.nct_id` (UNIQUE)
- `documents.trial_id`
- `documents.nct_id`
- `documents.file_hash` (for deduplication)

## API Endpoints

### GET /api/health
Health check.

**Response:** `{"status": "ok"}`

### GET /api/stats
Return index statistics.

**Response:**
```json
{
  "trials_indexed": 150,
  "documents_indexed": 423,
  "documents_with_embeddings": 400,
  "storage_mb": 125.5
}
```

### GET /api/search
Search documents.

**Query Parameters:**
- `q` (string, required): Search query
- `limit` (int, default 20): Max results
- `offset` (int, default 0): Pagination offset
- `method` (string, default "hybrid"): "keyword", "semantic", or "hybrid"

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "nct_id": "NCT00000001",
      "title": "Trial Title",
      "doc_type": "results",
      "snippet": "...matching text with <mark>highlights</mark>...",
      "score": 0.85,
      "rank": 1
    }
  ],
  "total": 150,
  "query": "diabetes treatment",
  "method": "hybrid"
}
```

### GET /api/docs/{nct_id}
Get document details and full text.

**Response:**
```json
{
  "nct_id": "NCT00000001",
  "title": "Trial Title",
  "status": "COMPLETED",
  "documents": [
    {
      "id": 1,
      "doc_type": "results",
      "file_path": "/data/NCT00000001_results.pdf",
      "page_count": 45,
      "text_length": 12500
    }
  ]
}
```

### GET /api/docs/{nct_id}/text/{doc_id}
Get extracted text for a specific document.

**Response:** Plain text or JSON depending on Accept header.

### POST /api/crawl
Trigger a new crawl (or could be CLI-only for POC).

**Request:**
```json
{
  "limit": 10,
  "conditions": ["Diabetes"]
}
```

**Response:**
```json
{
  "status": "started",
  "trials_found": 10,
  "new_pdfs": 8
}
```

## Search Implementation

### Hybrid Search Ranking

1. **Keyword search**: SQLite FTS5 full-text search on `raw_text`
2. **Semantic search**: Cosine similarity between query embedding and document embedding
3. **Hybrid scoring**:
   - Normalize both scores to 0-1
   - Weight: 50% keyword, 50% semantic (configurable)
   - Combine and rank

### Embedding Generation

- Model: Configurable via `.env` (default: `sentence-transformers/all-MiniLM-L6-v2`)
- Input: Document title + first 2000 chars of extracted text (truncated for performance)
- Storage: JSON array of floats serialized to binary SQLite blob

## File Structure

```
confydex/
├── .env                       # Configuration (API keys, model, paths)
├── .gitignore
├── PLAN.md
├── README.md
├── confydex.py               # Main CLI entry point
├── config.py                 # Load .env and provide config
├── db.py                     # SQLite database + models
├── requirements.txt           # Python dependencies
├── requirements-dev.txt      # Dev dependencies
├── data/                     # Downloaded PDFs
│   └── .gitkeep
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── search.py        # /api/search
│   │   ├── docs.py          # /api/docs
│   │   └── crawl.py         # /api/crawl
│   └── services/
│       ├── __init__.py
│       ├── crawler.py       # clinicaltrials.gov API client
│       ├── docling_ingest.py # PDF parsing
│       └── embed.py         # Embedding generation
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   ├── components/
│   │   │   ├── SearchBar.tsx
│   │   │   ├── ResultsList.tsx
│   │   │   └── DocPreview.tsx
│   │   └── styles/
│   │       └── index.css
│   └── tsconfig.json
└── tests/
    ├── __init__.py
    ├── test_crawler.py
    └── test_search.py
```

## Configuration (.env)

```bash
# Database
DATABASE_URL=confydex.db

# Data storage
DATA_DIR=./data

# Embedding model (sentence-transformers)
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu

# Clinicaltrials.gov API (if needed)
# CLINICALTRIALS_API_KEY=

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000

# Frontend (dev only, served via Vite)
FRONTEND_PORT=5173

# Search weights (0.0 to 1.0)
KEYWORD_WEIGHT=0.5
SEMANTIC_WEIGHT=0.5
```

## Dependencies

### Python (requirements.txt)
```
fastapi
uvicorn
httpx
docling
sqlalchemy
sqlite-vector  # or just store embeddings in blob
sentence-transformers
python-dotenv
tiktoken  # for chunking if needed
```

### Frontend (frontend/package.json)
```
react
react-dom
axios
tailwindcss
@tanstack/react-query  # optional, for data fetching
```

## Development Workflow

1. **Init**: `python confydex.py init` - Create database tables
2. **Crawl**: `python confydex.py crawl --limit 50` - Get first batch of PDFs
3. **Ingest**: `python confydex.py ingest` - Extract text with docling
4. **Embed**: `python confydex.py embed` - Generate vectors
5. **Serve**: `python confydex.py serve` - Full stack dev server

## Future Considerations (Out of Scope for POC)

- Full-text search with Elasticsearch/OpenSearch
- Dedicated vector database (Weaviate, Qdrant)
- Background job queue (Celery) for crawling/ingestion
- User authentication
- Saved searches / bookmarks
- PDF streaming / pagination for large documents
- More sophisticated text chunking for embeddings
- Multiple embedding models for comparison

## Success Criteria

- [ ] Can crawl clinicaltrials.gov and download PDFs
- [ ] Can extract text from PDFs using docling
- [ ] Can generate vector embeddings for documents
- [ ] Can search with keyword matching
- [ ] Can search with semantic/vector similarity
- [ ] Can combine both in hybrid ranking
- [ ] Frontend can display search results
- [ ] Frontend can preview document text

