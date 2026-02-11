## Dependency Graph

Module dependencies within the project:

### Core Dependencies

#### AI/ML Frameworks
- **streamlit** (1.52.2) - Web application framework
- **google-genai** (1.59.0) - Google Gemini API
- **openai** (2.9.0) - OpenAI API
- **langextract** (1.1.1) - Language detection

#### Data Processing
- **pandas** (2.3.3) - Data manipulation and analysis
- **numpy** (2.4.1) - Numerical computing
- **pyarrow** (22.0.0) - Apache Arrow data format

#### Visualization
- **plotly** (6.5.2) - Interactive plotting
- **matplotlib** (3.10.8) - Static plotting
- **altair** (6.0.0) - Declarative visualization

#### Storage & Cloud
- **google-cloud-storage** (3.8.0) - GCS integration
- **boto3** (1.42.28) - AWS SDK
- **supabase** (>=2.3.0) - Supabase client
- **snowflake-connector-python** (4.2.0) - Snowflake integration

#### Testing & Quality
- **pytest** (8.3.4) - Testing framework
- **pytest-mock** (3.14.0) - Mocking support
- **Faker** (40.1.2) - Synthetic data generation

#### Utilities
- **python-dotenv** (1.2.1) - Environment variables
- **PyYAML** (6.0.3) - YAML parsing
- **requests** (2.32.5) - HTTP client
- **beautifulsoup4** (4.14.3) - HTML parsing
- **Jinja2** (3.1.6) - Template engine

#### Security
- **cryptography** (46.0.3) - Cryptographic primitives
- **PyJWT** (2.10.1) - JSON Web Tokens
- **certifi** (2025.11.12) - SSL certificates

#### Streamlit Extensions
- **streamlit-extras** (0.7.8) - Additional components
- **streamlit-camera-input-live** (0.2.0) - Camera input
- **streamlit-cookies-manager** (0.2.0) - Cookie management
- **st-annotated-text** (4.0.2) - Text annotation

---

### Internal Module Dependencies

#### Core Modules
```
medbilldozer/
├── core/
│   ├── analysis_runner.py      (depends on: providers, utils)
│   └── auth.py                 (depends on: streamlit)
│
├── providers/
│   ├── openai_analysis_provider.py     (depends on: openai, core)
│   ├── medgemma_ensemble_provider.py   (depends on: openai, core)
│   └── provider_registry.py            (depends on: all providers)
│
├── extractors/
│   ├── openai_langextractor.py   (depends on: openai, utils)
│   ├── gemini_langextractor.py   (depends on: google.genai, utils)
│   └── extraction_prompt.py      (depends on: utils)
│
├── ingest/
│   └── api.py                    (depends on: data, extractors)
│
├── data/
│   ├── fictional_entities.py          (depends on: Faker, utils)
│   ├── health_data_ingestion.py       (depends on: fictional_entities, streamlit)
│   └── portal_templates.py            (depends on: Faker, utils)
│
├── prompts/
│   ├── extraction_prompt.py
│   ├── insurance_claim_item_prompt.py
│   ├── medical_line_item_prompt.py
│   ├── dental_line_item_prompt.py
│   ├── fsa_claim_item_prompt.py
│   └── receipt_line_item_prompt.py
│
├── ui/
│   ├── ui.py                     (depends on: core, data, streamlit)
│   ├── page_router.py            (depends on: streamlit)
│   ├── billdozer_widget.py       (depends on: streamlit)
│   ├── guided_tour.py            (depends on: streamlit, openai)
│   ├── doc_assistant.py          (depends on: streamlit, openai, gemini)
│   ├── health_profile.py         (depends on: streamlit, data)
│   └── [other UI components]
│
└── utils/
    ├── config.py                 (depends on: PyYAML)
    ├── sanitize.py               (depends on: re, html)
    ├── serialization.py
    └── runtime_flags.py          (depends on: streamlit)
```

#### Dependency Flow

```
┌─────────────┐
│   UI Layer  │ ← streamlit, components
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Core Layer  │ ← analysis_runner, auth
└──────┬──────┘
       │
       ├──────→ ┌──────────────┐
       │        │  Providers   │ ← OpenAI, MedGemma
       │        └──────────────┘
       │
       ├──────→ ┌──────────────┐
       │        │  Extractors  │ ← openai, google-genai
       │        └──────────────┘
       │
       └──────→ ┌──────────────┐
                │     Data     │ ← fictional_entities, ingestion
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │   Prompts    │
                └──────────────┘
```

#### External API Dependencies

**Required Environment Variables:**
- `OPENAI_API_KEY` - OpenAI API access
- `GOOGLE_API_KEY` - Google Gemini API access (optional)
- `HUGGINGFACE_API_TOKEN` - HuggingFace model access (optional)

**API Endpoints Used:**
- OpenAI: `https://api.openai.com/v1/chat/completions`
- Google Gemini: Via `google-genai` SDK
- HuggingFace Inference: `https://api-inference.huggingface.co/models/`

---

### Development Dependencies

#### From `requirements-test.txt`
- pytest and testing frameworks
- Code coverage tools
- Linting and formatting tools

#### From `requirements-monitoring.txt`
- Prometheus client
- Monitoring and observability tools

#### From `requirements-benchmarks.txt`
- Benchmark evaluation frameworks
- Performance testing tools

---

### Package Structure

The project uses modern Python packaging with:
- **pyproject.toml** - Project metadata and build configuration
- **setup.py** - Package installation (if present)
- **src/medbilldozer/** - Main package directory
- **_modules/** - Legacy module directory (being deprecated)

**Installation:**
```bash
pip install -e .
```

This installs the package in editable mode, making all modules importable:
```python
from medbilldozer.core import analysis_runner
from medbilldozer.data import fictional_entities
from medbilldozer.utils import sanitize
```

---

### Compatibility Notes

- **Python Version:** Requires Python 3.9+
- **Operating Systems:** Cross-platform (macOS, Linux, Windows)
- **Streamlit:** Optimized for Streamlit 1.52.2
- **API Clients:** OpenAI SDK 2.x, Google GenAI 1.x

### Security Considerations

- All API keys should be stored in environment variables
- Never commit `.env` files or `app_config.yaml` with secrets
- Use `app_config.example.yaml` as template
- Sanitization utilities prevent injection attacks
- HTTPS required for production deployments
