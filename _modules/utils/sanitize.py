"""Sanitization utilities for user input to prevent XSS attacks.

This module provides comprehensive input sanitization to protect against:
- JavaScript injection
- HTML injection
- Script tag injection
- Event handler injection
- Data URI schemes
- Other XSS attack vectors

Use these functions before rendering any user-provided content in the UI.
"""

import re
import html
from typing import Any, Optional


# Patterns for dangerous content
# Note: These patterns are defense-in-depth. The primary protection is html.escape()
# which safely escapes ALL HTML, including malformed tags. These patterns provide
# an additional layer by removing dangerous content before escaping.
SCRIPT_PATTERNS = [
    # Match <script> tags with forgiving end tag (handles </script foo="bar"> etc.)
    # Browsers accept closing tags with attributes even though it's a parser error
    re.compile(r'<script[^>]*>.*?</script\s*[^>]*>', re.IGNORECASE | re.DOTALL),
    re.compile(r'javascript:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),  # onclick, onload, etc.
    re.compile(r'<iframe[^>]*>', re.IGNORECASE),
    re.compile(r'<embed[^>]*>', re.IGNORECASE),
    re.compile(r'<object[^>]*>', re.IGNORECASE),
    re.compile(r'data:text/html', re.IGNORECASE),
    re.compile(r'vbscript:', re.IGNORECASE),
    re.compile(r'<meta[^>]*http-equiv', re.IGNORECASE),
]


def sanitize_text(text: Any, allow_newlines: bool = True) -> str:
    """Sanitize text input by removing dangerous patterns and escaping HTML.
    
    Args:
        text: Input text to sanitize (will be converted to string)
        allow_newlines: If True, preserves newline characters
        
    Returns:
        Sanitized text safe for display
        
    Examples:
        >>> sanitize_text("<script>alert('xss')</script>Hello")
        "Hello"
        >>> sanitize_text("Normal text with <b>tags</b>")
        "Normal text with &lt;b&gt;tags&lt;/b&gt;"
    """
    if text is None:
        return ""
    
    # Convert to string
    text = str(text)
    
    # Remove dangerous patterns
    for pattern in SCRIPT_PATTERNS:
        text = pattern.sub('', text)
    
    # Escape HTML entities
    text = html.escape(text)
    
    # Preserve newlines if requested
    if allow_newlines:
        # Already escaped, so newlines are safe
        pass
    else:
        text = text.replace('\n', ' ').replace('\r', ' ')
    
    return text


def sanitize_filename(filename: Any) -> str:
    """Sanitize filename to prevent path traversal and injection.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Safe filename with dangerous characters removed
        
    Examples:
        >>> sanitize_filename("../../etc/passwd")
        "passwd"
        >>> sanitize_filename("file<script>.txt")
        "file.txt"
    """
    if filename is None:
        return "unnamed"
    
    filename = str(filename)
    
    # Remove path traversal attempts
    filename = filename.replace('..', '')
    filename = filename.replace('/', '_')
    filename = filename.replace('\\', '_')
    
    # Remove dangerous characters
    filename = re.sub(r'[<>:"|?*]', '', filename)
    
    # Remove script patterns
    for pattern in SCRIPT_PATTERNS:
        filename = pattern.sub('', filename)
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename or "unnamed"


def sanitize_html_content(content: Any, max_length: Optional[int] = None) -> str:
    """Sanitize HTML content for safe display in text areas or code blocks.
    
    This is more aggressive than sanitize_text and suitable for
    displaying user-provided content that might contain HTML/code.
    
    Args:
        content: Content to sanitize
        max_length: Optional maximum length to truncate to
        
    Returns:
        Sanitized content safe for display
    """
    if content is None:
        return ""
    
    content = str(content)
    
    # Remove all dangerous patterns
    for pattern in SCRIPT_PATTERNS:
        content = pattern.sub('[REMOVED]', content)
    
    # Escape HTML
    content = html.escape(content)
    
    # Truncate if needed
    if max_length and len(content) > max_length:
        content = content[:max_length] + "..."
    
    return content


def sanitize_dict(data: dict, keys_to_sanitize: Optional[list] = None) -> dict:
    """Recursively sanitize dictionary values.
    
    Args:
        data: Dictionary to sanitize
        keys_to_sanitize: Optional list of keys to sanitize. If None, sanitizes all string values.
        
    Returns:
        Dictionary with sanitized values
        
    Examples:
        >>> sanitize_dict({"name": "<script>alert(1)</script>John", "age": 30})
        {"name": "John", "age": 30}
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, keys_to_sanitize)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_dict(item, keys_to_sanitize) if isinstance(item, dict) 
                else sanitize_text(item) if isinstance(item, str) and (keys_to_sanitize is None or key in keys_to_sanitize)
                else item
                for item in value
            ]
        elif isinstance(value, str):
            if keys_to_sanitize is None or key in keys_to_sanitize:
                sanitized[key] = sanitize_text(value)
            else:
                sanitized[key] = value
        else:
            sanitized[key] = value
    
    return sanitized


def sanitize_for_markdown(text: Any) -> str:
    """Sanitize text for safe use in Streamlit markdown with unsafe_allow_html=True.
    
    This is the most restrictive sanitization and should be used when
    rendering user content in markdown with HTML enabled.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text safe for markdown with HTML
    """
    if text is None:
        return ""
    
    text = str(text)
    
    # Remove all HTML/script patterns
    for pattern in SCRIPT_PATTERNS:
        text = pattern.sub('', text)
    
    # Remove all HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Escape special markdown characters that could be abused
    text = text.replace('[', '\\[')
    text = text.replace(']', '\\]')
    
    # Escape HTML
    text = html.escape(text)
    
    return text


def sanitize_provider_name(name: Any) -> str:
    """Sanitize provider/user names for display.
    
    Args:
        name: Name to sanitize
        
    Returns:
        Sanitized name
    """
    if name is None or name == "":
        return "N/A"
    
    name = str(name)
    
    # Remove dangerous patterns
    for pattern in SCRIPT_PATTERNS:
        name = pattern.sub('', name)
    
    # Escape HTML
    name = html.escape(name)
    
    # Limit length
    if len(name) > 200:
        name = name[:200] + "..."
    
    return name or "N/A"


def sanitize_amount(amount: Any) -> float:
    """Sanitize and validate amount values.
    
    Args:
        amount: Amount to sanitize
        
    Returns:
        Float value, 0.0 if invalid
    """
    if amount is None:
        return 0.0
    
    try:
        # Convert to float, handle strings
        if isinstance(amount, str):
            # Remove currency symbols and commas
            amount = amount.replace('$', '').replace(',', '').strip()
        return float(amount)
    except (ValueError, TypeError):
        return 0.0


def sanitize_date(date: Any) -> str:
    """Sanitize date strings.
    
    Args:
        date: Date to sanitize
        
    Returns:
        Sanitized date string or "N/A"
    """
    if date is None or date == "":
        return "N/A"
    
    date = str(date)
    
    # Remove dangerous patterns
    for pattern in SCRIPT_PATTERNS:
        date = pattern.sub('', date)
    
    # Validate date format (basic check)
    date = date[:50]  # Limit length
    
    # Escape HTML
    date = html.escape(date)
    
    return date or "N/A"


# Convenience function for common use case
def safe_format(template: str, **kwargs) -> str:
    """Safely format a string template with sanitized user inputs.
    
    Args:
        template: Format string
        **kwargs: Values to format (will be sanitized)
        
    Returns:
        Formatted string with sanitized values
        
    Examples:
        >>> safe_format("Hello {name}!", name="<script>alert(1)</script>John")
        "Hello John!"
    """
    sanitized_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, (int, float)):
            sanitized_kwargs[key] = value
        else:
            sanitized_kwargs[key] = sanitize_text(value)
    
    return template.format(**sanitized_kwargs)
