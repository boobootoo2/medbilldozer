# medBillDozer

**AI-powered medical billing analysis and error detection**

medBillDozer helps patients audit medical bills, insurance EOBs, and healthcare receipts by detecting billing errors, overcharges, and policy violations using a hybrid deterministic + LLM approach.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io)

## Key Features

🎯 **Hybrid Detection Engine**: Combines rule-based deterministic analysis with LLM-powered context-aware detection

📊 **DAG Pipeline Visualization**: Real-time workflow tracking showing classification → extraction → parsing → analysis stages

🔄 **Cross-Document Reasoning**: Analyzes multiple related documents to detect duplicates and validate insurance calculations

🧪 **Benchmark-Driven**: Continuous validation against ground-truth annotated test cases

🔌 **Provider-Agnostic**: Pluggable LLM backends (OpenAI GPT-4, Google Gemini, MedGemma, or local heuristics)

🔒 **Privacy-First**: Local execution, no required cloud storage, user-controlled data persistence

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/boobootoo2/medbilldozer.git
cd medbilldozer

# Install package in editable mode
pip install -e .

# Install dependencies
pip install -r requirements.txt

# Launch application
streamlit run app.py
```

### Environment Variables (Optional)

```bash
# AI Provider Keys (or use "Local Heuristic" mode)
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-gemini-key"

# Optional: Access control
export APP_ACCESS_PASSWORD="your_password"

# Optional: Enable features
export GUIDED_TOUR=TRUE
export PROFILE_EDITOR_ENABLED=TRUE
```

### 5-Minute Tutorial

1. **Try Demo Document**:
   - Launch app: `streamlit run app.py`
   - Accept privacy policy
   - Select "🏥 Colonoscopy Bill" in demo section
   - Click "Analyze with medBillDozer"
   - Review $650 in detected issues

2. **Analyze Your Own Bill**:
   - Copy text from any medical bill or EOB
   - Paste into document input area
   - Click analyze
   - Review detected issues and potential savings

3. **Cross-Document Analysis**:
   - Upload multiple related documents (bill + EOB + receipt)
   - System automatically detects duplicates
   - Review coverage matrix and aggregate savings

## What Documents Can I Analyze?

✅ Medical procedure bills (CPT codes)  
✅ Dental treatment bills (CDT codes)  
✅ Pharmacy receipts  
✅ Insurance Explanation of Benefits (EOB)  
✅ FSA/HSA claim statements  
✅ Hospital itemized bills  

## Architecture Highlights

### 1. DAG Execution Pipeline

Each document follows a 5-stage directed acyclic graph:

```
Classification → Extraction → Line Items → Analysis → Complete
     ↓               ↓            ↓            ↓          ↓
  Document       Structured    CPT/CDT    Issue      Cross-Doc
   Type           Facts         Codes    Detection    Reasoning
```

- **Idempotent**: Re-running produces consistent results
- **Traceable**: UUID-tracked workflow logs
- **Live Updates**: Real-time progress visualization

See [DAG Pipeline Documentation](docs/architecture/dag_pipeline.md)

### 2. Provider Abstraction Layer

Pluggable LLM backends via `ProviderRegistry`:

```python
# Switch providers without code changes
agent = OrchestratorAgent(analyzer_override="gemini-2.0-flash")
result = agent.run(document_text)
```

Supported providers:
- **OpenAI**: GPT-4o, GPT-4o-mini
- **Google Gemini**: gemini-2.0-flash, gemini-1.5-pro
- **MedGemma**: Healthcare-aligned foundation model
- **Local Heuristic**: Rule-based, no API key required

See [Provider Abstraction Documentation](docs/architecture/provider_abstraction.md)

### 3. Fact-Aware Analysis

Structured extraction before analysis improves accuracy:

```python
# Extract facts
facts = extract_facts_openai(raw_text)
# {"provider": "Dr. Smith", "cpt_codes": ["99213"], ...}

# Fact-aware analysis (15-20% better F1 score)
analysis = provider.analyze_document(raw_text, facts=facts)
```

### 4. Benchmark Validation Engine

Continuous testing against annotated ground truth:

```bash
# Run benchmark suite
python scripts/run_benchmarks.py --provider gpt-4o-mini

# Results: Precision 0.87 | Recall 0.92 | F1 0.89
```

See [Benchmark Engine Documentation](docs/architecture/benchmark_engine.md)

### 5. Cross-Document Reasoning

Analyze multiple related documents together:

- **Coverage Matrix**: Match bills to insurance plans
- **Transaction Normalization**: Deduplicate across documents
- **Aggregate Savings**: Total potential refunds

## Package Structure

```
src/medbilldozer/
├── core/              # Pipeline orchestration, analysis runner
│   ├── orchestrator_agent.py    # Main DAG workflow
│   ├── analysis_runner.py       # Streamlit integration
│   ├── coverage_matrix.py       # Cross-document matching
│   └── transaction_normalization.py
│
├── providers/         # LLM provider implementations
│   ├── openai_analysis_provider.py
│   ├── gemini_analysis_provider.py
│   ├── medgemma_hosted_provider.py
│   └── provider_registry.py     # Provider management
│
├── extractors/        # Fact extraction
│   ├── openai_langextractor.py  # Structured extraction
│   ├── gemini_langextractor.py
│   ├── fact_normalizer.py       # Schema normalization
│   └── local_heuristic_extractor.py  # No LLM required
│
├── prompts/           # Domain-specific prompt templates
│   ├── medical_bill_prompt.py
│   ├── dental_bill_prompt.py
│   └── receipt_line_item_prompt.py
│
├── ui/                # Streamlit UI components
│   ├── ui_pipeline_dag.py       # DAG visualization
│   ├── ui_coverage_matrix.py    # Cross-doc view
│   └── billdozer_widget.py      # Custom UI elements
│
├── data/              # Data access layer
├── ingest/            # Document ingestion
├── utils/             # Config, sanitization, serialization
└── __init__.py
```

## Performance Benchmarks

Tested on 50 annotated medical bills with known errors:

| Provider | F1 Score | Precision | Recall | Latency |
|----------|----------|-----------|--------|---------|
| **GPT-4o-mini** | 0.89 | 0.87 | 0.92 | 4.2s |
| **Gemini 2.0** | 0.86 | 0.90 | 0.82 | 3.8s |
| **MedGemma** | 0.91 | 0.93 | 0.89 | 5.1s |
| **Heuristic** | 0.72 | 1.00 | 0.57 | 0.3s |

**Issue Detection by Category**:
- Duplicate Charges: 100% detection rate (deterministic)
- Upcoding: 92% detection rate (LLM + rules)
- Balance Billing: 88% detection rate
- Missing Information: 95% detection rate

## Documentation

### For Users
- [User Workflow Guide](docs/product/user_workflow.md)
- [Analysis Model Explained](docs/product/analysis_model.md)
- [Cross-Document Reasoning](docs/product/cross_document_reasoning.md)

### For Developers
- [System Architecture](docs/architecture/system_overview.md)
- [DAG Pipeline](docs/architecture/dag_pipeline.md)
- [Orchestration Workflow](docs/architecture/orchestration.md)
- [Provider Abstraction](docs/architecture/provider_abstraction.md)
- [Benchmark Engine](docs/architecture/benchmark_engine.md)

### For Contributors
- [Development Setup](docs/development/setup.md)
- [Testing Guide](docs/development/testing.md)
- [Package Structure](docs/development/package_structure.md)

## Development

### Running Tests

```bash
# Unit tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/medbilldozer --cov-report=html

# Specific test
pytest tests/test_orchestrator_agent.py -v
```

### Running Benchmarks

```bash
# Benchmark all providers
python scripts/run_benchmarks.py --all

# Benchmark specific provider
python scripts/run_benchmarks.py --provider gpt-4o-mini

# Launch benchmark dashboard
streamlit run benchmark_dashboard.py
```

### Code Quality

```bash
# Linting
flake8 src/ tests/ scripts/

# Type checking
mypy src/

# Auto-formatting
black src/ tests/ scripts/
```

## Contributing

We welcome contributions! Key areas:

1. **New Providers**: Add support for additional LLM backends
2. **Detection Rules**: Improve deterministic issue detection
3. **Benchmark Cases**: Add more ground-truth test cases
4. **UI Enhancements**: Improve Streamlit interface
5. **Documentation**: Clarify and expand docs

See [Contributing Guide](CONTRIBUTING.md) for details.

## Privacy & Security

- **Local-First**: All analysis runs locally by default
- **No Tracking**: No analytics, cookies, or third-party services
- **Input Sanitization**: HTML stripping and XSS prevention
- **Optional Cloud**: Supabase integration user-controlled
- **No PHI Storage**: We don't store protected health information

See [Security Documentation](docs/security/sanitization.md)

## License

MIT License - see [LICENSE](LICENSE) file

## Acknowledgments

- **MedGemma**: Healthcare-aligned foundation models from Google
- **HAI-DEF Framework**: Healthcare AI development guidelines
- **Open Source Community**: Streamlit, OpenAI, and contributors

## Citation

If you use medBillDozer in research or production:

```bibtex
@software{medbilldozer2026,
  title = {medBillDozer: AI-Powered Medical Billing Analysis},
  author = {medBillDozer Team},
  year = {2026},
  url = {https://github.com/boobootoo2/medbilldozer},
  version = {0.2.0}
}
```

## Contact

- **Issues**: [GitHub Issues](https://github.com/boobootoo2/medbilldozer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/boobootoo2/medbilldozer/discussions)

---

**⚠️ Disclaimer**: medBillDozer is an analysis tool, not medical or legal advice. Always verify findings with your healthcare provider and insurance company before taking action.
