# Security Sanitization - Quick Reference

## Import Statement

```python
from _modules.utils.sanitize import (
    sanitize_text,
    sanitize_html_content,
    sanitize_provider_name,
    sanitize_filename,
    sanitize_amount,
    sanitize_date
)
```

## Function Reference

| Function | Use For | Example |
|----------|---------|---------|
| `sanitize_text(text)` | General text, names, descriptions | `safe_name = sanitize_text(user_input)` |
| `sanitize_html_content(content, max_length)` | Pasted text, raw HTML, file content | `safe_content = sanitize_html_content(pasted_text, max_length=500)` |
| `sanitize_provider_name(name)` | Provider names, user names | `provider = sanitize_provider_name(receipt['provider'])` |
| `sanitize_filename(filename)` | File upload names | `safe_name = sanitize_filename(uploaded_file.name)` |
| `sanitize_amount(amount)` | Monetary values | `amount = sanitize_amount(user_input)` |
| `sanitize_date(date)` | Date strings | `date = sanitize_date(receipt['date'])` |

## Common Patterns

### Pattern 1: File Upload

```python
uploaded_file = st.file_uploader("Upload receipt")
if uploaded_file:
    safe_name = sanitize_filename(uploaded_file.name)
    content = uploaded_file.read().decode('utf-8')
    safe_content = sanitize_html_content(content, max_length=1000)
```

### Pattern 2: Text Area Input

```python
pasted_text = st.text_area("Paste receipt text")
if pasted_text:
    safe_text = sanitize_html_content(pasted_text, max_length=10000)
    save_receipt(safe_text)
```

### Pattern 3: Display User Data

```python
receipt = load_receipt()
safe_provider = sanitize_provider_name(receipt['provider'])
safe_filename = sanitize_filename(receipt['file_name'])
safe_amount = sanitize_amount(receipt['amount'])

st.write(f"**File:** {safe_filename}")
st.write(f"**Provider:** {safe_provider}")
st.write(f"**Amount:** ${safe_amount:.2f}")
```

### Pattern 4: Loop Through Data

```python
for doc in documents:
    safe_provider = sanitize_provider_name(doc['provider'])
    safe_date = sanitize_date(doc['service_date'])
    safe_amount = sanitize_amount(doc['amount'])
    
    st.write(f"{safe_date} - {safe_provider}: ${safe_amount:.2f}")
```

### Pattern 5: Content Field Construction

```python
# Sanitize all variables first
safe_filename = sanitize_filename(file_name)
safe_provider = sanitize_provider_name(provider)
safe_notes = sanitize_text(notes)
safe_content = sanitize_html_content(raw_content, max_length=500)

# Then build content string
content = f"""RECEIPT - {safe_filename}

Provider: {safe_provider}
Notes: {safe_notes}

--- RAW CONTENT ---
{safe_content}
"""
```

## Protected Locations

✅ `_modules/ui/profile_editor.py`
- Receipt upload (paste & file)
- Receipt display table
- Import text paste

✅ `_modules/ui/prod_workflow.py`
- Receipt loading
- Imported line items
- Document display

## Cheat Sheet

### What to Sanitize

✅ File names from uploads
✅ Pasted text content
✅ Provider names
✅ User notes
✅ Imported data (any source)
✅ Raw file content
✅ Document descriptions

### When to Sanitize

✅ At input (when receiving data)
✅ Before display (when rendering)
✅ Before storage (when saving)

### Functions by Risk Level

**High Risk** (user HTML/code):
- `sanitize_html_content()` - Most aggressive

**Medium Risk** (general text):
- `sanitize_text()` - Standard protection

**Low Risk** (specific types):
- `sanitize_filename()` - Path traversal
- `sanitize_provider_name()` - Names
- `sanitize_amount()` - Numbers
- `sanitize_date()` - Dates

## Testing Snippets

```python
# Test script injection
test = "<script>alert('xss')</script>Hello"
result = sanitize_text(test)
# Expected: "Hello" (script removed)

# Test HTML escape
test = "Price: $100 <b>bold</b>"
result = sanitize_text(test)
# Expected: "Price: $100 &lt;b&gt;bold&lt;/b&gt;"

# Test filename safety
test = "../../etc/passwd"
result = sanitize_filename(test)
# Expected: "passwd" (no path traversal)

# Test amount parsing
test = "$1,234.56"
result = sanitize_amount(test)
# Expected: 1234.56 (float)
```

## Quick Decisions

**Q: Should I sanitize this user input?**
A: YES, always sanitize user input.

**Q: Which function should I use?**
A: Match to data type:
- Text → `sanitize_text()`
- HTML/Code → `sanitize_html_content()`
- Filename → `sanitize_filename()`
- Name → `sanitize_provider_name()`
- Money → `sanitize_amount()`
- Date → `sanitize_date()`

**Q: Do I need to sanitize data from our database?**
A: YES, if it originated from user input.

**Q: What about data from external APIs?**
A: YES, sanitize all external data.

**Q: Can I use `unsafe_allow_html=True` with sanitized data?**
A: YES, but prefer using it without user data when possible.

## Example: Complete Receipt Processing

```python
from _modules.utils.sanitize import (
    sanitize_filename,
    sanitize_html_content,
    sanitize_provider_name,
    sanitize_amount,
    sanitize_date,
    sanitize_text
)

# 1. RECEIVE INPUT
uploaded_file = st.file_uploader("Upload receipt")
pasted_text = st.text_area("Or paste text")
provider_input = st.text_input("Provider name")
amount_input = st.number_input("Amount")

# 2. SANITIZE IMMEDIATELY
if uploaded_file:
    safe_filename = sanitize_filename(uploaded_file.name)
    file_content = uploaded_file.read().decode('utf-8')
    safe_content = sanitize_html_content(file_content, max_length=5000)

if pasted_text:
    safe_pasted = sanitize_html_content(pasted_text, max_length=10000)

safe_provider = sanitize_provider_name(provider_input)
safe_amount = sanitize_amount(amount_input)

# 3. STORE SANITIZED DATA
receipt = {
    'file_name': safe_filename,
    'raw_content': safe_content or safe_pasted,
    'provider': safe_provider,
    'amount': safe_amount,
    'date': datetime.now().isoformat()
}
save_receipt(receipt)

# 4. DISPLAY SAFELY
st.write(f"**File:** {safe_filename}")
st.write(f"**Provider:** {safe_provider}")
st.write(f"**Amount:** ${safe_amount:.2f}")
st.text(safe_content[:200] + "...")
```

## Remember

🔐 **Sanitize ALWAYS**
🔐 **Sanitize EARLY** (at input)
🔐 **Sanitize CONSISTENTLY** (every display)
🔐 **Test with MALICIOUS input**

For complete documentation, see `docs/SECURITY_SANITIZATION.md`
