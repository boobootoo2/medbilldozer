# medBillDozer: AI-Powered Medical Bill Error Detection

**Empowering patients to detect medical billing errors with healthcare-aligned AI**

**Team**: John Shultz | Healthcare AI Systems Engineer

## Problem & Impact

**The Crisis**: 49-80% of medical bills contain errors averaging $1,300, contributing to ~550,000 annual medical-related bankruptcies.

**The Gap**: Patients lack tools to detect CPT/CDT coding errors, duplicate charges, and clinically inappropriate procedures without expert knowledge.

**Impact**: At 10% adoption, medBillDozer could help 55,000 families annually, saving $71.5M in billing errors.

## Solution: MedGemma Ensemble

**Why MedGemma**: Healthcare-aligned foundation model (`google/medgemma-4b-it`) with medical domain expertise, CPT/CDT code understanding, clinical reasoning for gender/age mismatches, and 4B parameter size enabling edge deployment.

**Architecture**: Four-phase pipeline combining MedGemma analysis → deterministic canonicalization → optional OpenAI semantic mapping → heuristic safety nets.

**Performance**: Ensemble achieves **61.9% recall** (highest), **46.9% F1**, and **59.21% savings capture rate** — detecting $26,130 in billing errors. On clinical reasoning cases, achieves **63.1% Domain Detection Rate** and **0.523 HES** (Healthcare Effectiveness Score). Superior recall minimizes missed errors.

## Technical Implementation

**Stack**: Streamlit frontend → OrchestratorAgent → MedGemmaEnsembleProvider (with GPT-4o/Gemini fallbacks) → Session-only storage.

**Configuration**: Conservative prompting with structured JSON output, three-tier canonicalization (deterministic → semantic → heuristic), and CPT/CDT code extraction.

**Deployment**: Currently cloud-based (Streamlit). Roadmap includes edge deployment with quantized GGUF models on M1+ Macs, Android tablets, and Raspberry Pi for 100% offline, HIPAA-compliant processing.

**Workflow**: Upload bill → automated issue detection → confidence-scored findings → exportable reports → insurance dispute support.

## Resources & Execution

**Code**: [github.com/boobootoo2/medbilldozer](https://github.com/boobootoo2/medbilldozer) (MIT License) — Modular architecture with comprehensive benchmarks, pytest coverage, and production monitoring dashboard. 12 benchmark runs across 4 models detecting $86,962.50 in test savings.

**Competitive Advantage**: Only patient-facing, open-source solution using healthcare-aligned foundation model with privacy-first architecture and edge deployment roadmap.

**HAI-DEF Alignment**: ✅ Adaptable | ✅ Privacy-focused | ✅ Offline-capable | ✅ Open source | ✅ Patient-empowering

**Roadmap**: Q2 2026 (HIPAA infrastructure, <3s latency) → Q2-Q3 2026 (clinical validation, 1,000+ patients, >60% F1) → Q3-Q4 2026 (mobile apps, 10,000+ users, $10M+ detected errors) → 2027+ (international expansion, enterprise platform)

---

## References

1. [Medical bill error statistics](https://orbdoc.com/blog/medical-bill-errors-80-percent-problem/)
2. [Hospital bill errors (ABC News)](https://abcnews.go.com/Health/hospital-bill-errors-cost/story?id=11819214)
3. [Medical bankruptcy data](https://www.ilr.cornell.edu/scheinman-institute/blog/john-august-healthcare/healthcare-insights-how-medical-debt-crushing-100-million-americans)
4. [MedGemma documentation](https://ai.google.dev/gemma/docs/medgemma)
5. [GitHub repository](https://github.com/boobootoo2/medbilldozer)
