# Benchmark Snapshot Automation ✅

**Status**: Fully automated snapshot creation on every GitHub Actions benchmark run

## Overview

The medBillDozer repository has a **complete automated benchmark snapshot system** that pushes results to Supabase every time benchmarks run in GitHub Actions.

## How It Works

### 1. Benchmark Execution (run_benchmarks.yml)

**Triggers**:
- ⏰ Daily at 2 AM UTC (scheduled)
- 🔀 Push to `develop` branch
- 🖱️ Manual trigger (workflow_dispatch)

**What it does**:
1. Runs benchmarks for each AI provider (OpenAI, Gemini, Baseline)
2. Generates aggregated metrics JSON files
3. Converts results to monitoring format
4. Uploads results as workflow artifacts

**File**: `.github/workflows/run_benchmarks.yml`

```yaml
- name: Run benchmarks
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
  run: |
    python3 scripts/generate_benchmarks.py --model baseline
    python3 scripts/generate_benchmarks.py --model openai
    python3 scripts/generate_benchmarks.py --model gemini
```

### 2. Snapshot Persistence (benchmark-persist.yml)

**Triggers**:
- ✅ Automatically after `run_benchmarks.yml` completes successfully
- 🖱️ Manual trigger (workflow_dispatch)

**What it does**:
1. Downloads benchmark artifacts from previous workflow
2. Validates results exist
3. **Pushes each result to Supabase** (creates snapshot)
4. Verifies persistence
5. Posts summary to GitHub

**File**: `.github/workflows/benchmark-persist.yml`

```yaml
- name: Push to Supabase
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
  run: |
    for result_file in ./benchmark-artifacts/*_benchmark_results.json; do
      python scripts/push_to_supabase.py \
        --input "$result_file" \
        --environment github-actions \
        --commit-sha "$GITHUB_SHA"
    done
```

### 3. Database Schema (Supabase)

**Two-table design**:

#### `benchmark_transactions` (Append-only log)
- **Every benchmark run** is recorded
- Immutable audit trail
- Full metrics in JSONB format
- Traceability (commit SHA, branch, run ID, triggered by)

#### `benchmark_snapshots` (Version history)
- **Snapshot for each configuration** (model + dataset + prompt + environment)
- Version numbers increment automatically
- Denormalized metrics for fast queries
- `is_current` flag for latest version
- `is_baseline` flag for baseline benchmarks

**Stored Procedure**: `upsert_benchmark_result()`
- Atomically inserts transaction + upserts snapshot
- Automatically increments snapshot version
- Marks previous snapshots as `is_current = FALSE`
- Extracts key metrics for denormalization

**File**: `sql/schema_benchmark_monitoring.sql`

## Snapshot Creation Flow

```
GitHub Actions Run
        ↓
Run Benchmarks (3 providers)
        ↓
Generate JSON Results
        ↓
Upload as Artifacts
        ↓
[TRIGGER: workflow_run completed]
        ↓
Download Artifacts
        ↓
For each result file:
        ↓
    scripts/push_to_supabase.py
        ↓
    Supabase RPC: upsert_benchmark_result()
        ↓
    BEGIN TRANSACTION
        ↓
    1. INSERT INTO benchmark_transactions
       (append-only log entry)
        ↓
    2. Get next snapshot_version
       (SELECT MAX(snapshot_version) + 1)
        ↓
    3. Mark previous as not current
       (UPDATE is_current = FALSE)
        ↓
    4. INSERT INTO benchmark_snapshots
       (new version with is_current = TRUE)
        ↓
    COMMIT TRANSACTION
        ↓
    ✅ Snapshot Created!
```

## What Gets Stored

### Transaction Record (Every Run)
```json
{
  "id": "uuid-...",
  "created_at": "2026-02-05T14:30:00Z",
  "commit_sha": "935d466...",
  "branch_name": "develop",
  "model_version": "gpt-4o-mini",
  "model_provider": "openai",
  "dataset_version": "v2024.02",
  "dataset_size": 50,
  "prompt_version": "v2.1",
  "environment": "github-actions",
  "run_id": "1234567890",
  "triggered_by": "github-actions[bot]",
  "metrics": {
    "precision": 0.87,
    "recall": 0.92,
    "f1": 0.895,
    "latency_ms": 4300,
    "analysis_cost": 0.015,
    "issue_counts": {...},
    "category_performance": {...}
  },
  "duration_seconds": 215.3
}
```

### Snapshot Record (Versioned State)
```json
{
  "id": "uuid-...",
  "snapshot_version": 42,
  "created_at": "2026-02-05T14:30:00Z",
  "model_version": "gpt-4o-mini",
  "dataset_version": "v2024.02",
  "prompt_version": "v2.1",
  "environment": "github-actions",
  "transaction_id": "uuid-...",
  "commit_sha": "935d466...",
  "metrics": {...},
  "precision_score": 0.87,
  "recall_score": 0.92,
  "f1_score": 0.895,
  "latency_ms": 4300,
  "cost_per_analysis": 0.015,
  "is_current": true,
  "is_baseline": false
}
```

## Required GitHub Secrets

To enable snapshot persistence, configure these secrets:

**Repository Settings → Secrets and variables → Actions**

1. **SUPABASE_URL**
   - Your Supabase project URL
   - Format: `https://xxx.supabase.co`

2. **SUPABASE_SERVICE_ROLE_KEY**
   - Service role key (not anon key)
   - Found in: Supabase Dashboard → Settings → API

3. **OPENAI_API_KEY** (for benchmarks)
   - OpenAI API key
   - Format: `sk-proj-...`

4. **GOOGLE_API_KEY** (for benchmarks)
   - Google Gemini API key
   - Format: `AIza...`

## Verification

### Check if Snapshots Are Being Created

#### Option 1: GitHub Actions UI
1. Go to: Repository → Actions
2. Check "Benchmark Persistence" workflow runs
3. Look for "✅ Successfully pushed..." messages

#### Option 2: Supabase Dashboard
```sql
-- Check recent snapshots
SELECT 
  model_version,
  snapshot_version,
  f1_score,
  created_at,
  is_current
FROM benchmark_snapshots
WHERE environment = 'github-actions'
ORDER BY created_at DESC
LIMIT 10;
```

#### Option 3: View Transactions
```sql
-- Check recent benchmark runs
SELECT 
  model_version,
  environment,
  (metrics->>'f1')::NUMERIC as f1_score,
  created_at,
  triggered_by
FROM benchmark_transactions
WHERE environment = 'github-actions'
ORDER BY created_at DESC
LIMIT 10;
```

## Troubleshooting

### Snapshots Not Being Created

**Check 1: Secrets Configured?**
```bash
# In GitHub UI:
Repository → Settings → Secrets → Actions
# Verify SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY exist
```

**Check 2: Benchmark Workflow Succeeded?**
```bash
# In GitHub Actions UI:
Actions → Run Benchmarks → Latest run
# Should show green checkmark
```

**Check 3: Persistence Workflow Triggered?**
```bash
# In GitHub Actions UI:
Actions → Benchmark Persistence
# Should run after "Run Benchmarks" completes
```

**Check 4: Check Logs**
```bash
# In workflow run:
Benchmark Persistence → Push to Supabase
# Look for:
# ✓ Successfully pushed openai_benchmark_results.json
# ✓ Successfully pushed gemini_benchmark_results.json
```

### Common Issues

#### "Supabase secrets not configured"
**Solution**: Add `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` secrets

#### "Artifact download failed"
**Cause**: Benchmark workflow didn't complete or didn't generate artifacts
**Solution**: Check `run_benchmarks.yml` completed successfully

#### "Failed to push to Supabase"
**Causes**:
- Invalid API credentials
- Network timeout
- Schema mismatch

**Debug**:
```bash
# Test locally:
python scripts/push_to_supabase.py \
  --input benchmarks/results/openai_benchmark_results.json \
  --environment local \
  --commit-sha $(git rev-parse HEAD) \
  --triggered-by $(whoami)
```

## Manual Snapshot Creation

To manually create a snapshot (testing/development):

```bash
# 1. Run benchmarks
python scripts/generate_benchmarks.py --model openai

# 2. Convert to monitoring format
python scripts/convert_benchmark_to_monitoring.py \
  --input benchmarks/results/aggregated_metrics_openai.json \
  --output openai_benchmark_results.json \
  --model openai

# 3. Push to Supabase
python scripts/push_to_supabase.py \
  --input openai_benchmark_results.json \
  --environment local \
  --commit-sha $(git rev-parse HEAD) \
  --triggered-by $(whoami)
```

## Snapshot Querying

### Get Latest Snapshot for Each Model
```sql
SELECT * FROM v_latest_benchmarks
ORDER BY f1_score DESC;
```

### Get Snapshot History for a Model
```sql
SELECT 
  snapshot_version,
  f1_score,
  created_at,
  commit_sha,
  is_current
FROM benchmark_snapshots
WHERE model_version = 'gpt-4o-mini'
  AND environment = 'github-actions'
ORDER BY snapshot_version DESC;
```

### Compare Current vs Previous Snapshot
```sql
WITH ranked_snapshots AS (
  SELECT *,
    ROW_NUMBER() OVER (
      PARTITION BY model_version, environment 
      ORDER BY snapshot_version DESC
    ) as rank
  FROM benchmark_snapshots
)
SELECT 
  model_version,
  MAX(CASE WHEN rank = 1 THEN f1_score END) as current_f1,
  MAX(CASE WHEN rank = 2 THEN f1_score END) as previous_f1,
  MAX(CASE WHEN rank = 1 THEN f1_score END) - 
    MAX(CASE WHEN rank = 2 THEN f1_score END) as delta
FROM ranked_snapshots
WHERE rank <= 2
GROUP BY model_version;
```

## Dashboard Integration

The Streamlit benchmark monitoring dashboard (`pages/benchmark_monitoring.py`) automatically:
- Fetches latest snapshots from Supabase
- Displays snapshot version history
- Shows performance trends over time
- Allows checking out specific snapshot versions

**Access**: `http://localhost:8502` or deployed URL

## Automation Summary

✅ **Fully Automated**: Every benchmark run creates a snapshot  
✅ **Version Controlled**: Snapshots numbered sequentially  
✅ **Immutable Log**: All runs preserved in transactions table  
✅ **Time Travel**: Can query any historical snapshot  
✅ **Zero Configuration**: Works automatically with secrets configured  
✅ **Fault Tolerant**: Retry logic + comprehensive error handling  

---

**Status**: ✅ ACTIVE  
**Frequency**: Daily + on code changes + manual triggers  
**Retention**: Unlimited (append-only log)  
**Cost**: ~$0.01 per benchmark run (API costs)
