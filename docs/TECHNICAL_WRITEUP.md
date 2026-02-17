# medBillDozer — A Governed Clinical Reasoning System for Medical Billing Error Detection
**John Shultz**

---

## Live Demo and Resources

- **Demo:** <https://medbilldozer.streamlit.app/>
- **Monitoring Dashboard:** <https://medbilldozer-benchmarks.streamlit.app/>
- **Passcode:** 2026MEDGEMMA
- **Source Code:** <https://github.com/boobootoo2/medbilldozer>
- **Documentation:** [Complete Project Documentation](https://github.com/boobootoo2/medbilldozer/tree/main/docs)

The demonstration uses synthetic and redacted data. It illustrates structured issue detection, confidence scoring, model monitoring, and exportable summaries. No user data is stored and the system is not presented as a HIPAA-compliant production deployment.

> **Quick Start:** [Installation and Deployment Guide](https://github.com/boobootoo2/medbilldozer/blob/main/QUICK_START.md)

---

## Problem Statement

Medical billing errors are widespread and difficult for patients to independently detect. Industry analyses estimate that **49–80% of medical bills contain at least one error**¹. Large hospital bills average approximately **$1,300 in errors**². Medical issues contribute to **66.5% of personal bankruptcies** in the United States³.

Bills contain CPT, CDT, and NDC codes that require domain knowledge to interpret. Patients must evaluate duplicate procedure charges, age- or gender-inappropriate services, clinically inconsistent procedures, drug–disease contraindications, and incorrect coding. This requires cross-document validation, demographic reasoning, and conservative clinical interpretation. General-purpose LLMs parse text well but are not optimized for healthcare reasoning.

> **Extended Analysis:** [Medical Billing Error Impact Report](https://github.com/boobootoo2/medbilldozer/blob/main/docs/MEDICAL_BILLING_ERROR_IMPACT.md) — Comprehensive statistics on financial impact, bankruptcy trends, and appeals data.

---

## Healthcare-Aligned Solution

medBillDozer is built on **MedGemma (google/medgemma-4b-it)**, part of Google's Health AI Developer Foundations (HAI-DEF). Generic LLMs parse language. **MedGemma reasons clinically.**

MedGemma provides training on biomedical and clinical corpora, structured understanding of medical coding systems, demographic constraint awareness, evidence-grounded outputs, and open weights for controlled deployment. Example detections include pregnancy procedures billed to male patients, pediatric colonoscopy billing, age-inconsistent mammograms, surgical history contradictions, and diagnosis–procedure mismatches.

> **Technical Deep Dive:** [Healthcare-Aligned Solution Guide](https://github.com/boobootoo2/medbilldozer/blob/main/docs/HEALTHCARE_ALIGNED_SOLUTION.md) — Architecture, deployment considerations, and detailed detection examples.

---

## System Architecture and Governance

medBillDozer integrates MedGemma within a governed pipeline:

1. Clinical reasoning via MedGemma
2. Deterministic canonicalization of issue types
3. Heuristic validation safeguards
4. Structured output formatting with instrumentation

The reasoning layer is model-driven; output control is deterministic and auditable. Model outputs are normalized into canonical issue categories to enable reproducible benchmarking and regression tracking.

---

## Evaluation Framework

Performance is measured against **structured synthetic benchmarks with annotated ground truth** across two tiers:

**Overall Metrics:** Measure all billing errors (technical + clinical)
- Precision_all = TP_all / (TP_all + FP_all)
- Recall_all = TP_all / (TP_all + FN_all)
- F1_all = 2 × (Precision_all × Recall_all) / (Precision_all + Recall_all)

**Clinical Subset Metrics:** Isolate healthcare-specific reasoning
- Detection_clinical = TP_clinical / (TP_clinical + FN_clinical)
- HES (Healthcare Effectiveness Score) = F1_clinical

The **Healthcare Effectiveness Score (HES)** isolates domain reasoning performance from general extraction accuracy, proving that healthcare-aligned models materially improve clinical pattern recognition.

> **Benchmark Methodology:** [Benchmarks Documentation](https://github.com/boobootoo2/medbilldozer/tree/main/benchmarks) — Dataset composition, ground truth annotation ([Schema](https://github.com/boobootoo2/medbilldozer/blob/main/benchmarks/GROUND_TRUTH_SCHEMA.md), [Guide](https://github.com/boobootoo2/medbilldozer/blob/main/benchmarks/ANNOTATION_GUIDE.md)), and continuous improvement processes.

---

## Model Performance

| Model | Precision | Recall | F1 | Domain Detection | HES |
|-------|-----------|--------|-----|------------------|-----|
| **MedGemma Ensemble** | 44.6% | 61.9% | **0.469** | **63.1%** | **0.523** |
| GPT-4o | 46% | 42% | 0.424 | 41.0% | 0.318 |
| MedGemma 4B-IT | 48% | 31% | 0.360 | 28.7% | 0.242 |

The MedGemma ensemble achieves the highest recall and strongest domain-specific detection (77 of 122 clinical inconsistencies detected). This suggests healthcare-aligned reasoning materially improves detection of clinically inappropriate billing patterns.

> **Model Comparison:** [Benchmarking Guide](https://github.com/boobootoo2/medbilldozer/blob/main/benchmarks/MODEL_COMPARISON.md) — Available models, methodology, cost comparison, and comparative evaluation.

---

## Category-Level Clinical Analysis

Aggregate F1 masks variation across error types. The figure below presents detection rates by billing error category.

![Detection rates by error category](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F6561712%2Ff299f20408d2fae93e029e41f40b9a57%2Fnewplot%20(3).png?generation=1770956700894373&alt=media)

**Figure:** Detection rate (%) by billing error category across models. Performance varies substantially by domain; the MedGemma ensemble improves diagnosis–procedure mismatch, surgical history contradiction, and health-history inconsistency detection, while all models struggle with allergy violations and upcoding.

**Key Observations:**
- Strong ensemble gains in diagnosis–procedure mismatch (100%) and procedure–history inconsistencies
- Robust detection of surgical history contradictions
- Persistent difficulty across models for allergy violations and upcoding
- Improved demographic reasoning in age- and gender-mismatch categories

This granular analysis highlights both strengths and limitations and supports the use of ensemble governance.

---

## Monitoring and Regression Control

The Production Stability Dashboard tracks versioned model performance, baseline regression detection, and F1 stability across benchmark runs.

**Current snapshot:**
- F1_all = 0.469
- No regression detected
- Multiple tracked model versions with rollback support

This ensures model evolution remains auditable and controlled.

> **Evaluation Framework:** [Production Stability Metrics](https://github.com/boobootoo2/medbilldozer/blob/main/docs/PRODUCTION_STABILITY_METRICS.md) — Comprehensive details on evaluation metrics, confidence scoring, continuous monitoring processes, and improvement roadmaps.

---

## Multimodal Extension Roadmap

MedGemma 1.5 introduces high-dimensional imaging support (CT, MRI, histopathology, advanced 2D interpretation). medBillDozer is architected for future multimodal validation including fracture casting validation against radiographic evidence, CT justification review based on imaging findings, and left/right anatomical consistency verification.

The current system focuses on governed text-based reasoning while maintaining compatibility with imaging-based clinical validation.

> **Multimodal Capabilities:** [Clinical Images Documentation](https://github.com/boobootoo2/medbilldozer/tree/main/benchmarks/clinical_images) — Image analysis, dataset integration, and MedGemma Vision implementation.

---

## Responsible AI Design

The system enforces evidence-grounded findings only, conservative reasoning policies, deterministic validation for high-risk categories, and confidence scoring on all outputs. All demonstrations use synthetic or redacted data and store no user information.

---

## Conclusion

medBillDozer operationalizes a healthcare-aligned open-weight model into a governed, monitored system for detecting clinically inconsistent billing patterns. By isolating domain reasoning performance (Domain Detection: 63.1%, HES: 0.523), performing category-level analysis, and integrating regression safeguards, the project demonstrates transparent and responsible deployment of healthcare AI. The architecture supports future multimodal expansion while maintaining evaluation rigor and governance controls.

---

## References

1. OrbDoc Industry Analysis, <https://orbdoc.com/blog>
2. ABC News Medical Billing Analysis, <https://abcnews.go.com/Health/hospital-bill-errors-cost/story?id=11819214>
3. Himmelstein et al., *American Journal of Public Health*, 2019

---

## Additional Resources

**Project Documentation:** [Documentation Index](https://github.com/boobootoo2/medbilldozer/tree/main/docs) | [Quick Start](https://github.com/boobootoo2/medbilldozer/blob/main/QUICK_START.md) | [Deployment Guide](https://github.com/boobootoo2/medbilldozer/blob/main/docs/DEPLOYMENT_GUIDE.md) | [User Guide](https://github.com/boobootoo2/medbilldozer/blob/main/docs/USER_GUIDE.md) | [API Docs](https://github.com/boobootoo2/medbilldozer/blob/main/docs/API.md) | [Interactive Challenge](https://github.com/boobootoo2/medbilldozer/blob/main/docs/CHALLENGE_AS_CONTEXTUAL_TOOL.md)

**Technical Deep Dives:** [Healthcare-Aligned Solution](https://github.com/boobootoo2/medbilldozer/blob/main/docs/HEALTHCARE_ALIGNED_SOLUTION.md) | [Medical Billing Error Impact](https://github.com/boobootoo2/medbilldozer/blob/main/docs/MEDICAL_BILLING_ERROR_IMPACT.md) | [Production Stability Metrics](https://github.com/boobootoo2/medbilldozer/blob/main/docs/PRODUCTION_STABILITY_METRICS.md) | [Model Comparison](https://github.com/boobootoo2/medbilldozer/blob/main/benchmarks/MODEL_COMPARISON.md)

**Benchmark System:** [Benchmarks Overview](https://github.com/boobootoo2/medbilldozer/tree/main/benchmarks) | [Ground Truth Schema](https://github.com/boobootoo2/medbilldozer/blob/main/benchmarks/GROUND_TRUTH_SCHEMA.md) | [Annotation Guide](https://github.com/boobootoo2/medbilldozer/blob/main/benchmarks/ANNOTATION_GUIDE.md) | [Clinical Images](https://github.com/boobootoo2/medbilldozer/tree/main/benchmarks/clinical_images)

**Source Code:** [Main Repository](https://github.com/boobootoo2/medbilldozer) | [Examples](https://github.com/boobootoo2/medbilldozer/tree/main/examples) | [Scripts](https://github.com/boobootoo2/medbilldozer/tree/main/scripts)
