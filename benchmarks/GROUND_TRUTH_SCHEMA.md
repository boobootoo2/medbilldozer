# Ground Truth Annotation Schema

This document describes how to create ground truth annotations for benchmark documents.

## Overview

Each benchmark input document has a corresponding JSON file in `expected_outputs/` that defines:
- The document type
- Expected facts to extract (patient info, line items, totals)
- Expected issues to detect (billing errors, discrepancies)
- Expected savings potential

## JSON Schema

### Basic Structure

```json
{
  "document_type": "medical_bill|dental_bill|pharmacy_receipt|insurance_eob",
  "expected_facts": {
    "patient_name": "string",
    "patient_dob": "YYYY-MM-DD",
    "date_of_service": "YYYY-MM-DD or null",
    "facility_name": "string",
    "medical_line_items": [
      {
        "cpt_code": "string",
        "date_of_service": "YYYY-MM-DD",
        "description": "string",
        "billed_amount": number,
        "patient_responsibility": number
      }
    ]
  },
  "expected_issues": [
    {
      "type": "duplicate_charge|coding_error|unbundling|facility_fee_error|cross_bill_discrepancy|excessive_charge",
      "severity": "high|medium|low",
      "cpt_code": "string or null",
      "line_item_index": number or null,
      "description": "string",
      "expected_savings": number,
      "should_detect": true
    }
  ],
  "expected_savings": number
}
```

## Issue Types

### duplicate_charge
- **Description**: Same line item billed multiple times
- **Example**: CPT 99213 appears twice on same date
- **Expected Savings**: Full duplicate amount

### coding_error
- **Description**: Wrong CPT/CDT code used for procedure
- **Example**: Preventive visit billed as office visit (higher code)
- **Expected Savings**: Difference in allowed amounts

### unbundling
- **Description**: Service should be bundled but billed separately
- **Example**: Ultrasound probe fee billed separately from procedure
- **Expected Savings**: Probe fee amount

### facility_fee_error
- **Description**: Facility fee applied incorrectly (amount or authorization)
- **Example**: $500 facility fee for simple office visit
- **Expected Savings**: Full facility fee amount

### cross_bill_discrepancy
- **Description**: Charge appears on multiple bills from different dates/facilities
- **Example**: Same lab work billed by facility AND lab provider
- **Expected Savings**: Full duplicate amount

### excessive_charge
- **Description**: Charge is significantly higher than market rate
- **Example**: Lab test 300% above typical cost
- **Expected Savings**: Amount over reasonable charge

## Creating Annotations

### Step 1: Identify the Document Type
```json
{
  "document_type": "medical_bill",
  ...
}
```

### Step 2: Extract Expected Facts
Read the document carefully and list all extracted facts:
```json
{
  "expected_facts": {
    "patient_name": "John Doe",
    "patient_dob": "1980-06-15",
    "date_of_service": "2026-01-10",
    "facility_name": "RIVERSIDE MEDICAL CENTER",
    "medical_line_items": [
      {
        "cpt_code": "99213",
        "date_of_service": "2026-01-10",
        "description": "Office Visit, Detailed",
        "billed_amount": 150.00,
        "patient_responsibility": 70.00
      }
    ]
  },
  ...
}
```

### Step 3: Identify Expected Issues
Review the document for billing errors:
```json
{
  "expected_issues": [
    {
      "type": "facility_fee_error",
      "severity": "high",
      "cpt_code": null,
      "line_item_index": 0,
      "description": "Excessive facility fee ($500) for simple office visit",
      "expected_savings": 500.00,
      "should_detect": true
    }
  ],
  ...
}
```

### Step 4: Calculate Total Expected Savings
Sum up all expected savings from detected issues:
```json
{
  "expected_savings": 500.00
}
```

## Examples

### Example 1: Clean Medical Bill (No Issues)

```json
{
  "document_type": "medical_bill",
  "expected_facts": {
    "patient_name": "Emily Chen",
    "patient_dob": "1996-10-25",
    "date_of_service": "2026-02-03",
    "facility_name": "RIVERSIDE FAMILY PRACTICE",
    "medical_line_items": [
      {
        "cpt_code": "99214",
        "date_of_service": "2026-02-03",
        "description": "Office Visit, High Complexity",
        "billed_amount": 200.00,
        "patient_responsibility": 15.00
      }
    ]
  },
  "expected_issues": [],
  "expected_savings": 0.0
}
```

### Example 2: Medical Bill with Issues

```json
{
  "document_type": "medical_bill",
  "expected_facts": {
    "patient_name": "John Smith",
    "patient_dob": "1975-03-12",
    "date_of_service": "2026-01-20",
    "facility_name": "MAJOR SURGICAL CENTER",
    "medical_line_items": [
      {
        "cpt_code": "99215",
        "date_of_service": "2026-01-20",
        "description": "Pre-op Evaluation",
        "billed_amount": 300.00,
        "patient_responsibility": 50.00
      },
      {
        "cpt_code": "47562",
        "date_of_service": "2026-01-20",
        "description": "Laparoscopic Cholecystectomy",
        "billed_amount": 4500.00,
        "patient_responsibility": 800.00
      },
      {
        "cpt_code": "99215",
        "date_of_service": "2026-01-20",
        "description": "Post-op Follow-up",
        "billed_amount": 300.00,
        "patient_responsibility": 50.00
      }
    ]
  },
  "expected_issues": [
    {
      "type": "unbundling",
      "severity": "high",
      "cpt_code": "99215",
      "line_item_index": 0,
      "description": "Pre-op evaluation should be bundled with surgical procedure",
      "expected_savings": 300.00,
      "should_detect": true
    },
    {
      "type": "duplicate_charge",
      "severity": "high",
      "cpt_code": "99215",
      "line_item_index": 2,
      "description": "Post-op follow-up billed on same date as procedure (should be separate visit)",
      "expected_savings": 300.00,
      "should_detect": true
    }
  ],
  "expected_savings": 600.00
}
```

## Notes for Annotators

- Use ISO 8601 date format (YYYY-MM-DD)
- For unknown dates, use `null`
- For unknown amounts, use `0`
- Set `should_detect: true` for issues that the model should realistically catch
- Set `should_detect: false` for issues that are too subtle or require context
- Always verify CPT codes against actual medical coding standards
- Research typical charge ranges for procedures (use Medicare rates as baseline)
- Estimate expected savings conservatively

## How the Benchmark Uses These Annotations

1. **Fact Extraction**: Verifies extracted patient info, dates, line items match expected facts
2. **Issue Detection**: Compares detected issues against expected issues
3. **Precision**: `(true_positives) / (true_positives + false_positives)`
4. **Recall**: `(true_positives) / (true_positives + false_negatives)`
5. **F1 Score**: `2 * (Precision * Recall) / (Precision + Recall)`
