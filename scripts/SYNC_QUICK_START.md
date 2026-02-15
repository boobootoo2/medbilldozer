# Supabase Data Sync - Quick Start Guide

## 🚀 Quick Sync Process

### Step 1: Set Environment Variables

You need **4** environment variables (use service_role keys, NOT anon keys):

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-main-service-role-key"
export SUPABASE_BETA_URL="https://your-beta-project.supabase.co"
export SUPABASE_BETA_KEY="your-beta-service-role-key"
```

**Where to find these:**
1. Go to Supabase project → Settings → API
2. Copy **service_role** key (NOT anon/public key!)
3. The service_role key starts with `eyJ...` and is very long

### Step 2: Verify Keys (Optional but Recommended)

```bash
python3 scripts/verify_supabase_keys.py
```

This will tell you if you're using the correct key type.

### Step 3: Run the Sync

```bash
python3 scripts/sync_supabase_data.py
```

Expected output:
```
✅ Inserted 36 records into benchmark_transactions
✅ Inserted 36 records into benchmark_snapshots
✅ Tables synced: 2/5
```

---

## 🔧 Troubleshooting

### Problem: "Missing required environment variables"

**Solution:** Export all 4 environment variables listed in Step 1.

### Problem: "new row violates row-level security policy"

**Cause:** You're using the anon key instead of service_role key.

**Solution:** 
1. Go to Supabase → Settings → API
2. Copy the **service_role** key (NOT anon key)
3. Update `SUPABASE_BETA_KEY` environment variable

**Temporary workaround:**
```bash
# In beta Supabase SQL Editor, run:
# scripts/disable_rls_beta.sql

# Then sync:
python3 scripts/sync_supabase_data.py

# Then re-enable RLS:
# scripts/enable_rls_beta.sql
```

### Problem: "violates foreign key constraint"

**Cause:** Tables synced in wrong order.

**Solution:** This is now fixed in the script! Make sure you have the latest version where `benchmark_transactions` is synced BEFORE `benchmark_snapshots`.

### Problem: "Could not find column in schema cache"

**Cause:** Beta schema is missing columns from production migrations.

**Solution:**
1. Drop beta tables:
```sql
DROP TABLE IF EXISTS public.benchmark_snapshots CASCADE;
DROP TABLE IF EXISTS public.benchmark_transactions CASCADE;
```

2. Re-run: `scripts/setup_beta_schema.sql`

3. Re-run sync

---

## 📋 Table Order (Important!)

The sync MUST happen in this order due to foreign key constraints:

1. `benchmark_transactions` (parent table)
2. `benchmark_snapshots` (has FK to transactions)

The script now handles this automatically.

---

## 🔍 Verify Sync Success

After sync completes, check beta Supabase:

```sql
-- Check record counts
SELECT 'transactions' as table_name, COUNT(*) as records 
FROM benchmark_transactions
UNION ALL
SELECT 'snapshots', COUNT(*) 
FROM benchmark_snapshots;

-- Check latest data
SELECT model_version, created_at 
FROM benchmark_transactions 
ORDER BY created_at DESC 
LIMIT 5;
```

---

## 🤖 Automated Daily Sync (GitHub Actions)

The workflow `.github/workflows/sync_supabase_data.yml` will run automatically at 2 AM UTC daily.

**Setup:**
1. Go to GitHub repo → Settings → Secrets
2. Add these secrets:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_BETA_URL`
   - `SUPABASE_BETA_KEY`

**Manual trigger:**
- Go to Actions tab → "Sync Supabase Data" → Run workflow

---

## 📝 Files Reference

- `scripts/sync_supabase_data.py` - Main sync script
- `scripts/setup_beta_schema.sql` - Create beta tables
- `scripts/disable_rls_beta.sql` - Temporarily disable RLS
- `scripts/enable_rls_beta.sql` - Re-enable RLS with policies
- `scripts/verify_supabase_keys.py` - Verify key types
- `scripts/SUPABASE_SYNC.md` - Detailed documentation
