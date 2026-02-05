# CodeQL Security Fix: Script Tag Regex Pattern

**Date:** January 31, 2026  
**Issue:** CodeQL Warning - Bad HTML filtering regexp  
**Severity:** Medium  
**Status:** ✅ FIXED

---

## Problem Description

### CodeQL Warning

```
py/bad-tag-filter: This regular expression does not match script end tags like </script >.
```

### Original Vulnerable Pattern

```python
re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
```

### Why This Was Problematic

Browsers have **very forgiving HTML parsers** and will accept malformed closing tags:

- `</script>` - Standard closing tag ✅
- `</script >` - Closing tag with space ✅ (accepted by browsers)
- `</script foo="bar">` - Closing tag with attributes ✅ (accepted by browsers, parser error but still works)
- `</SCRIPT>` - Case variations ✅

The original regex only matched `</script>` exactly and would miss these variants:

```html
<script>alert(1)</script foo="bar">
<!-- Original regex would NOT match the closing tag with attributes -->
```

Even though `</script foo="bar">` is technically a **parser error**, browsers will still interpret it as a closing script tag and execute the JavaScript.

---

## Solution: Defense-in-Depth Architecture

### Our Security Model

We use a **layered defense** approach:

```
Layer 1 (Primary): html.escape() - Escapes ALL HTML including malformed tags
         ↓
Layer 2 (Secondary): Regex removal - Removes dangerous content before escaping
```

### Why html.escape() is the Critical Layer

The `html.escape()` function is our **primary protection** and handles ALL cases:

```python
# Input: <script>alert(1)</script foo="bar">
# After html.escape(): &lt;script&gt;alert(1)&lt;/script foo="bar"&gt;
# Result: Completely safe - no execution possible
```

Even malformed tags become harmless:
- `<` becomes `&lt;`
- `>` becomes `&gt;`
- Browser sees text, not HTML

### Why We Still Fixed the Regex

The regex provides **defense-in-depth**:

1. **Removes dangerous content** before escaping (cleaner output)
2. **Reduces attack surface** (less content to escape)
3. **Belt and suspenders** (multiple layers of protection)
4. **Best practice** (CodeQL recommendations)

### Fixed Pattern

```python
# Match <script> tags with forgiving end tag (handles </script foo="bar"> etc.)
# Browsers accept closing tags with attributes even though it's a parser error
re.compile(r'<script[^>]*>.*?</script\s*[^>]*>', re.IGNORECASE | re.DOTALL)
```

**What changed:**
- `</script>` → `</script\s*[^>]*>`
- Now matches: `</script>`, `</script >`, `</script foo="bar">`, etc.

---

## Test Coverage

### New Test Case Added

```python
def test_malformed_script_tag_removal(self):
    """Test that malformed script closing tags are handled (CodeQL security fix)."""
    # Browsers accept </script foo="bar"> as a valid closing tag
    input_text = '<script>alert(1)</script foo="bar">Safe text'
    result = sanitize_text(input_text)
    
    # Script content should be removed
    assert "alert" not in result.lower()
    assert "<script>" not in result.lower()
    
    # Safe text should remain (escaped)
    assert "Safe text" in result or "Safe" in result
```

### Test Results

```bash
$ pytest tests/test_sanitization.py -v
============================= test session starts ==============================
...
tests/test_sanitization.py::TestSanitizeText::test_malformed_script_tag_removal PASSED
...
============================== 44 passed in 0.06s ===============================
```

✅ **All 44 tests pass** (previously 115 tests, refactored to 44)

---

## Security Impact Assessment

### Before Fix

**Risk Level:** 🟡 LOW-MEDIUM
- Primary defense (`html.escape()`) was already protecting against ALL attacks
- Regex was defense-in-depth layer only
- Theoretical bypass if someone only used regex without html.escape()

### After Fix

**Risk Level:** 🟢 LOW
- Primary defense (`html.escape()`) unchanged and still protecting
- Secondary defense (regex) now more robust
- CodeQL warning resolved
- Best practices followed

### Why This Wasn't Critical

Our architecture already had strong protection:

```python
def sanitize_text(text):
    # Step 1: Remove dangerous patterns (SECONDARY)
    for pattern in SCRIPT_PATTERNS:
        text = pattern.sub('', text)
    
    # Step 2: Escape HTML (PRIMARY - this is the real protection)
    text = html.escape(text)
    
    return text
```

Even if the regex missed a malformed tag, `html.escape()` would still make it safe:

```python
# Input: <script>alert(1)</script foo="bar">
# After regex (before fix): <script>alert(1)</script foo="bar">  # Missed the closing tag
# After html.escape(): &lt;script&gt;alert(1)&lt;/script foo="bar"&gt;
# Result: STILL SAFE - browser sees text, not executable code
```

---

## References

### CodeQL Documentation

- **Rule ID:** `py/bad-tag-filter`
- **CWE:** CWE-116 (Improper Encoding or Escaping of Output)
- **Category:** Security / XSS Prevention

### External References

1. **Securitum:** "The Curious Case of Copy & Paste" - HTML sanitization pitfalls
2. **Stack Overflow:** "You can't parse [X]HTML with regex" - Why parsing HTML is hard
3. **HTML Standard:** Comment end bang state - Browser parsing behavior
4. **Stack Overflow:** "Why aren't browsers strict about HTML?" - Forgiving parsers

### Related Security Standards

- **CWE-116:** Improper Encoding or Escaping of Output
- **CWE-20:** Improper Input Validation  
- **CWE-185:** Incorrect Regular Expression
- **CWE-186:** Overly Restrictive Regular Expression

---

## Best Practices Applied

### ✅ Use Well-Tested Sanitization Libraries

We use Python's built-in `html.escape()` which is:
- Battle-tested across millions of applications
- Part of Python standard library
- Handles ALL HTML edge cases correctly

### ✅ Defense-in-Depth

Multiple layers of protection:
1. Regex removal (catches obvious attacks)
2. HTML escaping (catches everything else)
3. Input validation (type checking, length limits)
4. Output encoding (proper escaping at render time)

### ✅ Prefer Escaping Over Parsing

We **escape** HTML rather than trying to **parse** it:
- Parsing HTML with regex is fundamentally flawed
- Escaping is simple, reliable, and fast
- No corner cases to miss

### ✅ Test Edge Cases

Our test suite covers:
- Standard script tags
- Malformed closing tags
- Event handlers
- JavaScript URLs
- Data URIs
- Unicode attacks
- Mixed attack vectors

---

## Code Changes Summary

### Files Modified

1. **`_modules/utils/sanitize.py`** (Line 21)
   - Updated `SCRIPT_PATTERNS` regex for script tags
   - Added documentation about defense-in-depth approach
   - No breaking changes to API

2. **`tests/test_sanitization.py`** (Line 29)
   - Added `test_malformed_script_tag_removal()` test case
   - Verifies malformed closing tags are handled

3. **`docs/SECURITY_CODEQL_FIX.md`** (NEW)
   - This document

### Git Commit

```bash
git add _modules/utils/sanitize.py tests/test_sanitization.py docs/SECURITY_CODEQL_FIX.md
git commit -m "security: Fix CodeQL warning for script tag regex pattern

- Updated regex to match malformed closing tags like </script foo='bar'>
- Added test case for malformed script tag handling
- Documented defense-in-depth architecture
- All 44 tests passing

CodeQL Rule: py/bad-tag-filter
Risk: Low (html.escape() already protecting, this is defense-in-depth)
Impact: More robust secondary defense layer"
```

---

## Developer Guidelines

### When to Use Each Sanitization Function

| Input Type | Function | Example |
|------------|----------|---------|
| **General text** | `sanitize_text()` | User names, descriptions |
| **HTML/Code** | `sanitize_html_content()` | Pasted content, file uploads |
| **Filenames** | `sanitize_filename()` | Receipt uploads, imports |
| **Provider names** | `sanitize_provider_name()` | Medical provider names |
| **Amounts** | `sanitize_amount()` | Dollar amounts, costs |
| **Dates** | `sanitize_date()` | Date strings |
| **Markdown** | `sanitize_for_markdown()` | Content for st.markdown() |

### Security Checklist

Before rendering user input:

- [ ] Input is sanitized with appropriate function
- [ ] HTML is escaped with `html.escape()` or sanitization function
- [ ] Length limits applied (prevent DoS)
- [ ] Type validation performed
- [ ] Test case added for new input vector
- [ ] Documentation updated if new pattern added

### When NOT to Worry

You do **NOT** need to sanitize:

- Static HTML (no user input)
- System-generated content (internal variables)
- Data from trusted sources (pre-sanitized)
- Numeric/boolean values (not strings)

---

## Monitoring and Maintenance

### CodeQL Scanning

Run CodeQL regularly:

```bash
# Via GitHub Actions (automated on push)
.github/workflows/codeql-analysis.yml

# Or manually
codeql database create /tmp/codeql-db --language=python
codeql database analyze /tmp/codeql-db python-security-and-quality.qls
```

### Security Testing

Run sanitization tests before each release:

```bash
pytest tests/test_sanitization.py -v
```

### Future Improvements

1. **Content Security Policy (CSP)**
   - Add CSP headers to prevent inline scripts
   - Block `unsafe-inline` and `unsafe-eval`

2. **Automated Scanning**
   - Pre-commit hooks for new `unsafe_allow_html` uses
   - CI/CD security checks

3. **Regular Expression Review**
   - Periodic review of regex patterns
   - Update based on new attack vectors

---

## Conclusion

✅ **CodeQL warning resolved**  
✅ **Defense-in-depth improved**  
✅ **Best practices followed**  
✅ **All tests passing**  
✅ **Documentation complete**

The fix strengthens our **secondary defense layer** while maintaining the robust **primary protection** of `html.escape()`. Our security posture remains strong with multiple layers of protection against XSS attacks.

**No breaking changes.** All existing code continues to work as expected.
