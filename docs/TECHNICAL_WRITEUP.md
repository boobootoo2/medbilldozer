# medBillDozer — A Governed Clinical Reasoning System for Medical Billing Error Detection

## Live Demo & Resources

**Demonstration Application:**  
<https://medbilldozer.streamlit.app/>

**Production Stability Dashboard:**  
<https://medbilldozer.streamlit.app/production_stability>

**Access:** Passcode provided to judges in submission materials.

**Source Code:**  
<https://github.com/boobootoo2/medbilldozer>

The demonstration environment uses synthetic and redacted billing examples. It showcases structured issue detection, confidence scoring, monitoring instrumentation, and exportable summaries. No user data is stored. The demo is not presented as a HIPAA-compliant production system.

---

## Your Team

**John Shultz — Healthcare AI Systems Engineer**  
Architecture design, MedGemma integration, evaluation framework development, monitoring instrumentation, and full-stack implementation.

---

## Problem Statement

Medical billing errors are common and difficult for patients to independently detect. Industry analyses estimate that 49–80% of medical bills contain at least one error, with an average error size of approximately $1,300.

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

medBillDozer is built around **MedGemma (google/medgemma-4b-it)** from Google's Health AI Developer Foundations (HAI-DEF).

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

medBillDozer integrates MedGemma into a structured workflow consisting of:

1. Primary clinical reasoning via MedGemma  
2. Deterministic canonicalization of issue types  
3. Heuristic validation safeguards  
4. Structured output formatting and monitoring instrumentation  

MedGemma performs the core medical reasoning step. Deterministic safeguards ensure consistency and controlled outputs.

---

## Evaluation Framework & Metric Definitions

The system is evaluated using structured benchmarks with annotated ground truth. For each case, detected issues are compared against expected issues.

Let:

- **TP_all** = correctly detected issues across all cases  
- **FP_all** = incorrectly flagged issues  
- **FN_all** = missed issues  

### Overall Precision

`Precision_all = TP_all / (TP_all + FP_all)`

Precision measures the proportion of flagged issues that are correct and penalizes false positives.

### Overall Recall

`Recall_all = TP_all / (TP_all + FN_all)`

Recall measures the proportion of true issues successfully detected and penalizes false negatives.

Precision and recall measure different failure modes.

### Overall F1

`F1_all = 2 × (Precision_all × Recall_all) / (Precision_all + Recall_all)`

F1 balances over-flagging and under-detection.

---

## Model Performance

| Model                | Precision | Recall | F1    | Domain Detection | HES   |
|----------------------|-----------|--------|-------|-----------------|-------|
| **MedGemma Ensemble** | 44.6%     | 61.9%  | 0.469 | **63.1%**       | **0.523** |
| GPT-4o               | 46%       | 42%    | 0.424 | -               | -     |
| MedGemma 4B-IT       | 48%       | 31%    | 0.360 | -               | -     |

The ensemble achieves the highest recall (61.9%), which is particularly important in detection systems where missed issues reduce system usefulness. More importantly, on clinical reasoning cases specifically, it achieves **63.1% Domain Detection Rate** — successfully identifying nearly 2/3 of clinically inappropriate procedures.

---

## Clinical Reasoning Subset & HES

Some benchmark cases require explicit clinical reasoning:

- Gender-inappropriate procedures (e.g., pregnancy ultrasound billed to male patient)
- Age-inappropriate services (e.g., colonoscopy for 8-year-old)
- Cross-document inconsistencies (e.g., bilateral knee surgery after amputation)
- Drug-disease contraindications (e.g., beta-blocker for asthma patient)
- Surgical history contradictions

Let:

- **TP_clinical**, **FP_clinical**, **FN_clinical** computed only on the clinical reasoning subset (61 domain-specific cases across 17 error types).

### Domain Knowledge Detection Rate

`Detection_Rate_clinical = TP_clinical / (TP_clinical + FN_clinical)`

This measures the proportion of clinically inappropriate procedures successfully detected. It is equivalent to recall on the clinical reasoning subset.

#### Calculation Method

The Domain Detection Rate is computed as follows:

1. **Identify Domain-Specific Issues**: Each ground truth billing error is annotated with `requires_domain_knowledge: true/false` in the benchmark dataset. Domain-specific issues are those that require healthcare expertise to detect, such as:
   - Gender-inappropriate procedures (e.g., pregnancy ultrasound for male patient)
   - Age-inappropriate services (e.g., colonoscopy for 8-year-old)
   - Anatomical contradictions (e.g., bilateral knee surgery after amputation)
   - Drug-disease contraindications (e.g., beta-blocker for asthma patient)
   - Surgical history violations

2. **Count Successful Detections**: For each patient case, the system matches detected issues against expected domain-specific issues. A match occurs when the detected issue type and description substantially overlap with an expected issue.

3. **Calculate Rate**:
   ```
   Domain Detection Rate = (Detected Domain Issues) / (Total Domain Issues) × 100%
   
   Where:
   - Detected Domain Issues = Count of domain-specific issues successfully identified
   - Total Domain Issues = Count of all domain-specific issues in ground truth
   ```

4. **Average Across Patients**: The final rate is the **macro-average** (mean of per-patient recall) across all 61 patient benchmark cases. This treats each patient equally regardless of how many domain-specific issues they have.

**Current value: 63.1%**

This means MedGemma Ensemble successfully identifies 63 out of every 100 clinical billing errors on average — cases that require healthcare domain knowledge to detect. Across the benchmark set, this represents detecting 70 out of 106 domain-specific billing errors (66.0% micro-average), with the macro-average slightly lower at 63.1% due to giving equal weight to all patients.

### Healthcare Effectiveness Score (HES)

`HES = F1_clinical`

Where:

- `Precision_clinical = TP_clinical / (TP_clinical + FP_clinical)`  
- `Recall_clinical = TP_clinical / (TP_clinical + FN_clinical)`  
- `F1_clinical = 2 × (Precision_clinical × Recall_clinical) / (Precision_clinical + Recall_clinical)`  

HES is not a novel metric; it is the F1 score restricted to clinically constrained benchmark cases.

**Current values:**

- Domain Precision: 44.6%
- Domain Recall: 63.1%
- **HES (Domain F1): 0.523**

This separation prevents improvements in general extraction (e.g., better OCR, text parsing) from inflating measured clinical reasoning capability. HES specifically measures the model's healthcare domain knowledge.

### Clinical Error Type Breakdown

The 17 clinical error types tested include:

1. **Gender Mismatch** (100% recall, 20 cases) — Perfect detection of gender-inappropriate procedures
2. **Age-Inappropriate Screening** (100% recall, 6 cases) — All age-restricted screenings caught
3. **Age-Inappropriate Procedure** (100% recall, 2 cases)
4. **Procedure Inconsistent with Health History** (87.5% recall, 24 cases)
5. **Diagnosis-Procedure Mismatch** (80% recall, 5 cases)
6. **Age-Inappropriate** (77.8% recall, 9 cases)
7. **Surgical History Contradiction** (75% recall, 4 cases)
8. **Drug-Disease Contraindication** (50% recall, 4 cases)
9. **Medical Necessity** (50% recall, 2 cases)
10. **Duplicate Charge** (25% recall, 4 cases)
11. **Temporal Violation** (25% recall, 8 cases)
12. **Drug-Drug Interaction** (16.7% recall, 6 cases)
13. **Upcoding** (0% recall, 2 cases)
14. **Care Setting Inconsistency** (0% recall, 4 cases)
15. **Anatomical Contradiction** (0% recall, 2 cases)
16. **Dosing Error** (0% recall, 3 cases)
17. **Allergy Violation** (0% recall, 1 case)

**Key Insight**: MedGemma excels at demographic and clinical history validation (gender, age, surgical history) with 75-100% recall. It struggles with billing-specific patterns (upcoding, care setting) and pharmacological complexity (drug-drug interactions, dosing).

---

## Monitoring & Governance

The Production Stability Dashboard provides:

- Regression detection against statistical baselines  
- Versioned model tracking  
- F1 stability monitoring across runs  
- Cost savings tracking by model
- Error-type performance heatmaps

**Current snapshot:**

- `F1_all (current) = 0.469`  
- `F1_all (baseline) = 0.469` (top 25% of historical runs)
- No regression detected  
- Two tracked versions with rollback support  
- **$161K total potential savings** detected across all models
- medgemma-ensemble: **$80K savings**, **8348x ROI**

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

## Cost Savings & ROI

**Total Potential Savings Detected:** $161,490 (all models, 61 patient benchmarks)

**Top Performers:**
- medgemma-ensemble-v1.0: $80,348 (8348x ROI)
- medgemma-v1.0: $52,470 (5453x ROI)
- openai-v1.0: $20,025 (2081x ROI)

The high ROI reflects that model inference costs (~$0.01 per patient analysis) are negligible compared to billing error values ($100-$5,000 per detected issue).

**Savings Capture Rate:** 59.2% — medgemma-ensemble successfully identifies savings opportunities in 59% of cases where errors exist.

---

## Conclusion

medBillDozer operationalizes a healthcare-aligned open-weight model into a governed, monitored system capable of detecting clinically inconsistent billing patterns.

By clearly defining evaluation metrics, isolating clinical reasoning performance (Domain Detection Rate: 63.1%, HES: 0.523), and incorporating regression safeguards and version tracking, this project demonstrates transparent and responsible deployment of healthcare AI.

The system's strength lies in its ability to detect demographic and clinical history violations — the exact cases where patients are most vulnerable and least likely to catch errors themselves.

---

## References

1. [Medical bill error statistics](https://orbdoc.com/blog/medical-bill-errors-80-percent-problem/)
2. [Hospital bill errors (ABC News)](https://abcnews.go.com/Health/hospital-bill-errors-cost/story?id=11819214)
3. [Medical bankruptcy data](https://www.ilr.cornell.edu/scheinman-institute/blog/john-august-healthcare/healthcare-insights-how-medical-debt-crushing-100-million-americans)
4. [MedGemma documentation](https://ai.google.dev/gemma/docs/medgemma)
5. [GitHub repository](https://github.com/boobootoo2/medbilldozer)
