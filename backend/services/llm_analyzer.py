"""
LLM Analyzer service - analyzes Section 3 against ICH E9(R1) framework.
"""
import json
from typing import Optional, Dict, Any

import openai
from anthropic import Anthropic

import config


# System prompt for the regulatory review agent
SYSTEM_PROMPT = """You are a VP of Regulatory Affairs reviewing a clinical trial protocol.
Your task is to evaluate Section 3 (Trial Objectives and Estimands) against the ICH E9(R1) 
estimand framework and FDA/EMA regulatory precedent for oncology programs.

## ICH E9(R1) Estimand Framework

An estimand has four mandatory attributes:
1. **Population**: The set of subjects about whom the clinical question is posed
2. **Variable (Endpoint)**: The variable to be observed or measured
3. **Intercurrent Events**: Events that occur after treatment initiation that can affect the interpretation of the variable
4. **Population-Level Summary**: A summary measure for the variable

## Key Regulatory Precedents

### Sotorasib (Lumakras) - CodeBreaK 100/200
- Accelerated approval (May 2021) based on ORR (36%) by BICR per RECIST 1.1
- Full approval denied (Dec 2025) - ODAC voted 10-2 that PFS was unreliable
- Key issue: Open-label design, PFS endpoint in single-arm setting

### Adagrasib (Krazati) - KRYSTAL-1
- Accelerated approval (Dec 2022) based on ORR (43%) and DOR (8.5 months)
- Endpoint: ORR by BICR per RECIST 1.1
- CRC combination approved June 2024

## KRAS G12C/G12D Competitive Landscape
- Zoldonrasib (RMC-9805): 61% ORR in NSCLC (Phase 1)
- VS-7375 (GFH375): 52% ORR in PDAC (Phase 1/2a)
- INCB161734: 34% ORR in PDAC (Phase 1/2)

## FDA Guidance
- March 2023: RCTs now preferred for accelerated approval
- August 2025: All RCTs should collect OS data
- PFS under heightened scrutiny post-sotorasib CRL

Your analysis must check:
1. Are all 4 estimand attributes explicitly defined?
2. Does the endpoint have regulatory precedent?
3. Does the estimand align with trial design (Section 4)?
4. Are intercurrent events properly addressed?
5. What are the key regulatory risks?
"""


class LLMAnalyzer:
    """LLM-powered regulatory review analyzer."""
    
    def __init__(self, provider: str = "openai", model: Optional[str] = None):
        self.provider = provider
        
        if provider == "openai":
            self.model = model or config.OPENAI_MODEL
            openai.api_key = config.OPENAI_API_KEY
        elif provider == "anthropic":
            self.model = model or config.ANTHROPIC_MODEL
            self.anthropic = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def analyze(self, section_3_text: str) -> Dict[str, Any]:
        """
        Analyze Section 3 text and generate regulatory review.
        
        Returns:
            Dictionary with structured review report
        """
        user_prompt = f"""Review the following Section 3 protocol text and generate a structured regulatory review report.

SECTION 3 TEXT:
{section_3_text}

Provide your analysis in the following JSON format (include ALL fields):
{{
  "executive_summary": {{
    "overall_rating": "High|Medium|Low",
    "top_3_findings": ["finding1", "finding2", "finding3"],
    "recommendation": "Approvable as-is|Revisions needed|Major concerns"
  }},
  "estimand_assessment": {{
    "population": "Defined|Partially Defined|Missing",
    "population_detail": "description of population definition",
    "variable": "Defined|Partially Defined|Missing",
    "variable_detail": "description of endpoint and measurement",
    "intercurrent_events": "Defined|Partially Defined|Missing",
    "intercurrent_events_detail": "description of intercurrent events and strategies",
    "population_level_summary": "Defined|Partially Defined|Missing",
    "summary_detail": "description of summary measure",
    "compliance_score": "X/4"
  }},
  "endpoint_assessment": {{
    "primary_endpoint": "ORR|PFS|OS|DOR|Other",
    "approval_pathway": "Accelerated|Traditional|Unclear",
    "regulatory_precedent": "Strong|Moderate|Weak|None",
    "key_risk": "description of primary regulatory concern"
  }},
  "competitive_comparison": [
    {{
      "program": "program name",
      "endpoint": "ORR/PFS/OS",
      "estimand_notes": "key estimand features",
      "status": "approved/in-review"
    }}
  ],
  "consistency_flags": {{
    "section_3_vs_section_10": "Aligned|Misaligned|Cannot assess",
    "section_3_vs_section_4": "Aligned|Misaligned|Cannot assess",
    "section_3_vs_section_5": "Aligned|Misaligned|Cannot assess"
  }},
  "detailed_findings": [
    {{
      "finding": "description",
      "risk": "H|M|L",
      "recommendation": "what to do"
    }}
  ],
  "recommended_actions": ["action1", "action2"]
}}

IMPORTANT: Return ONLY valid JSON, no additional text."""

        if self.provider == "openai":
            return self._analyze_openai(user_prompt)
        else:
            return self._analyze_anthropic(user_prompt)
    
    def _analyze_openai(self, user_prompt: str) -> Dict[str, Any]:
        """Analyze using OpenAI."""
        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    def _analyze_anthropic(self, user_prompt: str) -> Dict[str, Any]:
        """Analyze using Anthropic."""
        message = self.anthropic.messages.create(
            model=self.model,
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        content = message.content[0].text
        return json.loads(content)
    
    def extract_review_fields(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key fields for the reviews table."""
        exec_summary = report.get("executive_summary", {})
        estimand = report.get("estimand_assessment", {})
        endpoint = report.get("endpoint_assessment", {})
        
        # Parse estimand score (e.g., "3/4" -> 3)
        score_str = estimand.get("compliance_score", "0/4")
        try:
            score = int(score_str.split("/")[0])
        except (ValueError, IndexError):
            score = 0
        
        return {
            "overall_rating": exec_summary.get("overall_rating", "Unknown"),
            "recommendation": exec_summary.get("recommendation", "Unknown"),
            "estimand_score": score,
            "endpoint": endpoint.get("primary_endpoint", "Unknown")
        }


def get_analyzer(provider: Optional[str] = None) -> LLMAnalyzer:
    """Get LLMAnalyzer instance."""
    provider = provider or config.LLM_PROVIDER
    return LLMAnalyzer(provider=provider)
