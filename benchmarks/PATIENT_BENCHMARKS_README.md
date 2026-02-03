# Patient-Level Cross-Document Benchmarks

## Overview

This benchmark suite tests models' ability to detect medical inconsistencies that require **healthcare domain knowledge**. Unlike simple duplicate detection, these benchmarks evaluate whether models understand:

- **Gender-specific procedures** (e.g., males cannot receive obstetric care)
- **Age-appropriate screening guidelines** (e.g., children don't need colonoscopies)
- **Anatomically impossible procedures** (e.g., hysterectomy in males)

**This is where MedGemma should excel** due to its healthcare-specific training data and medical domain expertise.

## Test Scenarios

### 10 Patient Profiles

Each patient has:
- Demographic data (age, sex, DOB)
- Medical history (conditions, allergies, surgeries)
- 2+ documents to analyze together
- Expected issues requiring domain knowledge

| Patient | Age | Sex | Issue Type | Example |
|---------|-----|-----|------------|---------|
| John Doe | 45 | M | Gender Mismatch | Obstetric ultrasound billed to male |
| Mary Smith | 72 | F | Age Inappropriate | IUD insertion in 72-year-old |
| Robert Chen | 8 | M | Age Inappropriate | Colonoscopy for 8-year-old |
| Jennifer Garcia | 34 | F | Gender Mismatch | Prostate biopsy billed to female |
| Michael O'Connor | 28 | M | Gender Mismatch | Hysterectomy billed to male |
| Sarah Patel | 15 | F | Age Inappropriate | Mammogram for 15-year-old |
| David Thompson | 55 | M | Gender Mismatch | Cervical biopsy billed to male |
| Lisa Rodriguez | 3 | F | Age Inappropriate | Cardiac stress test for 3-year-old |
| James Williams | 82 | M | Multiple Issues | Pregnancy test + sports physical for 82-year-old male |
| Amanda Lee | 29 | F | Gender Mismatch | Vasectomy billed to female |

## Running Benchmarks

### Single Model
```bash
python scripts/generate_patient_benchmarks.py --model medgemma
python scripts/generate_patient_benchmarks.py --model openai
python scripts/generate_patient_benchmarks.py --model baseline
```

### All Models (Comparison)
```bash
python scripts/generate_patient_benchmarks.py --model all
```

## Metrics

### Standard Metrics
- **Precision**: Accuracy of detected issues (TP / (TP + FP))
- **Recall**: Coverage of expected issues (TP / (TP + FN))
- **F1 Score**: Harmonic mean of precision and recall

### Domain Knowledge Metric
- **Domain Knowledge Detection Rate**: Percentage of domain-knowledge issues correctly identified
  - Gender mismatches (anatomically impossible procedures)
  - Age-inappropriate screenings
  - Medical contraindications

This metric specifically measures healthcare expertise, not just pattern matching.

## Expected Results

### MedGemma Advantages
MedGemma should outperform general-purpose LLMs on:

1. **Gender-specific anatomy** - Understanding which procedures are physically impossible for each sex
2. **Age-based guidelines** - Knowing screening recommendations by age group
3. **Medical appropriateness** - Recognizing clinically inappropriate procedures

### Baseline Limitations
The local heuristic model will miss most of these issues because they require:
- Understanding medical terminology (CPT codes)
- Knowledge of human anatomy
- Clinical practice guidelines
- Age-based screening recommendations

## File Structure

```
benchmarks/
├── patient_profiles/
│   ├── patient_001_john_doe.json
│   ├── patient_002_mary_smith.json
│   └── ... (10 total)
├── inputs/
│   ├── patient_001_doc_1_medical_bill.txt
│   ├── patient_001_doc_2_lab_results.txt
│   └── ... (20 documents total)
└── results/
    ├── patient_benchmark_medgemma.json
    ├── patient_benchmark_openai.json
    └── patient_benchmark_baseline.json
```

## Example Output

```
🏥 PATIENT-LEVEL CROSS-DOCUMENT BENCHMARK SUITE
===================================================================
Testing models' ability to detect medical inconsistencies requiring
healthcare domain knowledge (gender/age-inappropriate procedures)
===================================================================

🏥 Running patient-level benchmarks for: MEDGEMMA
===================================================================
📋 Found 10 patient profiles

[1/10] John Doe (M, 45y)... ✅ 2450ms | Issues: 1/1 | Domain: 100%
[2/10] Mary Smith (F, 72y)... ✅ 1820ms | Issues: 1/1 | Domain: 100%
...

===================================================================
PATIENT BENCHMARK SUMMARY: MEDGEMMA
===================================================================
Patients Analyzed: 10/10
Avg Precision: 0.95
Avg Recall: 0.92
Avg F1 Score: 0.93
Domain Knowledge Detection Rate: 92.0%
Avg Analysis Time: 2100ms (2.10s)
===================================================================
```

## Why This Matters

Medical billing errors involving anatomically impossible procedures represent:
- **Coding errors** that insurers should reject automatically
- **Fraud indicators** that require investigation
- **System failures** in EMR/billing software

A model that can catch these errors protects patients from paying for procedures they couldn't have received and helps identify systemic billing issues.

## Contributing

To add new patient scenarios:
1. Create profile JSON in `patient_profiles/`
2. Add 2+ realistic documents to `inputs/`
3. Define expected issues with `requires_domain_knowledge: true`
4. Run benchmarks to validate

Focus on issues that require medical expertise, not just pattern matching!
