# API Keys Quick Setup

## 🎯 What You Need

The benchmark workflow needs **3 API keys** configured as GitHub Secrets:

| Secret Name | Provider | Get Key From | Format |
|-------------|----------|--------------|--------|
| `OPENAI_API_KEY` | OpenAI GPT | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | `sk-proj-...` |
| `HF_API_TOKEN` | Hugging Face | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) | `hf_...` |
| `GOOGLE_API_KEY` | Google Gemini | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) | `AIza...` |

## ⚡ Quick Setup (3 Steps)

### 1. Get Your API Keys
- Visit the links above
- Create/copy API keys
- Save them somewhere safe temporarily

### 2. Add to GitHub Secrets
Go to: `https://github.com/boobootoo2/medbilldozer/settings/secrets/actions`

Or: **Repository → Settings → Secrets and variables → Actions**

Click **"New repository secret"** for each:
```
Name: OPENAI_API_KEY
Value: [paste your OpenAI key]
→ Add secret

Name: HF_API_TOKEN  
Value: [paste your Hugging Face token]
→ Add secret

Name: GOOGLE_API_KEY
Value: [paste your Gemini key]
→ Add secret
```

### 3. Test the Workflow
Go to: `https://github.com/boobootoo2/medbilldozer/actions`

Click **"Run Benchmarks"** → **"Run workflow"** → **"Run workflow"**

Watch it run! Should complete in ~2-3 minutes. ✅

## 📊 Current Workflow Status

The workflow is configured to:
- ✅ Use Python 3.11 (fixed compatibility)
- ✅ Install minimal dependencies (google-genai included)
- ✅ Pass all 3 API keys as environment variables
- ✅ Run all provider benchmarks
- ✅ Commit results back to repo

## 🔍 Verify It's Working

After workflow runs successfully:

```bash
# Pull latest results
git pull origin develop

# Check for new benchmark files
ls -lh benchmarks/results/

# Should see:
# - openai_latest.json
# - medgemma_latest.json  
# - gemini_latest.json
# - baseline_latest.json
# - aggregated_metrics.json
```

## 🚨 Common Issues

### "Secret not found"
→ You haven't added the secret yet. Go to Settings → Secrets → Actions

### "401 Unauthorized"  
→ Invalid API key. Check you copied it correctly

### "google-genai not installed"
→ Old requirements file. Commit and push latest `requirements-benchmarks.txt`

### Only 2 providers run (Gemini fails)
→ GOOGLE_API_KEY not set. Add it to GitHub Secrets

## 💰 Cost Estimate

Running benchmarks on ~10 test documents:
- **OpenAI**: ~$0.01 per run (GPT-4o-mini)
- **Hugging Face**: Free tier available (Inference API)
- **Gemini**: Free tier available (1.5 Flash)
- **Baseline**: $0 (no API needed)

Daily runs = ~$0.30/month maximum

## 🎓 Where to Learn More

- **Full setup guide**: `docs/GITHUB_ACTIONS_SETUP.md`
- **Dashboard deployment**: `BENCHMARK_DASHBOARD_QUICKSTART.md`
- **Local .env setup**: `.env.example`

## ✅ Checklist

- [ ] Got all 3 API keys
- [ ] Added secrets to GitHub (Settings → Secrets → Actions)
- [ ] Committed latest workflow file (`git push`)
- [ ] Tested manual workflow run
- [ ] Verified results in `benchmarks/results/`
- [ ] Deployed dashboard to Streamlit Cloud (optional)

---

**Next**: See `BENCHMARK_DASHBOARD_QUICKSTART.md` to deploy the interactive dashboard! 🚀
