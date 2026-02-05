# 📊 Benchmark Dashboard - Quick Start

## What We Created

A **standalone Streamlit dashboard** for visualizing benchmark metrics - separate from your main app!

## 🚀 Running Locally

### Your Benchmark Dashboard
```bash
# Port 8502 (benchmark dashboard)
python3 -m streamlit run benchmark_dashboard.py --server.port 8502
```
**Access at:** http://localhost:8502

### Your Main App
```bash
# Port 8501 (main medBillDozer app)
streamlit run app.py
```
**Access at:** http://localhost:8501

**Now both can run simultaneously!** ✅

## 🎯 Dashboard Features

The benchmark dashboard shows:

- ✅ **Performance Metrics**: Precision, Recall, F1 Score for all models
- ✅ **Interactive Visualizations**: Charts comparing speed vs accuracy
- ✅ **Detailed Breakdowns**: Per-model statistics and individual document results
- ✅ **Smart Filters**: Select which models to compare
- ✅ **Real-time Updates**: Reflects latest benchmark results

## 📁 Files Created

1. **`benchmark_dashboard.py`** - Standalone dashboard app (runs on port 8502)
2. **`.github/workflows/run_benchmarks.yml`** - GitHub Actions for automation
3. **`BENCHMARK_REPORTING_SETUP.md`** - Complete deployment guide

## 🌐 Deploying to Streamlit Cloud

### Step 1: Push to GitHub
```bash
git add benchmark_dashboard.py .github/workflows/run_benchmarks.yml
git commit -m "Add standalone benchmark dashboard"
git push
```

### Step 2: Deploy Dashboard
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New App"**
3. Select:
   - **Repository**: `boobootoo2/medbilldozer`
   - **Branch**: `develop` (or `main`)
   - **File**: `benchmark_dashboard.py`
4. Click **"Deploy"**

### Step 3: Access Your Dashboard
You'll get a URL like: `https://medbilldozer-benchmarks.streamlit.app`

**Result**: Separate dashboard that's always live! 🎉

## ⚙️ GitHub Actions Setup

The workflow automatically:
- ✅ Runs benchmarks daily at 2am UTC
- ✅ Runs on manual trigger
- ✅ Runs when you change providers
- ✅ Commits results to repo
- ✅ Dashboard updates automatically

### To Enable:
1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Add secrets:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `HF_API_TOKEN` - Hugging Face token (optional)
3. Done! Benchmarks run automatically

## 🎨 Current Dashboard State

**Running on:** http://localhost:8502  
**Status:** ✅ Active (fixed deprecation warnings)  
**Data source:** `benchmarks/results/*.json`

## 🔄 Workflow

```
Generate Benchmarks → JSON Results → Dashboard Displays
     (Manual/CI)     →   (Committed)  →  (Auto-updates)
```

### Local Development
```bash
# 1. Make changes to providers
vim _modules/providers/openai_analysis_provider.py

# 2. Run benchmarks
python3 scripts/generate_benchmarks.py --model all

# 3. View results in dashboard (auto-refreshes)
# Dashboard at: http://localhost:8502
```

### Production Flow
```bash
# 1. Push changes
git push

# 2. GitHub Actions runs benchmarks automatically

# 3. Results committed to repo

# 4. Streamlit Cloud dashboard updates live

# 5. View at: https://your-app.streamlit.app
```

## 📊 What You See

### Main Comparison
- Side-by-side metrics for all models
- Precision, Recall, F1 Score
- Latency comparisons

### Visualizations
- Precision vs Recall scatter plot
- F1 Score bar chart
- Speed comparison
- Cost/benefit analysis

### Detailed Per-Model
- Full statistics
- Individual document results
- Token usage (if available)
- Extraction metrics

## 🛠️ Configuration

### Change Port (if needed)
```bash
# Use any available port (example with 8503)
python3 -m streamlit run benchmark_dashboard.py --server.port 8503
```

### Update Benchmark Schedule
Edit `.github/workflows/run_benchmarks.yml`:
```yaml
schedule:
  - cron: '0 2 * * *'  # Change to your preferred time
```

## 💡 Pro Tips

### Tip 1: Run Both Apps Together
```bash
# Terminal 1: Main app
streamlit run app.py

# Terminal 2: Benchmarks
python3 -m streamlit run benchmark_dashboard.py --server.port 8502
```

### Tip 2: Quick Benchmark Check
```bash
# Run just one model to test
python3 scripts/generate_benchmarks.py --model baseline

# View immediately in dashboard (auto-refresh)
```

### Tip 3: Historical Tracking
```bash
# View benchmark changes over time
git log --oneline benchmarks/results/

# Compare specific runs
git diff [commit] benchmarks/results/aggregated_metrics.json
```

## 🎯 Next Steps

1. ✅ **Dashboard is running** - http://localhost:8502
2. ⏭️ **Deploy to Streamlit Cloud** - Get permanent URL
3. ⏭️ **Set up GitHub Actions** - Automate benchmarks
4. ⏭️ **Remove README updates** - Clean up generate_benchmarks.py

## 📚 Full Documentation

See `BENCHMARK_REPORTING_SETUP.md` for:
- Detailed architecture
- Advanced configuration
- Database integration
- Custom metrics
- Troubleshooting

## ✅ Summary

**What you have now:**

| Feature | Status |
|---------|--------|
| Standalone dashboard | ✅ Running on port 8502 |
| Separates from main app | ✅ No conflicts |
| Interactive visualizations | ✅ Multiple charts |
| Model comparison | ✅ All models shown |
| GitHub Actions workflow | ✅ Ready to deploy |
| Documentation | ✅ Complete guide |

**No more README pollution!** 🎉

The dashboard is your new benchmark reporting home.
