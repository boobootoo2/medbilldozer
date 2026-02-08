# Cost Savings Metrics Setup Guide

This guide walks you through adding cost savings metrics to the Model Benchmark system.

## What Changed

### 1. Benchmark Script (`generate_patient_benchmarks.py`)
✅ **ALREADY UPDATED** - Now calculates:
- `potential_savings`: $ from detected issues (using `max_savings` field)
- `missed_savings`: $ from undetected issues ($250 per missed issue)
- `avg_savings_per_patient`: Average $ captured per patient
- `savings_capture_rate`: % of possible savings captured (ROI metric)

### 2. Conversion Script (`convert_benchmark_to_monitoring.py`)
✅ **ALREADY UPDATED** - Now includes cost savings in monitoring format

### 3. Dashboard (`pages/production_stability.py`)
✅ **ALREADY UPDATED** - Now displays cost savings metrics when available

### 4. Database Schema
⚠️ **NEEDS MIGRATION** - Add 4 new columns and update upsert function

## Setup Steps

### Step 1: Run Database Migrations

Open your Supabase SQL Editor and run these two migrations in order:

#### Migration 1: Add Columns
```bash
cat sql/migration_add_cost_savings.sql
```

Copy and paste this into Supabase SQL Editor:
- Adds 4 new columns to `benchmark_snapshots` table
- Creates index for cost savings queries
- All columns default to 0 (safe for existing data)

#### Migration 2: Update Upsert Function
```bash
cat sql/migration_update_upsert_function.sql
```

Copy and paste this into Supabase SQL Editor:
- Updates `upsert_benchmark_result()` function
- Extracts cost savings from `metrics` JSONB
- Populates new columns during insert

### Step 2: Re-run Benchmarks

Run benchmarks to generate results with cost savings:

```bash
# Run all models
python3 scripts/generate_patient_benchmarks.py --model all

# Or run specific model
python3 scripts/generate_patient_benchmarks.py --model medgemma
```

You should see new output section:
```
💰 COST SAVINGS METRICS:
  Total Potential Savings:   $1,234.56
  Total Missed Savings:      $567.89
  Avg Savings per Patient:   $123.45
  Savings Capture Rate:      68.5%
```

### Step 3: Push Results to Supabase

```bash
# Push all models
./scripts/push_local_benchmarks.sh

# Or push specific model
python3 scripts/convert_benchmark_to_monitoring.py \
  --input benchmarks/results/patient_benchmark_medgemma.json \
  --output benchmark_results_medgemma.json \
  --model medgemma

python3 scripts/push_to_supabase.py \
  --file benchmark_results_medgemma.json \
  --environment local \
  --triggered-by "cost-savings-metrics"
```

### Step 4: Restart Dashboard

```bash
# Stop current dashboard (Ctrl+C in terminal)
# Then restart:
python3 -m streamlit run pages/production_stability.py --server.port 8502
```

### Step 5: Verify in Dashboard

Navigate to **📊 Current Snapshot** tab and look for:

```
💰 Cost Savings Metrics
┌─────────────────────────────┬──────────────────────────┬─────────────────────┬──────────────────────┐
│ Total Potential Savings     │ Avg Savings per Patient  │ Avg Capture Rate    │ Total Missed Savings │
│ $1,234.56                   │ $123.45                  │ 68.5%               │ $567.89              │
└─────────────────────────────┴──────────────────────────┴─────────────────────┴──────────────────────┘
```

## How Cost Savings Are Calculated

### For Detected Issues
Uses actual `max_savings` field from detected issues:
```python
potential_savings = sum(
    detected_issue.get('max_savings', 0) or 0
    for detected_issue in detected
    if detected.index(detected_issue) in matched_detected_indices
)
```

### For Missed Issues
Conservative estimate of $250 per undetected issue:
```python
avg_issue_value = 250.0  # Conservative average
missed_savings = false_negatives * avg_issue_value
```

### Capture Rate
Percentage of total possible savings that were captured:
```python
total_possible = potential_savings + missed_savings
savings_capture_rate = (potential_savings / total_possible * 100) if total_possible > 0 else 0.0
```

## Troubleshooting

### Issue: "Column does not exist" error when pushing

**Solution:** Run Migration 1 first (add columns to table)

### Issue: "Function upsert_benchmark_result failed"

**Solution:** Run Migration 2 (update function to handle new columns)

### Issue: Cost savings show as $0.00

**Possible causes:**
1. Ground truth annotations don't have `max_savings` values
2. Model didn't detect any issues (check F1 score)
3. Re-run benchmarks to generate fresh data with calculations

**Solution:** Check patient profile expected issues:
```bash
cat benchmarks/patient_profiles/patient_001.json | jq '.expected_issues[].max_savings'
```

If null, add `max_savings` to expected issues.

### Issue: Dashboard doesn't show cost savings section

**Possible causes:**
1. Database columns don't exist yet
2. Old results in database without cost savings data
3. Dashboard needs restart

**Solution:**
1. Run migrations
2. Re-push benchmarks
3. Restart dashboard
4. Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)

## Naming Convention Change

Also renamed "Patient Benchmarks" → "Model Benchmarks" throughout:
- Script messages and output
- Dashboard titles
- Documentation

This reflects that we're measuring **model performance**, not patient health metrics.

## Files Modified

### Core Changes
- ✅ `scripts/generate_patient_benchmarks.py` - Added cost calculations
- ✅ `scripts/convert_benchmark_to_monitoring.py` - Added cost fields to monitoring format
- ✅ `pages/production_stability.py` - Added cost savings display section

### Database Changes
- ⚠️ `sql/migration_add_cost_savings.sql` - Add columns (NEEDS RUNNING)
- ⚠️ `sql/migration_update_upsert_function.sql` - Update function (NEEDS RUNNING)

### Documentation
- ✅ `COST_SAVINGS_SETUP.md` - This guide

## Next Steps

After setup is complete:

1. **Compare models by ROI**: Which model captures the most savings per analysis?
2. **Track savings over time**: Is prompt engineering improving ROI?
3. **Calculate cost/benefit**: Model cost vs savings captured
4. **Set ROI targets**: Aim for >80% savings capture rate

## Quick Reference Commands

```bash
# Full workflow
python3 scripts/generate_patient_benchmarks.py --model all
./scripts/push_local_benchmarks.sh
python3 -m streamlit run pages/production_stability.py --server.port 8502

# Check results locally
cat benchmarks/results/patient_benchmark_medgemma.json | jq '.total_potential_savings'

# Verify database
python3 << 'EOF'
from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

response = client.table('benchmark_snapshots').select(
    'model_version, total_potential_savings, savings_capture_rate'
).eq('is_current', True).execute()

for row in response.data:
    print(f"{row['model_version']}: ${row['total_potential_savings']:.2f} ({row['savings_capture_rate']:.1f}%)")
EOF
```

## Questions?

See the conversation history for context on why these metrics matter and how they tie into the broader benchmark system improvements.
