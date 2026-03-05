"""
Upload API routes - handle protocol file uploads.
"""
import json
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

import config
from db import SessionLocal, Protocol, compute_file_hash
from backend.services.file_parser import get_parser


router = APIRouter()


class UploadResponse(BaseModel):
    protocol_id: int
    filename: str
    section_3_extracted: bool
    section_3_length: int


@router.post("/upload", response_model=UploadResponse)
async def upload_protocol(file: UploadFile = File(...)):
    """Upload a protocol document for review."""
    # Validate file type
    allowed_extensions = {".pdf", ".docx", ".doc"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {allowed_extensions}"
        )
    
    # Create upload directory if needed
    upload_dir = Path(config.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded file
    file_path = upload_dir / file.filename
    
    # Handle duplicate filename
    counter = 1
    stem = file_path.stem
    suffix = file_path.suffix
    while file_path.exists():
        file_path = upload_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Compute hash for deduplication
    file_hash = compute_file_hash(file_path)
    
    # Extract Section 3
    parser = get_parser()
    try:
        section_3_text, was_found = parser.parse_and_extract(file_path)
    except Exception as e:
        # If parsing fails, still save the file but mark section as not found
        section_3_text = ""
        was_found = False
    
    # Save to database
    db = SessionLocal()
    try:
        protocol = Protocol(
            filename=file_path.name,
            file_path=str(file_path),
            file_hash=file_hash,
            section_3_text=section_3_text
        )
        db.add(protocol)
        db.commit()
        db.refresh(protocol)
        
        return UploadResponse(
            protocol_id=protocol.id,
            filename=protocol.filename,
            section_3_extracted=was_found,
            section_3_length=len(section_3_text) if section_3_text else 0
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
