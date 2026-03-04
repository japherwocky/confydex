"""
Embedding generation using sentence-transformers.
"""
import logging
from typing import Optional

from sentence_transformers import SentenceTransformer

import config
from db import SessionLocal, Document, embedding_to_bytes

logger = logging.getLogger(__name__)

# Cache the model
_model = None


def get_model():
    """Get or create the sentence-transformers model."""
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        _model = SentenceTransformer(
            config.EMBEDDING_MODEL,
            device=config.EMBEDDING_DEVICE,
        )
    return _model


def generate_embeddings(force: bool = False) -> dict:
    """
    Generate vector embeddings for documents.
    
    Args:
        force: If True, regenerate embeddings even if they exist
        
    Returns:
        dict with embedded, skipped, errors counts
    """
    results = {
        "embedded": 0,
        "skipped": 0,
        "errors": 0,
    }
    
    db = SessionLocal()
    
    try:
        # Get documents with text but no embedding (or force=True)
        query = db.query(Document).filter(Document.raw_text.isnot(None))
        
        if not force:
            query = query.filter(Document.embedding.is_(None))
        
        documents = query.all()
        
        if not documents:
            logger.info("No documents to embed.")
            return results
        
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        
        model = get_model()
        
        for doc in documents:
            try:
                # Prepare text for embedding
                # Use title + first ~2000 chars of text
                trial = doc.trial
                if trial:
                    text = f"{trial.title}: {doc.raw_text[:2000]}"
                else:
                    text = doc.raw_text[:2000]
                
                # Generate embedding
                embedding = model.encode(text, normalize_embeddings=True)
                
                # Convert to bytes and store
                doc.embedding = embedding_to_bytes(embedding.tolist())
                db.commit()
                
                results["embedded"] += 1
                logger.debug(f"Embedded: {doc.nct_id} ({doc.doc_type})")
                
            except Exception as e:
                logger.error(f"Error embedding {doc.nct_id}: {e}")
                results["errors"] += 1
                db.rollback()
        
        logger.info(f"Embedding complete: {results}")
        
    finally:
        db.close()
    
    return results


def embed_text(text: str) -> list:
    """
    Generate embedding for arbitrary text (e.g., search queries).
    
    Args:
        text: Text to embed
        
    Returns:
        List of floats (embedding vector)
    """
    model = get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()
