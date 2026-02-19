# MedBillDozer: AI-Powered Medical Billing Error Detection

### Project Name
**MedBillDozer** - Intelligent Medical Billing Audit Platform

### Your Team
**John Shultz** - Project Lead & Full-Stack Engineer with life sciences academic experience, focusing on AI/ML integration, system architecture, FastAPI backend, React frontend, and Google Cloud deployment.

### Problem Statement

Medical billing errors affect **80% of medical bills**, costing American consumers an estimated **$25+ billion annually** (Medical Billing Advocates of America). For comprehensive analysis, see our [detailed problem domain documentation](https://github.com/boobootoo2/medbilldozer/wiki).

**Key Pain Points:**
- **Complexity**: Medical bills contain cryptic codes (CPT/CDT) and confusing terminology that patients cannot understand
- **Cost Barriers**: Professional billing advocates charge 25-35% of recovered amounts, making them inaccessible to average consumers
- **Time-Intensive**: Manual review and appeals processes are intimidating and time-consuming
- **Lack of Transparency**: Healthcare providers and insurers benefit from complexity, creating information asymmetry
- **Clinical Inconsistencies**: Billed treatments may not align with diagnoses, clinical images, or medical necessity

**Impact Potential:**
- **$25B+ Total Addressable Market** - Annual billing error cost to US consumers
- **320M+ Potential Users** - Americans with employer, Medicare, or Medicaid insurance
- **40-60% Error Recovery Rate** - Based on professional advocate success rates
- **Healthcare Cost Reduction** - System-wide savings through error prevention and transparency

### Overall Solution

MedBillDozer leverages **Google's MedGemma** (medical domain-specific AI) as the foundation for multi-modal billing error detection. Our **MedGemma-Ensemble** approach combines:

**1. Text-Based Analysis** (Bills, EOBs, Claims)
- **Primary Engine**: MedGemma-4B-IT for medical terminology expertise
- **Ensemble Validation**: Cross-validation with GPT-4o-mini for bias reduction
- **Deterministic Rules**: CPT/CDT code validation, duplicate charge detection, pricing benchmarks

**2. Clinical Image Analysis** (X-rays, Histopathology, MRI, Ultrasound)
- **MedGemma Vision Integration**: Validates billed procedures align with clinical evidence
- **Multi-Modal Reasoning**: Detects when charged treatments are inconsistent with diagnoses or imaging findings
- **Ensemble Validation**: Cross-model validation approach designed to reduce hallucination risk through consensus

**Performance Results:**

![Detection Performance by Modality](https://github.com/boobootoo2/medbilldozer/blob/main/images/detection-by-modality.png)
Our current benchmarks show **MedGemma-Ensemble achieves 78% detection rate** with **40% F1 score** (75% recall, 30% precision) across 61 test patients. While these early results outperform GPT-4o in detection rate (29% detection), there is significant room for improvement. **Our target is 90-94% accuracy** through expanded training data and model refinement. See our [interactive data flow diagram](https://boobootoo2.github.io/medbilldozer/data_flow_diagram.html) for technical architecture.

**Key Differentiators:**
- **Domain-Specific AI**: Purpose-built medical models vs. general-purpose LLMs
- **Privacy-First**: Local processing option, no PHI sharing required
- **Multi-Document Analysis**: Cross-references bills, EOBs, clinical images, and claims
- **Plain-Language Explanations**: Converts medical jargon into actionable insights

### Technical Details

#### Live Demo
🎯 **Try MedBillDozer Now**: [https://medbilldozer.vercel.app/](https://medbilldozer.vercel.app/)
🔐 **Invite Code**: `2026MEDGEMMA`

🧪 **Prototype & AI Agent Assistant & MedBillDozer Challenge Simulator**: [https://medbilldozer.streamlit.app/](https://medbilldozer.streamlit.app/)
🔐 **Passcode**: `2026MEDGEMMA`
- Guided tour of medical billing error detection
- Benchmark visualizations and performance metrics
- MedBillDozer Challenge Game (interactive learning)

**Demo Features:**
- Upload medical bills, dental bills, pharmacy receipts, or insurance EOBs
- Real-time analysis using MedGemma-Ensemble
- Interactive error breakdown with savings estimates
- Clinical image validation (X-ray, MRI, ultrasound compatibility)

#### Architecture

**Frontend**: React + Vite (Vercel deployment)
**Backend**: FastAPI + Google Cloud Run (auto-scaling, serverless)
**AI Pipeline**: MedGemma-Ensemble + GPT-4o-mini validation
**Storage**: Google Cloud Storage (documents) + Supabase PostgreSQL (metadata, audit logs)
**Authentication**: Firebase Auth with OAuth 2.0 (Google, GitHub)

**Production System Metrics:**
- **Response Time**: <2 seconds for single-document analysis
- **Throughput**: 10 concurrent requests/instance with auto-scaling to 10 instances
- **Uptime**: 99.5% (Google Cloud Run SLA)
- **Security**: HTTPS, JWT authentication, environment-based secrets management

#### Development Timeline

**Historical Progress:**
| Version | Date | Status | Milestone |
|---------|------|--------|-----------|
| v0.1 | Feb 13, 2026 | ✅ Released | Initial proof of concept - Streamlit prototype |
| v0.2 | Feb 15, 2026 | ✅ Released | Clinical imaging dataset & MedGemma benchmarks |
| v0.3 | Feb 17, 2026 | ✅ Released | Production deployment - FastAPI backend, React frontend |

**Roadmap:**
| Phase | Timeline | Objective | Funding Gate |
|-------|----------|-----------|--------------|
| **v0.4** | Mar 2026 | Post-investor feedback iteration | Pre-Seed/Angel ($500K-$1.5M) |
| **v0.5-v0.6** | Jun-Jul 2026 | HIPAA compliance, PHI handling, audit logging | Series A ($3M-$8M) |
| **v1.0** | Sep 2026 | Public beta launch with 1,000 pilot users | Revenue-driven growth |

Full timeline with fundraising gates: [RELEASE_TIMELINE.md](RELEASE_TIMELINE.md)

#### Business Model

**Revenue Streams:**
1. **B2C (Direct-to-Consumer)**: Freemium model - $9.99/month subscription for unlimited analyses
2. **B2B (Healthcare Organizations)**: Enterprise SaaS - $50K-$500K annual contracts for provider billing quality assurance
3. **B2B2C (Insurance Partnerships)**: White-label API - $1-$3 per analysis as member benefit

**Market Validation:**
- **TAM**: $25B+ annual billing error costs
- **Competitive Landscape**: No direct competitors offering medical AI + clinical image validation
- **GTM Strategy**: SEO content marketing, Reddit/healthcare forums, insurance partnership pilots

Full business plan: [BUSINESS_PLAN.md](BUSINESS_PLAN.md)

#### Data Ingestion Strategy

**Current State**: Manual PDF/image upload (v0.3)

**Target State** (v0.5-v1.0):
- **FHIR API Integration**: Direct pull from EHR systems (Epic, Cerner)
- **Insurance Portals**: Automated EOB retrieval via HL7 protocols
- **Dental Verification Services**: Real-time eligibility checks (Change Healthcare API)
- **Pharmacy Networks**: NDC-based prescription verification

**Expected Improvements:**
- **Onboarding Time**: 15+ minutes → <2 minutes (87% reduction)
- **Data Accuracy**: 70% (manual entry) → 95%+ (API-sourced)
- **User Retention**: 40% improvement through reduced friction

**Privacy & Compliance:**
- User-controlled data sharing with OAuth 2.0 consent flows
- Zero-knowledge architecture option (local processing)
- HIPAA-compliant infrastructure (GCP HIPAA-eligible services)

Full data strategy: [STREAMLINED_INTAKE_PLAN.md](STREAMLINED_INTAKE_PLAN.md)

#### Technology Stack

**AI/ML:**
- MedGemma-4B-IT (Vertex AI Hosted)
- GPT-4o-mini (OpenAI API for ensemble validation)
- Google Vision API (clinical image analysis)
- Custom deterministic rules engine (20,000+ LOC)

**Backend:**
- FastAPI (async Python web framework)
- Google Cloud Run (containerized serverless)
- Supabase PostgreSQL (with Row Level Security)
- Google Cloud Storage (HIPAA-eligible bucket)

**Frontend:**
- React 18 + TypeScript + Vite (production application)
- Streamlit (AI agent assistant & MedBillDozer Challenge simulator)
- TailwindCSS for responsive design
- Zustand for state management
- Firebase Auth SDK

**DevOps:**
- GitHub Actions (CI/CD, automated testing, security scans)
- Docker (multi-stage builds for Cloud Run)
- Google Secret Manager (API keys, credentials)
- Cloud Logging & Monitoring

**Code Quality:**
- 20,000+ lines of production Python code
- 95%+ test coverage on core modules
- Automated CodeQL security scanning
- Benchmark suite (clinical validation accuracy)

**Development Goals & Documentation:**
- **Current Performance**: 78% detection rate, 40% F1 score (based on 61 test patients)
- **Target Accuracy Goal**: 90-94% true positive detection with reduced false positives
- **Path to Target**: Expanded training data, model refinement, and ensemble optimization
- **Referenced Planning Documents**:
  - [Regulatory Affairs Compliance Strategy](REGULATORY_AFFAIRS_COMPLIANCE_STRATEGY.md)
  - [Release Timeline](RELEASE_TIMELINE.md)
  - [Business Plan](BUSINESS_PLAN.md)
  - [Streamlined Intake Plan](STREAMLINED_INTAKE_PLAN.md)

#### Open Source & Reproducibility

**Repository**: [github.com/boobootoo2/medbilldozer](https://github.com/boobootoo2/medbilldozer)
**License**: MIT (open to community contributions)
**Benchmarks**: Clinical validation dataset published at `/benchmarks/`
**Documentation**: Full API docs at `/docs/` + interactive architecture diagram

**Community Impact:**
- Transparent medical billing error detection methodology
- Open benchmark datasets for MedGemma research community
- Reusable components for healthcare AI applications

---

### Conclusion

MedBillDozer demonstrates effective use of **MedGemma as a domain-specific foundation** for real-world healthcare financial applications. By combining medical AI expertise with ensemble validation and clinical image analysis, we are building toward high-accuracy detection while maintaining patient privacy and accessibility. Current proof-of-concept shows promising results with clear pathways to production-grade performance.

**Key Achievements:**
- ✅ Production deployment with FastAPI + React frontend
- ✅ MedGemma-Ensemble proof-of-concept (78% detection rate, targeting 90-94%)
- ✅ Multi-modal analysis (text + clinical images)
- ✅ HIPAA-ready architecture on Google Cloud Platform
- ✅ Open-source benchmarks advancing medical AI research
- 🎯 **In Progress**: Expanding training data to achieve 90-94% accuracy target

**Try It Now**: [medbilldozer.vercel.app](https://medbilldozer.vercel.app/) | **Invite Code**: `2026MEDGEMMA`


