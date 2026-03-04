"""
PDF ingestion using docling.
"""
import logging
from pathlib import Path
from typing import Optional

from docling.document_converter import DocumentConverter

from db import SessionLocal, Document
import config

logger = logging.getLogger(__name__)


def ingest_documents(nct_id: Optional[str] = None) -> dict:
    """
    Process PDFs with docling and extract text.
    
    Args:
        nct_id: If provided, only process documents for this trial
        
    Returns:
        dict with processed, errors counts
    """
    results = {
        "processed": 0,
        "errors": 0,
    }
    
    db = SessionLocal()
    
    try:
        # Get documents to process
        query = db.query(Document).filter(Document.raw_text.is_(None))
        
        if nct_id:
            query = query.filter(Document.nct_id == nct_id)
        
        documents = query.all()
        
        if not documents:
            logger.info("No documents to process.")
            return results
        
        # Initialize docling converter
        logger.info(f"Processing {len(documents)} documents...")
        converter = DocumentConverter()
        
        for doc in documents:
            try:
                filepath = Path(doc.file_path)
                if not filepath.exists():
                    logger.warning(f"File not found: {filepath}")
                    results["errors"] += 1
                    continue
                
                # Convert PDF to text
                result = converter.convert(str(filepath))
                text = result.document.export_to_text()
                
                # Truncate if too long (SQLite has limits, and embeddings have context limits)
                max_chars = 100000  # Keep first 100k chars
                if len(text) > max_chars:
                    text = text[:max_chars]
                
                # Update document
                doc.raw_text = text
                db.commit()
                
                results["processed"] += 1
                logger.debug(f"Processed: {doc.nct_id} ({doc.doc_type})")
                
            except Exception as e:
                logger.error(f"Error processing {doc.nct_id}: {e}")
                results["errors"] += 1
                db.rollback()
        
        logger.info(f"Ingestion complete: {results}")
        
    finally:
        db.close()
    
    return results
