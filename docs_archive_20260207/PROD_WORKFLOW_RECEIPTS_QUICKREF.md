# Production Workflow - Receipt Integration Quick Reference

## Quick Start

### Adding Receipts to Production Workflow

1. **Upload in Profile Editor**:
   ```
   Profile Editor → Upload Receipt → Fill Details → Save
   ```

2. **View in Production Workflow**:
   ```
   Production Workflow → Select Profile → Receipts Appear Automatically
   ```

3. **Reload New Receipts**:
   ```
   Advanced Options → 📥 Reload Receipts
   ```

## Key Features

| Feature | Description | Button/Action |
|---------|-------------|---------------|
| **Auto-Load** | Receipts load automatically on first open | Automatic |
| **Reload** | Add new receipts without restart | "📥 Reload Receipts" |
| **Profile Assignment** | Receipts assigned to selected profile | Radio button selection |
| **Smart Analysis** | Only unflagged docs are analyzed | "🔍 Analyze X Documents" |

## Receipt → Document Mapping

```
Receipt (Profile Editor)         ProfileDocument (Prod Workflow)
─────────────────────────────    ────────────────────────────────
receipt_id: "rcpt_sample_1"   →  doc_id: "DOC-RCPT-SAMPLE_1"
provider: "CVS Pharmacy"      →  provider: "CVS Pharmacy"
amount: 125.00                →  amount: 125.00
status: "pending_review"      →  flagged: True, status: "pending"
status: "reconciled"          →  flagged: False, status: "completed"
file_name: "dental_bill.pdf"  →  doc_type: "dental_bill"
```

## Document Type Auto-Detection

| Filename Contains | Document Type |
|------------------|---------------|
| `dental` | `dental_bill` |
| `medical`, `hospital` | `medical_bill` |
| (default) | `pharmacy_receipt` |

## Analyze Button States

### ✅ Enabled (Can Analyze)
```
🔍 Analyze 3 Pending Document(s)
```
- Has unflagged pending documents
- Button is enabled (not disabled)
- Click to analyze

### ⚠️ Disabled (Flagged Only)
```
🔍 Analyze Documents [DISABLED]
"X flagged documents require manual review"
```
- Only flagged documents remain
- Review flagged items first
- Unflag to analyze

### ✅ Disabled (All Done)
```
🔍 Analyze Documents [DISABLED]
"All documents have been analyzed"
```
- All documents completed
- Nothing to analyze

## Common Workflows

### Workflow 1: Fresh Start with Receipts

```
1. Profile Editor → Upload 3 receipts
2. Production Workflow → Auto-loads 6 preloaded + 3 receipts
3. Select profile → See 9 total documents
4. Click Analyze → Process unflagged docs
```

### Workflow 2: Adding More Receipts

```
1. Production Workflow open → Currently 6 docs
2. Profile Editor → Upload 2 new receipts
3. Production Workflow → Click "Reload Receipts"
4. Success → "Added 2 new receipts!" → Now 8 docs
```

### Workflow 3: Mixed Analysis

```
Before:
  Total: 6 docs (3 flagged, 3 pending)
  
Action:
  Click "Analyze 3 Documents"
  
After:
  Total: 6 docs (3 flagged, 3 completed)
  Note: Flagged docs skipped
```

## Session State Keys

| Key | Value | Purpose |
|-----|-------|---------|
| `prod_workflow_documents` | `List[ProfileDocument]` | All documents |
| `selected_profile_id` | `"PH-001"` or `"DEP-001"` | Active profile |
| `selected_profile_name` | `"John Sample"` | Profile name |

## Functions Quick Reference

### `load_receipts_as_documents()`
**Purpose**: Load receipts from Profile Editor  
**Returns**: `List[ProfileDocument]`  
**When**: On initialization

### `reload_receipts_into_session()`
**Purpose**: Add new receipts to session  
**Returns**: `int` (count of new receipts)  
**When**: User clicks "Reload Receipts"

### `initialize_prod_workflow_state()`
**Purpose**: Setup session state  
**Returns**: `None`  
**When**: First render

## Advanced Options Panel

```
⚙️ Advanced Options
├─ 📥 Reload Receipts  → Add new receipts from Profile Editor
└─ 🔄 Reset All        → Clear session, restart with defaults
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Receipts not showing | Click "Reload Receipts" |
| Duplicates appearing | Use "Reset All" |
| Can't analyze | Check if only flagged docs remain |
| Wrong profile | Select correct profile radio button |

## Receipt Status Examples

### Example 1: Flagged Receipt
```json
{
  "receipt_id": "rcpt_001",
  "status": "pending_review",
  "amount": 125.00
}
```
**Result**: Flagged, excluded from auto-analysis

### Example 2: Reconciled Receipt
```json
{
  "receipt_id": "rcpt_002",
  "status": "reconciled",
  "amount": 15.00
}
```
**Result**: Not flagged, marked completed

## Profile Assignment

```
Session State:
  selected_profile_id = "PH-001"
  selected_profile_name = "John Sample"

New Receipt:
  receipt_id: "rcpt_new"
  
Becomes:
  doc_id: "DOC-RCPT-NEW"
  profile_id: "PH-001"
  profile_name: "John Sample"
```

## Export Integration

Follow-up tasks export includes receipt documents:

```csv
Document ID,Provider,Amount,Action,Notes,Flagged
DOC-RCPT-001,CVS Pharmacy,125.00,followup,"Check coverage",Yes
```

## Best Practices

✅ **DO**:
- Upload receipts in Profile Editor first
- Use "Reload Receipts" after adding new ones
- Review flagged documents before analysis
- Select appropriate profile

❌ **DON'T**:
- Manually edit session state
- Assume receipts auto-reload (use button)
- Analyze without reviewing flagged items
- Mix profiles without switching

## Code Example

### Adding Custom Receipt Processing

```python
# Load receipts
receipts = load_receipts()

# Filter for specific profile
profile_receipts = [
    r for r in receipts 
    if r.get('profile_id') == 'PH-001'
]

# Convert to documents
docs = load_receipts_as_documents()

# Process
for doc in docs:
    if doc['flagged']:
        # Review logic
        pass
    else:
        # Auto-process
        pass
```

## Related Docs

- [Full Receipt Integration Guide](PROD_WORKFLOW_RECEIPTS.md)
- [Two-Tab Workflow](TWO_TAB_WORKFLOW.md)
- [Action Management](ACTION_MANAGEMENT.md)

---

**Version**: 1.0  
**Last Updated**: January 31, 2026
