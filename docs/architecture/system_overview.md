# System Architecture Overview

medBillDozer is a medical billing analysis system that detects errors, overcharges, and policy violations in healthcare documents using a hybrid deterministic + LLM approach.

## Architecture Principles

1. **Privacy-First**: All analysis runs locally; no required cloud storage
2. **Provider-Agnostic**: Pluggable LLM backend (OpenAI, Gemini, MedGemma, or local heuristics)
3. **Deterministic Core**: Rule-based detection for known error patterns
4. **DAG Execution**: Idempotent pipeline with trackable workflow logs
5. **Test-Driven**: Continuous benchmark validation against patient profiles

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Streamlit UI                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Doc Upload   │  │ Profile      │  │ Guided Tour  │      │
│  │ & Analysis   │  │ Editor       │  │ & Assistant  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Core Analysis Engine                       │
│  ┌──────────────────────────────────────────────────┐       │
│  │          OrchestratorAgent (DAG Pipeline)        │       │
│  │  1. Classification  →  2. Extraction  →          │       │
│  │  3. Line Items  →  4. Analysis  →  5. Complete  │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
      ┌───────────────────────┼────────────────────────┐
      │                       │                        │
┌─────────────┐    ┌─────────────────┐    ┌──────────────────┐
│  Extractors │    │ Provider Registry│    │ Fact Normalizer │
│  ─────────  │    │  ─────────────── │    │  ────────────── │
│  • OpenAI   │    │  • OpenAI        │    │  • CPT/CDT      │
│  • Gemini   │    │  • Gemini        │    │  • FSA Claims   │
│  • Local    │    │  • MedGemma      │    │  • Line Items   │
│             │    │  • Heuristic     │    │  • Transactions │
└─────────────┘    └─────────────────┘    └──────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Data & Utilities                          │
│  • Coverage Matrix   • Transaction Normalization            │
│  • Document Identity • Sanitization & Security              │
│  • Benchmark Engine  • Workflow Persistence                 │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Input**: User uploads medical documents (PDF text, EOB, receipt)
2. **Classification**: Regex patterns identify document type
3. **Extraction**: LLM extracts structured facts (provider, dates, codes, amounts)
4. **Phase-2 Parsing**: Document-specific parsers extract line items
5. **Analysis**: Hybrid deterministic + LLM issue detection
6. **Output**: Structured issues with severity, savings, and explanations

## Key Differentiators

### 1. DAG Pipeline with Live Visualization
- Each document analysis follows a directed acyclic graph
- Real-time progress updates via callback mechanism
- Workflow logs persist for reproducibility

### 2. Cross-Document Reasoning
- Coverage matrix matches bills to insurance plans
- Transaction deduplication across multiple documents
- Aggregate savings calculations

### 3. Benchmark-Driven Development
- Patient profile-based test generation
- Ground truth annotation system
- Continuous validation against real-world scenarios

### 4. Provider Abstraction
- Pluggable LLM backends (no vendor lock-in)
- Fact-aware analysis: providers receive extracted facts + raw text
- Graceful fallback when providers unavailable

## Package Structure

```
src/medbilldozer/
├── core/              # Pipeline orchestration, analysis runner
├── providers/         # LLM provider implementations
├── extractors/        # Fact extraction (OpenAI, Gemini, local)
├── prompts/           # Prompt templates for medical domains
├── ui/                # Streamlit UI components
├── data/              # Data access layer
├── ingest/            # Document ingestion pipeline
├── utils/             # Config, sanitization, serialization
└── __init__.py
```

See [Package Structure](../development/package_structure.md) for details.

## External Integrations

- **OpenAI** (GPT-4o, GPT-4o-mini): Fact extraction & analysis
- **Google Gemini** (gemini-2.0-flash, gemini-1.5-pro): Alternative LLM
- **MedGemma** (hosted): Healthcare-aligned foundation model
- **Supabase** (optional): User-controlled persistence layer

## Performance Characteristics

- **Latency**: 3-8 seconds per document (varies by LLM provider)
- **Throughput**: Parallel document processing supported
- **Memory**: O(n) where n = document count
- **Scalability**: Stateless design enables horizontal scaling

## Next Steps

- [DAG Pipeline Details](dag_pipeline.md)
- [Orchestration Workflow](orchestration.md)
- [Provider Abstraction](provider_abstraction.md)
- [Benchmark Engine](benchmark_engine.md)
