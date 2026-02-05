# 📊 Benchmark Monitoring System

**Production-ready MLOps infrastructure for tracking and monitoring ML model performance**

---

## 🎯 Overview

This system provides a complete benchmark persistence and monitoring solution designed for CI/CD integration. It tracks model performance over time, detects regressions, and provides actionable insights through an interactive dashboard.

### Key Features

- ✅ **Immutable Audit Trail** - Every benchmark run is permanently logged
- ✅ **Real-Time Dashboard** - Visualize performance trends and comparisons
- ✅ **Regression Detection** - Automatic alerts when performance drops
- ✅ **Version Tracking** - Trace results to specific commits, datasets, and prompts
- ✅ **CI/CD Integration** - Seamless GitHub Actions workflow
- ✅ **Multi-Environment** - Track local, staging, and production separately
- ✅ **Extensible Design** - Ready for ML observability features

---

## 🏗️ Architecture

```
GitHub Actions → Benchmark Results → Supabase → Streamlit Dashboard
     (CI/CD)         (JSON)          (Postgres)    (Visualization)
```

### Core Components

1. **Supabase Database** - Postgres backend with two-table design:
   - `benchmark_transactions` - Append-only log of all runs
   - `benchmark_snapshots` - Current state for fast queries

2. **Python Scripts**
   - `push_to_supabase.py` - Persist results from CI/CD
   - `benchmark_data_access.py` - Data access layer for dashboard

3. **Streamlit Dashboard**
   - `pages/benchmark_monitoring.py` - Interactive performance monitoring

4. **GitHub Actions**
   - `.github/workflows/benchmark-persist.yml` - Automated persistence

---

## 🚀 Quick Start

### Prerequisites

- Supabase account (free tier works)
- GitHub repository with Actions enabled
- Python 3.9+

### 5-Minute Setup

```bash
# 1. Clone and install dependencies
pip install supabase streamlit plotly pandas

# 2. Set environment variables
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"

# 3. Initialize database (run SQL in Supabase dashboard)
# Copy contents of sql/schema_benchmark_monitoring.sql

# 4. Test push
python scripts/push_to_supabase.py \
  --input benchmarks/sample_benchmark_results.json \
  --environment local \
  --commit-sha $(git rev-parse HEAD) \
  --triggered-by $(whoami)

# 5. Launch dashboard
export SUPABASE_ANON_KEY="your-anon-key"
streamlit run pages/benchmark_monitoring.py
```

**👉 See [BENCHMARK_MONITORING_SETUP.md](docs/BENCHMARK_MONITORING_SETUP.md) for detailed instructions**

---

## 📂 File Structure

```
.
├── sql/
│   └── schema_benchmark_monitoring.sql      # Database schema
│
├── .github/workflows/
│   └── benchmark-persist.yml                # CI/CD automation
│
├── scripts/
│   ├── push_to_supabase.py                  # Persistence script
│   └── benchmark_data_access.py             # Data access layer
│
├── pages/
│   └── benchmark_monitoring.py              # Streamlit dashboard
│
├── benchmarks/
│   └── sample_benchmark_results.json        # Example result format
│
└── docs/
    ├── BENCHMARK_MONITORING_SETUP.md        # Setup guide
    └── BENCHMARK_PERSISTENCE_ARCHITECTURE.md # Architecture docs
```

---

## 📊 Dashboard Features

### 1. Current Snapshot
- View latest performance across all models
- Top performers by F1 score
- Fastest models by latency
- Cost efficiency analysis

### 2. Performance Trends
- Time-series charts of F1, precision, recall
- Daily run counts
- Confidence intervals
- Multi-metric tracking

### 3. Model Comparison
- Side-by-side comparison of multiple models
- Statistical summaries
- Visual performance comparison

### 4. Regression Detection
- Automatic baseline comparison
- Configurable thresholds
- Actionable alerts
- Historical context

---

## 🔄 CI/CD Integration

### GitHub Actions Workflow

```yaml
- name: Run Benchmarks
  run: python run_benchmarks.py --output benchmark_results.json

- name: Persist to Supabase
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
  run: |
    python scripts/push_to_supabase.py \
      --input benchmark_results.json \
      --environment github-actions \
      --commit-sha ${{ github.sha }} \
      --run-id ${{ github.run_id }} \
      --triggered-by ${{ github.actor }}
```

### Expected JSON Format

```json
{
  "model_version": "medgemma-v1.2",
  "dataset_version": "benchmark-set-v3",
  "prompt_version": "analysis-v4",
  "model_provider": "google",
  "metrics": {
    "precision": 0.91,
    "recall": 0.88,
    "f1": 0.895,
    "latency_ms": 412,
    "analysis_cost": 0.0042
  }
}
```

---

## 🎯 Use Cases

### For ML Engineers
- Track model improvements over time
- Compare prompt variations
- Identify performance regressions
- Debug failing benchmarks

### For Data Scientists
- Analyze dataset quality impact
- Experiment with hyperparameters
- A/B test model architectures
- Validate hypothesis

### For Product Teams
- Monitor production model health
- Track cost per analysis
- Measure latency SLAs
- Report on model improvements

### For MLOps Teams
- Enforce quality gates in CI/CD
- Alert on performance degradation
- Audit model changes
- Maintain compliance logs

---

## 🛡️ Security

### Best Practices

- ✅ Use **service role key** for CI/CD (write access)
- ✅ Use **anon key** for dashboard (read-only)
- ✅ Store credentials in GitHub Secrets
- ✅ Enable Row Level Security (RLS) in production
- ✅ Never commit API keys to Git

### Environment Variables

```bash
# Required for persistence script
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="eyJhbG..."

# Required for dashboard
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_ANON_KEY="eyJhbG..."
```

---

## 📈 Performance & Scaling

### Current Capacity
- **0-10K runs/day:** No optimization needed
- **10K-100K runs/day:** Add partitioning and materialized views
- **100K+ runs/day:** Consider TimescaleDB extension

### Storage Estimates
- ~1KB per transaction
- 1M runs = ~1GB storage
- Supabase free tier: 500MB (500K runs)

### Query Performance
- Latest snapshot: < 50ms
- Historical trends (30 days): < 500ms
- Full comparison: < 1s

---

## 🧪 Testing

### Unit Tests

```python
# Test persistence
def test_push_benchmark():
    result = push_to_supabase(sample_data)
    assert result.transaction_id is not None

# Test regression detection
def test_detect_regression():
    result = detect_regression('model-v1', threshold=0.05)
    assert 'is_regression' in result
```

### Integration Tests

```bash
# End-to-end test
python scripts/push_to_supabase.py \
  --input benchmarks/sample_benchmark_results.json \
  --environment local \
  --commit-sha test-commit \
  --verify
```

---

## 🔧 Maintenance

### Weekly Tasks
- Review dashboard for anomalies
- Check for new regressions
- Update baselines if needed

### Monthly Tasks
- Review storage usage
- Check index performance
- Archive old data if needed

### Quarterly Tasks
- Review schema optimizations
- Update documentation
- Train team on new features

---

## 🚀 Future Enhancements

### Planned Features

1. **Drift Detection**
   - Monitor input distribution changes
   - Alert on dataset drift
   - Track feature importance

2. **Alerting System**
   - Slack/email notifications
   - Configurable thresholds
   - Auto-create GitHub issues

3. **Experiment Tracking**
   - Compare experiment branches
   - Track hyperparameter variations
   - Link to MLflow/Weights & Biases

4. **Cost Optimization**
   - Cost/performance frontier analysis
   - Budget tracking
   - Efficiency recommendations

5. **SLA Monitoring**
   - Latency percentiles (p50, p95, p99)
   - Uptime tracking
   - Error rate monitoring

---

## 📚 Documentation

- **[Setup Guide](docs/BENCHMARK_MONITORING_SETUP.md)** - Step-by-step installation
- **[Architecture Docs](docs/BENCHMARK_PERSISTENCE_ARCHITECTURE.md)** - Technical design
- **[SQL Schema](sql/schema_benchmark_monitoring.sql)** - Database structure

---

## 🤝 Contributing

### Adding New Metrics

1. Update JSON format in your benchmark script
2. Metrics are stored in JSONB (no schema change needed)
3. For frequently queried metrics, add denormalized column:

```sql
ALTER TABLE benchmark_snapshots
ADD COLUMN new_metric NUMERIC;
```

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Add tests
4. Update documentation
5. Submit pull request

---

## 🐛 Troubleshooting

### Common Issues

**Dashboard shows "No data"**
- Check environment filter in sidebar
- Verify data exists: `SELECT COUNT(*) FROM benchmark_snapshots`
- Ensure `is_active = TRUE` for snapshots

**GitHub Action fails**
- Verify secrets are configured
- Check `benchmark_results.json` exists
- Review workflow logs

**Slow queries**
- Check indexes: `SELECT * FROM pg_indexes WHERE tablename LIKE 'benchmark%'`
- Consider partitioning for large datasets
- Use materialized views for complex aggregations

**👉 See [Setup Guide](docs/BENCHMARK_MONITORING_SETUP.md#troubleshooting) for more**

---

## 📊 Example Queries

### Get latest F1 scores

```sql
SELECT model_version, f1_score, last_updated_at
FROM benchmark_snapshots
WHERE is_active = TRUE
ORDER BY f1_score DESC;
```

### Compare to baseline

```sql
SELECT * FROM detect_regression('medgemma-v1.2', 0.05);
```

### Historical trend

```sql
SELECT 
  DATE_TRUNC('day', created_at) AS date,
  AVG((metrics->>'f1')::NUMERIC) AS avg_f1
FROM benchmark_transactions
WHERE model_version = 'medgemma-v1.2'
  AND created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date;
```

---

## 💡 Tips & Best Practices

1. **Set baselines early** - Mark your production model as baseline for regression detection
2. **Use tags** - Tag experiments for easier filtering and analysis
3. **Document versions** - Keep a changelog of model/prompt/dataset changes
4. **Monitor regularly** - Review dashboard weekly to catch issues early
5. **Archive old data** - Keep last 90 days hot, archive the rest
6. **Test locally first** - Validate changes in local environment before CI/CD

---

## 📞 Support

- **Documentation:** See `docs/` folder
- **Issues:** Open a GitHub issue
- **Discussions:** Use GitHub Discussions for questions
- **Security:** Email security issues privately

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

Built with:
- [Supabase](https://supabase.com) - Backend infrastructure
- [Streamlit](https://streamlit.io) - Dashboard framework
- [Plotly](https://plotly.com) - Visualization library
- [GitHub Actions](https://github.com/features/actions) - CI/CD automation

---

**Ready to track your ML benchmarks?**

👉 Start with the [Setup Guide](docs/BENCHMARK_MONITORING_SETUP.md)

👉 Read the [Architecture Docs](docs/BENCHMARK_PERSISTENCE_ARCHITECTURE.md)

👉 Test with [Sample Data](benchmarks/sample_benchmark_results.json)

---

**Questions or improvements?** Open an issue or submit a PR!

**Author:** Senior MLOps Engineer  
**Last Updated:** 2026-02-03  
**Version:** 1.0
