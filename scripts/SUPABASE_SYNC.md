# Supabase Data Sync

This directory contains scripts for syncing data between the main (production) Supabase instance and the beta (testing) Supabase instance.

## Overview

The `sync_supabase_data.py` script copies all data from the main Supabase database to the beta Supabase database. This is useful for:

- Testing new features with production-like data
- Debugging issues in a safe environment
- Maintaining consistency between environments

## Setup

### 1. Create Beta Database Schema

Before syncing data, you need to create the tables in your beta Supabase database:

1. Open your **beta** Supabase project dashboard
2. Go to **SQL Editor**
3. Open the file `scripts/setup_beta_schema.sql` from this repository
4. Copy and paste the entire SQL script
5. Click **Run** to execute

This creates:
- ✅ `benchmark_snapshots` table
- ✅ `benchmark_transactions` table  
- ✅ `v_performance_trends` view
- ✅ Proper indexes and RLS policies

**Note**: If tables already exist, the script will skip creation (safe to run multiple times).

### 2. Install Dependencies

```bash
pip install supabase
```

### 3. Set Environment Variables

You need credentials for both Supabase instances:

```bash
# Main/Production Supabase
export SUPABASE_URL="https://your-main-project.supabase.co"
export SUPABASE_KEY="your-main-service-role-key"

# Beta/Testing Supabase
export SUPABASE_BETA_URL="https://your-beta-project.supabase.co"
export SUPABASE_BETA_KEY="your-beta-service-role-key"
```

⚠️ **Important**: Use service role keys (not anon keys) to ensure you have full access to all data.

### 4. Configure GitHub Secrets

For the automated workflow, add these secrets to your GitHub repository:

1. Go to repository Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_BETA_URL`
   - `SUPABASE_BETA_KEY`

## Usage

### Manual Sync

#### Sync All Tables

```bash
python scripts/sync_supabase_data.py
```

#### Dry Run (Test Without Making Changes)

```bash
python scripts/sync_supabase_data.py --dry-run
```

#### Sync Specific Tables

```bash
python scripts/sync_supabase_data.py --tables receipts,providers,insurance_plans
```

#### Verbose Output

```bash
python scripts/sync_supabase_data.py --verbose
```

### Automated Sync via GitHub Actions

The sync runs automatically via GitHub Actions:

#### Schedule
- Runs daily at 2 AM UTC
- Syncs all default tables

#### Manual Trigger

1. Go to Actions → Sync Supabase Data
2. Click "Run workflow"
3. Configure options:
   - **Dry run**: Test without making changes
   - **Tables**: Specify tables to sync (leave empty for all)
4. Click "Run workflow"

## Default Tables

The script syncs these tables in order (respecting foreign key dependencies):

1. `receipts`
2. `providers`
3. `insurance_plans`
4. `benchmark_snapshots`
5. `benchmark_transactions`

## How It Works

1. **Check**: Verifies the table exists in both source and target databases
2. **Fetch**: Retrieves all data from each table in the source database
3. **Clear**: Removes existing data from the target table
4. **Insert**: Copies data to the target table in batches (100 records at a time)
5. **Report**: Provides a summary of sync statistics

**Important**: Both databases must have the same table schema. If a table doesn't exist in the target database, it will be skipped automatically.

## Safety Features

- **Dry Run Mode**: Test the sync without making any changes
- **Batch Processing**: Inserts data in small batches to avoid API limits
- **Error Handling**: Continues syncing other tables if one fails
- **Detailed Logging**: Shows progress and results for each table

## Troubleshooting

### Authentication Errors

```
Error: Missing required environment variables
```

**Solution**: Ensure all four environment variables are set correctly.

### API Rate Limits

```
Error inserting into table: Rate limit exceeded
```

**Solution**: The script uses batch processing (100 records at a time) to avoid this. If you still hit limits, contact Supabase support to increase limits.

### Foreign Key Constraints

```
Error inserting into table: Foreign key constraint violation
```

**Solution**: Tables are synced in dependency order. If you're syncing specific tables, make sure to include parent tables first.

### No Data Synced

```
No data found in source table
```

**Solution**: This is normal if the source table is empty. Check that:
1. You're connected to the correct source database
2. The table name is spelled correctly
3. Your service role key has read access

### Table Not Found

```
⚠️  Table does not exist in source/target database - skipping
💡 Create the table in target database first, then re-run sync
```

**Solution**: The table doesn't exist in one of the databases:
1. **Target database missing table**: Create the table schema in the beta/target database first
2. **Source database missing table**: Update the DEFAULT_TABLES list in the script to remove non-existent tables
3. **Both databases should have identical schemas** before syncing data

### Streamlit App Error (postgrest.exceptions.APIError)

```
postgrest.exceptions.APIError: This app has encountered an error.
File "pages/production_stability.py", line 90
    environments = data_access.get_available_environments()
```

**Solution**: The beta Streamlit app is trying to access tables that don't exist in beta Supabase:

1. **Run the schema setup script first**: 
   - Go to beta Supabase → SQL Editor
   - Run `scripts/setup_beta_schema.sql`
   
2. **Sync the data**:
   ```bash
   python scripts/sync_supabase_data.py
   ```

3. **Restart the Streamlit app**: 
   - Go to Streamlit Cloud → Manage app → Reboot

The app needs both the schema (tables/views) AND the data to function properly.

## Examples

### Example 1: Test Sync Before Running

```bash
# First, do a dry run to see what would happen
python scripts/sync_supabase_data.py --dry-run --verbose

# If everything looks good, run for real
python scripts/sync_supabase_data.py --verbose
```

### Example 2: Sync Only Benchmark Data

```bash
python scripts/sync_supabase_data.py --tables benchmark_snapshots,benchmark_transactions
```

### Example 3: Automated Daily Sync

The GitHub Actions workflow automatically syncs all data daily. No manual intervention needed!

## Output Example

```
======================================================================
🔄 SUPABASE DATA SYNC
======================================================================

📋 Tables to sync: receipts, providers, insurance_plans, benchmark_snapshots
📊 Total tables: 4

📋 Syncing table: receipts
  📥 Fetching data from source...
  📊 Found 150 records
  🗑️  Clearing target table...
  📤 Inserting data into target...
  ✅ Inserted 150 records into receipts

📋 Syncing table: providers
  📥 Fetching data from source...
  📊 Found 45 records
  🗑️  Clearing target table...
  📤 Inserting data into target...
  ✅ Inserted 45 records into providers

======================================================================
📊 SYNC SUMMARY
======================================================================
✅ Tables synced: 4/4
📝 Records copied: 195
⏭️  Tables skipped: 0
❌ Errors: 0
⏱️  Duration: 12.34s
======================================================================

✅ Sync completed successfully!
```

## Security Considerations

- Service role keys have full database access - protect them carefully
- Never commit credentials to version control
- Use GitHub Secrets for automated workflows
- Beta environment should not contain real patient data (use fictional data only)
- Regularly rotate service role keys

## Contributing

When adding new tables to sync:

1. Add table name to `DEFAULT_TABLES` in `sync_supabase_data.py`
2. Ensure tables are ordered correctly (parent tables before child tables)
3. Test with `--dry-run` first
4. Update this README with the new table

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review GitHub Actions logs for automated runs
3. Check Supabase logs in both dashboards
4. Open an issue in the repository
