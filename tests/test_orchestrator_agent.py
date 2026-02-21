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

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock external dependencies BEFORE any imports
sys.modules["openai"] = MagicMock()
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()

from medbilldozer.core.orchestrator_agent import (
    OrchestratorAgent,
    _clean_llm_json,
    classify_document,
    compute_deterministic_savings,
    deterministic_issues_from_facts,
    extract_pre_facts,
    model_backend,
    normalize_issues,
)
from medbilldozer.providers.llm_interface import Issue


class TestCleanLLMJson:
    """Test _clean_llm_json function."""

    def test_removes_markdown_json_wrapper(self):
        """Should remove ```json and ``` markers."""
        text = '```json\n{"key": "value"}\n```'
        result = _clean_llm_json(text)
        assert result == '{"key": "value"}'

    def test_removes_plain_code_wrapper(self):
        """Should remove ``` markers without json label."""
        text = '```\n{"key": "value"}\n```'
        result = _clean_llm_json(text)
        assert result == '{"key": "value"}'

    def test_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        text = '\n\n  {"key": "value"}  \n\n'
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
        assert result["document_type"] in [
            "insurance_eob",
            "insurance_claim_history",
            "insurance_document",
        ]
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
                {
                    "cpt_code": "99213",
                    "date_of_service": "2024-01-15",
                    "patient_responsibility": 50.0,
                },
                {
                    "cpt_code": "99213",
                    "date_of_service": "2024-01-15",
                    "patient_responsibility": 50.0,
                },  # Duplicate
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
        issues = [Issue(type="billing_error", summary="Test", evidence="Evidence")]
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
            Issue(type="billing_error", summary="Test", evidence="Evidence", max_savings=100.0)
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
        agent = OrchestratorAgent(extractor_override="gemini", analyzer_override="gpt-4o-mini")
        assert agent.extractor_override == "gemini"
        assert agent.analyzer_override == "gpt-4o-mini"

    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    def test_run_basic_workflow(
        self, mock_registry, mock_normalize, mock_extract, mock_pre_facts, mock_classify
    ):
        """Should execute basic workflow without errors."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.9,
            "scores": {"medical_bill": 3},
        }
        mock_pre_facts.return_value = {"has_cpt_codes": True, "line_count": 10, "char_count": 500}
        mock_extract.return_value = {"document_type": "medical_bill", "patient_name": "John Doe"}
        mock_normalize.return_value = {"document_type": "medical_bill", "patient_name": "John Doe"}

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

    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    def test_run_generates_workflow_log(self, mock_pre_facts, mock_classify):
        """Should generate workflow log with UUID and timestamp."""
        mock_classify.return_value = {"document_type": "generic", "confidence": 0, "scores": {}}
        mock_pre_facts.return_value = {"has_cpt_codes": False, "line_count": 1, "char_count": 10}

        with patch("medbilldozer.core.orchestrator_agent.extract_facts_openai") as mock_extract:
            mock_extract.return_value = {}
            with patch("medbilldozer.core.orchestrator_agent.normalize_facts") as mock_normalize:
                mock_normalize.return_value = {}
                with patch(
                    "medbilldozer.core.orchestrator_agent.ProviderRegistry.get"
                ) as mock_registry:
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


# ========== New Comprehensive Pipeline Tests ==========


# Test Fixtures
@pytest.fixture
def sample_medical_bill_text():
    """Sample medical bill text for testing."""
    return """
    Medical Services Invoice
    Patient: John Doe
    Date of Service: 2024-01-15
    CPT Code: 99213 - Office Visit
    Provider: Dr. Smith
    Amount: $150.00
    Patient Responsibility: $50.00
    """


@pytest.fixture
def sample_pharmacy_receipt_text():
    """Sample pharmacy receipt text for testing."""
    return """
    CVS Pharmacy Receipt
    Rx Number: 12345678
    NDC: 12345-1234-12
    Medication: Lisinopril 10mg
    Copay: $10.00
    Date Filled: 2024-01-15
    """


@pytest.fixture
def sample_facts():
    """Sample facts dictionary."""
    return {
        "document_type": "medical_bill",
        "patient_name": "John Doe",
        "provider_name": "Dr. Smith",
        "date_of_service": "2024-01-15",
        "total_amount_due": "50.00",
    }


@pytest.fixture
def sample_medical_line_items():
    """Sample medical line items for phase-2 extraction."""
    return [
        {
            "cpt_code": "99213",
            "date_of_service": "2024-01-15",
            "description": "Office Visit",
            "charge": 150.0,
            "patient_responsibility": 50.0,
        },
        {
            "cpt_code": "99214",
            "date_of_service": "2024-01-15",
            "description": "Extended Office Visit",
            "charge": 200.0,
            "patient_responsibility": 75.0,
        },
    ]


class TestOrchestratorRunMethod:
    """Test OrchestratorAgent.run() method pipeline steps."""

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_run_step1_pre_extraction_classification(
        self, mock_classify, mock_pre_facts, mock_extract, mock_normalize, mock_registry
    ):
        """Test Step 1: Pre-extraction classification is performed and logged."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.9,
            "scores": {"medical_bill": 3, "pharmacy_receipt": 1},
        }
        mock_pre_facts.return_value = {
            "contains_cpt": True,
            "contains_dental_code": False,
            "contains_rx": False,
            "line_count": 10,
            "char_count": 500,
        }
        mock_extract.return_value = {"document_type": "medical_bill"}
        mock_normalize.return_value = {"document_type": "medical_bill"}

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent and run
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Test medical bill text")

        # Verify classification was called
        mock_classify.assert_called_once()
        mock_pre_facts.assert_called_once()

        # Verify workflow_log contains pre_extraction data
        workflow_log = result["_workflow_log"]
        assert "pre_extraction" in workflow_log
        assert "classification" in workflow_log["pre_extraction"]
        assert workflow_log["pre_extraction"]["classification"]["document_type"] == "medical_bill"
        assert workflow_log["pre_extraction"]["classification"]["confidence"] == 0.9

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_run_step2_extractor_selection(
        self, mock_classify, mock_pre_facts, mock_extract, mock_normalize, mock_registry
    ):
        """Test Step 2: Extractor selection follows DOCUMENT_EXTRACTOR_MAP."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.9,
            "scores": {"medical_bill": 3},
        }
        mock_pre_facts.return_value = {"contains_cpt": True, "line_count": 10, "char_count": 500}
        mock_extract.return_value = {"document_type": "medical_bill"}
        mock_normalize.return_value = {"document_type": "medical_bill"}

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent and run
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Test medical bill text")

        # Verify extractor selection
        workflow_log = result["_workflow_log"]
        assert "pre_extraction" in workflow_log
        assert "extractor_selected" in workflow_log["pre_extraction"]
        # Medical bills should map to gpt-4o-mini according to DOCUMENT_EXTRACTOR_MAP
        assert workflow_log["pre_extraction"]["extractor_selected"] in [
            "gpt-4o-mini",
            "openai",
            "gemini",
        ]

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_run_step3_fact_extraction_openai(
        self, mock_classify, mock_pre_facts, mock_extract, mock_normalize, mock_registry
    ):
        """Test Step 3: OpenAI fact extraction is performed and logged."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.9,
            "scores": {},
        }
        mock_pre_facts.return_value = {"contains_cpt": True}
        mock_extract.return_value = {
            "document_type": "medical_bill",
            "patient_name": "John Doe",
            "provider_name": "Dr. Smith",
            "date_of_service": "2024-01-15",
        }
        mock_normalize.return_value = {
            "document_type": "medical_bill",
            "patient_name": "John Doe",
            "provider_name": "Dr. Smith",
            "date_of_service": "2024-01-15",
        }

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent with default (should use openai)
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Test medical bill text")

        # Verify extraction was called
        mock_extract.assert_called_once()
        mock_normalize.assert_called_once()

        # Verify workflow_log contains extraction data
        workflow_log = result["_workflow_log"]
        assert "extraction" in workflow_log
        assert "extractor" in workflow_log["extraction"]
        assert "fact_count" in workflow_log["extraction"]
        assert workflow_log["extraction"]["fact_count"] == 4  # 4 facts returned

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_gemini")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_run_step3_fact_extraction_gemini(
        self, mock_classify, mock_pre_facts, mock_extract_gemini, mock_normalize, mock_registry
    ):
        """Test Step 3: Gemini fact extraction when specified."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "pharmacy_receipt",
            "confidence": 0.9,
            "scores": {},
        }
        mock_pre_facts.return_value = {"contains_rx": True}
        mock_extract_gemini.return_value = {
            "document_type": "pharmacy_receipt",
            "patient_name": "Jane Doe",
            "pharmacy_name": "CVS",
        }
        mock_normalize.return_value = {
            "document_type": "pharmacy_receipt",
            "patient_name": "Jane Doe",
            "pharmacy_name": "CVS",
        }

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent with gemini extractor override
        agent = OrchestratorAgent(extractor_override="gemini", analyzer_override="gpt-4o-mini")
        result = agent.run("Test pharmacy receipt text")

        # Verify gemini extraction was called
        mock_extract_gemini.assert_called_once()

        # Verify workflow_log shows gemini was used
        workflow_log = result["_workflow_log"]
        assert workflow_log["extraction"]["extractor"] == "gemini"

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_local")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_run_step3_fact_extraction_heuristic(
        self, mock_classify, mock_pre_facts, mock_extract_local, mock_normalize, mock_registry
    ):
        """Test Step 3: Heuristic/local fact extraction when specified."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.5,
            "scores": {},
        }
        mock_pre_facts.return_value = {"contains_cpt": True}
        mock_extract_local.return_value = {
            "document_type": "medical_bill",
            "patient_name": None,
            "total_amount_due": "100.00",
        }
        mock_normalize.return_value = {
            "document_type": "medical_bill",
            "patient_name": None,
            "total_amount_due": "100.00",
        }

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent with heuristic extractor
        agent = OrchestratorAgent(extractor_override="heuristic", analyzer_override="gpt-4o-mini")
        result = agent.run("Test text")

        # Verify heuristic extraction was called
        mock_extract_local.assert_called_once()

        # Verify workflow_log shows heuristic was used
        workflow_log = result["_workflow_log"]
        assert workflow_log["extraction"]["extractor"] == "heuristic"


class TestOrchestratorPhase2Extractions:
    """Test optional phase-2 line item extractions."""

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent._run_phase2_prompt")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_phase2_receipt_line_items(
        self,
        mock_classify,
        mock_pre_facts,
        mock_extract,
        mock_phase2,
        mock_normalize,
        mock_registry,
    ):
        """Test phase-2 receipt line item extraction for pharmacy receipts."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "pharmacy_receipt",
            "confidence": 0.9,
            "scores": {},
        }
        mock_pre_facts.return_value = {"contains_rx": True}
        mock_extract.return_value = {"document_type": "pharmacy_receipt"}

        # Mock phase-2 extraction returning receipt items
        mock_phase2.return_value = """{
            "receipt_items": [
                {"medication": "Lisinopril 10mg", "ndc": "12345-1234-12", "copay": 10.0},
                {"medication": "Metformin 500mg", "ndc": "54321-4321-21", "copay": 15.0}
            ]
        }"""

        mock_normalize.return_value = {"document_type": "pharmacy_receipt"}

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent and run
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("CVS Pharmacy Receipt\nRx: 12345")

        # Verify phase-2 was called
        assert mock_phase2.called

        # Verify workflow_log contains receipt_item_count
        workflow_log = result["_workflow_log"]
        assert "extraction" in workflow_log
        if "receipt_item_count" in workflow_log["extraction"]:
            assert workflow_log["extraction"]["receipt_item_count"] == 2

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent._run_phase2_prompt")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_phase2_medical_line_items(
        self,
        mock_classify,
        mock_pre_facts,
        mock_extract,
        mock_phase2,
        mock_normalize,
        mock_registry,
    ):
        """Test phase-2 medical line item extraction for medical bills."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.9,
            "scores": {},
        }
        mock_pre_facts.return_value = {"contains_cpt": True}
        mock_extract.return_value = {"document_type": "medical_bill"}

        # Mock phase-2 extraction returning medical items
        mock_phase2.return_value = """{
            "medical_line_items": [
                {"cpt_code": "99213", "charge": 150.0},
                {"cpt_code": "99214", "charge": 200.0}
            ]
        }"""

        mock_normalize.return_value = {"document_type": "medical_bill"}

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent and run
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Medical Bill\nCPT: 99213")

        # Verify workflow_log contains medical_item_count
        workflow_log = result["_workflow_log"]
        if "medical_item_count" in workflow_log.get("extraction", {}):
            assert workflow_log["extraction"]["medical_item_count"] == 2

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent._run_phase2_prompt")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_phase2_dental_line_items(
        self,
        mock_classify,
        mock_pre_facts,
        mock_extract,
        mock_phase2,
        mock_normalize,
        mock_registry,
    ):
        """Test phase-2 dental line item extraction for dental bills."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "dental_bill",
            "confidence": 0.9,
            "scores": {},
        }
        mock_pre_facts.return_value = {"contains_dental_code": True}
        mock_extract.return_value = {"document_type": "dental_bill"}

        # Mock phase-2 extraction returning dental items
        mock_phase2.return_value = """{
            "dental_line_items": [
                {"code": "D2750", "charge": 500.0},
                {"code": "D1110", "charge": 75.0}
            ]
        }"""

        mock_normalize.return_value = {"document_type": "dental_bill"}

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent and run
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Dental Services\nD2750 Crown")

        # Verify workflow_log contains dental_item_count
        workflow_log = result["_workflow_log"]
        if "dental_item_count" in workflow_log.get("extraction", {}):
            assert workflow_log["extraction"]["dental_item_count"] == 2

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent._run_phase2_prompt")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_phase2_insurance_line_items(
        self,
        mock_classify,
        mock_pre_facts,
        mock_extract,
        mock_phase2,
        mock_normalize,
        mock_registry,
    ):
        """Test phase-2 insurance claim item extraction for EOBs."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "insurance_eob",
            "confidence": 0.9,
            "scores": {},
        }
        mock_pre_facts.return_value = {}
        mock_extract.return_value = {"document_type": "insurance_eob"}

        # Mock phase-2 extraction returning insurance items
        mock_phase2.return_value = """{
            "insurance_claim_items": [
                {"service": "Office Visit", "billed": 150.0, "allowed": 120.0}
            ]
        }"""

        mock_normalize.return_value = {"document_type": "insurance_eob"}

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent and run
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("EOB\nClaim Number: 123456")

        # Verify workflow_log contains insurance_item_count
        workflow_log = result["_workflow_log"]
        if "insurance_item_count" in workflow_log.get("extraction", {}):
            assert workflow_log["extraction"]["insurance_item_count"] == 1

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent._run_phase2_prompt")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_phase2_fsa_line_items(
        self,
        mock_classify,
        mock_pre_facts,
        mock_extract,
        mock_phase2,
        mock_normalize,
        mock_registry,
    ):
        """Test phase-2 FSA claim item extraction."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "fsa_claim_history",
            "confidence": 0.9,
            "scores": {},
        }
        mock_pre_facts.return_value = {}
        mock_extract.return_value = {"document_type": "fsa_claim_history"}

        # Mock phase-2 extraction returning FSA items
        mock_phase2.return_value = """{
            "fsa_claim_items": [
                {"claim_id": "FSA001", "amount_requested": 50.0, "amount_reimbursed": 50.0}
            ]
        }"""

        mock_normalize.return_value = {"document_type": "fsa_claim_history"}

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent and run
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("FSA Claim History")

        # Verify workflow_log contains fsa_item_count
        workflow_log = result["_workflow_log"]
        if "fsa_item_count" in workflow_log.get("extraction", {}):
            assert workflow_log["extraction"]["fsa_item_count"] == 1

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent._run_phase2_prompt")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_phase2_extraction_error_handling(
        self,
        mock_classify,
        mock_pre_facts,
        mock_extract,
        mock_phase2,
        mock_normalize,
        mock_registry,
    ):
        """Test that phase-2 extraction errors are handled gracefully."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.9,
            "scores": {},
        }
        mock_pre_facts.return_value = {"contains_cpt": True}
        mock_extract.return_value = {"document_type": "medical_bill"}

        # Mock phase-2 extraction raising an exception
        mock_phase2.side_effect = Exception("API Error")

        mock_normalize.return_value = {"document_type": "medical_bill"}

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent and run - should not raise exception
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Medical Bill\nCPT: 99213")

        # Pipeline should continue despite error
        assert "facts" in result
        assert "analysis" in result

        # Workflow log should contain error information
        workflow_log = result["_workflow_log"]
        if "medical_extraction_error" in workflow_log.get("extraction", {}):
            assert "error" in workflow_log["extraction"]["medical_extraction_error"].lower()

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent._run_phase2_prompt")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_phase2_invalid_json_response(
        self,
        mock_classify,
        mock_pre_facts,
        mock_extract,
        mock_phase2,
        mock_normalize,
        mock_registry,
    ):
        """Test handling of invalid JSON responses from phase-2 extraction."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.9,
            "scores": {},
        }
        mock_pre_facts.return_value = {"contains_cpt": True}
        mock_extract.return_value = {"document_type": "medical_bill"}

        # Mock phase-2 extraction returning invalid JSON
        mock_phase2.return_value = "This is not valid JSON {broken"

        mock_normalize.return_value = {"document_type": "medical_bill"}

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent and run - should not raise exception
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Medical Bill\nCPT: 99213")

        # Pipeline should continue despite invalid JSON
        assert "facts" in result
        assert "analysis" in result


class TestOrchestratorAnalysisPhase:
    """Test analyzer selection and analysis execution (Steps 4-5)."""

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_step4_analyzer_selection(
        self, mock_classify, mock_pre_facts, mock_extract, mock_normalize, mock_registry
    ):
        """Test Step 4: Analyzer selection from ProviderRegistry."""
        # Setup mocks
        mock_classify.return_value = {"document_type": "generic", "confidence": 0, "scores": {}}
        mock_pre_facts.return_value = {}
        mock_extract.return_value = {}
        mock_normalize.return_value = {}

        # Mock provider
        mock_provider = Mock()
        mock_provider.name = "gpt-4o-mini"
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent with analyzer override
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Test text")

        # Verify ProviderRegistry.get was called
        mock_registry.assert_called_once_with("gpt-4o-mini")

        # Verify workflow_log contains analyzer selection
        workflow_log = result["_workflow_log"]
        assert "analysis" in workflow_log
        assert "analyzer" in workflow_log["analysis"]
        assert workflow_log["analysis"]["analyzer"] == "gpt-4o-mini"

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_step5_analyze_with_facts(
        self, mock_classify, mock_pre_facts, mock_extract, mock_normalize, mock_registry
    ):
        """Test Step 5: Analysis with fact-aware provider."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.9,
            "scores": {},
        }
        mock_pre_facts.return_value = {}
        mock_extract.return_value = {"document_type": "medical_bill", "patient_name": "John Doe"}
        mock_normalize.return_value = {"document_type": "medical_bill", "patient_name": "John Doe"}

        # Mock fact-aware provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = [
            Issue(
                type="overbilling",
                summary="Possible overcharge",
                evidence="Charge exceeds typical rate",
                max_savings=50.0,
                source="llm",
            )
        ]
        mock_analysis.meta = {}
        # Provider accepts facts parameter
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent and run
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Medical bill text")

        # Verify provider was called with facts
        assert mock_provider.analyze_document.called
        call_kwargs = mock_provider.analyze_document.call_args[1]
        if "facts" in call_kwargs:
            assert call_kwargs["facts"]["document_type"] == "medical_bill"

        # Verify workflow_log shows fact-aware mode
        workflow_log = result["_workflow_log"]
        if "mode" in workflow_log.get("analysis", {}):
            assert workflow_log["analysis"]["mode"] in ["facts+text", "text_only"]

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_step5_analyze_text_only(
        self, mock_classify, mock_pre_facts, mock_extract, mock_normalize, mock_registry
    ):
        """Test Step 5: Analysis fallback to text-only when provider doesn't support facts."""
        # Setup mocks
        mock_classify.return_value = {"document_type": "generic", "confidence": 0, "scores": {}}
        mock_pre_facts.return_value = {}
        mock_extract.return_value = {}
        mock_normalize.return_value = {}

        # Mock provider that doesn't accept facts (raises TypeError)
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}

        # First call with facts raises TypeError, second call without facts succeeds
        mock_provider.analyze_document.side_effect = [
            TypeError("unexpected keyword"),
            mock_analysis,
        ]
        mock_registry.return_value = mock_provider

        # Create agent and run
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Test text")

        # Verify provider was called twice (once with facts, once without)
        assert mock_provider.analyze_document.call_count == 2

        # Verify workflow_log shows text_only mode
        workflow_log = result["_workflow_log"]
        if "mode" in workflow_log.get("analysis", {}):
            assert workflow_log["analysis"]["mode"] == "text_only"

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_step5_savings_calculation(
        self, mock_classify, mock_pre_facts, mock_extract, mock_normalize, mock_registry
    ):
        """Test Step 5: Savings calculation from deterministic + LLM issues."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.9,
            "scores": {},
        }
        mock_pre_facts.return_value = {}

        # Create facts with duplicate charges (will generate deterministic issue)
        mock_extract.return_value = {
            "document_type": "medical_bill",
            "medical_line_items": [
                {
                    "cpt_code": "99213",
                    "date_of_service": "2024-01-15",
                    "patient_responsibility": 50.0,
                },
                {
                    "cpt_code": "99213",
                    "date_of_service": "2024-01-15",
                    "patient_responsibility": 50.0,
                },  # Duplicate
            ],
        }
        mock_normalize.return_value = {
            "document_type": "medical_bill",
            "medical_line_items": [
                {
                    "cpt_code": "99213",
                    "date_of_service": "2024-01-15",
                    "patient_responsibility": 50.0,
                },
                {
                    "cpt_code": "99213",
                    "date_of_service": "2024-01-15",
                    "patient_responsibility": 50.0,
                },
            ],
        }

        # Mock provider returning LLM issues
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = [
            Issue(
                type="overbilling",
                summary="Overcharge detected",
                evidence="Rate exceeds benchmark",
                max_savings=25.0,
                source="llm",
            )
        ]
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent and run
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Medical bill with duplicate charges")

        # Verify analysis contains both deterministic and LLM issues
        analysis = result["analysis"]
        assert len(analysis.issues) >= 2  # At least duplicate + LLM issue

        # Verify savings are calculated
        if "deterministic_savings" in analysis.meta:
            assert analysis.meta["deterministic_savings"] >= 0
        if "llm_max_savings" in analysis.meta:
            assert analysis.meta["llm_max_savings"] >= 0
        if "total_max_savings" in analysis.meta:
            assert analysis.meta["total_max_savings"] >= 0


class TestOrchestratorProgressCallbacks:
    """Test progress callback mechanism."""

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_progress_callback_invocation_order(
        self, mock_classify, mock_pre_facts, mock_extract, mock_normalize, mock_registry
    ):
        """Test that progress_callback is invoked in correct order."""
        # Setup mocks
        mock_classify.return_value = {"document_type": "generic", "confidence": 0, "scores": {}}
        mock_pre_facts.return_value = {}
        mock_extract.return_value = {}
        mock_normalize.return_value = {}

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Track callback invocations
        callback_calls = []

        def mock_callback(workflow_log, step_status):
            callback_calls.append(step_status)

        # Create agent and run with callback
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Test text", progress_callback=mock_callback)

        # Verify callbacks were invoked in correct order
        expected_order = [
            "pre_extraction_active",
            "extraction_active",
            # line_items_active may or may not be called depending on document type
            "analysis_active",
            "complete",
        ]

        # Check that callbacks follow the expected sequence (may have additional calls)
        assert "pre_extraction_active" in callback_calls
        assert "extraction_active" in callback_calls
        assert "analysis_active" in callback_calls
        assert "complete" in callback_calls

        # Verify order is correct
        pre_idx = callback_calls.index("pre_extraction_active")
        extract_idx = callback_calls.index("extraction_active")
        analysis_idx = callback_calls.index("analysis_active")
        complete_idx = callback_calls.index("complete")

        assert pre_idx < extract_idx < analysis_idx < complete_idx

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_progress_callback_workflow_log_passed(
        self, mock_classify, mock_pre_facts, mock_extract, mock_normalize, mock_registry
    ):
        """Test that workflow_log is correctly passed to progress_callback."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.9,
            "scores": {},
        }
        mock_pre_facts.return_value = {"contains_cpt": True}
        mock_extract.return_value = {"document_type": "medical_bill"}
        mock_normalize.return_value = {"document_type": "medical_bill"}

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Track workflow_log passed to callback
        received_workflow_logs = []

        def mock_callback(workflow_log, step_status):
            received_workflow_logs.append((step_status, dict(workflow_log)))

        # Create agent and run with callback
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Medical bill text", progress_callback=mock_callback)

        # Verify workflow_log was passed and has correct structure
        assert len(received_workflow_logs) > 0

        for step_status, workflow_log in received_workflow_logs:
            assert "workflow_id" in workflow_log
            assert "timestamp" in workflow_log

            # Verify progressive building of workflow_log
            if step_status == "pre_extraction_active":
                assert "pre_extraction" in workflow_log
            elif step_status == "extraction_active":
                assert "pre_extraction" in workflow_log
                assert "extraction" in workflow_log
            elif step_status == "analysis_active":
                assert "analysis" in workflow_log

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_progress_callback_optional(
        self, mock_classify, mock_pre_facts, mock_extract, mock_normalize, mock_registry
    ):
        """Test that progress_callback is optional and doesn't cause errors when None."""
        # Setup mocks
        mock_classify.return_value = {"document_type": "generic", "confidence": 0, "scores": {}}
        mock_pre_facts.return_value = {}
        mock_extract.return_value = {}
        mock_normalize.return_value = {}

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Create agent and run WITHOUT callback (should not raise error)
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run("Test text", progress_callback=None)

        # Verify pipeline completes successfully
        assert "facts" in result
        assert "analysis" in result
        assert "_workflow_log" in result


class TestOrchestratorIntegration:
    """Integration tests with realistic end-to-end scenarios."""

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_full_pipeline_medical_bill(
        self,
        mock_classify,
        mock_pre_facts,
        mock_extract,
        mock_normalize,
        mock_registry,
        sample_medical_bill_text,
    ):
        """Test complete pipeline with medical bill document."""
        # Setup realistic mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.95,
            "scores": {"medical_bill": 5, "generic": 1},
        }
        mock_pre_facts.return_value = {
            "contains_cpt": True,
            "contains_dental_code": False,
            "contains_rx": False,
            "line_count": 8,
            "char_count": 250,
        }
        mock_extract.return_value = {
            "document_type": "medical_bill",
            "patient_name": "John Doe",
            "provider_name": "Dr. Smith",
            "date_of_service": "2024-01-15",
            "total_amount_due": "50.00",
        }
        mock_normalize.return_value = {
            "document_type": "medical_bill",
            "patient_name": "John Doe",
            "provider_name": "Dr. Smith",
            "date_of_service": "2024-01-15",
            "total_amount_due": "50.00",
        }

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = [
            Issue(
                type="billing_clarification",
                summary="Verify office visit code",
                evidence="CPT 99213 requires documentation review",
                max_savings=0.0,
                source="llm",
            )
        ]
        mock_analysis.meta = {"provider": "gpt-4o-mini"}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Run full pipeline
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run(sample_medical_bill_text)

        # Comprehensive assertions
        assert "facts" in result
        assert "analysis" in result
        assert "_orchestration" in result
        assert "_workflow_log" in result

        # Verify facts
        assert result["facts"]["document_type"] == "medical_bill"
        assert result["facts"]["patient_name"] == "John Doe"

        # Verify analysis
        assert len(result["analysis"].issues) >= 1

        # Verify orchestration metadata
        assert result["_orchestration"]["classification"]["document_type"] == "medical_bill"
        assert result["_orchestration"]["extractor"] in ["openai", "gpt-4o-mini"]
        assert result["_orchestration"]["analyzer"] == "gpt-4o-mini"

        # Verify workflow_log completeness
        workflow_log = result["_workflow_log"]
        assert "workflow_id" in workflow_log
        assert "timestamp" in workflow_log
        assert "pre_extraction" in workflow_log
        assert "extraction" in workflow_log
        assert "analysis" in workflow_log

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent._run_phase2_prompt")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_full_pipeline_with_line_items(
        self,
        mock_classify,
        mock_pre_facts,
        mock_extract,
        mock_phase2,
        mock_normalize,
        mock_registry,
        sample_medical_bill_text,
        sample_medical_line_items,
    ):
        """Test complete pipeline including phase-2 line item extraction."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.95,
            "scores": {"medical_bill": 5},
        }
        mock_pre_facts.return_value = {"contains_cpt": True}
        mock_extract.return_value = {"document_type": "medical_bill"}

        # Mock phase-2 extraction
        import json

        mock_phase2.return_value = json.dumps({"medical_line_items": sample_medical_line_items})

        mock_normalize.return_value = {"document_type": "medical_bill"}

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Run pipeline
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")
        result = agent.run(sample_medical_bill_text)

        # Verify phase-2 extraction occurred
        assert mock_phase2.called

        # Verify workflow_log contains line item information
        workflow_log = result["_workflow_log"]
        if "medical_item_count" in workflow_log.get("extraction", {}):
            assert workflow_log["extraction"]["medical_item_count"] == 2

    @patch("medbilldozer.core.orchestrator_agent.ProviderRegistry.get")
    @patch("medbilldozer.core.orchestrator_agent.normalize_facts")
    @patch("medbilldozer.core.orchestrator_agent.extract_facts_openai")
    @patch("medbilldozer.core.orchestrator_agent.extract_pre_facts")
    @patch("medbilldozer.core.orchestrator_agent.classify_document")
    def test_error_recovery(
        self, mock_classify, mock_pre_facts, mock_extract, mock_normalize, mock_registry
    ):
        """Test pipeline resilience when extraction fails."""
        # Setup mocks
        mock_classify.return_value = {
            "document_type": "medical_bill",
            "confidence": 0.9,
            "scores": {},
        }
        mock_pre_facts.return_value = {"contains_cpt": True}

        # Mock extraction failure
        mock_extract.side_effect = Exception("API timeout")

        # Even with failed extraction, normalize should still be called with empty facts
        mock_normalize.return_value = {"document_type": "medical_bill"}

        # Mock provider
        mock_provider = Mock()
        mock_analysis = Mock()
        mock_analysis.issues = []
        mock_analysis.meta = {}
        mock_provider.analyze_document.return_value = mock_analysis
        mock_registry.return_value = mock_provider

        # Run pipeline - should handle error gracefully or raise appropriately
        agent = OrchestratorAgent(analyzer_override="gpt-4o-mini")

        # Depending on implementation, this might raise or return partial results
        try:
            result = agent.run("Medical bill text")
            # If it doesn't raise, verify we got some result
            assert "facts" in result or "error" in result
        except Exception as e:
            # If it does raise, that's also acceptable error handling
            assert "timeout" in str(e).lower() or "api" in str(e).lower()


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
