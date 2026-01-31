# Security: Input Sanitization & XSS Prevention

## Overview

All user-provided input is sanitized before rendering to prevent Cross-Site Scripting (XSS) attacks and other injection vulnerabilities. This document describes the sanitization system and best practices.

## Table of Contents

- [Threat Model](#threat-model)
- [Sanitization Module](#sanitization-module)
- [Protected Areas](#protected-areas)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)
- [Testing](#testing)

## Threat Model

### Attack Vectors

1. **JavaScript Injection**: Malicious `<script>` tags in user input
2. **HTML Injection**: Harmful HTML tags (`<iframe>`, `<embed>`, `<object>`)
3. **Event Handler Injection**: `onclick`, `onload`, `onerror` attributes
4. **Data URI Schemes**: `data:text/html`, `javascript:` URLs
5. **Path Traversal**: `../../etc/passwd` in filenames
6. **Script Execution**: VBScript, meta refresh attacks

### Protected Data Types

- File uploads (PDF, images, text)
- Pasted text content
- Receipt data (provider names, notes, raw content)
- Imported line items (descriptions, provider names)
- User profile data (names, addresses)
- Document metadata (filenames, notes)

## Sanitization Module

**Location**: `_modules/utils/sanitize.py`

### Core Functions

#### `sanitize_text(text, allow_newlines=True)`

General purpose text sanitization.

```python
from _modules.utils.sanitize import sanitize_text

# Basic usage
safe_name = sanitize_text(user_input)

# Display in UI
st.write(f"Provider: {safe_name}")
```

**What it does:**
- Removes `<script>` tags and JavaScript
- Escapes HTML entities (`<`, `>`, `&`, etc.)
- Removes event handlers (`onclick`, etc.)
- Optionally preserves newlines

**Example:**
```python
sanitize_text("<script>alert('xss')</script>Hello")
# Returns: "Hello"

sanitize_text("Normal text with <b>tags</b>")
# Returns: "Normal text with &lt;b&gt;tags&lt;/b&gt;"
```

#### `sanitize_html_content(content, max_length=None)`

Aggressive sanitization for HTML/code display.

```python
from _modules.utils.sanitize import sanitize_html_content

# Sanitize pasted content
pasted_text = st.text_area("Paste receipt text")
safe_content = sanitize_html_content(pasted_text, max_length=500)
```

**What it does:**
- Removes ALL HTML tags
- Marks removed scripts as `[REMOVED]`
- Escapes all HTML entities
- Optional truncation

**Use for:**
- Raw receipt text
- Pasted document content
- User-provided HTML/code
- File content preview

#### `sanitize_filename(filename)`

Prevent path traversal and filename injection.

```python
from _modules.utils.sanitize import sanitize_filename

safe_name = sanitize_filename(uploaded_file.name)
```

**What it does:**
- Removes `../` path traversal
- Converts `/` and `\` to `_`
- Removes dangerous characters: `<>:"|?*`
- Limits length to 255 characters

**Example:**
```python
sanitize_filename("../../etc/passwd")
# Returns: "passwd"

sanitize_filename("file<script>.txt")
# Returns: "file.txt"
```

#### `sanitize_provider_name(name)`

Specialized sanitization for provider/user names.

```python
from _modules.utils.sanitize import sanitize_provider_name

provider = sanitize_provider_name(receipt.get('provider'))
st.write(f"Provider: {provider}")
```

**What it does:**
- Returns "N/A" for None/empty
- Removes scripts and HTML
- Limits to 200 characters
- Escapes HTML entities

#### `sanitize_amount(amount)`

Validate and sanitize monetary values.

```python
from _modules.utils.sanitize import sanitize_amount

amount = sanitize_amount(user_input)
st.write(f"Total: ${amount:.2f}")
```

**What it does:**
- Converts to float
- Handles None → 0.0
- Strips currency symbols ($, commas)
- Returns 0.0 for invalid input

**Example:**
```python
sanitize_amount("$1,234.56")  # Returns: 1234.56
sanitize_amount(None)          # Returns: 0.0
sanitize_amount("invalid")     # Returns: 0.0
```

#### `sanitize_date(date)`

Sanitize date strings.

```python
from _modules.utils.sanitize import sanitize_date

safe_date = sanitize_date(receipt.get('date'))
```

**What it does:**
- Returns "N/A" for None/empty
- Removes scripts/HTML
- Limits to 50 characters
- Escapes HTML entities

#### `sanitize_dict(data, keys_to_sanitize=None)`

Recursively sanitize dictionary values.

```python
from _modules.utils.sanitize import sanitize_dict

# Sanitize all string values
safe_data = sanitize_dict(user_data)

# Sanitize specific keys
safe_data = sanitize_dict(user_data, keys_to_sanitize=['notes', 'description'])
```

**Use for:**
- JSON imports
- API responses
- Bulk data sanitization

## Protected Areas

### 1. Profile Editor (`profile_editor.py`)

#### Receipt Upload

**Before:**
```python
new_receipt = {
    'raw_content': pasted_text,
    'provider': paste_provider,
    'file_name': uploaded_file.name
}
```

**After:**
```python
new_receipt = {
    'raw_content': sanitize_html_content(pasted_text, max_length=10000),
    'provider': sanitize_provider_name(paste_provider),
    'file_name': sanitize_filename(uploaded_file.name)
}
```

#### Receipt Display

**Before:**
```python
st.write(f"Provider: {receipt['provider']}")
st.text(receipt['raw_content'][:500])
```

**After:**
```python
safe_provider = sanitize_provider_name(receipt['provider'])
st.write(f"Provider: {safe_provider}")

safe_content = sanitize_html_content(receipt['raw_content'], max_length=500)
st.text(safe_content)
```

#### Import Text Paste

**Before:**
```python
st.session_state.import_data = {
    'raw_text': pasted_text
}
```

**After:**
```python
sanitized_text = sanitize_html_content(pasted_text, max_length=50000)
st.session_state.import_data = {
    'raw_text': sanitized_text
}
```

### 2. Production Workflow (`prod_workflow.py`)

#### Receipt Loading

**Before:**
```python
provider = receipt.get('provider') or 'Unknown'
file_name = receipt.get('file_name') or 'Unknown'
raw_content = receipt.get('raw_content') or ''
```

**After:**
```python
provider = sanitize_provider_name(receipt.get('provider') or 'Unknown')
file_name = sanitize_filename(receipt.get('file_name') or 'Unknown')
raw_content = sanitize_html_content(receipt.get('raw_content') or '', max_length=500)
```

#### Imported Line Items

**Before:**
```python
provider_name = item.get('provider_name') or 'Unknown'
procedure_desc = item.get('procedure_description') or 'No description'
```

**After:**
```python
provider_name = sanitize_provider_name(item.get('provider_name') or 'Unknown')
procedure_desc = sanitize_text(item.get('procedure_description') or 'No description')
```

### 3. Document Content Fields

All `content` fields in ProfileDocument now contain sanitized data:

```python
receipt_doc: ProfileDocument = {
    'content': f"""RECEIPT - {file_name}

Source: {source_method}
Provider: {provider}
Amount: ${float(amount_value):.2f}
Date: {date_value}

Notes: {notes_value}

--- RAW CONTENT ---
{raw_content}..."""
}
```

All variables are sanitized before inclusion in the content string.

## Usage Examples

### Example 1: Safe File Upload Display

```python
from _modules.utils.sanitize import sanitize_filename, sanitize_html_content

uploaded_file = st.file_uploader("Upload receipt")
if uploaded_file:
    # Sanitize filename
    safe_name = sanitize_filename(uploaded_file.name)
    st.write(f"File: {safe_name}")
    
    # Read and sanitize content
    content = uploaded_file.read().decode('utf-8')
    safe_content = sanitize_html_content(content, max_length=1000)
    st.text(safe_content)
```

### Example 2: Safe Text Input Display

```python
from _modules.utils.sanitize import sanitize_text

user_notes = st.text_area("Enter notes")
if user_notes:
    # Sanitize before storing
    safe_notes = sanitize_text(user_notes)
    
    # Store sanitized version
    receipt['notes'] = safe_notes
    
    # Safe to display
    st.write(f"Notes: {safe_notes}")
```

### Example 3: Safe Dictionary Processing

```python
from _modules.utils.sanitize import sanitize_dict

# User imports data
imported_data = load_user_json()

# Sanitize all strings in dictionary
safe_data = sanitize_dict(imported_data)

# Safe to use
for item in safe_data:
    st.write(f"{item['name']}: {item['description']}")
```

### Example 4: Safe Markdown Rendering

```python
from _modules.utils.sanitize import sanitize_text

user_title = get_user_input()
safe_title = sanitize_text(user_title)

# Safe in markdown (no HTML tags will execute)
st.markdown(f"### {safe_title}")
```

## Best Practices

### DO ✅

1. **Sanitize at Input**: Sanitize immediately when receiving user input

```python
pasted_text = st.text_area("Paste content")
if pasted_text:
    # Sanitize immediately
    safe_text = sanitize_html_content(pasted_text)
    save_to_database(safe_text)
```

2. **Sanitize Before Display**: Always sanitize before rendering

```python
# Load from database
receipt = load_receipt()

# Sanitize before display
safe_name = sanitize_filename(receipt['file_name'])
st.write(f"File: {safe_name}")
```

3. **Use Appropriate Function**: Match sanitization to data type

```python
# For names
safe_name = sanitize_provider_name(name)

# For amounts
safe_amount = sanitize_amount(amount)

# For filenames
safe_filename = sanitize_filename(filename)

# For HTML content
safe_content = sanitize_html_content(content)
```

4. **Sanitize in Loops**: Don't forget repeated data

```python
for receipt in receipts:
    safe_provider = sanitize_provider_name(receipt['provider'])
    safe_filename = sanitize_filename(receipt['file_name'])
    st.write(f"{safe_filename} from {safe_provider}")
```

5. **Log Original Data**: Keep original for debugging

```python
# Log original (secure context only)
logger.debug(f"Original input: {original_text}")

# Sanitize for display
safe_text = sanitize_text(original_text)
st.write(safe_text)
```

### DON'T ❌

1. **Don't Trust User Input**

```python
# BAD - displays raw user input
st.write(f"Name: {user_input}")

# GOOD - sanitizes first
safe_input = sanitize_text(user_input)
st.write(f"Name: {safe_input}")
```

2. **Don't Use `unsafe_allow_html=True` with User Data**

```python
# BAD - allows HTML execution
st.markdown(f"<div>{user_input}</div>", unsafe_allow_html=True)

# GOOD - sanitize first
safe_input = sanitize_text(user_input)
st.markdown(f"<div>{safe_input}</div>", unsafe_allow_html=True)
```

3. **Don't Skip Sanitization for "Trusted" Sources**

```python
# BAD - assumes import is safe
provider = imported_data['provider']

# GOOD - sanitize all external data
provider = sanitize_provider_name(imported_data['provider'])
```

4. **Don't Sanitize Multiple Times**

```python
# BAD - double sanitization can cause issues
text = sanitize_text(sanitize_text(user_input))

# GOOD - sanitize once
text = sanitize_text(user_input)
```

5. **Don't Forget Nested Data**

```python
# BAD - only sanitizes top level
safe_data = {
    'name': sanitize_text(data['name']),
    'items': data['items']  # NOT sanitized!
}

# GOOD - use sanitize_dict for nested structures
safe_data = sanitize_dict(data)
```

## Testing

### Manual Testing

Test with known malicious inputs:

```python
# Test script injection
test_input = "<script>alert('XSS')</script>Hello"
result = sanitize_text(test_input)
assert "<script>" not in result
assert "Hello" in result

# Test event handler
test_input = "<img src=x onerror='alert(1)'>"
result = sanitize_text(test_input)
assert "onerror" not in result

# Test path traversal
test_input = "../../etc/passwd"
result = sanitize_filename(test_input)
assert ".." not in result
```

### Common Test Cases

1. **Script Tags**: `<script>alert('xss')</script>`
2. **Event Handlers**: `<img onerror="alert(1)" src=x>`
3. **JavaScript URLs**: `<a href="javascript:alert(1)">Click</a>`
4. **Data URIs**: `data:text/html,<script>alert(1)</script>`
5. **Iframe Injection**: `<iframe src="evil.com"></iframe>`
6. **Path Traversal**: `../../etc/passwd`
7. **Special Characters**: `<>&"'`

### Integration Testing

Test with actual UI workflows:

1. Upload receipt with malicious filename
2. Paste text containing `<script>` tags
3. Import data with HTML in descriptions
4. Enter provider names with special characters
5. Save notes with JavaScript code

## Maintenance

### Adding New Input Fields

When adding new user input fields:

1. Identify data type (text, filename, amount, date, etc.)
2. Choose appropriate sanitization function
3. Apply sanitization at input AND display
4. Test with malicious inputs
5. Document the protection

### Updating Sanitization Rules

To modify sanitization behavior:

1. Update `_modules/utils/sanitize.py`
2. Test all existing use cases
3. Update this documentation
4. Run security tests
5. Review all call sites

## Summary

✅ **All user input is sanitized before rendering**
✅ **Multiple sanitization functions for different data types**
✅ **Applied in profile_editor.py and prod_workflow.py**
✅ **Protects against XSS, injection, and path traversal**
✅ **Easy to use and maintain**
✅ **CodeQL security warnings resolved**

**Key Files:**
- `_modules/utils/sanitize.py` - Sanitization module (340 lines, 8 functions)
- `_modules/ui/profile_editor.py` - Protected receipt upload/display (4 locations)
- `_modules/ui/prod_workflow.py` - Protected document workflow (2 locations)
- `tests/test_sanitization.py` - Test suite (44 tests, all passing)
- `docs/SECURITY_SANITIZATION.md` - This document
- `docs/SECURITY_CODEQL_FIX.md` - CodeQL fix for malformed script tags
- `docs/SECURITY_FIXES_SUMMARY.md` - Complete security overview

For questions or security concerns, review the sanitization module source code and test with malicious inputs before deploying to production.
