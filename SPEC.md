# Confydex - Regulatory Review Specification

## AI-Powered Regulatory Review of Protocol Section 3 (Trial Objectives & Estimands)

**Version:** 1.0  
**Date:** March 2026  
**Status:** Stakeholder Requirements

---

## 1. Objective

Build a focused POC that takes a clinical trial protocol (PDF/DOCX) and performs an automated regulatory review specifically on **Section 3: Trial Objectives and Associated Estimands**. The tool should:

- Evaluate whether the primary estimand is properly defined per ICH E9(R1)
- Assess whether the chosen endpoint has regulatory precedent for the indication
- Compare the design to competitor KRAS G12C/G12D programs

---

## 2. Why This Section Matters

Section 3 is the foundation of every FDA/EMA regulatory review. The estimand framework (ICH E9(R1), adopted by FDA in May 2021) is now the lens through which regulators evaluate whether a trial's objectives are clearly defined and approvable.

A poorly defined estimand leads to misalignment between clinical question, trial design, and statistical analysis — which can result in:
- Refuse-to-file
- Clinical hold
- ODAC challenge

---

## 3. Core User Flow

1. **User uploads** the Section 3 protocol document (PDF or DOCX)
2. **LLM agent reviews** the extracted content against:
   - Structured ICH E9(R1) checklist
   - Reference guidance documents
   - Competitor benchmarks
3. **Output:** A structured review report with findings, risk ratings, and recommendations

---

## 4. Estimand Completeness Checklist

The ICH E9(R1) framework defines **four mandatory attributes** of an estimand. The agent must evaluate each:

| # | Attribute | What to Check | Common Deficiency |
|---|----------|---------------|-------------------|
| 1 | **Population** | Is the target population clearly defined through I/E criteria? Does it match the intended label population? | Population described too vaguely; mismatch with Section 5 I/E criteria |
| 2 | **Variable (Endpoint)** | Is the primary endpoint clearly specified? Is the measurement method defined (e.g., RECIST 1.1 by BICR vs. investigator)? | Endpoint stated without specifying assessment method or timing |
| 3 | **Intercurrent Events** | Are intercurrent events identified (treatment discontinuation, rescue therapy, crossover, death)? Is a strategy specified for each (treatment policy, composite, hypothetical, principal stratum, while-on-treatment)? | Intercurrent events not listed or strategy not specified per event |
| 4 | **Population-Level Summary** | Is the summary measure defined (difference in means, hazard ratio, odds ratio, response rate difference)? | Summary measure implied but not explicitly stated |

---

## 5. Additional Checks

- **Internal consistency:** Does the estimand in Section 3 align with the statistical analysis described in Section 10?
- **Estimand-design alignment:** Does the trial design (Section 4) actually support the stated estimand?
- **Multiple estimands:** If secondary estimands exist (Section 3.2), are they clearly differentiated from the primary?
- **Regulatory precedent:** Has this type of estimand/endpoint been accepted by FDA or EMA for the same or analogous indication?

---

## 6. Endpoint Approvability Assessment

For oncology protocols (particularly KRAS-targeted therapies), the agent should assess:

| Endpoint | Approval Pathway | Regulatory Precedent | Risk Flag |
|----------|-----------------|---------------------|------------|
| **ORR** (Objective Response Rate) | Accelerated approval | Accepted for sotorasib (CodeBreaK 100) and adagrasib (KRYSTAL-1) in KRAS G12C NSCLC | Standard for single-arm; FDA now prefers RCTs even for accelerated approval |
| **PFS** (Progression-Free Survival) | Traditional or accelerated | Used in CodeBreaK 200 (sotorasib vs. docetaxel); ODAC found PFS difference too small and unreliable | PFS accepted as surrogate but under increasing scrutiny post-sotorasib CRL |
| **OS** (Overall Survival) | Traditional approval | Gold standard; FDA Aug 2025 draft guidance recommends all RCTs collect OS data | Longer timelines, potential crossover confounding |
| **DOR** (Duration of Response) | Supportive (not standalone) | Reported alongside ORR for both sotorasib and adagrasib approvals | Never used as standalone primary endpoint |

---

## 7. Key Regulatory Signals

### FDA Sotorasib CRL (December 2025)
- FDA issued a Complete Response Letter (CRL) for sotorasib's sNDA seeking full approval
- ODAC voted 10-2 that PFS from CodeBreaK 200 could not be reliably interpreted
- **Precedent:** PFS in open-label KRAS inhibitor trials faces heightened scrutiny

### FDA Draft Guidance (March 2023)
- RCTs are now the **preferred approach** for accelerated approval
- Moving away from single-arm trials

### FDA Draft Guidance (August 2025)
- All randomized oncology trials should collect OS data
- Even when OS is not the primary endpoint

---

## 8. Reference Documents

### Tier 1: Core Regulatory Guidance (MUST include)

| Document | URL | Use In Review |
|----------|-----|---------------|
| ICH E9(R1) — Estimands and Sensitivity Analysis (Step 4 Final, Nov 2019) | [ICH PDF](https://database.ich.org/sites/default/files/ICH_E9-R1_Step4.pdf) | Primary reference for estimand framework; defines the 4 attributes |
| FDA Adoption of ICH E9(R1) | [FDA Guidance Page](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/e9r1-estimands-and-sensitivity-analysis-clinical-trials) | FDA-specific implementation (May 2021) |
| EMA Adoption of ICH E9(R1) | [EMA Scientific Guideline](https://www.ema.europa.eu/en/ich-e9-r1-estimands-sensitivity-analysis) | EMA-specific implementation |
| ICH E9(R1) Training Materials | [ICH Training PDF](https://www.ich.org/page/ich-e9-r1-estimands-training) | Practical examples of estimand construction |
| FDA Guidance: Clinical Trial Endpoints for Cancer Drugs (Dec 2018) | [FDA Guidance Page](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-trial-endpoints-approval-cancer-drugs-and-biologics) | Which endpoints are acceptable |
| FDA Draft Guidance: Accelerated Approval (March 2023) | [FDA Draft Guidance PDF](https://www.fda.gov/media/167093/download) | RCTs preferred over single-arm |
| FDA Project Endpoint | [FDA Project Endpoint](https://www.fda.gov/about-fda/center-drug-evaluation-and-research-cder/project-endpoint) | FDA's evolving thinking on oncology endpoints |

### Tier 2: Competitor Approval Packages (MUST include for benchmarking)

| Document | URL | Use In Review |
|----------|-----|---------------|
| Sotorasib (Lumakras) — Multi-Discipline Review (NDA 214665) | [FDA Accessdata PDF](https://www.accessdata.fda.gov/drugsatfda_docs/nda/2021/214665Orig1s000MultidisciplineR.pdf) | Full FDA review; endpoint rationale, statistical review |
| Sotorasib FDA Accelerated Approval (May 2021) | [FDA Approval Page](https://www.fda.gov/drugs/drug-approvals-and-databases/drug-approvals-tool) | Endpoint accepted: ORR by BICR per RECIST 1.1 |
| Adagrasib (Krazati) — Multi-Discipline Review (NDA 216340) | [FDA Accessdata PDF](https://www.accessdata.fda.gov/drugsatfda_docs/nda/2022/216340Orig1s000MultidisciplineR.pdf) | Full FDA review of KRYSTAL-1 |
| Adagrasib FDA Accelerated Approval (Dec 2022) | [FDA Approval Page](https://www.fda.gov/drugs/drug-approvals-and-databases/drug-approvals-tool) | Approved based on ORR and DOR |
| Sotorasib CRL / Full Approval Rejection | [OncLive Article](https://www.onclive.com/view/fda-issues-crl-to-sotorasib-s-nda) | ODAC voted 10-2 that PFS was unreliable |

### Tier 3: KRAS G12D Competitor Landscape (Include for competitive benchmarking)

| Program | Sponsor | Trial ID | Status | Key Data |
|---------|---------|----------|--------|----------|
| Zoldonrasib (RMC-9805) | Revolution Medicines | NCT06040541 | Phase 1; FDA Breakthrough (Jan 2026) | 61% ORR in NSCLC at 1200 mg daily (n=18); 89% DCR |
| VS-7375 (GFH375) | Verastem / GenFleet | NCT06500676, NCT07020221 | Phase 1/2a; FDA Fast Track (July 2025) | 52% ORR in PDAC (n=23); 68.8% ORR in NSCLC at RP2D |
| INCB161734 | Incyte | Phase 1/2 | Phase 1; Pivotal planned 2026 | 34% ORR in PDAC at 1200 mg daily |
| HRS-4642 | Jiangsu HengRui | Phase 1/2 (China) | Phase 1/2 | 25% confirmed ORR in PDAC; 63% ORR with chemo combo in 1L PDAC |
| MRTX1133 | Mirati / BMS | Preclinical-to-Phase 1 | Early stage | Preclinical G12D inhibitor |

### Tier 4: Supplementary References

| Resource | URL | Use |
|----------|-----|-----|
| ICH E9(R1) Primer (BMJ/PMC) | [PMC Article](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7167182/) | Accessible explainer of estimand framework |
| ClinicalTrials.gov | https://clinicaltrials.gov | Compare competitor trial designs, endpoints, I/E criteria |
| Drugs@FDA | https://www.accessdata.fda.gov/scripts/cder/daf/ | Pull approval packages |
| EMA EPARs | https://www.ema.europa.eu/en/medicines | European regulatory precedent |

---

## 9. Output Format

The agent should generate a structured review report with the following sections:

```
SECTION 3 REGULATORY REVIEW REPORT
====================================

1. EXECUTIVE SUMMARY
   - Overall risk rating (High / Medium / Low)
   - Top 3 findings
   - Recommendation: Approvable as-is / Revisions needed / Major concerns

2. ESTIMAND COMPLETENESS ASSESSMENT
   - Population: [Defined / Partially Defined / Missing] — Detail
   - Variable: [Defined / Partially Defined / Missing] — Detail
   - Intercurrent Events: [Defined / Partially Defined / Missing] — Detail
   - Population-Level Summary: [Defined / Partially Defined / Missing] — Detail
   - ICH E9(R1) Compliance Score: [X/4 attributes fully defined]

3. ENDPOINT APPROVABILITY ASSESSMENT
   - Primary endpoint identified: [ORR / PFS / OS / Other]
   - Approval pathway implied: [Accelerated / Traditional / Unclear]
   - Regulatory precedent: [Strong / Moderate / Weak / None]
   - Key risk: [Description of primary concern]

4. COMPETITIVE BENCHMARK COMPARISON
   Table comparing this protocol's endpoint choice, assessment method,
   and estimand structure vs. 2-3 closest competitor programs

5. INTERNAL CONSISTENCY FLAGS
   - Section 3 vs. Section 10 (Statistical Plan) alignment
   - Section 3 vs. Section 4 (Trial Design) alignment
   - Section 3 vs. Section 5 (Population) alignment

6. DETAILED FINDINGS
   - Finding 1: [Description] | Risk: [H/M/L] | Recommendation
   - Finding 2: [Description] | Risk: [H/M/L] | Recommendation
   - ...

7. RECOMMENDED ACTIONS
   - Prioritized list of revisions before agency submission
```

---

## 10. Prompt Architecture

### SYSTEM PROMPT:
```
You are a VP of Regulatory Affairs reviewing a clinical trial protocol.
Your task is to evaluate Section 3 (Trial Objectives and Estimands)
against the ICH E9(R1) estimand framework and FDA/EMA regulatory
precedent for oncology programs.

[Insert chunked reference guidance here]
[Insert competitor benchmark data here]
```

### USER PROMPT:
```
Review the following protocol section and generate a structured
regulatory review report.

[Insert extracted Section 3 text here]
```

---

## 11. Success Criteria

- [ ] Upload a sample oncology protocol → system correctly extracts Section 3 content
- [ ] Agent identifies which of the 4 estimand attributes are present/missing
- [ ] Agent flags whether the primary endpoint has regulatory precedent (with specific references to sotorasib/adagrasib approvals)
- [ ] Agent produces a structured report that a regulatory professional would recognize as directionally accurate
- [ ] End-to-end demo runs in under 60 seconds

---

## 12. Technical Requirements

### Input Handling
- Support PDF and DOCX file uploads
- Extract and isolate Section 3 content specifically
- Handle multi-section protocols (ability to reference Sections 4, 5, 10 for consistency checks)

### LLM Integration
- Configurable LLM provider (OpenAI, Anthropic, or local)
- Reference documents embedded as context (RAG or system prompt)
- Structured output parsing for consistent report format

### Storage
- SQLite database for indexed protocols
- Document storage for uploaded files
- (Future: Vector store for embedding regulatory precedents)

---

*End of Specification*
