# Benchmark Workflow - Quick Start Guide

## Generate & Upload Benchmarks to Dashboard

### Step 1: Run Benchmarks for All Models

```bash
python3 scripts/generate_benchmarks.py --model all
```

This runs benchmarks on:
- ✅ MedGemma (medgemma)
- ✅ OpenAI GPT-4 (openai)
- ✅ Google Gemini (gemini) - if GOOGLE_API_KEY is set
- ✅ Heuristic Baseline (baseline)

Results saved to: `benchmarks/results/aggregated_metrics_*.json`

### Step 2: Convert & Upload to Supabase

**Quick Command (all models at once):**

```bash
# Get current git commit
COMMIT=$(git rev-parse --short HEAD)

# Convert and upload each model
for MODEL in medgemma openai baseline; do
  python3 scripts/convert_benchmark_to_monitoring.py \
    --input benchmarks/results/aggregated_metrics_${MODEL}.json \
    --output /tmp/${MODEL}_monitoring.json \
    --model $MODEL
  
  python3 scripts/push_to_supabase.py \
    --input /tmp/${MODEL}_monitoring.json \
    --environment local \
    --commit-sha $COMMIT \
    --branch-name develop \
    --triggered-by "manual-benchmark"
done
```

### Step 3: View in Dashboard

```bash
# Start dashboard (if not already running)
python3 -m streamlit run pages/benchmark_monitoring.py --server.port 8502
```

Open: http://localhost:8502

## Individual Model Workflow

### Just One Model

```bash
# 1. Run benchmark
python3 scripts/generate_benchmarks.py --model openai

# 2. Convert
python3 scripts/convert_benchmark_to_monitoring.py \
  --input benchmarks/results/aggregated_metrics_openai.json \
  --output /tmp/openai_monitoring.json \
  --model openai

# 3. Upload
python3 scripts/push_to_supabase.py \
  --input /tmp/openai_monitoring.json \
  --environment local \
  --commit-sha $(git rev-parse --short HEAD) \
  --branch-name develop \
  --triggered-by "manual-test"
```

## Environment Options

When uploading, you can specify the environment:

- `local` - Local development testing
- `staging` - Staging environment
- `production` - Production deployment
- `github-actions` - Automated CI/CD runs

```bash
# Production example
python3 scripts/push_to_supabase.py \
  --input /tmp/openai_monitoring.json \
  --environment production \
  --commit-sha $(git rev-parse --short HEAD) \
  --branch-name main \
  --triggered-by "release-v1.2"
```

## Verify Uploads

Check what's in the database:

```bash
python3 scripts/check_snapshots.py
```

## Dashboard Features

Once uploaded, you can:

1. **Current Snapshot** - See latest metrics for all models
2. **Performance Trends** - Track metrics over time
3. **Model Comparison** - Compare models side-by-side
4. **Regression Detection** - Auto-detect performance drops
5. **Snapshot History** - View and checkout older versions

## Makefile Shortcuts

Add to your `Makefile`:

```makefile
.PHONY: benchmark-all benchmark-upload

benchmark-all:
\t@echo "Running benchmarks for all models..."
\tpython3 scripts/generate_benchmarks.py --model all

benchmark-upload:
\t@echo "Uploading benchmarks to Supabase..."
\t@COMMIT=$$(git rev-parse --short HEAD); \
\tfor MODEL in medgemma openai baseline; do \
\t\tpython3 scripts/convert_benchmark_to_monitoring.py \
\t\t\t--input benchmarks/results/aggregated_metrics_$${MODEL}.json \
\t\t\t--output /tmp/$${MODEL}_monitoring.json \
\t\t\t--model $$MODEL; \
\t\tpython3 scripts/push_to_supabase.py \
\t\t\t--input /tmp/$${MODEL}_monitoring.json \
\t\t\t--environment local \
\t\t\t--commit-sha $$COMMIT \
\t\t\t--branch-name develop \
\t\t\t--triggered-by "make-benchmark"; \
\tdone

benchmark-cycle: benchmark-all benchmark-upload
\t@echo "✅ Full benchmark cycle complete!"
```

Then use:

```bash
make benchmark-cycle
```

## Troubleshooting

### Missing API Keys

If you see "Skipping Gemini (GOOGLE_API_KEY not set)":

```bash
# Add to .env file
GOOGLE_API_KEY=your_key_here
```

### Supabase Connection Errors

Check your `.env` file has:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
```

### Dashboard Not Updating

1. Clear Streamlit cache: Press `C` in the dashboard
2. Restart dashboard: `pkill -f streamlit && python3 -m streamlit run pages/benchmark_monitoring.py --server.port 8502`

### Check Uploads

```bash
# Verify snapshots
python3 scripts/check_snapshots.py

# Check for specific model
python3 scripts/check_snapshots.py | grep "openai-v1.0"
```

## Automated CI/CD

The GitHub Actions workflow (`.github/workflows/benchmark-persist.yml`) automatically:

1. Runs benchmarks on every push to `main` or `develop`
2. Converts results to monitoring format
3. Uploads to Supabase
4. Creates snapshot versions

No manual intervention needed! 🚀

---

**Quick Reference:**

| Task | Command |
|------|---------|
| Run all benchmarks | `python3 scripts/generate_benchmarks.py --model all` |
| Run single model | `python3 scripts/generate_benchmarks.py --model openai` |
| Convert results | `python3 scripts/convert_benchmark_to_monitoring.py --input FILE --output OUT --model NAME` |
| Upload to Supabase | `python3 scripts/push_to_supabase.py --input FILE --environment ENV --commit-sha SHA` |
| View dashboard | `python3 -m streamlit run pages/benchmark_monitoring.py --server.port 8502` |
| Check database | `python3 scripts/check_snapshots.py` |

---

**Last Updated**: 2026-02-03  
**Dashboard**: http://localhost:8502
