# Cross-Document Reasoning

medBillDozer analyzes multiple related documents together to detect inconsistencies, duplicates, and insurance calculation errors that wouldn't be visible from a single document.

## Use Cases

### 1. Bill + EOB Reconciliation
Validate that insurance company paid correctly:
- Upload medical bill from provider
- Upload Explanation of Benefits (EOB) from insurance
- System matches transactions and validates calculations

### 2. Duplicate Charge Detection
Identify charges appearing on multiple documents:
- Same procedure billed by multiple providers
- Charges on both hospital and physician bills
- Duplicate copays or deductibles

### 3. Coverage Matrix Analysis
Match bills to insurance plans:
- Verify in-network vs out-of-network status
- Validate deductible application
- Check co-insurance percentages
- Confirm out-of-pocket max enforcement

## How It Works

### Transaction Normalization

Each document's charges are normalized to a standard format:

```python
{
  "transaction_id": "hash_of_content",      # Deterministic ID
  "source_document": "doc_001",             # Which document
  "service_date": "2024-01-15",             # When performed
  "provider": "Dr. Smith",                  # Who provided
  "cpt_code": "99213",                      # What service
  "charge": 150.00,                         # Billed amount
  "payment": 120.00,                        # Amount paid
  "patient_responsibility": 30.00,          # What patient owes
  "description": "Office visit"             # Plain text
}
```

### Deduplication Algorithm

Transactions are deduplicated across documents:

```python
def deduplicate_transactions(all_transactions: List[Dict]) -> List[Dict]:
    """Remove duplicate transactions across documents."""
    
    seen = {}
    deduplicated = []
    
    for txn in all_transactions:
        # Generate deterministic key
        key_parts = [
            txn.get("service_date", ""),
            txn.get("provider", ""),
            txn.get("cpt_code", ""),
            str(txn.get("charge", 0))
        ]
        key = "|".join(key_parts)
        
        if key not in seen:
            seen[key] = txn
            deduplicated.append(txn)
        else:
            # Mark as duplicate
            txn["is_duplicate"] = True
            txn["duplicate_of"] = seen[key]["source_document"]
            deduplicated.append(txn)
    
    return deduplicated
```

### Coverage Matrix

Matches bills to insurance plans:

```
┌─────────────────────────────────────────────────────────────┐
│                    Coverage Matrix                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Document 1: Medical Bill ($2,450)                           │
│  ├─ Provider: Dr. Smith (NPI: 1234567890)                    │
│  ├─ Network Status: In-Network ✓                             │
│  └─ Insurance: Blue Cross PPO                                │
│                                                               │
│  Document 2: Insurance EOB                                   │
│  ├─ Claim Amount: $2,450 ✓                                   │
│  ├─ Allowed Amount: $1,800                                   │
│  ├─ Insurance Paid: $1,440 (80% of $1,800)                   │
│  ├─ Patient Owes: $360 (20% co-insurance)                    │
│  └─ Deductible Applied: $500 (already met)                   │
│                                                               │
│  ✅ MATCH: Bill and EOB align                                │
│  💰 Potential Savings: $0 (correctly processed)              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Cross-Document Issue Detection

### 1. Insurance Calculation Errors

Compare billed amount to EOB payment:

```python
def detect_insurance_errors(bill: Dict, eob: Dict) -> List[Issue]:
    """Detect discrepancies between bill and EOB."""
    
    issues = []
    
    # Check if amounts match
    bill_total = bill["facts"].get("total_charge", 0)
    eob_claim = eob["facts"].get("claim_amount", 0)
    
    if abs(bill_total - eob_claim) > 0.01:
        issues.append(Issue(
            category="calculation_error",
            severity="high",
            title="Bill/EOB Amount Mismatch",
            explanation=f"Provider billed ${bill_total} but EOB shows ${eob_claim}",
            max_savings=abs(bill_total - eob_claim)
        ))
    
    # Check co-insurance calculation
    allowed = eob["facts"].get("allowed_amount", 0)
    paid = eob["facts"].get("insurance_paid", 0)
    coinsurance_rate = eob["facts"].get("coinsurance", 0.2)
    
    expected_insurance = allowed * (1 - coinsurance_rate)
    if abs(paid - expected_insurance) > 0.01:
        issues.append(Issue(
            category="incorrect_insurance",
            severity="high",
            title="Incorrect Co-Insurance Calculation",
            explanation=f"Insurance should pay ${expected_insurance} but paid ${paid}",
            max_savings=abs(paid - expected_insurance)
        ))
    
    return issues
```

### 2. Duplicate Charges

Detect same service across multiple documents:

```python
def detect_cross_document_duplicates(documents: List[Dict]) -> List[Issue]:
    """Find duplicate charges across documents."""
    
    all_transactions = []
    for doc in documents:
        txns = normalize_line_items(doc.get("facts", {}).get("line_items", []))
        for txn in txns:
            txn["source_document"] = doc["document_id"]
            all_transactions.append(txn)
    
    duplicates = find_duplicates(all_transactions)
    
    issues = []
    for dup in duplicates:
        issues.append(Issue(
            category="duplicate_charge",
            severity="high",
            title=f"Duplicate Charge: {dup['description']}",
            explanation=f"Same service appears on {dup['source_document']} and {dup['duplicate_of']}",
            max_savings=dup["charge"],
            affected_line_items=[dup["cpt_code"]]
        ))
    
    return issues
```

### 3. Network Status Validation

Verify provider network status matches EOB:

```python
def validate_network_status(bill: Dict, eob: Dict, insurance_plan: Dict) -> List[Issue]:
    """Validate in-network vs out-of-network status."""
    
    issues = []
    
    provider_npi = bill["facts"].get("provider_npi")
    eob_network_status = eob["facts"].get("network_status", "unknown")
    
    # Check against insurance plan's provider directory
    in_network_npis = insurance_plan.get("in_network_providers", [])
    
    expected_status = "in-network" if provider_npi in in_network_npis else "out-of-network"
    
    if eob_network_status != expected_status:
        # EOB shows out-of-network but provider is in-network
        if expected_status == "in-network" and eob_network_status == "out-of-network":
            # Calculate savings if properly processed as in-network
            in_network_rate = 0.8  # 80% coverage
            out_network_rate = 0.6  # 60% coverage
            allowed = eob["facts"].get("allowed_amount", 0)
            
            savings = allowed * (in_network_rate - out_network_rate)
            
            issues.append(Issue(
                category="incorrect_network_status",
                severity="high",
                title="Provider Incorrectly Marked Out-of-Network",
                explanation=f"Provider NPI {provider_npi} is in your network but processed as out-of-network",
                max_savings=savings
            ))
    
    return issues
```

## Aggregate Savings Calculation

Calculate total potential refund across all documents:

```python
def calculate_aggregate_savings(documents: List[Dict]) -> Dict:
    """Calculate total savings across all documents."""
    
    total_savings = 0.0
    savings_by_category = {}
    savings_by_document = {}
    
    for doc in documents:
        doc_savings = 0.0
        analysis = doc.get("analysis")
        
        if analysis:
            for issue in analysis.issues:
                savings = issue.max_savings or 0.0
                total_savings += savings
                doc_savings += savings
                
                category = issue.category
                savings_by_category[category] = savings_by_category.get(category, 0) + savings
        
        savings_by_document[doc["document_id"]] = doc_savings
    
    return {
        "total_savings": total_savings,
        "by_category": savings_by_category,
        "by_document": savings_by_document,
        "document_count": len(documents)
    }
```

## UI Visualization

### Coverage Matrix Table

```
┌────────────────────────────────────────────────────────────────┐
│ Document         │ Type        │ Total   │ Matched │ Issues    │
├────────────────────────────────────────────────────────────────┤
│ Medical Bill     │ Provider    │ $2,450  │ EOB-001 │ 0         │
│ Insurance EOB    │ Payer       │ $2,450  │ Bill-01 │ 0         │
│ Payment Receipt  │ Remittance  │ $360    │ EOB-001 │ 1 (dup)   │
└────────────────────────────────────────────────────────────────┘

Cross-Document Issues:
  🟡 Duplicate copay charge on receipt (already in EOB): $30
```

### Transaction Flow Diagram

```
Medical Bill                EOB                    Payment Receipt
─────────────              ─────                   ────────────────
$2,450 billed    ────────► $1,800 allowed         
                           $1,440 ins. paid ──────► Confirmed ✓
                           $360 patient owes ─────► $360 paid ✓
                                                    $30 copay ✗ (dup)
```

## Implementation

See `src/medbilldozer/core/`:
- `transaction_normalization.py` - Transaction deduplication
- `coverage_matrix.py` - Cross-document matching
- `analysis_runner.py` - Aggregate calculation

## Performance

- **Deduplication**: O(n) where n = total transactions
- **Coverage Matrix**: O(n²) worst case for matching
- **Aggregate Savings**: O(n×m) where n = documents, m = issues per doc

Typical performance: <1 second for 10 documents with 100 total transactions

## Best Practices

1. **Upload Related Documents Together**: Bill + EOB + receipt in same session
2. **Use Consistent Names**: Help system match documents (same patient name)
3. **Include Dates**: Service dates enable accurate matching
4. **Provide Insurance Info**: Add plan details in Profile Editor for validation
5. **Review Coverage Matrix**: Check document matching before trusting results

## Next Steps

- [User Workflow](user_workflow.md)
- [Analysis Model](analysis_model.md)
- [Coverage Matrix Implementation](../architecture/system_overview.md)
