# Confydex - Clinical Trial Document Search

A proof-of-concept web application for searching clinical trial documents from clinicaltrials.gov.

## Features

- Crawl clinicaltrials.gov for trial PDFs
- Extract text using docling
- Generate vector embeddings for semantic search
- Hybrid search (keyword + semantic)
- Simple React frontend

## Quick Start

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 3. Initialize the database

```bash
python confydex.py init
```

### 4. Crawl some trials

```bash
python confydex.py crawl --limit 10
```

### 5. Ingest PDFs (extract text with docling)

```bash
python confydex.py ingest
```

### 6. Generate embeddings

```bash
python confydex.py embed
```

### 7. Run the app

```bash
python confydex.py serve
```

This starts:
- Frontend at http://localhost:5173
- API at http://localhost:8000

## Commands

| Command | Description |
|---------|-------------|
| `python confydex.py init` | Initialize database |
| `python confydex.py crawl --limit N` | Crawl N trials from clinicaltrials.gov |
| `python confydex.py ingest` | Extract text from PDFs |
| `python confydex.py embed` | Generate vector embeddings |
| `python confydex.py serve-api` | Run API only |
| `python confydex.py serve` | Run full stack |
| `python confydex.py status` | Show index statistics |

## Configuration

Edit `.env` to configure:

- `EMBEDDING_MODEL` - Sentence-transformers model (default: all-MiniLM-L6-v2)
- `EMBEDDING_DEVICE` - cpu or cuda
- `KEYWORD_WEIGHT` - Weight for keyword search (0.0-1.0)
- `SEMANTIC_WEIGHT` - Weight for semantic search (0.0-1.0)
- `API_PORT` - API port (default: 8000)
- `FRONTEND_PORT` - Frontend port (default: 5173)

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/stats` - Index statistics
- `GET /api/search?q=query&method=hybrid` - Search documents
- `GET /api/docs/{nct_id}` - Get trial documents
- `GET /api/docs/{nct_id}/text/{doc_id}` - Get document text
