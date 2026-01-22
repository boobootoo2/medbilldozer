# Test Suite for medBillDozer

This directory contains pytest-based unit tests for the medBillDozer application.

## Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-mock
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

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

### Run with Coverage

```bash
pip install pytest-cov
pytest --cov=_modules --cov-report=html
```

## Test Structure

- `test_config.py` - Configuration system tests (AppConfig, feature flags, YAML loading)
- *(More test files to be added)*

## Testing Principles

### What We Test
- ✅ Pure functions (deterministic logic)
- ✅ Data transformations and normalization
- ✅ Configuration loading and merging
- ✅ Error handling with mocked external services
- ✅ Business logic in orchestrator and analysis modules

### What We Don't Test
- ❌ Streamlit UI rendering
- ❌ Sidebar layout or components
- ❌ Avatar animations or JavaScript
- ❌ Actual LLM API calls (always mocked)
- ❌ Network requests
- ❌ Timing-based behaviors

## Writing New Tests

1. **Name test files**: `test_<module>.py`
2. **Name test classes**: `Test<ClassName>`
3. **Name test functions**: `test_<behavior_description>`
4. **Use descriptive docstrings**: Explain what behavior is verified
5. **Mock external services**: Never make real API calls
6. **Keep tests fast**: Each test file should run in <1 second

### Example Test Structure

```python
"""Tests for module_name.

Tests verify:
- Specific behavior 1
- Specific behavior 2
- Error handling for case X
"""

import pytest
from unittest.mock import patch, Mock
from _modules.path.to.module import function_to_test


class TestFunctionName:
    """Test function_name behavior."""
    
    def test_normal_case(self):
        """function_name should return X when given Y."""
        result = function_to_test(input_data)
        assert result == expected_output
    
    def test_edge_case(self):
        """function_name should handle edge case Z."""
        result = function_to_test(edge_case_input)
        assert result is not None
    
    @patch('module.external_service')
    def test_with_mocked_dependency(self, mock_service):
        """function_name should work with mocked external service."""
        mock_service.return_value = "mocked_response"
        result = function_to_test()
        assert result == "expected_result"
```

## Continuous Integration

Tests run automatically in GitHub Actions. All tests must pass before merging.

No API keys or secrets required - external services are mocked.

## Current Test Coverage

### Completed
- [x] Configuration system (`test_config.py`)
  - Default configuration loading
  - YAML file loading and merging
  - Deep merge logic
  - Dot-notation path retrieval
  - Feature flag checks
  - Error handling (missing/invalid files)

### Planned
- [ ] Documentation Assistant (`test_doc_assistant.py`)
- [ ] Transaction Normalization (`test_transaction_normalization.py`)
- [ ] Document Identity (`test_document_identity.py`)
- [ ] Serialization (`test_serialization.py`)
- [ ] Coverage Matrix (`test_coverage_matrix.py`)
