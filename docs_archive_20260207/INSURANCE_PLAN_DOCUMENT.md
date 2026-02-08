# Insurance Plan Document - Production Workflow

## Overview

The Production Workflow now includes an **Insurance Plan Document** that displays eligible expenses with in-network and out-of-network approved prices. This reference document helps users understand what their insurance will pay for specific procedures and identify when they're being overcharged.

## Key Features

### 1. Comprehensive Plan Information
- **Coverage Details**: Deductibles, out-of-pocket maximums, current year totals
- **Copays**: Primary care, specialist, urgent care, ER, prescriptions
- **Coinsurance Rates**: In-network vs out-of-network percentages
- **Plan Metadata**: Carrier, member ID, group number, effective dates

### 2. Eligible Expenses Table
Shows approved prices for common procedures:
- **Procedure Code**: CPT/CDT codes
- **Description**: Service details
- **In-Network Allowed**: What insurance approves for in-network providers
- **Out-of-Network Allowed**: What insurance approves for out-of-network providers
- **Typical Billed**: What providers usually charge

### 3. Price Comparison
Helps identify:
- **Balance Billing**: When provider charges above allowed amount
- **Network Savings**: Difference between in/out-of-network
- **Overpayment**: When you're charged more than approved rate

## Document Structure

### Plan Document Format

```
INSURANCE PLAN DOCUMENT - Horizon PPO Plus

Carrier: Horizon Blue Cross Blue Shield
Plan Type: PPO
Member ID: HPP-8743920
Group Number: GRP-55512
Plan Year: 2026
Effective Date: 2026-01-01

DEDUCTIBLE:
Individual: $1,500.00 (Met: $450.00)
Family:     $3,000.00 (Met: $450.00)

OUT-OF-POCKET MAXIMUM:
Individual: $5,000.00 (Met: $1,250.00)
Family:     $10,000.00 (Met: $1,250.00)

COPAYS:
Primary Care:   $30.00
Specialist:     $60.00
Urgent Care:    $75.00
Emergency Room: $250.00
Generic Rx:     $10.00
Brand Rx:       $35.00

COINSURANCE:
In-Network:     20% (after deductible)
Out-of-Network: 40% (after deductible)

ELIGIBLE EXPENSES - APPROVED PRICES:
(Shows in-network vs out-of-network allowed amounts)

  Code     | Description                                   | In-Network  | Out-Network | Typical Bill
  ---------|-----------------------------------------------|-------------|-------------|-------------
  99213    | Office Visit - Established Patient (15-29 min)| In: $150.00 | Out: $120.00 | Typical: $200.00
  99214    | Office Visit - Established Patient (30-39 min)| In: $220.00 | Out: $176.00 | Typical: $280.00
  80053    | Comprehensive Metabolic Panel                 | In: $120.00 | Out: $96.00  | Typical: $180.00
  45378    | Colonoscopy, Diagnostic                       | In: $1,400.00| Out: $1,120.00| Typical: $2,500.00
  70553    | MRI Brain without and with contrast           | In: $2,200.00| Out: $1,760.00| Typical: $3,500.00
  D0120    | Periodic Oral Evaluation                      | In: $70.00  | Out: $56.00  | Typical: $85.00
  D0220    | Intraoral Periapical X-ray - First Film       | In: $35.00  | Out: $28.00  | Typical: $50.00

NOTE: Charges above allowed amounts are not eligible for reimbursement.
Out-of-network providers may balance bill the difference.
```

## Sample Eligible Services

The plan includes 7 common procedures:

### Medical Procedures

| Code | Description | In-Network | Out-Network | Typical Bill |
|------|-------------|-----------|-------------|--------------|
| 99213 | Office Visit (15-29 min) | $150 | $120 | $200 |
| 99214 | Office Visit (30-39 min) | $220 | $176 | $280 |
| 80053 | Comprehensive Metabolic Panel | $120 | $96 | $180 |
| 45378 | Colonoscopy, Diagnostic | $1,400 | $1,120 | $2,500 |
| 70553 | MRI Brain w/ contrast | $2,200 | $1,760 | $3,500 |

### Dental Procedures

| Code | Description | In-Network | Out-Network | Typical Bill |
|------|-------------|-----------|-------------|--------------|
| D0120 | Periodic Oral Evaluation | $70 | $56 | $85 |
| D0220 | Periapical X-ray | $35 | $28 | $50 |

## Use Cases

### Example 1: Identifying Balance Billing

**Scenario:**
- Provider bills $2,500 for colonoscopy (code 45378)
- Plan allows $1,400 in-network
- Insurance pays 80% after deductible = $1,120
- Patient responsibility: $280 (20% coinsurance)

**Analysis:**
- Provider billed: $2,500
- Allowed amount: $1,400
- **Excess charge: $1,100** ← Not patient's responsibility if in-network
- Patient should only pay: $280

### Example 2: Network Savings Comparison

**Scenario:** Office visit (99213)

| Provider Type | Allowed | Patient Pays (20% coinsurance) |
|--------------|---------|-------------------------------|
| In-Network | $150 | $30 + copay |
| Out-of-Network | $120 | $48 (40% coinsurance) + balance billing up to $80 |

**Savings by staying in-network: $50+**

### Example 3: Validating Lab Charges

**Scenario:**
- Lab bills $250 for metabolic panel (80053)
- Plan allows $120 in-network
- Patient billed: $125

**Analysis:**
- Billed amount: $250
- Allowed amount: $120
- **Overcharge: $130**
- If deductible met, patient owes: $24 (20% of $120)
- **Extra charge: $101** ← Should be adjusted

## Integration with Other Documents

### Cross-Reference Analysis

The plan document helps validate:

1. **Medical Bills** → Check if charges exceed allowed amounts
2. **Insurance EOBs** → Verify insurance used correct allowed amounts
3. **Receipts** → Confirm patient paid correct coinsurance/copay

### Workflow Example

```
1. Import provider bill: $2,500 for colonoscopy
   ↓
2. Check plan document: Allowed amount = $1,400
   ↓
3. Flag difference: $1,100 overcharge
   ↓
4. Import insurance EOB: Shows $1,400 allowed
   ↓
5. Analysis: Provider may be balance billing
   ↓
6. Action: Contact provider for adjustment
```

## Technical Implementation

### Data Structure

```python
SAMPLE_INSURANCE_PLAN_DOCUMENT = {
    'plan_id': 'PLAN-DEMO-001',
    'plan_name': 'Horizon PPO Plus',
    'carrier': 'Horizon Blue Cross Blue Shield',
    'member_id': 'HPP-8743920',
    'group_number': 'GRP-55512',
    'effective_date': '2026-01-01',
    'plan_year': '2026',
    'network_type': 'PPO',
    
    # Coverage
    'deductible_individual': 1500.00,
    'deductible_met_individual': 450.00,
    'out_of_pocket_max_individual': 5000.00,
    'out_of_pocket_met_individual': 1250.00,
    
    # Copays
    'copay_primary_care': 30.00,
    'copay_specialist': 60.00,
    
    # Coinsurance
    'coinsurance_in_network': 0.20,
    'coinsurance_out_of_network': 0.40,
    
    # Eligible services
    'eligible_services': [
        {
            'procedure_code': '99213',
            'description': 'Office Visit',
            'in_network_allowed': 150.00,
            'out_of_network_allowed': 120.00,
            'typical_billed': 200.00,
            'subject_to_deductible': True,
            'copay_applies': True
        },
        # ... more services
    ]
}
```

### Conversion to ProfileDocument

```python
def load_insurance_plan_as_document() -> Optional[ProfileDocument]:
    """Convert insurance plan data to ProfileDocument format."""
    plan = SAMPLE_INSURANCE_PLAN_DOCUMENT
    
    # Build services table
    services_table = []
    for svc in plan['eligible_services']:
        services_table.append(
            f"{svc['procedure_code']} | {svc['description']} | "
            f"In: ${svc['in_network_allowed']:.2f} | "
            f"Out: ${svc['out_of_network_allowed']:.2f}"
        )
    
    return {
        'doc_id': 'DOC-PLAN-001',
        'doc_type': 'insurance_eob',
        'provider': plan['carrier'],
        'amount': 0.0,  # Reference document
        'flagged': False,
        'status': 'completed',  # Already processed
        'content': f"""... formatted plan details ..."""
    }
```

### Initialization

Plan document is automatically included on startup:

```python
def initialize_prod_workflow_state():
    all_docs = copy.deepcopy(PRELOADED_DOCUMENTS)
    
    # Add plan document
    plan_doc = load_insurance_plan_as_document()
    if plan_doc:
        all_docs.append(plan_doc)
    
    # Add receipts and imports
    all_docs.extend(load_receipts_as_documents())
    all_docs.extend(load_imported_line_items_as_documents())
    
    st.session_state.prod_workflow_documents = all_docs
```

## Document Characteristics

### Special Properties

- **Document ID**: `DOC-PLAN-001`
- **Type**: `insurance_eob`
- **Amount**: `$0.00` (reference document, no balance due)
- **Flagged**: `False` (not an issue to review)
- **Status**: `completed` (reference data, no analysis needed)
- **Provider**: Insurance carrier name

### Display Location

Appears in Production Workflow alongside:
- 6 preloaded sample documents
- 3 imported line items
- User-uploaded receipts

## Benefits

### For Users

1. **Price Transparency**: See what insurance actually approves
2. **Overcharge Detection**: Compare bills to allowed amounts
3. **Network Guidance**: Understand in/out-of-network differences
4. **Budget Planning**: Know expected out-of-pocket costs

### For Analysis

1. **Validation**: Cross-check provider charges
2. **Flagging**: Auto-flag charges above allowed amounts
3. **Recommendations**: Suggest in-network alternatives
4. **Reconciliation**: Match EOBs to plan terms

## Future Enhancements

### Planned Features

1. **Real Plan Import**
   - Upload actual plan documents
   - Extract coverage details automatically
   - Update eligible expenses from plan PDFs

2. **Dynamic Pricing**
   - Load plan-specific fee schedules
   - Update allowed amounts per provider
   - Track annual changes

3. **Automated Validation**
   - Auto-compare bills to plan prices
   - Flag balance billing automatically
   - Calculate exact patient responsibility

4. **Cost Estimator**
   - Predict costs for upcoming procedures
   - Show deductible impact
   - Compare providers by allowed amounts

5. **Plan Comparison**
   - Load multiple plans
   - Compare coverage side-by-side
   - Calculate total cost under each plan

## Best Practices

### For Accurate Analysis

1. **Keep Plan Updated**: Update deductible met amounts regularly
2. **Verify Network Status**: Confirm provider network participation
3. **Check Effective Dates**: Ensure plan year matches service dates
4. **Include All Plans**: Add dental, vision, pharmacy plans separately

### For Users

1. **Reference First**: Check plan allowed amounts before paying
2. **Question Overcharges**: Ask providers about charges above allowed
3. **Know Your Network**: Stay in-network to avoid balance billing
4. **Track Progress**: Monitor deductible and out-of-pocket totals

## Related Documentation

- [Imported Data Integration](IMPORTED_DATA_INTEGRATION.md)
- [Receipt Integration](PROD_WORKFLOW_RECEIPTS.md)
- [Profile Editor](PROFILE_EDITOR_QUICKSTART.md)
- [Analysis Workflow](TWO_TAB_WORKFLOW.md)

---

**Last Updated**: January 31, 2026  
**Version**: 1.0  
**Status**: Production Ready
