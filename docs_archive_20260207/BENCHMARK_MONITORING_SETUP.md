# Benchmark Monitoring Setup Guide

**Quick Start Guide for Setting Up ML Benchmark Persistence**

---

## 📋 Prerequisites

- Supabase account ([sign up here](https://supabase.com))
- GitHub repository with Actions enabled
- Python 3.9+
- Streamlit for dashboard

---

## 🚀 Quick Start (15 minutes)

### Step 1: Create Supabase Project (3 min)

1. Go to [https://supabase.com](https://supabase.com)
2. Click "New Project"
3. Fill in:
   - **Name:** `medbilldozer-benchmarks`
   - **Database Password:** (generate strong password)
   - **Region:** (closest to your CI/CD runners)
4. Wait for project to provision
5. Copy your project URL and keys:
   - Project URL: `https://xxxxx.supabase.co`
   - Anon/Public Key: `eyJhbG...` (for dashboard)
   - Service Role Key: `eyJhbG...` (for CI/CD - keep secret!)

### Step 2: Initialize Database Schema (2 min)

1. In Supabase dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy contents of `sql/schema_benchmark_monitoring.sql`
4. Paste into editor
5. Click "Run" (bottom right)
6. Verify success message

**Verify:**
```sql
-- Run this query to confirm tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('benchmark_transactions', 'benchmark_snapshots');
```

Should return 2 rows.

### Step 3: Configure GitHub Secrets (2 min)

1. Go to your GitHub repo
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add two secrets:

   **Secret 1:**
   - Name: `SUPABASE_URL`
   - Value: Your project URL (e.g., `https://xxxxx.supabase.co`)

   **Secret 2:**
   - Name: `SUPABASE_SERVICE_ROLE_KEY`
   - Value: Your service role key (the long JWT token)

### Step 4: Install Python Dependencies (1 min)

Add to your `requirements.txt`:

```txt
# Benchmark persistence
supabase==2.3.0
python-dotenv==1.0.0

# Dashboard
streamlit==1.31.0
plotly==5.18.0
pandas==2.2.0
```

Install locally:
```bash
pip install -r requirements.txt
```

### Step 5: Test Local Push (3 min)

1. Create a test benchmark result:

```bash
cat > test_benchmark_results.json << EOF
{
  "model_version": "test-v1.0",
  "dataset_version": "test-set-v1",
  "prompt_version": "test-prompt-v1",
  "model_provider": "openai",
  "metrics": {
    "precision": 0.91,
    "recall": 0.88,
    "f1": 0.895,
    "latency_ms": 412,
    "analysis_cost": 0.0042
  }
}
EOF
```

2. Set environment variables:

```bash
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
```

3. Run push script:

```bash
python scripts/push_to_supabase.py \
  --input test_benchmark_results.json \
  --environment local \
  --commit-sha $(git rev-parse HEAD) \
  --triggered-by $(whoami) \
  --verify
```

4. You should see:
```
✓ Benchmark persisted successfully: <uuid>
✓ Verification passed: Transaction <uuid> exists
SUCCESS: Benchmark results persisted to Supabase
```

### Step 6: Verify in Supabase (1 min)

Go to Supabase dashboard → **Table Editor**:

1. Open `benchmark_transactions` table
2. You should see 1 row with your test data
3. Open `benchmark_snapshots` table
4. You should see 1 row with the same data

### Step 7: Launch Dashboard (3 min)

1. Create `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key"
```

2. Add to `.gitignore`:
```
.streamlit/secrets.toml
```

3. Set environment variables (alternative to secrets.toml):
```bash
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_ANON_KEY="your-anon-key"
```

4. Launch dashboard:
```bash
streamlit run pages/benchmark_monitoring.py
```

5. Open browser to `http://localhost:8501`
6. You should see your test data!

---

## 🔧 CI/CD Integration

### Option A: Add to Existing Workflow

Add this step to your benchmark workflow:

```yaml
- name: Push to Supabase
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
  run: |
    python scripts/push_to_supabase.py \
      --input benchmark_results.json \
      --environment github-actions \
      --commit-sha ${{ github.sha }} \
      --branch-name ${{ github.ref_name }} \
      --run-id ${{ github.run_id }} \
      --triggered-by ${{ github.actor }}
```

### Option B: Separate Workflow

Use the provided `.github/workflows/benchmark-persist.yml`:

1. Update the trigger to match your benchmark workflow name
2. Ensure benchmark results are saved as artifacts
3. Commit and push

---

## 📊 Dashboard Configuration

### Environment Variables

Create `.env` file (for local development):

```bash
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Optional: Dashboard customization
STREAMLIT_THEME_PRIMARY_COLOR="#1f77b4"
STREAMLIT_THEME_BACKGROUND_COLOR="#ffffff"
```

### Streamlit Cloud Deployment

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repo
3. Set main file: `clinical_performance.py` or `pages/production_stability.py`
4. Add secrets in Streamlit Cloud dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
5. Deploy!

---

## 🧪 Testing Your Setup

### Test 1: Manual Push

```bash
python scripts/push_to_supabase.py \
  --input test_benchmark_results.json \
  --environment local \
  --commit-sha abc123 \
  --triggered-by manual-test
```

**Expected:** Success message with transaction ID

### Test 2: Query Latest Snapshots

In Supabase SQL Editor:

```sql
SELECT * FROM v_latest_benchmarks;
```

**Expected:** Your test data appears

### Test 3: Check Regression Detection

```sql
-- Set baseline
UPDATE benchmark_snapshots
SET is_baseline = TRUE
WHERE model_version = 'test-v1.0';

-- Insert lower-performing run
SELECT upsert_benchmark_result(
  'abc124',
  'develop',
  'test-v1.0',
  'openai',
  'test-set-v1',
  100,
  'test-prompt-v1',
  'local',
  'test-run-2',
  'test-user',
  '{"precision": 0.85, "recall": 0.82, "f1": 0.835, "latency_ms": 420, "analysis_cost": 0.0043}'::JSONB,
  30.0,
  ARRAY['test'],
  'Test regression detection'
);

-- Check for regression (5% threshold)
SELECT * FROM detect_regression('test-v1.0', 0.05);
```

**Expected:** `is_regression = TRUE` (F1 dropped from 0.895 to 0.835)

### Test 4: Dashboard Load

```bash
streamlit run pages/production_stability.py
```

**Expected:** 
- Dashboard loads without errors
- "Current Snapshot" tab shows your test data
- Charts render correctly

---

## 🔐 Security Best Practices

### ✅ DO

- Use **service role key** for CI/CD (write access)
- Use **anon key** for dashboard (read-only)
- Store keys in GitHub Secrets, never in code
- Enable Row Level Security (RLS) in production
- Use environment variables for local development
- Add `.env` and `secrets.toml` to `.gitignore`

### ❌ DON'T

- Commit API keys to Git
- Share service role key publicly
- Use service role key in frontend code
- Expose database credentials in logs

### Optional: Enable RLS

Uncomment RLS policies in `schema_benchmark_monitoring.sql`:

```sql
ALTER TABLE benchmark_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE benchmark_snapshots ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY "Service role has full access to transactions"
  ON benchmark_transactions FOR ALL TO service_role USING (true);

-- Allow authenticated users read-only access
CREATE POLICY "Authenticated users can read transactions"
  ON benchmark_transactions FOR SELECT TO authenticated USING (true);
```

---

## 🐛 Troubleshooting

### Issue: "Could not connect to Supabase"

**Check:**
1. Environment variables are set correctly
2. Supabase project is running (check dashboard)
3. URL has `https://` prefix
4. No trailing slashes in URL

**Fix:**
```bash
echo $SUPABASE_URL
# Should output: https://xxxxx.supabase.co (no trailing slash)
```

### Issue: "Permission denied" when pushing

**Cause:** Using anon key instead of service role key

**Fix:** Ensure `SUPABASE_SERVICE_ROLE_KEY` is set correctly in CI/CD

### Issue: "Function upsert_benchmark_result does not exist"

**Cause:** Schema not fully applied

**Fix:** Re-run the schema SQL in Supabase SQL Editor

### Issue: Dashboard shows "No data"

**Check:**
1. Data exists in `benchmark_snapshots` table
2. Filters in sidebar aren't too restrictive
3. `is_active = TRUE` for snapshots
4. Environment variables are correct

**Debug query:**
```sql
SELECT COUNT(*) FROM benchmark_snapshots WHERE is_active = TRUE;
```

### Issue: GitHub Action fails to push

**Check workflow logs for:**
- `benchmark_results.json` exists
- Environment variables are set
- Network connectivity to Supabase

**Debug:**
```yaml
- name: Debug environment
  run: |
    echo "Checking environment..."
    echo "SUPABASE_URL is set: $([ ! -z "$SUPABASE_URL" ] && echo 'yes' || echo 'no')"
    ls -la ./benchmark-artifacts/
```

---

## 📈 Performance Optimization

### For Large Datasets (>10K runs)

#### 1. Add Partitioning

```sql
-- Partition by month
CREATE TABLE benchmark_transactions_2026_02 
PARTITION OF benchmark_transactions
FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
```

#### 2. Create Materialized View

```sql
CREATE MATERIALIZED VIEW mv_daily_stats AS
SELECT 
  DATE_TRUNC('day', created_at) AS date,
  model_version,
  AVG((metrics->>'f1')::NUMERIC) AS avg_f1,
  COUNT(*) AS run_count
FROM benchmark_transactions
GROUP BY DATE_TRUNC('day', created_at), model_version;

-- Refresh nightly
CREATE EXTENSION IF NOT EXISTS pg_cron;
SELECT cron.schedule('refresh-daily-stats', '0 1 * * *', 
  'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_stats');
```

#### 3. Archive Old Data

```sql
-- Archive runs older than 1 year
CREATE TABLE benchmark_transactions_archive AS
SELECT * FROM benchmark_transactions
WHERE created_at < NOW() - INTERVAL '1 year';

DELETE FROM benchmark_transactions
WHERE created_at < NOW() - INTERVAL '1 year';
```

---

## 🎯 Next Steps

Now that your system is running:

1. ✅ **Set a baseline:** Mark your best model as baseline for regression detection
2. ✅ **Configure alerts:** Set up Slack/email notifications for regressions
3. ✅ **Add tags:** Use tags for experiment tracking
4. ✅ **Document versions:** Keep a changelog of model/prompt/dataset versions
5. ✅ **Schedule reviews:** Weekly review of dashboard for anomalies

### Set Baseline Example

```sql
UPDATE benchmark_snapshots
SET is_baseline = TRUE
WHERE model_version = 'medgemma-v1.2'
  AND environment = 'production';
```

### Add Experiment Tags

```bash
python scripts/push_to_supabase.py \
  --input results.json \
  --environment local \
  --commit-sha $(git rev-parse HEAD) \
  --tags experiment-42 temperature-0.7 prompt-variation-a \
  --notes "Testing new prompt template"
```

---

## 📚 Additional Resources

- [Architecture Documentation](BENCHMARK_PERSISTENCE_ARCHITECTURE.md)
- [Supabase Python Client Docs](https://supabase.com/docs/reference/python/introduction)
- [Streamlit Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/get-started)
- [GitHub Actions Security](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## ✅ Setup Checklist

Use this checklist to track your progress:

- [ ] Supabase project created
- [ ] Database schema applied
- [ ] GitHub secrets configured
- [ ] Python dependencies installed
- [ ] Local test successful
- [ ] Data visible in Supabase
- [ ] Dashboard running locally
- [ ] CI/CD workflow integrated
- [ ] First automated push successful
- [ ] Baseline configured
- [ ] Team trained on dashboard

---

**Questions?** Open an issue on GitHub or consult the [Architecture Documentation](BENCHMARK_PERSISTENCE_ARCHITECTURE.md).

**Happy monitoring! 🚀**
