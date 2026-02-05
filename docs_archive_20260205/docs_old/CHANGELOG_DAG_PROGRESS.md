# DAG Progress Visualization Enhancement

## Summary
Enhanced the document analysis workflow to show real-time progress visualization with step highlighting during analysis execution.

## Changes Made

### 1. UI Module: `_modules/ui/ui_pipeline_dag.py`
- **Added `_build_initial_plan_html()`**: Shows analysis plan outline before execution starts
- **Updated `create_pipeline_dag_container()`**: Displays initial plan with all 4 steps in pending state
- **Added `_build_progress_html()`**: Renders progressive status with visual indicators:
  - 🔄 Blue - Currently executing step
  - ✅ Green - Completed step
  - ⏳ Gray - Pending step
- **Updated `update_pipeline_dag()`**: Accepts optional `step_status` parameter for real-time updates

### 2. Core Orchestrator: `_modules/core/orchestrator_agent.py`
- **Updated `run()` method signature**: Added optional `progress_callback` parameter
- **Added progress callbacks at 5 key points**:
  1. **Pre-extraction start**: Document classification and feature detection
  2. **Extraction start**: Fact extraction with selected extractor
  3. **Line items start**: Phase-2 parsing based on document type
  4. **Analysis start**: Issue detection with selected analyzer
  5. **Complete**: Final workflow completion

### 3. Main App: `app.py`
- **Moved DAG container creation**: Now happens before `agent.run()` to show initial plan
- **Added progress callback**: Updates DAG in real-time as each step executes
- **Removed duplicate DAG update**: Progressive updates replace single final update

## Workflow Steps Visualized

1. **Pre-Extraction**
   - Document classification and feature detection
   - Shows detected document type when complete

2. **Fact Extraction**
   - Extract key medical/financial information
   - Shows fact count when complete

3. **Line Item Parsing**
   - Parse detailed line items based on document type
   - Shows parsed item count when complete

4. **Issue Analysis**
   - Detect potential billing issues and anomalies
   - Shows issue count when complete

## Technical Details

### Callback Pattern
```python
def progress_callback(workflow_log, step_status):
    # step_status values:
    # - 'pre_extraction_active'
    # - 'extraction_active'
    # - 'line_items_active'
    # - 'analysis_active'
    # - 'complete'
    if dag_placeholder and is_dag_enabled():
        update_pipeline_dag(placeholder, workflow_log, step_status=step_status)
```

### Visual States
- **Pending**: ⏳ Gray border, white background
- **Active**: 🔄 Blue border, light blue background
- **Complete**: ✅ Green border, light green background

## Testing
- All 171 existing tests pass
- No breaking changes to existing functionality
- Backward compatible (progress_callback is optional)

## User Experience Improvements

### Before
- DAG appeared only after analysis completed
- No visibility into what was happening during analysis
- Single static view of final results

### After
- Analysis plan shown immediately when "Analyze" is clicked
- Real-time step highlighting shows current execution phase
- Visual feedback with icons and colors
- Success indicators show completed steps with result counts
- Smooth progressive disclosure of workflow state

## Configuration
Progress visualization respects existing `is_dag_enabled()` feature flag.

