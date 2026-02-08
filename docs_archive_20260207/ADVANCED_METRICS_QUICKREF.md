# Advanced Metrics Quick Reference

**Version:** 1.0 | **Date:** 2026-02-05

---

## 🚀 Quick Start

```bash
# 1. Run database migration (Supabase)
python3 scripts/run_advanced_metrics_migration.py
# This will guide you through running the migration in Supabase Dashboard

# 2. Run benchmarks (automatically includes advanced metrics)
python3 scripts/generate_patient_benchmarks.py --model gemma3

# 3. Push to Supabase
./scripts/push_local_benchmarks.sh gemma3

# 4. Run tests
python -m pytest tests/test_advanced_metrics.py -v
```

### Supabase Migration (Detailed)

**Option 1: Supabase Dashboard (Easiest)**
1. Go to https://supabase.com/dashboard
2. Select your project
3. Click "SQL Editor" in sidebar
4. Click "New Query"
5. Copy contents of `sql/migration_advanced_metrics.sql`
6. Paste and click "Run"

**Option 2: psql CLI**
```bash
# Get your connection string from Supabase Dashboard > Settings > Database
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres" \
     -f sql/migration_advanced_metrics.sql
```

---

## 📊 Key Metrics

| Metric | Formula | Range | Interpretation |
|--------|---------|-------|----------------|
| **Risk-Weighted Recall** | `Σ(w×detected) / Σ(w×total)` | 0.0-1.0 | Prioritizes critical errors |
| **Conservatism Index** | `FN / (FN + FP)` | 0.0-1.0 | 1.0=conservative, 0.0=aggressive |
| **P95 Latency** | 95th percentile | >0 ms | Tail latency for SLA |
| **ROI Ratio** | `savings / inference_cost` | >0 | Financial efficiency |
| **Complementarity Gain** | `combined - max(individual)` | 0.0-1.0 | Hybrid model benefit |

---

## 🎯 Risk Weights

```python
Critical (3x):  surgical_history_contradiction, diagnosis_procedure_mismatch
High (2x):      medical_necessity, upcoding  
Standard (1x):  All others (gender_mismatch, duplicate_charge, etc.)
```

---

## 📝 Common Queries

```sql
-- Latest advanced metrics
SELECT model_version, risk_weighted_recall, conservatism_index, roi_ratio
FROM v_advanced_benchmark_metrics
ORDER BY created_at DESC LIMIT 10;

-- Category regressions
SELECT * FROM v_category_regression_tracking
WHERE regression_status IN ('severe_regression', 'moderate_regression');

-- P95 latency trend
SELECT created_at::DATE, model_version, p95_latency_ms
FROM v_advanced_benchmark_metrics
WHERE created_at > NOW() - INTERVAL '30 days'
ORDER BY created_at;
```

---

## 🐍 Python Usage

```python
from scripts.advanced_metrics import compute_advanced_metrics

metrics = compute_advanced_metrics(
    patient_results=results,
    error_type_performance=categories,
    total_potential_savings=15000.0
)

print(f"Risk-weighted: {metrics.risk_weighted_recall:.3f}")
print(f"ROI: {metrics.roi_ratio:.1f}x")
```

---

## ✅ Validation

```bash
# Check advanced metrics in latest run
cat benchmarks/results/patient_benchmark_*.json | jq '.advanced_metrics'

# Verify in database
psql $DATABASE_URL -c "SELECT (metrics->>'risk_weighted_recall')::FLOAT FROM benchmark_transactions ORDER BY created_at DESC LIMIT 1;"
```

---

## 🎨 Dashboard Snippets

```python
# Risk-Weighted Recall Gauge
fig = go.Indicator(
    value=metrics['risk_weighted_recall'],
    mode="gauge+number",
    gauge={'axis': {'range': [0, 1]}}
)

# ROI Card
st.metric(
    "ROI Ratio",
    f"{metrics['roi_ratio']:.1f}x",
    delta=f"{delta:.1f}x"
)

# Conservatism Index Bar
st.progress(metrics['conservatism_index'])
st.caption("←Aggressive | Balanced | Conservative→")
```

---

## 🔧 Configuration

```python
# Adjust inference cost (scripts/advanced_metrics.py)
cost_per_second = 0.0005  # $0.0005 default
# Small models: 0.0001-0.0003
# Large models: 0.0005-0.002

# Adjust risk weights
RISK_WEIGHTS['your_category'] = 3  # Critical priority
```

---

## 🧪 Testing

```bash
# All tests
pytest tests/test_advanced_metrics.py -v

# Specific test
pytest tests/test_advanced_metrics.py::TestRiskWeightedRecall -v

# With coverage
pytest tests/test_advanced_metrics.py --cov=scripts.advanced_metrics
```

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| Advanced metrics not computing | `python3 -c "from scripts.advanced_metrics import compute_advanced_metrics"` |
| Category table empty | Re-run migration: `psql $DB -f sql/migration_advanced_metrics.sql` |
| ROI seems wrong | Check `cost_per_second` parameter matches your model costs |
| Backward compatibility issue | Advanced metrics are optional - old code still works |

---

## 📁 File Locations

```
sql/migration_advanced_metrics.sql        # Database migration
scripts/advanced_metrics.py               # Computation module
scripts/generate_patient_benchmarks.py    # Integration (lines 30-50, 1070-1100, 1201-1230)
scripts/convert_benchmark_to_monitoring.py # Supabase push (lines 35-90)
tests/test_advanced_metrics.py            # Unit tests
docs/ADVANCED_METRICS_IMPLEMENTATION.md   # Full documentation
```

---

## 📞 Support

- **Full Docs:** [ADVANCED_METRICS_IMPLEMENTATION.md](ADVANCED_METRICS_IMPLEMENTATION.md)
- **Unit Tests:** [test_advanced_metrics.py](../tests/test_advanced_metrics.py)
- **Code Examples:** See inline docstrings in `scripts/advanced_metrics.py`

---

**Status:** ✅ Production-Ready | **Tests:** 26/26 Passing | **Compatibility:** 100%
