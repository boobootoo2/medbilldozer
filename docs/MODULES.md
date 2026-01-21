# MedBillDozer Documentation

*Auto-generated from codebase analysis*

## Project Overview

**Total Modules:** 25

### Application (1 modules)

- **app**: No description

### Core Business Logic (4 modules)

- **_modules.core.coverage_matrix**: No description
- **_modules.core.document_identity**: No description
- **_modules.core.orchestrator_agent**: No description
- **_modules.core.transaction_normalization**: No description

### Fact Extractors (5 modules)

- **_modules.extractors.extraction_prompt**: No description
- **_modules.extractors.fact_normalizer**: No description
- **_modules.extractors.gemini_langextractor**: No description
- **_modules.extractors.local_heuristic_extractor**: No description
- **_modules.extractors.openai_langextractor**: No description

### LLM Providers (4 modules)

- **_modules.providers.gemini_analysis_provider**: No description
- **_modules.providers.llm_interface**: Model-agnostic LLM interface for medBillDozer.
- **_modules.providers.medgemma_hosted_provider**: No description
- **_modules.providers.openai_analysis_provider**: No description

### Prompt Builders (5 modules)

- **_modules.prompts.dental_line_item_prompt**: No description
- **_modules.prompts.fsa_claim_item_prompt**: No description
- **_modules.prompts.insurance_claim_item_prompt**: No description
- **_modules.prompts.medical_line_item_prompt**: No description
- **_modules.prompts.receipt_line_item_prompt**: No description

### UI Components (4 modules)

- **_modules.ui.privacy_ui**: No description
- **_modules.ui.ui**: No description
- **_modules.ui.ui_coverage_matrix**: No description
- **_modules.ui.ui_documents**: No description

### Utilities (2 modules)

- **_modules.utils.runtime_flags**: No description
- **_modules.utils.serialization**: No description


## Module: `_modules.core.coverage_matrix`

**Source:** `_modules/core/coverage_matrix.py`

### Classes

#### `CoverageRow`

**Attributes:**
- `description`
- `date`
- `receipt_amount`
- `fsa_amount`
- `insurance_amount`
- `receipt_doc`
- `fsa_doc`
- `insurance_doc`
- `status`


### Functions

#### `build_coverage_matrix(documents) -> List[CoverageRow]`


## Module: `_modules.core.document_identity`

**Source:** `_modules/core/document_identity.py`

### Functions

#### `build_canonical_string(facts) -> str`

#### `hash_canonical(canonical) -> str`

#### `_shorten(text, max_len) -> str`

#### `_format_date(date_str) -> str`

#### `_pretty_doc_type(doc_type) -> Optional[str]`

#### `make_user_friendly_document_id(facts, fallback_index) -> str`

#### `maybe_enhance_identity(doc) -> None`


## Module: `_modules.core.orchestrator_agent`

**Source:** `_modules/core/orchestrator_agent.py`

### Constants

- **`DOCUMENT_EXTRACTOR_MAP`**: `{'medical_bill': 'gpt-4o-mini', 'insurance_eob': 'gpt-4o-mini', 'pharmacy_receipt': 'gemini-1.5-flash', 'dental_bill': 'gpt-4o-mini', 'generic': 'gpt-4o-mini'}`
- **`DOCUMENT_SIGNALS`**: `{'medical_bill': ['\\bCPT\\b', '\\bICD-10\\b', 'Date of Service', 'Patient Responsibility', 'Allowed Amount'], 'insurance_eob': ['Explanation of Benefits', '\\bEOB\\b', 'Insurance Paid', 'Claim Number'], 'pharmacy_receipt': ['\\bRx\\b', 'NDC', 'Pharmacy', 'Copay'], 'dental_bill': ['\\bD\\d{4}\\b', 'Dental', 'Crown', 'Lab Fee']}`

### Classes

#### `OrchestratorAgent`

**Methods:**

- **`__init__(self, extractor_override, analyzer_override)`**

- **`run(self, raw_text) -> Dict`**


### Functions

#### `_clean_llm_json(text) -> str`

Cleans LLM output so it can be parsed as JSON.
Safe for OpenAI and Gemini.

#### `model_backend(model) -> Optional[str]`

#### `_run_phase2_prompt(prompt, model) -> Optional[str]`

#### `deterministic_issues_from_facts(facts) -> list[Issue]`

#### `deterministic_issues_from_facts(facts) -> list[Issue]`

#### `compute_deterministic_savings(facts) -> float`

#### `normalize_issues(issues) -> list`

#### `classify_document(text) -> Dict`

#### `extract_pre_facts(text) -> Dict`

Lightweight heuristic facts (cheap, deterministic).


### Dependencies

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

## Module: `_modules.core.transaction_normalization`

**Source:** `_modules/core/transaction_normalization.py`

### Classes

#### `NormalizedTransaction`

**Attributes:**
- `canonical_id`
- `source_document_id`
- `patient_dob`
- `provider_name`
- `date_of_service`
- `cpt_code`
- `units`
- `billed_amount`
- `allowed_amount`
- `description`


### Functions

#### `_norm_str(value) -> str`

#### `_norm_money(value) -> str`

#### `build_transaction_fingerprint() -> str`

#### `normalize_line_items(line_items, source_document_id) -> List[NormalizedTransaction]`

#### `deduplicate_transactions(transactions) -> Tuple[Dict[str, NormalizedTransaction], Dict[str, List[str]]]`


## Module: `_modules.extractors.extraction_prompt`

**Source:** `_modules/extractors/extraction_prompt.py`

### Functions

#### `build_fact_extraction_prompt(document_text) -> str`

Provider-agnostic prompt for structured healthcare fact extraction.
Compatible with OpenAI, Gemini, MedGemma, or local LLMs.


## Module: `_modules.extractors.fact_normalizer`

**Source:** `_modules/extractors/fact_normalizer.py`

### Constants

- **`DATE_INPUT_FORMATS`**: `['%B %d, %Y', '%b %d, %Y', '%m/%d/%Y', '%Y-%m-%d']`
- **`TIME_INPUT_FORMATS`**: `['%I:%M %p', '%H:%M']`

### Functions

#### `_normalize_string(value) -> Optional[str]`

#### `_normalize_date(value) -> Optional[str]`

#### `_normalize_time(value) -> Optional[str]`

#### `normalize_facts(facts) -> Dict[str, Optional[str]]`

Provider-agnostic normalization pass.
SAFE: never raises, preserves keys.


## Module: `_modules.extractors.gemini_langextractor`

**Source:** `_modules/extractors/gemini_langextractor.py`

### Functions

#### `_safe_empty_result() -> Dict[str, Optional[str]]`

#### `extract_facts_gemini(raw_text) -> Dict[str, Optional[str]]`

Gemini-based fact extractor.
SAFE: never raises, always returns full schema.

#### `run_prompt_gemini(prompt) -> str`

Runs a raw prompt using Gemini and returns the text response.
Intended for Phase-2 extraction.
SAFE: raises to caller (caller must catch).


### Dependencies

- `_modules.extractors.extraction_prompt`

## Module: `_modules.extractors.local_heuristic_extractor`

**Source:** `_modules/extractors/local_heuristic_extractor.py`

### Functions

#### `_safe_empty() -> Dict[str, Optional[str]]`

#### `_find_first(pattern, text) -> Optional[str]`

#### `_find_date(patterns, text) -> Optional[str]`

#### `extract_facts_local(raw_text) -> Dict[str, Optional[str]]`

Deterministic local heuristic fact extractor.
Conservative by design.


### Dependencies

- `_modules.extractors.extraction_prompt`

## Module: `_modules.extractors.openai_langextractor`

**Source:** `_modules/extractors/openai_langextractor.py`

### Functions

#### `_safe_empty_result() -> Dict[str, Optional[str]]`

#### `_clean_json(text) -> str`

Removes markdown fences and leading junk.

#### `extract_facts_openai(raw_text) -> Dict[str, Optional[str]]`

Extract structured healthcare facts using OpenAI.
SAFE: never raises, always returns all keys.

#### `run_prompt_openai(prompt) -> str`

Runs a raw prompt using OpenAI and returns the text response.
Intended for Phase-2 extraction (receipt items, line items, etc).
SAFE: raises to caller (caller must catch).


### Dependencies

- `_modules.extractors.extraction_prompt`

## Module: `_modules.prompts.dental_line_item_prompt`

**Source:** `_modules/prompts/dental_line_item_prompt.py`

### Functions

#### `build_dental_line_item_prompt(raw_text) -> str`


## Module: `_modules.prompts.fsa_claim_item_prompt`

**Source:** `_modules/prompts/fsa_claim_item_prompt.py`

### Functions

#### `build_fsa_claim_item_prompt(document_text) -> str`


## Module: `_modules.prompts.insurance_claim_item_prompt`

**Source:** `_modules/prompts/insurance_claim_item_prompt.py`

### Functions

#### `build_insurance_claim_item_prompt(raw_text) -> str`


## Module: `_modules.prompts.medical_line_item_prompt`

**Source:** `_modules/prompts/medical_line_item_prompt.py`

### Functions

#### `build_medical_line_item_prompt(raw_text) -> str`


## Module: `_modules.prompts.receipt_line_item_prompt`

**Source:** `_modules/prompts/receipt_line_item_prompt.py`

### Functions

#### `build_receipt_line_item_prompt(document_text) -> str`


## Module: `_modules.providers.gemini_analysis_provider`

**Source:** `_modules/providers/gemini_analysis_provider.py`

### Classes

#### `GeminiAnalysisProvider`

**Inherits from:** `LLMProvider`

Gemini-powered analysis provider.

**Methods:**

- **`__init__(self, model)`**

- **`name(self) -> str`**

- **`analyze_document(self, raw_text, facts) -> AnalysisResult`**


### Dependencies

- `_modules.extractors.gemini_langextractor`
- `_modules.providers.llm_interface`

## Module: `_modules.providers.llm_interface`

**Source:** `_modules/providers/llm_interface.py`

### Description

Model-agnostic LLM interface for medBillDozer.

### Classes

#### `Issue`

**Attributes:**
- `type`
- `summary`
- `evidence`
- `code`
- `date`
- `recommended_action`
- `max_savings`
- `source`
- `confidence`

#### `AnalysisResult`

**Attributes:**
- `issues`
- `meta`

#### `LLMProvider`

**Inherits from:** `ABC`

All analysis providers MUST implement the same interface.

Contract:
    analyze_document(raw_text: str, facts: Optional[Dict]) -> AnalysisResult

**Methods:**

- **`name(self) -> str`**
  - Return a short provider name.

- **`analyze_document(self, raw_text, facts) -> AnalysisResult`**
  - Analyze a document and return structured issues.

- **`health_check(self) -> bool`**

#### `ProviderRegistry`

**Attributes:**
- `_providers`

**Methods:**

- **`register(cls, key, provider) -> None`**

- **`get(cls, key) -> Optional[LLMProvider]`**

- **`list(cls) -> List[str]`**

#### `LocalHeuristicProvider`

**Inherits from:** `LLMProvider`

**Methods:**

- **`name(self) -> str`**

- **`analyze_document(self, raw_text, facts) -> AnalysisResult`**


## Module: `_modules.providers.medgemma_hosted_provider`

**Source:** `_modules/providers/medgemma_hosted_provider.py`

### Constants

- **`HF_MODEL_ID`**: `<complex value>`
- **`HF_MODEL_URL`**: `<complex value>`
- **`SYSTEM_PROMPT`**: `
You are a medical billing analysis system.

Yo...`
- **`TASK_PROMPT`**: `
Analyze the following medical billing document...`

### Classes

#### `MedGemmaHostedProvider`

**Inherits from:** `LLMProvider`

**Methods:**

- **`__init__(self)`**

- **`name(self) -> str`**

- **`health_check(self) -> bool`**

- **`analyze_document(self, text) -> AnalysisResult`**


### Functions

#### `_extract_json(text) -> dict`

Extract the first valid JSON object from model output.
Handles leading whitespace, prose, or accidental formatting.


### Dependencies

- `_modules.providers.llm_interface`

## Module: `_modules.providers.openai_analysis_provider`

**Source:** `_modules/providers/openai_analysis_provider.py`

### Classes

#### `OpenAIAnalysisProvider`

**Inherits from:** `LLMProvider`

OpenAI-powered analysis provider.

**Methods:**

- **`__init__(self, model)`**

- **`name(self) -> str`**

- **`analyze_document(self, raw_text, facts) -> AnalysisResult`**


### Dependencies

- `_modules.providers.llm_interface`

## Module: `_modules.ui.privacy_ui`

**Source:** `_modules/ui/privacy_ui.py`

### Functions

#### `_init_privacy_state()`

#### `_privacy_dialog()`

**Decorators:** `@st.dialog('🔒 Privacy & Cookie Preferences')`

#### `render_privacy_dialog()`


## Module: `_modules.ui.ui`

**Source:** `_modules/ui/ui.py`

### Functions

#### `calculate_max_savings(issues)`

Returns:
  total_max (float)
  breakdown (list of dicts)

#### `render_savings_breakdown(title, total, breakdown)`

#### `toggle_expander_state(key)`

#### `show_empty_warning()`

#### `show_analysis_success()`

#### `show_analysis_error(msg)`

#### `setup_page()`

#### `inject_css()`

#### `render_header()`

#### `_read_html(path) -> str`

#### `html_to_plain_text(html_doc) -> str`

#### `copy_to_clipboard_button(label, text)`

#### `render_document_rows(docs, html_docs, text_docs, key_prefix)`

#### `render_demo_documents()`

#### `render_input_area()`

#### `render_provider_selector(providers) -> str`

#### `render_analyze_button() -> bool`

#### `render_results(result)`

#### `render_footer()`


### Dependencies

- `_modules.utils.runtime_flags`

## Module: `_modules.ui.ui_coverage_matrix`

**Source:** `_modules/ui/ui_coverage_matrix.py`

### Functions

#### `render_coverage_matrix(rows)`


## Module: `_modules.ui.ui_documents`

**Source:** `_modules/ui/ui_documents.py`

### Functions

#### `_shorten_provider(name, max_len) -> str`

#### `_format_date(date_str) -> str`

Accepts many formats, returns YYYY-MM-DD or YYYY-MM

#### `make_user_friendly_document_id(facts, fallback_index) -> str`

#### `render_document_inputs()`


## Module: `_modules.utils.runtime_flags`

**Source:** `_modules/utils/runtime_flags.py`

### Functions

#### `debug_enabled() -> bool`


## Module: `_modules.utils.serialization`

**Source:** `_modules/utils/serialization.py`

### Functions

#### `issue_to_dict(issue)`

#### `analysis_to_dict(result) -> dict`

Convert an AnalysisResult-like object into a pure dict.
Duck-typed to avoid importing domain models.


## Module: `app`

**Source:** `app.py`

### Constants

- **`ENGINE_OPTIONS`**: `{'Smart (Recommended)': None, 'gpt-4o-mini': 'gpt-4o-mini', 'gemini-3-flash-preview': 'gemini-3-flash-preview', 'Local (Offline)': 'heuristic'}`

### Functions

#### `render_total_savings_summary(total_potential_savings, per_document_savings)`

Render a single aggregate summary once per run.

#### `bootstrap_ui()`

#### `register_providers()`

#### `main()`


### Dependencies

- `_modules.core.coverage_matrix`
- `_modules.core.document_identity`
- `_modules.core.orchestrator_agent`
- `_modules.core.transaction_normalization`
- `_modules.providers.gemini_analysis_provider`
- `_modules.providers.llm_interface`
- `_modules.providers.medgemma_hosted_provider`
- `_modules.providers.openai_analysis_provider`
- `_modules.ui.privacy_ui`
- `_modules.ui.ui`
- `_modules.ui.ui_coverage_matrix`
- `_modules.ui.ui_documents`
- `_modules.utils.runtime_flags`
- `_modules.utils.serialization`
