# 🧪 BETA Mode Quick Start

Enable clinical validation dashboard in 3 steps:

## 1️⃣ Enable BETA

```bash
echo "BETA=true" >> .env
echo "SUPABASE_BETA_KEY=your_key_here" >> .env
echo "SUPABASE_BETA_URL=https://zrhlpitzonhftigmdvgz.supabase.co" >> .env
```

## 2️⃣ Download Images

```bash
python3 scripts/download_kaggle_medical_images.py --select-images
```

## 3️⃣ View Dashboard

```bash
streamlit run medBillDozer.py
```

Navigate to: **Production Stability** → **🏥 Clinical Validation (BETA)** tab

---

## 📊 What You'll See

### Metrics
- 🎯 **Accuracy**: Overall correctness (target: >85%)
- 🔍 **Error Detection Rate**: Catching actual errors (target: 100%)
- ⚠️ **False Positive Rate**: Incorrect error flags (target: <10%)
- 💰 **Cost Savings**: Value of detected errors ($15K-$150K each)

### Charts
- Bar chart: Accuracy by modality (X-ray, MRI, Histopathology, Ultrasound)
- Line chart: Historical accuracy trends
- Table: Model comparison across all runs

### Clinical Data Sets (New Feature!)
- **Thumbnail gallery** of all medical images
- **Modal viewer**: Click "🔍 View Full" to see full-size image
- **Complete attribution**: Dataset name, license, citation
- **Metadata**: Modality, diagnosis, source file

---

## 🤖 Run Benchmarks

### Test Single Model
```bash
# Commercial models
python3 scripts/run_clinical_validation_benchmarks.py --model gpt-4o-mini
python3 scripts/run_clinical_validation_benchmarks.py --model claude-3-5-sonnet

# Medical-specific models (HuggingFace)
python3 scripts/run_clinical_validation_benchmarks.py --model medgemma
python3 scripts/run_clinical_validation_benchmarks.py --model medgemma-ensemble
```

### Test All Models + Push to Database
```bash
# Runs all 6 models: GPT-4o (mini/full), Claude 3.5, Gemini 2.0, MedGemma (single/ensemble)
python3 scripts/run_clinical_validation_benchmarks.py --model all --push-to-supabase
```

**Available Models:**
- `gpt-4o-mini` / `gpt-4o` - OpenAI models
- `claude-3-5-sonnet` - Anthropic Claude
- `gemini-2.0-flash` - Google Gemini
- `medgemma` - Google MedGemma (medical-specific)
- `medgemma-ensemble` - MedGemma ensemble voting
- `all` - Run all models

---

## ⏰ Automation

Benchmarks run automatically via GitHub Actions:

- **11:00 PM UTC**: Warmup endpoints
- **12:00 AM UTC**: Clinical validation (all models)
- **Results**: Auto-pushed to Supabase Beta

Manual trigger: **Actions** → **Clinical Validation Benchmarks** → **Run workflow**

---

## 🔍 Modal Image Viewer

New accordion section at bottom of Clinical Validation tab:

1. Expand **"📚 Clinical Data Sets"**
2. Browse image thumbnails with descriptions
3. Click **"🔍 View Full"** on any image
4. View full-size image with complete attribution
5. Click **"✖ Close"** to dismiss

**Attribution includes:**
- Source dataset name
- License type (CC BY 4.0, etc.)
- Dataset URL
- Full citation

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| Tab not showing | `export BETA=true` |
| No data | Add `SUPABASE_BETA_KEY` to `.env` |
| Images not found | Run `download_kaggle_medical_images.py` |
| Modal not working | `pip install Pillow` |

---

📖 **Full Documentation**: [BETA_MODE_GUIDE.md](./BETA_MODE_GUIDE.md)
