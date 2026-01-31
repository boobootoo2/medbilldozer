"""Test suite for input sanitization module.

Tests all sanitization functions against known malicious inputs.
"""

import pytest
from _modules.utils.sanitize import (
    sanitize_text,
    sanitize_html_content,
    sanitize_filename,
    sanitize_provider_name,
    sanitize_amount,
    sanitize_date,
    sanitize_dict,
    sanitize_for_markdown,
    safe_format
)


class TestSanitizeText:
    """Test sanitize_text function."""
    
    def test_script_tag_removal(self):
        """Test that script tags are removed."""
        input_text = "<script>alert('xss')</script>Hello"
        result = sanitize_text(input_text)
        assert "<script>" not in result
        assert "alert" not in result
        assert "Hello" in result
    
    def test_event_handler_removal(self):
        """Test that event handlers are removed."""
        input_text = '<img onerror="alert(1)" src=x>'
        result = sanitize_text(input_text)
        # Check that dangerous patterns are removed/escaped, not benign words
        assert "onerror=" not in result.lower()
        assert "<script>" not in result.lower()
        assert "javascript:" not in result.lower()
    
    def test_html_escape(self):
        """Test that HTML is properly escaped."""
        input_text = "Price: <b>$100</b>"
        result = sanitize_text(input_text)
        assert "&lt;b&gt;" in result
        assert "&lt;/b&gt;" in result
        assert "<b>" not in result
    
    def test_javascript_url_removal(self):
        """Test that javascript: URLs are removed."""
        input_text = '<a href="javascript:alert(1)">Click</a>'
        result = sanitize_text(input_text)
        assert "javascript:" not in result.lower()
    
    def test_newline_preservation(self):
        """Test that newlines are preserved by default."""
        input_text = "Line 1\nLine 2"
        result = sanitize_text(input_text, allow_newlines=True)
        assert "\n" in result
    
    def test_newline_removal(self):
        """Test that newlines can be removed."""
        input_text = "Line 1\nLine 2"
        result = sanitize_text(input_text, allow_newlines=False)
        assert "\n" not in result


class TestSanitizeHtmlContent:
    """Test sanitize_html_content function."""
    
    def test_aggressive_html_removal(self):
        """Test that all HTML is removed."""
        input_text = "<div><p>Hello <b>world</b></p></div>"
        result = sanitize_html_content(input_text)
        assert "<div>" not in result
        assert "<p>" not in result
        assert "<b>" not in result
        # Should still contain the text
        assert "Hello" in result
        assert "world" in result
    
    def test_script_marked_as_removed(self):
        """Test that scripts are marked as [REMOVED]."""
        input_text = "<script>alert('xss')</script>Content"
        result = sanitize_html_content(input_text)
        assert "[REMOVED]" in result
        assert "Content" in result
    
    def test_iframe_removal(self):
        """Test that iframes are removed."""
        input_text = '<iframe src="evil.com">Content</iframe>'
        result = sanitize_html_content(input_text)
        assert "iframe" not in result.lower() or "[REMOVED]" in result
    
    def test_max_length_truncation(self):
        """Test that content is truncated to max_length."""
        input_text = "A" * 1000
        result = sanitize_html_content(input_text, max_length=100)
        assert len(result) <= 103  # 100 + "..."
    
    def test_data_uri_removal(self):
        """Test that data URIs are removed."""
        input_text = 'data:text/html,<script>alert(1)</script>'
        result = sanitize_html_content(input_text)
        assert "data:text/html" not in result.lower() or "[REMOVED]" in result


class TestSanitizeFilename:
    """Test sanitize_filename function."""
    
    def test_path_traversal_removal(self):
        """Test that path traversal is blocked."""
        input_text = "../../etc/passwd"
        result = sanitize_filename(input_text)
        # Check that path traversal is prevented (.. removed)
        assert ".." not in result
        # Check that forward/backward slashes are removed or replaced
        assert "/" not in result
        assert "\\" not in result
        # Result should be safe (original was __etc_passwd after sanitization)
        assert len(result) > 0
    
    def test_slash_replacement(self):
        """Test that slashes are replaced."""
        input_text = "path/to/file.txt"
        result = sanitize_filename(input_text)
        assert "/" not in result
        assert "_" in result
    
    def test_dangerous_char_removal(self):
        """Test that dangerous characters are removed."""
        input_text = 'file<script>.txt'
        result = sanitize_filename(input_text)
        assert "<" not in result
        assert ">" not in result
        assert "script" in result  # word stays, brackets removed
    
    def test_length_limit(self):
        """Test that filename is limited to 255 chars."""
        input_text = "A" * 300
        result = sanitize_filename(input_text)
        assert len(result) <= 255
    
    def test_empty_filename(self):
        """Test that empty filename returns 'unnamed'."""
        result = sanitize_filename("")
        assert result == "unnamed"


class TestSanitizeProviderName:
    """Test sanitize_provider_name function."""
    
    def test_script_removal(self):
        """Test that scripts are removed from names."""
        input_text = "<script>alert(1)</script>Dr. Smith"
        result = sanitize_provider_name(input_text)
        assert "<script>" not in result
        assert "Dr. Smith" in result
    
    def test_none_returns_na(self):
        """Test that None returns N/A."""
        result = sanitize_provider_name(None)
        assert result == "N/A"
    
    def test_empty_returns_na(self):
        """Test that empty string returns N/A."""
        result = sanitize_provider_name("")
        assert result == "N/A"
    
    def test_length_limit(self):
        """Test that names are limited to 200 chars."""
        input_text = "Dr. " + "A" * 300
        result = sanitize_provider_name(input_text)
        assert len(result) <= 203  # 200 + "..."


class TestSanitizeAmount:
    """Test sanitize_amount function."""
    
    def test_string_to_float(self):
        """Test string conversion to float."""
        result = sanitize_amount("123.45")
        assert result == 123.45
    
    def test_currency_symbol_removal(self):
        """Test that currency symbols are removed."""
        result = sanitize_amount("$1,234.56")
        assert result == 1234.56
    
    def test_none_returns_zero(self):
        """Test that None returns 0.0."""
        result = sanitize_amount(None)
        assert result == 0.0
    
    def test_invalid_returns_zero(self):
        """Test that invalid input returns 0.0."""
        result = sanitize_amount("invalid")
        assert result == 0.0
    
    def test_negative_numbers(self):
        """Test that negative numbers work."""
        result = sanitize_amount("-50.00")
        assert result == -50.0


class TestSanitizeDate:
    """Test sanitize_date function."""
    
    def test_script_removal(self):
        """Test that scripts are removed from dates."""
        input_text = "<script>alert(1)</script>2026-01-31"
        result = sanitize_date(input_text)
        assert "<script>" not in result
        assert "2026-01-31" in result
    
    def test_none_returns_na(self):
        """Test that None returns N/A."""
        result = sanitize_date(None)
        assert result == "N/A"
    
    def test_length_limit(self):
        """Test that dates are limited to 50 chars."""
        input_text = "2026" + "-01" * 30
        result = sanitize_date(input_text)
        assert len(result) <= 50


class TestSanitizeDict:
    """Test sanitize_dict function."""
    
    def test_all_strings_sanitized(self):
        """Test that all string values are sanitized."""
        input_dict = {
            "name": "<script>alert(1)</script>John",
            "age": 30,
            "city": "<b>NYC</b>"
        }
        result = sanitize_dict(input_dict)
        assert "<script>" not in result["name"]
        assert "John" in result["name"]
        assert result["age"] == 30  # Numbers unchanged
        assert "&lt;b&gt;" in result["city"]
    
    def test_nested_dict_sanitization(self):
        """Test that nested dictionaries are sanitized."""
        input_dict = {
            "user": {
                "name": "<script>evil</script>Bob"
            }
        }
        result = sanitize_dict(input_dict)
        assert "<script>" not in result["user"]["name"]
        assert "Bob" in result["user"]["name"]
    
    def test_list_sanitization(self):
        """Test that lists are sanitized."""
        input_dict = {
            "names": ["<b>Alice</b>", "<i>Bob</i>"]
        }
        result = sanitize_dict(input_dict)
        assert "&lt;b&gt;" in result["names"][0]
        assert "&lt;i&gt;" in result["names"][1]
    
    def test_selective_sanitization(self):
        """Test that only specified keys are sanitized."""
        input_dict = {
            "name": "<b>John</b>",
            "code": "<special_code>"
        }
        result = sanitize_dict(input_dict, keys_to_sanitize=["name"])
        assert "&lt;b&gt;" in result["name"]  # Sanitized
        assert "<special_code>" in result["code"]  # Not sanitized


class TestSanitizeForMarkdown:
    """Test sanitize_for_markdown function."""
    
    def test_html_removal(self):
        """Test that all HTML is removed."""
        input_text = "<div>Hello <b>world</b></div>"
        result = sanitize_for_markdown(input_text)
        assert "<div>" not in result
        assert "<b>" not in result
        assert "Hello" in result
        assert "world" in result
    
    def test_markdown_escape(self):
        """Test that markdown special chars are escaped."""
        input_text = "[Link](url)"
        result = sanitize_for_markdown(input_text)
        assert "\\[" in result
        assert "\\]" in result


class TestSafeFormat:
    """Test safe_format function."""
    
    def test_sanitized_formatting(self):
        """Test that format values are sanitized."""
        result = safe_format(
            "Hello {name}!",
            name="<script>alert(1)</script>John"
        )
        assert "<script>" not in result
        assert "John" in result
    
    def test_numbers_unchanged(self):
        """Test that numbers are not sanitized."""
        result = safe_format(
            "Amount: {amount}",
            amount=123.45
        )
        assert "123.45" in result


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_receipt_processing(self):
        """Test complete receipt processing workflow."""
        # Simulate user input
        pasted_text = """
        <script>alert('xss')</script>
        Dr. Smith Office
        Date: 2026-01-31
        Amount: $150.00
        """
        
        # Sanitize
        safe_content = sanitize_html_content(pasted_text, max_length=500)
        safe_provider = sanitize_provider_name("Dr. Smith<script>")
        safe_amount = sanitize_amount("$150.00")
        safe_date = sanitize_date("2026-01-31")
        
        # Verify
        assert "<script>" not in safe_content
        assert "<script>" not in safe_provider
        assert safe_amount == 150.0
        assert safe_date == "2026-01-31"
    
    def test_imported_data_processing(self):
        """Test imported line item processing."""
        import_data = {
            "provider_name": "<script>Evil</script>Hospital",
            "procedure_description": "<b>Surgery</b>",
            "billed_amount": "$2,500.00",
            "service_date": "2026-01-15<script>"
        }
        
        # Sanitize
        safe_data = sanitize_dict(import_data)
        
        # Verify
        assert "<script>" not in safe_data["provider_name"]
        assert "Hospital" in safe_data["provider_name"]
        assert "&lt;b&gt;" in safe_data["procedure_description"]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_none_inputs(self):
        """Test that None inputs are handled gracefully."""
        assert sanitize_text(None) == ""
        assert sanitize_html_content(None) == ""
        assert sanitize_filename(None) == "unnamed"
        assert sanitize_provider_name(None) == "N/A"
        assert sanitize_amount(None) == 0.0
        assert sanitize_date(None) == "N/A"
    
    def test_empty_inputs(self):
        """Test that empty inputs are handled."""
        assert sanitize_text("") == ""
        assert sanitize_filename("") == "unnamed"
        assert sanitize_provider_name("") == "N/A"
    
    def test_very_long_inputs(self):
        """Test handling of very long inputs."""
        long_text = "A" * 100000
        result = sanitize_html_content(long_text, max_length=1000)
        assert len(result) <= 1003
    
    def test_unicode_handling(self):
        """Test that unicode is preserved."""
        input_text = "Hello 世界 🌍"
        result = sanitize_text(input_text)
        assert "世界" in result
        assert "🌍" in result
    
    def test_mixed_attacks(self):
        """Test combinations of multiple attack vectors."""
        input_text = """
        <script>alert('xss')</script>
        <img onerror="alert(1)" src=x>
        javascript:alert(2)
        ../../etc/passwd
        <iframe src="evil.com"></iframe>
        """
        result = sanitize_html_content(input_text)
        assert "<script>" not in result
        assert "onerror" not in result
        assert "javascript:" not in result.lower()
        assert "<iframe>" not in result


if __name__ == "__main__":
    """Run tests manually."""
    import sys
    
    print("Running sanitization tests...\n")
    
    tests_run = 0
    tests_passed = 0
    
    # Get all test classes
    test_classes = [
        TestSanitizeText,
        TestSanitizeHtmlContent,
        TestSanitizeFilename,
        TestSanitizeProviderName,
        TestSanitizeAmount,
        TestSanitizeDate,
        TestSanitizeDict,
        TestSanitizeForMarkdown,
        TestSafeFormat,
        TestIntegration,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                tests_run += 1
                try:
                    method = getattr(instance, method_name)
                    method()
                    print(f"  ✅ {method_name}")
                    tests_passed += 1
                except Exception as e:
                    print(f"  ❌ {method_name}: {e}")
    
    print(f"\n{'='*50}")
    print(f"Tests run: {tests_run}")
    print(f"Tests passed: {tests_passed}")
    print(f"Tests failed: {tests_run - tests_passed}")
    
    if tests_passed == tests_run:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {tests_run - tests_passed} test(s) failed")
        sys.exit(1)
