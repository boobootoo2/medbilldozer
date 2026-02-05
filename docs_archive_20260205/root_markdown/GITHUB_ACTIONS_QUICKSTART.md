# GitHub Actions Monitoring - Quick Start

## 🎯 What This Does

Automatically persist benchmark results to Supabase every time benchmarks run in GitHub Actions.

## ⚡ Quick Setup (5 minutes)

### 1. Get Supabase Credentials

1. Go to <https://app.supabase.com/>
2. **Project Settings** → **API**
3. Copy:
   - **Project URL**
   - **service_role** key (secret key with write access)

### 2. Add GitHub Secrets

**Option A: Using GitHub CLI (recommended)**

```bash
# Run the setup script
./scripts/setup_github_monitoring.sh
```

**Option B: Manual**

1. Go to: `https://github.com/YOUR_USERNAME/medbilldozer/settings/secrets/actions`
2. Add two secrets:
   - `SUPABASE_URL` = `https://your-project.supabase.co`
   - `SUPABASE_SERVICE_ROLE_KEY` = `eyJhbGci...` (the long JWT token)

### 3. Test It

```bash
# Trigger benchmark workflow
gh workflow run run_benchmarks.yml

# Watch the run
gh run watch
```

## 📋 What Happens

```
Run Benchmarks → Convert to Monitoring Format → Upload Artifact
                                                      ↓
                                          Benchmark Persist Workflow
                                                      ↓
                                             Push to Supabase
                                                      ↓
                                          View in Dashboard
```

## ✅ Verification

1. Check workflow ran: `gh run list --workflow=benchmark-persist.yml`
2. Query Supabase:

```sql
SELECT model_version, f1_score, created_at 
FROM benchmark_snapshots 
WHERE is_current = TRUE 
ORDER BY created_at DESC;
```

3. View in dashboard: `make monitoring-dashboard`

## 🔧 Files Updated

- ✅ `.github/workflows/run_benchmarks.yml` - Now uploads artifacts
- ✅ `.github/workflows/benchmark-persist.yml` - Processes multiple models
- ✅ `scripts/convert_benchmark_to_monitoring.py` - Converts format
- ✅ `scripts/setup_github_monitoring.sh` - Automated setup

## 📖 Full Documentation

See: [`docs/GITHUB_ACTIONS_MONITORING_SETUP.md`](./docs/GITHUB_ACTIONS_MONITORING_SETUP.md)

## 🚨 Troubleshooting

**"Invalid API key"**: Use `service_role` key, not `anon` key

**"Workflow not triggering"**: Check workflow name matches in `benchmark-persist.yml` line 4

**"No artifacts"**: Ensure benchmarks ran successfully first

**"Schema errors"**: Re-run the SQL schema in Supabase SQL Editor

## 🎉 That's It!

Benchmarks now automatically persist to Supabase on every run.
