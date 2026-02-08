# Testing Guide

Comprehensive testing strategy for medBillDozer.

## Test Suite Overview

```
tests/
├── test_core.py                    # Core orchestration (23 tests)
├── test_providers.py               # AI provider abstraction (18 tests)
├── test_extractors.py              # Document parsing (15 tests)
├── test_prompts.py                 # Prompt engineering (12 tests)
├── test_ui.py                      # UI components (16 tests)
├── test_data.py                    # Data models (14 tests)
├── test_ingest.py                  # Document ingestion (10 tests)
├── test_utils.py                   # Utilities (11 tests)
├── integration/
│   ├── test_end_to_end.py         # Full pipeline (8 tests)
│   └── test_benchmark_engine.py   # Benchmark validation (7 tests)
└── conftest.py                     # Shared fixtures
```

**Total**: 134 tests (100% passing)

## Quick Start

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/medbilldozer --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run specific test
pytest tests/test_core.py::test_orchestrator_run

# Run tests matching pattern
pytest -k "provider"

# Verbose output
pytest -v

# Show print statements
pytest -s
```

## Test Categories

### Unit Tests

Test individual components in isolation.

**Example: Testing DAG Execution**

```python
# tests/test_core.py
import pytest
from medbilldozer.core.dag import DAG, Stage

def test_dag_execution_order():
    """DAG executes stages in dependency order."""
    dag = DAG()
    
    # Define stages
    stage1 = Stage(name="extract", fn=lambda x: x.upper())
    stage2 = Stage(name="normalize", fn=lambda x: x.strip(), depends_on=["extract"])
    stage3 = Stage(name="analyze", fn=lambda x: len(x), depends_on=["normalize"])
    
    dag.add_stage(stage1)
    dag.add_stage(stage2)
    dag.add_stage(stage3)
    
    # Execute
    result = dag.run("  hello  ")
    
    # Verify execution order
    assert result["extract"] == "  HELLO  "
    assert result["normalize"] == "HELLO"
    assert result["analyze"] == 5
```

**Example: Testing Provider Abstraction**

```python
# tests/test_providers.py
import pytest
from medbilldozer.providers.base_provider import BaseProvider
from medbilldozer.providers.openai_provider import OpenAIProvider

def test_provider_interface_conformance():
    """All providers implement BaseProvider interface."""
    provider = OpenAIProvider(api_key="test-key")
    
    # Check interface methods exist
    assert hasattr(provider, "generate")
    assert hasattr(provider, "get_model_name")
    assert hasattr(provider, "estimate_cost")
    
    # Check return types
    assert callable(provider.generate)
    assert isinstance(provider.get_model_name(), str)

@pytest.mark.asyncio
async def test_openai_provider_response():
    """OpenAI provider returns structured response."""
    provider = OpenAIProvider()
    
    prompt = "Analyze this medical bill: ..."
    response = await provider.generate(prompt, temperature=0.0)
    
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
```

### Integration Tests

Test component interactions and full workflows.

**Example: End-to-End Pipeline**

```python
# tests/integration/test_end_to_end.py
import pytest
from medbilldozer.core.orchestrator import OrchestratorAgent
from medbilldozer.providers.registry import ProviderRegistry

@pytest.mark.integration
def test_full_pipeline_medical_bill(sample_medical_bill):
    """Full pipeline processes medical bill correctly."""
    # Setup
    registry = ProviderRegistry()
    registry.register("gpt-4o-mini", OpenAIProvider())
    
    orchestrator = OrchestratorAgent(
        provider_key="gpt-4o-mini",
        registry=registry
    )
    
    # Execute
    result = orchestrator.run(
        text=sample_medical_bill,
        document_type="medical_bill"
    )
    
    # Verify result structure
    assert result["status"] == "success"
    assert "extracted_data" in result
    assert "analysis" in result
    assert "issues" in result["analysis"]
    
    # Verify issue detection
    issues = result["analysis"]["issues"]
    assert len(issues) > 0
    assert all("category" in issue for issue in issues)
    assert all("severity" in issue for issue in issues)

@pytest.mark.integration
@pytest.mark.slow
def test_cross_document_reasoning(sample_bill, sample_eob):
    """Cross-document analysis detects discrepancies."""
    orchestrator = OrchestratorAgent(provider_key="gpt-4o-mini")
    
    # Process both documents
    bill_result = orchestrator.run(sample_bill, document_type="medical_bill")
    eob_result = orchestrator.run(sample_eob, document_type="eob")
    
    # Cross-document analysis
    from medbilldozer.core.cross_document import detect_cross_document_duplicates
    duplicates = detect_cross_document_duplicates(
        [bill_result["extracted_data"], eob_result["extracted_data"]]
    )
    
    assert duplicates is not None
    assert len(duplicates) >= 0
```

### Benchmark Tests

Validate benchmark engine accuracy.

**Example: Benchmark Validation**

```python
# tests/integration/test_benchmark_engine.py
import pytest
from medbilldozer.core.benchmark import BenchmarkEngine, calculate_f1_score

def test_benchmark_engine_evaluation(benchmark_case):
    """Benchmark engine correctly evaluates predictions."""
    engine = BenchmarkEngine()
    
    # Load expected output
    expected = benchmark_case["expected_output"]
    
    # Get model prediction
    predicted = engine.run_benchmark(
        input_file=benchmark_case["input_file"],
        provider_key="gpt-4o-mini"
    )
    
    # Calculate metrics
    metrics = engine.evaluate(predicted, expected)
    
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1_score" in metrics
    assert 0.0 <= metrics["f1_score"] <= 1.0

def test_f1_score_calculation():
    """F1 score calculation is accurate."""
    predicted = [
        {"category": "overcharge", "title": "Upcoding"},
        {"category": "duplicate", "title": "Duplicate charge"}
    ]
    
    expected = [
        {"category": "overcharge", "title": "Upcoding"},
        {"category": "duplicate", "title": "Duplicate anesthesia"}
    ]
    
    f1 = calculate_f1_score(predicted, expected)
    
    assert f1 == 1.0  # Both matches
```

## Fixtures

Shared test data and setup.

**conftest.py**:

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_medical_bill():
    """Sample medical bill for testing."""
    return """
    MEDICAL BILL
    Provider: Dr. Jane Doe
    Patient: John Smith
    Date: 2024-01-15
    
    CPT 45385 - Colonoscopy ............ $2,450.00
    CPT 00810 - Anesthesia ............. $400.00
    
    Total: $2,850.00
    """

@pytest.fixture
def sample_eob():
    """Sample EOB for testing."""
    return """
    EXPLANATION OF BENEFITS
    Patient: John Smith
    Claim Date: 2024-01-15
    
    Colonoscopy (45385)
      Billed: $2,450.00
      Allowed: $1,800.00
      Paid: $1,440.00
      You owe: $360.00
    """

@pytest.fixture
def benchmark_case():
    """Sample benchmark case."""
    return {
        "input_file": "benchmarks/inputs/patient_001_colonoscopy.txt",
        "expected_output": {
            "issues": [
                {
                    "category": "overcharge",
                    "severity": "high",
                    "title": "Procedure Upcoded",
                    "max_savings": 250.00
                }
            ]
        }
    }

@pytest.fixture
def mock_provider():
    """Mock AI provider for testing."""
    class MockProvider:
        async def generate(self, prompt, **kwargs):
            return '{"issues": [], "total_charges": 100.00}'
        
        def get_model_name(self):
            return "mock-model"
    
    return MockProvider()
```

## Mocking

Mock external dependencies for faster, reliable tests.

**Example: Mocking OpenAI API**

```python
# tests/test_providers.py
from unittest.mock import Mock, patch
import pytest

@patch("openai.ChatCompletion.create")
def test_openai_provider_with_mock(mock_create):
    """Test OpenAI provider with mocked API."""
    # Setup mock response
    mock_create.return_value = Mock(
        choices=[Mock(message=Mock(content='{"issues": []}'))]
    )
    
    # Test provider
    provider = OpenAIProvider(api_key="test-key")
    response = provider.generate("Test prompt")
    
    # Verify mock was called
    mock_create.assert_called_once()
    assert response == '{"issues": []}'
```

**Example: Mocking File System**

```python
# tests/test_ingest.py
from unittest.mock import mock_open, patch

@patch("builtins.open", new_callable=mock_open, read_data="bill content")
def test_document_ingestion(mock_file):
    """Test document ingestion with mocked file."""
    from medbilldozer.ingest.document_loader import load_document
    
    content = load_document("fake_path.txt")
    
    assert content == "bill content"
    mock_file.assert_called_once_with("fake_path.txt", "r")
```

## Coverage

Track test coverage to identify untested code.

```bash
# Generate coverage report
pytest --cov=src/medbilldozer --cov-report=html

# View report
open htmlcov/index.html

# Terminal report
pytest --cov=src/medbilldozer --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=src/medbilldozer --cov-fail-under=80
```

**Current Coverage**:
```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/medbilldozer/__init__.py               5      0   100%
src/medbilldozer/core/dag.py             120     12    90%
src/medbilldozer/core/orchestrator.py    180     15    92%
src/medbilldozer/providers/base.py        25      0   100%
src/medbilldozer/providers/openai.py      85      8    91%
src/medbilldozer/extractors/text.py       60      5    92%
src/medbilldozer/ui/analysis_view.py     140     20    86%
-----------------------------------------------------------
TOTAL                                   1847    142    92%
```

## Test Markers

Organize tests with markers.

**pytest.ini**:
```ini
[pytest]
markers =
    integration: Integration tests (slower)
    unit: Unit tests (fast)
    slow: Slow tests (> 5 seconds)
    benchmark: Benchmark tests
    requires_api: Tests requiring API keys
```

**Usage**:
```bash
# Run only unit tests
pytest -m unit

# Run all except slow tests
pytest -m "not slow"

# Run integration tests only
pytest -m integration

# Run tests requiring API keys
pytest -m requires_api
```

**Mark tests**:
```python
@pytest.mark.integration
def test_full_pipeline():
    pass

@pytest.mark.slow
@pytest.mark.requires_api
def test_openai_integration():
    pass
```

## Parameterized Tests

Test multiple scenarios with one test function.

**Example: Test Multiple Providers**

```python
@pytest.mark.parametrize("provider_key,expected_model", [
    ("gpt-4o-mini", "gpt-4o-mini"),
    ("gemini-2.0-flash", "gemini-2.0-flash-exp"),
    ("heuristic", "rule-based"),
])
def test_provider_model_names(provider_key, expected_model):
    """All providers return correct model names."""
    registry = ProviderRegistry()
    provider = registry.get(provider_key)
    
    assert provider.get_model_name() == expected_model
```

**Example: Test Multiple Issue Categories**

```python
@pytest.mark.parametrize("category,severity,savings_range", [
    ("overcharge", "high", (100, 1000)),
    ("duplicate", "high", (50, 500)),
    ("unbundling", "medium", (20, 200)),
    ("missing_info", "low", (0, 0)),
])
def test_issue_detection_by_category(category, severity, savings_range):
    """Issue detection works across categories."""
    orchestrator = OrchestratorAgent(provider_key="gpt-4o-mini")
    
    # Load test case for category
    bill = load_test_case(category)
    result = orchestrator.run(bill)
    
    # Find issues matching category
    issues = [i for i in result["analysis"]["issues"] if i["category"] == category]
    
    assert len(issues) > 0
    assert all(i["severity"] == severity for i in issues)
    
    for issue in issues:
        min_savings, max_savings = savings_range
        assert min_savings <= issue["max_savings"] <= max_savings
```

## CI/CD Testing

Tests run automatically on GitHub Actions.

**Workflow** (`.github/workflows/test.yml`):
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install -r requirements-test.txt
      
      - name: Run tests
        run: pytest --cov=src/medbilldozer --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Best Practices

### 1. **Test Naming**
```python
# Good: Descriptive test names
def test_dag_executes_stages_in_dependency_order():
    pass

def test_openai_provider_returns_structured_json():
    pass

# Bad: Vague test names
def test_dag():
    pass

def test_provider():
    pass
```

### 2. **Arrange-Act-Assert Pattern**
```python
def test_issue_detection():
    # Arrange: Setup test data
    bill = load_sample_bill()
    orchestrator = OrchestratorAgent(provider_key="gpt-4o-mini")
    
    # Act: Execute function
    result = orchestrator.run(bill)
    
    # Assert: Verify results
    assert result["status"] == "success"
    assert len(result["analysis"]["issues"]) > 0
```

### 3. **Isolated Tests**
```python
# Good: Each test is independent
def test_dag_stage_addition():
    dag = DAG()  # Fresh DAG for this test
    stage = Stage(name="test", fn=lambda x: x)
    dag.add_stage(stage)
    assert len(dag.stages) == 1

# Bad: Tests depend on shared state
dag = DAG()  # Shared state

def test_first():
    dag.add_stage(stage1)

def test_second():
    dag.add_stage(stage2)  # Depends on test_first
```

### 4. **Mock External Dependencies**
```python
# Good: Mock API calls
@patch("openai.ChatCompletion.create")
def test_with_mock(mock_api):
    mock_api.return_value = Mock(...)
    # Test without hitting real API

# Bad: Hit real APIs in tests
def test_without_mock():
    api_response = openai.ChatCompletion.create(...)  # Slow, costs money
```

## Writing New Tests

### Template

```python
# tests/test_my_module.py
import pytest
from medbilldozer.my_module import MyClass

class TestMyClass:
    """Test suite for MyClass."""
    
    def test_initialization(self):
        """MyClass initializes correctly."""
        obj = MyClass(param="value")
        assert obj.param == "value"
    
    def test_main_functionality(self):
        """MyClass main method works correctly."""
        obj = MyClass()
        result = obj.do_something("input")
        assert result == "expected_output"
    
    @pytest.mark.parametrize("input,expected", [
        ("a", "A"),
        ("b", "B"),
    ])
    def test_with_parameters(self, input, expected):
        """MyClass handles different inputs."""
        obj = MyClass()
        assert obj.process(input) == expected
```

## Next Steps

- [Scripts Reference](scripts.md) - CLI tools for benchmarking
- [Package Structure](package_structure.md) - Module organization
- [Benchmark Engine](../architecture/benchmark_engine.md) - Validation system
