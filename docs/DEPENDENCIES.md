## Dependency Graph

Module dependencies within the project:

### `_modules.core.analysis_runner`

**Depends on:**
- `_modules.core.coverage_matrix`
- `_modules.core.document_identity`
- `_modules.core.orchestrator_agent`
- `_modules.core.transaction_normalization`
- `_modules.ui.billdozer_widget`
- `_modules.ui.doc_assistant`
- `_modules.ui.ui`
- `_modules.ui.ui_coverage_matrix`
- `_modules.ui.ui_pipeline_dag`
- `_modules.utils.config`
- `_modules.utils.serialization`

### `_modules.core.orchestrator_agent`

**Depends on:**
- `_modules.extractors.fact_normalizer`
- `_modules.extractors.gemini_langextractor`
- `_modules.extractors.local_heuristic_extractor`
- `_modules.extractors.openai_langextractor`
- `_modules.prompts.dental_line_item_prompt`
- `_modules.prompts.fsa_claim_item_prompt`
- `_modules.prompts.insurance_claim_item_prompt`
- `_modules.prompts.medical_line_item_prompt`
- `_modules.prompts.receipt_line_item_prompt`
- `_modules.providers.llm_interface`
- `_modules.ui.billdozer_widget`

### `_modules.data.health_data_ingestion`

**Depends on:**
- `_modules.data.fictional_entities`
- `_modules.ui.profile_editor`

### `_modules.extractors.gemini_langextractor`

**Depends on:**
- `_modules.extractors.extraction_prompt`

### `_modules.extractors.local_heuristic_extractor`

**Depends on:**
- `_modules.extractors.extraction_prompt`

### `_modules.extractors.openai_langextractor`

**Depends on:**
- `_modules.extractors.extraction_prompt`

### `_modules.ingest.api`

**Depends on:**
- `_modules.data.fictional_entities`
- `_modules.data.health_data_ingestion`

### `_modules.providers.gemini_analysis_provider`

**Depends on:**
- `_modules.extractors.gemini_langextractor`
- `_modules.providers.llm_interface`

### `_modules.providers.medgemma_hosted_provider`

**Depends on:**
- `_modules.providers.llm_interface`

### `_modules.providers.openai_analysis_provider`

**Depends on:**
- `_modules.providers.llm_interface`

### `_modules.providers.provider_registry`

**Depends on:**
- `_modules.providers.gemini_analysis_provider`
- `_modules.providers.llm_interface`
- `_modules.providers.medgemma_hosted_provider`
- `_modules.providers.openai_analysis_provider`

### `_modules.ui.api_docs_page`

**Depends on:**
- `_modules.data.fictional_entities`
- `_modules.ingest.api`

### `_modules.ui.audio_controls`

**Depends on:**
- `_modules.utils.config`

### `_modules.ui.bootstrap`

**Depends on:**
- `_modules.ui.doc_assistant`
- `_modules.ui.ui`
- `_modules.utils.config`

### `_modules.ui.doc_assistant`

**Depends on:**
- `_modules.utils.image_paths`

### `_modules.ui.guided_tour`

**Depends on:**
- `_modules.ui.audio_controls`

### `_modules.ui.page_router`

**Depends on:**
- `_modules.ui.api_docs_page`
- `_modules.ui.audio_controls`
- `_modules.ui.bootstrap`
- `_modules.ui.guided_tour`
- `_modules.ui.profile_editor`

### `_modules.ui.prod_workflow`

**Depends on:**
- `_modules.utils.sanitize`

### `_modules.ui.profile_editor`

**Depends on:**
- `_modules.utils.sanitize`

### `_modules.ui.splash_screen`

**Depends on:**
- `_modules.ui.audio_controls`
- `_modules.ui.billdozer_widget`

### `_modules.ui.ui`

**Depends on:**
- `_modules.ui.ui_pipeline_dag`
- `_modules.utils.image_paths`
- `_modules.utils.runtime_flags`

### `app`

**Depends on:**
- `_modules.core.analysis_runner`
- `_modules.core.auth`
- `_modules.core.coverage_matrix`
- `_modules.core.orchestrator_agent`
- `_modules.providers.llm_interface`
- `_modules.providers.provider_registry`
- `_modules.ui.audio_controls`
- `_modules.ui.bootstrap`
- `_modules.ui.doc_assistant`
- `_modules.ui.guided_tour`
- `_modules.ui.health_profile`
- `_modules.ui.page_router`
- `_modules.ui.privacy_ui`
- `_modules.ui.splash_screen`
- `_modules.ui.ui`
- `_modules.ui.ui_coverage_matrix`
- `_modules.ui.ui_documents`
- `_modules.utils.config`
- `_modules.utils.runtime_flags`
