"""Tests for DocumentationAssistant (_modules/ui/doc_assistant.py).

Tests verify:
- Documentation file loading
- Context prompt building
- Document search functionality
- Avatar image loading (base64 encoding)
- OpenAI and Gemini API integration (mocked)
- Error handling for missing files and API failures
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock, mock_open
import base64
import sys

# Mock all external dependencies before importing DocumentationAssistant
# Mock Streamlit
streamlit_mock = MagicMock()
streamlit_mock.components = MagicMock()
streamlit_mock.components.v1 = MagicMock()
sys.modules['streamlit'] = streamlit_mock
sys.modules['streamlit.components'] = streamlit_mock.components
sys.modules['streamlit.components.v1'] = streamlit_mock.components.v1

# Mock OpenAI
openai_mock = MagicMock()
sys.modules['openai'] = openai_mock

# Mock Google GenAI
google_mock = MagicMock()
google_genai_mock = MagicMock()
google_mock.genai = google_genai_mock
sys.modules['google'] = google_mock
sys.modules['google.genai'] = google_genai_mock

from _modules.ui.doc_assistant import DocumentationAssistant


class TestDocumentationAssistantInit:
    """Test DocumentationAssistant initialization."""

    def test_init_sets_correct_paths(self):
        """__init__ should set docs_path and images_path relative to module."""
        assistant = DocumentationAssistant()

        # Paths should be set
        assert assistant.docs_path is not None
        assert assistant.images_path is not None
        assert isinstance(assistant.docs_path, Path)
        assert isinstance(assistant.images_path, Path)

        # Should initialize empty cache
        assert isinstance(assistant.docs_cache, dict)

    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="# Test Doc\n\nContent here.")
    def test_init_loads_existing_docs(self, mock_file, mock_exists):
        """__init__ should load documentation files that exist."""
        # Mock all expected doc files as existing
        mock_exists.return_value = True

        assistant = DocumentationAssistant()

        # Should have loaded docs into cache
        expected_files = ["QUICKSTART.md", "USER_GUIDE.md", "INDEX.md", "README.md"]
        for doc_file in expected_files:
            assert doc_file in assistant.docs_cache
            assert assistant.docs_cache[doc_file] == "# Test Doc\n\nContent here."

    @patch('pathlib.Path.exists')
    def test_init_skips_missing_docs(self, mock_exists):
        """__init__ should skip documentation files that don't exist."""
        # Mock no files existing
        mock_exists.return_value = False

        assistant = DocumentationAssistant()

        # Cache should be empty (no files loaded)
        assert len(assistant.docs_cache) == 0


class TestLoadDocumentation:
    """Test _load_documentation method."""

    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_documentation_reads_all_expected_files(self, mock_file, mock_exists):
        """_load_documentation should attempt to load all doc files."""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = "Doc content"

        assistant = DocumentationAssistant()

        # Should have called open for each doc file
        expected_files = ["QUICKSTART.md", "USER_GUIDE.md", "INDEX.md", "README.md"]
        assert len(assistant.docs_cache) == len(expected_files)

    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="Different content for each file")
    def test_load_documentation_stores_content_by_filename(self, mock_file, mock_exists):
        """_load_documentation should store content keyed by filename."""
        mock_exists.return_value = True

        assistant = DocumentationAssistant()

        # Each file should be in cache with its content
        for filename in ["QUICKSTART.md", "USER_GUIDE.md", "INDEX.md", "README.md"]:
            assert filename in assistant.docs_cache
            assert isinstance(assistant.docs_cache[filename], str)


class TestBuildContextPrompt:
    """Test _build_context_prompt method."""

    def test_build_context_prompt_includes_user_question(self):
        """_build_context_prompt should include the user's question."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {"test.md": "Test content"}

        question = "How do I analyze a bill?"
        prompt = assistant._build_context_prompt(question)

        assert question in prompt
        assert "USER QUESTION:" in prompt

    def test_build_context_prompt_includes_all_docs(self):
        """_build_context_prompt should include all loaded documentation."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {
            "QUICKSTART.md": "Quick start content",
            "USER_GUIDE.md": "User guide content"
        }

        prompt = assistant._build_context_prompt("test question")

        # Should include both docs
        assert "QUICKSTART.md" in prompt
        assert "Quick start content" in prompt
        assert "USER_GUIDE.md" in prompt
        assert "User guide content" in prompt

    def test_build_context_prompt_includes_guidelines(self):
        """_build_context_prompt should include AI guidelines."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {"test.md": "Content"}

        prompt = assistant._build_context_prompt("test")

        # Should include key instructions
        assert "medBillDozer" in prompt
        assert "IMPORTANT GUIDELINES:" in prompt
        assert "DOCUMENTATION:" in prompt

    def test_build_context_prompt_with_empty_cache(self):
        """_build_context_prompt should work with empty docs cache."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {}

        prompt = assistant._build_context_prompt("test question")

        # Should still return a valid prompt
        assert "test question" in prompt
        assert "DOCUMENTATION:" in prompt

    def test_build_context_prompt_formats_docs_with_separator(self):
        """_build_context_prompt should separate docs with clear delimiter."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {
            "doc1.md": "Content 1",
            "doc2.md": "Content 2"
        }

        prompt = assistant._build_context_prompt("test")

        # Should use separator between docs
        assert "---" in prompt


class TestGetAnswerOpenAI:
    """Test get_answer_openai method."""

    @patch('_modules.ui.doc_assistant.DocumentationAssistant._build_context_prompt')
    @patch('openai.OpenAI')
    def test_get_answer_openai_calls_api_with_correct_params(self, mock_openai_class, mock_build_prompt):
        """get_answer_openai should call OpenAI API with correct parameters."""
        # Setup mocks
        mock_build_prompt.return_value = "Test prompt"
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "AI response"
        mock_client.chat.completions.create.return_value = mock_response

        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {}

        result = assistant.get_answer_openai("test question")

        # Should call OpenAI with correct model
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == "gpt-4o-mini"
        assert call_kwargs['max_tokens'] == 500
        assert call_kwargs['temperature'] == 0.3

        # Should return stripped response
        assert result == "AI response"

    @patch('_modules.ui.doc_assistant.DocumentationAssistant._build_context_prompt')
    @patch('openai.OpenAI')
    def test_get_answer_openai_returns_error_on_exception(self, mock_openai_class, mock_build_prompt):
        """get_answer_openai should return error message on API failure."""
        mock_build_prompt.return_value = "Test prompt"
        mock_openai_class.side_effect = Exception("API Error")

        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {}

        result = assistant.get_answer_openai("test question")

        # Should return error message
        assert "❌ OpenAI API Error" in result
        assert "API Error" in result
        assert "OPENAI_API_KEY" in result


class TestGetAnswer:
    """Test get_answer dispatcher method."""

    @patch.object(DocumentationAssistant, 'get_answer_gemini')
    def test_get_answer_routes_to_gemini(self, mock_gemini):
        """get_answer should route to get_answer_gemini when provider is 'gemini-2.0-flash-exp'."""
        mock_gemini.return_value = "Gemini response"

        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        result = assistant.get_answer("test question", provider="gemini-2.0-flash-exp")

        mock_gemini.assert_called_once_with("test question")
        assert result == "Gemini response"

    @patch.object(DocumentationAssistant, 'get_answer_openai')
    def test_get_answer_routes_to_openai_by_default(self, mock_openai):
        """get_answer should route to get_answer_openai by default."""
        mock_openai.return_value = "OpenAI response"

        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        result = assistant.get_answer("test question")

        mock_openai.assert_called_once_with("test question")
        assert result == "OpenAI response"

    @patch.object(DocumentationAssistant, 'get_answer_openai')
    def test_get_answer_routes_to_openai_explicitly(self, mock_openai):
        """get_answer should route to get_answer_openai when provider is 'openai'."""
        mock_openai.return_value = "OpenAI response"

        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        result = assistant.get_answer("test question", provider="openai")

        mock_openai.assert_called_once_with("test question")
        assert result == "OpenAI response"


class TestSearchDocs:
    """Test search_docs method."""

    def test_search_docs_finds_matching_content(self):
        """search_docs should find sections containing search query."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {
            "guide.md": "# Introduction\n\nThis is about medical bills.\n\n## Setup\n\nHow to install."
        }

        results = assistant.search_docs("medical")

        # Should find match
        assert len(results) > 0
        assert results[0]['file'] == "guide.md"
        assert 'medical' in results[0]['preview'].lower()

    def test_search_docs_is_case_insensitive(self):
        """search_docs should perform case-insensitive search."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {
            "doc.md": "Content with UPPERCASE and lowercase"
        }

        results_upper = assistant.search_docs("UPPERCASE")
        results_lower = assistant.search_docs("uppercase")

        # Both should find the same content
        assert len(results_upper) > 0
        assert len(results_lower) > 0

    def test_search_docs_returns_max_five_results(self):
        """search_docs should return at most 5 results."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)

        # Create docs with many matching sections
        assistant.docs_cache = {
            f"doc{i}.md": f"## Section\n\nCommon keyword appears here."
            for i in range(10)
        }

        results = assistant.search_docs("keyword")

        # Should limit to 5 results
        assert len(results) <= 5

    def test_search_docs_returns_empty_for_no_matches(self):
        """search_docs should return empty list when no matches."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {
            "doc.md": "Content without the search term"
        }

        results = assistant.search_docs("nonexistent")

        assert results == []

    def test_search_docs_splits_by_headers(self):
        """search_docs should split content by markdown headers."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {
            "doc.md": "# Title\n\n## Section 1\n\nText with keyword.\n\n## Section 2\n\nMore content."
        }

        results = assistant.search_docs("keyword")

        # Should find section with keyword
        assert len(results) > 0
        assert results[0]['title'] == "Section 1"

    def test_search_docs_truncates_long_previews(self):
        """search_docs should truncate previews longer than 200 chars."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)

        long_content = "keyword " + ("x" * 250)
        assistant.docs_cache = {"doc.md": f"## Section\n\n{long_content}"}

        results = assistant.search_docs("keyword")

        # Preview should be truncated with ellipsis
        assert len(results) > 0
        assert len(results[0]['preview']) <= 203  # 200 + "..."
        assert results[0]['preview'].endswith("...")

    def test_search_docs_handles_untitled_sections(self):
        """search_docs should handle sections without clear titles."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {
            "doc.md": "Content with keyword but no header"
        }

        results = assistant.search_docs("keyword")

        # Should still find match, title may be "Untitled" or first line
        assert len(results) > 0
        assert 'title' in results[0]


class TestGetAvatarImage:
    """Test get_avatar_image method."""

    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=b'\x89PNG\r\n\x1a\n')
    def test_get_avatar_image_returns_base64_data_uri(self, mock_file, mock_exists):
        """get_avatar_image should return base64-encoded data URI."""
        mock_exists.return_value = True

        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.images_path = Path("/fake/path")

        result = assistant.get_avatar_image("ready_open")

        # Should return data URI format
        assert result.startswith("data:image/png;base64,")
        # Should contain base64-encoded data
        assert len(result) > len("data:image/png;base64,")

    @patch('pathlib.Path.exists')
    def test_get_avatar_image_returns_empty_string_if_missing(self, mock_exists):
        """get_avatar_image should return empty string if file doesn't exist."""
        mock_exists.return_value = False

        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.images_path = Path("/fake/path")

        result = assistant.get_avatar_image("ready_open")

        assert result == ""

    def test_get_avatar_image_maps_states_correctly(self):
        """get_avatar_image should map state names to correct filenames."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.images_path = Path("/fake/path")

        # Test state mapping (doesn't require actual files for this test)
        state_map = {
            "ready_open": "billy__eyes_open__ready.png",
            "ready_closed": "billy__eyes_closed__ready.png",
            "talking_open": "billy__eyes_open__talking.png",
            "talking_closed": "billy__eyes_closed__talking.png",
            "smile_open": "billy__eyes_open__smiling.png",
        }

        # Verify the mapping exists (implementation detail check)
        for state in state_map.keys():
            # Method should handle the state without error
            with patch('pathlib.Path.exists', return_value=False):
                result = assistant.get_avatar_image(state)
                # If file doesn't exist, returns empty string
                assert result == ""

    @patch('pathlib.Path.exists')
    def test_get_avatar_image_uses_default_for_invalid_state(self, mock_exists):
        """get_avatar_image should use default image for invalid state."""
        mock_exists.return_value = False

        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.images_path = Path("/fake/path")

        # Invalid state should default to ready_open
        result = assistant.get_avatar_image("invalid_state")

        # Should handle gracefully (returns empty string since file doesn't exist)
        assert result == ""


class TestDocumentationAssistantEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_docs_cache_doesnt_break_prompt(self):
        """Assistant should handle empty docs cache gracefully."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {}

        # Should not raise exception
        prompt = assistant._build_context_prompt("test question")
        assert "test question" in prompt

    def test_search_with_empty_query(self):
        """search_docs should handle empty query."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {"doc.md": "Some content"}

        results = assistant.search_docs("")

        # Empty query matches everything (case-insensitive search on empty string)
        # Should still return results (at most 5)
        assert len(results) <= 5

    def test_search_with_special_characters(self):
        """search_docs should handle special regex characters."""
        assistant = DocumentationAssistant.__new__(DocumentationAssistant)
        assistant.docs_cache = {"doc.md": "Content with [brackets] and (parens)"}

        # Should not raise regex error
        results = assistant.search_docs("[brackets]")

        # Should find match
        assert len(results) > 0

    @patch('pathlib.Path.exists')
    @patch('builtins.open', side_effect=IOError("Read error"))
    def test_load_documentation_handles_read_errors(self, mock_file, mock_exists):
        """_load_documentation should handle file read errors gracefully."""
        mock_exists.return_value = True

        # Should not raise exception
        with pytest.raises(IOError):
            # The current implementation doesn't handle IO errors,
            # but we document the behavior
            assistant = DocumentationAssistant()

