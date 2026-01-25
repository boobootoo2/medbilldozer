# Profile Editor Integration Guide

This document explains how to integrate the Profile Editor into your Streamlit app.

## Quick Start

### 1. Enable the Feature

Set environment variables:

```bash
export PROFILE_EDITOR_ENABLED=true
export IMPORTER_ENABLED=true
```

Or add to your `.env` file:

```bash
PROFILE_EDITOR_ENABLED=true
IMPORTER_ENABLED=true
```

### 2. Integration in app.py

Add the following code to your `app.py`:

#### Import the Module

```python
from _modules.ui.profile_editor import (
    render_profile_editor,
    is_profile_editor_enabled
)
```

#### Add Navigation

In your sidebar or main navigation, add a "Profile" option:

```python
def main():
    """Main application function."""

    # ... existing code ...

    # Add profile navigation
    with st.sidebar:
        st.markdown("## Navigation")

        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = 'home'
            st.rerun()

        if is_profile_editor_enabled():
            if st.button("📋 Profile", use_container_width=True):
                st.session_state.current_page = 'profile'
                st.rerun()

    # Route to appropriate page
    current_page = st.session_state.get('current_page', 'home')

    if current_page == 'profile':
        render_profile_editor()
    else:
        # Your existing home page rendering
        render_home_page()
```

### 3. Alternative: Tab-Based Navigation

If you prefer tabs instead of sidebar navigation:

```python
def main():
    """Main application function."""

    tabs = ["🏠 Home", "� Analyze", "📋 Profile"] if is_profile_editor_enabled() else ["🏠 Home", "� Analyze"]

    tab_objects = st.tabs(tabs)

    with tab_objects[0]:
        render_home_page()

    with tab_objects[1]:
        render_analysis_page()

    if is_profile_editor_enabled() and len(tab_objects) > 2:
        with tab_objects[2]:
            render_profile_editor()
```

### 4. Alternative: Query Parameters

For URL-based navigation:

```python
def main():
    """Main application function."""

    # Get page from query params
    query_params = st.query_params
    page = query_params.get('page', ['home'])[0]

    if page == 'profile' and is_profile_editor_enabled():
        render_profile_editor()
    else:
        render_home_page()
```

## Features Overview

### Identity Management
- Full name, date of birth, contact information
- Mailing address
- Persistent storage with atomic writes

### Insurance Plan Management
- Multiple insurance plans
- Deductibles, OOP maximums, copays, coinsurance
- In-network/out-of-network tracking
- Effective and termination dates

### Provider Management
- Healthcare provider directory
- NPI and tax ID tracking
- Specialty and contact information
- In-network status

### Data Importer (Plaid-like Experience)

**4-Step Wizard:**

1. **Choose Source Type**
   - Insurance EOB (PDF, CSV, text)
   - Provider bills (PDF, CSV, text)
   - FHIR Connect (UI placeholder)

2. **Provide Data**
   - File upload
   - Text paste
   - CSV import

3. **Review & Edit**
   - Inline field editing
   - Data validation
   - Preview before save

4. **Complete**
   - Save normalized line items
   - Success confirmation
   - Import more or return to profile

## Data Storage

All data is stored as JSON files in the `./data/` directory:

```
data/
├── user_profile.json          # Single user profile
├── insurance_plans.json       # Array of insurance plans
├── providers.json             # Array of providers
├── import_jobs.json           # Array of import job records
├── normalized_line_items.json # Array of all imported line items
├── schema_examples.json       # Example JSON structures
└── uploads/                   # Uploaded PDF/CSV files
    └── 1737850000.678_eob_2024_q1.pdf
```

### Atomic Writes

All JSON writes use atomic file operations:
1. Write to temporary file
2. Atomic rename to final location
3. Prevents corruption from interrupted writes

## Accessing Profile Data in Your App

You can access the profile data from anywhere in your app:

```python
from _modules.ui.profile_editor import (
    load_profile,
    load_insurance_plans,
    load_providers,
    load_line_items
)

def my_analysis_function():
    # Get user profile
    profile = load_profile()
    if profile:
        user_name = profile.get('full_name')
        dob = profile.get('date_of_birth')

    # Get insurance plans
    plans = load_insurance_plans()
    for plan in plans:
        carrier = plan.get('carrier_name')
        deductible = plan.get('deductible', {}).get('individual', 0)

    # Get providers
    providers = load_providers()
    in_network_providers = [p for p in providers if p.get('in_network')]

    # Get imported line items
    line_items = load_line_items()
    total_patient_resp = sum(item.get('patient_responsibility', 0) for item in line_items)
```

## Customization

### Styling

The Profile Editor uses standard Streamlit components. To customize styling:

```python
# In your app's CSS injection
st.markdown("""
<style>
/* Profile Editor customization */
.stButton > button[data-testid*="profile"] {
    background-color: #667eea;
    color: white;
}
</style>
""", unsafe_allow_html=True)
```

### Adding Custom Fields

To add custom fields to the profile:

1. Update the `UserProfile` TypedDict in `profile_editor.py`
2. Add form fields in `render_identity_editor()`
3. Update save logic to include new fields

Example:

```python
# In UserProfile TypedDict
class UserProfile(TypedDict, total=False):
    # ... existing fields ...
    ssn_last_4: str  # Add custom field
    preferred_language: str

# In render_identity_editor()
ssn_last_4 = st.text_input(
    "Last 4 of SSN",
    value=profile.get('ssn_last_4', ''),
    max_chars=4,
    help="For insurance verification"
)
```

### Integration with Existing Analysis

To use profile data in your document analysis:

```python
def analyze_document_with_profile(document_text: str):
    # Load user context
    profile = load_profile()
    plans = load_insurance_plans()

    # Build context for analysis
    context = f"""
    Patient: {profile.get('full_name', 'Unknown')}
    Insurance: {plans[0].get('carrier_name', 'None')} if plans else 'No insurance'
    Deductible: ${plans[0].get('deductible', {}).get('individual', 0):,.2f}
    """

    # Pass context to your analysis agent
    result = your_analysis_agent.analyze(document_text, context)
    return result
```

## Environment Variables

| Variable | Values | Description |
|----------|--------|-------------|
| `PROFILE_EDITOR_ENABLED` | `true`/`false`, `1`/`0`, `yes`/`no`, `on`/`off` | Enable/disable profile editor |
| `IMPORTER_ENABLED` | `true`/`false`, `1`/`0`, `yes`/`no`, `on`/`off` | Enable/disable data importer |

## Accessibility Features

The Profile Editor includes:

- ✅ Clear heading hierarchy (h1, h2, h3)
- ✅ Form labels for all inputs
- ✅ Help text and placeholders
- ✅ Keyboard navigation (native Streamlit)
- ✅ ARIA labels where appropriate
- ✅ No color-only cues (icons + text)
- ✅ High contrast UI elements

## Production Considerations

### Security

1. **File Permissions**: Ensure `./data/` directory has appropriate permissions
2. **Data Encryption**: Consider encrypting sensitive data at rest
3. **Access Control**: Add authentication before profile access
4. **Input Validation**: Validate all user inputs (already included)

### Performance

1. **File Size**: JSON files load entirely into memory. For large datasets (>10,000 line items), consider a database.
2. **Atomic Writes**: Current implementation is safe for concurrent reads, but not concurrent writes.
3. **Caching**: Add `@st.cache_data` for load functions if needed.

### Scaling

For production deployment:

```python
# Replace JSON storage with database
import sqlite3

def load_profile():
    conn = sqlite3.connect('medbilldozer.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,))
    return cursor.fetchone()
```

## Testing

Example test cases:

```python
def test_profile_save_load():
    profile = {
        'full_name': 'Test User',
        'date_of_birth': '1990-01-01'
    }
    save_profile(profile)
    loaded = load_profile()
    assert loaded['full_name'] == 'Test User'

def test_import_wizard():
    # Mock CSV import
    st.session_state.import_source_type = 'insurance_csv'
    st.session_state.import_data = {
        'rows': [{'Date of Service': '2024-01-01', ...}]
    }
    extract_and_normalize_data()
    assert len(st.session_state.pending_line_items) > 0
```

## Troubleshooting

### "Profile Editor is not enabled"
- Set `PROFILE_EDITOR_ENABLED=true` environment variable
- Restart Streamlit app

### "Data directory not found"
- Ensure `./data/` directory exists and is writable
- Check file permissions

### "Import wizard stuck on step 2"
- Verify file format (CSV must have correct columns)
- Check that text paste has >50 characters
- Review browser console for JavaScript errors

### "Atomic write failed"
- Check disk space
- Verify write permissions on `./data/` directory
- Ensure no other process is locking the files

## Support

For issues or questions:
1. Check this documentation
2. Review `schema_examples.json` for data format
3. Check Streamlit logs for error messages
4. File an issue in the repository

