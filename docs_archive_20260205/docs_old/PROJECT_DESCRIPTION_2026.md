# medBillDozer - Updated Project Description (2026)

## Project Name

**medBillDozer**

## Your Team

**John Shultz** — Software Engineer & Data Engineer  
Responsible for system design, model integration, document analysis logic, user experience, accessibility features, and production deployment.

_(Solo project demonstrating end-to-end healthcare AI application development)_

---

## Problem Statement

Medical billing errors are common, difficult to detect, and financially stressful for patients. A single episode of care often produces multiple disconnected documents — hospital bills, insurance claims, pharmacy receipts, dental statements, and FSA claim histories — each with its own terminology, rules, and timelines.

Patients are expected to reconcile these documents manually, despite:

- **Inconsistent billing codes** across providers
- **Opaque coverage rules** that vary by plan and procedure
- **Delayed or missing claims** from insurers
- **Unclear responsibility** between insurers, providers, and benefit administrators
- **Fragmented information** across multiple systems and portals

As a result, patients frequently overpay, miss reimbursements, or fail to challenge incorrect charges — not because the information is unavailable, but because it is **fragmented, technical, and hard to interpret**.

medBillDozer addresses this gap by helping users surface likely billing inconsistencies and administrative errors across real-world healthcare documents, enabling more informed follow-up and dispute resolution.

---

## Overall Solution

medBillDozer is a **human-centered analysis tool** that uses **MedGemma**, an open-weight healthcare-focused language model from Google's Health AI Developer Foundations (HAI-DEF), to analyze medical billing and benefits documents.

Rather than offering clinical advice, the system focuses on **administrative reasoning**, including:

- Detecting **duplicate procedures** on the same date of service
- Identifying **coverage mismatches** for preventive services
- Flagging **unbundled or inconsistent charges**
- Highlighting **FSA-eligible expenses** that may be missing from claim histories
- Reconciling **insurance copays with FSA reimbursements** to estimate true out-of-pocket cost
- Cross-referencing **procedure codes (CPT/CDT)** against typical pricing ranges
- Validating **claim consistency** across provider bills and insurance EOBs

MedGemma is used to **extract structured signals and patterns** from unstructured billing text, while deterministic reconciliation logic is applied to identify inconsistencies and generate clear, actionable explanations for users.

The result is a **transparent assistant** that helps users understand **where to ask questions** — not what medical decisions to make.

---

## Technical Details

### Model Usage

**MedGemma** is the primary analysis engine used to:

- Interpret healthcare-specific billing language
- Identify administrative signals such as procedure duplication, copays, and eligibility indicators
- Support cross-document reconciliation in privacy-sensitive contexts
- Extract structured data from unstructured medical documents

An **optional fallback model** (OpenAI GPT-4 or Google Gemini) is used only for non-critical summarization tasks to improve robustness. **All core medical reasoning is driven by MedGemma outputs** combined with deterministic logic.

This design supports:

- **Offline or edge deployment** (MedGemma can run locally)
- **Reduced reliance** on closed, cloud-only models
- **Alignment with real clinical and administrative environments**
- **Privacy-first architecture** (no PHI sent to third-party APIs by default)

### Application Architecture

The application consists of:

1. **Streamlit UI with Interactive Onboarding**
   - Fullscreen splash screen with Billy & Billie character introductions
   - Dual-voice audio narration (OpenAI Neural TTS)
   - 9-step guided tour with autoplay audio narration
   - Accessible design with ARIA support and visual fallbacks

2. **Model-Agnostic Analysis Layer**
   - MedGemma-first adapter with fallback support
   - Provider registry supporting multiple LLM backends
   - Structured extraction pipeline for billing codes and charges

3. **Rule-Based Reconciliation Logic**
   - Deterministic error detection for common billing mistakes
   - Cross-document validation (EOB vs. provider bill)
   - FSA eligibility checking against IRS guidelines

4. **Profile & Data Management**
   - User profile editor for insurance and provider information
   - Plaid-inspired data importer for EOBs and claim histories
   - Privacy-first local storage (no cloud databases)

5. **API & Integration Layer**
   - RESTful API for programmatic document analysis
   - JSON-based data ingestion pipeline
   - Designed for integration with insurer portals and provider systems

6. **Accessibility & UX Features**
   - OpenAI Neural TTS for splash screen (dual-voice: Billy/echo, Billie/nova)
   - Audio narration for all 9 guided tour steps (alloy voice)
   - Screen reader support with ARIA live regions
   - Graceful fallback when audio unavailable
   - Responsive design for mobile and desktop

### Static Demo Documents

The application includes realistic demo documents for testing and demonstration:

- Hospital procedure bills (colonoscopy, imaging)
- Dental treatment bills (crown, cleaning)
- Pharmacy receipts (prescription medications)
- Insurance Explanation of Benefits (EOB)
- FSA/HSA claim histories

These demonstrate realistic workflows and error scenarios without requiring PHI.

---

## Product Feasibility

medBillDozer is designed as a **production-ready prototype** that reflects real deployment constraints:

✅ **No reliance on PHI** — Works with redacted or synthetic documents  
✅ **No clinical decision-making** — Focuses on administrative clarity only  
✅ **Explainable outputs** suitable for patient use  
✅ **Privacy-sensitive architecture** — Compatible with offline or edge deployment  
✅ **Accessible design** — Audio narration, screen reader support, keyboard navigation  
✅ **Production deployment** — Currently deployed on Streamlit Cloud  

### Deployment Features

- **Smart caching** for audio files (no runtime TTS generation)
- **Pre-generated assets** (~1 MB audio files for splash + tour)
- **Zero API dependencies** in production (audio pre-cached)
- **Graceful degradation** (works without audio if files missing)
- **Cost-effective** (~$0.46 one-time for all audio generation)

The approach can be extended to integrate directly with:

- Insurer portals (Blue Cross, UnitedHealthcare, Cigna)
- Provider billing systems (Epic, Cerner)
- Benefits administrators (FSA/HSA platforms)
- Employer health benefit portals

---

## Technical Innovation

### 1. Dual-Voice Character System

**Billy and Billie** serve as user guides with distinct personalities:

- **Billy** (male, echo voice): Technical explanations and billing analysis
- **Billie** (female, nova voice): Welcomes users and provides guidance

Implemented using:
- OpenAI Neural TTS (tts-1 model)
- Character-specific voice selection
- Synchronized audio with visual speech bubbles
- Real-time transcript highlighting

### 2. Audio-Enhanced Guided Tour

**9-step interactive tour** with:
- Per-step audio narration (autoplay)
- Visual progress tracking
- Contextual help messages
- Skippable and resumable
- Accessible to screen readers

Audio specifications:
- Format: MP3, 128kbps
- Total size: ~712 KB (tour) + ~310 KB (splash)
- Pre-generated with smart caching
- Zero production API calls

### 3. MedGemma-First Architecture

**Healthcare-aligned model usage:**
- MedGemma for medical billing analysis (primary)
- OpenAI/Gemini for summarization only (fallback)
- Deterministic logic for validation
- Explainable outputs with evidence

### 4. Privacy-First Design

**No cloud storage or databases:**
- All analysis happens client-side or in stateless compute
- No PHI persisted beyond user session
- API designed for stateless operation
- Compatible with HIPAA-compliant deployments

---

## Impact Potential

If deployed at scale, medBillDozer could help patients:

### Financial Impact

- **Avoid unnecessary payments** by catching billing errors before payment
- **Recover missed reimbursements** from FSA/HSA administrators
- **Negotiate charges** armed with evidence of overpricing or duplication
- **Estimate true out-of-pocket costs** by reconciling copays and reimbursements

### Administrative Impact

- **Reduce time spent** deciphering medical bills (from hours to minutes)
- **Lower stress** by explaining complex billing documents in plain language
- **Increase confidence** when challenging incorrect charges
- **Streamline disputes** with clear evidence and suggested next steps

### Healthcare System Impact

- **Improve billing accuracy** through systematic error detection
- **Reduce administrative burden** on patients and providers
- **Enable data-driven auditing** of billing practices
- **Support value-based care** by surfacing cost inefficiencies

### Accessibility Impact

- **Audio narration** makes billing analysis accessible to visually impaired users
- **Plain language explanations** help users with limited health literacy
- **Character-driven UX** reduces intimidation factor of medical billing
- **Multi-modal guidance** (audio + visual) improves comprehension

By focusing on **administrative clarity** rather than clinical judgment, the system complements existing healthcare tools while addressing a **persistent and underserved pain point**.

---

## Key Features Implemented

### User Experience

✅ **Interactive Splash Screen** with dual-voice narration  
✅ **9-Step Guided Tour** with audio narration  
✅ **Character Personalities** (Billy & Billie)  
✅ **Responsive Design** for mobile and desktop  
✅ **Accessibility Features** (ARIA, screen readers, keyboard nav)  

### Document Analysis

✅ **Multi-Document Support** (bills, EOBs, receipts, FSA statements)  
✅ **CPT/CDT Code Recognition** for procedures and dental work  
✅ **Duplicate Detection** across multiple documents  
✅ **Coverage Validation** for preventive services  
✅ **FSA Eligibility Checking** against IRS guidelines  

### AI & Models

✅ **MedGemma Integration** (primary medical analysis)  
✅ **OpenAI/Gemini Fallback** (summarization only)  
✅ **Neural TTS** for audio narration (OpenAI tts-1)  
✅ **Structured Extraction** with JSON schemas  
✅ **Provider Registry** for model flexibility  

### Data Management

✅ **Profile Editor** for insurance and provider info  
✅ **Data Importer** (Plaid-inspired wizard)  
✅ **Local Storage** (no cloud databases)  
✅ **Privacy-First** architecture  

### Developer Tools

✅ **RESTful API** for programmatic access  
✅ **JSON Ingestion** pipeline  
✅ **Comprehensive Documentation** (25+ docs files)  
✅ **Testing Suite** with pytest  
✅ **CI/CD Ready** with GitHub Actions  

### Production Deployment

✅ **Streamlit Cloud** deployment  
✅ **Pre-Generated Audio Assets** (~1 MB total)  
✅ **Smart Caching** (no runtime TTS)  
✅ **Graceful Fallbacks** (works without audio)  
✅ **Cost-Effective** (~$0.46 one-time audio generation)  

---

## Technical Metrics

| Metric | Value |
|--------|-------|
| **Lines of Code** | ~10,000+ (Python) |
| **Documentation Files** | 25+ markdown files |
| **Audio Assets** | 12 files (~1 MB total) |
| **Tour Steps** | 9 interactive steps |
| **Supported Document Types** | 5+ (bills, EOBs, receipts, FSA, dental) |
| **AI Models Supported** | 4 (MedGemma, OpenAI, Gemini, Local) |
| **Test Coverage** | Comprehensive pytest suite |
| **Deployment Platforms** | Streamlit Cloud, Heroku, Docker |

---

## Alignment with HAI-DEF Principles

medBillDozer follows **Health AI Developer Foundations** best practices:

### 1. Separation of Responsibilities (Safety by Design)

- **Extraction** → Identify facts without interpretation
- **Normalization** → Convert to structured, inspectable data
- **Analysis** → MedGemma reasoning over known facts
- **Presentation** → Clear explanations, defer decisions to user

### 2. Explainability Over Automation

Does **NOT** attempt to:
- ❌ Modify claims automatically
- ❌ Submit appeals on behalf of users
- ❌ Make coverage determinations
- ❌ Provide medical or legal advice

Instead, it:
- ✅ Flags _potential_ issues with evidence
- ✅ Shows reasoning for each finding
- ✅ Explains why something may be problematic
- ✅ Recommends next steps for human action

### 3. Human-in-the-Loop by Default

All outputs require human review:
- Users provide documents manually
- System explains findings, doesn't auto-correct
- Users decide whether and how to act
- No "auto-fix" behavior

### 4. Privacy & Security First

- No PHI storage or databases
- Stateless API design
- Compatible with offline deployment
- HIPAA-compliant architecture possible

---

## Future Roadmap

### Near-Term Enhancements

- [ ] Multi-language support (Spanish, Chinese)
- [ ] Voice customization (choose Billy/Billie/neutral)
- [ ] Audio playback controls (skip, replay, speed)
- [ ] Mobile app (React Native wrapper)
- [ ] Browser extension for portal integration

### Long-Term Vision

- [ ] Direct integrations with major insurers
- [ ] Provider billing system plugins
- [ ] Employer benefit portal widgets
- [ ] Analytics dashboard for billing trends
- [ ] Community-sourced billing code pricing database

---

## Demonstration & Deployment

**Live Demo**: [medBillDozer on Streamlit Cloud]  
**GitHub Repository**: [boobootoo2/medbilldozer]  
**Documentation**: 25+ comprehensive markdown guides  
**Video Demo**: Submitted to MedGemma Impact Challenge  

---

## Conclusion

medBillDozer demonstrates that **healthcare-aligned AI** (MedGemma) can be deployed in a **safe, explainable, and user-friendly** manner to address real patient pain points.

By combining:
- 🏥 **Healthcare-specific AI** (MedGemma)
- 🎭 **Character-driven UX** (Billy & Billie)
- 🎵 **Audio accessibility** (Neural TTS)
- 🔒 **Privacy-first architecture** (no PHI storage)
- 📋 **Administrative focus** (not clinical)

...the system creates a **production-ready prototype** that could help millions of patients better understand and challenge medical billing errors.

The project showcases **end-to-end healthcare AI application development** from model integration to accessible UX to production deployment — all while adhering to HAI-DEF principles and real-world deployment constraints.

---

**Total Development**: Solo project by John Shultz  
**Technology Stack**: Python, Streamlit, MedGemma, OpenAI TTS, GitHub Actions  
**Status**: Production-deployed and demo-ready  
**Impact**: Accessible billing analysis for all patients  
