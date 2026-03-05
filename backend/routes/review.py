"""
Review API routes - generate regulatory reviews.
"""
import json
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db import SessionLocal, Protocol, Review, review_to_full_dict
from backend.services.llm_analyzer import get_analyzer


router = APIRouter()


class ReviewRequest(BaseModel):
    protocol_id: int
    llm_provider: Optional[str] = None


class ReviewResponse(BaseModel):
    review_id: int
    status: str
    overall_rating: str
    recommendation: str
    estimand_score: str
    report: dict


@router.post("/review", response_model=ReviewResponse)
async def generate_review(request: ReviewRequest):
    """Generate regulatory review for an uploaded protocol."""
    db = SessionLocal()
    
    try:
        # Get protocol
        protocol = db.query(Protocol).filter(
            Protocol.id == request.protocol_id
        ).first()
        
        if not protocol:
            raise HTTPException(status_code=404, detail="Protocol not found")
        
        if not protocol.section_3_text:
            raise HTTPException(
                status_code=400, 
                detail="Section 3 text not found. Please upload a valid protocol."
            )
        
        # Get analyzer
        analyzer = get_analyzer(request.llm_provider)
        
        # Run analysis
        report = analyzer.analyze(protocol.section_3_text)
        
        # Extract fields for review record
        review_fields = analyzer.extract_review_fields(report)
        
        # Create review record
        review = Review(
            protocol_id=protocol.id,
            report_json=json.dumps(report),
            **review_fields
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        
        return ReviewResponse(
            review_id=review.id,
            status="completed",
            overall_rating=review.overall_rating,
            recommendation=review.recommendation,
            estimand_score=f"{review.estimand_score}/4",
            report=report
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
