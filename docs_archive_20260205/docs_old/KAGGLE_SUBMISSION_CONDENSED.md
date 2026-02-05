# medBillDozer – MedGemma Impact Challenge Submission (Condensed)

## Project Name
**medBillDozer**

## Your Team
**John Shultz** — Software Engineer & Data Engineer  
Responsible for system design, MedGemma integration, deterministic validation pipeline, user experience, accessibility features, and production deployment.

---

## Problem Statement

Medical billing errors impose significant financial and administrative burdens on patients. Studies indicate that 30-40% of medical bills contain errors[1,2], with individual discrepancies ranging from $50 to over $500[3]. In the United States alone, patients face an estimated $500M–$5B in avoidable annual costs due to duplicate charges, coding errors, unbundled procedures, and coverage mismatches[4].

These errors persist because patients lack tools to validate billing structures across fragmented documents—hospital bills, insurance Explanation of Benefits (EOBs), pharmacy receipts, and Flexible Spending Account (FSA) claims. Each document uses different terminology, coding standards, and timelines, requiring specialized administrative knowledge to reconcile.

Existing solutions either focus on provider-side automation or offer consumer tools without healthcare-specific reasoning capabilities. What patients need is **structured validation support**—not clinical advice, but administrative clarity grounded in billing logic and procedural coding.

---

## Overall Solution

**medBillDozer** is a privacy-first analysis tool that uses **MedGemma**, Google's healthcare-aligned language model, to extract and validate structured billing information from synthetic healthcare documents.

The system operates through a **deterministic execution graph**:

1. **Document Classification**: Regex-based identification of document type (medical bill, insurance EOB, pharmacy receipt, dental statement, FSA claim).
2. **Fact Extraction**: MedGemma extracts structured fields—procedure codes (CPT/CDT), dates of service, billed amounts, allowed amounts, patient responsibility—from unstructured text.
3. **Normalization**: Extracted facts are standardized into a consistent schema for cross-document comparison.
4. **Rule-Based Reconciliation**: Deterministic logic detects duplicate charges (same CPT + date + amount), coding inconsistencies, coverage mismatches for preventive services, and FSA eligibility gaps.
5. **Presentation**: Findings are surfaced with evidence, explanations, and recommended next steps—empowering users to follow up with providers or insurers.

**Key Design Principle**: MedGemma validates structured findings from deterministic processing rather than generating open-ended analyses. This constrained execution graph mitigates hallucination risk and ensures reproducible outputs.

**Demonstration Context**: This proof-of-concept uses synthetic/mock healthcare billing documents intentionally created to reflect realistic billing structures, coding patterns, and reimbursement scenarios. This approach ensures PHI protection, reproducibility, and safe demonstration while maintaining workflow transferability to real-world data.

---

## Technical Details

### Effective Use of MedGemma (HAI-DEF Models)

**MedGemma's Role in the Pipeline**:
- **Healthcare-Specific Reasoning**: MedGemma interprets CPT/CDT codes, interprets insurance terminology (e.g., "allowed amount," "copay," "coinsurance"), and identifies billing relationships that general LLMs misinterpret.
- **Structured Extraction**: Using constrained prompts, MedGemma extracts key-value pairs (e.g., `{"cpt_code": "99213", "date_of_service": "2024-01-15", "patient_responsibility": 45.00}`) rather than generating prose.
- **Validation Layer**: MedGemma validates extracted patterns against known billing norms (e.g., duplicate charge detection, preventive service coverage rules).
- **Conservative Estimation**: Savings estimates are constrained to document-supported values only—no speculative insurance outcomes.

**Hallucination Mitigation**:
- Deterministic pre-processing limits MedGemma's input to relevant document sections.
- JSON schema enforcement prevents unconstrained generation.
- Rule-based post-processing validates model outputs against known billing logic.

**Open-Weight Deployability**:
- MedGemma's open-weight architecture supports offline/edge deployment—critical for privacy-sensitive healthcare environments.
- No dependency on proprietary cloud APIs for core analysis.

**Technical Implementation**:
```python
# MedGemma extracts structured facts via constrained prompt
facts = medgemma_provider.analyze_document(document_text)

# Deterministic reconciliation validates findings
issues = deterministic_issues_from_facts(facts)

# Combined output includes evidence and conservative savings
for issue in issues:
    print(f"{issue.type}: {issue.summary}")
    print(f"Evidence: {issue.evidence}")
    print(f"Max Savings: ${issue.max_savings}")
```

### Application Architecture

**Modular Pipeline**:
1. **Extraction Module**: Document classification (regex-based) + MedGemma fact extraction
2. **Normalization Module**: Schema standardization across document types
3. **Reconciliation Module**: Deterministic billing validation logic
4. **Presentation Layer**: Streamlit UI with evidence display and action recommendations

**Privacy-First Design**:
- Stateless API: No persistent storage of PHI
- Local execution: Compatible with offline/edge deployment
- No third-party logging of billing data

**Accessibility Features**:
- Dual-voice audio narration (Billy & Billie characters) using OpenAI Neural TTS
- 9-step interactive guided tour with screen reader support
- Pre-generated audio assets (~1 MB total) eliminate runtime API dependencies

**Deployment Configuration**:
- Production-deployed on Streamlit Cloud
- Docker-compatible for enterprise integration
- RESTful API for programmatic access

---

## Product Feasibility

**Production Readiness**:
- **Modular Design**: Each pipeline stage (extraction → normalization → analysis → presentation) is independently testable and replaceable.
- **Deterministic Validation**: Rule-based reconciliation provides reproducible, auditable outputs.
- **Privacy-First Architecture**: No PHI persistence beyond user session; compatible with HIPAA-compliant deployments.
- **Open-Weight Compatibility**: MedGemma enables offline deployment in regulated environments (hospitals, insurers, benefits administrators).

**Real-World Deployment Pathway**:
1. **Patient Tools**: Browser extension or mobile app integrating with insurer portals
2. **Provider Integration**: Billing systems surface potential errors pre-submission
3. **Benefits Administrators**: Automated pre-payment validation for FSA/HSA claims

**Limitations Acknowledged**:
- Demonstration uses synthetic data; clinical validation with real PHI requires partnership with healthcare institutions.
- Current workflow assumes readable text; future work includes OCR integration for scanned documents.
- Conservative savings estimates may underestimate actual patient impact.

**Cost Efficiency**:
- MedGemma inference: Open-weight model eliminates per-query API costs
- Audio assets: $0.46 one-time TTS generation cost (pre-generated, zero runtime cost)
- Compute: Streamlit Cloud free tier supports prototype; production scales via containerization

---

## Impact Potential

**Financial Impact**:
- Target population: 100M+ insured Americans with employer-sponsored or marketplace health plans[5]
- If 30% of bills contain errors averaging $150 in patient overpayment, annual addressable impact: **$4.5B in avoidable costs**[1,2]
- Even a 10% error detection rate could save patients **$450M annually**

**Administrative Burden Reduction**:
- Average time to manually reconcile billing documents: 2-4 hours per episode of care[6]
- medBillDozer reduces this to minutes, freeing patients to focus on health rather than paperwork

**Accessibility Impact**:
- Audio narration and plain-language explanations make billing analysis accessible to visually impaired users and those with limited health literacy
- Character-driven UX (Billy & Billie) reduces intimidation factor for vulnerable populations

**Systemic Impact**:
- Empowers patients to challenge incorrect charges, creating feedback loops that incentivize provider billing accuracy
- Supports health equity by reducing financial barriers disproportionately affecting low-income and underinsured populations

**Scalability**:
- Open-weight MedGemma enables deployment by insurers, employers, or benefits administrators without vendor lock-in
- Modular architecture supports integration with existing EHR systems, patient portals, and claims processing platforms

---

## Execution and Communication

**Demonstration Strategy**:
This submission includes:
1. **GitHub Repository**: Fully documented codebase with 25+ markdown guides covering architecture, API usage, and deployment
2. **Live Demo**: Production-deployed Streamlit application showcasing end-to-end workflow on synthetic healthcare documents
3. **Video Walkthrough**: Narrated demonstration highlighting MedGemma integration, deterministic validation, and user workflow

**Synthetic Data Transparency**:
The demonstration uses carefully constructed mock billing documents to:
- Avoid PHI exposure
- Ensure reproducibility for judges and stakeholders
- Demonstrate workflow behavior safely
- Maintain alignment with privacy-sensitive healthcare deployment principles

These synthetic documents reflect realistic billing structures (CPT codes, insurance terminology, reimbursement patterns) encountered in real-world scenarios. The workflows and architecture are transferable to real data in production environments.

**Technical Documentation**:
- `HAI_DEF_ALIGNMENT.md`: Details alignment with Health AI Developer Foundations principles
- `MODULES.md`: Comprehensive API reference for all pipeline components
- `INGESTION_SERVICE_README.md`: RESTful API specification for programmatic integration
- `PROFILE_EDITOR_ARCHITECTURE.md`: User data management and privacy safeguards

**Alignment with HAI-DEF Principles**:
- **Separation of Responsibilities**: Modular pipeline reduces hallucination risk
- **Explainability Over Automation**: System flags issues with evidence; users make decisions
- **Human-in-the-Loop**: No autonomous corrections or submissions; all actions require user confirmation
- **Privacy & Security**: Stateless design, no PHI storage, offline deployment compatibility

**Communication for Judges**:
This writeup is structured for technical evaluators from Google Health AI and Research backgrounds, emphasizing:
- MedGemma's specific technical contributions (structured extraction, healthcare-aligned reasoning)
- Deterministic validation as a hallucination mitigation strategy
- Privacy-first architecture as a deployment enabler in regulated environments
- Synthetic data as an intentional choice for safe demonstration

---

## Summary

**medBillDozer** demonstrates that healthcare-aligned AI (MedGemma) can be deployed safely and effectively to address a high-impact patient pain point—medical billing errors. By combining MedGemma's healthcare-specific reasoning with deterministic validation and privacy-first design, the system provides structured administrative clarity without clinical overreach.

The use of synthetic healthcare documents ensures reproducible demonstration while maintaining transferability to real-world deployment contexts. With open-weight deployability, modular architecture, and accessibility features, medBillDozer represents a feasible, scalable approach to reducing the $500M–$5B annual burden of billing errors on patients.

**Status**: Production-deployed prototype  
**Technology Stack**: Python, Streamlit, MedGemma (open-weight), OpenAI TTS, Docker  
**Impact**: Accessible billing validation for all patients through AI-assisted administrative clarity

---

## References

[1] Medical Billing Advocates of America (2023), [2] Equifax Healthcare Payment Accuracy Report (2022), [3] Becker's Hospital Review (2023), [4] National Patient Advocate Foundation (2024), [5] U.S. Census Bureau Health Insurance Coverage (2024), [6] Patient Advocate Foundation Navigation Study (2023). Full citations available in supplementary documentation.
