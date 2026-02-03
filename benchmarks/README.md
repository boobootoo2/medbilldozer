# medBillDozer Benchmarks

This directory contains the benchmarking framework for evaluating the medBillDozer analysis pipeline.

## Directory Structure

```
benchmarks/
├── inputs/                    # Synthetic benchmark documents
│   ├── medical_bill_duplicate.txt
│   ├── dental_bill_clean.txt
│   └── pharmacy_receipt.txt
├── expected_outputs/          # Ground truth for evaluation
│   ├── medical_bill_duplicate.json
│   ├── dental_bill_clean.json
│   └── pharmacy_receipt.json
├── results/                   # Generated benchmark results
│   └── aggregated_metrics.json
└── README.md                  # This file
```

## Running Benchmarks

### Test All Available Models

```bash
# Automatically tests all models with available API keys
python scripts/generate_benchmarks.py --model all
```

The `--model all` option will:
- Test MedGemma (if `HF_API_TOKEN` is set)
- Test OpenAI GPT-4o-mini (if `OPENAI_API_KEY` is set)
- Test Gemini 1.5 Flash (if `GOOGLE_API_KEY` is set)
- Always test Baseline (no API key required)
- Show comparison table at the end

### Test Individual Models

```bash
# MedGemma
export HF_API_TOKEN="your-token-here"
python scripts/generate_benchmarks.py --model medgemma

# OpenAI
export OPENAI_API_KEY="your-key-here"
python scripts/generate_benchmarks.py --model openai

# Gemini
export GOOGLE_API_KEY="your-key-here"
python scripts/generate_benchmarks.py --model gemini

# Baseline (no API key needed)
python scripts/generate_benchmarks.py --model baseline
```

## What Gets Measured

### Model Performance Metrics

- **Extraction Accuracy**: Percentage of documents successfully processed
- **Issue Detection Precision**: True positives / (True positives + False positives)
- **Issue Detection Recall**: True positives / (True positives + False negatives)
- **Issue Detection F1 Score**: Harmonic mean of precision and recall
- **JSON Validity Rate**: Percentage of outputs with valid JSON structure

### Operational Metrics

- **Avg Input Tokens**: Average tokens in input documents (provider-specific)
- **Avg Output Tokens**: Average tokens in model responses (provider-specific)
- **Avg Total Tokens**: Sum of input + output tokens
- **Avg Extraction Latency**: Time to extract structured facts (ms)
- **Avg Pipeline Latency**: Total time for extraction + reconciliation (ms)

## Expected Output Format

Each `expected_outputs/*.json` file should contain:

```json
{
  "document_type": "medical_bill",
  "expected_issues": [
    {
      "type": "duplicate_charge",
      "code": "99213",
      "date": "2024-01-15",
      "should_detect": true
    }
  ],
  "expected_facts": {
    "patient_name": "John Doe",
    "date_of_service": "2024-01-15",
    "medical_line_items": [...]
  },
  "expected_savings": 75.00
}
```

### Issue Evaluation

Issues are matched based on:
- `type`: Issue type (e.g., "duplicate_charge")
- `code`: CPT/CDT code (e.g., "99213")
- `date`: Date of service (e.g., "2024-01-15")

An issue is considered:
- **True Positive**: Expected and detected
- **False Positive**: Detected but not expected
- **False Negative**: Expected but not detected

## README Integration

After running benchmarks, the script automatically updates `.github/README.md` by:

1. Looking for markers: `<!-- BENCHMARK_SECTION_START -->` and `<!-- BENCHMARK_SECTION_END -->`
2. If markers exist: Replaces content between them
3. If markers don't exist: Appends benchmark section to end of README

## Adding New Benchmarks

1. **Create input document**:
   ```
   benchmarks/inputs/your_document_name.txt
   ```

2. **Create expected output**:
   ```
   benchmarks/expected_outputs/your_document_name.json
   ```

3. **Run benchmarks**:
   ```bash
   python scripts/generate_benchmarks.py --model medgemma
   ```

## Results Storage

Aggregated metrics are saved to `benchmarks/results/aggregated_metrics.json`:

```json
{
  "model_name": "medgemma",
  "total_documents": 3,
  "successful_extractions": 3,
  "extraction_accuracy": 100.0,
  "issue_precision": 1.0,
  "issue_recall": 1.0,
  "issue_f1_score": 1.0,
  "json_validity_rate": 100.0,
  "avg_input_tokens": 450.0,
  "avg_output_tokens": 180.0,
  "avg_total_tokens": 630.0,
  "avg_extraction_latency_ms": 850.0,
  "avg_pipeline_latency_ms": 920.0,
  "generated_at": "2026-02-03 14:30:00",
  "individual_results": [...]
}
```

## Design Principles

### Non-Invasive
- **Does not refactor production pipeline**: Wraps existing provider interface
- **Uses existing orchestrator logic**: Calls `deterministic_issues_from_facts()`
- **Provider-agnostic token tracking**: Falls back gracefully if unavailable

### Reproducible
- **Synthetic documents only**: No PHI exposure
- **Deterministic evaluation**: Same inputs always produce same results
- **Version controlled**: All benchmark data tracked in git

### Production-Quality
- **Clean Python code**: Type hints, dataclasses, proper error handling
- **Idempotent README updates**: Safe to run multiple times
- **Machine-readable output**: JSON format for automation/CI

## CI/CD Integration

To run benchmarks automatically in GitHub Actions:

```yaml
- name: Run Benchmarks
  env:
    HF_API_TOKEN: ${{ secrets.HF_API_TOKEN }}
  run: |
    python scripts/generate_benchmarks.py --model medgemma
```

## Troubleshooting

### "MedGemma provider not available"
- Ensure `HF_API_TOKEN` environment variable is set
- Verify token has access to MedGemma model

### "No benchmark pairs found"
- Check that `benchmarks/inputs/` contains `.txt` files
- Verify matching `.json` files exist in `benchmarks/expected_outputs/`

### "README not found"
- Ensure `.github/README.md` exists at project root
- Script will warn but continue if README is missing

## Development Notes

### Token Tracking
Token usage is currently provider-specific. The baseline model (local heuristic) does not track tokens. To add token tracking for a provider, modify `run_extraction()` in `generate_benchmarks.py`.

### Timing Precision
Uses `time.perf_counter()` for high-resolution timing. Results may vary slightly between runs due to system load.

### Extensibility
To add new metrics:
1. Update `BenchmarkResult` dataclass
2. Add calculation in `run_single_benchmark()`
3. Update `aggregate_metrics()` for aggregation
4. Modify `_generate_benchmark_section()` for README display
