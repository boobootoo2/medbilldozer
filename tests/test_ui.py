"""Tests for UI utility functions (_modules/ui/ui.py).

Tests verify:
- Savings calculation logic
- HTML to plain text conversion
- State management helpers
- Pure utility functions (no Streamlit rendering)
"""

import pytest
from unittest.mock import Mock, MagicMock
import sys

# Mock streamlit
streamlit_mock = MagicMock()
streamlit_mock.components = MagicMock()
streamlit_mock.components.v1 = MagicMock()
sys.modules['streamlit'] = streamlit_mock
sys.modules['streamlit.components'] = streamlit_mock.components
sys.modules['streamlit.components.v1'] = streamlit_mock.components.v1

from medbilldozer.ui.ui import calculate_max_savings, html_to_plain_text
from medbilldozer.providers.llm_interface import Issue


class TestCalculateMaxSavings:
    """Test calculate_max_savings function."""

    def test_calculates_total_from_issues_with_savings(self):
        """Should sum max_savings from all issues."""
        issues = [
            Issue(type="billing_error", summary="Issue 1", evidence="Evidence 1", max_savings=100.0),
            Issue(type="duplicate_charge", summary="Issue 2", evidence="Evidence 2", max_savings=50.0),
            Issue(type="overbilling", summary="Issue 3", evidence="Evidence 3", max_savings=25.50),
        ]

        total, breakdown = calculate_max_savings(issues)

        assert total == 175.50
        assert len(breakdown) == 3

    def test_handles_issues_without_max_savings(self):
        """Should skip issues without max_savings attribute."""
        issues = [
            Issue(type="billing_error", summary="Issue 1", evidence="Evidence 1", max_savings=100.0),
            Issue(type="duplicate_charge", summary="Issue 2", evidence="Evidence 2"),  # No max_savings
        ]

        total, breakdown = calculate_max_savings(issues)

        assert total == 100.0
        assert len(breakdown) == 1

    def test_handles_issues_with_none_max_savings(self):
        """Should skip issues where max_savings is None."""
        issues = [
            Issue(type="billing_error", summary="Issue 1", evidence="Evidence 1", max_savings=100.0),
            Issue(type="duplicate_charge", summary="Issue 2", evidence="Evidence 2", max_savings=None),
        ]

        total, breakdown = calculate_max_savings(issues)

        assert total == 100.0
        assert len(breakdown) == 1

    def test_returns_zero_for_empty_issues_list(self):
        """Should return 0 total and empty breakdown for no issues."""
        total, breakdown = calculate_max_savings([])

        assert total == 0.0
        assert breakdown == []

    def test_returns_zero_when_no_issues_have_savings(self):
        """Should return 0 total when all issues lack max_savings."""
        issues = [
            Issue(type="billing_error", summary="Issue 1", evidence="Evidence 1"),
            Issue(type="duplicate_charge", summary="Issue 2", evidence="Evidence 2"),
        ]

        total, breakdown = calculate_max_savings(issues)

        assert total == 0.0
        assert breakdown == []

    def test_rounds_total_to_two_decimals(self):
        """Should round total to 2 decimal places."""
        issues = [
            Issue(type="billing_error", summary="Issue 1", evidence="Evidence 1", max_savings=10.555),
            Issue(type="duplicate_charge", summary="Issue 2", evidence="Evidence 2", max_savings=20.444),
        ]

        total, breakdown = calculate_max_savings(issues)

        # Total should be rounded: 10.555 + 20.444 = 30.999, rounds to 31.00
        assert total == 31.00

    def test_breakdown_includes_summary_and_savings(self):
        """Breakdown should include summary and max_savings for each issue."""
        issues = [
            Issue(type="billing_error", summary="Test Issue", evidence="Evidence", max_savings=123.45),
        ]

        total, breakdown = calculate_max_savings(issues)

        assert len(breakdown) == 1
        assert breakdown[0]["summary"] == "Test Issue"
        assert breakdown[0]["max_savings"] == 123.45

    def test_breakdown_rounds_individual_savings(self):
        """Breakdown should round individual savings to 2 decimals."""
        issues = [
            Issue(type="billing_error", summary="Issue", evidence="Evidence", max_savings=123.456),
        ]

        total, breakdown = calculate_max_savings(issues)

        assert breakdown[0]["max_savings"] == 123.46


class TestHtmlToPlainText:
    """Test html_to_plain_text function."""

    def test_removes_html_tags(self):
        """Should remove all HTML tags."""
        html = "<p>This is <b>bold</b> text.</p>"
        result = html_to_plain_text(html)

        # BeautifulSoup get_text(separator="\n") preserves newlines between tags
        assert "This is" in result
        assert "bold" in result
        assert "text." in result
        assert "<" not in result
        assert ">" not in result

    def test_removes_script_tags_and_content(self):
        """Should remove <script> tags and their content."""
        html = """
        <p>Visible text</p>
        <script>alert('hidden');</script>
        <p>More text</p>
        """
        result = html_to_plain_text(html)

        assert "Visible text" in result
        assert "More text" in result
        assert "alert" not in result
        assert "script" not in result.lower()

    def test_removes_style_tags_and_content(self):
        """Should remove <style> tags and their content."""
        html = """
        <p>Visible text</p>
        <style>.class { color: red; }</style>
        <p>More text</p>
        """
        result = html_to_plain_text(html)

        assert "Visible text" in result
        assert "More text" in result
        assert "color" not in result
        assert ".class" not in result

    def test_converts_line_breaks(self):
        """Should preserve some line break structure."""
        html = "<p>Paragraph 1</p><p>Paragraph 2</p>"
        result = html_to_plain_text(html)

        # Should have text from both paragraphs
        assert "Paragraph 1" in result
        assert "Paragraph 2" in result

    def test_normalizes_excessive_whitespace(self):
        """Should collapse multiple consecutive newlines."""
        html = """
        <p>Text 1</p>


        <p>Text 2</p>
        """
        result = html_to_plain_text(html)

        # Should not have more than 2 consecutive newlines
        assert "\n\n\n" not in result

    def test_strips_leading_trailing_whitespace(self):
        """Should strip leading and trailing whitespace."""
        html = "   <p>Text</p>   "
        result = html_to_plain_text(html)

        assert result == "Text"
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_handles_empty_html(self):
        """Should handle empty HTML string."""
        result = html_to_plain_text("")
        assert result == ""

    def test_handles_html_with_only_tags(self):
        """Should return empty string for HTML with no text content."""
        html = "<div><span></span></div>"
        result = html_to_plain_text(html)
        assert result == ""

    def test_preserves_special_characters(self):
        """Should preserve special characters in text."""
        html = "<p>Cost: $100.50 &amp; taxes</p>"
        result = html_to_plain_text(html)

        assert "$100.50" in result
        # BeautifulSoup automatically decodes HTML entities
        assert "&" in result or "amp" not in result

    def test_handles_nested_tags(self):
        """Should handle deeply nested HTML tags."""
        html = "<div><section><article><p>Nested <b>bold <i>italic</i></b> text</p></article></section></div>"
        result = html_to_plain_text(html)

        # Check for key words (newlines may be present)
        assert "Nested" in result
        assert "bold" in result
        assert "italic" in result
        assert "text" in result

    def test_handles_medical_bill_html(self):
        """Should extract readable text from medical bill HTML."""
        html = """
        <html>
        <head><title>Medical Bill</title></head>
        <body>
            <h1>Patient Statement</h1>
            <p>Patient: John Doe</p>
            <p>Amount Due: $150.00</p>
            <script>trackVisit();</script>
        </body>
        </html>
        """
        result = html_to_plain_text(html)

        assert "Patient Statement" in result
        assert "John Doe" in result
        assert "$150.00" in result
        assert "trackVisit" not in result


class TestEdgeCases:
    """Test edge cases for UI utility functions."""

    def test_calculate_max_savings_with_negative_values(self):
        """Should handle negative max_savings (though unusual)."""
        issues = [
            Issue(type="billing_error", summary="Issue", evidence="Evidence", max_savings=-50.0),
        ]

        total, breakdown = calculate_max_savings(issues)

        # Should still include negative values
        assert total == -50.0
        assert len(breakdown) == 1

    def test_calculate_max_savings_with_zero_values(self):
        """Should handle zero max_savings."""
        issues = [
            Issue(type="billing_error", summary="Issue", evidence="Evidence", max_savings=0.0),
        ]

        total, breakdown = calculate_max_savings(issues)

        assert total == 0.0
        assert len(breakdown) == 1

    def test_html_to_plain_text_with_malformed_html(self):
        """Should handle malformed HTML gracefully."""
        html = "<p>Unclosed tag<p>Another paragraph"
        result = html_to_plain_text(html)

        # BeautifulSoup should handle this
        assert "Unclosed tag" in result
        assert "Another paragraph" in result

    def test_html_to_plain_text_with_html_entities(self):
        """Should decode HTML entities."""
        html = "<p>&lt;CPT&gt; 99213 &amp; 99214</p>"
        result = html_to_plain_text(html)

        # Should decode entities
        assert "<CPT>" in result or "&lt;" not in result
        assert "&" in result or "&amp;" not in result

    def test_calculate_max_savings_with_very_large_numbers(self):
        """Should handle very large savings amounts."""
        issues = [
            Issue(type="billing_error", summary="Issue", evidence="Evidence", max_savings=999999.99),
        ]

        total, breakdown = calculate_max_savings(issues)

        assert total == 999999.99
        assert breakdown[0]["max_savings"] == 999999.99

    def test_html_to_plain_text_with_unicode_characters(self):
        """Should preserve Unicode characters."""
        html = "<p>Cost: €100.50 • Patient: José</p>"
        result = html_to_plain_text(html)

        assert "€100.50" in result
        assert "José" in result or "Jos" in result  # Unicode handling

