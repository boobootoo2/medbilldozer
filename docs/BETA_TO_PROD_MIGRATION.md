# Clinical Validation Data Migration Guide

This guide explains how to migrate clinical validation benchmark data from the beta database to production as part of the transition from BETA-gated features to general availability.

## Overview

With the removal of the `BETA=true` requirement, clinical validation features are now generally available. This migration moves existing benchmark data from the beta database to the production database.

## Prerequisites

### Environment Variables Required

**Source Database (Beta):**
- `SUPABASE_BETA_URL` or `SUPABASE_CLINICAL_URL`: Beta database URL
- `SUPABASE_BETA_KEY` or `SUPABASE_CLINICAL_KEY`: Beta database API key

**Destination Database (Production):**
- `SUPABASE_URL`: Production database URL
- `SUPABASE_SERVICE_ROLE_KEY`: Production service role key (requires write access)

### Dependencies

Ensure you have the required Python packages:

```bash
pip install supabase python-dotenv
```

## Migration Process

### Step 1: Dry Run (Recommended)

First, perform a dry run to verify the migration without writing any data:

```bash
python scripts/migrate_beta_to_prod.py --dry-run
```

This will:
- Connect to both databases
- Count records in beta
- Check for existing records in production
- Simulate the migration
- Display what would be migrated

**Expected Output:**
```
🔄 Clinical Validation Data Migration
Mode: DRY RUN
Duplicate handling: SKIP

✅ Connected to source database: https://zrhlpitzonhftigmdvgz.supabase.co
✅ Connected to destination database: https://your-prod-database.supabase.co

🔍 Verifying database tables...
✅ Tables verified successfully

📊 Fetching snapshots from beta database...
✅ Found 150 snapshots in beta database

🔍 Checking for existing snapshots in production...
✅ Found 0 existing snapshots in production

📦 Migrating 150 snapshots...
  [DRY RUN] Would migrate snapshot abc-123 (created: 2026-02-10)
  ...

📊 Migration Summary
Total snapshots in beta:    150
Skipped (already exist):    0
Successfully migrated:      150
Failed:                     0

⚠️  This was a DRY RUN. No data was actually migrated.
Run without --dry-run to perform the actual migration.
```

### Step 2: Verify Production Table Schema

Ensure the `clinical_validation_snapshots` table exists in production with the correct schema:

```sql
-- Production database should have this table
CREATE TABLE clinical_validation_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    environment TEXT,
    model_version TEXT,
    total_patients INTEGER,
    successful INTEGER,
    failed INTEGER,
    f1_score NUMERIC,
    precision_score NUMERIC,
    recall NUMERIC,
    domain_detection NUMERIC,
    avg_confidence NUMERIC,
    performance_data JSONB,
    -- Add other columns as needed
);
```

### Step 3: Run Live Migration

Once the dry run looks good, perform the actual migration:

```bash
python scripts/migrate_beta_to_prod.py
```

By default, this will:
- Skip records that already exist in production (based on ID)
- Migrate only new records
- Show progress for every 10 records

### Step 4: Verify Migration

After migration, verify the data in production:

```bash
# Count records
python -c "
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
result = client.table('clinical_validation_snapshots').select('id', count='exact').execute()
print(f'Total records in production: {len(result.data)}')
"
```

Check the dashboard:
```bash
streamlit run pages/production_stability.py
```

Navigate to the "🏥 Clinical Validation" tab and verify the data appears correctly.

## Migration Options

### Skip Duplicates (Default)

```bash
python scripts/migrate_beta_to_prod.py --skip-duplicates
```

Skips records that already exist in production. Safe for re-running the migration.

### Force Overwrite

```bash
python scripts/migrate_beta_to_prod.py --force
```

Overwrites existing records in production. Use with caution.

### Dry Run

```bash
python scripts/migrate_beta_to_prod.py --dry-run
```

Simulates the migration without writing data. Always recommended to run first.

## Troubleshooting

### Error: "Beta database credentials not found"

**Solution:** Ensure you have set the beta database environment variables:

```bash
# In .env file
SUPABASE_BETA_URL=https://zrhlpitzonhftigmdvgz.supabase.co
SUPABASE_BETA_KEY=your-beta-key
```

Or use the new naming:
```bash
SUPABASE_CLINICAL_URL=https://zrhlpitzonhftigmdvgz.supabase.co
SUPABASE_CLINICAL_KEY=your-clinical-key
```

### Error: "Production database credentials not found"

**Solution:** Ensure you have set the production database environment variables:

```bash
# In .env file
SUPABASE_URL=https://your-prod-db.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

**Important:** Use the service role key (not anon key) for write access.

### Error: "Destination table not accessible"

**Solution:** Create the table in production or ensure your service role key has write access:

```sql
-- Grant access to service role
GRANT ALL ON clinical_validation_snapshots TO service_role;
```

### Migration Failed Partway Through

The migration is idempotent and can be safely re-run. Use the default `--skip-duplicates` option:

```bash
python scripts/migrate_beta_to_prod.py
```

This will skip already-migrated records and continue with the remaining ones.

## Post-Migration

### 1. Update Environment Variables

After successful migration, you can update your production `.env` to use the cleaner variable names:

```bash
# Old (still supported for backward compatibility)
SUPABASE_BETA_URL=...
SUPABASE_BETA_KEY=...

# New (preferred)
SUPABASE_CLINICAL_URL=...
SUPABASE_CLINICAL_KEY=...
```

Or point to production database:

```bash
# Use production database for clinical validation
# (if you've merged beta and prod databases)
SUPABASE_CLINICAL_URL=${SUPABASE_URL}
SUPABASE_CLINICAL_KEY=${SUPABASE_SERVICE_ROLE_KEY}
```

### 2. Verify Dashboard Access

Test the dashboard without BETA mode:

```bash
# Remove or set to false
BETA=false

# Start dashboard
streamlit run pages/production_stability.py
```

The Clinical Validation tab should be visible and populated with migrated data.

### 3. Decommission Beta Database (Optional)

Once you've verified the migration is successful and the production system is working:

1. Keep beta database running for a grace period (7-30 days)
2. Monitor for any issues
3. Once confirmed stable, you can decommission the beta database
4. Archive any necessary data for compliance

## Data Validation

### Verify Record Counts Match

```python
# Count beta records
beta_count = beta_client.table('clinical_validation_snapshots').select('id', count='exact').execute()

# Count production records
prod_count = prod_client.table('clinical_validation_snapshots').select('id', count='exact').execute()

print(f"Beta: {len(beta_count.data)}")
print(f"Prod: {len(prod_count.data)}")
```

### Verify Date Ranges

```python
# Check earliest and latest records
response = prod_client.table('clinical_validation_snapshots') \
    .select('created_at') \
    .order('created_at', desc=False) \
    .limit(1) \
    .execute()

print(f"Earliest record: {response.data[0]['created_at']}")

response = prod_client.table('clinical_validation_snapshots') \
    .select('created_at') \
    .order('created_at', desc=True) \
    .limit(1) \
    .execute()

print(f"Latest record: {response.data[0]['created_at']}")
```

## Rollback Plan

If issues arise after migration:

1. **Re-enable BETA mode temporarily:**
   ```bash
   BETA=true streamlit run pages/production_stability.py
   ```
   This will show the old beta tab alongside the new general availability tab.

2. **Point back to beta database:**
   Ensure `SUPABASE_CLINICAL_URL` and `SUPABASE_CLINICAL_KEY` point to beta database.

3. **Fix issues and re-migrate:**
   Once fixed, re-run the migration with `--force` if needed.

## Support

For issues or questions:
- Check the [GitHub Issues](https://github.com/your-org/medbilldozer/issues)
- Contact the MLOps team
- Review the migration script logs

## Summary Checklist

- [ ] Set up all required environment variables
- [ ] Run dry-run migration and review output
- [ ] Verify production table schema exists
- [ ] Run actual migration
- [ ] Verify record counts match
- [ ] Test dashboard with migrated data
- [ ] Update environment variables to new naming
- [ ] Monitor for 7 days
- [ ] (Optional) Decommission beta database
