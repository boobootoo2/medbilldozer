# Production Workflow - Receipt Integration

## Overview

The Production Workflow now integrates receipts uploaded via the Profile Editor, allowing all documents (preloaded samples + uploaded receipts) to appear together in the selected health profile.

## Key Features

### 1. Receipt Integration
- **Automatic Loading**: Receipts from the Profile Editor are automatically loaded when the Production Workflow is initialized
- **Profile Assignment**: Receipts are assigned to the currently selected profile (Policy Holder or Dependent)
- **Type Detection**: Receipt document type is automatically determined based on file name:
  - Contains "dental" → `dental_bill`
  - Contains "medical" or "hospital" → `medical_bill`
  - Default → `pharmacy_receipt`

### 2. Dynamic Receipt Reload
- **Reload Button**: Added "📥 Reload Receipts" button in Advanced Options
- **Incremental Loading**: Only new receipts (not already in session) are added
- **Live Updates**: Receipts uploaded in Profile Editor can be instantly integrated

### 3. Analyze Button Enhancement
- **Always Enabled for Unflagged**: Button is explicitly enabled (not disabled) when unflagged pending documents exist
- **Clear State Indication**: Button shows count of documents to analyze
- **Smart Filtering**: Flagged documents are automatically excluded from analysis

## How It Works

### Receipt Conversion

When receipts are loaded from the Profile Editor, they are converted to `ProfileDocument` format:

```python
ProfileDocument = {
    'doc_id': 'DOC-RCPT-{receipt_id}',  # Unique ID from receipt
    'profile_id': 'PH-001',  # Active profile (PH-001 or DEP-001)
    'profile_name': 'John Sample',  # Profile holder name
    'doc_type': 'pharmacy_receipt',  # Auto-detected
    'provider': 'Provider Name',  # From receipt
    'service_date': '2026-01-20',  # From receipt
    'amount': 125.00,  # From receipt
    'flagged': True/False,  # True if status is 'pending_review'
    'status': 'pending',  # 'pending' or 'completed'
    'content': '...',  # Formatted receipt text
    'action': None,  # Can be marked as ignored/followup/resolved
    'action_notes': '',
    'action_date': None
}
```

### Receipt Status Mapping

Profile Editor receipt statuses map to Production Workflow states:

| Profile Editor Status | Flagged? | Analysis Status |
|----------------------|----------|-----------------|
| `pending_review`     | ✅ Yes   | `pending`       |
| `review`             | ✅ Yes   | `pending`       |
| `reconciled`         | ❌ No    | `completed`     |

### Workflow Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                      Production Workflow                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Initialize Session State                                    │
│     ├─ Load PRELOADED_DOCUMENTS (sample data)                  │
│     └─ Load receipts from Profile Editor                       │
│                                                                  │
│  2. User Selects Profile (PH-001 or DEP-001)                   │
│     └─ Store profile ID/name in session state                  │
│                                                                  │
│  3. Display Documents for Selected Profile                      │
│     ├─ Filter by profile_id                                    │
│     ├─ Show metrics (total, flagged, pending)                  │
│     └─ Render document cards                                   │
│                                                                  │
│  4. User Clicks "Reload Receipts"                              │
│     ├─ Call load_receipts() from Profile Editor               │
│     ├─ Convert receipts to ProfileDocument format             │
│     ├─ Add only new receipts (check doc_id)                   │
│     └─ Refresh UI                                              │
│                                                                  │
│  5. User Clicks "Analyze"                                       │
│     ├─ Filter: pending + not flagged                          │
│     ├─ Process each document                                   │
│     └─ Update status to 'completed'                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Usage Examples

### Example 1: Adding a New Receipt

1. **Upload Receipt in Profile Editor**:
   - Go to Profile Editor tab
   - Upload a pharmacy receipt (e.g., "CVS_Prescription.pdf")
   - Set provider, amount, date
   - Status: "pending_review"

2. **Switch to Production Workflow**:
   - Receipt automatically appears in selected profile
   - Flagged for review (since status was "pending_review")
   - Not included in automatic analysis

3. **Review and Analyze**:
   - Review flagged receipt
   - Unflag if appropriate
   - Click "Analyze" to process

### Example 2: Reloading New Receipts

1. **Production Workflow is Open**:
   - Currently viewing Policy Holder profile
   - Has 6 documents (3 preloaded + 3 receipts)

2. **User Uploads More Receipts in Profile Editor**:
   - Add 2 new dental bills
   - Return to Production Workflow tab

3. **Reload Receipts**:
   - Click "⚙️ Advanced Options"
   - Click "📥 Reload Receipts"
   - Success: "Added 2 new receipt(s)!"
   - Documents now show 8 total

### Example 3: Analyze with Mixed Documents

**Before Analysis**:
```
Profile: John Sample (Policy Holder)
Total Documents: 6
├─ 3 Preloaded (2 flagged, 1 pending)
└─ 3 Receipts (1 flagged, 2 pending)

Unflagged Pending: 3 documents
```

**Click "Analyze"**:
- Button text: "🔍 Analyze 3 Pending Document(s)"
- Processes: 1 preloaded + 2 receipts
- Skips: 3 flagged documents

**After Analysis**:
```
Profile: John Sample (Policy Holder)
Total Documents: 6
├─ 3 Analyzed ✅
└─ 3 Flagged (require manual review) 🚩
```

## Technical Implementation

### Key Functions

#### `load_receipts_as_documents()`
Loads receipts from Profile Editor and converts to `ProfileDocument` format.

**Returns**: `List[ProfileDocument]`

**Features**:
- Handles missing Profile Editor module gracefully
- Uses active profile from session state
- Auto-detects document type from filename
- Maps receipt status to flagged/status fields

#### `reload_receipts_into_session()`
Reloads receipts and adds only new ones to session state.

**Returns**: `int` (count of new receipts added)

**Features**:
- Checks existing document IDs
- Prevents duplicates
- Incremental loading

#### `initialize_prod_workflow_state()`
Initializes session state with preloaded documents + receipts.

**Features**:
- Deep copies PRELOADED_DOCUMENTS
- Loads receipts on first run
- Persists across reruns

### Session State Structure

```python
st.session_state = {
    'prod_workflow_documents': [
        # Preloaded sample documents
        {'doc_id': 'DOC-PH-001', ...},
        {'doc_id': 'DOC-PH-002', ...},
        # Receipt documents
        {'doc_id': 'DOC-RCPT-SAMPLE_1', ...},
        {'doc_id': 'DOC-RCPT-SAMPLE_2', ...},
    ],
    'selected_profile_id': 'PH-001',  # Current profile
    'selected_profile_name': 'John Sample',  # Profile name
    'prod_analyzing': False,  # Analysis in progress
}
```

## UI Components

### Advanced Options Panel

```
⚙️ Advanced Options
┌────────────────────────────────────────────────────────┐
│ Reset all documents to initial state or reload         │
│ receipts from profile editor                           │
│                                                         │
│ [📥 Reload Receipts] [🔄 Reset All]                   │
└────────────────────────────────────────────────────────┘
```

### Analyze Button States

1. **Enabled State** (unflagged pending documents exist):
   ```
   [🔍 Analyze 3 Pending Document(s)]  ← PRIMARY (blue)
   disabled=False
   ```

2. **Disabled State** (only flagged documents):
   ```
   [🔍 Analyze Documents]  ← SECONDARY (gray)
   disabled=True
   help="2 flagged documents require manual review"
   ```

3. **Disabled State** (all analyzed):
   ```
   [🔍 Analyze Documents]  ← SECONDARY (gray)
   disabled=True
   help="All documents have been analyzed"
   ```

## Error Handling

### Receipt Loading Failures

```python
try:
    receipts = load_receipts()
except ImportError:
    # Profile Editor module not available
    return []
except Exception as e:
    st.warning(f"Could not load receipts: {e}")
    return []
```

### Missing Receipt Fields

- Missing `provider` → "Unknown Provider"
- Missing `date` → Current date
- Missing `amount` → 0.0
- Missing `raw_content` → Empty string

## Best Practices

### For Users

1. **Upload Receipts in Profile Editor First**:
   - Use Profile Editor to upload/paste receipts
   - Set provider, amount, date accurately
   - Mark status appropriately

2. **Select Appropriate Profile**:
   - Receipts are assigned to active profile
   - Switch profiles to see different documents

3. **Reload After Adding Receipts**:
   - Use "Reload Receipts" button
   - Checks for new receipts only
   - Instant integration

4. **Review Flagged Items Before Analysis**:
   - Flagged receipts need manual review
   - Unflag when ready to analyze
   - Or mark action as "ignored"

### For Developers

1. **Maintain Type Safety**:
   - Use `ProfileDocument` TypedDict
   - Validate all required fields
   - Handle optional fields gracefully

2. **Session State Management**:
   - Deep copy data to prevent mutations
   - Check existence before access
   - Clear state on reset

3. **Error Handling**:
   - Wrap external calls in try/except
   - Provide user-friendly error messages
   - Fail gracefully with empty lists

## Troubleshooting

### Receipts Not Appearing

**Problem**: Uploaded receipts don't show in Production Workflow

**Solutions**:
1. Click "📥 Reload Receipts" button
2. Check that receipts exist in Profile Editor
3. Verify correct profile is selected
4. Reset workflow and reinitialize

### Duplicate Receipts

**Problem**: Same receipt appears multiple times

**Solutions**:
- `reload_receipts_into_session()` checks `doc_id`
- Only adds new receipts
- If duplicates exist, use "🔄 Reset All"

### Analyze Button Disabled

**Problem**: Can't analyze documents

**Check**:
1. Are there unflagged pending documents?
2. Have all documents been analyzed already?
3. Are only flagged documents remaining?

**Solution**:
- Unflag documents that need analysis
- Or review flagged items manually

## Future Enhancements

### Planned Features

1. **Profile-Specific Receipt Assignment**:
   - Allow assigning receipts to specific profiles
   - Multi-profile receipt management

2. **Bulk Receipt Import**:
   - Upload multiple receipts at once
   - Auto-assignment based on rules

3. **Receipt Reconciliation**:
   - Match receipts to EOBs/bills
   - Track duplicate charges
   - Calculate savings opportunities

4. **Export Integration**:
   - Include receipts in CSV exports
   - Generate combined reports
   - Share with insurance/providers

## Related Documentation

- [Two-Tab Workflow](TWO_TAB_WORKFLOW.md) - Overall architecture
- [Action Management](ACTION_MANAGEMENT.md) - Document action system
- [Session Persistence](PROD_WORKFLOW_PERSISTENCE.md) - State management
- [Profile Editor](PROFILE_EDITOR_QUICKSTART.md) - Receipt upload interface

---

**Last Updated**: January 31, 2026  
**Version**: 1.0  
**Status**: Production Ready
