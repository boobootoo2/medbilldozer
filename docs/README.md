# MedBillDozer Documentation

*Auto-generated from codebase analysis*

## Project Overview

**Total Modules:** 26

### Application (1 modules)

- **app**: MedBillDozer - Medical billing error detection application.

### Core Business Logic (4 modules)

- **_modules.core.coverage_matrix**: Cross-document coverage matrix builder.
- **_modules.core.document_identity**: Document identity and labeling utilities.
- **_modules.core.orchestrator_agent**: Main workflow orchestration for healthcare document analysis.
- **_modules.core.transaction_normalization**: Transaction normalization and deduplication.

### Fact Extractors (5 modules)

- **_modules.extractors.extraction_prompt**: Core fact extraction prompt builder.
- **_modules.extractors.fact_normalizer**: Provider-agnostic fact normalization utilities.
- **_modules.extractors.gemini_langextractor**: No description
- **_modules.extractors.local_heuristic_extractor**: Deterministic local heuristic fact extractor.
- **_modules.extractors.openai_langextractor**: OpenAI-based LLM fact extractor and generic prompt runner.

### LLM Providers (4 modules)

- **_modules.providers.gemini_analysis_provider**: Gemini-powered healthcare document analysis provider.
- **_modules.providers.llm_interface**: Model-agnostic LLM interface for medBillDozer.
- **_modules.providers.medgemma_hosted_provider**: MedGemma hosted model analysis provider.
- **_modules.providers.openai_analysis_provider**: OpenAI-powered healthcare document analysis provider.

### Prompt Builders (5 modules)

- **_modules.prompts.dental_line_item_prompt**: Prompt builder for dental bill line item extraction.
- **_modules.prompts.fsa_claim_item_prompt**: Prompt builder for FSA/HSA claim history extraction.
- **_modules.prompts.insurance_claim_item_prompt**: Prompt builder for insurance claim history extraction.
- **_modules.prompts.medical_line_item_prompt**: Prompt builder for medical bill line item extraction.
- **_modules.prompts.receipt_line_item_prompt**: No description

### UI Components (5 modules)

- **_modules.ui.doc_assistant**: Documentation Assistant - AI-powered help sidebar.
- **_modules.ui.privacy_ui**: Privacy dialog and cookie preferences UI.
- **_modules.ui.ui**: No description
- **_modules.ui.ui_coverage_matrix**: Coverage matrix UI rendering.
- **_modules.ui.ui_documents**: Document input and management UI.

### Utilities (2 modules)

- **_modules.utils.runtime_flags**: Runtime flags and feature toggles.
- **_modules.utils.serialization**: Serialization utilities for converting analysis objects to dicts.
