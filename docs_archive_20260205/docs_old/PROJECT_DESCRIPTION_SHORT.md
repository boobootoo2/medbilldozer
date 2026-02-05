# medBillDozer - Project Description (Submission Version)

## Project Name

medBillDozer

## Your Team

John Shultz — Software Engineer & Data Engineer  
Responsible for system design, model integration, document analysis logic, and user experience.

## Problem Statement

Medical billing errors are common, difficult to detect, and financially stressful for patients. A single episode of care often produces multiple disconnected documents — hospital bills, insurance claims, pharmacy receipts, dental statements, and FSA claim histories — each with its own terminology, rules, and timelines.

Patients are expected to reconcile these documents manually, despite:

- Inconsistent billing codes
- Opaque coverage rules
- Delayed or missing claims
- Unclear responsibility between insurers, providers, and benefit administrators

As a result, patients frequently overpay, miss reimbursements, or fail to challenge incorrect charges — not because the information is unavailable, but because it is fragmented and hard to interpret.

medBillDozer addresses this gap by helping users surface likely billing inconsistencies and administrative errors across real-world healthcare documents, enabling more informed follow-up and dispute resolution.

## Overall Solution

medBillDozer is a human-centered analysis tool that uses **MedGemma**, an open-weight healthcare-focused language model from Google's Health AI Developer Foundations (HAI-DEF), to analyze medical billing and benefits documents.

Rather than offering clinical advice, the system focuses on administrative reasoning, including:

- Detecting duplicate procedures on the same date of service
- Identifying coverage mismatches for preventive services
- Flagging unbundled or inconsistent charges
- Highlighting FSA-eligible expenses that may be missing from claim histories
- Reconciling insurance copays with FSA reimbursements to estimate true out-of-pocket cost

MedGemma is used to extract structured signals and patterns from unstructured billing text, while deterministic reconciliation logic is applied to identify inconsistencies and generate clear, actionable explanations for users.

The application features **Billy and Billie**, character guides with dual-voice audio narration (OpenAI Neural TTS) that introduce the app and provide step-by-step guidance through an accessible 9-step interactive tour. The system includes audio narration for all onboarding steps, screen reader support, and graceful fallbacks for accessibility.

The result is a transparent assistant that helps users understand where to ask questions — not what medical decisions to make.

## Technical Details

### Model Usage

**MedGemma** is the primary analysis engine used to:

- Interpret healthcare-specific billing language
- Identify administrative signals such as procedure duplication, copays, and eligibility indicators
- Support cross-document reconciliation in privacy-sensitive contexts

An optional fallback model is used only for non-critical summarization tasks to improve robustness. All core reasoning is driven by MedGemma outputs combined with deterministic logic.

This design supports:

- Offline or edge deployment
- Reduced reliance on closed, cloud-only models
- Alignment with real clinical and administrative environments

### Application Architecture

The application consists of:

1. **Interactive Streamlit UI** with:
   - Fullscreen splash screen featuring Billy & Billie character introductions
   - Dual-voice audio narration (Billy: echo/male, Billie: nova/female)
   - 9-step guided tour with per-step audio narration
   - Accessible design with ARIA support and keyboard navigation

2. **Model-Agnostic Analysis Layer** with:
   - MedGemma-first adapter with fallback support
   - Structured extraction pipeline for billing codes

3. **Rule-Based Reconciliation Logic** for:
   - Detecting common billing inconsistencies
   - Cross-document validation (EOB vs. provider bill)

4. **Profile & Data Management**:
   - User profile editor for insurance and provider information
   - Plaid-inspired data importer for EOBs and claim histories
   - Privacy-first local storage (no cloud databases)

5. **API & Integration Layer**:
   - RESTful API for programmatic document analysis
   - Designed for integration with insurer portals and provider systems

6. **Accessibility Features**:
   - OpenAI Neural TTS for character voices (Billy/Billie)
   - Audio narration for all 9 guided tour steps
   - Screen reader support with ARIA live regions
   - Graceful fallback when audio unavailable

Static demo documents (hospital bills, pharmacy receipts, dental statements, insurance claim histories, and FSA records) are used to demonstrate realistic workflows and error scenarios.

### Production Deployment

- **Pre-generated audio assets** (~1 MB total) for zero-latency playback
- **Smart caching** eliminates runtime TTS API calls in production
- **Cost-effective** (~$0.46 one-time for all audio generation)
- **Graceful degradation** (works without audio if files missing)
- Currently deployed on **Streamlit Cloud**

## Product Feasibility

medBillDozer is designed as a production-ready prototype that reflects real deployment constraints:

✅ No reliance on PHI  
✅ No clinical decision-making  
✅ Explainable outputs suitable for patient use  
✅ Privacy-sensitive architecture compatible with offline or edge deployment  
✅ Accessible design with audio narration and screen reader support  

The approach can be extended to integrate directly with insurer portals, provider billing systems, or benefits administrators.

## Impact Potential

If deployed, medBillDozer could help patients:

- **Avoid unnecessary payments** by catching billing errors before payment
- **Recover missed reimbursements** from FSA/HSA administrators
- **Reduce administrative burden** (from hours to minutes)
- **Engage more confidently** with providers and insurers armed with evidence
- **Access billing analysis** through audio-enhanced, accessible interface

By focusing on administrative clarity rather than clinical judgment, the system complements existing healthcare tools while addressing a persistent and underserved pain point.

### Accessibility Impact

The dual-voice character system (Billy & Billie) with OpenAI Neural TTS makes medical billing analysis accessible to:

- Visually impaired users (audio narration + screen reader support)
- Users with limited health literacy (plain language + audio explanations)
- Mobile users (responsive design with audio guidance)
- Users who prefer multi-modal learning (audio + visual + interactive)

## Key Technical Innovations

1. **Dual-Voice Character System**: Billy (male/echo) and Billie (female/nova) with distinct personalities and synchronized audio/visual guidance

2. **Audio-Enhanced Guided Tour**: 9-step interactive onboarding with per-step audio narration, visual progress tracking, and skip/resume capability

3. **MedGemma-First Architecture**: Healthcare-aligned model for billing analysis with deterministic validation and explainable outputs

4. **Privacy-First Design**: No cloud storage, stateless API, compatible with HIPAA-compliant deployments

5. **Production-Ready Audio**: Pre-generated OpenAI Neural TTS assets with smart caching for zero-latency playback and no runtime costs

## Alignment with HAI-DEF Principles

medBillDozer follows Health AI Developer Foundations best practices:

- **Separation of Responsibilities**: Modular pipeline (extraction → normalization → analysis → presentation)
- **Explainability Over Automation**: Flags issues with evidence, recommends next steps, defers decisions to users
- **Human-in-the-Loop**: All outputs require human review and judgment
- **Privacy & Security**: No PHI storage, stateless design, offline-compatible

## Summary

medBillDozer demonstrates that healthcare-aligned AI (MedGemma) can be deployed in a safe, explainable, and user-friendly manner to address real patient pain points. The addition of dual-voice audio narration (Billy & Billie) with OpenAI Neural TTS creates an accessible, engaging experience that makes medical billing analysis available to all users, including those with visual impairments or limited health literacy.

**Technology Stack**: Python, Streamlit, MedGemma, OpenAI TTS, GitHub Actions  
**Status**: Production-deployed on Streamlit Cloud  
**Impact**: Accessible billing analysis for all patients through AI-powered administrative clarity
