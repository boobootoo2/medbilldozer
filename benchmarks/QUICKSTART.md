# Benchmark Quickstart Guide

Get benchmark results in 3 steps.

## Step 1: Set Up Environment

### For All Models (Optional - only set what you have)

```bash
# MedGemma (optional)
export HF_API_TOKEN="hf_your_token_here"

# OpenAI (optional)
export OPENAI_API_KEY="sk-your-key-here"

# Gemini (optional)
export GOOGLE_API_KEY="your-key-here"

# Baseline requires no API key
```

You can set one, some, or all API keys. The `--model all` option will automatically detect which models are available.

## Step 2: Run Benchmarks

```bash
# From project root
cd /path/to/medbilldozer

# Run ALL available models (recommended)
python scripts/generate_benchmarks.py --model all

# OR run specific models:
python scripts/generate_benchmarks.py --model medgemma
python scripts/generate_benchmarks.py --model openai
python scripts/generate_benchmarks.py --model gemini
python scripts/generate_benchmarks.py --model baseline
```

## Step 3: Check Results

### Console Output

You'll see real-time progress and a summary:

```
🔬 Running benchmarks on 6 documents...
📊 Model: medgemma

[1/6] medical_bill_duplicate... ✅ 850ms
[2/6] dental_bill_clean... ✅ 720ms
[3/6] pharmacy_receipt... ✅ 680ms
[4/6] dental_bill_duplicate... ✅ 830ms
[5/6] insurance_eob_clean... ✅ 750ms
[6/6] medical_bill_clean... ✅ 710ms

======================================================================
SUMMARY: MEDGEMMA
======================================================================
Documents: 6
Successful: 6
Extraction Accuracy: 100.0%
Issue Precision: 1.00
Issue Recall: 1.00
Issue F1 Score: 1.00
JSON Validity: 100.0%
Avg Tokens: 650
Avg Extraction Time: 757ms
Avg Pipeline Time: 820ms
======================================================================

💾 Results saved to: benchmarks/results/aggregated_metrics.json
📝 Updated README: .github/README.md

✅ All benchmarks complete!
```

When running `--model all`, you'll also see a comparison table:

```
======================================================================
MODEL COMPARISON
======================================================================
Model           Precision    Recall     F1         Latency   
----------------------------------------------------------------------
medgemma        1.00         1.00       1.00       0.82s     
openai          0.95         0.95       0.95       1.20s     
gemini          0.90         0.95       0.92       0.65s     
baseline        0.85         0.90       0.87       0.15s     
======================================================================
```

### JSON Results

Check `benchmarks/results/aggregated_metrics.json` for detailed machine-readable results.

### Updated README

View `.github/README.md` - a new benchmark section is automatically added/updated.

## Common Issues

### "MedGemma provider not available"

**Problem**: `HF_API_TOKEN` not set or invalid.

**Solution**:
```bash
export HF_API_TOKEN="your-actual-token"
python scripts/generate_benchmarks.py --model medgemma
```

### "No benchmark pairs found"

**Problem**: Input/output files missing.

**Solution**: Ensure these directories exist with matching files:
- `benchmarks/inputs/*.txt`
- `benchmarks/expected_outputs/*.json`

### Module Import Errors

**Problem**: Python can't find `_modules`.

**Solution**: Run from project root:
```bash
cd /path/to/medbilldozer
python scripts/generate_benchmarks.py --model baseline
```

## Next Steps

- **Add More Benchmarks**: See `benchmarks/README.md` for how to add test cases
- **CI Integration**: Add to GitHub Actions for automated testing
- **Compare Models**: Run both `medgemma` and `baseline` to compare performance

## Example Expected Output Section in README

After running, `.github/README.md` will contain:

```markdown
<!-- BENCHMARK_SECTION_START -->

## Benchmark Analysis

_Evaluated on 6 synthetic healthcare billing documents._

### Medgemma Model Results

- **Extraction Accuracy**: 100.0%
- **Issue Detection Precision**: 1.00
- **Issue Detection Recall**: 1.00
- **Issue Detection F1 Score**: 1.00
- **JSON Validity Rate**: 100.0%
- **Avg Tokens per Doc**: 650
  - Input: 450
  - Output: 200
- **Avg Extraction Time**: 0.76s
- **Avg Full Pipeline Time**: 0.82s

_Generated: 2026-02-03 14:30:00_

<!-- BENCHMARK_SECTION_END -->
```

## Benchmark Coverage

Current test suite includes:

| Document Type | Has Duplicates | File |
|--------------|----------------|------|
| Medical Bill | ✅ Yes | `medical_bill_duplicate.txt` |
| Medical Bill | ❌ No | `medical_bill_clean.txt` |
| Dental Bill | ✅ Yes | `dental_bill_duplicate.txt` |
| Dental Bill | ❌ No | `dental_bill_clean.txt` |
| Pharmacy Receipt | ❌ No | `pharmacy_receipt.txt` |
| Insurance EOB | ❌ No | `insurance_eob_clean.txt` |

**Total**: 6 documents, 2 with intentional errors

## Performance Notes

- **Extraction latency** includes model API call time
- **Pipeline latency** includes extraction + deterministic reconciliation
- **Token counts** only available for cloud-based models (not baseline)
- Times may vary based on network latency and system load

## Need Help?

See full documentation: `benchmarks/README.md`
