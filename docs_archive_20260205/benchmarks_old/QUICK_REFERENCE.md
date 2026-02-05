# Quick Reference: Ground Truth Annotations

## Problem Fixed

❌ **Before**: Precision/Recall/F1 all 0.00  
✅ **After**: Real metrics (e.g., 0.78 / 0.95 / 0.83)

## Quick Start

### 1. Annotate a Document

```bash
python scripts/annotate_benchmarks.py \
  --input benchmarks/inputs/patient_002_doc_1_medical_bill.txt
```

### 2. Run Benchmarks

```bash
python scripts/generate_benchmarks.py --model all
```

### 3. Check Results

View `.github/README.md` - metrics now show real performance!

## Annotation Format

```json
{
  "document_type": "medical_bill",
  "expected_facts": {
    "patient_name": "John Doe",
    "patient_dob": "1980-06-15",
    "date_of_service": "2026-01-10",
    "facility_name": "Hospital",
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
      "type": "duplicate_charge",
      "severity": "high",
      "cpt_code": "99213",
      "line_item_index": 1,
      "description": "Duplicate office visit charge",
      "expected_savings": 150.00,
      "should_detect": true
    }
  ],
  "expected_savings": 150.00
}
```

## Issue Types

| Type | What to Look For |
|------|-----------------|
| **duplicate_charge** | Same CPT code on same date |
| **coding_error** | Wrong CPT code selected |
| **unbundling** | Service billed separately instead of bundled |
| **facility_fee_error** | Fee seems too high for procedure |
| **cross_bill_discrepancy** | Charge appears on multiple bills |
| **excessive_charge** | Charge significantly above market rate |

## Key Concepts

### should_detect

Set to `true` if heuristic model should catch it:
- ✅ `true`: Obvious errors (exact duplicates, extreme charges)
- ❌ `false`: Subtle issues (requires medical knowledge, context from other bills)

### expected_savings

Realistic dollar amount a patient could save:
- Duplicates: Full amount
- Facility fees: Difference from typical charge
- Coding errors: Difference in allowed amounts
- Unbundling: Separate fee only (not procedure total)

## Common Workflows

### Edit Existing Annotation

```bash
vim benchmarks/expected_outputs/patient_002_doc_1_medical_bill.json
```

### Check What's Annotated

```bash
ls benchmarks/expected_outputs/
```

### Auto-Extract Facts Only

```bash
python scripts/annotate_benchmarks.py \
  --input benchmarks/inputs/patient_003_doc_1_medical_bill.txt \
  --batch
```

## Troubleshooting

### Metrics Still Show 0.00

**Problem**: `expected_issues` is empty array

**Solution**: Add at least one issue with `should_detect: true`

### Issue Not Detected

**Problem**: Model missed an issue you added

**Possible causes**:
- Model detection needs improvement
- Issue is too subtle (set `should_detect: false`)
- Issue signature doesn't match (check type string)

### Too Many False Positives

**Problem**: Model detecting issues that don't exist

**Solution**: Add detected issue type to expected_issues as false positives for tracking

## File Locations

```
benchmarks/
├── GROUND_TRUTH_SCHEMA.md        ← Format documentation
├── ANNOTATION_GUIDE.md            ← Complete workflow guide
├── IMPLEMENTATION_NOTES.md        ← This implementation summary
├── inputs/                        ← Medical documents
│   └── patient_001_doc_1_medical_bill.txt
└── expected_outputs/              ← Ground truth JSON files
    └── patient_001_doc_1_medical_bill.json
```

## Scripts

```bash
# Create/update annotations interactively
python scripts/annotate_benchmarks.py --input benchmarks/inputs/FILE.txt

# Run benchmarks with ground truth
python scripts/generate_benchmarks.py --model all

# View/edit JSON directly
vim benchmarks/expected_outputs/FILE.json
```

## Metrics Math

```
TP = True Positives (correctly detected)
FP = False Positives (wrongly flagged)  
FN = False Negatives (missed)

Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1 = 2 * (P * R) / (P + R)
```

## Status

- ✅ Annotation system created
- ✅ Benchmark script updated
- ✅ Initial annotations (patients 1, 10)
- 🔲 Complete annotations (patients 2-9)
- 🔲 Run full benchmark suite

## Resources

- Schema: `GROUND_TRUTH_SCHEMA.md`
- Workflow: `ANNOTATION_GUIDE.md`
- Implementation: `IMPLEMENTATION_NOTES.md`

