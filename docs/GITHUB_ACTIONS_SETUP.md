# GitHub Actions Setup Guide

## Overview

The benchmark workflow (`.github/workflows/run_benchmarks.yml`) automatically runs benchmarks and commits results. This guide explains how it works and how to configure API keys.

## 🔄 How the Workflow Works

### Triggers
The workflow runs on:
1. **Schedule**: Daily at 2:00 AM UTC
2. **Manual**: Click "Run workflow" in GitHub Actions tab
3. **Push**: When code changes to:
   - `_modules/providers/**` (provider code)
   - `scripts/generate_benchmarks.py` (benchmark script)
   - `benchmarks/inputs/**` (test cases)
   - `.github/workflows/run_benchmarks.yml` (workflow itself)

### Execution Steps

```yaml
1. Checkout code
2. Setup Python 3.11
3. Install dependencies (requirements-benchmarks.txt)
4. Run benchmarks with API keys from secrets
5. Commit results to repo
6. Comment on PR (if triggered by PR)
```

## 🔑 API Keys Required

The workflow needs these API keys (configured as GitHub Secrets):

### 1. `OPENAI_API_KEY` (Required)
- **Provider**: OpenAI GPT models
- **Used by**: `OpenAIAnalysisProvider`
- **Get it**: https://platform.openai.com/api-keys
- **Format**: `sk-proj-...` (starts with `sk-`)

### 2. `HF_API_TOKEN` (Required)
- **Provider**: Hugging Face (MedGemma hosted model)
- **Used by**: `MedGemmaHostedProvider`
- **Get it**: https://huggingface.co/settings/tokens
- **Format**: `hf_...` (starts with `hf_`)

### 3. `GOOGLE_API_KEY` (Required for Gemini)
- **Provider**: Google Gemini
- **Used by**: `GeminiAnalysisProvider`
- **Get it**: https://aistudio.google.com/app/apikey
- **Format**: `AIza...` (starts with `AIza`)
- **Note**: Currently referenced as `GOOGLE_API_KEY` in `.env.example` but workflow needs to pass it to the script

## 📝 How to Configure GitHub Secrets

### Option 1: Via GitHub Web UI (Recommended)

1. **Navigate to Settings**
   - Go to: `https://github.com/boobootoo2/medbilldozer/settings/secrets/actions`
   - Or: Repository → Settings → Secrets and variables → Actions

2. **Add Secrets**
   - Click "New repository secret"
   - For each secret:
     - Name: `OPENAI_API_KEY`
     - Value: Your actual API key
     - Click "Add secret"

3. **Required Secrets**
   ```
   OPENAI_API_KEY    → Your OpenAI API key
   HF_API_TOKEN      → Your Hugging Face token
   GOOGLE_API_KEY    → Your Google Gemini API key
   ```

### Option 2: Via GitHub CLI

```bash
# Install GitHub CLI first: brew install gh
gh auth login

# Add secrets
gh secret set OPENAI_API_KEY --repo boobootoo2/medbilldozer
# Paste your key when prompted

gh secret set HF_API_TOKEN --repo boobootoo2/medbilldozer
# Paste your token when prompted

gh secret set GOOGLE_API_KEY --repo boobootoo2/medbilldozer
# Paste your key when prompted
```

### Verify Secrets Are Set

```bash
gh secret list --repo boobootoo2/medbilldozer
```

Should show:
```
OPENAI_API_KEY    Updated YYYY-MM-DD
HF_API_TOKEN      Updated YYYY-MM-DD
GOOGLE_API_KEY    Updated YYYY-MM-DD
```

## 🔍 Current Workflow Configuration

### Environment Variables in Workflow

The workflow passes secrets as environment variables:

```yaml
- name: Run benchmarks
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    HF_API_TOKEN: ${{ secrets.HF_API_TOKEN }}
  run: |
    python3 scripts/generate_benchmarks.py --model all
```

### ⚠️ Missing: GOOGLE_API_KEY

**Current Issue**: The Gemini provider needs `GOOGLE_API_KEY` but it's not currently passed in the workflow.

**Fix Required**: Update `.github/workflows/run_benchmarks.yml`:

```yaml
- name: Run benchmarks
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    HF_API_TOKEN: ${{ secrets.HF_API_TOKEN }}
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}  # ADD THIS LINE
  run: |
    python3 scripts/generate_benchmarks.py --model all
```

## 🏃 How API Keys Are Used

### In Local Development

```bash
# Create .env file (copy from .env.example)
cp .env.example .env

# Edit .env and add your keys
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIza...
HF_API_TOKEN=hf_...

# The python-dotenv package loads these automatically
```

### In GitHub Actions

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}  # From GitHub Secrets
  HF_API_TOKEN: ${{ secrets.HF_API_TOKEN }}      # From GitHub Secrets
  GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}  # From GitHub Secrets
```

### In Provider Code

#### OpenAI Provider
```python
# _modules/providers/openai_analysis_provider.py
# Uses OpenAI library which reads OPENAI_API_KEY from environment
client = OpenAI()  # Automatically finds OPENAI_API_KEY
```

#### MedGemma Provider
```python
# _modules/providers/medgemma_hosted_provider.py
self.token = os.getenv("HF_API_TOKEN")  # Reads from environment
```

#### Gemini Provider
```python
# _modules/extractors/gemini_langextractor.py
_client = genai.Client()  # Reads GOOGLE_API_KEY from environment
```

## 🧪 Testing the Workflow

### 1. Manual Trigger (Recommended First Test)

1. Go to: `https://github.com/boobootoo2/medbilldozer/actions`
2. Select "Run Benchmarks" workflow
3. Click "Run workflow" → Select branch → Run
4. Watch the logs to see if API keys work

### 2. Test Locally First

```bash
# Make sure .env has all keys
cat .env | grep -E "OPENAI|GOOGLE|HF_API"

# Test individual providers
python3 scripts/generate_benchmarks.py --model openai
python3 scripts/generate_benchmarks.py --model medgemma
python3 scripts/generate_benchmarks.py --model gemini

# Test all providers
python3 scripts/generate_benchmarks.py --model all
```

### 3. Check Workflow Logs

If workflow fails, check logs:
1. Go to Actions tab
2. Click on the failed workflow run
3. Click on "benchmark" job
4. Look for errors like:
   - `401 Unauthorized` → Wrong API key
   - `ModuleNotFoundError` → Missing dependency
   - `OPENAI_API_KEY not found` → Secret not set

## 🚨 Troubleshooting

### Error: "OPENAI_API_KEY not found"
**Cause**: Secret not configured in GitHub  
**Fix**: Add secret via Settings → Secrets → Actions

### Error: "401 Unauthorized"
**Cause**: Invalid or expired API key  
**Fix**: Generate new key and update secret

### Error: "google-genai not installed"
**Cause**: Missing dependency in requirements-benchmarks.txt  
**Fix**: Already fixed! We added `google-genai>=1.0.0`

### Error: "ModuleNotFoundError: No module named 'google'"
**Cause**: Same as above  
**Fix**: Push latest requirements-benchmarks.txt

### Gemini Provider Fails but Others Work
**Cause**: GOOGLE_API_KEY not passed in workflow  
**Fix**: Update workflow YAML to include GOOGLE_API_KEY in env section

## 📊 Expected Workflow Output

When successful, the workflow will:

1. ✅ Run all provider benchmarks
2. ✅ Generate JSON results in `benchmarks/results/`
3. ✅ Commit results with message: "📊 Update benchmark results"
4. ✅ Push to develop branch
5. ✅ Trigger dashboard update (if deployed to Streamlit Cloud)

Example commit:
```
📊 Update benchmark results

Files changed:
- benchmarks/results/openai_latest.json
- benchmarks/results/medgemma_latest.json
- benchmarks/results/gemini_latest.json
- benchmarks/results/baseline_latest.json
- benchmarks/results/aggregated_metrics.json
```

## 🔒 Security Notes

### Secret Best Practices

1. **Never commit API keys** to the repository
   - `.env` is in `.gitignore` ✅
   - Secrets are in GitHub Settings, not code ✅

2. **Rotate keys periodically**
   - Update secrets every 90 days
   - Revoke old keys after updating

3. **Use minimum permissions**
   - OpenAI: Read-only model access
   - HF: Inference API access only
   - Gemini: Generative AI API only

4. **Monitor usage**
   - Check API usage dashboards
   - Set spending limits
   - Watch for unexpected spikes

### What GitHub Actions Can See

- ✅ Secrets are encrypted at rest
- ✅ Secrets are masked in logs (`***`)
- ✅ Secrets never appear in PR comments
- ❌ Secrets visible to workflow YAML
- ❌ Anyone with push access can modify workflow to expose secrets

## 📈 Monitoring

### Check Workflow Status

```bash
# View recent runs
gh run list --repo boobootoo2/medbilldozer

# View specific run
gh run view <run-id> --repo boobootoo2/medbilldozer

# Watch live run
gh run watch <run-id> --repo boobootoo2/medbilldozer
```

### Check Results

After successful run:
```bash
# Pull latest results
git pull origin develop

# View results
ls -lh benchmarks/results/

# Check latest metrics
cat benchmarks/results/aggregated_metrics.json | jq
```

## 🎯 Next Steps

1. **Set up all three API keys** in GitHub Secrets
2. **Update workflow** to pass GOOGLE_API_KEY
3. **Test manually** from Actions tab
4. **Deploy dashboard** to Streamlit Cloud (see BENCHMARK_DASHBOARD_QUICKSTART.md)
5. **Monitor** daily runs at 2 AM UTC

## 📚 Related Documentation

- [BENCHMARK_DASHBOARD_QUICKSTART.md](BENCHMARK_DASHBOARD_QUICKSTART.md) - Deploy dashboard
- [BENCHMARK_REPORTING_SETUP.md](BENCHMARK_REPORTING_SETUP.md) - Complete setup guide
- [.env.example](../.env.example) - Local environment variables
- [.github/workflows/run_benchmarks.yml](../.github/workflows/run_benchmarks.yml) - Workflow definition

## ❓ FAQ

**Q: Do I need all three API keys?**  
A: Yes, if you want to benchmark all providers. You can run subsets with `--model baseline` (no key needed) or `--model openai` (only OpenAI key needed).

**Q: How much do API calls cost?**  
A: Benchmarks test on ~10 documents. Typical costs:
- OpenAI: ~$0.01 per run
- MedGemma (HF): Free tier available
- Gemini: Free tier available

**Q: Can I disable specific providers?**  
A: Yes! Modify workflow to use `--model openai` instead of `--model all`.

**Q: Where can I see the workflow running?**  
A: `https://github.com/boobootoo2/medbilldozer/actions/workflows/run_benchmarks.yml`

**Q: Can I run benchmarks without API keys?**  
A: Yes! The baseline provider needs no API: `python3 scripts/generate_benchmarks.py --model baseline`
