# Benchmark Results Directory

## Architecture

Benchmark results are **NOT stored in git**. Instead, they are:

1. **Generated** by `scripts/generate_benchmarks.py`
2. **Converted** to monitoring format by `scripts/convert_benchmark_to_monitoring.py`
3. **Uploaded** to Supabase by `scripts/push_to_supabase.py`
4. **Visualized** in the dashboard by querying Supabase

## Why Not Commit Results?

### Old Approach (Problematic)
- ❌ Results committed to git → repo bloat
- ❌ Merge conflicts on every benchmark run
- ❌ Git history polluted with data changes
- ❌ Hard to query historical data
- ❌ No central source of truth

### New Approach (Database-Driven)
- ✅ Results stored in Supabase database
- ✅ Clean git history (code only)
- ✅ No merge conflicts
- ✅ Easy to query with SQL
- ✅ Dashboard pulls live data
- ✅ Automatic versioning with snapshots

## Local Development

### Running Benchmarks Locally

```bash
# Generate benchmarks (stored locally)
python3 scripts/generate_benchmarks.py --model openai

# Convert to monitoring format
python3 scripts/convert_benchmark_to_monitoring.py \
  --input benchmarks/results/aggregated_metrics_openai.json \
  --output openai_benchmark_results.json \
  --model openai

# Push to Supabase (requires .env with credentials)
python3 scripts/push_to_supabase.py \
  --input openai_benchmark_results.json \
  --environment local \
  --commit-sha $(git rev-parse HEAD)
```

### Viewing Results

```bash
# Local dashboard (pulls from Supabase)
make monitoring-dashboard

# Or manually
streamlit run pages/production_stability.py
```

Visit: <http://localhost:8502>

## CI/CD Workflow

### Automated Process

1. **Trigger**: Push to `develop` or scheduled (daily 2am UTC)
2. **Run**: `.github/workflows/run_benchmarks.yml`
   - Runs benchmarks for all models
   - Converts to monitoring format
   - Uploads as GitHub artifact
3. **Persist**: `.github/workflows/benchmark-persist.yml`
   - Downloads artifacts
   - Pushes to Supabase
   - Posts summary

### Required Secrets

Configure in GitHub Settings → Secrets:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Database access key
- `OPENAI_API_KEY`: For OpenAI benchmarks
- `GOOGLE_API_KEY`: For Gemini benchmarks

## Files in This Directory

### Kept in Git
- `README.md` (this file) - Documentation
- `.gitkeep` - Preserves directory structure
- `aggregated_metrics.example.json` - Example result format

### Ignored by Git (Local Only)
- `*.json` - All actual benchmark results
- Generated during local development
- Automatically cleaned by CI/CD

## Querying Results

### From Dashboard
Use the monitoring dashboard tabs:
1. **Current Snapshot** - Latest results
2. **Performance Trends** - Time series
3. **Model Comparison** - Side-by-side
4. **Regression Detection** - Alerts
5. **Snapshot History** - Version control

### From Database
Connect directly to Supabase:

```python
from supabase import create_client
import os

client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

# Get latest snapshots
snapshots = client.table('benchmark_snapshots')\
    .select('*')\
    .eq('is_current', True)\
    .execute()

# Get history for a model
history = client.table('benchmark_snapshots')\
    .select('*')\
    .eq('model_version', 'openai-v1.0')\
    .order('snapshot_version', desc=True)\
    .execute()
```

## Migration Notes

### If You Have Old Committed Results

The old workflow committed results to git. These have been removed from tracking:

```bash
# Files removed from git (but kept locally)
git rm --cached benchmarks/results/*.json
```

Your local files are **preserved** but won't be tracked anymore.

### Uploading Historical Data

To upload existing local results to the database:

```bash
# For each existing result file
for model in openai gemini baseline medgemma; do
  if [ -f "benchmarks/results/aggregated_metrics_${model}.json" ]; then
    python3 scripts/convert_benchmark_to_monitoring.py \
      --input "benchmarks/results/aggregated_metrics_${model}.json" \
      --output "${model}_results.json" \
      --model "${model}"

    python3 scripts/push_to_supabase.py \
      --input "${model}_results.json" \
      --environment local \
      --commit-sha $(git rev-parse HEAD)
  fi
done
```

## Troubleshooting

### Dashboard Shows No Data

**Cause**: No results in Supabase database

**Solution**:
1. Check Supabase credentials in `.env`
2. Run benchmarks and push results (see above)
3. Verify data with: `python3 scripts/check_snapshots.py`

### Benchmarks Not Persisting from CI/CD

**Cause**: GitHub secrets not configured or workflow failed

**Solution**:
1. Check GitHub Actions logs
2. Verify secrets are set correctly
3. See `docs/GITHUB_ACTIONS_BENCHMARK_FIX.md`

### Local Results Not Showing in Dashboard

**Cause**: Dashboard pulls from database, not local files

**Solution**: Push local results to database (see "Uploading Historical Data" above)

## Related Documentation

- `docs/GITHUB_ACTIONS_BENCHMARK_FIX.md` - CI/CD setup
- `docs/MONITORING_DASHBOARD_COMPLETE.md` - Dashboard overview
- `BENCHMARK_WORKFLOW_QUICKSTART.md` - Quick reference
- `STREAMLIT_CLOUD_DEPLOYMENT.md` - Cloud deployment

## Summary

📊 **Results live in the database, not in git**

✅ Run benchmarks locally → files stay local
✅ Push to Supabase → visible in dashboard
✅ Clean git history → code only, no data
✅ Query anywhere → SQL, API, or dashboard
