# MedBillDozer: AI-Powered Medical Billing Error Detection

## Project Overview
**MedBillDozer** is an intelligent medical billing audit platform that uses domain-specific medical AI to identify billing errors, clinical inconsistencies, and unjustified charges across medical bills, insurance EOBs, and supporting clinical evidence.

## Team
**John Shultz**  
Project Lead & Full-Stack Engineer with a life-sciences academic background, specializing in AI/ML integration, healthcare system architecture, FastAPI backends, React frontends, and Google Cloud–based deployments.

---

## Problem Statement

Medical billing errors are widespread and difficult for patients to independently detect. Industry estimates suggest that **up to 80% of medical bills contain at least one error**, costing U.S. consumers **over $25 billion annually**.

Medical bills combine opaque procedure codes, fragmented documentation, and clinical context that patients cannot realistically validate on their own. The result is a system where errors persist due to complexity rather than intent.

### Key Pain Points
- **Complexity**: CPT/CDT codes and medical terminology are inaccessible to most patients
- **Cost Barriers**: Professional billing advocates charge 25–35% of recovered savings
- **Time Burden**: Manual appeals are slow, confusing, and intimidating
- **Information Asymmetry**: Providers and insurers benefit from opaque workflows
- **Clinical Mismatch**: Billed procedures may not align with diagnoses, imaging, or medical necessity

### Impact Potential
- **$25B+ Total Addressable Market** — annual U.S. billing error costs
- **320M+ Potential Users** — insured Americans (employer, Medicare, Medicaid)
- **40–60% Recovery Rates** — based on professional advocate benchmarks
- **System-Wide Cost Reduction** — through error prevention and transparency

---

## Solution Overview

MedBillDozer uses **MedGemma**, a domain-specific medical AI model, as the foundation for **multi-modal billing error detection**. The system combines structured rules, ensemble validation, and clinical reasoning across documents and images.

### MedGemma-Ensemble Architecture

#### 1. Text-Based Analysis  
*(Bills, Claims, EOBs, Receipts)*
- **Primary Engine**: MedGemma-4B-IT for medical language and billing context
- **Ensemble Validation**: GPT-4o-mini for cross-model consistency and bias reduction
- **Deterministic Rules**:
  - CPT/CDT validation
  - Duplicate and overlapping charges
  - Pricing and utilization benchmarks

#### 2. Clinical Image Analysis  
*(X-ray, MRI, Ultrasound, Histopathology)*
- **Clinical Evidence Validation**: Confirms billed procedures align with imaging findings
- **Multi-Modal Reasoning**: Flags treatments unsupported by diagnoses or images
- **Consensus-Based Validation**: Reduces hallucinations through cross-model agreement

---

## Performance & Benchmarks

### Performance by Error Type

![Performance by Error Type](https://raw.githubusercontent.com/boobootoo2/medbilldozer/main/images/performance-by-error-type_v2.png)

This figure shows **detection performance segmented by billing error category**, illustrating how MedBillDozer performs on the types of issues that most directly impact patients and payers (e.g., duplicate charges, coding errors, medical necessity mismatches).

Across 61 synthetic and semi-structured patient scenarios, **MedGemma-Ensemble achieves a 78% overall detection rate** with an **F1 score of 40%** (75% recall, 30% precision). The results emphasize recall across high-impact error classes, aligning with real-world reconciliation workflows where missing an error is costlier than flagging one for review.

---

### Detection Performance by Modality

![Detection Performance by Modality](https://raw.githubusercontent.com/boobootoo2/medbilldozer/main/images/detection-by-modality.png)

This figure presents **detection performance across input modalities**, including text-based documents and clinical imaging.

- **X-ray & Ultrasound** show the strongest alignment between billed procedures and clinical evidence  
- **MRI** exhibits higher variance due to protocol and interpretation complexity  
- **Histopathology** shows lower recall, reflecting higher semantic density and annotation sensitivity  

Rather than averaging performance across modalities, MedBillDozer explicitly models these differences, enabling **modality-aware ensemble weighting** and targeted improvement strategies.

📊 **Full system architecture and data flow:**  
https://boobootoo2.github.io/medbilldozer/data_flow_diagram.html

---

## Key Differentiators
- **Medical-Domain AI** — purpose-built models vs. generic LLMs
- **Multi-Document Reasoning** — bills, EOBs, claims, and images cross-validated
- **Privacy-First Design** — no required PHI sharing; local processing supported
- **Plain-Language Output** — actionable explanations for non-experts

---

## Live Demos

### 🔗 Production Prototype
**URL:** https://www.medbilldozer.com/  
**Invite Code:** `2026MEDGEMMA`

- Full React + FastAPI production deployment
- Real-time MedGemma-Ensemble analysis
- End-to-end billing error detection workflow
- Designed for non-technical end users

---

### 🧪 Live Proof of Concept (POC)
**URL:** https://medbilldozer.streamlit.app/  
**Passcode:** `2026MEDGEMMA`

- Streamlit-based research and experimentation environment
- AI agent assistant for guided exploration
- Benchmark visualizations and modality performance analysis
- MedBillDozer Challenge simulator for educational and evaluation use

---

## System Architecture

**Frontend**: React + Vite (Vercel)  
**Backend**: FastAPI on Google Cloud Run  
**AI Pipeline**: MedGemma-Ensemble + GPT-4o-mini validation  
**Storage**: Google Cloud Storage + Supabase PostgreSQL  
**Authentication**: Firebase Auth (OAuth 2.0: Google, GitHub)

### Production Metrics
- **Latency**: <2 seconds per document
- **Scalability**: Auto-scaling to 10 instances
- **Uptime**: 99.5% (Cloud Run SLA)
- **Security**: HTTPS, JWT, environment-based secrets

---

## Development Timeline

| Version | Date | Milestone |
|--------|------|-----------|
| v0.1 | Feb 13, 2026 | Streamlit proof-of-concept |
| v0.2 | Feb 15, 2026 | Clinical imaging benchmarks |
| v0.3 | Feb 17, 2026 | Production FastAPI + React |

### Roadmap

| Phase | Goal | Funding |
|------|------|---------|
| v0.4 | Investor-driven iteration | Pre-Seed ($500K–$1.5M) |
| v0.5–v0.6 | HIPAA compliance & PHI handling | Series A ($3M–$8M) |
| v1.0 | Public beta (1,000 users) | Revenue growth |

---

## Business Model

### Revenue Streams
1. **B2C** — $9.99/month subscription
2. **B2B** — $50K–$500K annual enterprise contracts
3. **B2B2C** — $1–$3 per API analysis (insurance partners)

### Go-To-Market Strategy
- SEO and educational content
- Healthcare and Reddit communities
- Insurance pilot partnerships

---

## Data Ingestion Strategy

**Current**: Manual uploads (v0.3)

**Planned**
- FHIR-based EHR integration (Epic, Cerner)
- Automated insurance EOB retrieval
- Dental and pharmacy verification APIs

### Expected Gains
- Onboarding time: 15 minutes → <2 minutes
- Data accuracy: 70% → 95%+
- User retention: +40%

---

## Technology Stack

### AI / ML
- MedGemma-4B-IT (Hugging Face Inference API)
- GPT-4o-mini (ensemble validation)
- Google Vision API
- Custom deterministic rules engine (20,000+ LOC)

### Backend
- FastAPI (async Python)
- Google Cloud Run
- Supabase PostgreSQL (RLS enabled)
- Google Cloud Storage

### Frontend
- React 18 + TypeScript + Vite
- Streamlit (agent assistant & simulator)
- TailwindCSS
- Zustand

### DevOps & Quality
- GitHub Actions CI/CD
- Docker (multi-stage builds)
- CodeQL security scanning
- 95%+ test coverage

---

## Open Source & Reproducibility
- **Repository**: https://github.com/boobootoo2/medbilldozer
- **License**: MIT
- **Benchmarks**: `/benchmarks/`
- **Documentation**: `/docs/` + interactive architecture diagrams

### Community Impact
- Transparent medical billing error detection methodology
- Open benchmark datasets for medical AI research
- Reusable components for healthcare AI systems

---

## Limitations & Remediations

### 1. Precision and False Positives
**Limitation:**  
Current performance prioritizes recall over precision, which can surface false positives.

**Remediation:**  
- Modality-aware ensemble weighting  
- Rule–model arbitration  
- Per-error-category decision thresholds  

---

### 2. Limited Training and Evaluation Data
**Limitation:**  
Benchmarks rely on a limited set of synthetic and semi-structured scenarios.

**Remediation:**  
- Expansion to de-identified real-world datasets  
- Active learning focused on ensemble disagreement  
- Increased cross-institution variability  

---

### 3. Modality Imbalance
**Limitation:**  
Lower recall in MRI and histopathology.

**Remediation:**  
- Modality-specific fine-tuning  
- Increased labeled data  
- Per-modality confidence normalization  

---

### 4. Ground Truth Ambiguity
**Limitation:**  
Billing correctness is not always binary.

**Remediation:**  
- Graded error severity levels  
- Policy-aware explanations  
- Human-in-the-loop review for borderline cases  

---

### 5. Explainability
**Limitation:**  
Multi-modal reasoning can feel opaque.

**Remediation:**  
- Evidence-linked explanations  
- Confidence scores per finding  
- “Billed vs. Supported by Evidence” comparisons  

---

### 6. Privacy & Deployment
**Limitation:**  
PHI handling introduces compliance complexity.

**Remediation:**  
- Local or customer-controlled inference  
- Zero-retention defaults  
- Expanded audit logging (v0.5–v0.6)  

---

## Conclusion

MedBillDozer demonstrates how **domain-specific medical AI**, combined with ensemble validation and clinical reasoning, can meaningfully reduce healthcare billing errors. By explicitly modeling differences across billing error types and input modalities, the platform delivers both strong empirical results and a credible path toward clinical-grade accuracy.

**Current status:**
- ✅ Production deployment (React + FastAPI)
- ✅ Multi-modal AI validation (text + imaging)
- ✅ Open benchmarks and reproducible evaluation
- 🎯 Scaling toward **90–94% detection accuracy**
