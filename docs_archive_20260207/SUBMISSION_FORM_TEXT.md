# medBillDozer - Submission Form Text

Copy and paste these sections into submission forms.

---

## Project Name

```
medBillDozer
```

---

## Your Team

```
John Shultz — Software Engineer & Data Engineer
Responsible for system design, model integration, document analysis logic, user experience, accessibility features, and production deployment.
```

---

## Problem Statement

```
Medical billing errors are common, difficult to detect, and financially stressful for patients. A single episode of care often produces multiple disconnected documents — hospital bills, insurance claims, pharmacy receipts, dental statements, and FSA claim histories — each with its own terminology, rules, and timelines.

Patients are expected to reconcile these documents manually, despite:
• Inconsistent billing codes across providers
• Opaque coverage rules that vary by plan and procedure
• Delayed or missing claims from insurers
• Unclear responsibility between insurers, providers, and benefit administrators

As a result, patients frequently overpay, miss reimbursements, or fail to challenge incorrect charges — not because the information is unavailable, but because it is fragmented and hard to interpret.

medBillDozer addresses this gap by helping users surface likely billing inconsistencies and administrative errors across real-world healthcare documents, enabling more informed follow-up and dispute resolution.
```

---

## Overall Solution

```
medBillDozer is a human-centered analysis tool that uses MedGemma, an open-weight healthcare-focused language model from Google's Health AI Developer Foundations (HAI-DEF), to analyze medical billing and benefits documents.

Rather than offering clinical advice, the system focuses on administrative reasoning, including:
• Detecting duplicate procedures on the same date of service
• Identifying coverage mismatches for preventive services
• Flagging unbundled or inconsistent charges
• Highlighting FSA-eligible expenses that may be missing from claim histories
• Reconciling insurance copays with FSA reimbursements to estimate true out-of-pocket cost

MedGemma is used to extract structured signals and patterns from unstructured billing text, while deterministic reconciliation logic is applied to identify inconsistencies and generate clear, actionable explanations for users.

The application features Billy and Billie, character guides with dual-voice audio narration (OpenAI Neural TTS) that introduce the app and provide step-by-step guidance through an accessible 9-step interactive tour. The system includes audio narration for all onboarding steps, screen reader support, and graceful fallbacks for accessibility.

The result is a transparent assistant that helps users understand where to ask questions — not what medical decisions to make.
```

---

## Technical Details - Model Usage

```
MedGemma is the primary analysis engine used to:
• Interpret healthcare-specific billing language
• Identify administrative signals such as procedure duplication, copays, and eligibility indicators
• Support cross-document reconciliation in privacy-sensitive contexts

An optional fallback model is used only for non-critical summarization tasks to improve robustness. All core medical reasoning is driven by MedGemma outputs combined with deterministic logic.

This design supports:
• Offline or edge deployment
• Reduced reliance on closed, cloud-only models
• Alignment with real clinical and administrative environments
```

---

## Technical Details - Application Architecture

```
The application consists of:

1. Interactive Streamlit UI with:
   • Fullscreen splash screen featuring Billy & Billie character introductions
   • Dual-voice audio narration (Billy: echo/male, Billie: nova/female)
   • 9-step guided tour with per-step audio narration
   • Accessible design with ARIA support and keyboard navigation

2. Model-Agnostic Analysis Layer with:
   • MedGemma-first adapter with fallback support
   • Structured extraction pipeline for billing codes

3. Rule-Based Reconciliation Logic for:
   • Detecting common billing inconsistencies
   • Cross-document validation (EOB vs. provider bill)

4. Profile & Data Management:
   • User profile editor for insurance and provider information
   • Plaid-inspired data importer for EOBs and claim histories
   • Privacy-first local storage (no cloud databases)

5. API & Integration Layer:
   • RESTful API for programmatic document analysis
   • Designed for integration with insurer portals and provider systems

6. Accessibility Features:
   • OpenAI Neural TTS for character voices (Billy/Billie)
   • Audio narration for all 9 guided tour steps
   • Screen reader support with ARIA live regions
   • Graceful fallback when audio unavailable

Static demo documents (hospital bills, pharmacy receipts, dental statements, insurance claim histories, and FSA records) are used to demonstrate realistic workflows and error scenarios.
```

---

## Product Feasibility

```
medBillDozer is designed as a production-ready prototype that reflects real deployment constraints:

✓ No reliance on PHI — Works with redacted or synthetic documents
✓ No clinical decision-making — Focuses on administrative clarity only
✓ Explainable outputs suitable for patient use
✓ Privacy-sensitive architecture — Compatible with offline or edge deployment
✓ Accessible design — Audio narration, screen reader support, keyboard navigation
✓ Production deployment — Currently deployed on Streamlit Cloud

Production features:
• Pre-generated audio assets (~1 MB total) for zero-latency playback
• Smart caching eliminates runtime TTS API calls
• Cost-effective (~$0.46 one-time for all audio generation)
• Graceful degradation (works without audio if files missing)

The approach can be extended to integrate directly with insurer portals, provider billing systems, or benefits administrators.
```

---

## Impact Potential

```
If deployed, medBillDozer could help patients:

Financial Impact:
• Avoid unnecessary payments by catching billing errors before payment
• Recover missed reimbursements from FSA/HSA administrators
• Negotiate charges armed with evidence of overpricing or duplication
• Estimate true out-of-pocket costs by reconciling copays and reimbursements

Administrative Impact:
• Reduce time spent deciphering medical bills (from hours to minutes)
• Lower stress by explaining complex billing documents in plain language
• Increase confidence when challenging incorrect charges
• Streamline disputes with clear evidence and suggested next steps

Accessibility Impact:
• Audio narration makes billing analysis accessible to visually impaired users
• Plain language explanations help users with limited health literacy
• Character-driven UX (Billy & Billie) reduces intimidation factor
• Multi-modal guidance (audio + visual) improves comprehension

By focusing on administrative clarity rather than clinical judgment, the system complements existing healthcare tools while addressing a persistent and underserved pain point.
```

---

## Key Technical Innovations (Optional)

```
1. Dual-Voice Character System: Billy (male/echo) and Billie (female/nova) with distinct personalities and synchronized audio/visual guidance using OpenAI Neural TTS

2. Audio-Enhanced Guided Tour: 9-step interactive onboarding with per-step audio narration, visual progress tracking, and skip/resume capability

3. MedGemma-First Architecture: Healthcare-aligned model for billing analysis with deterministic validation and explainable outputs

4. Privacy-First Design: No cloud storage, stateless API, compatible with HIPAA-compliant deployments

5. Production-Ready Audio: Pre-generated assets with smart caching for zero-latency playback and no runtime costs
```

---

## HAI-DEF Alignment (Optional)

```
medBillDozer follows Health AI Developer Foundations best practices:

• Separation of Responsibilities: Modular pipeline (extraction → normalization → analysis → presentation) reduces hallucinations and improves debuggability

• Explainability Over Automation: Flags potential issues with evidence, recommends next steps, defers decisions to users. No auto-corrections or autonomous actions.

• Human-in-the-Loop: All outputs require human review and judgment. Users provide documents, review findings, and decide whether/how to act.

• Privacy & Security: No PHI storage, stateless API design, compatible with offline deployment and HIPAA-compliant architectures.
```

---

## Project Status & Metrics (Optional)

```
Status: Production-deployed on Streamlit Cloud

Technical Metrics:
• Lines of Code: 10,000+ (Python)
• Documentation Files: 25+ markdown files
• Audio Assets: 12 files (~1 MB total)
• Tour Steps: 9 interactive steps
• Supported Document Types: 5+ (bills, EOBs, receipts, FSA, dental)
• AI Models Supported: 4 (MedGemma, OpenAI, Gemini, Local)
• Test Coverage: Comprehensive pytest suite

Impact Potential:
• Target Users: 100M+ insured Americans
• Avg. Billing Errors: 30-40% of bills contain errors
• Avg. Error Value: $50-$500 per bill
• Potential Annual Savings: $500M-$5B for patients
```

---

## Demo Links (Optional)

```
Live Demo: [Your Streamlit Cloud URL]
GitHub Repository: https://github.com/boobootoo2/medbilldozer
Documentation: 25+ comprehensive markdown guides included
Video Demo: [Link to video submission]
```

---

## Summary (One-Sentence Version)

```
medBillDozer uses MedGemma and dual-voice audio narration (Billy & Billie) to help patients detect billing errors and understand medical bills through an accessible, explainable, privacy-first interface.
```

---

## Summary (Two-Sentence Version)

```
medBillDozer uses MedGemma to analyze medical bills, insurance EOBs, and FSA statements, detecting administrative errors like duplicate charges, coverage mismatches, and unbundled procedures. The application features Billy and Billie, character guides with OpenAI Neural TTS audio narration, providing an accessible 9-step interactive tour with screen reader support and graceful fallbacks.
```

---

## Summary (Short Paragraph)

```
medBillDozer is a human-centered tool that uses MedGemma to help patients detect billing errors across hospital bills, insurance claims, pharmacy receipts, and FSA statements. The application features Billy and Billie, character guides with dual-voice audio narration (OpenAI Neural TTS), providing an accessible 9-step interactive tour with screen reader support. MedGemma extracts structured billing data and identifies administrative issues like duplicate procedures, coverage mismatches, and unbundled charges, while deterministic logic validates findings and generates clear explanations. The system focuses on administrative clarity rather than clinical advice, following HAI-DEF principles with no PHI storage and human-in-the-loop design. Currently production-deployed on Streamlit Cloud with pre-generated audio assets for zero-latency accessibility.
```

---

## Tags/Keywords (If Applicable)

```
medical billing, healthcare AI, MedGemma, accessibility, audio narration, billing errors, insurance claims, patient advocacy, HAI-DEF, TTS, assistive technology, administrative AI, explainable AI, privacy-first, HIPAA-compatible
```

---

## Category (If Applicable)

```
Healthcare / Medical Billing / Patient Tools / Accessibility
```
