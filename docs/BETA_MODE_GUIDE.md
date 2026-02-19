# 🧪 BETA Mode Guide: Clinical Validation Dashboard

This guide explains how to enable and use the BETA mode in MedBillDozer, which adds **Clinical Validation** capabilities to the production stability dashboard.

## 📋 Overview

BETA mode adds a new tab to the Production Stability dashboard that displays:
- ✅ Clinical validation benchmark results
- 🔍 Error detection rates across medical imaging modalities
- 💰 Cost savings potential from detected clinical errors
- 📊 Multi-modal performance breakdown (X-ray, MRI, Histopathology, Ultrasound)
- 📈 Historical accuracy trends
- 📚 Clinical datasets with full attribution

## 🚀 Quick Start

### 1. Enable BETA Mode

Add the `BETA` environment variable to your `.env` file:

```bash
# Enable BETA features (Clinical Validation Dashboard)
BETA=true
```

Or export it in your shell:

```bash
export BETA=true
```

### 2. Configure Beta Database Access

Add Supabase Beta credentials to your `.env` file:

```bash
# Supabase Beta Database (for clinical validation)
SUPABASE_BETA_URL=https://zrhlpitzonhftigmdvgz.supabase.co
SUPABASE_BETA_KEY=your_beta_api_key_here
```

### 3. Download Clinical Images

Download and prepare medical imaging datasets:

```bash
# Download datasets from Kaggle
python3 scripts/download_kaggle_medical_images.py --select-images

# Verify images
ls -lh benchmarks/clinical_images/kaggle_datasets/selected/
```

This creates a `manifest.json` with proper attribution for all images.

### 4. Run Clinical Validation Benchmarks

Test locally:

```bash
# Single model
python3 scripts/run_clinical_validation_benchmarks.py --model gpt-4o-mini

# All models with Supabase push
python3 scripts/run_clinical_validation_benchmarks.py --model all --push-to-supabase
```

### 5. View in Dashboard

Start Streamlit:

```bash
streamlit run medBillDozer.py
```

Navigate to: **🚨 Production Stability** → **🏥 Clinical Validation (BETA)** tab

---

## 🏥 Clinical Validation Benchmarks

### What It Tests

The clinical validation system tests AI models' ability to detect **mismatches between diagnostic findings and prescribed treatments** across multiple medical imaging modalities.

### Scenarios

8 clinical scenarios covering 4 imaging modalities:

#### X-Ray (2 scenarios)
- ❌ Normal lung → Unnecessary antibiotics ($15K error)
- ✅ COVID pneumonia → Appropriate treatment

#### Histopathology (2 scenarios)
- ❌ Benign tissue → Unnecessary chemotherapy ($150K error)
- ✅ Adenocarcinoma → Appropriate surgery

#### MRI (2 scenarios)
- ❌ No tumor → Unnecessary craniotomy ($85K error)
- ✅ Glioma → Appropriate surgery

#### Ultrasound (2 scenarios)
- ❌ Normal breast → Unnecessary biopsy ($8K error)
- ✅ Malignant mass → Appropriate biopsy

### Metrics

- **Accuracy**: Percentage of correct determinations
- **Error Detection Rate**: Percentage of actual errors correctly identified
- **False Positive Rate**: Percentage of correct treatments incorrectly flagged
- **Cost Savings Potential**: Total value of detected errors

---

## 🤖 GitHub Actions Integration

### Automated Benchmarks

The clinical validation benchmarks run automatically via GitHub Actions:

**Schedule:**
- 🕚 **11:00 PM UTC** - Warmup HuggingFace endpoints
- 🕛 **12:00 AM UTC** - Run clinical validation benchmarks

**Workflow:** `.github/workflows/clinical_validation_benchmarks.yml`

### Required Secrets

Add these secrets to your GitHub repository:

```
Settings → Secrets and variables → Actions → New repository secret
```

| Secret Name | Description |
|------------|-------------|
| `SUPABASE_BETA_KEY` | Beta database API key |
| `OPENAI_API_KEY` | OpenAI API key (GPT models) |
| `ANTHROPIC_API_KEY` | Anthropic API key (Claude) |
| `GEMINI_API_KEY` | Google Gemini API key |
| `HF_API_TOKEN` | HuggingFace API token (MedGemma) |
| `HF_ENDPOINT_BASE` | HuggingFace endpoint URL (MedGemma) |

### Manual Trigger

Run benchmarks manually:

1. Go to **Actions** tab
2. Select **Clinical Validation Benchmarks**
3. Click **Run workflow**
4. Choose model (default: `all`)

---

## 📊 Dashboard Features

### Main Metrics (Top Row)

```
🎯 Accuracy          🔍 Error Detection    ⚠️ False Positive    💰 Cost Savings
   87.5%                100.0%                 0.0%              $258K
```

### Performance by Modality

Table showing accuracy breakdown by imaging type:

| Modality | Accuracy | Scenarios | Errors Detected | False Positives |
|----------|----------|-----------|-----------------|-----------------|
| X-ray | 100.0% | 2 | 1 | 0 |
| Histopathology | 100.0% | 2 | 1 | 0 |
| MRI | 100.0% | 2 | 1 | 0 |
| Ultrasound | 50.0% | 2 | 0 | 1 |

### Historical Trends

Line chart showing accuracy over time across all models:
- Track performance regressions
- Compare models (GPT-4o, Claude 3.5, Gemini 2.0)
- Identify trends

### Cost Impact Analysis

Shows potential savings from detected clinical errors:
- **Unnecessary Antibiotics**: ~$15K/case
- **Unnecessary Biopsy**: ~$8K/case
- **Unnecessary Craniotomy**: ~$85K/case
- **Unnecessary Chemotherapy**: ~$150K/case

### Clinical Data Sets (Accordion)

Expandable section showing:
- 📸 **Image thumbnails** (clickable to view full size)
- 📄 **Full attribution** (dataset name, license, citation)
- 🏷️ **Metadata** (modality, diagnosis, source file)
- 🔍 **Modal viewer** for large image display with caption

**Example:**

```
[Thumbnail]  | xray_positive.png
             | Modality: Xray
             | Diagnosis: Positive
             | Dataset: COVID-19 Radiography Database
             | [📄 Full Attribution]
```

Clicking "🔍 View Full" opens a modal with:
- Full-size image
- Complete attribution caption
- Dataset URL and citation

---

## 🗄️ Database Schema

### Supabase Beta Database

**Table:** `clinical_validation_snapshots`

```sql
CREATE TABLE clinical_validation_snapshots (
  id BIGSERIAL PRIMARY KEY,
  model_version TEXT NOT NULL,
  dataset_version TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  environment TEXT NOT NULL,
  benchmark_type TEXT NOT NULL DEFAULT 'clinical_validation',
  metrics JSONB NOT NULL,
  scenario_results JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  triggered_by TEXT
);
```

**Metrics Structure:**

```json
{
  "accuracy": 0.875,
  "error_detection_rate": 1.0,
  "false_positive_rate": 0.0,
  "total_scenarios": 8,
  "correct_determinations": 7,
  "scenarios_by_modality": {
    "xray": 2,
    "histopathology": 2,
    "mri": 2,
    "ultrasound": 2
  },
  "total_cost_savings_potential": 258000
}
```

---

## 🖼️ Medical Image Attribution

All images are sourced from publicly available Kaggle datasets with proper licensing and attribution.

### Manifest Structure

File: `benchmarks/clinical_images/kaggle_datasets/selected/manifest.json`

```json
{
  "created": "2026-02-14T10:30:00Z",
  "total_images": 7,
  "modalities": ["xray", "histopathology", "mri", "ultrasound"],
  "images": [
    {
      "filename": "xray_positive.png",
      "modality": "xray",
      "diagnosis": "positive",
      "source_file": "COVID/images/COVID-1.png",
      "dataset_name": "COVID-19 Radiography Database",
      "dataset_url": "https://www.kaggle.com/datasets/tawsifurrahman/covid19-radiography-database",
      "license": "CC BY 4.0",
      "citation": "Chowdhury et al. (2020). Can AI help in screening Viral and COVID-19 pneumonia?"
    }
  ],
  "datasets_used": {
    "COVID-19 Radiography Database": {
      "url": "https://www.kaggle.com/datasets/tawsifurrahman/covid19-radiography-database",
      "license": "CC BY 4.0",
      "images_used": 1
    }
  }
}
```

### Supported Datasets

| Modality | Dataset | License | Size |
|----------|---------|---------|------|
| X-ray | COVID-19 Radiography | CC BY 4.0 | 1.2 GB |
| Histopathology | LC25000 Lung/Colon | CC BY-NC-SA 4.0 | 1.5 GB |
| MRI | Brain Tumor MRI | Custom | 150 MB |
| CT | SIIM Medical Images | CC0 | 3 GB |
| Ultrasound | Breast Ultrasound | CC BY-NC-SA 4.0 | 50 MB |

---

## 🔧 Troubleshooting

### "BETA Mode not showing"

**Check:**
```bash
# Verify environment variable
echo $BETA

# Should output: true
```

**Fix:**
```bash
export BETA=true
streamlit run medBillDozer.py
```

### "Clinical validation data unavailable"

**Check:**
```bash
# Verify Supabase Beta credentials
echo $SUPABASE_BETA_KEY
echo $SUPABASE_BETA_URL
```

**Fix:**
Add to `.env`:
```bash
SUPABASE_BETA_KEY=your_actual_key_here
SUPABASE_BETA_URL=https://zrhlpitzonhftigmdvgz.supabase.co
```

### "Manifest not found"

**Check:**
```bash
ls -l benchmarks/clinical_images/kaggle_datasets/selected/manifest.json
```

**Fix:**
```bash
python3 scripts/download_kaggle_medical_images.py --select-images
```

### "Images not loading in modal"

**Check:**
- PIL/Pillow installed: `pip install Pillow`
- Image files exist: `ls benchmarks/clinical_images/kaggle_datasets/selected/`
- File permissions: `chmod 644 benchmarks/clinical_images/kaggle_datasets/selected/*.png`

---

## 📈 Production Rollout Plan

### Phase 1: Internal Beta (Current)
- ✅ BETA mode flag required
- ✅ Separate beta database
- ✅ Manual testing and validation
- ✅ GitHub Actions automation

### Phase 2: Limited Production (Future)
- 📅 Promote to main production database
- 📅 Remove BETA flag requirement
- 📅 Production monitoring and alerts
- 📅 Cost-benefit analysis

### Phase 3: Full Production (Future)
- 📅 Integrate with main billing error detection
- 📅 Multi-tab dashboard as default
- 📅 Automated clinical error alerts
- 📅 Healthcare partner integration

---

## 📚 Related Documentation

- [KAGGLE_QUICKSTART.md](./KAGGLE_QUICKSTART.md) - Download medical images
- [DATASETS_OVERVIEW.md](./DATASETS_OVERVIEW.md) - Available datasets
- [benchmarks/clinical_images/README.md](./benchmarks/clinical_images/README.md) - Clinical validation details
- [scripts/run_clinical_validation_benchmarks.py](./scripts/run_clinical_validation_benchmarks.py) - Benchmark script

---

## 🤝 Contributing

To add new clinical scenarios:

1. Add images to manifest
2. Update `CLINICAL_SCENARIOS` in `run_clinical_validation_benchmarks.py`
3. Document expected behavior
4. Test locally before pushing
5. Submit PR with benchmark results

---

## 📝 License

Medical images are subject to their original dataset licenses (see manifest.json for attribution).

MedBillDozer code is licensed under [LICENSE](./LICENSE).

---

**Questions?** Open an issue on GitHub or contact the MLOps team.
