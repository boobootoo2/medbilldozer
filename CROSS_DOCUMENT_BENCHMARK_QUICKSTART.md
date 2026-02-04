# Cross-Document Medical Context Benchmark - Quick Start Guide

## Overview

This benchmark suite tests **medical domain knowledge** across multiple documents. It evaluates if models can detect billing errors that require understanding:

- **Gender-specific procedures** (e.g., males can't receive obstetric care)
- **Age-appropriate screenings** (e.g., children don't need colonoscopies)
- **Anatomically impossible procedures** (e.g., prostate surgery for females)

**This is where MedGemma demonstrates its superiority** due to healthcare-specific training.

## Test Scenarios

10 patient profiles with intentional medical billing errors:

| Patient | Age | Sex | Issue Type | Example Error |
|---------|-----|-----|------------|---------------|
| John Doe | 45 | M | Gender Mismatch | Obstetric ultrasound (CPT 76805) |
| Mary Smith | 72 | F | Age Inappropriate | IUD insertion |
| Robert Chen | 8 | M | Age Inappropriate | Colonoscopy screening |
| Jennifer Garcia | 34 | F | Gender Mismatch | Prostate biopsy |
| Michael O'Connor | 28 | M | Gender Mismatch | Hysterectomy |
| Sarah Patel | 15 | F | Age Inappropriate | Mammogram screening |
| David Thompson | 55 | M | Gender Mismatch | Cervical biopsy |
| Lisa Rodriguez | 3 | F | Age Inappropriate | Cardiac stress test |
| James Williams | 82 | M | Multiple Issues | Pregnancy test + sports physical |
| Amanda Lee | 29 | F | Gender Mismatch | Vasectomy |

## Quick Start

### 1. Run Benchmarks Locally

```bash
# Run all models
python scripts/generate_patient_benchmarks.py --model all

# Run specific model
python scripts/generate_patient_benchmarks.py --model medgemma

# Results saved to: benchmarks/results/patient_benchmark_{model}.json
```

### 2. Run and Push to Database (for Historical Tracking)

```bash
# Run and automatically push to Supabase
python scripts/generate_patient_benchmarks.py \
  --model all \
  --push-to-supabase \
  --environment local

# From CI/CD (GitHub Actions)
python scripts/generate_patient_benchmarks.py \
  --model all \
  --push-to-supabase \
  --environment github-actions \
  --commit-sha ${{ github.sha }}
```

### 3. View Historical Results

```bash
# Start monitoring dashboard
python3 -m streamlit run pages/benchmark_monitoring.py

# Navigate to "Patient Benchmarks" tab
# View MedGemma's performance over time
```

## Expected Results

### MedGemma Advantages
MedGemma should significantly outperform general-purpose LLMs:

```
Model Performance (Expected):
- MedGemma:    F1: 0.90+  Domain Detection: 90%+  ✅
- GPT-4:       F1: 0.20   Domain Detection: 20%   ⚠️
- Gemini Pro:  F1: 0.15   Domain Detection: 15%   ⚠️
- Baseline:    F1: 0.00   Domain Detection: 0%    ❌
```

**Why MedGemma Wins:**
1. **Understands CPT codes** - Knows what procedures mean medically
2. **Medical training data** - Trained on healthcare-specific content
3. **Anatomical knowledge** - Understands gender-specific procedures
4. **Clinical guidelines** - Knows age-appropriate screenings

### General LLM Limitations
GPT-4 and Gemini struggle because they need explicit prompting:
- Don't automatically check gender/procedure compatibility
- Lack built-in medical screening guidelines
- Treat medical bills like generic documents

## Metrics Explained

### Standard Metrics
- **Precision**: % of detected issues that are real (no false alarms)
- **Recall**: % of real issues that were detected (didn't miss any)
- **F1 Score**: Balanced metric combining precision and recall

### Domain Knowledge Metric (Key Differentiator)
- **Domain Knowledge Detection Rate**: % of medical-context issues caught
- This specifically measures healthcare expertise, not just pattern matching
- Calculated from issues that require medical domain knowledge

## File Structure

```
benchmarks/
├── patient_profiles/                    # Patient demographics + expected issues
│   ├── patient_001_john_doe.json
│   ├── patient_002_mary_smith.json
│   └── ... (10 total)
├── inputs/                              # Documents to analyze
│   ├── patient_001_doc_1_medical_bill.txt
│   ├── patient_001_doc_2_lab_results.txt
│   ├── patient_001_medical_history.txt
│   └── ... (30 documents total)
└── results/                             # Generated results
    ├── patient_benchmark_medgemma.json
    ├── patient_benchmark_openai.json
    ├── patient_benchmark_gemini.json
    └── patient_benchmark_baseline.json
```

## Sample Output

```
🏥 PATIENT-LEVEL CROSS-DOCUMENT BENCHMARK SUITE
======================================================================
Testing models' ability to detect medical inconsistencies requiring
healthcare domain knowledge (gender/age-inappropriate procedures)
======================================================================

🏥 Running patient-level benchmarks for: MEDGEMMA
======================================================================
📋 Found 10 patient profiles

[1/10] John Doe (M, 45y)... ✅ 2450ms | Issues: 1/1 | Domain: 100%
[2/10] Mary Smith (F, 72y)... ✅ 1820ms | Issues: 1/1 | Domain: 100%
[3/10] Robert Chen (M, 8y)... ✅ 2100ms | Issues: 1/1 | Domain: 100%
...

======================================================================
PATIENT BENCHMARK SUMMARY: MEDGEMMA
======================================================================
Patients Analyzed: 10/10
Avg Precision: 0.95
Avg Recall: 0.95
Avg F1 Score: 0.95
Domain Knowledge Detection Rate: 95.0%
Avg Analysis Time: 2100ms (2.10s)
======================================================================
```

## Advanced Usage

### Compare Models Over Time

```bash
# Run benchmarks daily/weekly
python scripts/generate_patient_benchmarks.py --model all --push-to-supabase

# View trends in dashboard
python3 -m streamlit run pages/benchmark_monitoring.py
# Go to "Patient Benchmarks" tab
# See MedGemma's consistent performance vs. competitors
```

### Manual Push to Database

```bash
# If you ran benchmarks without --push-to-supabase
python scripts/push_patient_benchmarks.py \
  --model medgemma \
  --environment local \
  --commit-sha $(git rev-parse HEAD)
```

### Query Historical Data

```python
from scripts.benchmark_data_access import BenchmarkDataAccess

data = BenchmarkDataAccess()

# Get patient benchmark time series
ts_df = data.get_time_series(
    model_version='medgemma',
    metric='domain_knowledge_detection_rate',
    days_back=90
)

# Compare models
comparison = data.compare_models(
    ['medgemma', 'openai', 'gemini'],
    days_back=30
)
```

## Real-World Impact

These test cases reflect **actual billing errors** patients encounter:

1. **Gender mismatches** - Common in electronic systems with data entry errors
2. **Age-inappropriate procedures** - Often from miscoded preventive screenings
3. **Anatomically impossible** - Clear fraud or data corruption indicators

A model with high domain knowledge detection protects patients from:
- ❌ Paying for impossible procedures
- ❌ Insurance denials due to inappropriate codes
- ❌ Medical identity theft
- ❌ Provider billing fraud

## Troubleshooting

### No API Key for MedGemma
```bash
# Set Hugging Face token
export HF_API_TOKEN="your_token_here"

# Or add to .env file
echo "HF_API_TOKEN=your_token_here" >> .env
```

### Database Connection Issues
```bash
# Verify Supabase credentials
python scripts/check_snapshots.py

# Test connection
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('URL:', os.getenv('SUPABASE_URL')[:20])"
```

### Low Domain Detection Rate
If MedGemma shows low domain detection (<80%):
- Check patient profile expected_issues are marked `requires_domain_knowledge: true`
- Verify medical_history documents exist for context
- Review prompt in `generate_patient_benchmarks.py` line ~220

## Next Steps

1. ✅ Run initial benchmarks: `python scripts/generate_patient_benchmarks.py --model all`
2. ✅ Review results in `benchmarks/results/`
3. ✅ Push to database: `--push-to-supabase`
4. ✅ View dashboard: `python3 -m streamlit run pages/benchmark_monitoring.py`
5. ✅ Set up CI/CD to run weekly
6. ✅ Track MedGemma's performance over time

## Related Documentation

- [Patient Benchmarks README](benchmarks/PATIENT_BENCHMARKS_README.md) - Detailed technical docs
- [Benchmark Monitoring Dashboard](BENCHMARK_MONITORING_README.md) - Dashboard guide
- [MedGemma Cross-Document Fix](docs/MEDGEMMA_CROSS_DOCUMENT_FIX.md) - Implementation details

---

**Questions?** Open an issue or check the detailed documentation.

**Last Updated:** February 4, 2026
