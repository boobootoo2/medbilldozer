# Benchmark Persistence & Monitoring Architecture

**Author:** Senior MLOps Engineer  
**Date:** 2026-02-03  
**Status:** Production-Ready  
**Version:** 1.0

---

## 🎯 Executive Summary

This document describes a production-grade benchmark persistence and monitoring system designed for ML model evaluation in a CI/CD pipeline. The architecture follows MLOps best practices and provides a foundation for advanced model monitoring capabilities.

**Key Features:**
- ✅ Immutable append-only transaction log
- ✅ Optimized snapshot layer for current state
- ✅ Time-series analysis support
- ✅ Regression detection
- ✅ Version traceability (model, dataset, prompt, commit)
- ✅ Multi-environment support
- ✅ CI/CD integration

---

## 📐 Architecture Overview

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub Actions                           │
│                                                                   │
│  ┌──────────────┐      ┌───────────────┐      ┌──────────────┐ │
│  │  Run Tests   │─────▶│  Generate     │─────▶│  Push to     │ │
│  │              │      │  Benchmark    │      │  Supabase    │ │
│  └──────────────┘      └───────────────┘      └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Supabase                                │
│                                                                   │
│  ┌───────────────────────────┐   ┌────────────────────────────┐ │
│  │ benchmark_transactions    │   │  benchmark_snapshots       │ │
│  │ (Append-Only Log)         │   │  (Current State)           │ │
│  │                           │   │                            │ │
│  │ • Every benchmark run     │   │ • Latest per config        │ │
│  │ • Immutable history       │   │ • Upsert on new data       │ │
│  │ • Full audit trail        │   │ • Fast dashboard queries   │ │
│  └───────────────────────────┘   └────────────────────────────┘ │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Stored Functions & Views                       │  │
│  │                                                              │  │
│  │  • upsert_benchmark_result() - Atomic insert + upsert      │  │
│  │  • detect_regression() - Compare to baseline               │  │
│  │  • v_latest_benchmarks - Current snapshot view             │  │
│  │  • v_performance_trends - Time-bucketed aggregations       │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                           │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Current     │  │  Historical  │  │  Regression  │          │
│  │  Snapshot    │  │  Trends      │  │  Detection   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema Design

### Two-Table Architecture

We use a **dual-layer persistence model**:

1. **`benchmark_transactions`** - Append-only immutable log
2. **`benchmark_snapshots`** - Materialized current state

### Why This Design?

#### ✅ Benefits of Append-Only Transaction Log

1. **Audit Trail**
   - Complete history of every benchmark run
   - Compliance and debugging support
   - Can replay history to recreate state

2. **Drift Detection**
   - Track performance changes over time
   - Identify when degradation started
   - Correlate with code changes via commit SHA

3. **A/B Testing**
   - Compare different model versions
   - Analyze prompt variations
   - Evaluate dataset quality

4. **Immutability**
   - No UPDATE or DELETE operations
   - Data integrity guaranteed
   - No accidental overwrite

5. **Time-Series Analysis**
   - Natural fit for time-series queries
   - Supports trend analysis
   - Enables forecasting

#### ✅ Benefits of Snapshot Layer

1. **Query Performance**
   - O(1) lookup for current state
   - No aggregation needed
   - Denormalized for speed

2. **Dashboard Efficiency**
   - Fast page loads
   - Reduced database load
   - Better UX

3. **Simplified Queries**
   - "What's the current F1?" → Simple SELECT
   - No complex JOINs or GROUP BYs
   - Easier to reason about

4. **Baseline Management**
   - Mark "golden" configurations
   - Compare against baselines
   - Set production targets

### Schema Details

#### `benchmark_transactions`

| Column | Type | Purpose |
|--------|------|---------|
| `id` | UUID | Primary key |
| `created_at` | TIMESTAMPTZ | When benchmark ran |
| `commit_sha` | TEXT | Git commit for traceability |
| `branch_name` | TEXT | Git branch context |
| `model_version` | TEXT | Model identifier |
| `model_provider` | TEXT | OpenAI, Anthropic, Google, etc. |
| `dataset_version` | TEXT | Dataset identifier |
| `prompt_version` | TEXT | Prompt template version |
| `environment` | TEXT | github-actions, local, staging, production |
| `metrics` | JSONB | Flexible metric storage |
| `duration_seconds` | NUMERIC | Runtime performance |
| `tags` | TEXT[] | Experimentation tags |

**Key Indexes:**
- `created_at DESC` - Time-based queries
- `model_version, created_at DESC` - Model history
- GIN index on `metrics` - Fast JSONB queries
- GIN index on `tags` - Tag filtering

#### `benchmark_snapshots`

| Column | Type | Purpose |
|--------|------|---------|
| `id` | UUID PK | Primary key |
| `snapshot_version` | INTEGER | Version number (1, 2, 3...) |
| `created_at` | TIMESTAMPTZ | When this version created |
| `model_version` | TEXT | Model identifier |
| `dataset_version` | TEXT | Dataset identifier |
| `prompt_version` | TEXT | Prompt identifier |
| `environment` | TEXT | Environment (local, CI, prod) |
| `transaction_id` | UUID FK | Links to source transaction |
| `metrics` | JSONB | Full metrics object |
| `f1_score` | NUMERIC | Denormalized for sorting |
| `precision` | NUMERIC | Denormalized for filtering |
| `recall` | NUMERIC | Denormalized for filtering |
| `latency_ms` | NUMERIC | Performance metric |
| `is_current` | BOOLEAN | Is this the active version? |
| `is_baseline` | BOOLEAN | Mark golden configs |
| `is_active` | BOOLEAN | Soft delete support |

**Key Indexes:**
- `(model_version, dataset_version, prompt_version, environment)` - Configuration lookup
- `(model_version, ..., snapshot_version DESC)` - Version history
- `f1_score DESC` - Leaderboard queries
- `is_current` - Filter current snapshots
- `is_baseline` - Baseline comparisons

**Unique Constraint:**
- `(model_version, dataset_version, prompt_version, environment, snapshot_version)` - Ensures version numbering per config

**✨ New Feature: Snapshot Versioning**
- Each configuration now maintains full version history
- All previous snapshots preserved (not overwritten)
- Can checkout (rollback) any previous version
- Compare versions side-by-side
- See [SNAPSHOT_VERSIONING_GUIDE.md](SNAPSHOT_VERSIONING_GUIDE.md) for details

---

## 🔄 Data Flow

### 1️⃣ Benchmark Run (CI/CD)

```bash
# GitHub Actions workflow
1. Run benchmarks → benchmark_results.json
2. Call push_to_supabase.py
3. Invoke upsert_benchmark_result() stored procedure
4. Transaction inserted + Snapshot upserted (atomic)
```

### 2️⃣ Stored Procedure Flow

```sql
BEGIN TRANSACTION;

  -- Step 1: Insert transaction (append-only)
  INSERT INTO benchmark_transactions (...) 
  RETURNING id;

  -- Step 2: Upsert snapshot (current state)
  INSERT INTO benchmark_snapshots (...)
  ON CONFLICT (model_version, dataset_version, prompt_version, environment)
  DO UPDATE SET
    transaction_id = NEW.id,
    metrics = NEW.metrics,
    last_updated_at = NOW();

COMMIT;
```

### 3️⃣ Dashboard Queries

```python
# Fast: Query snapshot for current state
df = data_access.get_latest_snapshots(environment='production')

# Historical: Query transactions for trends
df = data_access.get_time_series(
    model_version='medgemma-v1.2',
    metric='f1',
    days_back=30
)
```

---

## 📊 Query Patterns

### Latest Snapshot

```sql
-- Fast O(1) lookup
SELECT * FROM benchmark_snapshots
WHERE is_active = TRUE
ORDER BY f1_score DESC;
```

### Historical Trend

```sql
-- Time-series aggregation
SELECT 
  DATE_TRUNC('day', created_at) AS date,
  AVG((metrics->>'f1')::NUMERIC) AS avg_f1
FROM benchmark_transactions
WHERE model_version = 'medgemma-v1.2'
  AND created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date;
```

### Regression Detection

```sql
-- Compare current vs baseline
WITH current AS (
  SELECT f1_score FROM benchmark_snapshots
  WHERE model_version = 'medgemma-v1.2' AND is_active = TRUE
),
baseline AS (
  SELECT f1_score FROM benchmark_snapshots
  WHERE model_version = 'medgemma-v1.2' AND is_baseline = TRUE
)
SELECT 
  c.f1_score AS current_f1,
  b.f1_score AS baseline_f1,
  (b.f1_score - c.f1_score) AS drop,
  (b.f1_score - c.f1_score) > 0.05 AS is_regression
FROM current c, baseline b;
```

---

## 🔍 MLOps Use Cases

### ✅ Currently Supported

1. **Performance Tracking**
   - Track F1, precision, recall over time
   - Monitor latency and cost
   - Compare across environments

2. **Regression Detection**
   - Automatic alerting on performance drops
   - Baseline comparison
   - Configurable thresholds

3. **Model Comparison**
   - A/B test different models
   - Compare prompt variations
   - Analyze dataset impact

4. **Version Traceability**
   - Link performance to Git commits
   - Track model/dataset/prompt versions
   - Environment-aware results

5. **CI/CD Integration**
   - Automatic persistence after benchmark runs
   - GitHub Actions workflow
   - PR comments with results

### 🚀 Future Extensions

#### 1. Data Drift Detection

```sql
-- Add distribution statistics to metrics
{
  "metrics": {
    "f1": 0.895,
    "distribution": {
      "mean": 0.89,
      "std": 0.05,
      "p50": 0.90,
      "p95": 0.92
    }
  }
}
```

**Use Case:** Detect when input data distribution changes

#### 2. Model Drift Monitoring

```sql
-- Track prediction confidence over time
ALTER TABLE benchmark_transactions
ADD COLUMN confidence_stats JSONB;
```

**Use Case:** Identify when model becomes less certain

#### 3. Alerting System

```python
# Webhook integration
if detect_regression(model, threshold):
    send_slack_alert(channel='#ml-alerts', message=...)
    create_github_issue(title='Regression Detected', body=...)
```

**Use Case:** Proactive notifications

#### 4. Feature Store Integration

```sql
-- Track feature importance
ALTER TABLE benchmark_transactions
ADD COLUMN feature_importance JSONB;
```

**Use Case:** Monitor which features drive performance

#### 5. Experiment Tracking

```sql
-- Enhanced tagging
INSERT INTO benchmark_transactions (..., tags)
VALUES (..., ARRAY['experiment-2', 'hypothesis-temperature', 'param-temp-0.7']);
```

**Use Case:** Structured experimentation

#### 6. Cost Optimization

```sql
-- Track cost-efficiency frontier
SELECT 
  model_version,
  f1_score,
  cost_per_analysis,
  (f1_score / cost_per_analysis) AS efficiency_score
FROM benchmark_snapshots
ORDER BY efficiency_score DESC;
```

**Use Case:** Find optimal cost/performance balance

#### 7. SLA Monitoring

```sql
-- Track SLA compliance
ALTER TABLE benchmark_transactions
ADD COLUMN sla_breaches JSONB;

-- Example: {'latency_sla_ms': 500, 'breached': false}
```

**Use Case:** Production SLA tracking

---

## ⚖️ Tradeoffs

### Storage vs Performance

| Aspect | Transaction Table | Snapshot Table |
|--------|------------------|----------------|
| **Size** | Grows linearly | Fixed size |
| **Query Speed** | Slower (aggregation) | Very fast |
| **Use Case** | Analytics, trends | Dashboards |
| **Data Loss Risk** | None (immutable) | Overwrites old state |

**Decision:** Keep both tables
- Small storage overhead (< 1MB per 1000 runs)
- Massive query performance gain
- Full history preserved

### Denormalization

**Tradeoff:** Store computed metrics (f1_score, precision) in snapshots

**Pros:**
- Fast sorting/filtering
- No JSON extraction overhead
- Better for indexed queries

**Cons:**
- Duplicate data (also in metrics JSONB)
- Schema changes require backfill

**Decision:** Denormalize for dashboard performance

### Flexibility vs Structure

**JSONB Metrics:**

**Pros:**
- Add new metrics without schema migration
- Support experiment-specific metrics
- Flexible for rapid iteration

**Cons:**
- Less type safety
- Harder to enforce constraints
- Requires extraction for queries

**Decision:** Use JSONB for metrics, denormalize common ones

---

## 🛡️ Data Integrity

### Immutability Enforcement

```sql
-- Prevent modifications to transactions
ALTER TABLE benchmark_transactions
ADD CONSTRAINT immutable_transaction 
CHECK (created_at <= NOW());

-- Disable UPDATE/DELETE triggers (optional)
CREATE RULE no_update AS ON UPDATE TO benchmark_transactions DO INSTEAD NOTHING;
CREATE RULE no_delete AS ON DELETE TO benchmark_transactions DO INSTEAD NOTHING;
```

### Atomicity

```sql
-- Wrapped in stored procedure
CREATE OR REPLACE FUNCTION upsert_benchmark_result(...)
RETURNS UUID AS $$
BEGIN
  -- Both operations succeed or both fail
  INSERT INTO benchmark_transactions ...;
  INSERT INTO benchmark_snapshots ... ON CONFLICT ...;
  RETURN transaction_id;
END;
$$ LANGUAGE plpgsql;
```

---

## 📈 Scalability Considerations

### Current Design (0-10K runs/day)

✅ No special optimization needed  
✅ Standard indexes sufficient  
✅ Supabase free tier capable

### Medium Scale (10K-100K runs/day)

🔧 Partitioning on `created_at`
```sql
CREATE TABLE benchmark_transactions_2026_02 
PARTITION OF benchmark_transactions
FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
```

🔧 Materialized views for aggregations
```sql
CREATE MATERIALIZED VIEW mv_daily_performance AS
SELECT ...
FROM benchmark_transactions
GROUP BY DATE_TRUNC('day', created_at);

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_performance;
```

### Large Scale (100K+ runs/day)

🔧 Time-series database (TimescaleDB)  
🔧 Separate cold storage (archive old data)  
🔧 Streaming aggregations  
🔧 Read replicas for dashboard queries

---

## 🧪 Testing Strategy

### Unit Tests

```python
def test_upsert_benchmark_result():
    """Test atomic insert + upsert."""
    result = push_benchmark(...)
    assert result.transaction_id is not None
    assert snapshot_exists(...)

def test_regression_detection():
    """Test regression detection logic."""
    result = detect_regression(model='test-model', threshold=0.05)
    assert result['is_regression'] == True
```

### Integration Tests

```python
def test_end_to_end_persistence():
    """Test full CI/CD flow."""
    # 1. Generate benchmark results
    # 2. Push to Supabase
    # 3. Query snapshot
    # 4. Verify data matches
```

### Performance Tests

```python
def test_query_performance():
    """Ensure queries complete within SLA."""
    start = time.time()
    data_access.get_latest_snapshots()
    duration = time.time() - start
    assert duration < 1.0  # < 1 second
```

---

## 🚀 Deployment Checklist

### Initial Setup

- [ ] Create Supabase project
- [ ] Run `schema_benchmark_monitoring.sql`
- [ ] Set up secrets in GitHub Actions:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
- [ ] Install Python dependencies: `pip install supabase pandas plotly streamlit`
- [ ] Test push script locally
- [ ] Deploy benchmark workflow
- [ ] Verify first transaction appears in database

### Monitoring

- [ ] Set up Supabase database alerts
- [ ] Monitor storage usage
- [ ] Track query performance
- [ ] Set up error alerting for failed pushes

### Maintenance

- [ ] Quarterly: Review and archive old data
- [ ] Monthly: Check index performance
- [ ] Weekly: Review dashboard usage
- [ ] Daily: Monitor for regressions

---

## 📚 References

### Files in This System

```
sql/
  schema_benchmark_monitoring.sql       # Database schema

.github/workflows/
  benchmark-persist.yml                 # CI/CD workflow

scripts/
  push_to_supabase.py                   # Persistence script
  benchmark_data_access.py              # Data access layer

pages/
  benchmark_monitoring.py               # Streamlit dashboard

docs/
  BENCHMARK_PERSISTENCE_ARCHITECTURE.md # This file
```

### External Resources

- [Supabase Documentation](https://supabase.com/docs)
- [MLOps Best Practices](https://ml-ops.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## 🎓 Learning Path

For teams new to MLOps, approach this system incrementally:

**Week 1:** Set up basic persistence (transactions + snapshots)  
**Week 2:** Deploy GitHub Actions integration  
**Week 3:** Build initial Streamlit dashboard  
**Week 4:** Add regression detection  
**Week 5:** Implement alerting  
**Week 6:** Expand to experiment tracking

---

## 💡 Key Takeaways

1. **Append-only logs are essential** for ML auditability and debugging
2. **Separate concerns**: Transaction log for history, snapshots for speed
3. **Version everything**: Model, data, prompts, and code (via commit SHA)
4. **Make it atomic**: Use stored procedures for transactional integrity
5. **Design for evolution**: JSONB metrics allow schema flexibility
6. **Observe early**: Don't wait for production to add monitoring
7. **Keep it simple**: Start with this foundation, add complexity as needed

---

**Questions or improvements?** Open an issue or submit a PR!

**Author:** Senior MLOps Engineer  
**Last Updated:** 2026-02-03  
**License:** MIT
