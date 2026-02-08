# Production Workflow - Session State Persistence

## Overview

The Production Workflow now uses Streamlit session state to persist document states across tab switches and reruns. This ensures that:

1. **Document states persist** when switching between Demo POC and Demo Prod Workflow tabs
2. **Analyzed documents remain analyzed** and are not re-processed
3. **Flagged documents are excluded** from automatic analysis
4. **Action changes are saved** and persist across page interactions

## Key Features

### 1. Session State Storage

All documents are stored in `st.session_state.prod_workflow_documents` on first load:

```python
# Initial load creates a deep copy of PRELOADED_DOCUMENTS
st.session_state.prod_workflow_documents = copy.deepcopy(PRELOADED_DOCUMENTS)
```

### 2. Persistent Document States

Each document maintains its state across interactions:

- **Status**: `pending` → `analyzing` → `completed`
- **Actions**: `ignored`, `followup`, `resolved`
- **Flags**: Documents marked as flagged remain flagged
- **Notes**: Action notes persist with documents

### 3. Intelligent Analysis Behavior

#### Excluded from Analysis:
- ✅ **Already completed documents** - Won't be re-analyzed
- ✅ **Flagged documents** - Require manual review first
- ✅ **Documents with errors** - Must be reviewed before retry

#### Included in Analysis:
- ⏳ **Pending unflagged documents** only

### 4. Tab Switching Persistence

When switching between tabs:

```
Demo POC Tab → Demo Prod Workflow Tab
     ↓                    ↓
  No impact          State preserved
                     (all docs retain status)
```

Navigate away and come back:
- Document statuses remain unchanged
- Actions and notes are preserved
- Analysis progress persists

## Usage Examples

### Example 1: Partial Analysis

**Initial State:**
- 6 total documents
- 3 flagged (DOC-PH-001, DOC-PH-002, DOC-DEP-001)
- 3 unflagged (DOC-PH-003, DOC-DEP-002, DOC-DEP-003)

**After First Analyze:**
- Button shows: "🔍 Analyze 3 Pending Document(s)"
- Processes: DOC-PH-003, DOC-DEP-002, DOC-DEP-003
- Skips: DOC-PH-001, DOC-PH-002, DOC-DEP-001 (flagged)
- Result: "✅ Successfully analyzed 3 document(s)! (3 flagged documents skipped)"

**After Tab Switch:**
- Switch to Demo POC, then back to Demo Prod Workflow
- Status preserved: 3 completed, 3 still pending (flagged)
- No re-analysis of completed documents

### Example 2: Action Persistence

**Set Follow-up Action:**
1. Open DOC-PH-001
2. Select "🔔 Follow-up Required"
3. Click "💾 Save Action"
4. Add notes: "Called provider on 1/31"
5. Click "💾 Save Notes"

**Switch Tabs:**
- Go to Demo POC
- Do some work there
- Return to Demo Prod Workflow

**Result:**
- DOC-PH-001 still shows Follow-up action
- Notes are intact
- Appears in Follow-up Tasks table

### Example 3: Reset for Demo

**Before Demo Presentation:**
1. Documents in various states (some completed, some actioned)
2. Click "⚙️ Advanced Options" expander
3. Click "🔄 Reset All" button
4. All documents return to initial state (pending, no actions)

**Use Case:**
- Clean slate for demonstrations
- Testing workflows from beginning
- Resetting after experiments

## Technical Implementation

### Session State Functions

#### `initialize_prod_workflow_state()`
Called on first render to create session state copy:
```python
if 'prod_workflow_documents' not in st.session_state:
    import copy
    st.session_state.prod_workflow_documents = copy.deepcopy(PRELOADED_DOCUMENTS)
```

#### `get_session_documents()`
Returns documents from session state:
```python
initialize_prod_workflow_state()
return st.session_state.prod_workflow_documents
```

#### `update_session_document(doc_id, updates)`
Updates specific document in session state:
```python
docs = get_session_documents()
for doc in docs:
    if doc['doc_id'] == doc_id:
        doc.update(updates)
        break
```

### Document Retrieval Functions

All retrieval functions now use session state:

- `get_documents_for_profile(profile_id)` → session state
- `get_flagged_documents(profile_id)` → session state
- `get_pending_documents(profile_id)` → session state
- `get_actioned_documents(profile_id)` → session state

### Analysis Logic

```python
# Filter out flagged and completed documents
pending_unflagged_docs = [d for d in pending_docs if not d['flagged']]

# Update status in session state during analysis
for doc in pending_unflagged_docs:
    update_session_document(doc['doc_id'], {'status': 'analyzing'})
    # ... simulate analysis ...
    update_session_document(doc['doc_id'], {'status': 'completed'})
```

## State Lifecycle

### 1. Initial Load
```
User opens Demo Prod Workflow
        ↓
initialize_prod_workflow_state() called
        ↓
PRELOADED_DOCUMENTS copied to session state
        ↓
Documents displayed with status: pending
```

### 2. User Interactions
```
User clicks Analyze
        ↓
pending_unflagged_docs filtered
        ↓
For each doc: status → analyzing → completed
        ↓
Session state updated via update_session_document()
        ↓
Page rerun shows new status
```

### 3. Tab Switching
```
User switches to Demo POC
        ↓
Session state remains in memory
        ↓
User switches back to Demo Prod Workflow
        ↓
initialize_prod_workflow_state() checks existing state
        ↓
Documents displayed with preserved status
```

### 4. Action Management
```
User sets action on DOC-PH-001
        ↓
doc['action'] = 'followup' (direct modification)
        ↓
doc['action_date'] = current timestamp
        ↓
Page rerun preserves changes (already in session state)
```

## Benefits

### For Users
1. **No Lost Work**: Actions and analysis persist across tabs
2. **Efficient Workflow**: Don't re-analyze completed documents
3. **Clear Status**: Always know what's been processed
4. **Safe Exploration**: Switch tabs without losing progress

### For Development
1. **Scalable**: Easy to add new document properties
2. **Testable**: Reset button for demos and testing
3. **Maintainable**: Centralized state management
4. **Extensible**: Can add database persistence later

## Future Enhancements

### Planned Features
- [ ] **Database Persistence**: Save to SQLite/PostgreSQL for true persistence
- [ ] **Multi-Session Sync**: Share state across browser tabs
- [ ] **Undo/Redo**: Revert document state changes
- [ ] **Export State**: Download session state as JSON
- [ ] **Import State**: Restore previous session
- [ ] **Auto-Save**: Periodic backup to local storage
- [ ] **State History**: Track all state changes with timestamps

### Technical Improvements
- [ ] **Optimistic Updates**: Faster UI with deferred persistence
- [ ] **Conflict Resolution**: Handle concurrent edits
- [ ] **State Validation**: Ensure data integrity
- [ ] **Performance**: Lazy loading for large document sets
- [ ] **Caching**: Memoize expensive computations

## Troubleshooting

### Documents Not Persisting
**Symptom**: Document states reset after tab switch

**Solution**: 
- Check `st.session_state.prod_workflow_documents` exists
- Verify `initialize_prod_workflow_state()` is called
- Ensure not using `PRELOADED_DOCUMENTS` directly

### Analyze Button Shows Wrong Count
**Symptom**: Button says "Analyze 6 documents" but only 3 are pending

**Solution**:
- Check filter: `pending_unflagged_docs = [d for d in pending_docs if not d['flagged']]`
- Verify flagged documents are excluded
- Check document status in session state

### Reset Not Working
**Symptom**: Reset button doesn't clear document states

**Solution**:
```python
if 'prod_workflow_documents' in st.session_state:
    del st.session_state.prod_workflow_documents
st.rerun()
```

### Actions Not Saving
**Symptom**: Action changes disappear after rerun

**Cause**: Direct modification of session state works due to reference semantics

**Verification**: Check that action buttons trigger `st.rerun()`

## API Reference

### Functions

#### `initialize_prod_workflow_state()`
Initialize session state with document copies.

**Returns**: None  
**Side Effects**: Creates `st.session_state.prod_workflow_documents`

#### `get_session_documents() -> List[ProfileDocument]`
Get all documents from session state.

**Returns**: List of ProfileDocument dicts  
**Note**: Initializes state if not exists

#### `update_session_document(doc_id: str, updates: Dict)`
Update specific document fields in session state.

**Args**:
- `doc_id`: Document ID to update
- `updates`: Dict of field names and new values

**Example**:
```python
update_session_document('DOC-PH-001', {
    'status': 'completed',
    'action': 'followup'
})
```

## Related Documentation

- [Two-Tab Workflow](TWO_TAB_WORKFLOW.md) - Overall architecture
- [Action Management](ACTION_MANAGEMENT.md) - Action tracking system
- [Quick Start](TWO_TAB_QUICKSTART.md) - Getting started guide

---

**Last Updated**: January 31, 2026
