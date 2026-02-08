# Benchmark Engine

medBillDozer uses a comprehensive benchmark system to validate AI provider accuracy against real-world test cases with ground truth annotations.

## Design Philosophy

1. **Patient-Profile Based**: Tests generated from realistic patient scenarios
2. **Ground Truth Annotation**: Expected issues manually annotated by domain experts
3. **Multi-Provider Comparison**: Test all LLM providers against same dataset
4. **Continuous Validation**: Automated regression detection
5. **Kaggle-Ready**: Structured for competition submission and evaluation

## Benchmark Structure

```
benchmarks/
├── inputs/                      # Test documents (medical bills, EOBs)
│   ├── patient_001_colonoscopy.txt
│   ├── patient_002_dental.txt
│   └── ...
│
├── patient_profiles/            # Patient context (insurance, history)
│   ├── patient_001_profile.json
│   ├── patient_002_profile.json
│   └── ...
│
├── expected_outputs/            # Ground truth annotations
│   ├── patient_001_colonoscopy_expected.json
│   ├── patient_002_dental_expected.json
│   └── ...
│
├── results/                     # Benchmark run results
│   ├── 2026-02-05_gpt-4o-mini/
│   ├── 2026-02-05_gemini-2.0-flash/
│   └── ...
│
├── README.md                    # Benchmark system overview
├── ANNOTATION_GUIDE.md          # How to annotate ground truth
└── GROUND_TRUTH_SCHEMA.md       # Expected output schema
```

## Patient Profile Schema

```json
{
  "patient_id": "patient_001",
  "name": "John Smith",
  "age": 45,
  "conditions": ["hypertension", "diabetes"],
  "insurance": {
    "carrier": "Blue Cross Blue Shield",
    "plan_type": "PPO",
    "deductible": 2000,
    "deductible_met": 500,
    "coinsurance": 0.2,
    "out_of_pocket_max": 6000
  },
  "known_providers": [
    {"name": "Dr. Jane Doe", "npi": "1234567890", "in_network": true},
    {"name": "City Hospital", "npi": "0987654321", "in_network": true}
  ],
  "test_scenario": "Colonoscopy with upcoding and duplicate charge"
}
```

## Ground Truth Schema

```json
{
  "document_id": "patient_001_colonoscopy",
  "patient_id": "patient_001",
  "expected_issues": [
    {
      "category": "upcoding",
      "severity": "high",
      "title": "Procedure Upcoded",
      "explanation": "Billed 45385 (with polyp removal) but op notes show diagnostic only",
      "max_savings": 250.00,
      "confidence": 0.95,
      "affected_line_items": ["CPT 45385"]
    },
    {
      "category": "duplicate_charge",
      "severity": "high",
      "title": "Duplicate Anesthesia Charge",
      "explanation": "Anesthesia billed twice on same date",
      "max_savings": 400.00,
      "confidence": 1.0,
      "affected_line_items": ["CPT 00810", "CPT 00810"]
    }
  ],
  "expected_total_savings": 650.00,
  "notes": "Test case for colonoscopy billing with known errors"
}
```

## Benchmark Generation

Generate test cases from patient profiles:

```python
# scripts/generate_patient_benchmarks.py

def generate_benchmark_from_profile(profile: Dict) -> Tuple[str, Dict]:
    """Generate synthetic bill and expected issues from patient profile."""
    
    scenario = profile["test_scenario"]
    
    # Generate realistic bill text
    bill_text = generate_bill_text(
        provider=profile["known_providers"][0],
        patient=profile["name"],
        scenario=scenario
    )
    
    # Define expected issues based on scenario
    expected_issues = generate_expected_issues(scenario, profile)
    
    expected_output = {
        "document_id": f"{profile['patient_id']}_{scenario_slug(scenario)}",
        "patient_id": profile["patient_id"],
        "expected_issues": expected_issues,
        "expected_total_savings": sum(i["max_savings"] for i in expected_issues),
        "notes": f"Generated from profile: {profile['patient_id']}"
    }
    
    return bill_text, expected_output
```

## Running Benchmarks

Execute benchmark suite against specific provider:

```bash
# Run benchmarks for GPT-4o-mini
python scripts/run_benchmarks.py --provider gpt-4o-mini

# Run benchmarks for all providers
python scripts/run_benchmarks.py --all

# Run specific test case
python scripts/run_benchmarks.py --test patient_001_colonoscopy --provider gemini-2.0-flash
```

Implementation:

```python
# scripts/run_benchmarks.py

def run_benchmark_suite(provider_key: str) -> BenchmarkResults:
    """Run all benchmarks against specified provider."""
    
    # Load test cases
    test_cases = load_test_cases("benchmarks/inputs/")
    expected_outputs = load_expected_outputs("benchmarks/expected_outputs/")
    
    results = []
    for test_case in test_cases:
        # Run analysis
        agent = OrchestratorAgent(analyzer_override=provider_key)
        result = agent.run(test_case["text"])
        
        # Compare to ground truth
        expected = expected_outputs[test_case["id"]]
        metrics = evaluate_result(result, expected)
        
        results.append({
            "test_case_id": test_case["id"],
            "provider": provider_key,
            "metrics": metrics,
            "detected_issues": len(result["analysis"].issues),
            "expected_issues": len(expected["expected_issues"]),
            "true_positives": metrics["true_positives"],
            "false_positives": metrics["false_positives"],
            "false_negatives": metrics["false_negatives"],
            "f1_score": metrics["f1_score"]
        })
    
    # Save results
    save_results(results, provider_key)
    
    return aggregate_results(results)
```

## Evaluation Metrics

### Issue Detection Metrics

```python
def evaluate_result(result: Dict, expected: Dict) -> Dict:
    """Compare detected issues to ground truth."""
    
    detected = result["analysis"].issues
    expected_issues = expected["expected_issues"]
    
    # Match issues by category + affected line items
    tp = 0  # True positives
    fp = 0  # False positives
    fn = 0  # False negatives
    
    for expected_issue in expected_issues:
        if issue_detected(expected_issue, detected):
            tp += 1
        else:
            fn += 1
    
    for detected_issue in detected:
        if not issue_expected(detected_issue, expected_issues):
            fp += 1
    
    # Calculate metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }
```

### Savings Estimation Accuracy

```python
def evaluate_savings_accuracy(result: Dict, expected: Dict) -> Dict:
    """Compare estimated savings to ground truth."""
    
    detected_savings = result["analysis"].meta.get("total_max_savings", 0)
    expected_savings = expected["expected_total_savings"]
    
    absolute_error = abs(detected_savings - expected_savings)
    relative_error = absolute_error / expected_savings if expected_savings > 0 else 0
    
    return {
        "detected_savings": detected_savings,
        "expected_savings": expected_savings,
        "absolute_error": absolute_error,
        "relative_error": relative_error,
        "within_20_percent": relative_error <= 0.2
    }
```

## Benchmark Results Format

```json
{
  "benchmark_run_id": "2026-02-05T10:30:00Z",
  "provider": "gpt-4o-mini",
  "test_suite_version": "1.0",
  "total_test_cases": 50,
  "aggregate_metrics": {
    "precision": 0.87,
    "recall": 0.92,
    "f1_score": 0.89,
    "avg_savings_error": 0.15,
    "total_runtime_seconds": 245
  },
  "per_category_metrics": {
    "upcoding": {"precision": 0.90, "recall": 0.95, "f1": 0.92},
    "duplicate_charge": {"precision": 1.0, "recall": 1.0, "f1": 1.0},
    "missing_info": {"precision": 0.75, "recall": 0.80, "f1": 0.77}
  },
  "test_case_results": [
    {
      "test_case_id": "patient_001_colonoscopy",
      "passed": true,
      "f1_score": 1.0,
      "savings_error": 0.05
    }
  ]
}
```

## Benchmark Monitoring Dashboard

Visualize benchmark results over time:

```bash
# Launch monitoring dashboard
streamlit run clinical_performance.py
```

Features:
- Provider comparison matrix
- F1 score trends over time
- Per-category performance
- Savings estimation accuracy
- Regression detection alerts

## Ground Truth Annotation

Manual annotation process:

1. **Review Document**: Read medical bill carefully
2. **Identify Issues**: Mark all billing errors
3. **Categorize**: Assign category (upcoding, duplicate, etc.)
4. **Estimate Savings**: Calculate potential refund
5. **Document Confidence**: Rate certainty (0.0-1.0)
6. **Add Notes**: Explain reasoning

See [ANNOTATION_GUIDE.md](../../benchmarks/ANNOTATION_GUIDE.md) for detailed instructions.

## Continuous Integration

Benchmarks run automatically in CI/CD:

```yaml
# .github/workflows/benchmarks.yml

name: Benchmark Validation

on: [push, pull_request]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run benchmarks
        run: python scripts/run_benchmarks.py --provider gpt-4o-mini
      - name: Check for regression
        run: python scripts/check_regression.py
```

## Next Steps

- [Annotation Guide](../../benchmarks/ANNOTATION_GUIDE.md)
- [Ground Truth Schema](../../benchmarks/GROUND_TRUTH_SCHEMA.md)
- [Testing Guide](../development/testing.md)
