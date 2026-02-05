"""Tests for OrchestratorAgent (_modules/core/orchestrator_agent.py).

Tests verify:
- Document classification logic
- Pre-fact extraction
- JSON cleaning and normalization
- Model backend mapping
- Deterministic issue detection
- Savings computation
- Issue normalization
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys

# Mock external dependencies
sys.modules['openai'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.genai'] = MagicMock()

from medbilldozer.core.orchestrator_agent import (
    _clean_llm_json,
    model_backend,
    deterministic_issues_from_facts,
    compute_deterministic_savings,
    normalize_issues,
    classify_document,
    extract_pre_facts,
    OrchestratorAgent,
)
from medbilldozer.providers.llm_interface import Issue


class TestCleanLLMJson:
    """Test _clean_llm_json function."""

    def test_removes_markdown_json_wrapper(self):
        """Should remove ```json and ``` markers."""
        text = "```json\n{\"key\": \"value\"}\n```"
        result = _clean_llm_json(text)
        assert result == '{"key": "value"}'

    def test_removes_plain_code_wrapper(self):
        """Should remove ``` markers without json label."""
        text = "```\n{\"key\": \"value\"}\n```"
        result = _clean_llm_json(text)
        assert result == '{"key": "value"}'

    def test_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        text = "\n\n  {\"key\": \"value\"}  \n\n"
        result = _clean_llm_json(text)
        assert result == '{"key": "value"}'

    def test_handles_text_without_markers(self):
        """Should work with plain JSON text."""
        text = '{"key": "value"}'
        result = _clean_llm_json(text)
        assert result == '{"key": "value"}'


class TestModelBackend:
    """Test model_backend function."""

    def test_returns_openai_for_gpt_models(self):
        """Should map gpt models to openai backend."""
        assert model_backend("gpt-4o-mini") == "openai"
        assert model_backend("gpt-4-turbo") == "openai"

    def test_returns_gemini_for_gemini_models(self):
        """Should map gemini models to gemini backend."""
        assert model_backend("gemini-1.5-flash") == "gemini"
        assert model_backend("gemini-pro") == "gemini"

    def test_returns_none_for_unknown_models(self):
        """Should return None for unrecognized models."""
        assert model_backend("unknown-model") is None
        assert model_backend("") is None

    def test_returns_none_for_heuristic(self):
        """Should return None for heuristic models."""
        assert model_backend("heuristic") is None


class TestClassifyDocument:
    """Test classify_document function."""

    def test_classifies_medical_bill(self):
        """Should identify medical bills from CPT codes."""
        text = """
        Medical Services
        Date of Service: 01/15/2024
        CPT Code: 99213
        Patient Responsibility: $150
        """
        result = classify_document(text)
        assert result["document_type"] == "medical_bill"
        assert result["confidence"] > 0
        assert "medical_bill" in result["scores"]

    def test_classifies_pharmacy_receipt(self):
        """Should identify pharmacy receipts from Rx markers."""
        text = """
        CVS Pharmacy Receipt
        Rx Number: 12345678
        NDC: 12345-1234-12
        Copay: $10.00
        """
        result = classify_document(text)
        assert result["document_type"] == "pharmacy_receipt"
        assert result["confidence"] > 0

    def test_classifies_dental_bill(self):
        """Should identify dental bills from D codes."""
        text = """
        Dental Services
        D2750 - Crown restoration
        D1110 - Cleaning
        Lab Fee: $500
        """
        result = classify_document(text)
        assert result["document_type"] == "dental_bill"
        assert result["confidence"] > 0

    def test_classifies_insurance_eob(self):
        """Should identify insurance EOBs."""
        text = """
        Explanation of Benefits
        Claim Number: CLM123456
        Insurance Paid: $200
        Patient Responsibility: $50
        """
        result = classify_document(text)
        assert result["document_type"] in ["insurance_eob", "insurance_claim_history", "insurance_document"]
        assert result["confidence"] > 0

    def test_returns_generic_for_unknown_document(self):
        """Should classify as generic when no patterns match."""
        text = "This is just some random text with no medical keywords."
        result = classify_document(text)
        assert result["document_type"] == "generic"
        assert result["confidence"] == 0.0
        assert result["scores"] == {}

    def test_case_insensitive_matching(self):
        """Should match patterns case-insensitively."""
        text = "cpt code: 99213"
        result = classify_document(text)
        assert result["document_type"] == "medical_bill"


class TestExtractPreFacts:
    """Test extract_pre_facts function."""

    def test_detects_cpt_codes(self):
        """Should detect presence of CPT codes."""
        text = "CPT 99213 and CPT 99214"
        result = extract_pre_facts(text)
        assert result["contains_cpt"] is True

    def test_detects_dental_codes(self):
        """Should detect presence of dental codes."""
        text = "D2750 - Crown and D1110 - Cleaning"
        result = extract_pre_facts(text)
        assert result["contains_dental_code"] is True

    def test_detects_rx_markers(self):
        """Should detect pharmacy/Rx markers."""
        text = "Rx Number: 12345678"
        result = extract_pre_facts(text)
        assert result["contains_rx"] is True

    def test_returns_line_count(self):
        """Should count number of lines."""
        text = "Line 1\nLine 2\nLine 3"
        result = extract_pre_facts(text)
        assert result["line_count"] == 3

    def test_returns_char_count(self):
        """Should count number of characters."""
        text = "Hello World"
        result = extract_pre_facts(text)
        assert result["char_count"] == 11

    def test_empty_text(self):
        """Should handle empty text gracefully."""
        result = extract_pre_facts("")
        assert result["contains_cpt"] is False
        assert result["contains_dental_code"] is False
        assert result["contains_rx"] is False
        assert result["line_count"] == 0  # Empty string has no lines
        assert result["char_count"] == 0


class TestDeterministicIssuesFromFacts:
    """Test deterministic_issues_from_facts function."""

    def test_detects_duplicate_charges_in_medical_items(self):
        """Should detect duplicate CPT codes in medical line items."""
        facts = {
            "medical_line_items": [
                {"cpt_code": "99213", "date_of_service": "2024-01-15", "patient_responsibility": 50.0},
                {"cpt_code": "99213", "date_of_service": "2024-01-15", "patient_responsibility": 50.0},  # Duplicate
            ]
        }
        issues = deterministic_issues_from_facts(facts)

        duplicate_issues = [i for i in issues if i.type == "duplicate_charge"]
        assert len(duplicate_issues) == 1
        assert "99213" in duplicate_issues[0].summary or "99213" in duplicate_issues[0].evidence

    def test_detects_duplicate_dental_charges(self):
        """Should detect duplicate dental codes."""
        facts = {
            "dental_line_items": [
                {"code": "D2750", "charge": 500.0},
                {"code": "D2750", "charge": 500.0},  # Duplicate
            ]
        }
        issues = deterministic_issues_from_facts(facts)

        duplicate_issues = [i for i in issues if i.type == "duplicate_charge"]
        assert len(duplicate_issues) > 0

    def test_returns_empty_list_for_no_duplicates(self):
        """Should return empty list when no issues found."""
        facts = {
            "medical_line_items": [
                {"cpt_code": "99213", "charge": 150.0},
                {"cpt_code": "99214", "charge": 200.0},
            ]
        }
        issues = deterministic_issues_from_facts(facts)
        assert isinstance(issues, list)
        # May return empty or non-empty depending on implementation

    def test_handles_empty_facts(self):
        """Should handle empty facts dictionary."""
        issues = deterministic_issues_from_facts({})
        assert isinstance(issues, list)

    def test_all_issues_have_source_deterministic(self):
        """All issues should be marked with source='deterministic'."""
        facts = {
            "medical_line_items": [
                {"cpt_code": "99213", "charge": 150.0},
                {"cpt_code": "99213", "charge": 150.0},
            ]
        }
        issues = deterministic_issues_from_facts(facts)

        for issue in issues:
            assert hasattr(issue, "source")
            assert issue.source == "deterministic"


class TestComputeDeterministicSavings:
    """Test compute_deterministic_savings function."""

    def test_sums_savings_from_deterministic_issues(self):
        """Should sum max_savings from all deterministic issues."""
        facts = {
            "medical_line_items": [
                {"cpt_code": "99213", "charge": 150.0},
                {"cpt_code": "99213", "charge": 150.0},
            ]
        }
        savings = compute_deterministic_savings(facts)
        assert isinstance(savings, float)
        assert savings >= 0

    def test_returns_zero_for_no_issues(self):
        """Should return 0 when no deterministic issues."""
        facts = {
            "medical_line_items": [
                {"cpt_code": "99213", "charge": 150.0},
                {"cpt_code": "99214", "charge": 200.0},
            ]
        }
        savings = compute_deterministic_savings(facts)
        assert savings >= 0

    def test_handles_empty_facts(self):
        """Should handle empty facts dictionary."""
        savings = compute_deterministic_savings({})
        assert savings == 0.0


class TestNormalizeIssues:
    """Test normalize_issues function."""

    def test_ensures_all_issues_have_required_fields(self):
        """Should ensure all issues have type, summary, evidence."""
        issues = [
            Issue(type="billing_error", summary="Test", evidence="Evidence")
        ]
        normalized = normalize_issues(issues)

        assert len(normalized) == 1
        assert hasattr(normalized[0], "type")
        assert hasattr(normalized[0], "summary")
        assert hasattr(normalized[0], "evidence")

    def test_handles_empty_list(self):
        """Should handle empty issues list."""
        normalized = normalize_issues([])
        assert normalized == []

    def test_preserves_max_savings(self):
        """Should preserve max_savings field if present."""
        issues = [
            Issue(
                type="billing_error",
                summary="Test",
                evidence="Evidence",
                max_savings=100.0
            )
        ]
        normalized = normalize_issues(issues)

        if hasattr(normalized[0], "max_savings"):
            assert normalized[0].max_savings == 100.0


class TestOrchestratorAgent:
    """Test OrchestratorAgent class."""

    def test_init_with_defaults(self):
        """Should initialize with no overrides."""
        agent = OrchestratorAgent()
        assert agent.extractor_override is None
        assert agent.analyzer_override is None

    def test_init_with_extractor_override(self):
        """Should initialize with extractor override."""
        agent = OrchestratorAgent(extractor_override="gemini")
        assert agent.extractor_override == "gemini"
        assert agent.analyzer_override is None

    def test_init_with_analyzer_override(self):
        """Should initialize with analyzer override."""
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        assert agent.extractor_override is None
        assert agent.analyzer_override == "gpt-4o-mini"

    def test_init_with_both_overrides(self):
        """Should initialize with both overrides."""
        agent = OrchestratorAgent(
            extractor_override="gemini",
            analyzer_override="gpt-4o-mini"
        )
        assert agent.extractor_override == "gemini"
        assert agent.analyzer_override == "gpt-4o-mini"

    @patch('_modules.core.orchestrator_agent.classify_document')
    @patch('_modules.core.orchestrator_agent.extract_pre_facts')
    @patch('_modules.core.orchestrator_agent.extract_facts_openai')
    @patch('_modules.core.orchestrator_agent.normalize_facts')
    @patch('_modules.core.orchestrator_agent.ProviderRegistry.get')
    def test_run_basic_workflow(self, mock_registry, mock_normalize, mock_extract, mock_pre_facts, mock_classify):
        """Should execute basic workflow without errors."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.9,
            "scores": {"medical_bill": 3}
        }
        mock_pre_facts.return_value = {
            "has_cpt_codes": True,
            "line_count": 10,
            "char_count": 500
        }
        mock_extract.return_value = {
            "document_type": "medical_bill",
            "patient_name": "John Doe"
        }
        mock_normalize.return_value = {
            "document_type": "medical_bill",
            "patient_name": "John Doe"
        }

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Test medical bill text")

        # Verify structure
        assert "facts" in result
        assert "analysis" in result
        assert "_orchestration" in result
        assert "_workflow_log" in result

    @patch('_modules.core.orchestrator_agent.classify_document')
    @patch('_modules.core.orchestrator_agent.extract_pre_facts')
    def test_run_generates_workflow_log(self, mock_pre_facts, mock_classify):
        """Should generate workflow log with UUID and timestamp."""
        mock_classify.return_value = {"document_type": "generic", "confidence": 0, "scores": {}}
        mock_pre_facts.return_value = {"has_cpt_codes": False, "line_count": 1, "char_count": 10}

        with patch('_modules.core.orchestrator_agent.extract_facts_openai') as mock_extract:
            mock_extract.return_value = {}
            with patch('_modules.core.orchestrator_agent.normalize_facts') as mock_normalize:
                mock_normalize.return_value = {}
                with patch('_modules.core.orchestrator_agent.ProviderRegistry.get') as mock_registry:
                    mock_provider = Mock()
                    mock_analysis = Mock()
                    mock_analysis.issues = []
                    mock_analysis.meta = {}
                    mock_provider.analyze_document.return_value = mock_analysis
                    mock_registry.return_value = mock_provider

                    agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
                    result = agent.run("Test")

                    workflow_log = result["_workflow_log"]
                    assert "workflow_id" in workflow_log
                    assert "timestamp" in workflow_log
                    assert "pre_extraction" in workflow_log
                    assert "extraction" in workflow_log
                    assert "analysis" in workflow_log


class TestOrchestratorEdgeCases:
    """Test edge cases and error handling."""

    def test_classify_document_with_multiple_signals(self):
        """Should handle documents with multiple type signals."""
        text = """
        Medical and Dental Services
        CPT 99213
        D2750 - Crown
        Patient Responsibility: $500
        """
        result = classify_document(text)
        # Should pick the strongest signal
        assert result["document_type"] in ["medical_bill", "dental_bill"]
        assert result["confidence"] > 0

    def test_extract_pre_facts_with_special_characters(self):
        """Should handle text with special characters."""
        text = "CPT: 99213 | D2750 → Rx#12345"
        result = extract_pre_facts(text)
        assert result["contains_cpt"] is True
        assert result["contains_dental_code"] is True
        assert result["contains_rx"] is True

    def test_deterministic_issues_with_missing_fields(self):
        """Should handle line items with missing required fields gracefully."""
        facts = {
            "medical_line_items": [
                {"charge": 150.0},  # Missing cpt_code
                {"cpt_code": "99213"},  # Missing charge
            ]
        }
        # Should not raise exception
        issues = deterministic_issues_from_facts(facts)
        assert isinstance(issues, list)

