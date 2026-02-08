# Package Structure

medBillDozer follows Python best practices with a `src/` layout and modular architecture.

## Overview

```
medbilldozer/
├── src/medbilldozer/          # Main package (installed via pip)
│   ├── core/                  # Core business logic
│   ├── providers/             # LLM provider implementations
│   ├── extractors/            # Fact extraction
│   ├── prompts/               # Prompt templates
│   ├── ui/                    # Streamlit UI components
│   ├── data/                  # Data access layer
│   ├── ingest/                # Document ingestion
│   ├── utils/                 # Utilities
│   └── __init__.py
│
├── medBillDozer.py                     # Main Streamlit application
├── benchmark_dashboard.py     # Benchmark monitoring UI
├── pyproject.toml             # Package configuration
├── requirements.txt           # Dependencies
│
├── tests/                     # Test suite
├── scripts/                   # CLI tools
├── benchmarks/                # Benchmark test cases
├── docs/                      # Documentation
└── config/                    # Configuration files
```

## Core Modules

### `src/medbilldozer/core/`

Core orchestration and analysis logic:

```
core/
├── __init__.py
├── orchestrator_agent.py          # Main DAG pipeline
├── analysis_runner.py             # Streamlit integration
├── coverage_matrix.py             # Cross-document matching
├── document_identity.py           # Document ID generation
├── transaction_normalization.py   # Transaction deduplication
└── auth.py                        # Authentication
```

**Key Classes**:
- `OrchestratorAgent`: 5-stage DAG execution
- `run_document_analysis()`: Batch document processing
- `build_coverage_matrix()`: Cross-doc analysis
- `normalize_line_items()`: Transaction standardization

### `src/medbilldozer/providers/`

LLM provider implementations:

```
providers/
├── __init__.py
├── llm_interface.py               # Abstract base class
├── provider_registry.py           # Provider management
├── openai_analysis_provider.py    # OpenAI GPT-4
├── gemini_analysis_provider.py    # Google Gemini
└── medgemma_hosted_provider.py    # MedGemma
```

**Key Classes**:
- `LLMAnalysisProvider`: Interface all providers implement
- `ProviderRegistry`: Singleton provider manager
- `AnalysisResult`: Structured analysis output
- `Issue`: Individual billing issue

### `src/medbilldozer/extractors/`

Fact extraction from raw text:

```
extractors/
├── __init__.py
├── openai_langextractor.py        # OpenAI extraction
├── gemini_langextractor.py        # Gemini extraction
├── local_heuristic_extractor.py   # Regex-based (no LLM)
└── fact_normalizer.py             # Schema enforcement
```

**Key Functions**:
- `extract_facts_openai()`: Structured extraction via GPT-4
- `extract_facts_gemini()`: Structured extraction via Gemini
- `extract_facts_local()`: Regex-based extraction
- `normalize_facts()`: Enforce fact schema

### `src/medbilldozer/prompts/`

Domain-specific prompt templates:

```
prompts/
├── __init__.py
├── medical_bill_prompt.py         # Medical billing prompts
├── dental_bill_prompt.py          # Dental billing prompts
├── insurance_eob_prompt.py        # EOB prompts
├── fsa_receipt_prompt.py          # FSA claim prompts
└── receipt_line_item_prompt.py    # Line item parsing
```

**Each file exports**:
- System prompt (expert persona)
- Extraction prompt (structured data)
- Analysis prompt (issue detection)

### `src/medbilldozer/ui/`

Streamlit UI components (18 files):

```
ui/
├── __init__.py
├── ui.py                          # Main result rendering
├── ui_pipeline_dag.py             # DAG visualization
├── ui_coverage_matrix.py          # Cross-doc view
├── bootstrap.py                   # App initialization
├── doc_assistant.py               # Contextual help
├── guided_tour.py                 # Onboarding
├── health_profile.py              # Profile editor
├── billdozer_widget.py            # Custom widgets
├── page_router.py                 # Multi-page routing
└── ...                            # 8 more UI files
```

**Key Functions**:
- `render_results()`: Display analysis results
- `render_pipeline_dag()`: Show DAG workflow
- `render_coverage_matrix()`: Cross-doc table
- `create_pipeline_dag_container()`: Live updates

### `src/medbilldozer/data/`

Data access layer:

```
data/
├── __init__.py
├── health_data_ingestion.py       # Import wizard
├── fictional_entities.py          # Demo data
└── portal_templates.py            # UI templates
```

### `src/medbilldozer/ingest/`

Document ingestion pipeline:

```
ingest/
├── __init__.py
└── api.py                         # Ingestion API
```

### `src/medbilldozer/utils/`

Utility functions:

```
utils/
├── __init__.py
├── config.py                      # Configuration management
├── sanitize.py                    # Input sanitization
├── serialization.py               # JSON serialization
├── image_paths.py                 # Asset management
└── runtime_flags.py               # Feature flags
```

## Application Entry Points

### `medBillDozer.py`

Main Streamlit application:

```python
# Import bootstrap (initializes providers, config)
from medbilldozer.ui.bootstrap import initialize_app

# Initialize
initialize_app()

# Import page components
from medbilldozer.ui import ui
from medbilldozer.ui.guided_tour import run_guided_tour
from medbilldozer.ui.health_profile import render_health_profile

# Routing
page = st.sidebar.selectbox("Page", ["Analysis", "Profile", "Tour"])

if page == "Analysis":
    # Main analysis UI
    ui.render_analysis_page()
elif page == "Profile":
    render_health_profile()
elif page == "Tour":
    run_guided_tour()
```

### `benchmark_dashboard.py`

Benchmark monitoring application:

```python
import streamlit as st
import pandas as pd
from pathlib import Path

# Load benchmark results
results_dir = Path("benchmarks/results")
all_results = load_all_results(results_dir)

# Display comparison
st.title("📊 Benchmark Monitoring")
render_provider_comparison(all_results)
render_f1_trends(all_results)
render_per_category_metrics(all_results)
```

## Configuration Files

### `pyproject.toml`

Package metadata and tool configuration:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "medbilldozer"
version = "0.2.0"
description = "Medical Bill Analysis and Error Detection System"
requires-python = ">=3.11"

[tool.setuptools.packages.find]
where = ["src"]
include = ["medbilldozer*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.black]
line-length = 120
target-version = ['py311', 'py312', 'py313']

[tool.flake8]
max-line-length = 120
ignore = ["E203", "W503", "E306"]
```

### `requirements.txt`

Core dependencies:

```
streamlit>=1.28.0
openai>=1.0.0
google-generativeai>=0.3.0
supabase>=2.0.0
pandas>=2.0.0
numpy>=1.24.0
python-dotenv>=1.0.0
```

### `.flake8`

Linter configuration (41 rules ignored for project style)

### `.env.example`

Environment variable template

## Import Patterns

### Internal Imports

Within package, use absolute imports:

```python
# ✅ Correct
from medbilldozer.core.orchestrator_agent import OrchestratorAgent
from medbilldozer.providers import ProviderRegistry
from medbilldozer.utils.config import get_config

# ❌ Avoid relative imports
from ..core.orchestrator_agent import OrchestratorAgent
```

### External Imports

From application code (medBillDozer.py, scripts):

```python
# After pip install -e .
from medbilldozer.core import OrchestratorAgent
from medbilldozer.providers import ProviderRegistry
from medbilldozer.ui import ui
```

## Package Installation

### Editable Mode (Development)

```bash
pip install -e .
```

Installs package in editable mode:
- Changes to source code immediately available
- No need to reinstall after edits
- Creates `medbilldozer.egg-info/`

### Standard Mode (Production)

```bash
pip install .
```

Installs package normally:
- Copies files to site-packages
- Requires reinstall after changes

## Module Responsibilities

| Module | Responsibility | External Dependencies |
|--------|---------------|----------------------|
| `core/` | Business logic, orchestration | None (pure Python) |
| `providers/` | LLM integration | openai, google-generativeai |
| `extractors/` | Text parsing | openai, google-generativeai |
| `prompts/` | Prompt templates | None |
| `ui/` | User interface | streamlit |
| `data/` | Data access | pandas |
| `ingest/` | Document import | None |
| `utils/` | Utilities | python-dotenv |

## Testing Structure

```
tests/
├── __init__.py
├── conftest.py                    # Pytest fixtures
├── test_orchestrator_agent.py     # Core logic tests
├── test_config.py                 # Config tests
├── test_sanitize.py               # Security tests
├── test_ui.py                     # UI tests
└── test_image_paths.py            # Asset tests
```

**Test count**: 134 tests, 100% passing

## Scripts Structure

```
scripts/
├── migrate_module.py              # Module migration tool
├── generate_patient_benchmarks.py # Benchmark generation
├── annotate_benchmarks.py         # Ground truth annotation
├── run_benchmarks.py              # Benchmark execution
├── archive_old_docs.sh            # Documentation cleanup
└── verify_setup.py                # Installation verification
```

## Benchmarks Structure

```
benchmarks/
├── inputs/                        # Test documents
│   ├── patient_001_colonoscopy.txt
│   └── ...
├── patient_profiles/              # Patient context
│   ├── patient_001_profile.json
│   └── ...
├── expected_outputs/              # Ground truth
│   ├── patient_001_colonoscopy_expected.json
│   └── ...
└── results/                       # Benchmark runs
    ├── 2026-02-05_gpt-4o-mini/
    └── ...
```

## Architecture Patterns

### Dependency Injection

Providers injected via registry:

```python
# Register providers at startup
ProviderRegistry.register("gpt-4o-mini", OpenAIAnalysisProvider("gpt-4o-mini"))

# Inject at runtime
provider = ProviderRegistry.get(analyzer_key)
analysis = provider.analyze_document(text, facts)
```

### Strategy Pattern

Pluggable extractors and analyzers:

```python
# Extractor strategy
if extractor == "openai":
    facts = extract_facts_openai(text)
elif extractor == "gemini":
    facts = extract_facts_gemini(text)
elif extractor == "local":
    facts = extract_facts_local(text)
```

### Observer Pattern

Progress callbacks for live updates:

```python
def progress_callback(workflow_log, step_status):
    update_pipeline_dag(placeholder, workflow_log, step_status)

result = agent.run(raw_text, progress_callback=progress_callback)
```

## Next Steps

- [Setup Guide](setup.md) - Install for development
- [Testing Guide](testing.md) - Run and write tests
- [Scripts Reference](scripts.md) - CLI tools
- [System Architecture](../architecture/system_overview.md) - Design patterns
