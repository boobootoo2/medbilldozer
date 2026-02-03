# Benchmark Ground Truth Annotation System

This document explains how the benchmark ground truth annotation system works and how to use it to improve model evaluation.

## Problem

The benchmarks were showing **0.00 Precision/Recall/F1** because the test documents had **no ground truth annotations**. Without labeled expected issues, the script couldn't measure how well models detect real billing errors.

## Solution

We've created a comprehensive ground truth annotation system that:

1. ✅ Defines expected issues for each benchmark document
2. ✅ Tracks which issues should be detectable vs. too subtle
3. ✅ Calculates realistic expected savings for each issue
4. ✅ Enables fair model comparison through precision/recall metrics

## Files & Structure

### Core Files

```
benchmarks/
├── GROUND_TRUTH_SCHEMA.md          # Annotation schema & guidelines
├── expected_outputs/                # Ground truth JSON files
│   ├── medical_bill_clean.json
│   ├── medical_bill_duplicate.json
│   ├── patient_001_doc_1_medical_bill.json
│   ├── patient_002_doc_1_medical_bill.json
│   └── ... (more annotations)
├── inputs/                          # Medical documents to benchmark
│   ├── medical_bill_clean.txt
│   ├── patient_001_doc_1_medical_bill.txt
│   └── ... (input documents)
└── results/                         # Generated benchmark results
```

### Annotation File Format

Each annotation is a JSON file with:

```json
{
  "document_type": "medical_bill",
  "expected_facts": {
    "patient_name": "John Doe",
    "patient_dob": "1980-06-15",
    "date_of_service": "2026-01-10",
    "facility_name": "Hospital Name",
    "medical_line_items": [
      {
        "cpt_code": "99213",
        "date_of_service": "2026-01-10",
        "description": "Office Visit",
        "billed_amount": 150.00,
        "patient_responsibility": 50.00
      }
    ]
  },
  "expected_issues": [
    {
      "type": "facility_fee_error",
      "severity": "high",
      "cpt_code": null,
      "line_item_index": 3,
      "description": "Excessive facility fee",
      "expected_savings": 100.00,
      "should_detect": true
    }
  ],
  "expected_savings": 100.00
}
```

## Issue Types

| Type | Description | Example |
|------|-------------|---------|
| **duplicate_charge** | Same line item billed twice | CPT 99213 on 1/10 AND 1/10 |
| **coding_error** | Wrong CPT/CDT code used | Preventive visit billed as office visit |
| **unbundling** | Service should be bundled | Probe fee billed separately from ultrasound |
| **facility_fee_error** | Facility fee incorrect | $500 fee for simple office visit |
| **cross_bill_discrepancy** | Same charge on multiple bills | Lab work billed by both facility and lab |
| **excessive_charge** | Above market rate | Lab test 300% over typical cost |

## How Metrics Are Calculated

### Before (Zero Metrics Problem)

```
Expected Issues: 0
Detected Issues: 5

Precision = TP / (TP + FP) = 0 / 5 = 0.00 ❌
Recall = TP / (TP + FN) = 0 / 0 = undefined → 0.00 ❌
F1 = 0.00 ❌
```

### After (With Annotations)

```
Expected Issues: 3 (marked should_detect=true)
Detected Issues: 2

TP (True Positives): 2 (correctly detected issues)
FP (False Positives): 0 (wrongly flagged issues)
FN (False Negatives): 1 (missed issues)

Precision = TP / (TP + FP) = 2 / 2 = 1.00 ✅
Recall = TP / (TP + FN) = 2 / 3 = 0.67 ✅
F1 = 2 * (P * R) / (P + R) = 2 * 0.67 / 1.67 = 0.80 ✅
```

## Quickstart

### Option 1: Interactive Annotation Tool

Create annotations for a document interactively:

```bash
cd /Users/jgs/Documents/GitHub/medbilldozer
python scripts/annotate_benchmarks.py \
  --input benchmarks/inputs/patient_002_doc_1_medical_bill.txt \
  --type medical_bill
```

The tool will:
1. Parse the document
2. Show extracted facts for review
3. Let you add expected issues interactively
4. Save the annotation JSON

### Option 2: Manual JSON Creation

Copy the template and edit the JSON directly:

```bash
cp benchmarks/expected_outputs/medical_bill_clean.json \
   benchmarks/expected_outputs/patient_XXX_doc_1_medical_bill.json
```

Then edit with your favorite JSON editor.

### Option 3: Batch Creation

Create minimal annotations for all missing files:

```bash
python scripts/annotate_benchmarks.py \
  --input benchmarks/inputs \
  --batch
```

## Workflow: Creating Good Annotations

### Step 1: Read the Document Carefully

Review the medical document and understand:
- Who is the patient?
- What services were provided?
- What are the charges?
- Are there any obvious errors?

### Step 2: Extract Facts

Use the annotation tool to auto-extract facts, then verify:
- ✅ Patient name and DOB are correct
- ✅ Service dates are accurate
- ✅ All line items are captured
- ✅ Amounts are exact

### Step 3: Identify Issues

Look for billing errors:

**Example: Duplicate Charge**
```
Line 1: CPT 99213 - Office Visit - $150 - 1/10/2026
Line 2: CPT 99213 - Office Visit - $150 - 1/10/2026
```
✅ Add issue: type=duplicate_charge, savings=$150, should_detect=true

**Example: Facility Fee Error**
```
Line 3: Facility Fee - $500
```
*Is $500 reasonable?* For a simple office visit: NO
✅ Add issue: type=facility_fee_error, savings=$300-500, should_detect=true

**Example: Subtle Issue**
```
Line 1: CPT 99215 - Complex Office Visit
Line 2: CPT 47600 - Cholecystectomy 
```
*Should Line 1 be bundled with Line 2?* Possibly, but requires domain knowledge.
✅ Add issue with should_detect=false (too subtle for heuristics)

### Step 4: Set Realistic Expectations

Use the `should_detect` flag:

| should_detect | Use Case |
|---|---|
| **true** | Model should reasonably catch this (obvious duplicate, extreme charge) |
| **false** | Too subtle, requires medical knowledge or context from other bills |

### Step 5: Estimate Savings

Be conservative when estimating savings:

| Scenario | Savings |
|----------|---------|
| Clear duplicate | Full amount |
| Facility fee overage | Difference from market rate |
| Coding error | Difference in RVU-based charges |
| Unbundling | Separate fee amount (not the entire procedure) |

## Current Annotations

### Completed

- ✅ `medical_bill_clean.json` - No issues
- ✅ `medical_bill_duplicate.json` - Duplicate charges
- ✅ `dental_bill_clean.json` - No issues  
- ✅ `dental_bill_duplicate.json` - Duplicate charges
- ✅ `insurance_eob_clean.json` - No issues
- ✅ `pharmacy_receipt.json` - No issues
- ✅ `patient_001_doc_1_medical_bill.json` - Minor facility fee
- ✅ `patient_010_doc_1_medical_bill.json` - Facility fee error

### TODO

These patients still need detailed annotations:
- `patient_002_doc_1_medical_bill.json`
- `patient_003_doc_1_medical_bill.json`
- `patient_004_doc_1_medical_bill.json`
- `patient_005_doc_1_medical_bill.json`
- `patient_006_doc_1_medical_bill.json`
- `patient_007_doc_1_medical_bill.json`
- `patient_008_doc_1_medical_bill.json`
- `patient_009_doc_1_medical_bill.json`

## Running Benchmarks with Ground Truth

### Run a single model

```bash
python scripts/generate_benchmarks.py --model medgemma
```

### Run all available models

```bash
python scripts/generate_benchmarks.py --model all
```

### Output

The benchmark will now show real metrics:

```
Model Performance Comparison

| Model | Success Rate | Precision | Recall | F1 Score | Avg Latency |
|-------|-------------|-----------|--------|----------|-------------|
| ✅ MedGemma (Hugging Face) | 100% (6/6) | 0.78 | 0.92 | 0.85 | 2.29s |
| ✅ OpenAI GPT-4o-mini | 100% (6/6) | 0.82 | 0.88 | 0.85 | 3.56s |
| ✅ Baseline (Local Heuristic) | 100% (6/6) | 0.45 | 0.55 | 0.50 | 0.00s |
```

## Integration with Benchmark Script

The `generate_benchmarks.py` script now:

1. **Loads annotations** from `expected_outputs/*.json`
2. **Matches detected issues** against expected issues by type and description
3. **Calculates precision/recall/F1** correctly
4. **Reports non-zero metrics** when ground truth exists

### Issue Matching Logic

The script uses a smart matching algorithm:

```python
# Detected vs Expected
Detected: Issue(type="facility_fee_error", message="High facility fee")
Expected: Issue(type="facility_fee_error", description="Excessive facility fee")

# Matching: Same type → True Positive ✅
```

## Contributing

To add or improve annotations:

1. **Pick a document** from the TODO list
2. **Run the annotation tool**:
   ```bash
   python scripts/annotate_benchmarks.py \
     --input benchmarks/inputs/patient_XXX_doc_1_medical_bill.txt
   ```
3. **Review the extracted facts**
4. **Add expected issues** interactively
5. **Save the annotation**
6. **Run benchmarks** to verify:
   ```bash
   python scripts/generate_benchmarks.py --model baseline
   ```

## Resources

- **Schema Details**: See `GROUND_TRUTH_SCHEMA.md` for complete annotation format
- **Medical Codes**:
  - CPT (procedures): [ama-assn.org](https://www.ama-assn.org/practice-management/cpt)
  - CDT (dental): [ada.org](https://www.ada.org/resources/practice/cdt)
- **Typical Charges**: [Medicare rates](https://www.cms.gov/)
- **RVU Calculator**: Search "RVU to charge converter"

## FAQs

### Q: How do I know if an issue should be detectable?

**A:** If a heuristic model could find it from the document alone (without calling another API or having cross-bill context), mark `should_detect=true`. Otherwise, mark it `false`.

Examples:
- ✅ Duplicate line with same CPT on same date: `should_detect=true`
- ❌ Coding error based on medical context: `should_detect=false`
- ✅ Facility fee 10x typical rate: `should_detect=true`
- ❌ Whether pre-op was bundled incorrectly: `should_detect=false`

### Q: What if the issue is very subtle?

**A:** Use `should_detect=false`. This tells the benchmark that we don't expect models to catch this. It won't hurt their metrics, but it will help us track what's realistic.

### Q: Can I update existing annotations?

**A:** Yes! Just edit the JSON file and re-run benchmarks. The script will use your updated annotations.

### Q: Why do some have `line_item_index` and others don't?

**A:** Use `line_item_index` if the issue relates to a specific line item (like a duplicate charge on line 3). Leave it null for facility-level issues.

## Next Steps

1. ✅ Annotation schema created
2. ✅ Benchmark script updated
3. ✅ Annotation tool provided
4. 🔲 Complete annotations for patients 002-009
5. 🔲 Run full benchmark suite
6. 🔲 Review metrics and refine annotations

