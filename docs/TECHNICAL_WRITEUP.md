# medBillDozer — A Governed Clinical Reasoning System for Medical Billing Error Detection  
**John Shultz**

---

## Live Demo and Resources

**Demo:** https://medbilldozer.streamlit.app/  
**Monitoring Dashboard:** https://medbilldozer.streamlit.app/production_stability  
**Passcode:** XXXXXXX  
**Source Code:** https://github.com/boobootoo2/medbilldozer  

The demonstration uses synthetic and redacted data. It illustrates structured issue detection, confidence scoring, model monitoring, and exportable summaries. No user data is stored and the system is not presented as a HIPAA-compliant production deployment.

---

## Problem Statement

Medical billing errors are widespread and difficult for patients to independently detect. Industry analyses estimate that **49–80% of medical bills contain at least one error**¹. Large hospital bills average approximately **$1,300 in errors**². Medical issues contribute to **66.5% of personal bankruptcies** in the United States³.

Bills contain CPT, CDT, and NDC codes that require domain knowledge to interpret. Patients must evaluate:

- Duplicate procedure charges  
- Age- or gender-inappropriate services  
- Clinically inconsistent procedures  
- Drug–disease contraindications  
- Incorrect coding  

This requires cross-document validation, demographic reasoning, and conservative clinical interpretation. General-purpose LLMs parse text well but are not optimized for healthcare reasoning.

---

## Healthcare-Aligned Solution

medBillDozer is built on **MedGemma (google/medgemma-4b-it)**, part of Google’s Health AI Developer Foundations (HAI-DEF).

Generic LLMs parse language. **MedGemma reasons clinically.**

MedGemma provides:

- Training on biomedical and clinical corpora  
- Structured understanding of medical coding systems  
- Demographic constraint awareness  
- Evidence-grounded outputs  
- Open weights for controlled deployment  

Example detections include pregnancy procedures billed to male patients, pediatric colonoscopy billing, age-inconsistent mammograms, surgical history contradictions, and diagnosis–procedure mismatches.

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

Performance is measured against structured synthetic benchmarks with annotated ground truth.

**Overall Metrics**

Precision_all = TP_all / (TP_all + FP_all)  
Recall_all = TP_all / (TP_all + FN_all)  
F1_all = 2 × (Precision_all × Recall_all) / (Precision_all + Recall_all)

**Clinical Subset Metrics**

Detection_clinical = TP_clinical / (TP_clinical + FN_clinical)  
HES = F1_clinical  

The **Healthcare Effectiveness Score (HES)** isolates domain reasoning performance from general extraction accuracy.

---

## Model Performance

| Model | Precision | Recall | F1 | Domain Detection | HES |
|-------|-----------|--------|-----|------------------|-----|
| **MedGemma Ensemble** | 44.6% | 61.9% | 0.469 | **63.1%** | **0.523** |
| GPT-4o | 46% | 42% | 0.424 | 41.0% | 0.318 |
| MedGemma 4B-IT | 48% | 31% | 0.360 | 28.7% | 0.242 |

The MedGemma ensemble achieves the highest recall and strongest domain-specific detection (77 of 122 clinical inconsistencies detected). This suggests healthcare-aligned reasoning materially improves detection of clinically inappropriate billing patterns.

---

## Category-Level Clinical Analysis

Aggregate F1 masks variation across error types. The figure below presents detection rates by billing error category.

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F6561712%2Ff299f20408d2fae93e029e41f40b9a57%2Fnewplot%20(3).png?generation=1770956700894373&alt=media)
**Figure:** Detection rate (%) by billing error category across models. Performance varies substantially by domain; the MedGemma ensemble improves diagnosis–procedure mismatch, surgical history contradiction, and health-history inconsistency detection, while all models struggle with allergy violations and upcoding.

### Key Observations

- Strong ensemble gains in diagnosis–procedure mismatch (100%) and procedure–history inconsistencies  
- Robust detection of surgical history contradictions  
- Persistent difficulty across models for allergy violations and upcoding  
- Improved demographic reasoning in age- and gender-mismatch categories  

This granular analysis highlights both strengths and limitations and supports the use of ensemble governance.

---

## Monitoring and Regression Control

The Production Stability Dashboard tracks:

- Versioned model performance  
- Baseline regression detection  
- F1 stability across benchmark runs  

**Current snapshot:**

- F1_all = 0.469  
- No regression detected  
- Multiple tracked model versions with rollback support  

This ensures model evolution remains auditable and controlled.

---

## Multimodal Extension Roadmap

MedGemma 1.5 introduces high-dimensional imaging support (CT, MRI, histopathology, advanced 2D interpretation). medBillDozer is architected for future multimodal validation.

Potential extensions include:

- Fracture casting validation against radiographic evidence  
- CT justification review based on imaging findings  
- Left/right anatomical consistency verification  

The current system focuses on governed text-based reasoning while maintaining compatibility with imaging-based clinical validation.

---

## Responsible AI Design

The system enforces:

- Evidence-grounded findings only  
- Conservative reasoning policies  
- Deterministic validation for high-risk categories  
- Confidence scoring on all outputs  

All demonstrations use synthetic or redacted data and store no user information.

---

## Conclusion

medBillDozer operationalizes a healthcare-aligned open-weight model into a governed, monitored system for detecting clinically inconsistent billing patterns. By isolating domain reasoning performance (Domain Detection: 63.1%, HES: 0.523), performing category-level analysis, and integrating regression safeguards, the project demonstrates transparent and responsible deployment of healthcare AI. The architecture supports future multimodal expansion while maintaining evaluation rigor and governance controls.

---

### References

1. https://orbdoc.com/blog
2. https://abcnews.go.com/Health/hospital-bill-errors-cost/story?id=11819214  
3. Himmelstein et al., *American Journal of Public Health*, 2019.
