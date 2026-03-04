"""
Document endpoints - get trial details and document text.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from db import SessionLocal, Document, Trial, document_to_dict, trial_to_dict

router = APIRouter()


@router.get("/docs/{nct_id}")
async def get_trial_documents(nct_id: str):
    """Get all documents for a trial."""
    db = SessionLocal()
    try:
        trial = db.query(Trial).filter(Trial.nct_id == nct_id).first()
        if not trial:
            raise HTTPException(status_code=404, detail="Trial not found")
        
        documents = db.query(Document).filter(Document.trial_id == trial.id).all()
        
        return {
            "nct_id": trial.nct_id,
            "title": trial.title,
            "status": trial.status,
            "sponsor": trial.sponsor,
            "conditions": trial.conditions,
            "documents": [document_to_dict(d) for d in documents],
        }
    finally:
        db.close()


@router.get("/docs/{nct_id}/text/{doc_id}", response_class=PlainTextResponse)
async def get_document_text(nct_id: str, doc_id: int):
    """Get extracted text for a document."""
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(
            Document.id == doc_id,
            Document.nct_id == nct_id
        ).first()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not doc.raw_text:
            raise HTTPException(status_code=404, detail="No text extracted for this document")
        
        return doc.raw_text
    finally:
        db.close()
