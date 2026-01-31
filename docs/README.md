# MedBillDozer Documentation

*Auto-generated from codebase analysis*

## Project Overview

**Total Modules:** 48

### Application (5 modules)

- **_modules.data.fictional_entities**: Fictional Healthcare Entity Generator
- **_modules.data.health_data_ingestion**: Healthcare Data Ingestion Logic
- **_modules.data.portal_templates**: Simulated Healthcare Portal Templates
- **_modules.ingest.api**: Demo-Only Healthcare Data Ingestion API
- **app**: MedBillDozer - Medical billing error detection application.

### Core Business Logic (6 modules)

- **_modules.core.analysis_runner**: Document analysis workflow runner and coordination.
- **_modules.core.auth**: Authentication and access control for the application.
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

### LLM Providers (5 modules)

- **_modules.providers.gemini_analysis_provider**: Gemini-powered healthcare document analysis provider.
- **_modules.providers.llm_interface**: Model-agnostic LLM interface for medBillDozer.
- **_modules.providers.medgemma_hosted_provider**: MedGemma hosted model analysis provider.
- **_modules.providers.openai_analysis_provider**: OpenAI-powered healthcare document analysis provider.
- **_modules.providers.provider_registry**: Provider registration and management for LLM analysis providers.

### Prompt Builders (5 modules)

- **_modules.prompts.dental_line_item_prompt**: Prompt builder for dental bill line item extraction.
- **_modules.prompts.fsa_claim_item_prompt**: Prompt builder for FSA/HSA claim history extraction.
- **_modules.prompts.insurance_claim_item_prompt**: Prompt builder for insurance claim history extraction.
- **_modules.prompts.medical_line_item_prompt**: Prompt builder for medical bill line item extraction.
- **_modules.prompts.receipt_line_item_prompt**: No description

### UI Components (17 modules)

- **_modules.ui.api_docs_page**: Interactive API Documentation Page for Streamlit
- **_modules.ui.audio_controls**: Audio Controls - Mute/unmute button for audio narration.
- **_modules.ui.billdozer_widget**: No description
- **_modules.ui.bootstrap**: UI bootstrap and initialization functions.
- **_modules.ui.doc_assistant**: Documentation Assistant - AI-powered help sidebar.
- **_modules.ui.guided_tour**: Guided Tour - Interactive tutorial using Streamlit Session State (No JavaScript).
- **_modules.ui.guided_tour_old**: Guided Tour - Interactive tutorial using Intro.js.
- **_modules.ui.health_profile**: Health profile management for policy holder and dependents.
- **_modules.ui.page_router**: Page navigation and routing for the application.
- **_modules.ui.privacy_ui**: Privacy dialog and cookie preferences UI.
- **_modules.ui.prod_workflow**: Production workflow with profile-based preloaded documents.
- **_modules.ui.profile_editor**: Profile Editor - User identity, insurance, and provider management with importer.
- **_modules.ui.splash_screen**: Splash Screen - Welcome screen with Billdozer introduction.
- **_modules.ui.ui**: No description
- **_modules.ui.ui_coverage_matrix**: Coverage matrix UI rendering.
- **_modules.ui.ui_documents**: Document input and management UI.
- **_modules.ui.ui_pipeline_dag**: Pipeline DAG Visualization - Visual representation of document analysis workflow.

### Utilities (5 modules)

- **_modules.utils.config**: Application Configuration Manager.
- **_modules.utils.image_paths**: Image path utilities for handling local vs production CDN URLs.
- **_modules.utils.runtime_flags**: Runtime flags and feature toggles.
- **_modules.utils.sanitize**: Sanitization utilities for user input to prevent XSS attacks.
- **_modules.utils.serialization**: Serialization utilities for converting analysis objects to dicts.
