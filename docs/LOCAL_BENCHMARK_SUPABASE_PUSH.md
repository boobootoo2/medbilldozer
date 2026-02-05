# Pushing Local Benchmark Results to Supabase

**Date:** February 5, 2026  
**Issue:** Local benchmark results not automatically pushed to Supabase  
**Solution:** Manual push script for local development workflow

---

## Problem Statement

When running benchmarks **locally** (on your development machine), the results are saved to:
```
benchmarks/results/patient_benchmark_*.json
```

However, these results **do not automatically** appear in Supabase because:

1. ❌ The Supabase persistence workflow (`benchmark-persist.yml`) only runs **after** GitHub Actions completes
2. ❌ It expects benchmark results to be uploaded as **GitHub Actions artifacts**
3. ❌ Local benchmark runs don't create GitHub Actions artifacts
4. ❌ The workflow never triggers for local runs

---

## Workflow Architecture

### GitHub Actions (Automated)
```
┌─────────────────────┐
│ run_benchmarks.yml  │  Runs on: schedule, push to develop
│                     │
│ 1. Run benchmarks   │
│ 2. Upload artifacts │
└──────────┬──────────┘
           │
           │ triggers
           ▼
┌──────────────────────────┐
│ benchmark-persist.yml    │
│                          │
│ 1. Download artifacts    │
│ 2. Convert format        │
│ 3. Push to Supabase      │
└──────────────────────────┘
```

### Local Development (Manual)
```
┌─────────────────────────────┐
│ You run benchmarks locally  │
│                             │
│ $ python3 scripts/          │
│   generate_patient_...py    │
└──────────┬──────────────────┘
           │
           │ saves to
           ▼
┌──────────────────────────┐
│ benchmarks/results/      │
│ patient_benchmark_*.json │
└──────────┬───────────────┘
           │
           │ NO AUTOMATIC PUSH ❌
           │
           │ YOU MUST MANUALLY RUN
           ▼
┌────────────────────────────────┐
│ ./scripts/                     │
│   push_local_benchmarks.sh     │
│                                │
│ 1. Convert to monitoring format│
│ 2. Push to Supabase            │
└────────────────────────────────┘
```

---

## Solution: Manual Push Script

### Quick Start

**Push all available benchmark results:**
```bash
./scripts/push_local_benchmarks.sh
```

**Push specific models:**
```bash
./scripts/push_local_benchmarks.sh baseline medgemma gemini
```

### What It Does

1. ✅ Finds all `patient_benchmark_*.json` files in `benchmarks/results/`
2. ✅ Converts each to monitoring format (using `convert_benchmark_to_monitoring.py`)
3. ✅ Pushes to Supabase with metadata:
   - Current commit SHA
   - Current branch name
   - Your username
   - Tags: `local-run`, `v2-structured-reasoning`, `prompt-enhancement`
   - Notes about the run

### Requirements

**Environment variables in `.env`:**
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

**Python dependencies:**
```bash
pip install supabase python-dotenv
```

---

## Step-by-Step: Local Benchmark → Supabase

### 1. Run Benchmarks Locally
```bash
# Run patient benchmarks for specific model
python3 scripts/generate_patient_benchmarks.py --model medgemma

# Or run for all models
python3 scripts/generate_patient_benchmarks.py --model all
```

**Output files created:**
- `benchmarks/results/patient_benchmark_medgemma.json`
- `benchmarks/results/patient_benchmark_baseline.json`
- etc.

### 2. Verify Results Exist
```bash
ls -lh benchmarks/results/patient_benchmark_*.json
```

### 3. Push to Supabase
```bash
# Push all available results
./scripts/push_local_benchmarks.sh

# Or push specific models
./scripts/push_local_benchmarks.sh medgemma gemini
```

### 4. Verify in Dashboard
Open your Streamlit monitoring dashboard:
```bash
streamlit run pages/benchmark_monitoring.py
```

Check that:
- New entries appear in the timeline
- Commit SHA matches your current commit
- Environment shows "local"
- Tags include `local-run` and `v2-structured-reasoning`

---

## Example Output

```bash
$ ./scripts/push_local_benchmarks.sh baseline

============================================================
Push Local Benchmark Results to Supabase
============================================================

📋 Metadata:
   Commit: 16e1d956
   Branch: develop
   User: jgs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Processing: baseline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Converting to monitoring format...
✅ Conversion successful

☁️  Pushing to Supabase...
✓ Benchmark persisted successfully: 7191ef41-ac6b-4e23-8cf1-e1b57f8de4e1
✅ Successfully pushed baseline results

============================================================
Summary
============================================================
✅ Successful: 1

🎉 Benchmark results have been pushed to Supabase!
View results at your Streamlit dashboard
```

---

## Troubleshooting

### Error: `.env file not found`
**Solution:** Create a `.env` file with Supabase credentials
```bash
cp .env.example .env
# Edit .env and add your SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY
```

### Error: `Supabase credentials not found in .env`
**Solution:** Add the required environment variables:
```bash
echo "SUPABASE_URL=https://your-project.supabase.co" >> .env
echo "SUPABASE_SERVICE_ROLE_KEY=your-key-here" >> .env
```

### Error: `No patient benchmark results found`
**Solution:** Run benchmarks first:
```bash
python3 scripts/generate_patient_benchmarks.py --model baseline
```

### Error: `Conversion failed`
**Check:**
- Is `scripts/convert_benchmark_to_monitoring.py` present?
- Is the input JSON file valid?
- Are all required Python packages installed?

### Error: `Failed to push results`
**Check:**
1. Network connection
2. Supabase credentials are correct
3. Supabase database schema is up to date
4. Check logs for specific error message

---

## Why Two Separate Workflows?

### GitHub Actions Workflow
- **Purpose:** Automated monitoring on main/develop branches
- **Trigger:** Automatic (push, schedule)
- **Use case:** CI/CD, production monitoring
- **Environment:** `github-actions`

### Local Push Script
- **Purpose:** Development and experimentation
- **Trigger:** Manual (you run it)
- **Use case:** Testing prompt changes, model experiments
- **Environment:** `local`

This separation allows you to:
- ✅ Quickly iterate on prompts locally
- ✅ Compare local experiments with production baselines
- ✅ Push results without creating a commit
- ✅ Tag experimental runs for easy filtering

---

## Advanced Usage

### Add Custom Tags
Edit the script to add custom tags:
```bash
--tags "v2-structured-reasoning" "local-run" "my-custom-tag"
```

### Add Custom Notes
```bash
--notes "Testing temperature=0.5 with enhanced examples"
```

### Dry Run (Check Without Pushing)
Modify the script to add `--verify` flag to validation only.

---

## Files Involved

| File | Purpose |
|------|---------|
| `scripts/generate_patient_benchmarks.py` | Runs benchmarks locally |
| `benchmarks/results/patient_benchmark_*.json` | Raw benchmark results |
| `scripts/convert_benchmark_to_monitoring.py` | Converts to monitoring format |
| `scripts/push_to_supabase.py` | Pushes to Supabase with metadata |
| `scripts/push_local_benchmarks.sh` | **Convenience wrapper (NEW)** |
| `.github/workflows/run_benchmarks.yml` | CI/CD benchmark runner |
| `.github/workflows/benchmark-persist.yml` | CI/CD Supabase uploader |

---

## Summary

**Problem:** Local benchmarks don't automatically push to Supabase  
**Root Cause:** Persistence workflow only runs after GitHub Actions  
**Solution:** Manual push script for local development  
**Usage:** `./scripts/push_local_benchmarks.sh [models...]`  
**Status:** ✅ Working (tested Feb 5, 2026)

---

**Author:** GitHub Copilot  
**Created:** February 5, 2026  
**Status:** ✅ Implemented and Tested
