# Benchmark Monitoring Quick Reference

**Essential commands and queries for daily use**

---

## 🚀 Common Commands

### Setup & Installation

```bash
# Install dependencies
make monitoring-setup
# or
pip install -r requirements-monitoring.txt

# Set environment variables
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
export SUPABASE_ANON_KEY="your-anon-key"
```

### Push Results

```bash
# From CI/CD or local
python scripts/push_to_supabase.py \
  --input benchmark_results.json \
  --environment github-actions \
  --commit-sha $GITHUB_SHA \
  --run-id $GITHUB_RUN_ID \
  --triggered-by $GITHUB_ACTOR

# With tags and notes
python scripts/push_to_supabase.py \
  --input results.json \
  --environment local \
  --commit-sha $(git rev-parse HEAD) \
  --triggered-by $(whoami) \
  --tags experiment-42 temperature-0.7 \
  --notes "Testing new prompt variation" \
  --verify
```

### Launch Dashboard

```bash
# Using make
make monitoring-dashboard

# Direct
streamlit run pages/benchmark_monitoring.py
```

---

## 📊 SQL Queries

### View Latest Results

```sql
-- All active snapshots
SELECT * FROM v_latest_benchmarks;

-- Top 5 by F1
SELECT model_version, f1_score, latency_ms
FROM benchmark_snapshots
WHERE is_active = TRUE
ORDER BY f1_score DESC
LIMIT 5;

-- Filter by environment
SELECT * FROM benchmark_snapshots
WHERE environment = 'production'
  AND is_active = TRUE;
```

### Historical Analysis

```sql
-- Last 30 days of runs
SELECT 
  created_at,
  model_version,
  (metrics->>'f1')::NUMERIC as f1_score
FROM benchmark_transactions
WHERE created_at > NOW() - INTERVAL '30 days'
ORDER BY created_at DESC;

-- Daily averages
SELECT * FROM v_performance_trends
WHERE date > NOW() - INTERVAL '30 days';

-- Specific model history
SELECT 
  created_at::DATE as date,
  AVG((metrics->>'f1')::NUMERIC) as avg_f1,
  COUNT(*) as run_count
FROM benchmark_transactions
WHERE model_version = 'medgemma-v1.2'
GROUP BY created_at::DATE
ORDER BY date DESC;
```

### Regression Detection

```sql
-- Check for regression
SELECT * FROM detect_regression('medgemma-v1.2', 0.05);

-- Set baseline
UPDATE benchmark_snapshots
SET is_baseline = TRUE
WHERE model_version = 'medgemma-v1.2'
  AND environment = 'production';

-- Compare current to baseline
SELECT 
  current.model_version,
  current.f1_score as current_f1,
  baseline.f1_score as baseline_f1,
  (baseline.f1_score - current.f1_score) as drop
FROM benchmark_snapshots current
JOIN benchmark_snapshots baseline
  ON current.model_version = baseline.model_version
WHERE current.is_active = TRUE
  AND baseline.is_baseline = TRUE;
```

### Model Comparison

```sql
-- Compare two models
SELECT 
  model_version,
  AVG((metrics->>'f1')::NUMERIC) as avg_f1,
  AVG((metrics->>'latency_ms')::NUMERIC) as avg_latency,
  COUNT(*) as run_count
FROM benchmark_transactions
WHERE model_version IN ('medgemma-v1.2', 'medgemma-v1.3')
  AND created_at > NOW() - INTERVAL '7 days'
GROUP BY model_version;
```

### Experiment Tracking

```sql
-- Find runs by tag
SELECT *
FROM benchmark_transactions
WHERE 'experiment-42' = ANY(tags)
ORDER BY created_at DESC;

-- Compare tagged experiments
SELECT 
  tags,
  AVG((metrics->>'f1')::NUMERIC) as avg_f1
FROM benchmark_transactions
WHERE 'experiment-42' = ANY(tags)
GROUP BY tags;
```

---

## 🐍 Python API

### Data Access Layer

```python
from scripts.benchmark_data_access import BenchmarkDataAccess

# Initialize
data_access = BenchmarkDataAccess()

# Get latest snapshots
df = data_access.get_latest_snapshots(environment='production')

# Get time series
df = data_access.get_time_series(
    model_version='medgemma-v1.2',
    metric='f1',
    days_back=30
)

# Compare models
df = data_access.compare_models(
    model_versions=['medgemma-v1.2', 'medgemma-v1.3'],
    metric='f1',
    days_back=7
)

# Detect regression
result = data_access.detect_regressions(
    model_version='medgemma-v1.2',
    threshold=0.05  # 5% drop
)

# Get available models
models = data_access.get_available_models(environment='production')
```

### Persistence

```python
from scripts.push_to_supabase import BenchmarkPersistence, BenchmarkResult

# Initialize
persistence = BenchmarkPersistence(supabase_url, supabase_key)

# Create result
result = BenchmarkResult(
    model_version='medgemma-v1.2',
    dataset_version='benchmark-set-v3',
    prompt_version='analysis-v4',
    metrics={
        'precision': 0.91,
        'recall': 0.88,
        'f1': 0.895,
        'latency_ms': 412,
        'analysis_cost': 0.0042
    }
)

# Push to database
transaction_id = persistence.push_benchmark(
    result=result,
    commit_sha='abc123',
    environment='local',
    tags=['experiment-1']
)

# Verify
persistence.verify_persistence(transaction_id)
```

---

## 🔧 Maintenance

### Archive Old Data

```sql
-- Archive transactions older than 1 year
CREATE TABLE benchmark_transactions_archive AS
SELECT * FROM benchmark_transactions
WHERE created_at < NOW() - INTERVAL '1 year';

-- Delete from main table
DELETE FROM benchmark_transactions
WHERE created_at < NOW() - INTERVAL '1 year';

-- Verify
SELECT 
  'main' as table_name,
  COUNT(*) as row_count,
  MIN(created_at) as oldest_record
FROM benchmark_transactions
UNION ALL
SELECT 
  'archive',
  COUNT(*),
  MIN(created_at)
FROM benchmark_transactions_archive;
```

### Check Storage Usage

```sql
-- Table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE 'benchmark%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Row counts
SELECT 
  'transactions' as table_name,
  COUNT(*) as row_count
FROM benchmark_transactions
UNION ALL
SELECT 
  'snapshots',
  COUNT(*)
FROM benchmark_snapshots;
```

### Refresh Materialized Views

```sql
-- If you created materialized views
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_performance;
```

### Reindex

```sql
-- Rebuild indexes for performance
REINDEX TABLE benchmark_transactions;
REINDEX TABLE benchmark_snapshots;
```

---

## 🎯 Best Practices

### Tagging Strategy

```bash
# Use consistent tag naming
--tags baseline                    # Mark baseline runs
--tags experiment-N                # Numbered experiments
--tags feature-new-prompt          # Feature testing
--tags bug-regression-123          # Bug investigation
--tags param-temperature-0.7       # Parameter variations
```

### Baseline Management

```sql
-- Set new baseline after validation
UPDATE benchmark_snapshots
SET is_baseline = FALSE
WHERE model_version = 'medgemma-v1.2';

UPDATE benchmark_snapshots
SET is_baseline = TRUE
WHERE model_version = 'medgemma-v1.2'
  AND environment = 'production'
  AND snapshot_version = 5;  -- The validated version
```

### Snapshot Versioning

```sql
-- View snapshot history
SELECT * FROM get_snapshot_history(
    'medgemma-v1.2',           -- model
    'benchmark-set-v3',        -- dataset
    'analysis-v4',             -- prompt
    'production',              -- environment
    10                         -- limit
);

-- Rollback to previous version
SELECT checkout_snapshot(
    'medgemma-v1.2',
    'benchmark-set-v3',
    'analysis-v4',
    'production',
    2  -- version to checkout
);

-- Compare two versions
SELECT * FROM compare_snapshots(
    'medgemma-v1.2',
    'benchmark-set-v3',
    'analysis-v4',
    'production',
    2,  -- version A
    3   -- version B
);
```

### Data Cleanup

```sql
-- Mark old snapshots as inactive (soft delete)
UPDATE benchmark_snapshots
SET is_active = FALSE
WHERE last_updated_at < NOW() - INTERVAL '90 days'
  AND is_baseline = FALSE;
```

---

## 📈 Monitoring Queries

### Health Checks

```sql
-- Check for recent activity
SELECT 
  environment,
  COUNT(*) as run_count,
  MAX(created_at) as last_run
FROM benchmark_transactions
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY environment;

-- Identify stale models (no runs in 30 days)
SELECT 
  model_version,
  MAX(created_at) as last_run,
  NOW() - MAX(created_at) as days_since_last_run
FROM benchmark_transactions
GROUP BY model_version
HAVING MAX(created_at) < NOW() - INTERVAL '30 days';
```

### Performance Degradation

```sql
-- Find models with declining F1
WITH recent AS (
  SELECT 
    model_version,
    AVG((metrics->>'f1')::NUMERIC) as recent_f1
  FROM benchmark_transactions
  WHERE created_at > NOW() - INTERVAL '7 days'
  GROUP BY model_version
),
older AS (
  SELECT 
    model_version,
    AVG((metrics->>'f1')::NUMERIC) as older_f1
  FROM benchmark_transactions
  WHERE created_at BETWEEN NOW() - INTERVAL '30 days' AND NOW() - INTERVAL '7 days'
  GROUP BY model_version
)
SELECT 
  r.model_version,
  r.recent_f1,
  o.older_f1,
  (r.recent_f1 - o.older_f1) as f1_change,
  ((r.recent_f1 - o.older_f1) / o.older_f1 * 100) as percent_change
FROM recent r
JOIN older o ON r.model_version = o.model_version
WHERE r.recent_f1 < o.older_f1
ORDER BY percent_change;
```

### Cost Analysis

```sql
-- Average cost per model
SELECT 
  model_version,
  AVG((metrics->>'analysis_cost')::NUMERIC) as avg_cost,
  COUNT(*) as run_count,
  SUM((metrics->>'analysis_cost')::NUMERIC) as total_cost
FROM benchmark_transactions
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY model_version
ORDER BY total_cost DESC;

-- Cost trend over time
SELECT 
  DATE_TRUNC('day', created_at) as date,
  AVG((metrics->>'analysis_cost')::NUMERIC) as avg_cost
FROM benchmark_transactions
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date;
```

---

## 🚨 Troubleshooting

### Connection Issues

```bash
# Test Supabase connection
python3 -c "
from supabase import create_client
import os
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
print('✓ Connection successful')
print('URL:', os.getenv('SUPABASE_URL'))
"
```

### Data Validation

```sql
-- Check for NULL metrics
SELECT COUNT(*) FROM benchmark_transactions WHERE metrics IS NULL;

-- Check for invalid F1 scores (should be 0-1)
SELECT * FROM benchmark_transactions
WHERE (metrics->>'f1')::NUMERIC NOT BETWEEN 0 AND 1;

-- Find orphaned snapshots (no linked transaction)
SELECT s.*
FROM benchmark_snapshots s
LEFT JOIN benchmark_transactions t ON s.transaction_id = t.id
WHERE t.id IS NULL;
```

### Performance Issues

```sql
-- Check index usage
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan as index_scans,
  idx_tup_read as tuples_read
FROM pg_stat_user_indexes
WHERE tablename LIKE 'benchmark%'
ORDER BY idx_scan DESC;

-- Identify slow queries (requires pg_stat_statements)
SELECT 
  query,
  calls,
  mean_exec_time,
  total_exec_time
FROM pg_stat_statements
WHERE query LIKE '%benchmark%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## 📚 Quick Links

- **Setup Guide:** [BENCHMARK_MONITORING_SETUP.md](BENCHMARK_MONITORING_SETUP.md)
- **Architecture:** [BENCHMARK_PERSISTENCE_ARCHITECTURE.md](BENCHMARK_PERSISTENCE_ARCHITECTURE.md)
- **Main README:** [BENCHMARK_MONITORING_README.md](../BENCHMARK_MONITORING_README.md)
- **SQL Schema:** [schema_benchmark_monitoring.sql](../sql/schema_benchmark_monitoring.sql)

---

**Pro Tip:** Bookmark this page for quick reference during daily operations!
