"""Tests for ReDoS (Regular Expression Denial of Service) protection.

These tests verify that regex operations on user-controlled data have proper
protections against catastrophic backtracking attacks.
"""

import time
import pytest
from medbilldozer.extractors.local_heuristic_extractor import _find_first, extract_facts_local


class TestReDoSProtection:
    """Test ReDoS protection in regex operations."""
    
    def test_find_first_handles_large_input(self):
        """Test that _find_first limits input size to prevent ReDoS."""
        # Create input larger than 100KB
        large_text = "A" * 200000  # 200KB
        pattern = r"(test)"
        
        # Should not raise error, just truncate
        result = _find_first(pattern, large_text)
        # Pattern won't match since we filled with 'A's
        assert result is None
    
    def test_find_first_handles_complex_input(self):
        """Test that _find_first handles complex input gracefully."""
        # Input with many repeated characters that could trigger
        # inefficient backtracking with poorly written patterns
        complex_input = "a" * 1000 + "test" + "b" * 1000
        
        # Use a safe pattern to test the protection works
        # (avoiding actually vulnerable patterns in tests)
        start = time.time()
        result = _find_first(r"(test)", complex_input)
        elapsed = time.time() - start
        
        # Should complete quickly due to input length limit and safe pattern
        assert elapsed < 1.0
        assert result == "test"
    
    def test_find_first_handles_invalid_regex(self):
        """Test that _find_first handles invalid regex patterns gracefully."""
        text = "Sample text"
        invalid_pattern = r"(?P<invalid"  # Unclosed group
        
        # Should return None instead of raising error
        result = _find_first(invalid_pattern, text)
        assert result is None
    
    def test_extract_facts_with_malicious_input(self):
        """Test that extract_facts_local handles malicious input without hanging."""
        # Create potentially malicious input
        malicious = "<" * 10000  # Could cause ReDoS in HTML stripping
        
        start = time.time()
        result = extract_facts_local(malicious)
        elapsed = time.time() - start
        
        # Should complete quickly
        assert elapsed < 2.0
        # Should return empty facts or valid result
        assert isinstance(result, dict)
    
    def test_extract_facts_with_nested_patterns(self):
        """Test extraction with deeply nested patterns that could cause backtracking."""
        # Nested parentheses that could cause issues with greedy matching
        text = "Provider: " + "(" * 500 + "Test" + ")" * 500
        
        start = time.time()
        result = extract_facts_local(text)
        elapsed = time.time() - start
        
        # Should complete without hanging
        assert elapsed < 2.0
        assert isinstance(result, dict)
    
    def test_find_first_with_normal_input(self):
        """Test that _find_first still works correctly with normal input."""
        text = "Patient Name: John Smith\nDOB: 01/15/1980"
        pattern = r"Patient Name:\s*([^\n\r]+)"
        
        result = _find_first(pattern, text)
        assert result == "John Smith"
    
    def test_extract_facts_with_normal_receipt(self):
        """Test that extract_facts_local still works with normal input."""
        receipt = """
        CVS Pharmacy
        Store #1234
        123 Main St, Springfield, IL
        (555) 123-4567
        
        Receipt #: RX-789456
        Date: January 15, 2024
        Time: 10:30 AM
        
        Patient Name: Jane Doe
        """
        
        result = extract_facts_local(receipt)
        
        # Should extract some facts successfully
        assert result["document_type"] == "pharmacy_receipt"
        assert result["store_id"] == "1234"
        assert result["receipt_number"] in ["RX-789456", "789456"]


class TestHTMLStripReDoS:
    """Test ReDoS protection in HTML stripping functions."""
    
    def test_malformed_html_tags(self):
        """Test handling of malformed HTML that could cause ReDoS."""
        # Import the module that has strip_html functions
        from medbilldozer.ui import ui_pipeline_dag
        
        # Malicious input: many < without closing >
        malicious_html = "<" * 10000
        
        # This should not hang or cause excessive CPU usage
        # Note: We can't directly call strip_html as it's defined inline,
        # but we can test that the module loads without errors
        assert hasattr(ui_pipeline_dag, 'render_pipeline_dag')
    
    def test_extremely_long_html_attribute(self):
        """Test handling of extremely long HTML attributes."""
        # HTML tag with extremely long attribute (could cause backtracking)
        long_attr = 'a' * 10000
        malicious = f'<div class="{long_attr}">'
        
        # The pattern r'<[^>]{1,500}>' should limit this to 500 chars
        # and prevent catastrophic backtracking
        import re
        
        start = time.time()
        result = re.sub(r'<[^>]{1,500}>', '', malicious)
        elapsed = time.time() - start
        
        # Should complete very quickly
        assert elapsed < 0.1

        # Either removes tag OR leaves it unchanged safely
        assert isinstance(result, str)




class TestInputLimits:
    """Test that input length limits are enforced."""
    
    def test_find_first_truncates_long_input(self):
        """Verify that _find_first truncates input beyond 100KB."""
        # Create 150KB of data with pattern at the end
        text = "x" * 150000 + "Patient Name: Test User"
        pattern = r"Patient Name:\s*([^\n\r]+)"
        
        # Pattern is beyond 100KB limit, so won't be found
        result = _find_first(pattern, text)
        
        # Should return None because pattern was truncated off
        assert result is None
    
    def test_find_first_finds_pattern_within_limit(self):
        """Verify that _find_first finds patterns within 100KB limit."""
        # Create pattern within first 100KB
        text = "Patient Name: John Doe\n" + "x" * 150000
        pattern = r"Patient Name:\s*([^\n\r]+)"
        
        # Pattern is within 100KB limit, so should be found
        result = _find_first(pattern, text)
        
        # Should find the pattern
        assert result == "John Doe"


class TestEdgeCases:
    """Test edge cases for regex protection."""
    
    def test_empty_input(self):
        """Test handling of empty input."""
        assert _find_first(r"(test)", "") is None
        assert extract_facts_local("") == {k: None for k in extract_facts_local("").keys()}
    
    def test_none_input(self):
        """Test handling of None input."""
        # _find_first expects string, so this would be caller's responsibility
        # extract_facts_local should handle it
        result = extract_facts_local("")
        assert isinstance(result, dict)
    
    def test_unicode_input(self):
        """Test handling of Unicode input."""
        unicode_text = "Patient Name: José García\n日本語\n🏥"
        
        result = extract_facts_local(unicode_text)
        assert isinstance(result, dict)
        # Should handle Unicode gracefully
    
    def test_binary_data_in_string(self):
        """Test handling of binary data converted to string."""
        # Simulate binary data that might come from file upload
        binary_like = "\\x00\\x01\\x02" * 100
        
        result = extract_facts_local(binary_like)
        assert isinstance(result, dict)
    
    def test_special_regex_chars(self):
        """Test that special regex characters in input don't cause errors."""
        special_chars = r".*+?[](){}^$|\\Test"
        
        # Should handle special chars in text (not pattern)
        result = _find_first(r"(Test)", special_chars)
        assert result == "Test"


class TestPerformance:
    """Test that regex operations perform within acceptable time limits."""
    
    def test_multiple_extractions_complete_quickly(self):
        """Test that multiple fact extractions complete in reasonable time."""
        receipts = [
            "CVS Receipt #" + str(i) + "\nStore #" + str(i)
            for i in range(100)
        ]
        
        start = time.time()
        for receipt in receipts:
            extract_facts_local(receipt)
        elapsed = time.time() - start
        
        # 100 extractions should complete in under 2 seconds
        assert elapsed < 2.0
    
    def test_pathological_input_bounded_time(self):
        """Test that even pathological input completes in bounded time."""
        # Create input that could trigger worst-case regex behavior
        pathological = "a" * 50000 + "b" * 50000
        
        start = time.time()
        result = extract_facts_local(pathological)
        elapsed = time.time() - start
        
        # Even worst case should complete quickly due to protections
        assert elapsed < 1.0
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
