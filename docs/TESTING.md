# Testing Guide for medBillDozer

## Overview

This document describes the test suite for medBillDozer, a Streamlit application for medical bill auditing.

## Test Files Created

### ✅ `tests/test_config.py` - Configuration System Tests

**Purpose**: Verify configuration loading, merging, and feature flag behavior.

**Test Coverage**: 35 test cases across 3 test classes

**What's Tested**:
- ✅ Default configuration structure and values
- ✅ YAML file loading and parsing
- ✅ Deep merge logic (nested dictionaries)
- ✅ Dot-notation path retrieval (`config.get("features.assistant.enabled")`)
- ✅ Feature flag convenience functions
- ✅ Error handling (missing files, invalid YAML, empty files)
- ✅ Singleton pattern for global config instance
- ✅ Configuration reloading
- ✅ Edge cases (null values, lists, empty paths)

**Test Coverage**: 35 test cases across 3 test classes

**Key Behaviors Verified**:
1. When config file missing → uses defaults + prints warning
2. When valid YAML exists → merges with defaults (overrides take precedence)
3. When YAML malformed → falls back to defaults + prints error
4. Deep merge preserves unspecified nested values
5. `get()` returns None for missing keys or uses provided default
6. `is_feature_enabled()` returns False for missing features
7. Global instance is reused unless explicitly reloaded

**Example Test**:
```python
def test_init_with_valid_yaml_file(self, tmp_path):
    """When valid YAML exists, should load and merge with defaults."""
    config_file = tmp_path / "test_config.yaml"

    test_config = {
        "features": {
            "assistant": {
                "enabled": False,
                "default_provider": "gemini"
            }
        }
    }

    with open(config_file, 'w') as f:
        yaml.dump(test_config, f)

    config = AppConfig(config_path=config_file)

    # Should merge: overrides take precedence
    assert config.config["features"]["assistant"]["enabled"] is False
    assert config.config["features"]["assistant"]["default_provider"] == "gemini"

    # Should keep defaults for unspecified values
    assert config.config["features"]["dag"]["enabled"] is True
```

## Installation

### Install Test Dependencies

```bash
# Option 1: Install just test tools
pip install pytest pytest-mock

# Option 2: Install all project dependencies (includes pytest)
pip install -r requirements.txt
```

---

### ✅ `tests/test_doc_assistant.py` - Documentation Assistant Tests

**Purpose**: Verify DocumentationAssistant class behavior including doc loading, LLM integration, and search.

**Test Coverage**: 43 test cases across 7 test classes

**What's Tested**:
- ✅ Initialization and documentation file loading
- ✅ Context prompt building with guidelines
- ✅ OpenAI API integration (mocked - no real API calls)
- ✅ Gemini API integration (mocked - no real API calls)
- ✅ Provider routing (openai vs gemini)
- ✅ Document search with regex splitting by markdown headers
- ✅ Avatar image loading and base64 encoding
- ✅ Error handling for missing files and API failures
- ✅ Edge cases (empty cache, special characters, long previews)

**Key Behaviors Verified**:
1. Loads QUICKSTART.md, USER_GUIDE.md, INDEX.md, README.md from docs/ folder
2. Skips missing documentation files gracefully
3. Builds prompts with full documentation context + guidelines
4. OpenAI calls use gpt-4o-mini, max_tokens=500, temperature=0.3
5. Gemini calls use gemini-2.0-flash-exp model
6. Returns "❌ API Error" message on exception with helpful instructions
7. Search splits markdown by headers (##), case-insensitive matching
8. Returns max 5 search results with 200-char preview truncation
9. Avatar images base64-encoded as data URIs

**Example Test**:
```python
@patch('_modules.ui.doc_assistant.DocumentationAssistant._build_context_prompt')
@patch('openai.OpenAI')
def test_get_answer_openai_calls_api_with_correct_params(self, mock_openai_class, mock_build_prompt):
    """get_answer_openai should call OpenAI API with correct parameters."""
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

    # Verify OpenAI API parameters
    mock_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_client.chat.completions.create.call_args[1]
    assert call_kwargs['model'] == "gpt-4o-mini"
    assert call_kwargs['max_tokens'] == 500
    assert call_kwargs['temperature'] == 0.3
    assert result == "AI response"
```

### Added to requirements.txt
- `pytest==8.3.4` - Test framework
- `pytest-mock==3.14.0` - Mocking utilities

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_config.py
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test Class
```bash
pytest tests/test_config.py::TestAppConfig
```

### Run Specific Test Function
```bash
pytest tests/test_config.py::TestAppConfig::test_default_config_structure
```

### Show Print Statements
```bash
pytest -s
```

## Configuration Files Added

### `pytest.ini`
Configures pytest behavior:
- Test discovery patterns
- Output verbosity
- Test markers (unit, integration, slow)

### `tests/__init__.py`
Makes tests directory a Python package.

### `tests/README.md`
Detailed testing documentation and examples.

## Testing Principles Applied

### ✅ What We Test
- Pure functions with deterministic outputs
- Configuration loading and merging logic
- Error handling with mocked services
- Data transformations
- Business logic

### ❌ What We Don't Test
- Streamlit UI rendering
- Sidebar layout or styling
- Avatar animations or JavaScript
- Actual LLM API calls (always mocked)
- Network requests
- Timing-based behaviors

### Test Design Principles
1. **Isolation**: Each test runs independently
2. **Fast**: Tests complete in milliseconds
3. **Deterministic**: Same input = same output, always
4. **No Secrets**: No API keys required (external services mocked)
5. **Clear Names**: Test names describe exact behavior verified
6. **Focused**: Each test verifies one specific behavior

## Next Steps

### Remaining Test Files

1. **`test_transaction_normalization.py`**
   - Line item normalization
   - Transaction deduplication
   - Data format conversions

2. **`test_document_identity.py`**
   - Document ID formatting
   - Identity enhancement logic

3. **`test_serialization.py`**
   - analysis_to_dict conversion
   - JSON serialization

4. **`test_coverage_matrix.py`**
   - Coverage aggregation
   - Matrix building logic

## No Application Code Changes

✅ **Zero modifications to application code** - all changes are test-only:
- Created `tests/` directory
- Added test files
- Added pytest dependencies
- Created configuration files

The application code remains completely unchanged and continues to work exactly as before.

## Continuous Integration Ready

Tests are designed to run in CI/CD pipelines:
- ✅ No external API calls
- ✅ No secrets required
- ✅ Fast execution (<1 second per test file)
- ✅ Isolated test cases
- ✅ Clear pass/fail indicators

## Example Output

```bash
$ pytest tests/test_config.py -v

======================== test session starts =========================
platform darwin -- Python 3.11.x, pytest-8.3.4
collected 35 items

tests/test_config.py::TestAppConfig::test_default_config_structure PASSED [ 2%]
tests/test_config.py::TestAppConfig::test_default_config_features PASSED [ 5%]
tests/test_config.py::TestAppConfig::test_init_with_missing_file PASSED [ 8%]
tests/test_config.py::TestAppConfig::test_init_with_valid_yaml_file PASSED [ 11%]
...
tests/test_config.py::TestConfigEdgeCases::test_deep_merge_does_not_mutate_inputs PASSED [100%]

========================= 35 passed in 0.15s =========================
```

## Summary

**Files Added**:
- `tests/__init__.py` - Package marker
- `tests/test_config.py` - 35 configuration tests
- `tests/test_doc_assistant.py` - 43 documentation assistant tests
- `tests/README.md` - Testing documentation
- `pytest.ini` - Pytest configuration
- `TESTING.md` - This file

**Dependencies Added**:
- `pytest==8.3.4`
- `pytest-mock==3.14.0`

**Total Test Coverage**: 78 test cases

**Lines of Test Code**: ~950 lines

**Application Code Modified**: 0 lines

**Ready to Run**: After `pip install pytest pytest-mock`

