"""
Search endpoint with hybrid keyword + semantic search.
"""
import math
from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import func

from db import SessionLocal, Document, Trial, embedding_to_list
from backend.services.embed import embed_text
import config

router = APIRouter()


def cosine_similarity(a: list, b: list) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def keyword_search(query: str, limit: int = 20) -> list:
    """
    Simple keyword search using SQL LIKE.
    For production, use SQLite FTS5.
    """
    db = SessionLocal()
    try:
        search_pattern = f"%{query}%"
        
        # Search in trial title and document text
        documents = (
            db.query(Document, Trial)
            .join(Trial, Document.trial_id == Trial.id)
            .filter(
                (Trial.title.like(search_pattern)) |
                (Document.raw_text.like(search_pattern))
            )
            .limit(limit * 2)  # Get more for re-ranking
            .all()
        )
        
        results = []
        for doc, trial in documents:
            # Get snippet
            snippet = get_snippet(doc.raw_text, query) if doc.raw_text else ""
            results.append({
                "id": doc.id,
                "nct_id": doc.nct_id,
                "title": trial.title,
                "doc_type": doc.doc_type,
                "snippet": snippet,
                "score": 1.0,  # Will be normalized later
            })
        
        return results
    finally:
        db.close()


def semantic_search(query: str, limit: int = 20) -> list:
    """
    Semantic search using vector embeddings.
    """
    db = SessionLocal()
    try:
        # Generate query embedding
        query_embedding = embed_text(query)
        
        # Get all documents with embeddings
        documents = (
            db.query(Document, Trial)
            .join(Trial, Document.trial_id == Trial.id)
            .filter(Document.embedding.isnot(None))
            .all()
        )
        
        # Compute similarities
        results = []
        for doc, trial in documents:
            doc_embedding = embedding_to_list(doc.embedding)
            if doc_embedding:
                sim = cosine_similarity(query_embedding, doc_embedding)
                snippet = get_snippet(doc.raw_text, query) if doc.raw_text else ""
                results.append({
                    "id": doc.id,
                    "nct_id": doc.nct_id,
                    "title": trial.title,
                    "doc_type": doc.doc_type,
                    "snippet": snippet,
                    "score": sim,
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    finally:
        db.close()


def get_snippet(text: str, query: str, context_chars: int = 100) -> str:
    """Extract a snippet around the first match."""
    if not text:
        return ""
    
    text_lower = text.lower()
    query_lower = query.lower()
    
    idx = text_lower.find(query_lower)
    if idx == -1:
        # No match, just return beginning
        return text[:200] + "..."
    
    start = max(0, idx - context_chars)
    end = min(len(text), idx + len(query) + context_chars)
    
    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    
    # Highlight matches
    snippet = snippet.replace(query, f"<mark>{query}</mark>")
    
    return snippet


@router.get("/search")
async def search_documents(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Max results"),
    offset: int = Query(0, description="Pagination offset"),
    method: str = Query("hybrid", description="Search method: keyword, semantic, or hybrid"),
):
    """
    Search documents using keyword and/or semantic search.
    """
    results = []
    
    if method == "keyword":
        results = keyword_search(q, limit=limit)
    elif method == "semantic":
        results = semantic_search(q, limit=limit)
    elif method == "hybrid":
        # Get both
        kw_results = keyword_search(q, limit=limit)
        sem_results = semantic_search(q, limit=limit)
        
        # Normalize scores
        if kw_results:
            max_kw = max(r["score"] for r in kw_results)
            for r in kw_results:
                r["score"] = r["score"] / max_kw if max_kw > 0 else 0
        
        if sem_results:
            max_sem = max(r["score"] for r in sem_results)
            for r in sem_results:
                r["score"] = r["score"] / max_sem if max_sem > 0 else 0
        
        # Merge results
        seen = {}
        for r in kw_results:
            seen[r["id"]] = r
        for r in sem_results:
            if r["id"] in seen:
                # Combine scores
                seen[r["id"]]["score"] = (
                    config.KEYWORD_WEIGHT * seen[r["id"]]["score"] +
                    config.SEMANTIC_WEIGHT * r["score"]
                )
            else:
                seen[r["id"]] = r
        
        results = list(seen.values())
        results.sort(key=lambda x: x["score"], reverse=True)
    
    # Apply pagination
    total = len(results)
    results = results[offset:offset + limit]
    
    # Add rank
    for i, r in enumerate(results):
        r["rank"] = i + 1
    
    return {
        "results": results,
        "total": total,
        "query": q,
        "method": method,
    }


@router.get("/stats")
async def get_stats():
    """Get index statistics."""
    db = SessionLocal()
    try:
        from pathlib import Path
        
        trials_count = db.query(func.count(Document.trial_id.distinct())).scalar() or 0
        docs_count = db.query(func.count(Document.id)).scalar() or 0
        docs_with_embed = db.query(func.count(Document.id)).filter(
            Document.embedding.isnot(None)
        ).scalar() or 0
        
        # Calculate storage
        data_dir = Path(config.DATA_DIR)
        total_size = 0
        if data_dir.exists():
            for f in data_dir.glob("*.pdf"):
                total_size += f.stat().st_size
        
        mb = total_size / (1024 * 1024)
        
        return {
            "trials_indexed": trials_count,
            "documents_indexed": docs_count,
            "documents_with_embeddings": docs_with_embed,
            "storage_mb": round(mb, 1),
        }
    finally:
        db.close()
