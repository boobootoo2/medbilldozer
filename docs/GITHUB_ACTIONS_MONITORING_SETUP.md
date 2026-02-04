# GitHub Actions Setup for Benchmark Monitoring

This guide walks you through setting up automated benchmark persistence to Supabase via GitHub Actions.

## 📋 Overview

The automation consists of two workflows:

1. **`run_benchmarks.yml`** - Runs benchmarks and uploads results as artifacts
2. **`benchmark-persist.yml`** - Downloads artifacts and persists to Supabase

```
┌─────────────────────┐
│  Run Benchmarks     │
│  (run_benchmarks)   │
└──────────┬──────────┘
           │
           │ uploads artifact
           │ (benchmark_results.json)
           ▼
┌─────────────────────┐
│  Persist Results    │
│ (benchmark-persist) │
└──────────┬──────────┘
           │
           │ pushes to Supabase
           ▼
┌─────────────────────┐
│  Supabase Database  │
│  (monitoring layer) │
└─────────────────────┘
```

## 🔧 Step 1: Configure GitHub Secrets

GitHub Actions needs your Supabase credentials to persist data.

### 1.1 Get Your Supabase Credentials

1. Go to your Supabase Dashboard: https://app.supabase.com/
2. Select your project
3. Navigate to: **Project Settings** → **API**
4. Copy these values:
   - **Project URL** (e.g., `https://abcdefg.supabase.co`)
   - **service_role** key (under "Project API keys")
   
   ⚠️ **IMPORTANT**: Use the `service_role` key (not `anon`), as it has write permissions.

### 1.2 Add Secrets to GitHub

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add these two secrets:

| Secret Name | Value |
|-------------|-------|
| `SUPABASE_URL` | `https://your-project.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |

## 📝 Step 2: Update Benchmark Workflow

The benchmark workflow needs to convert results to the monitoring format and upload as an artifact.

### 2.1 Add Conversion Script

Create a script to convert benchmark output to monitoring format:

```bash
cat > scripts/convert_benchmark_to_monitoring.py << 'EOF'
#!/usr/bin/env python3
"""
Convert benchmark results to monitoring format for Supabase persistence.

Usage:
    python scripts/convert_benchmark_to_monitoring.py \\
        --input benchmarks/results/aggregated_metrics_openai.json \\
        --output benchmark_results.json \\
        --model openai
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

def convert_to_monitoring_format(input_file: Path, model_name: str) -> dict:
    """Convert aggregated metrics to monitoring format."""
    
    with open(input_file, 'r') as f:
        metrics = json.load(f)
    
    # Extract version info (you can customize this)
    model_version = f"{model_name}-v1.0"
    dataset_version = "benchmark-set-v1"
    prompt_version = metrics.get('prompt_version', 'v1')
    
    # Convert metrics
    monitoring_format = {
        "model_version": model_version,
        "model_provider": model_name,
        "dataset_version": dataset_version,
        "dataset_size": metrics.get('total_documents', 0),
        "prompt_version": prompt_version,
        "metrics": {
            "precision": metrics.get('issue_precision', 0),
            "recall": metrics.get('issue_recall', 0),
            "f1": metrics.get('issue_f1_score', 0),
            "latency_ms": metrics.get('avg_pipeline_latency_ms', 0),
            "analysis_cost": metrics.get('total_cost', 0) / max(metrics.get('total_documents', 1), 1),
            "total_documents": metrics.get('total_documents', 0),
            "total_issues_detected": metrics.get('total_issues_detected', 0),
            "total_issues_expected": metrics.get('total_issues_expected', 0)
        },
        "duration_seconds": metrics.get('avg_pipeline_latency_ms', 0) / 1000,
        "error_count": metrics.get('error_count', 0),
        "success_count": metrics.get('total_documents', 0) - metrics.get('error_count', 0),
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }
    
    return monitoring_format

def main():
    parser = argparse.ArgumentParser(description='Convert benchmark to monitoring format')
    parser.add_argument('--input', required=True, help='Input aggregated metrics file')
    parser.add_argument('--output', required=True, help='Output monitoring format file')
    parser.add_argument('--model', required=True, help='Model name (openai, gemini, etc.)')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1
    
    monitoring_data = convert_to_monitoring_format(input_path, args.model)
    
    # Save to output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(monitoring_data, f, indent=2)
    
    print(f"✅ Converted {input_path} → {output_path}")
    print(f"   Model: {monitoring_data['model_version']}")
    print(f"   F1: {monitoring_data['metrics']['f1']:.4f}")
    
    return 0

if __name__ == '__main__':
    exit(main())
EOF
chmod +x scripts/convert_benchmark_to_monitoring.py
```

### 2.2 Update run_benchmarks.yml

Add these steps after the "Run benchmarks" step:

```yaml
      - name: Convert results to monitoring format
        if: always()
        run: |
          # Convert each model's results
          for model in openai gemini baseline; do
            if [ -f "benchmarks/results/aggregated_metrics_${model}.json" ]; then
              python3 scripts/convert_benchmark_to_monitoring.py \\
                --input "benchmarks/results/aggregated_metrics_${model}.json" \\
                --output "benchmark-artifacts/${model}_benchmark_results.json" \\
                --model "${model}"
            fi
          done
      
      - name: Upload benchmark results as artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: benchmark-artifacts/*.json
          retention-days: 90
```

## 🚀 Step 3: Test the Workflow

### 3.1 Manual Trigger

1. Go to **Actions** tab in your GitHub repository
2. Select **"Run Benchmarks"** workflow
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait for completion
5. Check that **"Benchmark Persistence"** workflow automatically triggers
6. Verify data in Supabase Dashboard

### 3.2 Verify in Supabase

1. Go to Supabase Dashboard → **SQL Editor**
2. Run query:

```sql
-- Check latest transactions
SELECT 
    created_at,
    model_version,
    environment,
    (metrics->>'f1')::numeric as f1_score,
    run_id
FROM benchmark_transactions
ORDER BY created_at DESC
LIMIT 10;

-- Check latest snapshots
SELECT 
    model_version,
    f1_score,
    precision_score,
    recall_score,
    created_at,
    is_current
FROM benchmark_snapshots
WHERE is_current = TRUE
ORDER BY f1_score DESC;
```

## 🎯 Step 4: Automatic Triggers

Once set up, benchmarks will automatically persist on:

- ✅ **Daily Schedule**: 2am UTC (configured in workflow)
- ✅ **Push to develop**: When you push changes to provider code
- ✅ **Manual Trigger**: Via Actions tab

## 🐛 Troubleshooting

### Issue: "Invalid API key"
**Solution**: Check that `SUPABASE_SERVICE_ROLE_KEY` (not `anon`) is set correctly.

### Issue: "Workflow not triggering"
**Solution**: 
1. Check workflow permissions: **Settings** → **Actions** → **General** → Enable "Read and write permissions"
2. Ensure `benchmark-persist.yml` references the correct workflow name

### Issue: "No artifact found"
**Solution**: 
1. Check that benchmarks ran successfully
2. Verify artifact upload step completed
3. Check artifact name matches in both workflows

### Issue: "Schema errors"
**Solution**: 
1. Verify schema is correctly deployed in Supabase
2. Check column names match (precision_score, recall_score, etc.)
3. Run schema with `--force` flag if needed

## 📊 Step 5: View Results in Dashboard

Once data is persisted:

```bash
# Locally
make monitoring-dashboard

# Or directly
python3 -m streamlit run pages/benchmark_monitoring.py
```

Open: http://localhost:8501

## 🔒 Security Best Practices

1. ✅ **Never commit** `.env` files or secrets to Git
2. ✅ **Use service_role key** only in GitHub Actions (server-side)
3. ✅ **Use anon key** for local dashboard (read-only)
4. ✅ **Rotate keys** periodically in Supabase Dashboard
5. ✅ **Enable RLS** (Row Level Security) in production

## 📚 Related Documentation

- [Benchmark Monitoring Setup](./BENCHMARK_MONITORING_SETUP.md)
- [Snapshot Versioning Guide](./SNAPSHOT_VERSIONING_GUIDE.md)
- [Architecture Overview](./BENCHMARK_PERSISTENCE_ARCHITECTURE.md)
- [Quick Reference](./BENCHMARK_MONITORING_QUICKREF.md)

## 🎉 You're Done!

Your benchmark results will now automatically flow into Supabase, and you can monitor performance over time in the dashboard.

**Next Steps:**
- Set up alerts for regressions
- Create baseline comparisons
- Monitor trends across model versions
- Use snapshot versioning to rollback configurations
