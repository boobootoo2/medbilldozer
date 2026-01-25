## Dependency Graph

Module dependencies within the project:

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

### `_modules.extractors.gemini_langextractor`

**Depends on:**
- `_modules.extractors.extraction_prompt`

### `_modules.extractors.local_heuristic_extractor`

**Depends on:**
- `_modules.extractors.extraction_prompt`

### `_modules.extractors.openai_langextractor`

**Depends on:**
- `_modules.extractors.extraction_prompt`

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

### `_modules.ui.doc_assistant`

**Depends on:**
- `_modules.utils.image_paths`

### `_modules.ui.ui`

**Depends on:**
- `_modules.ui.ui_pipeline_dag`
- `_modules.utils.image_paths`
- `_modules.utils.runtime_flags`

### `app`

**Depends on:**
- `_modules.core.coverage_matrix`
- `_modules.core.document_identity`
- `_modules.core.orchestrator_agent`
- `_modules.core.transaction_normalization`
- `_modules.providers.gemini_analysis_provider`
- `_modules.providers.llm_interface`
- `_modules.providers.medgemma_hosted_provider`
- `_modules.providers.openai_analysis_provider`
- `_modules.ui.billdozer_widget`
- `_modules.ui.doc_assistant`
- `_modules.ui.guided_tour`
- `_modules.ui.health_profile`
- `_modules.ui.privacy_ui`
- `_modules.ui.ui`
- `_modules.ui.ui_coverage_matrix`
- `_modules.ui.ui_documents`
- `_modules.ui.ui_pipeline_dag`
- `_modules.utils.config`
- `_modules.utils.runtime_flags`
- `_modules.utils.serialization`
