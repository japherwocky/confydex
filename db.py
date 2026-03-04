"""
Database module - SQLite with SQLAlchemy.
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    LargeBinary,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

import config

# Create engine
engine = create_engine(f"sqlite:///{config.DATABASE_URL}", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Trial(Base):
    """Clinical trial metadata."""
    __tablename__ = "trials"

    id = Column(Integer, primary_key=True)
    nct_id = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    status = Column(String(50))
    conditions = Column(Text)  # JSON array
    interventions = Column(Text)  # JSON array
    sponsor = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents = relationship("Document", back_populates="trial")


class Document(Base):
    """PDF document linked to a trial."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    trial_id = Column(Integer, ForeignKey("trials.id"), nullable=False)
    nct_id = Column(String(20), nullable=False, index=True)
    doc_type = Column(String(50))  # protocol, results, protocol_sap, etc.
    file_path = Column(Text, nullable=False)
    file_hash = Column(String(64), unique=True)  # SHA256
    page_count = Column(Integer)
    raw_text = Column(Text)  # Extracted text (may be truncated)
    embedding = Column(LargeBinary)  # JSON serialized vector, stored as binary
    ingested_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trial = relationship("Trial", back_populates="documents")

    __table_args__ = (
        Index("ix_documents_trial_id", "trial_id"),
        Index("ix_documents_nct_id", "nct_id"),
    )


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create_trial(db, nct_id: str, title: str, **kwargs) -> Trial:
    """Get existing trial or create new one."""
    trial = db.query(Trial).filter(Trial.nct_id == nct_id).first()
    if not trial:
        trial = Trial(nct_id=nct_id, title=title, **kwargs)
        db.add(trial)
        db.commit()
        db.refresh(trial)
    return trial


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def trial_to_dict(trial: Trial) -> dict:
    """Convert trial to dictionary."""
    return {
        "id": trial.id,
        "nct_id": trial.nct_id,
        "title": trial.title,
        "status": trial.status,
        "conditions": json.loads(trial.conditions) if trial.conditions else [],
        "interventions": json.loads(trial.interventions) if trial.interventions else [],
        "sponsor": trial.sponsor,
        "created_at": trial.created_at.isoformat() if trial.created_at else None,
    }


def document_to_dict(doc: Document) -> dict:
    """Convert document to dictionary."""
    return {
        "id": doc.id,
        "trial_id": doc.trial_id,
        "nct_id": doc.nct_id,
        "doc_type": doc.doc_type,
        "file_path": doc.file_path,
        "page_count": doc.page_count,
        "text_length": len(doc.raw_text) if doc.raw_text else 0,
        "has_embedding": doc.embedding is not None,
        "ingested_at": doc.ingested_at.isoformat() if doc.ingested_at else None,
    }


def embedding_to_list(embedding: bytes) -> list:
    """Convert stored binary embedding to list of floats."""
    if embedding is None:
        return []
    return json.loads(embedding.decode("utf-8"))


def embedding_to_bytes(embedding: list) -> bytes:
    """Convert list of floats to binary for storage."""
    return json.dumps(embedding).encode("utf-8")
