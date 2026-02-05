# Cost Savings Metrics - Quick Start

## Current Status

✅ **Code Updated:**
- ✅ Dashboard now says "Model Benchmarks" (not "Patient Benchmarks")
- ✅ Benchmark script calculates cost savings
- ✅ MedGemma results have cost savings: $13,315 (45.8% capture rate)
- ✅ Dashboard has cost savings display section

❌ **Database Not Updated:**
- ❌ Supabase database missing 4 cost savings columns
- ❌ Dashboard can't show data without these columns

## 3-Step Fix

### Step 1: Run Database Migration (2 minutes)

1. Open your Supabase SQL Editor:
   - Go to: https://supabase.com/dashboard
   - Select your project
   - Click "SQL Editor" in left sidebar
   - Click "+ New query"

2. Copy the **entire** contents of this file:
   ```bash
   cat sql/combined_cost_savings_migration.sql
   ```

3. Paste into SQL Editor and click **RUN** (or press Cmd+Enter)

4. You should see output confirming 4 columns were added

### Step 2: Re-run Benchmarks (10 minutes)

```bash
# Re-run all models to get fresh cost savings data
python3 scripts/generate_patient_benchmarks.py --model all
```

Expected output includes:
```
💰 COST SAVINGS METRICS:
  Total Potential Savings:   $13,315.00
  Total Missed Savings:      $15,775.00
  Avg Savings per Patient:   $289.46
  Savings Capture Rate:      45.8%
```

### Step 3: Push to Supabase & Restart (1 minute)

```bash
# Push all results to database
./scripts/push_local_benchmarks.sh

# Restart dashboard (Ctrl+C to stop current one, then:)
python3 -m streamlit run pages/benchmark_monitoring.py --server.port 8502
```

## Verify It Worked

1. Open dashboard: http://localhost:8502
2. Go to **📊 Current Snapshot** tab
3. Scroll down - you should see:

```
💰 Cost Savings Metrics
┌─────────────────────────┬────────────────────┬────────────────┬──────────────────┐
│ Total Potential Savings │ Avg Savings/Patient│ Avg Capture Rate│ Total Missed     │
│ $13,315.00              │ $289.46            │ 45.8%          │ $15,775.00       │
└─────────────────────────┴────────────────────┴────────────────┴──────────────────┘
```

4. Go to **🏥 Model Benchmarks** tab (should say "Model" not "Patient")

## What If It Doesn't Work?

Run the verification script:
```bash
python3 scripts/verify_cost_savings.py
```

This will tell you exactly what's missing.

## Understanding the Metrics

- **Total Potential Savings**: $ from billing errors the model detected
- **Total Missed Savings**: $ from errors the model missed  
- **Avg Savings per Patient**: Average $ value per patient analyzed
- **Savings Capture Rate**: % of total possible savings captured (ROI metric)

Higher capture rate = better ROI for automated error detection.

## Files You Need

All files are ready:
- ✅ `sql/combined_cost_savings_migration.sql` - Database migration
- ✅ `scripts/generate_patient_benchmarks.py` - Updated benchmark script
- ✅ `scripts/verify_cost_savings.py` - Verification tool
- ✅ `pages/benchmark_monitoring.py` - Updated dashboard

## Questions?

See `COST_SAVINGS_SETUP.md` for detailed documentation.
