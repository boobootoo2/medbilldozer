# 🧪 BETA Mode: Clinical Validation Dashboard

## Overview

BETA mode adds a **Clinical Validation Dashboard** to the Production Stability monitoring system, providing multi-modal medical imaging error detection benchmarks alongside the existing billing error detection dashboard.

## Features

### Clinical Validation Benchmarks
- **Multi-Modal Imaging**: X-ray, MRI, Histopathology, Ultrasound
- **Error Detection Scenarios**: Overtreatment, unnecessary procedures, incorrect diagnoses
- **Correct Treatment Validation**: Verifies appropriate clinical decisions
- **Cost Impact Analysis**: Tracks potential savings from detected errors ($15K-$150K per case)
- **Historical Trends**: Accuracy tracking over time across models
- **Modality Breakdown**: Performance comparison by imaging type

### Dashboard Layout (BETA Mode)
When `BETA=true`, the dashboard displays **7 tabs** instead of 6:

1. **🏥 Clinical Validation (BETA)** - New multi-modal clinical error detection
2. 🏥 Clinical Reasoning Evaluation - Existing billing error analysis
3. 📊 System Health Overview
4. 📈 Reliability Over Time
5. ⚖️ Model Effectiveness Comparison
6. 🚨 Performance Stability Monitor
7. 🕐 Snapshot History

## Setup

### 1. Environment Variables

Add these to your `.env` file:

```bash
# Enable BETA mode
BETA=true

# Beta database credentials (clinical validation)
SUPABASE_BETA_URL=https://zrhlpitzonhftigmdvgz.supabase.co
SUPABASE_BETA_KEY=your_beta_api_key_here
```

### 2. GitHub Actions Secrets

Add to your repository secrets:

```
SUPABASE_BETA_KEY=your_beta_api_key_here
SUPABASE_BETA_URL=https://zrhlpitzonhftigmdvgz.supabase.co
```

### 3. Database Schema

The beta database requires a `clinical_validation_snapshots` table:

```sql
CREATE TABLE clinical_validation_snapshots (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    model_version VARCHAR(100),
    environment VARCHAR(50) DEFAULT 'beta',
    accuracy FLOAT,
    error_detection_rate FLOAT,
    false_positive_rate FLOAT,
    total_scenarios INTEGER,
    correct_determinations INTEGER,
    errors_detected INTEGER,
    false_positives INTEGER,
    total_cost_savings_potential INTEGER,
    modality_breakdown JSONB,
    scenario_results JSONB,
    metadata JSONB
);

CREATE INDEX idx_clinical_timestamp ON clinical_validation_snapshots(timestamp DESC);
CREATE INDEX idx_clinical_model ON clinical_validation_snapshots(model_version);
CREATE INDEX idx_clinical_env ON clinical_validation_snapshots(environment);
```

## Automated Workflows

### Clinical Validation Benchmarks
- **Schedule**: Daily at 12:00 AM UTC (midnight)
- **Workflow**: `.github/workflows/clinical_validation_benchmarks.yml`
- **Script**: `scripts/run_clinical_validation_benchmarks.py`
- **Models Tested**: GPT-4o-mini, GPT-4o, Claude-3.5-Sonnet, Gemini-2.0-Flash

### Warmup Endpoint
- **Schedule**: Daily at 11:00 PM UTC (1 hour before validation)
- **Workflow**: `.github/workflows/warmup_hf_endpoint.yml`
- **Purpose**: Ensure HuggingFace endpoint is warm before benchmark runs

## Manual Testing

### Run Clinical Validation Locally

```bash
# Set environment variables
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
export GEMINI_API_KEY=your_key
export SUPABASE_BETA_KEY=your_beta_key
export SUPABASE_BETA_URL=https://zrhlpitzonhftigmdvgz.supabase.co

# Run with single model
python3 scripts/run_clinical_validation_benchmarks.py --model gpt-4o-mini

# Run all models and push to Supabase
python3 scripts/run_clinical_validation_benchmarks.py --model all --push-to-supabase --environment beta
```

### View Dashboard Locally

```bash
# Enable BETA mode
export BETA=true
export SUPABASE_BETA_KEY=your_beta_key
export SUPABASE_BETA_URL=https://zrhlpitzonhftigmdvgz.supabase.co

# Also need production credentials for billing error dashboard
export SUPABASE_URL=your_prod_url
export SUPABASE_SERVICE_ROLE_KEY=your_prod_key

# Run Streamlit
streamlit run medBillDozer.py
```

Navigate to **🚨 Production Stability** page to see both dashboards.

## Clinical Scenarios

### Error Detection Scenarios (4 total)
1. **X-ray (Overtreatment)**: Normal lung → Unnecessary antibiotics ($15K)
2. **Histopathology (Overtreatment)**: Benign tissue → Unnecessary chemo ($150K)
3. **MRI (Unnecessary Procedure)**: No tumor → Unnecessary craniotomy ($85K)
4. **Ultrasound (Unnecessary Procedure)**: Normal breast → Unnecessary biopsy ($8K)

### Correct Treatment Validation (4 total)
1. **X-ray (Appropriate)**: COVID pneumonia → Appropriate treatment
2. **Histopathology (Appropriate)**: Adenocarcinoma → Surgery
3. **MRI (Appropriate)**: Glioma → Appropriate surgery
4. **Ultrasound (Appropriate)**: Malignant mass → Appropriate biopsy

## Metrics Tracked

### Performance Metrics
- **Accuracy**: Overall percentage of correct determinations
- **Error Detection Rate**: Percentage of actual errors correctly identified
- **False Positive Rate**: Percentage of correct treatments incorrectly flagged
- **Cost Savings Potential**: Total value of detected errors

### Modality Breakdown
Each imaging modality tracked separately:
- X-ray
- Histopathology
- MRI
- Ultrasound

## Disabling BETA Mode

To return to standard billing error dashboard only:

```bash
# Remove or set to false
export BETA=false
# or
unset BETA
```

Dashboard will revert to 6 tabs without clinical validation.

## Troubleshooting

### "Clinical validation data unavailable"
- Check `SUPABASE_BETA_KEY` is set correctly
- Verify database URL: `https://zrhlpitzonhftigmdvgz.supabase.co`
- Ensure `clinical_validation_snapshots` table exists

### "No clinical validation data available yet"
- Benchmarks run daily at midnight UTC
- Run manually to populate data: `python3 scripts/run_clinical_validation_benchmarks.py --model all --push-to-supabase`

### GitHub Actions not pushing data
- Verify `SUPABASE_BETA_KEY` secret is set in repository
- Check workflow logs: `.github/workflows/clinical_validation_benchmarks.yml`
- Ensure clinical images exist in `benchmarks/clinical_images/kaggle_datasets/selected/`

## Image Attribution

All clinical images sourced from Kaggle datasets with full attribution tracked in:
```
benchmarks/clinical_images/kaggle_datasets/selected/manifest.json
```

Licenses: CC BY 4.0, CC BY-NC-SA 4.0, CC0 (Public Domain)

## Future Enhancements

- [ ] Expand to 12 scenarios (6 positive, 6 negative)
- [ ] Add CT scan and Echocardiogram modalities
- [ ] Real-time clinical validation API endpoint
- [ ] Integration with production clinical workflows
- [ ] Multi-reader agreement studies

---

**Status**: 🧪 BETA (February 2026)  
**Maintainer**: MLOps Team  
**Database**: Supabase Beta Instance
