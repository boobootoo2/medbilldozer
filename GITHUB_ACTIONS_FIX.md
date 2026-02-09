# GitHub Actions MedGemma Fix

## Problem
GitHub Actions benchmarks were failing with 400 Bad Request errors from HuggingFace:
```
❌ 400 Client Error: Bad Request for url: https://router.huggingface.co/v1/chat/completions
```

This caused medgemma and medgemma-ensemble models to report:
- 0% domain detection rate
- All metrics at 0.0
- 61/61 errors, 0/61 successes

## Root Cause
The `medgemma_hosted_provider.py` was hardcoded to use HuggingFace's Router endpoint (`https://router.huggingface.co/v1/chat/completions`), but:
1. The Router doesn't support the `google/medgemma-4b-it` model
2. Locally, the system works because it uses a dedicated inference endpoint via `HF_ENDPOINT_BASE`

## Solution

### Code Changes (Already Applied)

1. **Updated `src/medbilldozer/providers/medgemma_hosted_provider.py`**
   - Now checks for `HF_ENDPOINT_BASE` environment variable first
   - Falls back to Router only if `HF_ENDPOINT_BASE` is not set
   - This makes it work with both dedicated endpoints and router

2. **Updated `.github/workflows/run_benchmarks.yml`**
   - Added `HF_ENDPOINT_BASE: ${{ secrets.HF_ENDPOINT_BASE }}` to environment variables

### Required GitHub Setup

**You need to add the `HF_ENDPOINT_BASE` secret to your GitHub repository:**

1. Go to: https://github.com/boobootoo2/medbilldozer/settings/secrets/actions

2. Click **"New repository secret"**

3. Add:
   - **Name:** `HF_ENDPOINT_BASE`
   - **Value:** `https://gzm1kdzim8rqw82w.us-east4.gcp.endpoints.huggingface.cloud`
   
   (This is your HuggingFace dedicated inference endpoint URL)

4. Save the secret

### Verification

After adding the secret, the next GitHub Actions run should:
- ✅ Successfully call MedGemma via your dedicated endpoint
- ✅ Report correct domain detection rates (~63-64%)
- ✅ Show successful analyses instead of errors

### Local Testing
To test locally that it still works:
```bash
export HF_ENDPOINT_BASE="https://gzm1kdzim8rqw82w.us-east4.gcp.endpoints.huggingface.cloud"
python3 scripts/run_benchmarks_v2.py --model medgemma --workers 2
```

### Alternative: Use OpenAI Only in CI
If you don't want to add the secret, you can modify the workflow to skip MedGemma in CI:
```yaml
python3 scripts/run_benchmarks_v2.py --model openai --workers 2
```

But adding the secret is recommended so you get complete benchmark coverage in CI.
