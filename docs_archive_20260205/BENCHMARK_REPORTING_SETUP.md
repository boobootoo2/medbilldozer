# 📊 Benchmark Reporting Service Architecture

## Overview

The benchmark reporting has been separated from the main application into a **standalone Streamlit dashboard**. This allows:

- ✅ Independent deployment to Streamlit Cloud
- ✅ No README pollution from repeated benchmark updates
- ✅ Real-time, interactive benchmark visualization
- ✅ Automatic metrics collection via GitHub Actions
- ✅ Historical tracking and comparisons

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    BENCHMARK PIPELINE                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌──────────────────────┐
                    │  generate_benchmarks │ (Local or CI/CD)
                    │      .py             │
                    └──────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │    JSON Results: benchmarks/results/    │
        │  - aggregated_metrics.json              │
        │  - aggregated_metrics_baseline.json     │
        │  - aggregated_metrics_openai.json       │
        │  - aggregated_metrics_medgemma.json     │
        └─────────────────────────────────────────┘
                              ↓
            ┌─────────────────────────────────┐
            │  Commit to Repository           │
            │  (GitHub Actions or Manual)     │
            └─────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │  Streamlit Cloud Deployment             │
        │  - benchmark_dashboard.py               │
        │  - Reads JSON files from repo            │
        │  - Generates interactive visualizations │
        │  - Live link: streamlit.app URL         │
        └─────────────────────────────────────────┘
```

## Quick Start

### 1. Local Testing

Run the benchmark dashboard locally first:

```bash
# Generate fresh benchmarks
python3 scripts/generate_benchmarks.py --model all

# View the dashboard
streamlit run benchmark_dashboard.py
```

This opens at `http://localhost:8501`

### 2. Deploy to Streamlit Cloud

**Option A: Automatic (Recommended)**

1. Push to your GitHub repo (main branch)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New App"
4. Connect to GitHub repo
5. Select:
   - Repository: `your-username/medbilldozer`
   - Branch: `main` or `develop`
   - File path: `benchmark_dashboard.py`
6. Click "Deploy"

**Option B: Manual**

```bash
# Requires Streamlit community account
streamlit deploy --logger.level=debug
```

### 3. Automate Benchmarks with GitHub Actions

The workflow `.github/workflows/run_benchmarks.yml` automatically:

- ✅ Runs benchmarks on schedule (daily at 2am UTC)
- ✅ Runs on manual trigger (`workflow_dispatch`)
- ✅ Runs on changes to providers or benchmark script
- ✅ Commits results back to repo
- ✅ Comments on PRs with benchmark results

**To set up:**

1. Add secrets to GitHub:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `HF_API_TOKEN` - Hugging Face token (optional)

2. Workflow runs automatically!

## File Structure

```
medbilldozer/
├── benchmark_dashboard.py          ← NEW: Standalone Streamlit app
├── scripts/
│   └── generate_benchmarks.py       ← Generate results (no more README updates)
├── benchmarks/
│   ├── inputs/                      ← Test documents
│   ├── expected_outputs/            ← Ground truth annotations
│   └── results/                     ← JSON results (committed to repo)
│       ├── aggregated_metrics.json
│       ├── aggregated_metrics_baseline.json
│       ├── aggregated_metrics_openai.json
│       └── aggregated_metrics_medgemma.json
├── .github/
│   └── workflows/
│       └── run_benchmarks.yml       ← NEW: GitHub Actions workflow
└── .streamlit/
    └── config.toml                  ← Streamlit configuration
```

## Dashboard Features

### 🎯 Main Comparison View
- Side-by-side metrics for all models
- Performance metrics (Precision, Recall, F1)
- Efficiency metrics (Latency, Success rate)

### 📈 Visualizations
- **Precision vs Recall**: Shows accuracy trade-offs
- **F1 Score**: Overall effectiveness
- **Speed Comparison**: Latency per document
- **Speed vs Accuracy**: Cost/benefit trade-off

### 🔍 Detailed Breakdown
- Per-model tabs with full statistics
- Individual document results
- Token usage (if available)
- Extraction statistics

### 💡 Smart Recommendations
- When to use each provider
- Performance characteristics
- Cost/benefit analysis

## Integration with CI/CD

### GitHub Actions Workflow

The workflow runs:

```yaml
on:
  # Daily at 2am UTC
  schedule:
    - cron: '0 2 * * *'
  
  # Manual trigger via UI
  workflow_dispatch:
  
  # On provider/benchmark changes
  push:
    branches:
      - develop
    paths:
      - '_modules/providers/**'
      - 'scripts/generate_benchmarks.py'
      - 'benchmarks/inputs/**'
```

### Result:
- ✅ Benchmarks run automatically
- ✅ Results committed to repo
- ✅ Dashboard updates live
- ✅ PR comments with metrics

## Configuration

### Streamlit Config (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"

[server]
port = 8501
headless = true
runOnSave = true
```

### Environment Variables

For running benchmarks:

```bash
export OPENAI_API_KEY="sk-..."
export HF_API_TOKEN="hf_..."
```

## Usage Examples

### Example 1: Local Development

```bash
# Make provider changes
# vim _modules/providers/openai_analysis_provider.py

# Run benchmarks to see impact
python3 scripts/generate_benchmarks.py --model all

# View results interactively
streamlit run benchmark_dashboard.py
```

### Example 2: CI/CD Automation

```bash
# Push changes
git push origin develop

# GitHub Actions automatically:
# 1. Installs dependencies
# 2. Runs benchmarks
# 3. Commits results
# 4. Dashboard updates live

# View at: https://your-app.streamlit.app
```

### Example 3: Scheduled Reporting

```bash
# Every day at 2am UTC:
# 1. Benchmarks run automatically
# 2. Results committed to repo
# 3. Dashboard reflects new metrics
# 4. You can track trends over time
```

## Performance Tracking

### Viewing Historical Changes

```bash
# See benchmark commits
git log --oneline benchmarks/results/

# Compare specific runs
git diff [commit1] [commit2] benchmarks/results/aggregated_metrics.json

# View changes over time
# git log -p benchmarks/results/
```

### Analyzing Trends

The dashboard can be extended to show:
- Metrics over time (line charts)
- Provider performance trends
- Issue detection improvements
- Cost/performance ratio tracking

## Troubleshooting

### Dashboard won't load

```bash
# Check if results exist
ls benchmarks/results/

# Generate if missing
python3 scripts/generate_benchmarks.py --model all

# Run dashboard
streamlit run benchmark_dashboard.py
```

### Streamlit Cloud deployment fails

```bash
# Check requirements
pip freeze > requirements-frozen.txt

# Ensure plotly is installed
pip install plotly pandas streamlit
```

### GitHub Actions workflow fails

1. Check secrets are set:
   - `Settings → Secrets and variables → Actions`
   - Verify `OPENAI_API_KEY` is set

2. Check API keys are valid

3. View workflow run:
   - `Actions → Run Benchmarks → Latest run`

## Advanced: Custom Metrics

To add custom metrics to the dashboard:

1. Modify `generate_benchmarks.py` to collect new data
2. Update result JSON structure
3. Add visualization to `benchmark_dashboard.py`
4. Commit and push - dashboard updates automatically

## Advanced: Database Integration

For larger-scale tracking, consider:

1. **Supabase** (PostgreSQL backend)
   - Store historical results
   - Query trends over time
   - Build time-series charts

2. **MongoDB** (Document storage)
   - Store full result objects
   - Query by model/date/metric
   - Build custom dashboards

3. **BigQuery** (Analytics)
   - Aggregate results across runs
   - Complex analysis
   - Cost tracking

## FAQ

**Q: Why separate the dashboard?**
A: Avoids polluting the README with repeated updates. Dashboard is always live and up-to-date.

**Q: Can I run benchmarks locally?**
A: Yes! `python3 scripts/generate_benchmarks.py --model all` - dashboard reads the local results.

**Q: How often do benchmarks run?**
A: By default, daily at 2am UTC. Configure in `.github/workflows/run_benchmarks.yml`

**Q: Can I deploy the dashboard privately?**
A: Yes! Deploy to your own server, AWS, GCP, or any platform supporting Streamlit.

**Q: What if results are too large?**
A: The JSON format is efficient. For 1000+ documents, consider database storage or sampling.

## Next Steps

1. ✅ Set up GitHub Actions secrets
2. ✅ Deploy dashboard to Streamlit Cloud
3. ✅ Configure scheduled benchmarks
4. ✅ Monitor dashboard over time
5. ✅ Track performance improvements

## Related Documentation

- `PROVIDER_IMPROVEMENTS_COMPLETE.md` - Provider implementation details
- `DETAILED_PROVIDER_COMPARISON.md` - Performance analysis
- `scripts/generate_benchmarks.py` - Benchmark code
- `.github/workflows/run_benchmarks.yml` - CI/CD workflow
