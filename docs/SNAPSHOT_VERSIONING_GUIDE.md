# Snapshot Versioning Guide

**How to track, checkout, and rollback benchmark snapshots**

---

## 🎯 Overview

The benchmark monitoring system now includes **snapshot versioning**, allowing you to:

- ✅ Keep full history of all snapshots (not just the latest)
- ✅ Checkout (revert to) any previous snapshot version
- ✅ Compare different snapshot versions side-by-side
- ✅ Track performance changes over snapshot versions

---

## 📊 How Snapshot Versioning Works

### Key Concepts

**Snapshot Version**: An incrementing integer for each configuration
- Configuration = (model_version, dataset_version, prompt_version, environment)
- Each new benchmark run creates a new snapshot version
- Version numbers start at 1 and increment sequentially

**Current Snapshot**: The active version used by dashboards
- Only ONE snapshot per configuration is marked as `is_current = TRUE`
- By default, the latest version is current
- You can checkout any previous version to make it current

**Historical Snapshots**: Previous versions preserved for analysis
- All older versions remain in the database
- Can be queried for historical analysis
- Can be compared against current or other versions

---

## 🔄 Lifecycle Example

```
Configuration: (medgemma-v1.2, benchmark-set-v3, analysis-v4, production)

Time    Action                 Version    is_current    F1 Score
-----   --------------------   -------    ----------    --------
T0      Initial benchmark      1          TRUE          0.89
T1      New benchmark          2          TRUE          0.91  (v1 now FALSE)
T2      New benchmark          3          TRUE          0.85  (v2 now FALSE)
T3      Regression detected!   -          -             -
T4      Checkout version 2     2          TRUE          0.91  (rollback!)
T5      New benchmark          4          TRUE          0.93  (fixed!)

Result: Version history preserved: [1, 2, 3, 4]
        Current version: 4
        All previous versions still queryable
```

---

## 💻 Usage Examples

### 1. View Snapshot History

**SQL:**
```sql
-- Get last 10 versions for a configuration
SELECT * FROM get_snapshot_history(
    'medgemma-v1.2',           -- model_version
    'benchmark-set-v3',        -- dataset_version
    'analysis-v4',             -- prompt_version
    'production',              -- environment
    10                          -- limit
);
```

**Python:**
```python
from scripts.benchmark_data_access import BenchmarkDataAccess

data = BenchmarkDataAccess()

history = data.get_snapshot_history(
    model_version='medgemma-v1.2',
    dataset_version='benchmark-set-v3',
    prompt_version='analysis-v4',
    environment='production',
    limit=10
)

print(history)
```

**Output:**
```
   snapshot_version            created_at commit_sha  f1_score  is_current  is_baseline
0                 4  2026-02-03 15:30:00   abc456       0.93        True        False
1                 3  2026-02-03 14:00:00   abc123       0.85       False        False
2                 2  2026-02-03 12:00:00   def789       0.91       False         True
3                 1  2026-02-03 10:00:00   ghi012       0.89       False        False
```

---

### 2. Checkout (Rollback) a Snapshot

**When to use:**
- Regression detected, need to revert to previous good state
- Testing showed new version has issues
- Want to temporarily use an older version

**SQL:**
```sql
-- Rollback to version 2
SELECT checkout_snapshot(
    'medgemma-v1.2',      -- model_version
    'benchmark-set-v3',   -- dataset_version
    'analysis-v4',        -- prompt_version
    'production',         -- environment
    2                     -- snapshot_version to checkout
);

-- Verify
SELECT snapshot_version, is_current, f1_score
FROM benchmark_snapshots
WHERE model_version = 'medgemma-v1.2'
  AND dataset_version = 'benchmark-set-v3'
  AND prompt_version = 'analysis-v4'
  AND environment = 'production'
ORDER BY snapshot_version DESC;
```

**Python:**
```python
# Rollback to version 2
success = data.checkout_snapshot(
    model_version='medgemma-v1.2',
    dataset_version='benchmark-set-v3',
    prompt_version='analysis-v4',
    environment='production',
    snapshot_version=2
)

print(f"Rollback successful: {success}")

# Now dashboard will show version 2 as current
```

**Effect:**
- Version 2 becomes current (`is_current = TRUE`)
- All other versions marked as not current
- Dashboard now shows version 2 metrics
- No data is lost - all versions still in database

---

### 3. Compare Snapshot Versions

**SQL:**
```sql
-- Compare version 2 vs version 3
SELECT * FROM compare_snapshots(
    'medgemma-v1.2',      -- model_version
    'benchmark-set-v3',   -- dataset_version
    'analysis-v4',        -- prompt_version
    'production',         -- environment
    2,                    -- version_a
    3                     -- version_b
);
```

**Output:**
```
      metric          version_a_value  version_b_value   delta  percent_change
0   f1_score                  0.91            0.85      -0.06          -6.59
1  precision                  0.92            0.87      -0.05          -5.43
2     recall                  0.90            0.83      -0.07          -7.78
3 latency_ms                412.00          425.00      13.00           3.16
```

**Python:**
```python
comparison = data.compare_snapshot_versions(
    model_version='medgemma-v1.2',
    dataset_version='benchmark-set-v3',
    prompt_version='analysis-v4',
    environment='production',
    version_a=2,
    version_b=3
)

print(comparison)

# Analysis
for _, row in comparison.iterrows():
    if row['percent_change'] < -5:
        print(f"⚠️ {row['metric']}: dropped {abs(row['percent_change']):.2f}%")
```

---

### 4. Query Specific Version

**SQL:**
```sql
-- Get metrics from version 2 specifically
SELECT *
FROM benchmark_snapshots
WHERE model_version = 'medgemma-v1.2'
  AND dataset_version = 'benchmark-set-v3'
  AND prompt_version = 'analysis-v4'
  AND environment = 'production'
  AND snapshot_version = 2;
```

**Python:**
```python
# Query historical version
query = data.client.table('benchmark_snapshots').select('*')
query = query.eq('model_version', 'medgemma-v1.2')
query = query.eq('dataset_version', 'benchmark-set-v3')
query = query.eq('prompt_version', 'analysis-v4')
query = query.eq('environment', 'production')
query = query.eq('snapshot_version', 2)

response = query.execute()
snapshot = response.data[0] if response.data else None

print(f"Version 2 F1: {snapshot['f1_score']}")
```

---

### 5. Track Changes Across Versions

**SQL:**
```sql
-- Show F1 progression across all versions
SELECT 
    snapshot_version,
    created_at,
    f1_score,
    f1_score - LAG(f1_score) OVER (ORDER BY snapshot_version) as f1_delta,
    CASE 
        WHEN is_current THEN '← CURRENT'
        WHEN is_baseline THEN '← BASELINE'
        ELSE ''
    END as status
FROM benchmark_snapshots
WHERE model_version = 'medgemma-v1.2'
  AND dataset_version = 'benchmark-set-v3'
  AND prompt_version = 'analysis-v4'
  AND environment = 'production'
ORDER BY snapshot_version DESC;
```

**Output:**
```
snapshot_version            created_at  f1_score  f1_delta       status
               4  2026-02-03 15:30:00      0.93     +0.08   ← CURRENT
               3  2026-02-03 14:00:00      0.85     -0.06
               2  2026-02-03 12:00:00      0.91     +0.02   ← BASELINE
               1  2026-02-03 10:00:00      0.89       NULL
```

---

## 🎯 Common Workflows

### Workflow 1: Regression Investigation

```bash
# 1. Detect regression
SELECT * FROM detect_regression('medgemma-v1.2', 0.05);
# Result: is_regression = TRUE

# 2. View recent history
SELECT * FROM get_snapshot_history(
    'medgemma-v1.2', 'benchmark-set-v3', 'analysis-v4', 'production', 5
);

# 3. Identify the problem version (version 3)
# 4. Compare good vs bad
SELECT * FROM compare_snapshots(
    'medgemma-v1.2', 'benchmark-set-v3', 'analysis-v4', 'production', 2, 3
);

# 5. Rollback to good version
SELECT checkout_snapshot(
    'medgemma-v1.2', 'benchmark-set-v3', 'analysis-v4', 'production', 2
);

# 6. Investigate what changed in commit from version 3
# 7. Fix the issue
# 8. Run new benchmark (creates version 4)
# 9. Verify version 4 is better than version 2
```

---

### Workflow 2: A/B Testing with Rollback Safety

```bash
# 1. Set current version as baseline
UPDATE benchmark_snapshots
SET is_baseline = TRUE
WHERE model_version = 'medgemma-v1.2'
  AND snapshot_version = 2;

# 2. Deploy experimental change
# 3. Run benchmark (creates version 3)

# 4. Evaluate
SELECT * FROM compare_snapshots(..., 2, 3);

# 5a. If better: Keep it (do nothing)
# 5b. If worse: Rollback
SELECT checkout_snapshot(..., 2);
```

---

### Workflow 3: Performance Trend Analysis

```python
# Get all versions
history = data.get_snapshot_history(
    'medgemma-v1.2', 'benchmark-set-v3', 'analysis-v4', 'production', 
    limit=100
)

# Plot F1 over versions
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(history['snapshot_version'], history['f1_score'], marker='o')
plt.axhline(y=0.90, color='r', linestyle='--', label='Target')
plt.xlabel('Snapshot Version')
plt.ylabel('F1 Score')
plt.title('F1 Score Evolution Across Snapshot Versions')
plt.legend()
plt.grid(True)
plt.show()
```

---

## 🔧 Maintenance

### Archive Old Snapshots

```sql
-- Mark snapshots older than 90 days as inactive
-- (Keeps them in DB but excludes from queries)
UPDATE benchmark_snapshots
SET is_active = FALSE
WHERE created_at < NOW() - INTERVAL '90 days'
  AND is_current = FALSE
  AND is_baseline = FALSE;
```

### Cleanup Excessive Versions

```sql
-- Keep only last 10 versions per configuration
WITH ranked AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (
            PARTITION BY model_version, dataset_version, prompt_version, environment
            ORDER BY snapshot_version DESC
        ) as rank
    FROM benchmark_snapshots
)
UPDATE benchmark_snapshots
SET is_active = FALSE
WHERE id IN (
    SELECT id FROM ranked WHERE rank > 10
)
AND is_baseline = FALSE;
```

---

## 🎓 Best Practices

### 1. Set Baselines Strategically
```sql
-- Mark production-validated versions as baselines
UPDATE benchmark_snapshots
SET is_baseline = TRUE
WHERE model_version = 'medgemma-v1.2'
  AND snapshot_version = 5  -- The validated version
  AND environment = 'production';
```

### 2. Document Major Versions
```sql
-- Add notes to important snapshots via their transaction
UPDATE benchmark_transactions
SET notes = 'Major release v1.2 - production validated'
WHERE id = (
    SELECT transaction_id
    FROM benchmark_snapshots
    WHERE snapshot_version = 5
);
```

### 3. Regular Cleanup
- Keep last 10-20 versions active
- Archive older versions
- Preserve baselines indefinitely

### 4. Use Descriptive Tags
```bash
# When creating new snapshots
python push_to_supabase.py \
  --input results.json \
  --tags release-v1.2 production-ready validated \
  --notes "Passed all QA tests"
```

---

## 🆚 Comparison: Old vs New Schema

### Old Schema (Single Snapshot)
```
❌ Only ONE snapshot per configuration
❌ Old snapshot overwritten on new benchmark
❌ Cannot rollback to previous state
❌ Lost historical context
```

### New Schema (Versioned Snapshots)
```
✅ MULTIPLE snapshots per configuration
✅ All snapshots preserved forever
✅ Can checkout any previous version
✅ Full historical analysis
✅ Side-by-side version comparison
```

---

## 📚 Quick Reference

### Key Functions

| Function | Purpose |
|----------|---------|
| `get_snapshot_history()` | View version history |
| `checkout_snapshot()` | Rollback to specific version |
| `compare_snapshots()` | Compare two versions |
| `detect_regression()` | Check current vs baseline |

### Key Fields

| Field | Description |
|-------|-------------|
| `snapshot_version` | Sequential version number (1, 2, 3...) |
| `is_current` | TRUE = active version shown in dashboard |
| `is_baseline` | TRUE = reference version for regression detection |
| `is_active` | TRUE = not archived |
| `created_at` | When this version was created |

---

## 🚀 Migration from Old Schema

If you already have data in the old schema:

```sql
-- The new schema is backward compatible
-- Old snapshots will become version 1
-- New benchmarks will create version 2, 3, etc.

-- If you want to preserve existing data:
-- 1. Backup current snapshots
CREATE TABLE benchmark_snapshots_backup AS
SELECT * FROM benchmark_snapshots;

-- 2. Drop old table
DROP TABLE benchmark_snapshots CASCADE;

-- 3. Run new schema from schema_benchmark_monitoring.sql

-- 4. Migrate data (adjust as needed)
-- This will convert old snapshots to version 1
-- Subsequent pushes will create version 2+
```

---

**Questions?** See [BENCHMARK_PERSISTENCE_ARCHITECTURE.md](BENCHMARK_PERSISTENCE_ARCHITECTURE.md) for full design details.
