# Scripts Reference

Command-line tools for development, testing, and benchmarking.

## Overview

```
scripts/
├── migrate_module.py                  # Module migration tool
├── generate_patient_benchmarks.py     # Generate test cases
├── annotate_benchmarks.py             # Ground truth annotation
├── run_benchmarks.py                  # Execute benchmarks
├── verify_setup.py                    # Installation check
└── archive_old_docs.sh                # Documentation cleanup
```

## Benchmark Scripts

### `generate_patient_benchmarks.py`

Generate synthetic medical bills from patient profiles.

**Usage**:
```bash
# Generate all benchmarks
python scripts/generate_patient_benchmarks.py

# Generate specific patient
python scripts/generate_patient_benchmarks.py --patient patient_001

# Generate with specific scenario
python scripts/generate_patient_benchmarks.py --scenario colonoscopy_upcoding

# Dry run (preview only)
python scripts/generate_patient_benchmarks.py --dry-run
```

**Options**:
- `--patient`: Patient ID to generate (default: all)
- `--scenario`: Specific scenario to generate
- `--output-dir`: Output directory (default: benchmarks/inputs/)
- `--dry-run`: Preview without writing files

**Example**:
```bash
$ python scripts/generate_patient_benchmarks.py --patient patient_001

Generating benchmarks...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ patient_001_colonoscopy.txt (2.3 KB)
✓ patient_001_colonoscopy_expected.json (1.2 KB)

Generated: 2 files
Expected savings: $650.00
Expected issues: 2 (upcoding, duplicate)
```

### `annotate_benchmarks.py`

Interactive ground truth annotation tool.

**Usage**:
```bash
# Annotate all unannotated documents
python scripts/annotate_benchmarks.py

# Annotate specific document
python scripts/annotate_benchmarks.py --document patient_001_colonoscopy.txt

# Review existing annotations
python scripts/annotate_benchmarks.py --review

# Validate annotations
python scripts/annotate_benchmarks.py --validate
```

**Interactive Workflow**:
```bash
$ python scripts/annotate_benchmarks.py --document patient_001_colonoscopy.txt

╔════════════════════════════════════════════════════════════╗
║           Benchmark Annotation Tool v1.0                   ║
╚════════════════════════════════════════════════════════════╝

Document: patient_001_colonoscopy.txt
Patient: patient_001 (John Smith, 45 years old)
Scenario: Colonoscopy with upcoding and duplicate charge

[Document Preview]
──────────────────────────────────────────────────────────
MEDICAL BILL
Provider: Dr. Jane Doe (Gastroenterology)
Patient: John Smith
Date of Service: 2024-01-15

CPT 45385 - Colonoscopy w/ polyp removal ........ $2,450.00
CPT 00810 - Anesthesia ........................... $400.00
CPT 00810 - Anesthesia ........................... $400.00
──────────────────────────────────────────────────────────

How many issues do you expect? [2]: 2

╔════════════════════════════════════════════════════════════╗
║ Issue 1 of 2                                               ║
╚════════════════════════════════════════════════════════════╝

Category: [overcharge/duplicate/unbundling/missing_info]: overcharge
Severity: [high/medium/low]: high
Title: Procedure Upcoded
Explanation: Billed 45385 (with polyp removal) but op notes show diagnostic only
Max Savings: $250.00
Confidence: [0.0-1.0]: 0.95
Affected CPT Codes: 45385

✓ Issue 1 saved

╔════════════════════════════════════════════════════════════╗
║ Issue 2 of 2                                               ║
╚════════════════════════════════════════════════════════════╝

Category: duplicate_charge
Severity: high
Title: Duplicate Anesthesia Charge
Explanation: Anesthesia billed twice on same date
Max Savings: $400.00
Confidence: 1.0
Affected CPT Codes: 00810

✓ Issue 2 saved

Annotation complete!
Saved to: benchmarks/expected_outputs/patient_001_colonoscopy_expected.json
```

### `run_benchmarks.py`

Execute benchmark suite against AI providers.

**Usage**:
```bash
# Run all providers
python scripts/run_benchmarks.py --all

# Run specific provider
python scripts/run_benchmarks.py --provider gpt-4o-mini

# Run specific test case
python scripts/run_benchmarks.py --test patient_001_colonoscopy --provider gemini-2.0-flash

# Compare providers
python scripts/run_benchmarks.py --compare gpt-4o-mini gemini-2.0-flash

# Save detailed report
python scripts/run_benchmarks.py --provider gpt-4o-mini --output-dir results/
```

**Options**:
- `--provider`: Provider key (gpt-4o-mini, gemini-2.0-flash, medgemma, heuristic)
- `--all`: Run all providers
- `--test`: Specific test case
- `--compare`: Compare multiple providers
- `--output-dir`: Output directory for results
- `--verbose`: Show detailed output

**Example Output**:
```bash
$ python scripts/run_benchmarks.py --provider gpt-4o-mini

╔═══════════════════════════════════════════════════════════╗
║          Benchmark Execution: gpt-4o-mini                  ║
╚═══════════════════════════════════════════════════════════╝

Loading test cases... ✓ 50 cases loaded
Loading expected outputs... ✓ 50 ground truths loaded

Running tests:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1/50] patient_001_colonoscopy ............ ✓ F1: 1.00 (4.2s)
[2/50] patient_002_dental ................. ✓ F1: 0.85 (3.8s)
[3/50] patient_003_pharmacy ............... ✓ F1: 0.92 (4.1s)
...
[50/50] patient_050_eob ................... ✓ F1: 0.89 (4.5s)

╔═══════════════════════════════════════════════════════════╗
║                     Results Summary                        ║
╚═══════════════════════════════════════════════════════════╝

Provider: gpt-4o-mini
Test Cases: 50
Duration: 215 seconds (3.6 min)

Aggregate Metrics:
  Precision:  0.87
  Recall:     0.92
  F1 Score:   0.89
  Avg Latency: 4.3s

Per-Category Performance:
  upcoding:           F1 0.92 (precision 0.90, recall 0.95)
  duplicate_charge:   F1 1.00 (precision 1.00, recall 1.00)
  unbundling:         F1 0.85 (precision 0.88, recall 0.82)
  balance_billing:    F1 0.88 (precision 0.90, recall 0.86)
  missing_info:       F1 0.95 (precision 1.00, recall 0.91)

Savings Estimation:
  Mean Absolute Error: $45.23
  Relative Error: 12%
  Within 20%: 92% of cases

Results saved to: benchmarks/results/2026-02-05_gpt-4o-mini/
```

## Development Scripts

### `verify_setup.py`

Verify development environment setup.

**Usage**:
```bash
python scripts/verify_setup.py
```

**Checks**:
- Python version (3.11+)
- Package installation (medbilldozer)
- Dependencies installed
- Environment variables set
- API keys valid
- Database connectivity (if Supabase configured)

**Example Output**:
```bash
$ python scripts/verify_setup.py

╔═══════════════════════════════════════════════════════════╗
║           medBillDozer Setup Verification                  ║
╚═══════════════════════════════════════════════════════════╝

Python Environment:
  ✓ Python version: 3.13.0
  ✓ Virtual environment: active
  ✓ pip version: 24.0

Package Installation:
  ✓ medbilldozer: 0.2.0 (editable mode)
  ✓ streamlit: 1.28.1
  ✓ openai: 1.5.0
  ✓ google-generativeai: 0.3.2

Environment Variables:
  ✓ OPENAI_API_KEY: set (sk-proj-****)
  ✓ GOOGLE_API_KEY: set (AIza****)
  ⚠ SUPABASE_URL: not set (optional)
  ⚠ MEDGEMMA_ENDPOINT: not set (optional)

Provider Registration:
  ✓ gpt-4o-mini: registered
  ✓ gemini-2.0-flash: registered
  ✗ medgemma: not available (no API key)
  ✓ heuristic: registered

Test Suite:
  ✓ All 134 tests passing

╔═══════════════════════════════════════════════════════════╗
║                  Setup Status: READY ✅                   ║
╚═══════════════════════════════════════════════════════════╝

You're all set! Run: streamlit run medBillDozer.py
```

### `migrate_module.py`

Tool used for Phase 2 migration (_modules → src/medbilldozer).

**Historical use** (migration complete):
```bash
# Migrated all modules
python scripts/migrate_module.py utils
python scripts/migrate_module.py data
python scripts/migrate_module.py prompts
# ... etc

# With dry-run
python scripts/migrate_module.py core --dry-run
```

## Documentation Scripts

### `archive_old_docs.sh`

Archive legacy documentation files.

**Usage**:
```bash
# Make executable
chmod +x scripts/archive_old_docs.sh

# Execute
bash scripts/archive_old_docs.sh
```

**Actions**:
- Creates `docs_archive_20260205/`
- Moves ~180 markdown files
- Preserves README.md, LICENSE
- Uses git mv when possible

## Utility Scripts

### Create Custom Scripts

Template for new scripts:

```python
#!/usr/bin/env python3
"""
Script description.

Usage:
    python scripts/my_script.py [options]
"""

import argparse
from pathlib import Path
from medbilldozer.core import OrchestratorAgent

def main():
    parser = argparse.ArgumentParser(description="My script")
    parser.add_argument("--input", help="Input file")
    parser.add_argument("--output", help="Output file")
    parser.add_argument("--verbose", action="store_true")
    
    args = parser.parse_args()
    
    # Script logic here
    print(f"Processing {args.input}...")
    
    # Use medbilldozer modules
    agent = OrchestratorAgent()
    result = agent.run(text)
    
    print("✓ Complete")

if __name__ == "__main__":
    main()
```

## Common Workflows

### Generate and Run Benchmarks

```bash
# 1. Generate test cases
python scripts/generate_patient_benchmarks.py

# 2. Annotate expected outputs
python scripts/annotate_benchmarks.py

# 3. Run benchmarks
python scripts/run_benchmarks.py --all

# 4. View results
streamlit run benchmark_dashboard.py
```

### Add New Test Case

```bash
# 1. Create patient profile
cat > benchmarks/patient_profiles/patient_051_profile.json << EOF
{
  "patient_id": "patient_051",
  "name": "Jane Doe",
  "age": 35,
  "test_scenario": "Pharmacy receipt with FSA issues"
}
EOF

# 2. Generate benchmark
python scripts/generate_patient_benchmarks.py --patient patient_051

# 3. Annotate expected output
python scripts/annotate_benchmarks.py --document patient_051_pharmacy.txt

# 4. Run test
python scripts/run_benchmarks.py --test patient_051_pharmacy --provider gpt-4o-mini
```

### Validate All Benchmarks

```bash
# Check all annotations are valid
python scripts/annotate_benchmarks.py --validate

# Expected output:
# ✓ 50/50 annotations valid
# ✓ All schemas conform
# ✓ No missing fields
```

## Next Steps

- [Testing Guide](testing.md) - Run test suite
- [Setup Guide](setup.md) - Development environment
- [Benchmark Engine](../architecture/benchmark_engine.md) - Validation system
