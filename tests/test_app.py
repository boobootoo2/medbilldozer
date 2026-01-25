"""Tests for main application module (app.py).

Tests verify:
- ENGINE_OPTIONS dictionary structure
- render_total_savings_summary display logic
- Provider registration side effects
- Bootstrap UI initialization

Note: Main workflow (main function) not tested due to Streamlit dependencies.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import sys

# Mock streamlit and external dependencies
streamlit_mock = MagicMock()
streamlit_mock.session_state = {}
streamlit_mock.components = MagicMock()
streamlit_mock.components.v1 = MagicMock()
sys.modules['streamlit'] = streamlit_mock
sys.modules['streamlit.components'] = streamlit_mock.components
sys.modules['streamlit.components.v1'] = streamlit_mock.components.v1
sys.modules['openai'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['anthropic'] = MagicMock()


from app import (
    ENGINE_OPTIONS,
    render_total_savings_summary,
    bootstrap_ui_minimal,
    bootstrap_home_page,
    register_providers,
)


class TestEngineOptions:
    """Test ENGINE_OPTIONS configuration dictionary."""
    
    def test_engine_options_is_dict(self):
        """ENGINE_OPTIONS should be a dictionary."""
        assert isinstance(ENGINE_OPTIONS, dict)
    
    def test_has_smart_recommended_option(self):
        """Should have 'Smart (Recommended)' option."""
        assert "Smart (Recommended)" in ENGINE_OPTIONS
    
    def test_smart_recommended_maps_to_none(self):
        """Smart option should map to None (auto-select)."""
        assert ENGINE_OPTIONS["Smart (Recommended)"] is None
    
    def test_has_gpt_4o_mini_option(self):
        """Should have gpt-4o-mini option."""
        assert "gpt-4o-mini" in ENGINE_OPTIONS
        assert ENGINE_OPTIONS["gpt-4o-mini"] == "gpt-4o-mini"
    
    def test_has_gemini_option(self):
        """Should have gemini flash preview option."""
        assert "gemini-3-flash-preview" in ENGINE_OPTIONS
        assert ENGINE_OPTIONS["gemini-3-flash-preview"] == "gemini-3-flash-preview"
    
    def test_has_local_offline_option(self):
        """Should have Local (Offline) option."""
        assert "Local (Offline)" in ENGINE_OPTIONS
        assert ENGINE_OPTIONS["Local (Offline)"] == "heuristic"
    
    def test_has_exactly_four_options(self):
        """Should have exactly 4 engine options."""
        assert len(ENGINE_OPTIONS) == 4
    
    def test_all_values_are_strings_or_none(self):
        """All engine values should be strings or None."""
        for key, value in ENGINE_OPTIONS.items():
            assert value is None or isinstance(value, str), \
                f"Expected string or None for {key}, got {type(value)}"


class TestRenderTotalSavingsSummary:
    """Test render_total_savings_summary display logic."""
    
    def setup_method(self):
        """Reset streamlit mock before each test."""
        streamlit_mock.reset_mock()
        streamlit_mock.markdown = MagicMock()
        streamlit_mock.metric = MagicMock()
        streamlit_mock.expander = MagicMock()
    
    def test_does_not_render_when_savings_zero(self):
        """Should not render anything when savings is zero."""
        per_doc = {"doc1": 0.0}
        
        render_total_savings_summary(0.0, per_doc)
        
        # Should return early without rendering
        streamlit_mock.markdown.assert_not_called()
        streamlit_mock.metric.assert_not_called()
    
    def test_does_not_render_when_savings_negative(self):
        """Should not render when savings is negative."""
        per_doc = {"doc1": -50.0}
        
        render_total_savings_summary(-50.0, per_doc)
        
        streamlit_mock.markdown.assert_not_called()
        streamlit_mock.metric.assert_not_called()
    
    def test_renders_markdown_header_for_positive_savings(self):
        """Should render markdown header when savings > 0."""
        per_doc = {"doc1": 100.0}
        
        render_total_savings_summary(100.0, per_doc)
        
        # Should call markdown with header
        calls = streamlit_mock.markdown.call_args_list
        assert any("💰" in str(call) for call in calls)
        assert any("Total Potential Savings" in str(call) for call in calls)
    
    def test_renders_metric_with_formatted_amount(self):
        """Should render metric with properly formatted amount."""
        per_doc = {"doc1": 1234.56}
        
        render_total_savings_summary(1234.56, per_doc)
        
        # Should call metric with formatted value
        streamlit_mock.metric.assert_called_once()
        call_kwargs = streamlit_mock.metric.call_args[1]
        assert "$1,234.56" in call_kwargs["value"]
    
    def test_renders_large_amounts_with_commas(self):
        """Should format large amounts with thousand separators."""
        per_doc = {"doc1": 1000000.00}
        
        render_total_savings_summary(1000000.00, per_doc)
        
        call_kwargs = streamlit_mock.metric.call_args[1]
        assert "$1,000,000.00" in call_kwargs["value"]
    
    def test_renders_expander_for_per_document_breakdown(self):
        """Should create expander with document breakdown."""
        per_doc = {"doc1": 50.0, "doc2": 75.0}
        
        # Mock expander context manager
        expander_ctx = MagicMock()
        streamlit_mock.expander.return_value.__enter__ = MagicMock(return_value=expander_ctx)
        streamlit_mock.expander.return_value.__exit__ = MagicMock(return_value=False)
        
        render_total_savings_summary(125.0, per_doc)
        
        # Should call expander
        streamlit_mock.expander.assert_called_once()
        assert "savings by document" in str(streamlit_mock.expander.call_args)
    
    def test_formats_per_document_amounts(self):
        """Should format each document's savings amount."""
        per_doc = {
            "document_1": 123.45,
            "document_2": 678.90,
        }
        
        render_total_savings_summary(802.35, per_doc)
        
        # Should call markdown for each document
        markdown_calls = streamlit_mock.markdown.call_args_list
        # Filter calls that look like per-document entries
        doc_calls = [str(c) for c in markdown_calls if "$" in str(c) and "document_" in str(c)]
        assert len(doc_calls) >= 2
    
    def test_handles_empty_per_document_dict(self):
        """Should handle empty per_document_savings dict."""
        per_doc = {}
        
        # Should not crash
        render_total_savings_summary(100.0, per_doc)
        
        # Should still render header and metric
        streamlit_mock.markdown.assert_called()
        streamlit_mock.metric.assert_called()
    
    def test_handles_single_document(self):
        """Should work with single document."""
        per_doc = {"single_doc": 42.99}
        
        render_total_savings_summary(42.99, per_doc)
        
        streamlit_mock.metric.assert_called_once()
        call_kwargs = streamlit_mock.metric.call_args[1]
        assert "$42.99" in call_kwargs["value"]


class TestBootstrapUi:
    """Test bootstrap UI initialization."""
    
    @patch('app.setup_page')
    @patch('app.inject_css')
    @patch('app.render_header')
    def test_bootstrap_ui_minimal_calls_setup_functions(
        self, mock_header, mock_css, mock_setup
    ):
        """Should call minimal UI setup functions in correct order."""
        bootstrap_ui_minimal()
        
        # Verify all functions called
        mock_setup.assert_called_once()
        mock_css.assert_called_once()
        mock_header.assert_called_once()
    
    @patch('app.setup_page')
    @patch('app.inject_css')
    @patch('app.render_header')
    def test_bootstrap_ui_minimal_calls_setup_page_first(
        self, mock_header, mock_css, mock_setup
    ):
        """setup_page should be called before other UI functions."""
        call_order = []
        mock_setup.side_effect = lambda: call_order.append('setup')
        mock_css.side_effect = lambda: call_order.append('css')
        mock_header.side_effect = lambda: call_order.append('header')
        
        bootstrap_ui_minimal()
        
        assert call_order == ['setup', 'css', 'header']
    
    @patch('app.should_enable_guided_tour', return_value=False)
    @patch('app.render_contextual_help')
    @patch('app.render_demo_documents')
    def test_bootstrap_home_page_calls_home_functions(
        self, mock_demo, mock_help, mock_tour
    ):
        """Should call home page functions when guided tour is not active."""
        bootstrap_home_page()
        
        mock_help.assert_called_once_with('demo')
        mock_demo.assert_called_once()
    
    @patch('app.should_enable_guided_tour', return_value=True)
    @patch('app.render_contextual_help')
    @patch('app.render_demo_documents')
    def test_bootstrap_home_page_skips_help_on_guided_tour(
        self, mock_demo, mock_help, mock_tour
    ):
        """Should skip contextual help when guided tour is active."""
        bootstrap_home_page()
        
        mock_help.assert_not_called()
        mock_demo.assert_called_once()


class TestRegisterProviders:
    """Test provider registration logic."""
    
    @patch('app.ProviderRegistry.register')
    @patch('app.OpenAIAnalysisProvider')
    @patch('app.GeminiAnalysisProvider')
    def test_attempts_to_register_openai_provider(
        self, mock_gemini_class, mock_openai_class, mock_register
    ):
        """Should attempt to register OpenAI provider."""
        # Mock successful health check
        mock_openai_provider = MagicMock()
        mock_openai_provider.health_check.return_value = True
        mock_openai_class.return_value = mock_openai_provider
        
        mock_gemini_provider = MagicMock()
        mock_gemini_provider.health_check.return_value = False
        mock_gemini_class.return_value = mock_gemini_provider
        
        register_providers()
        
        # Should create OpenAI provider with correct model
        mock_openai_class.assert_called_once_with("gpt-4o-mini")
    
    @patch('app.ProviderRegistry.register')
    @patch('app.OpenAIAnalysisProvider')
    @patch('app.GeminiAnalysisProvider')
    def test_registers_openai_provider_when_health_check_passes(
        self, mock_gemini_class, mock_openai_class, mock_register
    ):
        """Should register OpenAI provider when health check succeeds."""
        # Mock successful health check
        mock_openai_provider = MagicMock()
        mock_openai_provider.health_check.return_value = True
        mock_openai_class.return_value = mock_openai_provider
        
        mock_gemini_provider = MagicMock()
        mock_gemini_provider.health_check.return_value = False
        mock_gemini_class.return_value = mock_gemini_provider
        
        register_providers()
        
        # Should register OpenAI provider
        calls = mock_register.call_args_list
        openai_calls = [c for c in calls if 'gpt' in str(c)]
        assert len(openai_calls) >= 1
    
    @patch('app.ProviderRegistry.register')
    @patch('app.OpenAIAnalysisProvider')
    @patch('app.GeminiAnalysisProvider')
    def test_does_not_register_openai_when_health_check_fails(
        self, mock_gemini_class, mock_openai_class, mock_register
    ):
        """Should not register OpenAI provider when health check fails."""
        # Mock failed health check
        mock_openai_provider = MagicMock()
        mock_openai_provider.health_check.return_value = False
        mock_openai_class.return_value = mock_openai_provider
        
        mock_gemini_provider = MagicMock()
        mock_gemini_provider.health_check.return_value = False
        mock_gemini_class.return_value = mock_gemini_provider
        
        register_providers()
        
        # Should not register OpenAI provider
        calls = mock_register.call_args_list
        openai_calls = [c for c in calls if 'gpt' in str(c)]
        assert len(openai_calls) == 0
    
    @patch('app.ProviderRegistry.register')
    @patch('app.OpenAIAnalysisProvider')
    @patch('app.GeminiAnalysisProvider')
    def test_attempts_to_register_gemini_provider(
        self, mock_gemini_class, mock_openai_class, mock_register
    ):
        """Should attempt to register Gemini provider."""
        # Mock successful health check
        mock_gemini_provider = MagicMock()
        mock_gemini_provider.health_check.return_value = True
        mock_gemini_class.return_value = mock_gemini_provider
        
        mock_openai_provider = MagicMock()
        mock_openai_provider.health_check.return_value = False
        mock_openai_class.return_value = mock_openai_provider
        
        register_providers()
        
        # Should create Gemini provider with correct model
        mock_gemini_class.assert_called_once_with("gemini-1.5-flash")
    
    @patch('app.ProviderRegistry.register')
    @patch('app.OpenAIAnalysisProvider')
    @patch('app.GeminiAnalysisProvider')
    def test_continues_registration_if_one_provider_fails(
        self, mock_gemini_class, mock_openai_class, mock_register
    ):
        """Should continue registering other providers if one fails."""
        # Make OpenAI raise exception
        mock_openai_class.side_effect = Exception("OpenAI API key missing")
        
        # Make Gemini succeed
        mock_gemini_provider = MagicMock()
        mock_gemini_provider.health_check.return_value = True
        mock_gemini_class.return_value = mock_gemini_provider
        
        # Should not crash
        register_providers()
        
        # Gemini should still be registered
        calls = mock_register.call_args_list
        gemini_calls = [c for c in calls if 'gemini' in str(c)]
        assert len(gemini_calls) >= 1
    
    @patch('app.ProviderRegistry.register')
    @patch('app.OpenAIAnalysisProvider')
    @patch('app.GeminiAnalysisProvider')
    @patch('app.MedGemmaHostedProvider', None)
    def test_handles_missing_medgemma_provider_gracefully(
        self, mock_gemini_class, mock_openai_class, mock_register
    ):
        """Should handle MedGemma provider being None (not available)."""
        # Mock other providers
        mock_gemini_provider = MagicMock()
        mock_gemini_provider.health_check.return_value = True
        mock_gemini_class.return_value = mock_gemini_provider
        
        mock_openai_provider = MagicMock()
        mock_openai_provider.health_check.return_value = True
        mock_openai_class.return_value = mock_openai_provider
        
        # Should not crash
        register_providers()
        
        # Other providers should still be registered
        assert mock_register.call_count >= 1


class TestEngineOptionsIntegration:
    """Integration tests for ENGINE_OPTIONS usage."""
    
    def test_engine_options_keys_are_user_friendly(self):
        """Engine option keys should be user-friendly display names."""
        # Most keys should be user-friendly (with spaces/parentheses)
        # But model names like "gpt-4o-mini" are also acceptable
        user_friendly_count = sum(1 for key in ENGINE_OPTIONS.keys() if " " in key or "(" in key)
        assert user_friendly_count >= 2, "Should have at least 2 user-friendly option names"
    
    def test_engine_options_values_match_provider_names(self):
        """Engine option values should match provider registry names."""
        # Get non-None values
        provider_names = [v for v in ENGINE_OPTIONS.values() if v is not None]
        
        # Should have recognizable provider names
        valid_providers = ["gpt-4o-mini", "gemini-3-flash-preview", "heuristic"]
        for name in provider_names:
            assert name in valid_providers, f"Unknown provider: {name}"
    
    def test_heuristic_option_exists_for_offline_mode(self):
        """Should have heuristic option for offline usage."""
        heuristic_options = [k for k, v in ENGINE_OPTIONS.items() if v == "heuristic"]
        assert len(heuristic_options) == 1
        assert "Offline" in heuristic_options[0] or "Local" in heuristic_options[0]
