# HTML Stripping in DAG Visualization

## Issue
When analyzing documents, the DAG diagrams were showing raw HTML markup instead of plain text for fields like document type, extractor reason, and analyzer mode.

## Root Cause
The workflow log contains data extracted from HTML documents (bills, EOBs, receipts). When this data was displayed in the DAG visualization, HTML tags and entities were being rendered as-is instead of being stripped and converted to plain text.

## Solution
Added comprehensive HTML stripping to all text displayed in DAG visualizations:

### Changes Made

#### 1. `_build_dag_html()` function
- Added `strip_html()` helper function that:
  - Removes all HTML tags using regex `<[^>]+>`
  - Decodes HTML entities (`&nbsp;`, `&amp;`, etc.) using `html.unescape()`
  - Normalizes whitespace
  - Escapes the cleaned text for safe HTML display using `html.escape()`

- Applied HTML stripping to:
  - `doc_type` - Document type classification
  - `extractor` - Selected extractor name
  - `extractor_reason` - Reason for extractor selection
  - `analyzer` - Selected analyzer name
  - `analysis_mode` - Analysis mode (facts+text or text_only)

#### 2. `_build_progress_html()` function
- Added same `strip_html()` helper function
- Applied HTML stripping to `doc_type` displayed during progressive analysis

#### 3. `_render_detailed_logs()` function
- Already had HTML stripping implemented
- No changes needed

## Examples

### Before
```
Document Type: <div>pharmacy_receipt</div>
Extractor Reason: <p>regex classification</p>
```

### After
```
Document Type: pharmacy_receipt
Extractor Reason: regex classification
```

## Technical Details

### HTML Stripping Function
```python
def strip_html(text):
    """Strip HTML tags and decode entities, then escape for safe display."""
    if not isinstance(text, str):
        return text
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities (&nbsp;, &amp;, etc.)
    text = unescape(text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Escape for safe HTML display
    return escape(text)
```

### Why Double Processing?
1. **First pass (unescape)**: Convert HTML entities to actual characters
2. **Strip tags**: Remove all HTML markup
3. **Second pass (escape)**: Re-escape for safe display in our HTML output

This ensures that if the source document contained literal HTML code, it displays as text instead of rendering as HTML.

## Testing
- All 171 tests pass
- No breaking changes
- Backward compatible

## User Experience
- Clean, readable text in all DAG visualizations
- No more confusing HTML markup during analysis
- Professional appearance of progress indicators

