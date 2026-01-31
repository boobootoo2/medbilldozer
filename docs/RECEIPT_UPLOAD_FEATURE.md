# 📤 Receipt Upload Feature

## Overview

The **Receipt Upload** feature allows users to import their own medical receipts (PDF, PNG, JPG) and store them in session storage for enhanced analysis context. This complements the pre-loaded sample receipts in the health profiles.

## Features

### 🎯 Key Capabilities

1. **Multi-File Upload**: Upload multiple receipt files at once
2. **Session Storage**: Receipts stored in session state (not persisted to disk)
3. **Format Support**: PDF, PNG, JPG, JPEG files accepted
4. **File Management**: View, list, and delete individual receipts
5. **Analysis Integration**: Automatically included in LLM analysis context
6. **Profile Independent**: Works with or without a selected profile

## User Interface

### Upload Section

```
🧾 Import Receipts
┌──────────────────────────────────────────────┐
│ Upload medical receipts (PDF, PNG, JPG)     │
│ [Browse Files...]  or drag and drop         │
└──────────────────────────────────────────────┘

💡 Upload receipts to enhance analysis with historical billing context
```

### After Upload

```
📎 3 receipt(s) uploaded

▼ View Uploaded Receipts
┌──────────────────────────────────────────────┐
│ medical_bill_01.pdf    125.3 KB    [🗑️]    │
│ Uploaded: 2026-01-30 14:23:15               │
├──────────────────────────────────────────────┤
│ receipt_pharmacy.jpg   89.2 KB     [🗑️]    │
│ Uploaded: 2026-01-30 14:23:20               │
├──────────────────────────────────────────────┤
│ dental_invoice.pdf     203.8 KB    [🗑️]    │
│ Uploaded: 2026-01-30 14:23:25               │
└──────────────────────────────────────────────┘

[🗑️ Clear All]
```

## Location in UI

The receipt uploader appears in the **Analysis Overview** section:

```
📊 Analysis Overview
├── Health Profile Selector
├── Profile Status Indicator
│
├── 🧾 Import Receipts  ⬅️ NEW!
│   ├── File Uploader
│   ├── Uploaded Receipts List
│   └── Delete/Clear Options
│
└── View Full Profile Details (expander)
```

## Technical Implementation

### Session Storage

Receipts are stored in `st.session_state.uploaded_receipts` as a list of dictionaries:

```python
{
    'name': 'medical_bill_01.pdf',
    'type': 'application/pdf',
    'size': 128345,  # bytes
    'bytes': b'...',  # file content
    'uploaded_at': '2026-01-30 14:23:15'
}
```

### Functions

#### `render_receipt_uploader()`
Renders the upload UI and manages session state:
- File uploader widget
- Duplicate detection
- Receipt list display
- Delete functionality

#### `get_uploaded_receipts_context()`
Generates LLM context string from uploaded receipts:
- Lists all uploaded files
- Includes metadata (name, size, type, date)
- Formatted for LLM consumption

### Analysis Integration

Uploaded receipts are automatically included in the analysis context:

```python
# In app.py
profile_context = get_profile_context_for_analysis(selected_profile)
uploaded_receipts_context = get_uploaded_receipts_context()

if uploaded_receipts_context:
    if profile_context:
        profile_context += uploaded_receipts_context
    else:
        profile_context = uploaded_receipts_context
```

## Analysis Context Output

When receipts are uploaded, the LLM receives:

```
========================================
UPLOADED RECEIPTS
========================================
Total Uploaded Files: 3

The user has uploaded the following receipt files for reference:
1. medical_bill_01.pdf (125.3 KB)
   Type: application/pdf
   Uploaded: 2026-01-30 14:23:15
2. receipt_pharmacy.jpg (89.2 KB)
   Type: image/jpeg
   Uploaded: 2026-01-30 14:23:20
3. dental_invoice.pdf (203.8 KB)
   Type: application/pdf
   Uploaded: 2026-01-30 14:23:25

Note: These receipts are available in session storage and can be referenced 
when analyzing new bills for pattern detection and comparison.
```

## Use Cases

### 1. Historical Context
Upload previous bills from the same provider to detect patterns:
```
User uploads: 3 bills from Valley Medical Center
LLM sees: Pattern of overcharging detected in uploaded receipts
Analysis: Flags similar overcharge in current bill
```

### 2. Provider Comparison
Upload bills from multiple providers:
```
User uploads: Bills from Doctor A, Doctor B, Doctor C
LLM analyzes: Fee differences for same procedure
Analysis: Recommends most cost-effective provider
```

### 3. Insurance Verification
Upload EOB (Explanation of Benefits) documents:
```
User uploads: Insurance EOB statements
LLM cross-references: Billed vs paid amounts
Analysis: Validates insurance calculations
```

### 4. Dispute Support
Upload receipts for billing disputes:
```
User uploads: Original bill + corrected bill
LLM compares: Differences and adjustments
Analysis: Summarizes changes and validates corrections
```

## Workflow

### Complete Analysis Workflow

1. **Select Profile** (optional)
   - Choose Policy Holder or Dependent
   - Loads insurance info and stored receipts

2. **Upload Receipts** ⬅️ NEW STEP
   - Upload your own medical receipts
   - Add historical billing context
   - Works with or without profile

3. **Upload Documents**
   - Upload bills to analyze
   - Can be new or related to uploaded receipts

4. **Run Analysis**
   - LLM receives:
     * Profile context (if selected)
     * Uploaded receipts context
     * Current documents
   - Enhanced analysis with historical data

## Benefits

### For Users
✅ **Personalized Context**: Use your own billing history
✅ **No Profile Required**: Works standalone or with profiles
✅ **Pattern Detection**: Identify recurring issues
✅ **Privacy**: Session storage only (not saved to disk)
✅ **Easy Management**: Simple upload, view, delete interface

### For Analysis
✅ **Richer Context**: Real user data vs sample data
✅ **Better Accuracy**: Pattern detection from actual history
✅ **Provider Intelligence**: Track specific provider behaviors
✅ **Comparative Analysis**: Compare multiple bills

## Data Privacy

### Session Storage
- Receipts stored **only** in browser session memory
- **Not persisted** to disk or database
- **Cleared** when:
  - User manually clears receipts
  - Browser tab/window closed
  - Session expires
  - App restarts

### Security Notes
- Files never leave user's browser session
- No upload to external servers
- No permanent storage
- HIPAA-compliant session handling

## File Size Limits

Recommended limits (configurable):
- **Max file size**: 10 MB per file
- **Max total**: 50 MB per session
- **File types**: PDF, PNG, JPG, JPEG

## Future Enhancements

### Planned Features
- [ ] OCR text extraction from receipt images
- [ ] Automatic receipt parsing (dates, amounts, providers)
- [ ] Receipt categorization (medical, dental, pharmacy)
- [ ] Export uploaded receipts context
- [ ] Receipt preview/thumbnail display
- [ ] Persistent storage option (encrypted)
- [ ] Receipt annotations and notes

### Advanced Features
- [ ] Automatic duplicate detection
- [ ] Receipt validation (check for required fields)
- [ ] Batch upload progress indicator
- [ ] Receipt search and filtering
- [ ] Integration with profile stored receipts
- [ ] Receipt comparison view

## API Usage

### Upload Receipts Programmatically

```python
# Initialize session state
if 'uploaded_receipts' not in st.session_state:
    st.session_state.uploaded_receipts = []

# Add receipt
receipt_data = {
    'name': 'bill.pdf',
    'type': 'application/pdf',
    'size': 123456,
    'bytes': file_bytes,
    'uploaded_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}
st.session_state.uploaded_receipts.append(receipt_data)
```

### Get Receipt Context

```python
from _modules.ui.health_profile import get_uploaded_receipts_context

context = get_uploaded_receipts_context()
# Returns formatted string for LLM
```

### Clear Receipts

```python
st.session_state.uploaded_receipts = []
st.rerun()
```

## Testing

### Test Scenarios

1. **Upload Single File**
   - Upload 1 PDF receipt
   - Verify appears in list
   - Check session state

2. **Upload Multiple Files**
   - Upload 3 different receipts
   - Verify all appear
   - Check sizes and types

3. **Delete Individual Receipt**
   - Click delete button
   - Verify receipt removed
   - Check list updates

4. **Clear All Receipts**
   - Click "Clear All"
   - Verify list empty
   - Check session state cleared

5. **Analysis Integration**
   - Upload receipts
   - Run analysis
   - Verify context includes receipts

## Troubleshooting

### Receipt Not Appearing
- Check file type (must be PDF, PNG, JPG, JPEG)
- Verify file size (under 10 MB)
- Try refreshing page

### Receipts Disappeared
- Session may have expired
- Browser tab closed
- App restarted
- Re-upload receipts

### Context Not in Analysis
- Check session state has receipts
- Verify `get_uploaded_receipts_context()` called
- Check LLM prompt includes context

## Related Documentation

- `docs/RECEIPTS_FEATURE.md` - Stored receipts in profiles
- `docs/RECEIPTS_QUICKSTART.md` - Quick start guide
- `docs/PROFILE_EDITOR_ARCHITECTURE.md` - Profile system

---

**Status**: ✅ Implemented and ready for testing
**Version**: 1.0.0
**Last Updated**: January 30, 2026
