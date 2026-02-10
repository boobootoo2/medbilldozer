# Scripts Directory# Documentation Scripts



Production-ready scripts for benchmark generation, data management, and analysis.## Automatic Documentation Generator



## 📊 Production ScriptsThe `generate_docs.py` script automatically generates comprehensive documentation by analyzing the codebase itself. No manual documentation writing required!



Core scripts for running benchmarks and managing results.### Features



### Benchmark Generation- **AST-based Analysis**: Parses Python source code using Abstract Syntax Trees to extract facts

- **`generate_patient_benchmarks.py`** - Main benchmark generator for patient-based test cases- **Comprehensive Coverage**: Documents modules, classes, functions, dependencies, and APIs

  ```bash- **Multiple Output Formats**: Generates Markdown docs and JSON manifest

  python3 scripts/generate_patient_benchmarks.py --model medgemma-ensemble --workers 2- **Dependency Tracking**: Maps internal dependencies between modules

  ```- **Zero Configuration**: Works out of the box, no setup needed



- **`annotate_benchmarks.py`** - Ground truth annotation tool for benchmark results### Usage

  ```bash

  python3 scripts/annotate_benchmarks.py benchmarks/inputs/```bash

  ```# Generate all documentation

python3 scripts/generate_docs.py

### Data Persistence

- **`push_patient_benchmarks.py`** - Push patient benchmark results to Supabase# Or use the convenience commands

  ```bashmake docs          # Generate documentation

  python3 scripts/push_patient_benchmarks.py --input benchmarks/results/patient_benchmark_medgemma.jsonmake docs-view     # Generate and view in browser

  ``````



- **`push_to_supabase.py`** - Generic Supabase push utility for monitoring format### Git Pre-Commit Hook

  ```bash

  python3 scripts/push_to_supabase.py --input results.json --environment localTo ensure documentation stays up-to-date automatically, install the pre-commit hook:

  ```

```bash

- **`convert_benchmark_to_monitoring.py`** - Convert benchmark format to monitoring format# Install the hook

  ```bashmake install-hooks

  python3 scripts/convert_benchmark_to_monitoring.py --input patient_benchmark.json --output monitoring.json --model medgemma

  ```# Or manually

bash scripts/install-hooks.sh

### Data Access```

- **`benchmark_data_access.py`** - Data access layer module for Supabase queries (~600 lines)

  - Used by dashboard and analysis scriptsOnce installed, documentation will be automatically regenerated and staged with every commit. The hook:

  - Provides clean interface to benchmark database

- Runs `make docs` before each commit

## 📈 Analysis & Reporting Scripts- Detects if documentation files changed

- Automatically stages updated docs with your commit

Scripts for analyzing benchmark results and generating insights.- Ensures docs never fall out of sync with code



### Metrics & ROITo skip the hook temporarily (not recommended):

- **`calculate_roi_metrics.py`** - Calculate ROI and cost savings metrics```bash

  ```bashgit commit --no-verify

  python3 scripts/calculate_roi_metrics.py --results-dir benchmark-artifacts --output roi_summary.json```

  ```

### Generated Documentation

- **`advanced_metrics.py`** - Advanced metrics computation module

  - Risk-weighted recallThe script creates the following files in the `docs/` directory:

  - Domain-specific F1 scores

  - Category-level performance tracking1. **README.md** - Project overview and module categorization

2. **MODULES.md** - Detailed documentation for each module

### Failure Analysis3. **API.md** - Public API reference for key interfaces

- **`patient_failure_analysis.py`** - Analyze patient-level failure patterns4. **DEPENDENCIES.md** - Module dependency graph

  ```bash5. **manifest.json** - Machine-readable metadata for programmatic access

  python3 scripts/patient_failure_analysis.py --model medgemma --output analysis.json

  ```### What Gets Documented



- **`analyze_failure_modes.py`** - Analyze failure modes across error categoriesThe generator extracts these facts from the code:

  ```bash

  python3 scripts/analyze_failure_modes.py --results benchmarks/results/- Module docstrings and descriptions

  ```- Function signatures (name, parameters, return types)

- Class definitions (inheritance, attributes, methods)

### Data Export- Decorators and async functions

- **`export_dashboard_summary.py`** - Export dashboard summary to JSON- Module-level constants

  ```bash- Internal dependencies (_modules imports)

  python3 scripts/export_dashboard_summary.py --output summary.json- File locations and line numbers

  ```

### Philosophy

- **`export_error_type_performance.py`** - Export error type performance metrics

  ```bash**Documentation is derived from code-owned facts, not written by hand.**

  python3 scripts/export_error_type_performance.py --output error_metrics.csv

  ```This ensures:

- Documentation stays in sync with code

## 🔍 Verification & Utility Scripts- No documentation drift or staleness

- Single source of truth (the code)

Scripts for verifying database state and results.- Automated updates on every change

- Consistent format and structure

### Database Verification

- **`verify_supabase_results.py`** - Verify benchmark results in Supabase### Extending the Generator

  ```bash

  python3 scripts/verify_supabase_results.py --limit 10To add new documentation sections, extend the `DocumentationGenerator` class:

  ```

```python

- **`check_snapshots.py`** - Check current database snapshotsdef generate_custom_section(self) -> str:

  ```bash    """Add your custom documentation logic"""

  python3 scripts/check_snapshots.py    lines = ["## Custom Section", ""]

  ```    # Your logic here

    return "\n".join(lines)

- **`get_supabase_transactions.py`** - Query benchmark transactions```

  ```bash

  python3 scripts/get_supabase_transactions.py --model medgemma-ensemble --limit 5Then call it in the `generate_all()` method.

  ```

### Integration with CI/CD

### Cost Verification

- **`verify_cost_savings.py`** - Verify cost savings calculationsAdd to your CI pipeline to auto-generate docs on every commit:

  ```bash

  python3 scripts/verify_cost_savings.py --benchmark-results results.json```yaml

  ```# .github/workflows/docs.yml

- name: Generate Documentation

## 🎨 UI & Audio Generation  run: python3 scripts/generate_docs.py

  

Scripts for generating user interface assets.- name: Commit Updated Docs

  run: |

### Audio    git add docs/

- **`generate_splash_audio.py`** - Generate splash screen audio narration    git commit -m "Auto-update documentation [skip ci]" || true

- **`generate_tour_audio.py`** - Generate guided tour audio narration```


## 🛠️ Development Tools

### Documentation
- **`generate_docs.py`** - Auto-generate API documentation
  ```bash
  python3 scripts/generate_docs.py
  ```

### Git Hooks
- **`install-hooks.sh`** - Install pre-commit hooks for code quality
  ```bash
  bash scripts/install-hooks.sh
  ```

## 📝 Shell Scripts

### Batch Operations
- **`push_local_benchmarks.sh`** - Batch push local benchmarks to Supabase
  ```bash
  ./scripts/push_local_benchmarks.sh medgemma-ensemble
  ```

## 🎯 Quick Reference

### Run benchmarks for a model
```bash
python3 scripts/generate_patient_benchmarks.py --model medgemma-ensemble --workers 2
```

### Push results to database
```bash
python3 scripts/push_patient_benchmarks.py --input benchmarks/results/patient_benchmark_medgemma-ensemble.json
```

### Verify what's in database
```bash
python3 scripts/verify_supabase_results.py --limit 5
```

### Check current snapshots
```bash
python3 scripts/check_snapshots.py
```

### Calculate ROI
```bash
python3 scripts/calculate_roi_metrics.py --results-dir benchmarks/results/ --output roi.json
```

## 🗂️ Script Organization

```
scripts/
├── Production (8 scripts)
│   ├── Benchmark generation
│   ├── Data persistence
│   └── Data access layer
├── Analysis & Reporting (7 scripts)
│   ├── Metrics & ROI
│   ├── Failure analysis
│   └── Data export
├── Verification & Utilities (4 scripts)
│   ├── Database verification
│   └── Cost verification
├── UI & Audio (2 scripts)
└── Development Tools (3 scripts)
```

**Total**: ~24 production-ready scripts

## 🚫 Deprecated Scripts Removed

The following scripts have been removed during repository cleanup (February 2026):

### Debug & Test Scripts
- `debug_supabase_domain_rate.py` - One-off debug for domain rate issue
- `test_hf_api.py` - HuggingFace API connectivity test
- `test_hf_openai_client.py` - Client test script
- `test_ingestion_api.py` - Ingestion API test
- `test_fictional_entities.py` - Entity generator test
- `test_health_data_ingestion.py` - Health data test
- `estimate_benchmark_tokens.py` - Token estimation utility

### One-off Database Scripts
- `cleanup_failed_benchmarks.py` - One-time cleanup of failed runs
- `delete_model_from_supabase.py` - Manual deletion utility
- `populate_test_snapshots.py` - Test data population
- `verify_snapshot_automation.py` - Snapshot verification

### Obsolete Versions
- `generate_benchmarks.py` - Replaced by `generate_patient_benchmarks.py`
- `run_benchmarks_v2.py` - Replaced by CI/CD workflows

## 📚 Related Documentation

- [Benchmark Guide](../benchmarks/README.md)
- [API Documentation](../docs/API.md)
- [Technical Documentation](../docs/TECHNICAL_WRITEUP.md)
- [Dependencies](../docs/DEPENDENCIES.md)

---

**Last Updated**: February 10, 2026  
**Maintained By**: MedBillDozer Team
