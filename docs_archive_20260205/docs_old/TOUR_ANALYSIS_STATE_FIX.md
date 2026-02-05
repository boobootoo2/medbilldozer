# Tour Analysis State Preservation Fix

**Date**: January 31, 2026  
**Issue**: Tour navigation clears analysis results and pending analysis  
**Status**: ✅ Fixed (Final v3 - Interrupted Analysis Restart)

## Problem Description

When a user:
1. Clicks "Analyze" to start document analysis
2. Then clicks "Next" on the guided tour (either during or after analysis)

The analysis results would be cleared and any pending analysis would be lost.

### Root Cause

When tour navigation buttons (Next/Back) call `st.rerun()`:
1. The entire page re-renders
2. `documents = render_document_inputs()` re-executes
3. If the text input widgets are empty or in a different state, `documents` becomes empty
4. This clears the analysis state and results

## Solution (Final v3)

Three-part solution to fully preserve analysis across tour navigation:

### Part 1: Save Documents Early
Store documents in `last_documents` **immediately** when analysis begins (not just at end)

### Part 2: Preserve Documents During Tour
When tour is active, use cached documents instead of widget input if ANY of these is true:
- `doc_results=True` (analysis completed)
- `analyzing=True` (analysis in progress)
- `pending_analysis=True` (analysis queued)

### Part 3: **Restart Interrupted Analysis** ⭐ NEW
Treat `analyzing=True` on rerun as a signal to restart analysis:
```python
should_analyze = (analyze_clicked OR 
                  pending_analysis OR 
                  analyzing)  # ← Restart if interrupted
```

**Why this matters**: When tour calls `st.rerun()` during analysis, the spinner code is **abandoned mid-execution**. The `analyzing` flag stays `True`, but no analysis is running. By checking this flag, we automatically restart the analysis on the next render.

### Code Changes

**File**: `app.py`

**Change 1: Enhanced Document Preservation Check**

**Before**:
```python
render_contextual_help('input')
documents = render_document_inputs()
```

**After**:
```python
render_contextual_help('input')

# Preserve documents during tour navigation to prevent clearing analysis state
# This includes: completed analysis (doc_results), ongoing analysis (analyzing), 
# and pending analysis (pending_analysis)
if (st.session_state.get('tour_active', False) and 
    st.session_state.get('last_documents') and 
    (st.session_state.get('doc_results', False) or 
     st.session_state.get('analyzing', False) or 
     st.session_state.get('pending_analysis', False))):
    # During active tour with results/analysis, preserve the documents
    documents = st.session_state.last_documents
    # Still render the inputs for display, but don't use their output
    render_document_inputs()
else:
    # Normal flow: get documents from input widgets
    documents = render_document_inputs()
```

**Change 2: Save Documents at Analysis Start**

**Before**:
```python
# Clear pending flag and proceed with analysis
st.session_state.pending_analysis = False
st.session_state.analyzing = True

# Wrap entire analysis in a spinner
with st.spinner("Analyzing your documents..."):
    # ... analysis code ...
    
    # Save analysis state for potential rerun (ONLY at end)
    st.session_state.last_documents = documents
```

**After**:
```python
# Clear pending flag and proceed with analysis
st.session_state.pending_analysis = False
st.session_state.analyzing = True

# Save documents at start of analysis so they persist during tour navigation
st.session_state.last_documents = documents

# Wrap entire analysis in a spinner
with st.spinner("Analyzing your documents..."):
    # ... analysis code ...
    
    # Update saved documents with analysis results at end
    st.session_state.last_documents = documents
```

**Change 3: Restart Interrupted Analysis** ⭐ NEW

**Before**:
```python
# Check if we should proceed with analysis
should_analyze = analyze_clicked or st.session_state.get('pending_analysis', False)

if should_analyze:
    # ...
```

**After**:
```python
# Check if we should proceed with analysis (including interrupted analysis)
# If analyzing flag is still True, analysis was interrupted by rerun and should restart
should_analyze = (analyze_clicked or 
                 st.session_state.get('pending_analysis', False) or
                 st.session_state.get('analyzing', False))

if should_analyze:
    # ...
```

## Testing

### Test Scenario 1: Analysis During Tour
1. Start guided tour
2. Add a document in text area
3. Click "Analyze"
4. Wait for results to appear
5. Click "Next" on tour
6. **Expected**: Results remain visible, analysis state preserved
7. **Before Fix**: Results would disappear

### Test Scenario 2: Multiple Tour Steps With Results
1. Complete analysis
2. Click "Next" multiple times on tour
3. **Expected**: Results persist through all tour steps
4. **Before Fix**: Results would clear on first "Next" click

### Test Scenario 3: Normal Use Without Tour
1. Add documents
2. Click "Analyze"
3. **Expected**: Normal analysis flow unchanged
4. **Actual**: No changes to normal behavior

## Session State Variables Used

| Variable | Purpose |
|----------|---------|
| `tour_active` | Whether guided tour is currently running |
| `last_documents` | Cached documents from last analysis |
| `doc_results` | Flag indicating analysis results exist |
| `analyzing` | Flag indicating analysis in progress |
| `last_total_savings` | Cached total savings amount |
| `last_per_doc_savings` | Cached per-document savings |

## Benefits

1. **User Experience**: Tour navigation doesn't interrupt workflow
2. **Data Preservation**: Analysis results persist during tour
3. **No Breaking Changes**: Normal app flow unchanged
4. **Clean Separation**: Tour logic separate from analysis logic

## Edge Cases Handled

### Case 1: Tour Active, No Results Yet
- Condition: `tour_active=True`, `doc_results=False`
- Behavior: Normal document input flow
- Result: Can still analyze new documents

### Case 2: Tour Inactive, Has Cached Results
- Condition: `tour_active=False`, `last_documents` exists
- Behavior: Normal document input flow
- Result: Can add new documents, cached results displayed separately

### Case 3: Tour Active, Has Results, User Adds New Document
- Condition: `tour_active=True`, `doc_results=True`, user types in widget
- Behavior: Widget input ignored, cached documents used
- Result: Prevents accidental clearing during tour

## Future Enhancements

### Option 1: Smarter State Preservation
Could extend to preserve other states:
- Provider selection
- Debug mode settings
- Sidebar state

### Option 2: Tour Step Awareness
Could make preservation conditional on specific tour steps:
```python
if (tour_active and 
    tour_step in ['analysis_running', 'review_issues', 'next_actions'] and
    has_results):
    use_cached_documents()
```

### Option 3: Explicit Tour Mode
Add a "tour_mode" flag that changes app behavior:
```python
if st.session_state.get('tour_mode'):
    # Lock all inputs, use cached data
    documents = st.session_state.last_documents
    st.text_area(..., disabled=True)  # Read-only during tour
```

## Related Issues

- Tour implementation: `docs/SESSION_DRIVEN_TOUR.md`
- Session state management: `docs/CHANGELOG_SESSION_TOUR.md`
- Analysis workflow: `docs/PROD_WORKFLOW_RECEIPTS.md`

## Verification

To verify the fix is working:
1. Enable tour: `GUIDED_TOUR=TRUE`
2. Start app
3. Complete splash and privacy screens
4. Follow test scenarios above
5. Verify results persist during tour navigation

---

**Status**: ✅ Complete  
**Tested**: Pending user verification  
**Breaking Changes**: None
