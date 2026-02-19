# Production Database Setup Guide

This guide walks through setting up the `clinical_validation_snapshots` table in your production Supabase database.

## Issue

The migration failed with:
```
❌ Error accessing table 'clinical_validation_snapshots'
Perhaps you meant the table 'public.benchmark_snapshots'
```

This means the production database has `benchmark_snapshots` but not `clinical_validation_snapshots`.

## Solution: Create the Table

### Option 1: Supabase Dashboard (Recommended)

1. **Open Supabase Dashboard:**
   - Go to [https://app.supabase.com](https://app.supabase.com)
   - Select your production project

2. **Open SQL Editor:**
   - Click "SQL Editor" in the left sidebar
   - Click "New query"

3. **Copy and Paste SQL:**
   - Open [`scripts/setup_clinical_validation_schema.sql`](scripts/setup_clinical_validation_schema.sql)
   - Copy the entire contents
   - Paste into the SQL Editor

4. **Run the Script:**
   - Click "Run" or press `Cmd+Enter` (Mac) / `Ctrl+Enter` (Windows)
   - Wait for success message: "Success. No rows returned"

5. **Verify Table Created:**
   ```sql
   SELECT table_name
   FROM information_schema.tables
   WHERE table_schema = 'public'
   AND table_name = 'clinical_validation_snapshots';
   ```

   Should return one row with `clinical_validation_snapshots`.

### Option 2: Supabase CLI

If you have the Supabase CLI installed:

```bash
# Link to your project (if not already linked)
supabase link --project-ref your-project-ref

# Run the migration
supabase db push --file scripts/setup_clinical_validation_schema.sql
```

### Option 3: psql

If you have direct database access:

```bash
psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres" \
  -f scripts/setup_clinical_validation_schema.sql
```

## Verify Setup

After creating the table, verify it's accessible:

### Test Query in SQL Editor

```sql
-- Check table structure
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'clinical_validation_snapshots'
ORDER BY ordinal_position;

-- Check RLS policies
SELECT policyname, cmd, qual
FROM pg_policies
WHERE tablename = 'clinical_validation_snapshots';

-- Check table is empty (or has data from beta)
SELECT COUNT(*) FROM clinical_validation_snapshots;
```

### Test with Python

```bash
python scripts/verify_migration_status.py
```

**Expected Output:**
```
🔍 Clinical Validation Data Migration Status
✅ Connected to beta: https://zrhlpitzonhftigmdvgz.supabase.co
✅ Connected to production: https://azoxzggvqhkugyysbabz.supabase.co

======================================================================
📊 Production Database
======================================================================
Total Records:      0
⚠️  No records found
```

## Run Migration

Once the table exists, run the migration:

```bash
# Dry run first
python scripts/migrate_beta_to_prod.py --dry-run

# If dry run looks good, run actual migration
python scripts/migrate_beta_to_prod.py
```

**Expected Success Output:**
```
🚀 Starting Clinical Validation Data Migration
======================================================================

📊 Fetching snapshots from beta database...
✅ Found 150 snapshots in beta database

🔍 Checking for existing snapshots in production...
✅ Found 0 existing snapshots in production

📦 Migrating 150 snapshots...
  ✅ Migrated snapshot abc-123 (created: 2026-02-10)
  ✅ Migrated snapshot def-456 (created: 2026-02-11)
  ...

======================================================================
📊 Migration Summary
======================================================================
Total snapshots in beta:    150
Skipped (already exist):    0
Successfully migrated:      150
Failed:                     0
======================================================================

✅ Migration completed successfully!
```

## Troubleshooting

### Error: "permission denied for table"

**Solution:** Make sure you're using the service role key, not anon key.

```bash
# Check your .env file has:
SUPABASE_SERVICE_ROLE_KEY=eyJ...  # Not SUPABASE_ANON_KEY
```

### Error: "Could not find the table"

**Solution:** The SQL script didn't run successfully. Check:

1. Did the SQL script complete without errors?
2. Is the table in the correct schema (`public`)?
3. Refresh the Supabase Dashboard table list

### Error: "relation does not exist"

**Solution:** Run the setup SQL script first, then retry.

### Table exists but migration still fails

**Solution:** Check RLS policies:

```sql
-- Verify service role has access
SELECT * FROM clinical_validation_snapshots LIMIT 1;
```

If this fails with permission error, re-run the RLS section of the setup script.

## Post-Migration Verification

### 1. Check Record Count

```bash
python scripts/verify_migration_status.py
```

Should show matching counts in beta and production.

### 2. Check Dashboard

```bash
streamlit run pages/production_stability.py
```

Navigate to "🏥 Clinical Validation" tab. Should display migrated data.

### 3. Check Latest Record

```sql
SELECT
    model_version,
    created_at,
    total_patients,
    successful,
    domain_detection
FROM clinical_validation_snapshots
ORDER BY created_at DESC
LIMIT 5;
```

### 4. Run Test Benchmark

```bash
python scripts/run_clinical_validation_benchmarks.py \
  --model gpt-4o-mini \
  --push-to-supabase
```

Should successfully push to production.

## Database Schema Details

The `clinical_validation_snapshots` table includes:

### Core Fields
- `id` (UUID): Primary key
- `created_at`: Timestamp
- `model_version`: Model identifier (e.g., "gpt-4o-mini")
- `environment`: "production" or "beta"
- `benchmark_type`: "clinical_validation"

### Metrics (JSONB)
- `accuracy`: Overall accuracy
- `error_detection_rate`: Rate of detecting clinical errors
- `false_positive_rate`: False positive rate
- `total_scenarios`: Number of test scenarios
- `correct_determinations`: Number of correct responses
- `scenarios_by_modality`: Results by imaging type

### Computed Fields (for dashboard queries)
- `total_patients`: Auto-computed from metrics
- `successful`: Auto-computed success count
- `failed`: Auto-computed failure count
- `f1_score`: Accuracy metric
- `domain_detection`: Error detection percentage

### Indexes
- `created_at` (descending) - for time-series queries
- `model_version` - for filtering by model
- `environment` - for filtering by env
- Composite indexes for optimized dashboard queries

### Row Level Security (RLS)
- ✅ Service role: Full access (read/write/delete)
- ✅ Authenticated: Read access
- ✅ Anon: Read access (for public dashboard)

## Next Steps

After successful migration:

1. ✅ Verify dashboard displays data correctly
2. ✅ Test benchmark workflow in GitHub Actions
3. ✅ Monitor for 7 days
4. ✅ Update environment variables to remove beta references
5. ✅ Decommission beta database (optional)

## Support

For issues:
- Check [BETA_TO_PROD_MIGRATION.md](BETA_TO_PROD_MIGRATION.md)
- Review [BENCHMARK_REFACTORING_SUMMARY.md](BENCHMARK_REFACTORING_SUMMARY.md)
- Run `python scripts/verify_migration_status.py`

## Quick Reference

```bash
# 1. Setup table (run SQL in Supabase Dashboard)
#    See: scripts/setup_clinical_validation_schema.sql

# 2. Verify setup
python scripts/verify_migration_status.py

# 3. Run migration (dry run first)
python scripts/migrate_beta_to_prod.py --dry-run
python scripts/migrate_beta_to_prod.py

# 4. Verify migration
python scripts/verify_migration_status.py

# 5. Test dashboard
streamlit run pages/production_stability.py

# 6. Test benchmark workflow
python scripts/run_clinical_validation_benchmarks.py \
  --model gpt-4o-mini \
  --push-to-supabase
```
