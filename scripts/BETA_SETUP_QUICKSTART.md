# Beta Supabase Setup - Quick Start Guide

Follow these steps to set up and sync your beta Supabase environment.

## 🎯 Goal
Get the beta Streamlit app working with a copy of production data.

## ✅ Prerequisites
- Beta Supabase project created
- Service role keys for both main and beta Supabase

## 📋 Steps

### Step 1: Create Database Schema (Beta Supabase)

1. Open your **beta** Supabase dashboard
2. Navigate to **SQL Editor** (left sidebar)
3. Click **New Query**
4. Copy the contents of `scripts/setup_beta_schema.sql`
5. Paste into the SQL editor
6. Click **Run** (or press Cmd/Ctrl + Enter)

✅ **Expected**: You should see "Beta Supabase schema setup complete!" message

### Step 2: Set Environment Variables (Local Machine)

```bash
# Main Supabase (source)
export SUPABASE_URL="https://your-main-project.supabase.co"
export SUPABASE_KEY="your-main-service-role-key"

# Beta Supabase (target)
export SUPABASE_BETA_URL="https://your-beta-project.supabase.co"
export SUPABASE_BETA_KEY="your-beta-service-role-key"
```

### Step 3: Test Connection (Dry Run)

```bash
python scripts/sync_supabase_data.py --dry-run
```

✅ **Expected**: Should show tables being checked and simulated sync

### Step 4: Sync Data

```bash
python scripts/sync_supabase_data.py
```

✅ **Expected**: Should copy data from main to beta Supabase

### Step 5: Verify Beta Streamlit App

1. Go to your beta Streamlit app URL
2. Navigate to pages that use Supabase data (e.g., Production Stability)
3. Verify data loads without errors

✅ **Expected**: App should load data successfully

## 🔄 Daily Sync (GitHub Actions)

### One-Time Setup

1. Go to GitHub → Repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_BETA_URL`
   - `SUPABASE_BETA_KEY`

### Automatic Daily Sync

The workflow runs automatically every day at 2 AM UTC. No action needed!

### Manual Sync via GitHub

1. Go to Actions tab
2. Select "Sync Supabase Data" workflow
3. Click "Run workflow"
4. Configure options (dry run, specific tables)
5. Click "Run workflow"

## 🐛 Troubleshooting

### Error: "Could not find the table"

**Problem**: Table doesn't exist in beta database

**Solution**: Run Step 1 again (setup_beta_schema.sql)

### Error: "Missing required environment variables"

**Problem**: Environment variables not set

**Solution**: Run Step 2 again

### Error: "APIError" on Streamlit App

**Problem**: Schema exists but no data, or stale data

**Solution**: Run Step 4 again (sync data), then reboot Streamlit app

### Error: "Rate limit exceeded"

**Problem**: Too many requests to Supabase API

**Solution**: Wait a few minutes and try again. Script uses batching to avoid this.

## 📊 Tables Synced

The sync script copies these tables:
- ✅ `benchmark_snapshots` - Main benchmark data
- ✅ `benchmark_transactions` - Transaction details

**Note**: `receipts`, `providers`, and `insurance_plans` tables are skipped if they don't exist (that's normal).

## 🎛️ Advanced Options

### Sync Only Benchmark Data

```bash
python scripts/sync_supabase_data.py --tables benchmark_snapshots,benchmark_transactions
```

### Verbose Output

```bash
python scripts/sync_supabase_data.py --verbose
```

### Check What Will Sync Without Making Changes

```bash
python scripts/sync_supabase_data.py --dry-run --verbose
```

## 📝 Next Steps

After setup is complete:

1. ✅ Beta database has schema
2. ✅ Beta database has data  
3. ✅ Beta Streamlit app works
4. ✅ Automated daily sync configured

Your beta environment is now ready for testing!

## 🆘 Need Help?

- Check `scripts/SUPABASE_SYNC.md` for detailed documentation
- Review GitHub Actions logs for automated runs
- Check Supabase logs in both dashboards
- Open an issue in the repository
