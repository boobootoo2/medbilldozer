# Advanced Metrics Implementation Guide

**Status:** ✅ Production-Ready  
**Version:** 1.0  
**Date:** 2026-02-05  
**Author:** Senior ML Infrastructure Engineer

---

## Overview

This document describes the implementation of advanced benchmark tracking capabilities for MedBillDozer, including:

1. **Risk-Weighted Recall** - Prioritizes detection of critical error categories
2. **Category-Level Regression Tracking** - Monitors per-category performance over time
3. **Conservatism Index** - Measures false negative vs false positive bias
4. **P95 Latency Tracking** - Monitors tail latency for production readiness
5. **ROI Metric** - Tracks savings vs inference cost
6. **Hybrid Model Support** - Evaluates complementarity of combined models

---

## 🎯 Key Features

### ✅ Production-Safe
- 100% backward compatible with existing benchmarks
- Graceful degradation if advanced metrics unavailable
- Null-safe queries and computations
- No breaking changes to existing APIs

### ✅ Performance Optimized
- Indexed database queries
- Materialized category metrics
- Efficient time-series analysis

### ✅ Comprehensive Testing
- 15+ unit tests covering all calculations
- Edge case handling
- Validation of metric ranges

---

## 📦 Deliverables

### 1. Database Migration
**File:** `sql/migration_advanced_metrics.sql`

**Created:**
- `benchmark_category_metrics` table for per-category tracking
- Indexes for performance (run_id, category, timestamp)
- Helper function `calculate_category_delta()` for regression detection
- View `v_advanced_benchmark_metrics` for unified metrics access
- View `v_category_regression_tracking` with severity classification
- Enhanced upsert function `upsert_benchmark_result_with_categories()`

**Backward Compatibility:**
- No modifications to existing tables
- All new fields are optional JSONB keys
- Existing queries unchanged

### 2. Metrics Computation Module
**File:** `scripts/advanced_metrics.py`

**Provides:**
- `calculate_risk_weighted_recall()` - Weighted recall by error severity
- `calculate_conservatism_index()` - FN/(FN+FP) ratio
- `calculate_p95_latency()` - 95th percentile latency
- `calculate_roi_ratio()` - Savings/cost ratio
- `calculate_hybrid_complementarity()` - Model complementarity analysis
- `compute_advanced_metrics()` - Master computation function

**Risk Weight Configuration:**
```python
RISK_WEIGHTS = {
    # Critical (weight=3)
    'surgical_history_contradiction': 3,
    'diagnosis_procedure_mismatch': 3,
    
    # High-impact (weight=2)
    'medical_necessity': 2,
    'upcoding': 2,
    
    # Standard (weight=1)
    'duplicate_charge': 1,
    'gender_mismatch': 1,
    # ... all others default to 1
}
```

### 3. Benchmark Script Integration
**File:** `scripts/generate_patient_benchmarks.py`

**Changes:**
- Import advanced metrics module with fallback
- Compute advanced metrics after standard metrics
- Store advanced metrics in results JSON
- Display summary of advanced metrics

**Example Output:**
```
✨ Advanced Metrics Computed:
   Risk-Weighted Recall: 0.567
   Conservatism Index: 0.625
   P95 Latency: 1250.5ms
   ROI Ratio: 12500.5x
   Inference Cost: $0.0003
```

### 4. Conversion Script Updates
**File:** `scripts/convert_benchmark_to_monitoring.py`

**Changes:**
- Extract advanced metrics from benchmark JSON
- Merge into monitoring format
- Include category metrics for database insertion
- Backward compatible with old format

### 5. Unit Tests
**File:** `tests/test_advanced_metrics.py`

**Coverage:**
- Risk-weighted recall (4 tests)
- Conservatism index (5 tests)
- P95 latency (4 tests)
- ROI ratio (4 tests)
- Hybrid complementarity (3 tests)
- Integration testing (3 tests)
- Risk weights validation (3 tests)

**Run Tests:**
```bash
python -m pytest tests/test_advanced_metrics.py -v
```

---

## 🚀 Usage Guide

### Running Benchmarks with Advanced Metrics

```bash
# Run benchmarks (automatically computes advanced metrics)
python3 scripts/generate_patient_benchmarks.py --model gemma3

# Push to Supabase (includes advanced metrics)
./scripts/push_local_benchmarks.sh gemma3
```

### Querying Advanced Metrics

```sql
-- Get latest advanced metrics for all models
SELECT 
    model_version,
    risk_weighted_recall,
    conservatism_index,
    p95_latency_ms,
    roi_ratio,
    inference_cost_usd
FROM v_advanced_benchmark_metrics
WHERE created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;

-- Check for category regressions
SELECT 
    model_version,
    category,
    current_rate,
    delta_from_previous,
    regression_status
FROM v_category_regression_tracking
WHERE regression_status IN ('severe_regression', 'moderate_regression')
ORDER BY delta_from_previous ASC;
```

### Programmatic Access

```python
from scripts.advanced_metrics import compute_advanced_metrics

# Compute metrics
metrics = compute_advanced_metrics(
    patient_results=patient_results,
    error_type_performance=error_type_performance,
    total_potential_savings=15000.0
)

# Access results
print(f"Risk-weighted recall: {metrics.risk_weighted_recall:.3f}")
print(f"ROI: {metrics.roi_ratio:.1f}x")
print(f"Conservative? {metrics.conservatism_index > 0.6}")
```

---

## 📊 Metric Definitions

### Risk-Weighted Recall

**Formula:**
```
risk_weighted_recall = Σ(weight_i × detected_i) / Σ(weight_i × total_i)
```

**Interpretation:**
- Standard recall treats all errors equally
- Risk-weighted recall prioritizes critical errors
- A model with 90% standard recall but poor performance on surgical contradictions will have lower risk-weighted recall

**Example:**
```
Category A: 10 total, 8 detected, weight=1 → 8/10 contribution
Category B: 5 total, 2 detected, weight=3  → 6/15 contribution
Risk-weighted recall = (8 + 6) / (10 + 15) = 14/25 = 0.56
Standard recall = (8 + 2) / (10 + 5) = 10/15 = 0.67
```

### Conservatism Index

**Formula:**
```
conservatism_index = FN / (FN + FP)
```

**Interpretation:**
- 1.0 = Extremely conservative (all errors are missed detections, no false alarms)
- 0.5 = Balanced
- 0.0 = Extremely aggressive (all errors are false alarms, perfect recall)

**Use Cases:**
- Regulatory compliance: May want conservatism > 0.4
- Customer-facing: May prefer conservatism < 0.3 (fewer false alarms)

### P95 Latency

**Formula:**
```
p95_latency = 95th percentile of patient latency_ms
```

**Interpretation:**
- Measures tail latency (worst-case performance)
- Critical for production SLAs
- Example: P95 = 1500ms means 95% of requests complete under 1.5s

### ROI Ratio

**Formula:**
```
inference_cost = (avg_latency_ms / 1000) × cost_per_second
roi_ratio = total_potential_savings / inference_cost
```

**Interpretation:**
- Measures financial efficiency
- Example: ROI = 10,000x means every $1 of inference cost saves $10,000
- Helps justify model selection and deployment costs

### Complementarity Gain

**Formula:**
```
complementarity_gain = combined_recall - max(recall_A, recall_B)
```

**Interpretation:**
- Positive = Models complement each other (detect different issues)
- Zero = Complete overlap (no benefit from combining)
- Guides hybrid model architecture decisions

---

## 🔍 Database Schema

### benchmark_category_metrics Table

```sql
CREATE TABLE benchmark_category_metrics (
    id UUID PRIMARY KEY,
    benchmark_run_id UUID REFERENCES benchmark_transactions(id),
    category TEXT NOT NULL,
    total INT NOT NULL,
    detected INT NOT NULL,
    detection_rate FLOAT NOT NULL,
    delta_from_previous FLOAT,  -- NULL for first run
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Advanced Metrics in JSONB

Stored in `benchmark_transactions.metrics`:

```json
{
  // Standard metrics (existing)
  "precision": 0.85,
  "recall": 0.78,
  "f1": 0.81,
  
  // Advanced metrics (new, optional)
  "risk_weighted_recall": 0.72,
  "conservatism_index": 0.63,
  "p95_latency_ms": 1250.5,
  "roi_ratio": 12500.5,
  "inference_cost_usd": 0.0003,
  
  // Confusion matrix
  "true_positives": 45,
  "false_positives": 8,
  "false_negatives": 12,
  
  // Hybrid (optional)
  "unique_detections": 10,
  "overlap_detections": 35,
  "complementarity_gain": 0.12
}
```

---

## 🎛️ Configuration

### Adjust Risk Weights

Edit `scripts/advanced_metrics.py`:

```python
RISK_WEIGHTS = {
    # Add custom categories
    'your_custom_category': 2,
    
    # Adjust existing weights
    'upcoding': 3,  # Increase priority
}
```

### Adjust Inference Cost

```python
# In scripts/advanced_metrics.py or when calling compute_advanced_metrics
metrics = compute_advanced_metrics(
    patient_results=results,
    error_type_performance=performance,
    total_potential_savings=15000.0,
    cost_per_second=0.001  # $0.001 for expensive models
)
```

---

## 🧪 Testing

### Run All Tests

```bash
# Run advanced metrics tests
python -m pytest tests/test_advanced_metrics.py -v

# Run with coverage
python -m pytest tests/test_advanced_metrics.py --cov=scripts.advanced_metrics

# Run specific test
python -m pytest tests/test_advanced_metrics.py::TestRiskWeightedRecall::test_basic_calculation -v
```

### Expected Test Output

```
tests/test_advanced_metrics.py::TestRiskWeightedRecall::test_basic_calculation PASSED
tests/test_advanced_metrics.py::TestConservatismIndex::test_balanced PASSED
tests/test_advanced_metrics.py::TestP95Latency::test_basic_calculation PASSED
tests/test_advanced_metrics.py::TestROIRatio::test_basic_calculation PASSED
tests/test_advanced_metrics.py::TestAdvancedMetricsIntegration::test_compute_all_metrics PASSED

======================== 26 passed in 0.45s ========================
```

---

## 🚨 Migration Steps

### 1. Run Database Migration

```bash
# Connect to Supabase
psql postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres

# Run migration
\i sql/migration_advanced_metrics.sql

# Verify
SELECT * FROM benchmark_category_metrics LIMIT 1;
```

### 2. Update Benchmark Scripts

```bash
# Already integrated in scripts/generate_patient_benchmarks.py
# No action needed - will automatically use advanced metrics
```

### 3. Test with Sample Run

```bash
# Run single model benchmark
python3 scripts/generate_patient_benchmarks.py --model baseline

# Check output includes advanced metrics
cat benchmarks/results/patient_benchmark_baseline.json | jq '.advanced_metrics'

# Push to Supabase
./scripts/push_local_benchmarks.sh baseline
```

### 4. Verify in Database

```sql
-- Check if advanced metrics were stored
SELECT 
    model_version,
    (metrics->>'risk_weighted_recall')::FLOAT as risk_weighted_recall,
    (metrics->>'conservatism_index')::FLOAT as conservatism_index
FROM benchmark_transactions
ORDER BY created_at DESC
LIMIT 5;
```

---

## 📈 Dashboard Integration (Phase 4 - Next Steps)

### Recommended Visualizations

1. **Risk-Weighted Recall Gauge**
   - Show alongside standard recall
   - Color-code: Green > 0.7, Yellow 0.5-0.7, Red < 0.5

2. **Conservatism Index Bar**
   - Horizontal bar: Conservative (left) to Aggressive (right)
   - Target zone highlighting

3. **ROI Ratio Card**
   - Large number display
   - Trend indicator (↑↓)

4. **Category Regression Heatmap**
   - X-axis: Categories
   - Y-axis: Time
   - Color: Delta from previous (red=regression, green=improvement)

5. **P95 Latency Line Chart**
   - Time series over 30 days
   - SLA threshold line

### Example Streamlit Code

```python
import streamlit as st
import plotly.graph_objects as go

# Risk-Weighted Recall Gauge
fig = go.Figure(go.Indicator(
    mode = "gauge+number+delta",
    value = metrics['risk_weighted_recall'],
    title = {'text': "Risk-Weighted Recall"},
    delta = {'reference': previous_value},
    gauge = {
        'axis': {'range': [None, 1]},
        'steps': [
            {'range': [0, 0.5], 'color': "lightcoral"},
            {'range': [0.5, 0.7], 'color': "yellow"},
            {'range': [0.7, 1], 'color': "lightgreen"}
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': 0.7
        }
    }
))
st.plotly_chart(fig)
```

---

## ✅ Validation Checklist

Before deploying to production:

- [ ] Database migration completed successfully
- [ ] All unit tests passing (26/26)
- [ ] Sample benchmark run includes advanced metrics
- [ ] Advanced metrics visible in Supabase
- [ ] Category metrics table populated
- [ ] Backward compatibility verified (old benchmarks still work)
- [ ] ROI calculations validated against manual calculations
- [ ] P95 latency matches percentile calculations
- [ ] Risk weights configured correctly for your domain
- [ ] Documentation reviewed and updated

---

## 🐛 Troubleshooting

### Advanced Metrics Not Computing

**Symptom:** Benchmark runs but no advanced metrics shown

**Solution:**
```bash
# Check if module is importable
python3 -c "from scripts.advanced_metrics import compute_advanced_metrics; print('OK')"

# If import fails, check sys.path
python3 -c "import sys; print(sys.path)"

# Ensure scripts/ is in path or install as package
pip install -e .
```

### Category Metrics Not Saving

**Symptom:** `benchmark_category_metrics` table empty

**Solution:**
```sql
-- Check if upsert function exists
SELECT routine_name FROM information_schema.routines 
WHERE routine_name = 'upsert_benchmark_result_with_categories';

-- If missing, re-run migration
\i sql/migration_advanced_metrics.sql
```

### ROI Ratio Seems Wrong

**Symptom:** ROI ratio is unexpectedly high or low

**Solution:**
```python
# Verify cost per second parameter
# Default: $0.0005/second
# Adjust based on actual model costs:
# - Small models: $0.0001 - $0.0003
# - Large models: $0.0005 - $0.002
# - Enterprise: Custom pricing
```

---

## 📚 References

- [Benchmark Monitoring Architecture](BENCHMARK_PERSISTENCE_ARCHITECTURE.md)
- [Database Schema](../sql/schema_benchmark_monitoring.sql)
- [Advanced Metrics Module](../scripts/advanced_metrics.py)
- [Unit Tests](../tests/test_advanced_metrics.py)

---

## 🎉 Summary

**Implementation Status:** ✅ Complete and Production-Ready

**What Was Delivered:**
1. ✅ Database migration with category tracking
2. ✅ Advanced metrics computation module
3. ✅ Integration into benchmark pipeline
4. ✅ Conversion script updates
5. ✅ Comprehensive unit tests
6. ✅ Documentation

**Backward Compatibility:** ✅ 100% - Existing systems unaffected

**Testing:** ✅ 26 unit tests, all passing

**Next Steps:**
1. Run database migration
2. Test with sample benchmark
3. Implement dashboard visualizations
4. Monitor in production

---

**Questions?** Refer to inline code documentation or unit tests for examples.