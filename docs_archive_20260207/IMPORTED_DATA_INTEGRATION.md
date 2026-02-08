# Imported Data Integration - Production Workflow

## Overview

The Production Workflow now automatically integrates imported data from the Profile Editor's importer. When you import and save insurance EOBs or provider bills, the line items appear as documents in the Production Workflow for analysis.

## Key Features

### 1. Automatic Import Integration
- **Insurance EOBs**: Import from insurance companies → Line items become documents
- **Provider Bills**: Import from healthcare providers → Line items become documents
- **CSV Imports**: Import structured data → Line items become documents
- **Automatic Loading**: Imports load when Production Workflow initializes
- **Manual Reload**: Click "📥 Reload Data" to add new imports

### 2. Intelligent Document Creation
- **One Document per Line Item**: Each billing line item becomes a separate document
- **Type Detection**: Auto-detects medical bill, dental bill, or pharmacy receipt
- **Smart Flagging**: Automatically flags high or suspicious charges
- **Profile Assignment**: Assigns to active profile (Policy Holder or Dependent)

### 3. Data Mapping

Imported line items are converted to ProfileDocument format:

```python
Line Item (from importer)          ProfileDocument (in Prod Workflow)
────────────────────────────       ────────────────────────────────
line_item_id: "item_001"       →   doc_id: "DOC-IMPORT-001"
provider_name: "Valley Medical"→   provider: "Valley Medical"
service_date: "2026-01-12"     →   service_date: "2026-01-12"
patient_responsibility: 1200   →   amount: 1200.00
procedure_code: "45378"        →   Included in content
billed_amount: 2500            →   Included in content
paid_by_insurance: 200         →   Included in content
```

## How It Works

### Import Workflow

```
┌──────────────────────────────────────────────────────────────┐
│                       Profile Editor                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. User Imports Data                                        │
│     ├─ Insurance EOB (PDF, CSV)                             │
│     ├─ Provider Bill (PDF, CSV)                             │
│     └─ Paste text data                                      │
│                                                               │
│  2. System Normalizes Data                                   │
│     ├─ Extracts line items                                  │
│     ├─ Normalizes fields                                    │
│     └─ Saves to normalized_line_items.json                  │
│                                                               │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                   Production Workflow                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  3. Auto-Load on Initialize                                  │
│     ├─ Loads normalized_line_items.json                     │
│     ├─ Converts to ProfileDocument format                   │
│     └─ Adds to session state                                │
│                                                               │
│  4. Display as Documents                                     │
│     ├─ Shows in selected profile                            │
│     ├─ Displays with provider, amount, date                 │
│     └─ Includes full billing details                        │
│                                                               │
│  5. Available for Analysis                                   │
│     ├─ Unflagged → Ready to analyze                         │
│     ├─ Flagged → Requires review first                      │
│     └─ Can mark actions (ignore/followup/resolved)          │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Document Type Detection

Line items are automatically categorized:

| Procedure Code | Document Type | Example |
|----------------|---------------|---------|
| Starts with `D` | `dental_bill` | D0120 - Dental exam |
| Contains `RX` or `pharmacy` | `pharmacy_receipt` | RX-12345 |
| All others | `medical_bill` | 45378 - Colonoscopy |

### Smart Flagging Rules

Line items are automatically flagged if:

1. **High Patient Responsibility**: Patient owes > $500
2. **Unusual Split**: Patient owes more than insurance paid
3. **Manual Review Needed**: Complex billing scenarios

**Examples:**

```python
# Flagged (high patient responsibility)
{
    'patient_responsibility': 1200.00,  # > $500 threshold
    'flagged': True
}

# Flagged (patient pays more than insurance)
{
    'paid_by_insurance': 200.00,
    'patient_responsibility': 1200.00,  # More than insurance
    'flagged': True
}

# Not flagged (normal copay)
{
    'patient_responsibility': 45.00,    # < $500, normal
    'flagged': False
}
```

## Usage Examples

### Example 1: Import Insurance EOB

**In Profile Editor:**

1. Go to **Importer** section
2. Upload insurance EOB PDF
3. System extracts 5 line items
4. Click "Save" → Saves to `normalized_line_items.json`

**In Production Workflow:**

1. Switch to Production Workflow tab
2. Select appropriate profile
3. **Automatically see 5 new documents**:
   - DOC-IMPORT-001
   - DOC-IMPORT-002
   - DOC-IMPORT-003
   - DOC-IMPORT-004
   - DOC-IMPORT-005

4. Click "🔍 Analyze Documents" to process

### Example 2: Import Provider Bill

**In Profile Editor:**

1. Paste provider bill text
2. System extracts 3 line items:
   - Lab work: $250 (patient owes $50)
   - Office visit: $200 (patient owes $45)
   - Procedure: $1500 (patient owes $800) ← Flagged

3. Save import

**In Production Workflow:**

1. Click "📥 Reload Data" button
2. Success: "Added 3 new document(s)!"
3. Documents show:
   - 2 unflagged (ready to analyze)
   - 1 flagged (review first)

### Example 3: Mixed Documents

**Starting State:**
- 6 preloaded sample documents
- 10 receipts from Profile Editor
- 5 imported line items

**Production Workflow Shows:**
```
Total Documents: 21
├─ 6 Preloaded samples
├─ 10 Receipts (from uploads/pastes)
└─ 5 Imported line items (from importer)

Breakdown:
- 12 Pending (ready to analyze)
- 5 Flagged (need review)
- 4 Completed (already analyzed)
```

## Document Content Format

Each imported line item displays comprehensive billing information:

```
IMPORTED LINE ITEM - 45378

Service Date: 2026-01-12
Provider: Valley Medical Center
NPI: 1234567890
Claim #: CLM-2026-001

Procedure: 45378
Description: Colonoscopy, Diagnostic

AMOUNTS:
Billed Amount:           $2,500.00
Allowed Amount:          $1,400.00
Paid by Insurance:       $200.00
Patient Responsibility:  $1,200.00

⚠️ FLAGGED: High patient responsibility

Import Job ID: job_20260131_001
Line Item ID: item_001
```

## Reload Data Feature

### Button Location

```
⚙️ Advanced Options
├─ 📥 Reload Data     → Loads new receipts + imports
└─ 🔄 Reset All       → Full reset
```

### What Gets Reloaded

The **"📥 Reload Data"** button loads:

✅ **New Receipts**:
- From `data/receipts.json`
- Uploaded or pasted receipts

✅ **New Imported Line Items**:
- From `data/normalized_line_items.json`
- Insurance EOB line items
- Provider bill line items

✅ **Duplicate Prevention**:
- Checks existing document IDs
- Only adds new documents
- No duplicates created

### When to Use

**Click "Reload Data" when:**
1. You just imported new data in Profile Editor
2. You uploaded new receipts
3. You want to sync latest data
4. After deleting documents from Profile Editor

## Technical Implementation

### Data Flow

```python
# 1. Load from Profile Editor
from _modules.ui.profile_editor import load_line_items
line_items = load_line_items()

# 2. Convert to ProfileDocument
for item in line_items:
    doc = {
        'doc_id': f"DOC-IMPORT-{item['line_item_id']}",
        'provider': item['provider_name'],
        'amount': item['patient_responsibility'],
        'flagged': item['patient_responsibility'] > 500,
        ...
    }

# 3. Add to session state
st.session_state.prod_workflow_documents.extend(import_docs)
```

### Function: `load_imported_line_items_as_documents()`

**Purpose**: Convert normalized line items to ProfileDocument format

**Returns**: `List[ProfileDocument]`

**Key Features**:
- Handles `None`/missing values safely
- Auto-detects document type from procedure code
- Smart flagging based on patient responsibility
- Assigns to active profile from session state

**Error Handling**:
- Graceful fallback if importer not available
- Warning message if loading fails
- Returns empty list on error

### Session State Structure

```python
st.session_state.prod_workflow_documents = [
    # Preloaded samples
    {'doc_id': 'DOC-PH-001', 'source': 'preloaded', ...},
    
    # Receipts
    {'doc_id': 'DOC-RCPT-SAMPLE_1', 'source': 'receipt', ...},
    
    # Imported line items
    {'doc_id': 'DOC-IMPORT-001', 'source': 'import', ...},
    {'doc_id': 'DOC-IMPORT-002', 'source': 'import', ...},
]
```

## Integration Points

### Profile Editor → Production Workflow

| Profile Editor Module | Production Workflow |
|----------------------|---------------------|
| `load_line_items()` | `load_imported_line_items_as_documents()` |
| `normalized_line_items.json` | ProfileDocument list |
| Save import job | Auto-appears in Prod Workflow |
| Delete line item | Reload Data to sync |

### Data Files

```
data/
├─ receipts.json                  → Receipts
├─ normalized_line_items.json     → Imported line items ★
├─ import_jobs.json               → Import job metadata
└─ health_profiles.json           → Profile data
```

## Best Practices

### For Users

1. **Import First, Analyze Second**
   - Complete all imports in Profile Editor
   - Switch to Production Workflow
   - Documents automatically loaded

2. **Use Reload Data**
   - After adding new imports
   - To sync latest changes
   - Before starting analysis

3. **Review Flagged Items**
   - High charges flagged automatically
   - Review before analyzing
   - Unflag when verified correct

4. **Organize by Profile**
   - Assign imports to correct profile
   - Switch profiles to see relevant documents
   - Keep policyholder and dependent separate

### For Developers

1. **Handle Missing Fields**
   - All fields use `.get()` with defaults
   - Safe formatting with None checks
   - Graceful error handling

2. **Maintain Data Consistency**
   - Document IDs must be unique
   - Use consistent formats
   - Validate before saving

3. **Test Integration**
   - Test with missing fields
   - Test with various procedure codes
   - Test flagging logic

## Troubleshooting

### Imported Items Not Showing

**Problem**: Imported data in Profile Editor but not in Prod Workflow

**Check**:
1. Did you save the import in Profile Editor?
2. Are you viewing the correct profile?
3. Did you click "Reload Data"?

**Solution**:
1. Verify `normalized_line_items.json` exists
2. Click "📥 Reload Data" in Advanced Options
3. Or click "🔄 Reset All" for complete refresh

### Duplicate Documents

**Problem**: Same import appears multiple times

**Explanation**: Each reload adds new documents

**Solution**:
- Reload Data checks for duplicates by doc_id
- If duplicates exist, use "Reset All"
- Or delete from Profile Editor and reload

### Wrong Document Type

**Problem**: Dental procedure showing as medical bill

**Check**: Procedure code format

**Fix**:
- Dental codes should start with `D`
- Medical codes are numeric (99213, 45378)
- Pharmacy should include `RX` or `pharmacy`

### Not Flagged When Should Be

**Problem**: High charge not flagged

**Check Flagging Rules**:
- Patient responsibility > $500?
- Patient pays more than insurance?

**Current Thresholds**:
```python
flagged = patient_responsibility > 500
# OR
flagged = (paid_by_insurance > 0 and 
           patient_responsibility > paid_by_insurance)
```

## Future Enhancements

### Planned Features

1. **Import Job Grouping**
   - Group line items by import job
   - Analyze entire EOB at once
   - Track which import each doc came from

2. **Custom Flagging Rules**
   - User-defined thresholds
   - Provider-specific rules
   - Insurance plan-based flagging

3. **Claim Matching**
   - Match line items to receipts
   - Reconcile EOB vs provider bill
   - Identify discrepancies

4. **Edit Import Data**
   - Modify line item details
   - Correct provider names
   - Update amounts

5. **Export Integration**
   - Include import source in CSV exports
   - Separate reports for imports vs receipts
   - Claim-level summaries

## Related Documentation

- [Profile Editor Integration](PROFILE_EDITOR_INTEGRATION.md)
- [Receipt Integration](PROD_WORKFLOW_RECEIPTS.md)
- [Importer Guide](INGESTION_QUICKSTART.md)
- [Data Schema](../data/schema_examples.json)

---

**Last Updated**: January 31, 2026  
**Version**: 1.0  
**Status**: Production Ready
