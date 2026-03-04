"""
Clinicaltrials.gov API crawler.
"""
import json
import logging
from pathlib import Path
from typing import Optional

import httpx

import config
from db import SessionLocal, Trial, Document, get_or_create_trial, compute_file_hash

logger = logging.getLogger(__name__)

BASE_URL = "https://clinicaltrials.gov/api/v2"


def search_trials(
    limit: int = 10,
    conditions: Optional[list] = None,
    query: str = "",
    format: str = "json",
) -> dict:
    """
    Search clinicaltrials.gov for trials.
    
    Returns dict with trials_found, next_page_token, etc.
    """
    params = {
        "pageSize": min(limit, 100),  # API max is 100
        "format": format,
    }
    
    if conditions:
        # Build condition filter
        cond_query = " ".join(conditions)
        params["query.cond"] = cond_query
    elif query:
        params["query.term"] = query
    
    # Get study fields we need
    params["fields"] = "NCTId,BriefTitle,OverallStatus,Condition,InterventionName,LeadSponsorName"
    
    url = f"{BASE_URL}/studies"
    
    results = {
        "trials_found": 0,
        "new_pdfs": 0,
        "updated": 0,
        "trials": [],
    }
    
    with httpx.Client(timeout=60.0) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        studies = data.get("studies", [])
        
        for study in studies:
            protocol = study.get("protocolSection", {})
            
            # Extract fields
            identification = protocol.get("identificationModule", {})
            nct_id = identification.get("nctId")
            title = identification.get("briefTitle", "Untitled")
            sponsor = identification.get("leadSponsor", {}).get("name")
            
            status_module = protocol.get("statusModule", {})
            status = status_module.get("overallStatus", "UNKNOWN")
            
            conditions_list = protocol.get("conditionsModule", {}).get("conditions", [])
            interventions = protocol.get("armsInterventionsModule", {}).get("interventions", [])
            
            if not nct_id:
                continue
            
            results["trials_found"] += 1
            
            # Save trial to DB
            db = SessionLocal()
            try:
                trial = get_or_create_trial(
                    db,
                    nct_id=nct_id,
                    title=title,
                    status=status,
                    conditions=json.dumps(conditions_list),
                    interventions=json.dumps([i.get("name") for i in interventions]),
                    sponsor=sponsor,
                )
                results["updated"] += 1
                
                # Now try to find PDFs for this trial
                pdf_count = download_pdfs_for_trial(client, db, nct_id)
                results["new_pdfs"] += pdf_count
                
            except Exception as e:
                logger.error(f"Error processing {nct_id}: {e}")
            finally:
                db.close()
    
    return results


def download_pdfs_for_trial(client: httpx.Client, db, nct_id: str) -> int:
    """
    Try to download PDF(s) for a given trial.
    Clinicaltrials.gov has PDFs in the results or documents sections.
    """
    # Try to get document info from the API
    url = f"{BASE_URL}/studies/{nct_id}"
    params = {
        "format": "json",
        "fields": "DocumentSection",
    }
    
    try:
        response = client.get(url, params=params)
        if response.status_code != 200:
            return 0
        
        data = response.json()
        protocol = data.get("protocolSection", {})
        
        downloaded = 0
        
        # Check for documents
        docs_module = protocol.get("documentSection", {})
        if docs_module:
            for doc in docs_module.get("documents", []):
                doc_type = doc.get("type", "unknown")
                if doc.get("url"):
                    pdf_url = doc["url"]
                    if download_pdf(db, nct_id, doc_type, pdf_url):
                        downloaded += 1
        
        # Also check for results (they often have PDFs)
        results_module = protocol.get("resultsSection", {})
        if results_module:
            # Results often link to PDFs in various places
            # For now, just mark we found the trial - actual PDF download 
            # might require different endpoints or scraping
        
        return downloaded
        
    except Exception as e:
        logger.debug(f"No PDFs found for {nct_id}: {e}")
        return 0


def download_pdf(db, nct_id: str, doc_type: str, url: str) -> bool:
    """
    Download a PDF and save to data directory.
    Returns True if downloaded successfully.
    """
    try:
        response = httpx.get(url, timeout=30.0)
        if response.status_code != 200:
            return False
        
        # Determine filename
        ext = ".pdf"
        filename = f"{nct_id}_{doc_type}{ext}"
        filepath = config.DATA_DIR / filename
        
        # Check if already exists
        if filepath.exists():
            # Verify hash
            file_hash = compute_file_hash(filepath)
            existing = db.query(Document).filter(Document.file_hash == file_hash).first()
            if existing:
                logger.debug(f"PDF already exists: {filename}")
                return False
        
        # Save file
        filepath.write_bytes(response.content)
        
        # Compute hash and create DB record
        file_hash = compute_file_hash(filepath)
        
        # Get trial
        trial = db.query(Trial).filter(Trial.nct_id == nct_id).first()
        if not trial:
            return False
        
        # Create document record
        doc = Document(
            trial_id=trial.id,
            nct_id=nct_id,
            doc_type=doc_type,
            file_path=str(filepath),
            file_hash=file_hash,
        )
        
        db.add(doc)
        db.commit()
        
        logger.info(f"Downloaded: {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error downloading PDF for {nct_id}: {e}")
        return False


def crawl_trials(limit: int = 10, conditions: Optional[list] = None) -> dict:
    """
    Main crawl function - called from CLI.
    """
    return search_trials(limit=limit, conditions=conditions)


# Also support async for future use
async def crawl_trials_async(limit: int = 10, conditions: Optional[list] = None) -> dict:
    """Async version using httpx."""
    return search_trials(limit=limit, conditions=conditions)
