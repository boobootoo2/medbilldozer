# Scripts Directory

24 production-ready scripts for benchmarks, analysis, and utilities.

## 🎯 Quick Start

```bash
# Run benchmarks
python3 scripts/generate_patient_benchmarks.py --model medgemma-ensemble --workers 2

# Push to database
python3 scripts/push_patient_benchmarks.py --input benchmarks/results/patient_benchmark_medgemma.json

# Verify results
python3 scripts/verify_supabase_results.py --limit 10
```

## 📊 Core Scripts

**Benchmarks**
- `generate_patient_benchmarks.py` - Generate patient-based benchmarks
- `annotate_benchmarks.py` - Ground truth annotation
- `push_patient_benchmarks.py` - Push results to Supabase

**Analysis**
- `calculate_roi_metrics.py` - ROI and cost savings
- `patient_failure_analysis.py` - Failure pattern analysis
- `analyze_failure_modes.py` - Error category analysis

**Utilities**
- `verify_supabase_results.py` - Verify database contents
- `check_snapshots.py` - Check database snapshots
- `generate_docs.py` - Auto-generate documentation

## 📁 Full Script List

<details>
<summary>View all 24 scripts by category</summary>

### Production (8)
- `generate_patient_benchmarks.py`
- `annotate_benchmarks.py`
- `push_patient_benchmarks.py`
- `push_to_supabase.py`
- `convert_benchmark_to_monitoring.py`
- `benchmark_data_access.py`
- `advanced_metrics.py`
- `calculate_roi_metrics.py`

### Analysis (4)
- `patient_failure_analysis.py`
- `analyze_failure_modes.py`
- `export_dashboard_summary.py`
- `export_error_type_performance.py`

### Verification (4)
- `verify_supabase_results.py`
- `verify_cost_savings.py`
- `check_snapshots.py`
- `get_supabase_transactions.py`

### UI & Dev (5)
- `generate_splash_audio.py`
- `generate_tour_audio.py`
- `generate_docs.py`
- `install-hooks.sh`
- `push_local_benchmarks.sh`

</details>

## 📚 More Info

Run any script with `--help` for usage details:
```bash
python3 scripts/generate_patient_benchmarks.py --help
```

**Related Docs**: [Benchmarks](../benchmarks/README.md) | [API](../docs/API.md) | [Technical](../docs/TECHNICAL_WRITEUP.md)

---

*Last cleanup: February 2026 - Removed 13 debug/obsolete scripts. See [docs/REPOSITORY_CLEANUP_2026.md](../docs/REPOSITORY_CLEANUP_2026.md) for details.*
