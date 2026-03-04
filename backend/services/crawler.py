"""
Clinicaltrials.gov API crawler - stores structured text as documents.
"""
import json
import logging
from typing import Optional

import requests

import config
from db import SessionLocal, Trial, Document, get_or_create_trial, compute_file_hash

logger = logging.getLogger(__name__)

BASE_URL = "https://clinicaltrials.gov/api/v2"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}


def search_trials(
    limit: int = 10,
    conditions: Optional[list] = None,
    query: str = "",
) -> dict:
    """
    Search clinicaltrials.gov for trials and store structured text as documents.
    """
    # Build query
    if conditions:
        query_param = " ".join(conditions)
    elif query:
        query_param = query
    else:
        query_param = ""
    
    params = {
        "pageSize": min(limit, 100),
    }
    
    if query_param:
        params["query.cond"] = query_param
    
    url = f"{BASE_URL}/studies"
    
    results = {
        "trials_found": 0,
        "new_documents": 0,
        "updated": 0,
    }
    
    response = requests.get(url, params=params, headers=HEADERS, timeout=60)
    response.raise_for_status()
    
    data = response.json()
    studies = data.get("studies", [])
    
    for study in studies:
        protocol = study.get("protocolSection", {})
        
        # Extract fields
        identification = protocol.get("identificationModule", {})
        nct_id = identification.get("nctId")
        title = identification.get("briefTitle", "Untitled")
        sponsor = identification.get("leadSponsorName")
        
        status_module = protocol.get("statusModule", {})
        status = status_module.get("overallStatus", "UNKNOWN")
        
        conditions_list = protocol.get("conditionsModule", {}).get("conditions", [])
        interventions = protocol.get("armsInterventionsModule", {}).get("interventions", [])
        
        description = protocol.get("descriptionModule", {}).get("briefSummary", "")
        
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
            
            # Create document from structured text
            # Combine all text fields into one document
            text_parts = []
            
            if title:
                text_parts.append(f"Title: {title}")
            if description:
                text_parts.append(f"Summary: {description}")
            if conditions_list:
                text_parts.append(f"Conditions: {', '.join(conditions_list)}")
            if interventions:
                text_parts.append(f"Interventions: {', '.join([i.get('name', '') for i in interventions])}")
            
            # Add outcomes if available
            outcomes_module = protocol.get("outcomesModule", {})
            if outcomes_module:
                primary = outcomes_module.get("primaryOutcomes", [])
                if primary:
                    text_parts.append("Primary Outcomes: " + ", ".join([o.get("measure", "") for o in primary]))
                secondary = outcomes_module.get("secondaryOutcomes", [])
                if secondary:
                    text_parts.append("Secondary Outcomes: " + ", ".join([o.get("measure", "") for o in secondary]))
            
            full_text = "\n\n".join(text_parts)
            
            # Check if document already exists for this trial
            existing_doc = db.query(Document).filter(
                Document.trial_id == trial.id,
                Document.doc_type == "structured"
            ).first()
            
            if not existing_doc:
                # Create fake file_hash for deduplication tracking
                file_hash = f"{nct_id}_structured"
                
                doc = Document(
                    trial_id=trial.id,
                    nct_id=nct_id,
                    doc_type="structured",
                    file_path=f"api://{nct_id}",
                    file_hash=file_hash,
                    raw_text=full_text,
                )
                db.add(doc)
                db.commit()
                results["new_documents"] += 1
                logger.info(f"Created document for {nct_id}")
            else:
                # Update existing
                existing_doc.raw_text = full_text
                db.commit()
                logger.info(f"Updated document for {nct_id}")
                
        except Exception as e:
            logger.error(f"Error processing {nct_id}: {e}")
        finally:
            db.close()
    
    return results


def crawl_trials(limit: int = 10, conditions: Optional[list] = None) -> dict:
    """
    Main crawl function - called from CLI.
    """
    return search_trials(limit=limit, conditions=conditions)
