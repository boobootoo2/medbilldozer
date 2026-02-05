# Input Sanitization & Security

Protect against malicious input and security vulnerabilities.

## Overview

medBillDozer processes user-uploaded documents that may contain:
- Malicious text (script injection attempts)
- Oversized files (DoS attacks)
- Invalid formats (parser exploits)
- Sensitive data (PII, PHI)

**Security layers**:
1. **Input validation**: Check file type, size, format
2. **Sanitization**: Strip HTML, remove scripts
3. **Rate limiting**: Prevent abuse
4. **Safe parsing**: Use secure libraries

## File Upload Security

### File Type Validation

```python
# src/medbilldozer/ui/upload.py
import streamlit as st
from typing import List

ALLOWED_EXTENSIONS = ["pdf", "txt", "png", "jpg", "jpeg"]
MAX_FILE_SIZE_MB = 10

def validate_file_upload(uploaded_file) -> tuple[bool, str]:
    """
    Validate uploaded file for security.
    
    Returns:
        (is_valid, error_message)
    """
    # Check file exists
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File too large: {file_size_mb:.1f} MB (max {MAX_FILE_SIZE_MB} MB)"
    
    # Check file extension
    file_ext = uploaded_file.name.split(".")[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type: .{file_ext} (allowed: {', '.join(ALLOWED_EXTENSIONS)})"
    
    # Check MIME type matches extension
    expected_mime = get_expected_mime(file_ext)
    if uploaded_file.type not in expected_mime:
        return False, f"File type mismatch: extension .{file_ext} but type {uploaded_file.type}"
    
    return True, ""

def get_expected_mime(extension: str) -> List[str]:
    """Get expected MIME types for file extension."""
    mime_map = {
        "pdf": ["application/pdf"],
        "txt": ["text/plain"],
        "png": ["image/png"],
        "jpg": ["image/jpeg"],
        "jpeg": ["image/jpeg"],
    }
    return mime_map.get(extension, [])
```

**Usage in Streamlit**:
```python
# app.py
uploaded_file = st.file_uploader(
    "Upload medical bill",
    type=ALLOWED_EXTENSIONS,
    accept_multiple_files=False
)

if uploaded_file:
    is_valid, error = validate_file_upload(uploaded_file)
    
    if not is_valid:
        st.error(f"❌ {error}")
        st.stop()
    
    # Process file
    process_document(uploaded_file)
```

### Content Validation

```python
# src/medbilldozer/utils/sanitization.py
import re
from typing import Optional

def sanitize_text(text: str, max_length: int = 100000) -> str:
    """
    Sanitize text input for safe processing.
    
    Args:
        text: Raw text input
        max_length: Maximum allowed text length
    
    Returns:
        Sanitized text
    
    Raises:
        ValueError: If text is invalid
    """
    # Check text is not empty
    if not text or not text.strip():
        raise ValueError("Empty text input")
    
    # Check length
    if len(text) > max_length:
        raise ValueError(f"Text too long: {len(text)} chars (max {max_length})")
    
    # Remove null bytes
    text = text.replace("\x00", "")
    
    # Remove control characters (except newline, tab)
    text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", text)
    
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()
```

## HTML/Script Injection Prevention

### Sanitize HTML in Text

```python
# src/medbilldozer/utils/sanitization.py
import html
import re

def strip_html_tags(text: str) -> str:
    """
    Remove HTML tags from text.
    
    Args:
        text: Text possibly containing HTML
    
    Returns:
        Plain text with HTML stripped
    """
    # Unescape HTML entities first
    text = html.unescape(text)
    
    # Remove script tags and content
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove style tags and content
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove all HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    
    # Remove HTML comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    
    return text

def escape_markdown(text: str) -> str:
    """
    Escape Markdown special characters.
    
    Prevents Markdown injection in Streamlit.
    """
    escape_chars = ["\\", "`", "*", "_", "{", "}", "[", "]", "(", ")", "#", "+", "-", ".", "!"]
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text
```

**Example usage**:
```python
# Process user input
raw_text = uploaded_file.read().decode("utf-8")

# Sanitize
clean_text = strip_html_tags(raw_text)
clean_text = sanitize_text(clean_text)

# Now safe to process
result = orchestrator.run(clean_text)
```

### Prevent XSS in Streamlit

```python
# Safe display of user content
import streamlit as st

def display_user_content(content: str):
    """Safely display user-provided content."""
    # Never use st.markdown with unsafe_allow_html=True
    # for user content
    
    # Option 1: Plain text
    st.text(content)
    
    # Option 2: Code block (escapes HTML)
    st.code(content, language="text")
    
    # Option 3: Escaped markdown
    st.markdown(escape_markdown(content))
    
    # ❌ NEVER do this with user content:
    # st.markdown(content, unsafe_allow_html=True)
```

## Rate Limiting

Prevent abuse by limiting request frequency.

### Simple Rate Limiter

```python
# src/medbilldozer/utils/rate_limit.py
from collections import defaultdict
from time import time
from typing import Optional

class RateLimiter:
    """
    Simple in-memory rate limiter.
    
    Tracks request counts per user within time windows.
    """
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)  # user_id -> [timestamps]
    
    def check_limit(self, user_id: str) -> tuple[bool, Optional[int]]:
        """
        Check if user has exceeded rate limit.
        
        Args:
            user_id: Unique user identifier
        
        Returns:
            (is_allowed, seconds_until_reset)
        """
        now = time()
        
        # Get user's request history
        user_requests = self.requests[user_id]
        
        # Remove old requests outside window
        user_requests = [t for t in user_requests if now - t < self.window_seconds]
        
        # Check if limit exceeded
        if len(user_requests) >= self.max_requests:
            oldest_request = min(user_requests)
            seconds_until_reset = int(self.window_seconds - (now - oldest_request))
            return False, seconds_until_reset
        
        # Log new request
        user_requests.append(now)
        self.requests[user_id] = user_requests
        
        return True, None
    
    def reset(self, user_id: str):
        """Clear rate limit for user."""
        if user_id in self.requests:
            del self.requests[user_id]
```

**Usage in Streamlit**:
```python
# app.py
import streamlit as st
from medbilldozer.utils.rate_limit import RateLimiter

# Initialize rate limiter (global)
if "rate_limiter" not in st.session_state:
    st.session_state.rate_limiter = RateLimiter(
        max_requests=10,  # 10 analyses per minute
        window_seconds=60
    )

# Get user identifier (session ID or IP)
user_id = st.runtime.scriptrunner.get_script_run_ctx().session_id

# Check rate limit before processing
rate_limiter = st.session_state.rate_limiter
is_allowed, wait_time = rate_limiter.check_limit(user_id)

if not is_allowed:
    st.error(f"⏱️ Rate limit exceeded. Try again in {wait_time} seconds.")
    st.stop()

# Process request
result = orchestrator.run(document)
```

## SQL Injection Prevention

If using Supabase or database:

### Parameterized Queries

```python
# ✓ Good: Use parameterized queries
from supabase import create_client

supabase = create_client(url, key)

# Safe query with parameters
result = supabase.table("analyses").select("*").eq("user_id", user_id).execute()

# ❌ Bad: String concatenation
# query = f"SELECT * FROM analyses WHERE user_id = '{user_id}'"  # NEVER DO THIS
```

### Input Validation for Database

```python
def validate_user_id(user_id: str) -> bool:
    """Validate user_id format before database query."""
    # Only allow alphanumeric and hyphens
    return bool(re.match(r"^[a-zA-Z0-9-]+$", user_id))

# Usage
if not validate_user_id(user_id):
    raise ValueError("Invalid user_id format")

result = supabase.table("analyses").select("*").eq("user_id", user_id).execute()
```

## API Key Security

### Never Log API Keys

```python
# src/medbilldozer/providers/openai_provider.py
import logging

logger = logging.getLogger(__name__)

class OpenAIProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        # ✓ Good: Redact API key in logs
        logger.info(f"Initialized OpenAI provider (key: {self.api_key[:8]}...)")
        
        # ❌ Bad: Log full API key
        # logger.info(f"API key: {self.api_key}")  # NEVER DO THIS
```

### Mask Secrets in Error Messages

```python
def mask_secret(secret: str, visible_chars: int = 4) -> str:
    """Mask secret for display in errors."""
    if len(secret) <= visible_chars:
        return "*" * len(secret)
    return secret[:visible_chars] + "*" * (len(secret) - visible_chars)

# Usage
try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    # Safe to show in UI
    st.error(f"OpenAI auth failed (key: {mask_secret(api_key)})")
```

## Path Traversal Prevention

Prevent directory traversal attacks in file operations.

```python
# src/medbilldozer/utils/file_ops.py
from pathlib import Path
import os

def safe_file_path(base_dir: str, filename: str) -> Path:
    """
    Create safe file path preventing directory traversal.
    
    Args:
        base_dir: Allowed base directory
        filename: User-provided filename
    
    Returns:
        Safe resolved path
    
    Raises:
        ValueError: If path escapes base_dir
    """
    # Resolve absolute paths
    base = Path(base_dir).resolve()
    target = (base / filename).resolve()
    
    # Check target is within base_dir
    if not str(target).startswith(str(base)):
        raise ValueError(f"Path traversal attempt: {filename}")
    
    return target

# Usage
BASE_DIR = "benchmarks/inputs"

# ✓ Safe
try:
    filepath = safe_file_path(BASE_DIR, "patient_001.txt")
    content = filepath.read_text()
except ValueError as e:
    st.error(f"Invalid file path: {e}")

# ❌ These would be blocked:
# safe_file_path(BASE_DIR, "../../../etc/passwd")  # Raises ValueError
# safe_file_path(BASE_DIR, "/etc/passwd")          # Raises ValueError
```

## Dependency Security

### Regular Updates

```bash
# Check for vulnerabilities
pip install safety
safety check

# Update dependencies
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# Audit specific package
pip show openai
```

### Pin Versions

```txt
# requirements.txt
# Pin exact versions for reproducibility
streamlit==1.28.1
openai==1.5.0
google-generativeai==0.3.2

# ❌ Don't use loose version ranges in production:
# streamlit>=1.20.0  # Too loose
# openai            # No version specified
```

### Scan with Bandit

```bash
# Install bandit
pip install bandit

# Scan codebase
bandit -r src/ -f json -o bandit-report.json

# Common issues detected:
# - Hardcoded passwords
# - SQL injection risks
# - Unsafe deserialization
# - Weak crypto
```

## Environment Security

### Secure .env Files

```bash
# Set strict permissions
chmod 600 .env

# Ensure in .gitignore
echo ".env" >> .gitignore
echo ".streamlit/secrets.toml" >> .gitignore

# Never commit secrets
git secrets --install  # Prevents accidental commits
```

### Validate Configuration

```python
# src/medbilldozer/core/config.py
import os

def validate_config():
    """Validate configuration at startup."""
    errors = []
    
    # Check required variables
    if not os.getenv("OPENAI_API_KEY"):
        errors.append("OPENAI_API_KEY not set")
    
    # Validate key format
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key and not openai_key.startswith("sk-"):
        errors.append("Invalid OPENAI_API_KEY format")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

# Run at startup
validate_config()
```

## Security Checklist

### Before Deployment

- [ ] All secrets in environment variables or Streamlit secrets
- [ ] No secrets committed to git
- [ ] File upload size limits enforced
- [ ] File type validation implemented
- [ ] HTML/script stripping on user input
- [ ] Rate limiting enabled
- [ ] HTTPS enforced (automatic on Streamlit Cloud)
- [ ] Dependencies scanned with safety/bandit
- [ ] Input validation on all user inputs
- [ ] Error messages don't leak sensitive info
- [ ] Logging doesn't include secrets
- [ ] API keys rotated regularly
- [ ] Database queries use parameterized statements
- [ ] Path traversal prevention on file operations

### Regular Maintenance

- [ ] Update dependencies monthly
- [ ] Scan with bandit/safety weekly
- [ ] Rotate API keys quarterly
- [ ] Review access logs monthly
- [ ] Test rate limits quarterly
- [ ] Review error handling quarterly

## Incident Response

### If API Key Compromised

1. **Immediately revoke** key in provider dashboard
2. **Generate new key** with minimal permissions
3. **Update** environment variables/secrets
4. **Review** usage logs for suspicious activity
5. **Monitor** costs for unexpected charges

### If Security Issue Found

1. **Document** the issue (description, impact, affected versions)
2. **Patch** the vulnerability immediately
3. **Test** the fix thoroughly
4. **Deploy** patched version
5. **Notify** users if data was compromised (if applicable)

## Next Steps

- [Privacy Guide](privacy.md) - Data handling best practices
- [Streamlit Deployment](../deployment/streamlit.md) - Secure deployment
- [Environment Variables](../deployment/environment_variables.md) - Configuration
