# Re-analyze Feature - Production Workflow

## Overview

The Production Workflow supports running analysis multiple times with a **single Analyze button** that automatically handles both new pending documents and re-analysis of completed documents.

## The Problem (Before)

Previously, once documents were analyzed:
- Status changed from `pending` → `completed`
- Analyze button became disabled
- Only way to re-run was "Reset All" (loses all data)

## The Solution (Now)

The **"� Analyze Documents"** button now:
- Works for both `pending` AND `completed` documents
- Automatically resets completed docs to pending before re-analyzing
- Preserves all document data (actions, notes, flags)
- Smart button text shows what will be analyzed
- No separate re-analyze button needed!

## How It Works

### Smart Analyze Button

The single analyze button shows different text based on document states:

| Document State | Button Text | Action |
|----------------|-------------|--------|
| Has pending docs | "🔍 Analyze X Document(s)" | Analyzes pending |
| Has completed docs | "🔍 Re-analyze X Document(s)" | Resets & analyzes |
| Has both | "🔍 Analyze X + Re-analyze Y Document(s)" | Handles both |
| Only flagged docs | "🔍 Analyze Documents" [disabled] | Requires review |

### Advanced Options Panel

```
⚙️ Advanced Options
┌──────────────────────────────────────────────────────┐
│ Reset all documents to initial state or reload       │
│ receipts from profile editor                         │
│                                                       │
│ [📥 Reload Receipts]              [🔄 Reset All]     │
└──────────────────────────────────────────────────────┘
```

## Usage Workflow

### Scenario 1: Re-run Analysis on Same Documents

```
1. Initial State:
   - 6 documents (all pending)

2. Click "🔍 Analyze 6 Documents"
   - Status: 6 completed
   - Button text changes to "🔍 Re-analyze 6 Documents"

3. Click "🔍 Re-analyze 6 Documents"
   - Automatically resets to pending
   - Analysis runs again
   - Status: 6 completed

4. Can repeat step 3 infinitely!
```

### Scenario 2: Selective Re-analysis

```
1. After first analysis:
   - 4 completed, 2 flagged

2. Review flagged documents
   - Unflag 1 document
   - Leave 1 flagged

3. Click "🔍 Analyze 1 Document"
   - Analyzes the newly unflagged doc
   - Status: 5 completed, 1 flagged

4. Want to re-run all completed?
   - Click "🔍 Re-analyze 5 Documents"
   - Automatically resets 5 completed → pending
   - Analyzes all 5 unflagged docs
   - Skips 1 flagged doc
```

### Scenario 3: Incremental Analysis

```
1. Start with 3 documents
   - Click "🔍 Analyze 3 Documents" → 3 completed

2. Add 2 new receipts
   - Click "Reload Receipts"
   - Status: 3 completed, 2 pending

3. Button shows "🔍 Analyze 2 + Re-analyze 3 Documents"
   - Clicking analyzes ALL 5 documents
   - Automatically resets the 3 completed to pending
   - Analyzes all 5 together
   - Status: 5 completed
```

## Technical Implementation

### State Changes

**Before Analyze (Completed Doc):**
```python
{
    'doc_id': 'DOC-PH-001',
    'status': 'completed',  # ← Previously analyzed
    'flagged': False,
    'action': 'followup',
    'action_notes': 'Check with provider'
}
```

**During Analyze (Auto-Reset):**
```python
{
    'doc_id': 'DOC-PH-001',
    'status': 'pending',    # ← Auto-reset to pending
    'flagged': False,       # ← Preserved
    'action': 'followup',   # ← Preserved
    'action_notes': 'Check with provider'  # ← Preserved
}
```

**After Analysis:**
```python
{
    'doc_id': 'DOC-PH-001',
    'status': 'completed',  # ← Analyzed again
    'flagged': False,       # ← Still preserved
    'action': 'followup',   # ← Still preserved
    'action_notes': 'Check with provider'  # ← Still preserved
}
```

### Code Logic

```python
# Get all analyzable documents (pending OR completed, but not flagged)
analyzable_docs = [
    d for d in profile_docs 
    if not d['flagged'] and d['status'] in ['pending', 'completed']
]

# When analyze button clicked
if analyze_clicked and analyzable_docs:
    # Auto-reset completed docs to pending
    for doc in completed_unflagged_docs:
        update_session_document(doc['doc_id'], {'status': 'pending'})
    
    # Now analyze all docs
    for doc in analyzable_docs:
        # ... analysis logic ...
        update_session_document(doc['doc_id'], {'status': 'completed'})
```

### What Gets Preserved

✅ **Preserved During Re-analyze:**
- Document content
- Provider, amount, dates
- Flagged status
- Action (ignored/followup/resolved)
- Action notes
- Action date

❌ **Reset During Re-analyze:**
- Analysis status (`completed` → `pending`)

## Button Help Text Updates

### Analyze Button (Disabled State)

**Before:**
```
"All documents have been analyzed"
```

**After:**
```
"All documents analyzed. Use 'Re-analyze All' in Advanced Options to run again."
```

### Success Message

**Before:**
```
✅ All documents have been analyzed!
```

**After:**
```
✅ All documents have been analyzed! Use '🔄 Re-analyze All' in Advanced Options to run analysis again.
```

## Comparison: Re-analyze vs Reset

| Feature | Re-analyze All | Reset All |
|---------|----------------|-----------|
| **Status** | `completed` → `pending` | Delete everything |
| **Actions** | ✅ Preserved | ❌ Lost |
| **Notes** | ✅ Preserved | ❌ Lost |
| **Flags** | ✅ Preserved | ❌ Lost |
| **Receipts** | ✅ Preserved | ❌ Lost |
| **Use Case** | Re-run analysis | Start fresh |

## Error Handling

### No Completed Documents

```python
disabled=len(completed_docs) == 0
```

Button is disabled when:
- All documents are pending
- All documents are flagged
- No documents exist

### Button Label

Always shows: **"🔄 Re-analyze All"**
- Enabled: Documents ready to reset
- Disabled (grayed): No completed documents

## Advanced Use Cases

### Testing Analysis Workflow

```python
# Developer testing
1. Load demo documents
2. Click "Analyze" → test analysis logic
3. Click "Re-analyze All" → reset
4. Modify code
5. Click "Analyze" → test again
# No need to restart app or lose data!
```

### Training Demonstrations

```python
# Training scenario
1. Show initial analysis
2. Demonstrate flagging
3. Re-analyze to show difference
4. Repeat multiple times
# Preserves narrative flow
```

### Iterative Development

```python
# Improving analysis
1. Run analysis v1
2. Review results
3. Mark actions
4. Re-analyze with v2
5. Compare outcomes
# Actions/notes track evolution
```

## Future Enhancements

### Potential Features

1. **Selective Re-analyze**
   - Checkbox per document
   - Re-analyze only selected docs

2. **Analysis History**
   - Track each analysis run
   - Compare results over time
   - Audit trail

3. **Conditional Re-analyze**
   - Re-analyze only if data changed
   - Skip unchanged documents
   - Smart incremental analysis

4. **Analysis Versioning**
   - Save analysis snapshots
   - Rollback to previous analysis
   - A/B testing different logic

## Best Practices

### When to Use Re-analyze

✅ **Good Use Cases:**
- Testing workflow changes
- Demonstrating to users
- Iterating on analysis logic
- Comparing different runs
- Training scenarios

❌ **Avoid:**
- To fix bugs (use Reset All instead)
- When data is corrupted
- After major code changes (full reset safer)

### Workflow Tips

1. **Mark Actions Before Re-analyzing**
   - Actions persist through re-analysis
   - Use to track findings

2. **Unflag Before Re-analyzing**
   - Flagged docs won't be re-analyzed
   - Review and unflag first

3. **Use Reset for Clean Slate**
   - Major changes? Reset All
   - Minor tweaks? Re-analyze

## Troubleshooting

### Re-analyze Button Disabled

**Problem**: Can't click "Re-analyze All"

**Check**:
- Are any documents `completed`?
- Or are all still `pending`?

**Solution**: Run analysis first, then re-analyze

### Documents Not Re-analyzing

**Problem**: Clicked re-analyze but documents don't analyze

**Check**:
- Are documents flagged?
- Did you click "Analyze" after "Re-analyze All"?

**Solution**: 
1. Click "Re-analyze All" (resets status)
2. Then click "Analyze" (runs analysis)

### Lost Data

**Problem**: Actions/notes disappeared

**Check**: Did you use "Reset All" instead of "Re-analyze All"?

**Solution**: Use "Re-analyze All" to preserve data

## Related Features

- **Reload Receipts**: Add new documents without reset
- **Reset All**: Complete fresh start
- **Refresh**: Reload UI state

## Documentation

- [Production Workflow Receipts](PROD_WORKFLOW_RECEIPTS.md)
- [Session Persistence](PROD_WORKFLOW_PERSISTENCE.md)
- [Action Management](ACTION_MANAGEMENT.md)

---

**Version**: 1.0  
**Last Updated**: January 31, 2026  
**Status**: Production Ready
