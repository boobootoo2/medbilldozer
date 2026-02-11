# medBillDozer — A Governed Clinical Reasoning System for Medical Billing Error Detection

## Live Demo & Resources

**Demonstration Application:**  
https://medbilldozer.streamlit.app/

**Production Stability Dashboard:**  
https://medbilldozer.streamlit.app/production_stability

**Passcode:** MEDGEMMA202

**Source Code:**  
https://github.com/boobootoo2/medbilldozer

The demonstration environment uses synthetic and redacted billing examples. It showcases structured issue detection, confidence scoring, monitoring instrumentation, and exportable summaries. No user data is stored. The demo is not presented as a HIPAA-compliant production system.

---

## Your Team

**John Shultz — Healthcare AI Systems Engineer**  
Architecture design, MedGemma integration, evaluation framework development, monitoring instrumentation, and full-stack implementation.

---

## Problem Statement

Medical billing errors are common and difficult for patients to independently detect. Industry estimates suggest that 49–80% of medical bills contain at least one error[^1] with an average error of approximately $1,300 on large hospital bills[^2]. Medical issues contribute to approximately 66.5% of personal bankruptcies in the United States[^3].

Medical bills contain CPT, CDT, and NDC codes requiring healthcare knowledge to interpret. Patients must evaluate:

- Duplicate procedure charges  
- Age- or gender-inappropriate services  
- Clinically inconsistent procedures  
- Drug interactions  
- Incorrect coding  

Billing validation requires cross-document demographic validation, clinical appropriateness checks, and conservative reasoning within healthcare constraints. Healthcare-aligned foundation models are well suited to this task.

---

## Overall Solution  
### Effective Use of HAI-DEF Models

medBillDozer is built around **MedGemma (google/medgemma-4b-it)** from Google’s Health AI Developer Foundations (HAI-DEF).

Generic LLMs parse text. MedGemma reasons clinically.

MedGemma provides:

- Training on clinical and biomedical text  
- Structured understanding of CPT/CDT/NDC codes  
- Awareness of age and gender constraints  
- Conservative, evidence-grounded outputs  
- Open weights enabling developer-controlled integration  

Example reasoning tasks include detecting pregnancy procedures billed to male patients, pediatric colonoscopy billing, age-inconsistent mammograms, and duplicate CPT codes.

---

## System Architecture

medBillDozer integrates MedGemma into a structured workflow:

1. Primary clinical reasoning via MedGemma  
2. Deterministic canonicalization of issue types  
3. Heuristic validation safeguards  
4. Structured output formatting and monitoring instrumentation  

MedGemma performs the core medical reasoning step. Deterministic safeguards ensure consistent and controlled outputs.

---

## Model Usage Disclosure

During development, benchmarking, and validation, the following large language models were used:

- **Google MedGemma-4B-IT** — primary healthcare reasoning engine and ensemble foundation  
- **Google Gemini 1.5 Pro** — benchmark comparison baseline  
- **OpenAI GPT-4o** — benchmark comparison baseline  
- **Anthropic Claude** — prompt refinement and structured benchmark generation support  

All final system architecture, evaluation framework design, monitoring instrumentation, and ensemble governance logic were independently implemented.

The project is model-agnostic at the orchestration layer, enabling controlled benchmarking across multiple foundation models while isolating healthcare-specific reasoning performance.

---

## Evaluation Framework & Metric Definitions

The system is evaluated using structured benchmarks with annotated ground truth.

Let:

- **TP_all** = correctly detected issues across all cases  
- **FP_all** = incorrectly flagged issues  
- **FN_all** = missed issues  

### Overall Precision

`Precision_all = TP_all / (TP_all + FP_all)`

### Overall Recall

`Recall_all = TP_all / (TP_all + FN_all)`

Precision and recall measure different failure modes.

### Overall F1

`F1_all = 2 × (Precision_all × Recall_all) / (Precision_all + Recall_all)`

F1 balances over-flagging and under-detection.

---

## Model Performance

| Model                  | Precision | Recall | F1    | Domain Detection | HES   |
|------------------------|-----------|--------|-------|------------------|-------|
| **MedGemma Ensemble**  | 44.6%     | 61.9%  | 0.469 | **63.1%**        | **0.523** |
| GPT-4o                 | 46%       | 42%    | 0.424 | 41.0%            | 0.318 |
| MedGemma 4B-IT         | 48%       | 31%    | 0.360 | 28.7%            | 0.242 |

The ensemble achieves the highest recall (61.9%) and strongest performance on clinical reasoning cases.

---

## Clinical Reasoning Subset & Domain Detection

Some benchmark cases require explicit clinical reasoning:

- Gender-inappropriate procedures  
- Age-inappropriate services  
- Cross-document inconsistencies  
- Drug–disease contraindications  

Let:

- **TP_clinical**, **FP_clinical**, **FN_clinical** computed only on this subset.

### Domain Knowledge Detection Rate

`Detection_clinical = TP_clinical / (TP_clinical + FN_clinical)`

This metric measures the proportion of clinically inappropriate procedures successfully detected. It is equivalent to recall on the clinical subset.

**MedGemma Ensemble: 63.1%**  
(77 of 122 domain-specific billing errors detected.)

---

### Healthcare Effectiveness Score (HES)

`HES = F1_clinical`

Where:

- `Precision_clinical = TP_clinical / (TP_clinical + FP_clinical)`  
- `Recall_clinical = TP_clinical / (TP_clinical + FN_clinical)`  
- `F1_clinical = 2 × (Precision_clinical × Recall_clinical) / (Precision_clinical + Recall_clinical)`  

**MedGemma Ensemble HES: 0.523**

HES isolates healthcare reasoning performance from general extraction accuracy.

---

## Monitoring & Governance

The Production Stability Dashboard provides:

- Regression detection against stored baselines  
- Versioned model tracking  
- F1 stability monitoring across runs  

Current snapshot:

- `F1_all (current) = 0.469`  
- `F1_all (baseline) = 0.469`  
- No regression detected  
- Two tracked versions with rollback support  

This instrumentation ensures model evolution is auditable and controlled.

---

## Responsible & Conservative AI Design

The system enforces:

- Evidence-grounded findings only  
- No speculative insurance outcomes  
- Conservative estimation logic  
- Deterministic validation of high-risk detections  
- Confidence scoring on all findings  

The demonstration environment uses synthetic and redacted data and stores no user information.

---

## Conclusion

medBillDozer operationalizes a healthcare-aligned open-weight model into a governed, monitored system capable of detecting clinically inconsistent billing patterns.

By clearly defining evaluation metrics, isolating clinical reasoning performance (Domain Detection: 63.1%, HES: 0.523), and incorporating regression safeguards and version tracking, this project demonstrates transparent and responsible deployment of healthcare AI.

---

## Footnotes

[^1]: OrbDoc industry summary: https://orbdoc.com/blog/medical-bill-errors-80-percent-problem/  
[^2]: ABC News reporting on hospital billing errors: https://abcnews.go.com/Health/hospital-bill-errors-cost/story?id=11819214  
[^3]: Himmelstein, D. U., et al. "Medical Bankruptcy: Still Common Despite the Affordable Care Act." *American Journal of Public Health*, 2019.
