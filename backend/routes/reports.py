"""
Reports API routes - list and retrieve reviews.
"""
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db import SessionLocal, Review, Protocol, review_to_dict, review_to_full_dict


router = APIRouter()


class ReviewListItem(BaseModel):
    id: int
    protocol_id: int
    filename: str
    overall_rating: str
    recommendation: str
    created_at: str


class ReportsResponse(BaseModel):
    reviews: List[ReviewListItem]


@router.get("/reports", response_model=ReportsResponse)
async def list_reports():
    """List all reviews."""
    db = SessionLocal()
    
    try:
        reviews = db.query(Review).order_by(Review.created_at.desc()).all()
        
        result = []
        for review in reviews:
            protocol = db.query(Protocol).filter(
                Protocol.id == review.protocol_id
            ).first()
            
            result.append(ReviewListItem(
                id=review.id,
                protocol_id=review.protocol_id,
                filename=protocol.filename if protocol else "Unknown",
                overall_rating=review.overall_rating,
                recommendation=review.recommendation,
                created_at=review.created_at.isoformat() if review.created_at else ""
            ))
        
        return ReviewsResponse(reviews=result)
    finally:
        db.close()


@router.get("/reports/{review_id}")
async def get_report(review_id: int):
    """Get full review report."""
    db = SessionLocal()
    
    try:
        review = db.query(Review).filter(Review.id == review_id).first()
        
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        protocol = db.query(Protocol).filter(
            Protocol.id == review.protocol_id
        ).first()
        
        result = review_to_full_dict(review)
        result["filename"] = protocol.filename if protocol else "Unknown"
        
        return result
    finally:
        db.close()
