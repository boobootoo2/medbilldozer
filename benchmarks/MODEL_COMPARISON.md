# Model Comparison Guide

This guide explains how to compare different AI models in medBillDozer using the benchmark system.

## Quick Start: Compare All Models

```bash
# Set API keys for models you want to test
export HF_API_TOKEN="your-huggingface-token"
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"

# Run benchmarks for all available models
python scripts/generate_benchmarks.py --model all
```

## Available Models

| Model | Provider | Requires API Key | Speed | Specialty |
|-------|----------|------------------|-------|-----------|
| **MedGemma** | Hugging Face | `HF_API_TOKEN` | Medium | Healthcare-specific language understanding |
| **OpenAI GPT-4o-mini** | OpenAI | `OPENAI_API_KEY` | Slow | General reasoning, JSON adherence |
| **Gemini 1.5 Flash** | Google | `GOOGLE_API_KEY` | Fast | Fast inference, good accuracy |
| **Baseline (Local)** | Built-in | None | Very Fast | Rule-based duplicate detection |

## What Gets Compared

### Accuracy Metrics
- **Extraction Accuracy**: % of documents successfully processed without errors
- **Issue Detection Precision**: Of all issues detected, what % are correct?
- **Issue Detection Recall**: Of all actual issues, what % were detected?
- **F1 Score**: Balance between precision and recall (harmonic mean)

### Performance Metrics
- **Avg Extraction Time**: How long to extract structured data
- **Avg Pipeline Time**: Total time including issue detection
- **Token Usage**: API costs (input/output tokens for cloud models)

## Understanding the Comparison Table

After running `--model all`, you'll see:

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

### How to Interpret

**Highest F1 Score** = Best overall accuracy (balance of precision and recall)  
**Lowest Latency** = Fastest processing  
**Best for Production** = Usually the model with highest F1 within acceptable latency

### Example Scenarios

**Scenario 1: Maximum Accuracy Needed**
- **Choose**: MedGemma (highest F1 score)
- **Trade-off**: Medium latency, requires API key
- **Use case**: Critical financial review, legal disputes

**Scenario 2: Cost-Sensitive / Offline Required**
- **Choose**: Baseline (no API costs)
- **Trade-off**: Lower accuracy, only detects duplicates
- **Use case**: Quick triage, offline environments

**Scenario 3: Speed + Good Accuracy**
- **Choose**: Gemini (fast with good F1)
- **Trade-off**: Requires API key, slightly lower precision
- **Use case**: Real-time web app, high volume processing

**Scenario 4: Best General Performance**
- **Choose**: OpenAI (good balance, best JSON adherence)
- **Trade-off**: Higher latency, API costs
- **Use case**: Complex documents, multi-step reasoning

## Cost Comparison

Estimated cost per 1,000 documents (6 documents avg 650 tokens each):

| Model | Input Cost | Output Cost | Total Cost |
|-------|------------|-------------|------------|
| MedGemma | Free (open-weight) or $0.02 (hosted) | $0.01 | $0.03 |
| OpenAI GPT-4o-mini | $0.15 | $0.60 | $0.75 |
| Gemini 1.5 Flash | $0.05 | $0.15 | $0.20 |
| Baseline | $0.00 | $0.00 | $0.00 |

*Prices based on Feb 2026 API pricing and may vary*

## Detailed Results Location

After running benchmarks, detailed results for each model are saved:

```
benchmarks/results/aggregated_metrics.json
```

This JSON file contains:
- Individual document results
- Per-model breakdowns
- Token usage stats
- Error details (if any)

## Running Sequential Comparisons

To test models one at a time and see detailed output:

```bash
# Test MedGemma
python scripts/generate_benchmarks.py --model medgemma

# Test OpenAI
python scripts/generate_benchmarks.py --model openai

# Test Gemini
python scripts/generate_benchmarks.py --model gemini

# Test Baseline
python scripts/generate_benchmarks.py --model baseline
```

Each run will:
1. Show per-document progress
2. Display summary metrics
3. Save results to JSON
4. Update `.github/README.md` (last model wins)

## Analyzing Strengths and Weaknesses

### MedGemma
**Strengths:**
- Healthcare-specific vocabulary understanding
- Accurate CPT/CDT code interpretation
- Conservative savings estimates

**Weaknesses:**
- Requires Hugging Face API token
- Medium latency (~800ms per document)
- May miss non-medical billing issues

### OpenAI GPT-4o-mini
**Strengths:**
- Best general reasoning
- Excellent JSON schema adherence
- Handles complex multi-document scenarios

**Weaknesses:**
- Slowest (>1s per document)
- Highest API costs
- May hallucinate savings amounts

### Gemini 1.5 Flash
**Strengths:**
- Fast inference (~650ms per document)
- Good accuracy-to-speed ratio
- Lower cost than OpenAI

**Weaknesses:**
- Sometimes less precise than MedGemma
- Requires Google API key
- May miss subtle billing patterns

### Baseline (Local Heuristic)
**Strengths:**
- No API key required
- Very fast (~150ms per document)
- Zero API costs
- 100% privacy (no external calls)

**Weaknesses:**
- Only detects duplicate charges
- Regex-based (brittle)
- No semantic understanding
- Lower recall on edge cases

## Production Recommendations

### For Healthcare Startups
**Primary**: MedGemma (domain expertise)  
**Fallback**: Baseline (offline mode)  
**Rationale**: Best accuracy for healthcare billing, open-weight allows self-hosting

### For Consumer Apps
**Primary**: Gemini (speed + cost)  
**Fallback**: Baseline (free tier)  
**Rationale**: Fast enough for real-time UX, affordable at scale

### For Enterprise/Compliance
**Primary**: Baseline (on-premise)  
**Secondary**: MedGemma (self-hosted)  
**Rationale**: No data leaves network, HIPAA-compliant deployment

### For Research/Academia
**Primary**: OpenAI (best reasoning)  
**Comparison**: All models (benchmarking)  
**Rationale**: Access to cutting-edge models, comparative studies

## Advanced: Custom Model Integration

To add a new model to benchmarks:

### Step 1: Create Provider Class

Create `_modules/providers/your_model_provider.py`:

```python
from _modules.providers.llm_interface import LLMProvider, AnalysisResult

class YourModelProvider(LLMProvider):
    def name(self) -> str:
        return "your-model"
    
    def analyze_document(self, text: str) -> AnalysisResult:
        # Your analysis logic
        pass
```

### Step 2: Update Benchmark Script

In `scripts/generate_benchmarks.py`:

```python
from _modules.providers.your_model_provider import YourModelProvider

# In BenchmarkRunner.__init__():
elif model == "your-model":
    self.provider = YourModelProvider()
```

### Step 3: Update Argument Choices

```python
choices=["medgemma", "openai", "gemini", "baseline", "your-model", "all"]
```

### Step 4: Run Benchmarks

```bash
python scripts/generate_benchmarks.py --model your-model
```

## Troubleshooting Multi-Model Runs

### Issue: Some models fail during `--model all`

**Solution**: The script continues running other models. Check error output for specific failures.

### Issue: API rate limits

**Solution**: Models are tested sequentially to avoid rate limits. If you still hit limits, test individually.

### Issue: Inconsistent results across runs

**Cause**: LLMs have non-deterministic outputs even with temperature=0

**Solution**: Run benchmarks multiple times and average results, or use baseline for reproducibility.

### Issue: Out of memory errors

**Cause**: Loading multiple models or large documents

**Solution**: Test models individually or increase system RAM

## Continuous Monitoring

For production deployments, consider:

1. **Weekly benchmarks**: Track model drift over time
2. **A/B testing**: Compare model performance on real user data
3. **Cost monitoring**: Track API spend per model
4. **Latency alerts**: Set SLAs for response times

## Example: CI/CD Integration

Add to `.github/workflows/benchmark.yml`:

```yaml
name: Weekly Model Comparison

on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight

jobs:
  benchmark-all-models:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run All Models
        env:
          HF_API_TOKEN: ${{ secrets.HF_API_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
        run: |
          python scripts/generate_benchmarks.py --model all
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-comparison
          path: benchmarks/results/aggregated_metrics.json
```

## Summary

The `--model all` option provides:
- ✅ Automatic detection of available models
- ✅ Side-by-side performance comparison
- ✅ Clear winner identification (highest F1)
- ✅ Cost and latency trade-off analysis
- ✅ Production-ready recommendations

**Next Steps**:
1. Run `python scripts/generate_benchmarks.py --model all`
2. Review comparison table
3. Check detailed JSON results
4. Choose model based on your priorities (accuracy/speed/cost)
5. Deploy chosen model in production
