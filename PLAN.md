# Confydex - AI-Powered Regulatory Review of Protocol Section 3

## Overview

**Confydex** is a proof-of-concept web application that:
1. Accepts uploaded clinical trial protocols (PDF/DOCX)
2. Extracts Section 3 (Trial Objectives and Estimands)
3. Analyzes against ICH E9(R1) framework using LLM
4. Generates structured regulatory review report with risk ratings
5. Compares against competitor programs (KRAS G12C/G12D landscape)

## Goals

- Evaluate whether primary estimand is properly defined per ICH E9(R1)
- Assess endpoint regulatory precedent for oncology indications
- Compare design to competitor KRAS programs (sotorasib, adagrasib, etc.)
- Produce structured output recognizable by regulatory professionals
- End-to-end demo in under 60 seconds

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                        │
│   File upload, review report display, competitive analysis       │
└─────────────────────────────┬───────────────────────────────────┘
                               │ HTTP
┌─────────────────────────────▼───────────────────────────────────┐
│                      FastAPI Backend                             │
│  /api/upload   - Upload protocol                                │
│  /api/review   - Generate regulatory review                     │
│  /api/reports  - List historical reviews                        │
│  /api/health   - Health check                                    │
└─────────────────────────────┬───────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  File Handler   │  │  LLM Analyzer   │  │  Reference      │
│  (PDF/DOCX)     │  │  (OpenAI/       │  │  Documents      │
│  → Section 3    │  │   Anthropic)    │  │  (Regulatory    │
│    extraction   │  │  → ICH E9(R1)   │  │    precedents)  │
│                 │  │    analysis     │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌───────────────────────────────────────────────────────────────┐
│                    SQLite Database                             │
│    protocols | reviews | reference_docs                       │
└───────────────────────────────────────────────────────────────┘
```

## CLI Commands (confydex.py)

```bash
# Initialize database
python confydex.py init

# Upload and analyze a protocol
python confydex.py review --file protocol.pdf
python confydex.py review --file protocol.docx

# List stored reviews
python confydex.py reports

# View specific review
python confydex.py report --id <review_id>

# Serve the application
python confydex.py serve-api              # FastAPI backend only (port 8000)
python confydex.py serve                  # Full stack (frontend + API)
```

## Database Schema (SQLite)

### Table: protocols
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| filename | TEXT | Original uploaded filename |
| file_path | TEXT | Path to stored file |
| file_hash | TEXT | SHA256 for deduplication |
| uploaded_at | DATETIME | Upload timestamp |
| section_3_text | TEXT | Extracted Section 3 content |

### Table: reviews
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| protocol_id | INTEGER | FK to protocols |
| overall_rating | TEXT | High / Medium / Low |
| recommendation | TEXT | Approvable / Revisions needed / Major concerns |
| estimand_score | INTEGER | X/4 ICH E9(R1) attributes |
| endpoint | TEXT | ORR / PFS / OS / Other |
| report_json | TEXT | Full structured report (JSON) |
| created_at | DATETIME | Analysis timestamp |

### Table: reference_docs
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Document title |
| doc_type | TEXT | guidance / approval_package / competitor |
| url | TEXT | Source URL |
| content_text | TEXT | Extracted text for RAG |
| added_at | DATETIME | When indexed |

## API Endpoints

### GET /api/health
Health check.

**Response:** `{"status": "ok"}`

### POST /api/upload
Upload a protocol document for review.

**Request:** multipart/form-data
- `file`: PDF or DOCX file

**Response:**
```json
{
  "protocol_id": 1,
  "filename": "protocol.pdf",
  "section_3_extracted": true,
  "section_3_length": 2500
}
```

### POST /api/review
Generate regulatory review for uploaded protocol.

**Request:**
```json
{
  "protocol_id": 1,
  "llm_provider": "openai"  // or "anthropic"
}
```

**Response:**
```json
{
  "review_id": 1,
  "status": "completed",
  "overall_rating": "Medium",
  "recommendation": "Revisions needed",
  "estimand_score": "3/4",
  "report": {
    "executive_summary": { ... },
    "estimand_assessment": { ... },
    "endpoint_assessment": { ... },
    "competitive_comparison": { ... },
    "consistency_flags": { ... },
    "detailed_findings": [ ... ],
    "recommended_actions": [ ... }
  }
}
```

### GET /api/reports
List all reviews.

**Response:**
```json
{
  "reviews": [
    {
      "id": 1,
      "protocol_id": 1,
      "filename": "protocol.pdf",
      "overall_rating": "Medium",
      "recommendation": "Revisions needed",
      "created_at": "2026-03-05T10:30:00"
    }
  ]
}
```

### GET /api/reports/{review_id}
Get full review report.

## Output Format (Per SPEC.md)

The system generates structured reports matching this format:

```
SECTION 3 REGULATORY REVIEW REPORT
====================================

1. EXECUTIVE SUMMARY
   - Overall risk rating (High / Medium / Low)
   - Top 3 findings
   - Recommendation: Approvable as-is / Revisions needed / Major concerns

2. ESTIMAND COMPLETENESS ASSESSMENT
   - Population: [Defined / Partially Defined / Missing] — Detail
   - Variable: [Defined / Partially Defined / Missing] — Detail
   - Intercurrent Events: [Defined / Partially Defined / Missing] — Detail
   - Population-Level Summary: [Defined / Partially Defined / Missing] — Detail
   - ICH E9(R1) Compliance Score: [X/4 attributes fully defined]

3. ENDPOINT APPROVABILITY ASSESSMENT
   - Primary endpoint identified: [ORR / PFS / OS / Other]
   - Approval pathway implied: [Accelerated / Traditional / Unclear]
   - Regulatory precedent: [Strong / Moderate / Weak / None]
   - Key risk: [Description of primary concern]

4. COMPETITIVE BENCHMARK COMPARISON
   Table comparing this protocol's endpoint choice, assessment method,
   and estimand structure vs. 2-3 closest competitor programs

5. INTERNAL CONSISTENCY FLAGS
   - Section 3 vs. Section 10 (Statistical Plan) alignment
   - Section 3 vs. Section 4 (Trial Design) alignment
   - Section 3 vs. Section 5 (Population) alignment

6. DETAILED FINDINGS
   - Finding 1: [Description] | Risk: [H/M/L] | Recommendation
   - Finding 2: [Description] | Risk: [H/M/L] | Recommendation

7. RECOMMENDED ACTIONS
   - Prioritized list of revisions before agency submission
```

## LLM Integration

### Prompt Architecture

**SYSTEM PROMPT:**
```
You are a VP of Regulatory Affairs reviewing a clinical trial protocol.
Your task is to evaluate Section 3 (Trial Objectives and Estimands)
against the ICH E9(R1) estimand framework and FDA/EMA regulatory
precedent for oncology programs.

Reference Documents:
- ICH E9(R1) framework (4 attributes: Population, Variable, Intercurrent Events, Summary)
- FDA guidance on clinical trial endpoints for cancer
- Sotorasib (CodeBreaK 100/200) approval package
- Adagrasib (KRYSTAL-1) approval package
- KRAS G12C/G12D competitive landscape data
```

**USER PROMPT:**
```
Review the following Section 3 protocol text and generate a structured
regulatory review report.

[SECTION_3_TEXT]

Provide your analysis in the following JSON format:
{
  "executive_summary": { ... },
  "estimand_assessment": { ... },
  "endpoint_assessment": { ... },
  "competitive_comparison": [ ... ],
  "consistency_flags": { ... },
  "detailed_findings": [ ... ],
  "recommended_actions": [ ... ]
}
```

### LLM Providers
- **OpenAI** (GPT-4o): Default provider
- **Anthropic** (Claude 3.5 Sonnet): Alternative
- Configurable via `.env`

## Reference Documents (RAG Sources)

### Tier 1: Core Regulatory Guidance
- ICH E9(R1) — Estimands and Sensitivity Analysis
- FDA Adoption of ICH E9(R1) (May 2021)
- EMA Adoption of ICH E9(R1)
- FDA Guidance: Clinical Trial Endpoints for Cancer Drugs (Dec 2018)
- FDA Draft Guidance: Accelerated Approval Considerations (March 2023)
- FDA Project Endpoint

### Tier 2: Competitor Approval Packages
- Sotorasib (Lumakras) Multi-Discipline Review (NDA 214665)
- Sotorasib Accelerated Approval (May 2021)
- Adagrasib (Krazati) Multi-Discipline Review (NDA 216340)
- Adagrasib Accelerated Approval (Dec 2022)
- Sotorasib CRL context (Dec 2025)

### Tier 3: KRAS Competitor Landscape
- Zoldonrasib (RMC-9805) — NCT06040541, 61% ORR
- VS-7375 (GFH375) — NCT06500676, 52% ORR in PDAC
- INCB161734 — Phase 1/2, 34% ORR in PDAC

## File Structure

```
confydex/
├── .env                       # Configuration
├── .gitignore
├── PLAN.md
├── SPEC.md                    # Stakeholder requirements
├── README.md
├── confydex.py               # Main CLI entry point
├── config.py                 # Load .env and provide config
├── db.py                     # SQLite database + models
├── requirements.txt           # Python dependencies
├── requirements-dev.txt      # Dev dependencies
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── upload.py       # /api/upload
│   │   ├── review.py       # /api/review
│   │   └── reports.py      # /api/reports
│   └── services/
│       ├── __init__.py
│       ├── file_parser.py  # PDF/DOCX extraction
│       ├── section_extractor.py # Isolate Section 3
│       ├── llm_analyzer.py # LLM prompt + response parsing
│       └── reference_docs.py # RAG document management
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   ├── components/
│   │   │   ├── FileUpload.tsx
│   │   │   ├── ReviewReport.tsx
│   │   │   ├── EstimandScorecard.tsx
│   │   │   └── CompetitiveTable.tsx
│   │   └── styles/
│   │       └── index.css
│   └── tsconfig.json
└── tests/
    ├── __init__.py
    ├── test_parser.py
    └── test_analyzer.py
```

## Configuration (.env)

```bash
# LLM Provider
LLM_PROVIDER=openai  # or "anthropic"
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Model selection
OPENAI_MODEL=gpt-4o
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# File storage
UPLOAD_DIR=./uploads

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000

# Frontend (dev only)
FRONTEND_PORT=5173
```

## Dependencies

### Python (requirements.txt)
```
fastapi
uvicorn
httpx
python-docx        # DOCX parsing
pypdf              # PDF parsing
pydantic
sqlalchemy
python-dotenv
openai             # LLM client
anthropic          # LLM client
tiktoken           # for chunking if needed
```

### Frontend (frontend/package.json)
```
react
react-dom
axios
tailwindcss
@tanstack/react-query
```

## Development Workflow

1. **Init**: `python confydex.py init` - Create database tables
2. **Load references**: `python confydex.py load-refs` - Index regulatory documents
3. **Upload protocol**: `python confydex.py review --file protocol.pdf` - Test analysis
4. **Serve**: `python confydex.py serve` - Full stack dev server

## Success Criteria

- [ ] Can upload PDF and DOCX protocol files
- [ ] Correctly extracts Section 3 content
- [ ] LLM identifies 4 estimand attributes (present/missing)
- [ ] Flags endpoint regulatory precedent with specific references
- [ ] Generates structured report matching SPEC.md format
- [ ] End-to-end demo runs in under 60 seconds

## Future Considerations (Out of Scope for POC)

- Support for full protocol analysis (Sections 4, 5, 10)
- Multiple LLM provider comparison
- Reference document vector store for RAG
- Batch review capabilities
- Export to PDF/Word
- Collaboration features (comments, revisions)
- Integration with regulatory submission systems

---

*Last Updated: March 2026*
