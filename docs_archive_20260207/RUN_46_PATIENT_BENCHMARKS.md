# Running 46-Patient Benchmark Analysis

**Last Updated:** 2026-02-05

This document explains how to run the comprehensive 46-patient benchmark analysis with advanced metrics.

---

## 🎯 Quick Start

### Run All Models (Baseline + MedGemma + OpenAI)

```bash
# Run patient benchmarks for all available models
python3 scripts/generate_patient_benchmarks.py --model all

# Or run individually
python3 scripts/generate_patient_benchmarks.py --model baseline
python3 scripts/generate_patient_benchmarks.py --model medgemma
python3 scripts/generate_patient_benchmarks.py --model openai
python3 scripts/generate_patient_benchmarks.py --model gemini   # Requires GOOGLE_API_KEY
python3 scripts/generate_patient_benchmarks.py --model gemma3   # Requires GOOGLE_API_KEY
```

### Push Results to Supabase

```bash
# Push all generated benchmarks
./scripts/push_local_benchmarks.sh

# Or push specific models
./scripts/push_local_benchmarks.sh baseline medgemma openai
```

---

## 📂 What You Have

### Patient Profiles
- **Location:** `benchmarks/patient_profiles/`
- **Count:** 46 patient profiles
- **Format:** JSON files with embedded documents
- **Files:** `patient_001.json` through `patient_046.json`

### Patient Documents
- **Location:** `benchmarks/inputs/`
- **Types:** Medical bills, EOBs, pharmacy receipts, dental bills, lab results, imaging reports
- **Medical History:** Each patient has a `patient_XXX_medical_history.txt` file

### Expected Outputs
- **Location:** `benchmarks/expected_outputs/`
- **Purpose:** Ground truth for evaluation

---

## ⚠️ Important: Don't Use Old Script

**❌ DON'T USE:** `python3 scripts/generate_benchmarks.py`
- This is the OLD document-level script
- It expects individual document files, not patient profiles
- It will show "Missing expected output" warnings

**✅ USE INSTEAD:** `python3 scripts/generate_patient_benchmarks.py`
- This is the NEW patient-level script
- It handles 46 patient profiles with multiple documents each
- It includes advanced metrics (risk-weighted recall, ROI, etc.)

---

## 🏃 Running Benchmarks

### Option 1: Run Single Model

```bash
python3 scripts/generate_patient_benchmarks.py --model baseline
```

**Expected Output:**
```
🏥 Running patient-level benchmarks for: Heuristic Baseline
======================================================================
📋 Found 46 patient profiles

[1/46] John Smith (M, 45y)... ✅ 1250ms | Issues: 3/3 | Domain Recall: 100%
[2/46] Sarah Johnson (F, 28y)... ✅ 980ms | Issues: 2/2 | Domain Recall: 100%
...
[46/46] Robert Lee (M, 72y)... ✅ 1100ms | Issues: 4/5 | Domain Recall: 80%

✨ Advanced Metrics Computed:
   Risk-Weighted Recall: 0.856
   Conservatism Index: 0.420
   P95 Latency: 2450.5ms
   ROI Ratio: 125.3x
   Inference Cost: $0.0234

💾 Results saved to: benchmarks/results/patient_benchmark_baseline.json
```

### Option 2: Run Multiple Models

```bash
python3 scripts/generate_patient_benchmarks.py --model baseline
python3 scripts/generate_patient_benchmarks.py --model medgemma
python3 scripts/generate_patient_benchmarks.py --model openai
```

### Option 3: Run All Available Models

```bash
# This will run all models that have API keys configured
python3 scripts/generate_patient_benchmarks.py --model all
```

**Note:** Models requiring API keys will be skipped if keys are missing:
- `gemini` - Requires `GOOGLE_API_KEY`
- `gemma3` - Requires `GOOGLE_API_KEY`
- `openai` - Requires `OPENAI_API_KEY`

---

## 🚀 Push to Supabase

After generating benchmarks locally, push them to Supabase:

```bash
# Push all generated patient benchmarks
./scripts/push_local_benchmarks.sh
```

This will:
1. Convert patient benchmarks to monitoring format
2. Extract advanced metrics
3. Upload to `benchmark_transactions` table
4. Upload to `benchmark_snapshots` table
5. Upload category metrics to `benchmark_category_metrics` table

**Expected Output:**
```bash
============================================================
Push Local Benchmark Results to Supabase
============================================================

📋 Metadata:
   Commit: a1b2c3d4
   Branch: develop
   User: jgs

Found 3 patient benchmark files to process:
  - benchmarks/results/patient_benchmark_baseline.json
  - benchmarks/results/patient_benchmark_medgemma.json
  - benchmarks/results/patient_benchmark_openai.json

Processing: patient_benchmark_baseline.json
   ✅ Converted to monitoring format
   ☁️  Pushing to Supabase...
   ✅ Successfully pushed to Supabase

🎉 Benchmark results have been pushed to Supabase!
```

---

## 📊 View Results

### Option 1: Streamlit Dashboard

```bash
streamlit run benchmark_dashboard.py
```

Then navigate to:
- **Model Benchmarks** page for model comparison
- **Advanced Metrics** section for risk-weighted recall, ROI, etc.
- **Category Performance** heatmap for regression tracking

### Option 2: Query Supabase Directly

```bash
# View latest results
python3 scripts/get_supabase_transactions.py

# View specific model
python3 scripts/get_supabase_transactions.py --model "Heuristic Baseline"

# Export to JSON
python3 scripts/get_supabase_transactions.py --output results.json
```

### Option 3: SQL Query

```sql
-- Latest advanced metrics
SELECT 
    model_version,
    risk_weighted_recall,
    conservatism_index,
    roi_ratio,
    p95_latency_ms
FROM v_advanced_benchmark_metrics
ORDER BY created_at DESC
LIMIT 10;

-- Category regression tracking
SELECT * 
FROM v_category_regression_tracking
WHERE regression_status IN ('severe_regression', 'moderate_regression')
ORDER BY created_at DESC;
```

---

## 🎯 High-Signal Subset Mode

For rapid testing, use the high-signal subset (8 patients with obvious errors):

```bash
python3 scripts/generate_patient_benchmarks.py --model baseline --subset high_signal
```

**High-Signal Patients:**
- `patient_001` - Male with obstetric ultrasound
- `patient_002` - Male with Pap smear
- `patient_006` - 15yo with screening mammogram
- `patient_011` - 8yo with screening colonoscopy
- `patient_031` - Right leg amputation + right knee billing
- `patient_032` - Appendectomy + appendix removal rebilling
- `patient_033` - Bilateral mastectomy + breast procedure billing
- `patient_035` - Hysterectomy + uterine procedure billing

---

## 📈 What Metrics Are Computed

### Standard Metrics
- **Precision** - TP / (TP + FP)
- **Recall** - TP / (TP + FN)
- **F1 Score** - Harmonic mean of precision and recall
- **Latency** - Average and P95 analysis time

### Advanced Metrics (NEW)
- **Risk-Weighted Recall** - Prioritizes critical errors (3x weight for surgical contradictions)
- **Conservatism Index** - FN/(FN+FP) - measures false negative bias
- **ROI Ratio** - Savings / Inference Cost
- **P95 Latency** - 95th percentile for SLA monitoring
- **Inference Cost** - Estimated cost based on latency

### Category-Level Metrics
- **Per-category recall** - Detection rate for each error type
- **Regression tracking** - Delta from previous run
- **Severity classification** - Severe/moderate/minor/stable/improvement

### Cost Savings Metrics
- **Total Potential Savings** - $ saved from detected errors
- **Total Missed Savings** - $ from undetected errors
- **Savings Capture Rate** - % of total possible savings captured
- **Avg Savings per Patient** - Average financial impact

---

## 🐛 Troubleshooting

### Issue: "Missing expected output" warnings
**Problem:** You're running the old `generate_benchmarks.py` script
**Solution:** Use `generate_patient_benchmarks.py` instead

### Issue: "GOOGLE_API_KEY not set"
**Problem:** Trying to run Gemini/Gemma3 without API key
**Solution:** 
```bash
export GOOGLE_API_KEY="your-key-here"
# Or skip these models and run: --model baseline
```

### Issue: "Advanced metrics not computing"
**Problem:** `scripts/advanced_metrics.py` module not found
**Solution:** Verify file exists and try:
```bash
python3 -c "from scripts.advanced_metrics import compute_advanced_metrics; print('✅ OK')"
```

### Issue: "Supabase push fails - table not found"
**Problem:** Database migration hasn't been run
**Solution:** Run the migration first:
```bash
# In Supabase Dashboard SQL Editor, run:
# sql/migration_advanced_metrics.sql
python3 scripts/run_advanced_metrics_migration.py
```

---

## 📋 Checklist

Before running full 46-patient benchmarks:

- [ ] Database migration run in Supabase
- [ ] API keys configured (if using paid models)
- [ ] `scripts/advanced_metrics.py` module exists
- [ ] At least 46 patient profiles in `benchmarks/patient_profiles/`
- [ ] `.env` file has `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`

---

## 🔗 Related Documentation

- [Advanced Metrics Implementation](ADVANCED_METRICS_IMPLEMENTATION.md) - Full technical guide
- [Advanced Metrics Quick Reference](ADVANCED_METRICS_QUICKREF.md) - Command cheat sheet
- [Benchmark Monitoring Setup](BENCHMARK_MONITORING_SETUP.md) - Dashboard configuration

---

**Ready to run?**
```bash
python3 scripts/generate_patient_benchmarks.py --model all
```
