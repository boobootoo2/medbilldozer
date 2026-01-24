# MedBillDozer Documentation

*Auto-generated from codebase analysis*

## Project Overview

**Total Modules:** 30

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

### UI Components (8 modules)

- **_modules.ui.billdozer_widget**: No description
- **_modules.ui.doc_assistant**: Documentation Assistant - AI-powered help sidebar.
- **_modules.ui.health_profile**: Health profile management for policy holder and dependents.
- **_modules.ui.privacy_ui**: Privacy dialog and cookie preferences UI.
- **_modules.ui.ui**: No description
- **_modules.ui.ui_coverage_matrix**: Coverage matrix UI rendering.
- **_modules.ui.ui_documents**: Document input and management UI.
- **_modules.ui.ui_pipeline_dag**: Pipeline DAG Visualization - Visual representation of document analysis workflow.

### Utilities (3 modules)

- **_modules.utils.config**: Application Configuration Manager.
- **_modules.utils.runtime_flags**: Runtime flags and feature toggles.
- **_modules.utils.serialization**: Serialization utilities for converting analysis objects to dicts.


## Module: `_modules.core.coverage_matrix`

**Source:** `_modules/core/coverage_matrix.py`

### Description

Cross-document coverage matrix builder.

Builds a coverage matrix that relates receipts, FSA claims, and insurance claims
across multiple documents to identify potential duplicate payments or coverage gaps.

### Classes

#### `CoverageRow`

Represents a single row in the coverage matrix.

Tracks amounts and document references across receipt, FSA, and insurance sources
for a specific service on a specific date.

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

Build a cross-document coverage matrix from analyzed documents.

Args:
    documents: List of document dicts with 'facts' and 'document_id' keys

Returns:
    List[CoverageRow]: Coverage rows showing related transactions across documents


## Module: `_modules.core.document_identity`

**Source:** `_modules/core/document_identity.py`

### Description

Document identity and labeling utilities.

Provides functions to generate canonical identities, user-friendly labels,
and unique fingerprints for medical billing documents.

### Functions

#### `build_canonical_string(facts) -> str`

Build canonical string representation of document facts.

Args:
    facts: Dictionary of document facts

Returns:
    str: Canonical string with sorted key-value pairs

#### `hash_canonical(canonical) -> str`

Generate short hash from canonical string.

Args:
    canonical: Canonical string representation

Returns:
    str: First 10 characters of SHA256 hash

#### `_shorten(text, max_len) -> str`

Shorten text to maximum length, normalizing whitespace.

Args:
    text: Text to shorten
    max_len: Maximum length (default 28)

Returns:
    str: Shortened text or "Unknown" if text is None

#### `_format_date(date_str) -> str`

Parse and format date string to YYYY-MM-DD format.

Tries multiple common date formats. Returns original string if parsing fails.

Args:
    date_str: Date string in various formats

Returns:
    str: Date in YYYY-MM-DD format or original string

#### `_pretty_doc_type(doc_type) -> Optional[str]`

Convert document type to user-friendly title case.

Args:
    doc_type: Document type string (e.g., 'insurance_claim')

Returns:
    Optional[str]: Title case string (e.g., 'Insurance Claim') or None

#### `make_user_friendly_document_id(facts, fallback_index) -> str`

Generate user-friendly document label from facts.

Creates a readable label like "Provider Name · 2024-01-15 · Document Type"

Args:
    facts: Dictionary of document facts
    fallback_index: Optional index to append for disambiguation

Returns:
    str: User-friendly document label

#### `maybe_enhance_identity(doc) -> None`

Enhance document with canonical identity and hash.

Modifies the document dict in-place to add '_identity' field if not present.

Args:
    doc: Document dict with 'facts' key


## Module: `_modules.core.orchestrator_agent`

**Source:** `_modules/core/orchestrator_agent.py`

### Description

Main workflow orchestration for healthcare document analysis.

Coordinates document classification, fact extraction, line item parsing,
and issue analysis through a multi-phase pipeline. Provides deterministic
issue detection and LLM-based analysis integration.

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

Clean LLM output for JSON parsing.

Removes markdown fences, leading commentary, and other artifacts
that prevent JSON parsing.

Args:
    text: Raw LLM output string
    
Returns:
    Cleaned string ready for JSON parsing

#### `model_backend(model) -> Optional[str]`

Determine backend provider from model name.

Args:
    model: Model identifier string (e.g., 'gpt-4', 'gemini-1.5-flash')
    
Returns:
    Backend name ('openai', 'gemini') or None if unknown

#### `_run_phase2_prompt(prompt, model) -> Optional[str]`

Execute phase 2 line item parsing prompt using appropriate backend.

Args:
    prompt: Formatted prompt string for line item extraction
    model: Model identifier to use for execution
    
Returns:
    LLM response text or None if backend not supported

#### `deterministic_issues_from_facts(facts) -> list[Issue]`

#### `deterministic_issues_from_facts(facts) -> list[Issue]`

#### `compute_deterministic_savings(facts) -> float`

Calculate total savings from deterministic issues.

Sums max_savings from all deterministic issues identified in facts.

Args:
    facts: Facts dictionary containing line items and extracted data
    
Returns:
    Total potential savings amount in dollars

#### `normalize_issues(issues) -> list`

#### `classify_document(text) -> Dict`

Classify document type using regex pattern matching.

Scores document against known patterns for medical bills, dental bills,
pharmacy receipts, insurance claims, and FSA claims.

Args:
    text: Raw document text
    
Returns:
    Dict with document_type, confidence score, and pattern match scores

#### `extract_pre_facts(text) -> Dict`

Extract lightweight heuristic facts before full extraction.

Provides fast, cheap feature detection (CPT codes, dental codes, Rx markers)
for downstream routing and optimization.

Args:
    text: Raw document text
    
Returns:
    Dict with boolean flags and document statistics


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
- `_modules.ui.billdozer_widget`

## Module: `_modules.core.transaction_normalization`

**Source:** `_modules/core/transaction_normalization.py`

### Description

Transaction normalization and deduplication.

Provides utilities to normalize billing transactions from various document formats
into a canonical structure, build unique fingerprints, and deduplicate across documents.

### Classes

#### `NormalizedTransaction`

Normalized representation of a billing transaction.

Provides a standardized structure for transactions from different document types
with a unique canonical_id for deduplication.

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

Normalize string to lowercase with trimmed whitespace.

Args:
    value: String to normalize

Returns:
    str: Normalized lowercase string or empty string if None

#### `_norm_money(value) -> str`

Format money value to standardized string.

Args:
    value: Decimal amount

Returns:
    str: Formatted amount with 2 decimal places or empty string if None

#### `build_transaction_fingerprint() -> str`

Build canonical fingerprint for transaction deduplication.

Creates a unique hash based on normalized transaction attributes.

Args:
    patient_dob: Patient date of birth
    provider_name: Provider or facility name
    date_of_service: Service date
    cpt_code: CPT procedure code
    units: Number of units
    billed_amount: Billed amount

Returns:
    str: SHA256 hash of canonical transaction representation

#### `normalize_line_items(line_items, source_document_id) -> List[NormalizedTransaction]`

Convert raw line items to normalized transaction objects.

Args:
    line_items: List of raw line item dicts from document facts
    source_document_id: ID of source document for provenance tracking

Returns:
    List[NormalizedTransaction]: Normalized transactions with canonical IDs

#### `deduplicate_transactions(transactions) -> Tuple[Dict[str, NormalizedTransaction], Dict[str, List[str]]]`

Deduplicate transactions and track provenance.

Args:
    transactions: List of normalized transactions (may contain duplicates)

Returns:
    Tuple of:
        - Dict mapping canonical_id to unique transaction
        - Dict mapping canonical_id to list of source document IDs


## Module: `_modules.extractors.extraction_prompt`

**Source:** `_modules/extractors/extraction_prompt.py`

### Description

Core fact extraction prompt builder.

Provides provider-agnostic prompts for extracting structured facts from
healthcare documents including bills, receipts, and claim histories.

### Functions

#### `build_fact_extraction_prompt(document_text) -> str`

Build provider-agnostic prompt for structured healthcare fact extraction.

Compatible with OpenAI, Gemini, MedGemma, or local LLMs.

Args:
    document_text: Raw document text

Returns:
    str: Formatted extraction prompt requesting JSON with FACT_KEYS


## Module: `_modules.extractors.fact_normalizer`

**Source:** `_modules/extractors/fact_normalizer.py`

### Description

Provider-agnostic fact normalization utilities.

Provides functions to normalize extracted facts (strings, dates, times, amounts)
into consistent formats for downstream processing.

### Constants

- **`DATE_INPUT_FORMATS`**: `['%B %d, %Y', '%b %d, %Y', '%m/%d/%Y', '%Y-%m-%d']`
- **`TIME_INPUT_FORMATS`**: `['%I:%M %p', '%H:%M']`

### Functions

#### `_normalize_string(value) -> Optional[str]`

Normalize string to lowercase with collapsed whitespace.

Args:
    value: Input string to normalize
    
Returns:
    Normalized lowercase string with single spaces, or None if input is empty

#### `_normalize_date(value) -> Optional[str]`

Parse date string into ISO format (YYYY-MM-DD).

Tries multiple common date formats and returns first successful parse.

Args:
    value: Date string in various formats (e.g., 'January 18, 2026', '01/18/2026')
    
Returns:
    ISO-formatted date string (YYYY-MM-DD) or None if parse fails

#### `_normalize_time(value) -> Optional[str]`

Parse time string into 24-hour format (HH:MM).

Tries multiple time formats and returns 24-hour normalized format.

Args:
    value: Time string in various formats (e.g., '3:42 PM', '15:42')
    
Returns:
    24-hour formatted time string (HH:MM) or None if parse fails

#### `normalize_facts(facts) -> Dict[str, Optional[str]]`

Provider-agnostic normalization pass.
SAFE: never raises, preserves keys.


## Module: `_modules.extractors.gemini_langextractor`

**Source:** `_modules/extractors/gemini_langextractor.py`

### Functions

#### `_get_client()`

Get or create the Gemini client lazily.

#### `_safe_empty_result() -> Dict[str, Optional[str]]`

Return empty facts dictionary with all keys set to None.

Returns:
    Dictionary with all FACT_KEYS mapped to None

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

### Description

Deterministic local heuristic fact extractor.

Provides regex-based fact extraction as a fast, cost-free alternative to LLM-based extraction.
Conservative by design - only extracts facts with high confidence patterns.

### Functions

#### `_safe_empty() -> Dict[str, Optional[str]]`

Return empty facts dictionary with all keys set to None.

Returns:
    Dictionary with all FACT_KEYS mapped to None

#### `_find_first(pattern, text) -> Optional[str]`

Find first match of regex pattern in text.

Args:
    pattern: Regex pattern with capture group
    text: Text to search
    
Returns:
    Captured group text (stripped) or None if no match

#### `_find_date(patterns, text) -> Optional[str]`

Try multiple date patterns and return first match.

Args:
    patterns: List of regex patterns to try in order
    text: Text to search
    
Returns:
    First matched date string or None if no patterns match

#### `extract_facts_local(raw_text) -> Dict[str, Optional[str]]`

Deterministic local heuristic fact extractor.
Conservative by design.


### Dependencies

- `_modules.extractors.extraction_prompt`

## Module: `_modules.extractors.openai_langextractor`

**Source:** `_modules/extractors/openai_langextractor.py`

### Description

OpenAI-based LLM fact extractor and generic prompt runner.

Provides OpenAI GPT-powered fact extraction from healthcare documents and
utility functions for running arbitrary prompts against OpenAI models.
Safe by design - never raises exceptions, always returns complete schema.

### Functions

#### `_safe_empty_result() -> Dict[str, Optional[str]]`

Return empty facts dictionary with all keys set to None.

Returns:
    Dictionary with all FACT_KEYS mapped to None

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

### Description

Prompt builder for dental bill line item extraction.

### Functions

#### `build_dental_line_item_prompt(raw_text) -> str`

Build prompt for extracting line items from dental bills.

Args:
    raw_text: Raw dental bill text

Returns:
    str: Formatted prompt for LLM extraction


## Module: `_modules.prompts.fsa_claim_item_prompt`

**Source:** `_modules/prompts/fsa_claim_item_prompt.py`

### Description

Prompt builder for FSA/HSA claim history extraction.

### Functions

#### `build_fsa_claim_item_prompt(document_text) -> str`

Build prompt for extracting claim rows from FSA/HSA claim history.

Args:
    document_text: Raw FSA/HSA claim history text

Returns:
    str: Formatted prompt for LLM extraction


## Module: `_modules.prompts.insurance_claim_item_prompt`

**Source:** `_modules/prompts/insurance_claim_item_prompt.py`

### Description

Prompt builder for insurance claim history extraction.

### Functions

#### `build_insurance_claim_item_prompt(raw_text) -> str`

Build prompt for extracting insurance claim history rows (EOB-style).

Args:
    raw_text: Raw insurance claim history text

Returns:
    str: Formatted prompt for LLM extraction


## Module: `_modules.prompts.medical_line_item_prompt`

**Source:** `_modules/prompts/medical_line_item_prompt.py`

### Description

Prompt builder for medical bill line item extraction.

### Functions

#### `build_medical_line_item_prompt(raw_text) -> str`

Build prompt for extracting line items from medical bills.

Args:
    raw_text: Raw medical bill text

Returns:
    str: Formatted prompt for LLM extraction


## Module: `_modules.prompts.receipt_line_item_prompt`

**Source:** `_modules/prompts/receipt_line_item_prompt.py`

### Functions

#### `build_receipt_line_item_prompt(document_text) -> str`

Build prompt for extracting line items from retail/pharmacy receipts.

Args:
    document_text: Raw receipt text

Returns:
    str: Formatted prompt for LLM extraction


## Module: `_modules.providers.gemini_analysis_provider`

**Source:** `_modules/providers/gemini_analysis_provider.py`

### Description

Gemini-powered healthcare document analysis provider.

Provides Google Gemini-based analysis of healthcare documents to identify billing issues,
discrepancies, and potential patient savings.

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

### Description

MedGemma hosted model analysis provider.

Provides MedGemma (medical domain-specific LLM) hosted on Hugging Face
for specialized medical billing analysis.

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

### Description

OpenAI-powered healthcare document analysis provider.

Provides GPT-based analysis of healthcare documents to identify billing issues,
discrepancies, and potential patient savings.

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

## Module: `_modules.ui.billdozer_widget`

**Source:** `_modules/ui/billdozer_widget.py`

### Constants

- **`BILLDOZER_TOKEN`**: `BILLDOZER_v1`
- **`_WIDGET_HTML_CACHE`**: `None`

### Functions

#### `get_billdozer_widget_html() -> str`

Loads and caches the Billdozer widget HTML.
Injects Streamlit-safe CSS overrides.

#### `install_billdozer_bridge()`

#### `dispatch_widget_message(character, message)`

Sends a speech message to the widget.
Safely queues if the iframe is not ready yet.


## Module: `_modules.ui.doc_assistant`

**Source:** `_modules/ui/doc_assistant.py`

### Description

Documentation Assistant - AI-powered help sidebar.

Provides contextual help and answers to user questions by reading
the comprehensive documentation as a source of truth.

### Constants

- **`_BILLY_IMAGES_CACHE`**: `None`

### Classes

#### `DocumentationAssistant`

AI-powered documentation assistant that provides contextual help.

**Methods:**

- **`__init__(self)`**
  - Initialize the documentation assistant with documentation content.

- **`get_avatar_image(self, state) -> str`**
  - Get base64 encoded avatar image.

- **`_load_documentation(self)`**
  - Load all documentation files into memory.

- **`_build_context_prompt(self, user_question) -> str`**
  - Build a comprehensive context prompt from documentation.

- **`get_answer_openai(self, user_question) -> str`**
  - Get answer using OpenAI API.

- **`get_answer_gemini(self, user_question) -> str`**
  - Get answer using Google Gemini API.

- **`get_answer(self, user_question, provider) -> str`**
  - Get answer using specified AI provider.

- **`search_docs(self, query) -> List[Dict[str, str]]`**
  - Search documentation for relevant sections.


### Functions

#### `dispatch_billy_event(event_type)`

#### `_get_billy_images()`

Load and cache Billy avatar images as base64 data URIs.

#### `calculate_blink_probability() -> bool`

Calculate if avatar should blink using Fourier transform harmonics.

This follows the randomized algorithms for blinking used by an android on the Enterprise.
Uses harmonic analysis to create natural-seeming but mathematically precise blink timing,
similar to how Data's positronic neural net regulated involuntary humanoid behaviors.

Returns:
    True if avatar should blink, False otherwise

#### `render_doc_assistant()`

#### `render_contextual_help(context)`

Render contextual help based on current page/action.

Args:
    context: Current context (e.g., 'input', 'results', 'error')


## Module: `_modules.ui.health_profile`

**Source:** `_modules/ui/health_profile.py`

### Description

Health profile management for policy holder and dependents.

Provides pre-loaded patient profiles with medical history, insurance details,
and demographic information for demo and testing purposes.

### Constants

- **`SAMPLE_PROFILES`**: `{'policyholder': {'id': 'PH-001', 'name': 'John Sample', 'date_of_birth': '01/15/1975', 'age': 51, 'gender': 'Male', 'relationship': 'Policy Holder', 'insurance': {'provider': 'Horizon PPO Plus', 'member_id': 'HPP-8743920', 'group_number': 'G-1234567', 'plan_type': 'PPO', 'effective_date': '01/01/2025', 'deductible_annual': 1500.0, 'deductible_met': 1500.0, 'oop_max': 3000.0, 'oop_met': 1500.0}, 'medical_history': {'conditions': ['Hypertension (controlled)', 'Type 2 Diabetes', 'Hyperlipidemia'], 'medications': ['Lisinopril 10mg daily', 'Metformin 500mg twice daily', 'Atorvastatin 20mg at bedtime'], 'allergies': ['Penicillin (rash)', 'Sulfa drugs (hives)'], 'recent_procedures': [{'date': '01/12/2026', 'procedure': 'Screening Colonoscopy', 'provider': 'Valley Medical Center', 'cpt_code': '45378', 'cost': 1200.0, 'out_of_pocket': 100.0}, {'date': '11/05/2025', 'procedure': 'Annual Physical Exam', 'provider': 'Dr. Sarah Mitchell', 'cpt_code': '99396', 'cost': 350.0, 'out_of_pocket': 0.0}], 'upcoming_appointments': [{'date': '03/15/2026', 'type': 'Follow-up', 'provider': 'Dr. Michael Reynolds', 'reason': 'Post-colonoscopy review'}]}, 'fsa_hsa': {'account_type': 'FSA', 'plan_year': 2026, 'annual_contribution': 2850.0, 'balance_remaining': 2247.5, 'claims_submitted': 5, 'claims_approved': 4, 'claims_pending': 0, 'claims_denied': 1}}, 'dependent': {'id': 'DEP-001', 'name': 'Jane Sample', 'date_of_birth': '08/22/1986', 'age': 39, 'gender': 'Female', 'relationship': 'Spouse', 'insurance': {'provider': 'Horizon PPO Plus', 'member_id': 'HPP-8743921', 'group_number': 'G-1234567', 'plan_type': 'PPO', 'effective_date': '01/01/2025', 'deductible_annual': 1500.0, 'deductible_met': 450.0, 'oop_max': 3000.0, 'oop_met': 850.0}, 'medical_history': {'conditions': ['Seasonal Allergies', 'Mild Asthma (controlled)'], 'medications': ['Cetirizine 10mg as needed', 'Albuterol inhaler as needed', 'Multivitamin daily'], 'allergies': ['Shellfish (anaphylaxis)', 'Cat dander'], 'recent_procedures': [{'date': '01/20/2026', 'procedure': 'Dental Crown (Tooth #14)', 'provider': 'BrightSmile Dental', 'cdt_code': 'D2740', 'cost': 2500.0, 'out_of_pocket': 1625.0}, {'date': '01/18/2026', 'procedure': 'Prescription Refill', 'provider': 'GreenLeaf Pharmacy', 'medication': 'Albuterol Inhaler', 'cost': 45.0, 'out_of_pocket': 15.0}, {'date': '10/12/2025', 'procedure': 'Annual Gynecological Exam', 'provider': 'Dr. Jennifer Adams', 'cpt_code': '99385', 'cost': 285.0, 'out_of_pocket': 0.0}], 'upcoming_appointments': [{'date': '02/28/2026', 'type': 'Dental Follow-up', 'provider': 'Dr. Laura Chen, DDS', 'reason': 'Crown check-up'}, {'date': '04/10/2026', 'type': 'Annual Physical', 'provider': 'Dr. Sarah Mitchell', 'reason': 'Preventive care'}]}, 'fsa_hsa': {'account_type': 'FSA', 'plan_year': 2026, 'annual_contribution': 2850.0, 'balance_remaining': 2247.5, 'claims_submitted': 5, 'claims_approved': 4, 'claims_pending': 0, 'claims_denied': 1}}}`

### Functions

#### `render_profile_selector()`

Render profile selection dropdown.

Returns:
    str: Selected profile key ('policyholder', 'dependent', or None)

#### `render_profile_details(profile_key)`

Render detailed profile information in expandable sections.

Args:
    profile_key: Profile key ('policyholder' or 'dependent')

#### `get_profile_data(profile_key) -> Optional[Dict]`

Get profile data by key.

Args:
    profile_key: Profile key ('policyholder' or 'dependent')

Returns:
    Dict with profile data or None if not found

#### `get_profile_context_for_analysis(profile_key) -> str`

Generate context string for LLM analysis based on profile.

Args:
    profile_key: Profile key ('policyholder' or 'dependent')

Returns:
    str: Formatted context string


## Module: `_modules.ui.privacy_ui`

**Source:** `_modules/ui/privacy_ui.py`

### Description

Privacy dialog and cookie preferences UI.

Provides privacy acknowledgment dialog with cookie preference management.

### Functions

#### `_init_privacy_state()`

Initialize privacy and cookie preference state in session.

Sets default values for privacy acceptance and cookie preferences.

#### `_privacy_dialog()`

**Decorators:** `@st.dialog('🔒 Privacy & Cookie Preferences')`

Display privacy policy and cookie preferences dialog.

Shows HIPAA disclaimer, privacy policy, and cookie preference toggles.

#### `render_privacy_dialog()`

Render privacy dialog if not already acknowledged.

Shows the privacy dialog on first visit. Subsequent visits skip the dialog
based on session state.


## Module: `_modules.ui.ui`

**Source:** `_modules/ui/ui.py`

### Functions

#### `calculate_max_savings(issues)`

Calculate the maximum potential savings from a list of billing issues.

Args:
    issues: List of Issue objects with optional max_savings attribute

Returns:
    tuple: (total_max (float), breakdown (list of dicts))
        - total_max: Sum of all max_savings values
        - breakdown: List of dicts with summary and max_savings per issue

#### `render_savings_breakdown(title, total, breakdown)`

Render a formatted savings breakdown UI component.

Args:
    title: Section title for the savings display
    total: Total maximum potential savings amount
    breakdown: List of dicts with 'summary' and 'max_savings' keys

#### `toggle_expander_state(key)`

Toggle the boolean state of an expander in session state.

Args:
    key: Session state key to toggle

#### `show_empty_warning()`

Display warning message when no document is provided.

#### `show_analysis_success()`

Display success message after analysis completion.

#### `show_analysis_error(msg)`

Display error message during analysis.

Args:
    msg: Error message to display

#### `setup_page()`

Configure Streamlit page settings. Must be called first in app.py.

Sets page title and centered layout.

#### `inject_css()`

Inject custom CSS styles for branding and UI consistency.

Includes styles for:
- Brand colors and variables
- Button styling (analyze button, copy buttons)
- Checkbox focus states with dashed outlines
- Accessibility improvements
- Layout and spacing

#### `render_header()`

Render the application header with logo and tagline.

Displays the medBillDozer logo and descriptive text about the application's purpose.

#### `_read_html(path) -> str`

Read HTML file contents from disk.

Args:
    path: Path to HTML file

Returns:
    str: HTML file contents

#### `html_to_plain_text(html_doc) -> str`

Convert HTML document to plain text.

Removes script and style tags, extracts text content, and normalizes whitespace.

Args:
    html_doc: HTML content as string

Returns:
    str: Cleaned plain text content

#### `copy_to_clipboard_button(label, text)`

Render a custom button that copies text to clipboard.

Uses HTML/JavaScript component to enable clipboard functionality.

Args:
    label: Button label text
    text: Text content to copy when clicked

#### `render_document_rows(docs, html_docs, text_docs, key_prefix)`

Render expandable document rows with toggle and copy functionality.

Args:
    docs: List of (title, path) tuples
    html_docs: List of HTML content strings
    text_docs: List of plain text content strings
    key_prefix: Prefix for Streamlit widget keys to avoid collisions

#### `render_demo_documents()`

Render the demo documents section with sample medical bills.

Displays 5 demo documents:
- Hospital bill (colonoscopy)
- Pharmacy receipt (FSA)
- Dental crown bill
- FSA claim history
- Insurance claim history

#### `render_input_area()`

Render the main text input area for document analysis.

Returns:
    str: User input text from the text area

#### `render_provider_selector(providers) -> str`

Render analysis provider selection dropdown.

Maps provider IDs to user-friendly display names.

Args:
    providers: List of available provider IDs

Returns:
    str: Selected provider ID

#### `render_analyze_button() -> bool`

Render the primary 'Analyze with medBillDozer' button.

Returns:
    bool: True if button was clicked, False otherwise

#### `render_results(result)`

Render analysis results including flagged issues and savings breakdown.

Args:
    result: AnalysisResult object or dict containing issues and metadata

#### `render_footer()`

Render application footer with disclaimer.


### Dependencies

- `_modules.ui.ui_pipeline_dag`
- `_modules.utils.runtime_flags`

## Module: `_modules.ui.ui_coverage_matrix`

**Source:** `_modules/ui/ui_coverage_matrix.py`

### Description

Coverage matrix UI rendering.

Displays cross-document coverage relationships in a formatted table.

### Functions

#### `render_coverage_matrix(rows)`

Render coverage matrix as a formatted dataframe.

Shows receipts, FSA claims, and insurance payments side-by-side for comparison.

Args:
    rows: List of CoverageRow objects


## Module: `_modules.ui.ui_documents`

**Source:** `_modules/ui/ui_documents.py`

### Description

Document input and management UI.

Provides UI components for document input, validation, and user-friendly labeling.

### Functions

#### `_shorten_provider(name, max_len) -> str`

Shorten provider name to maximum length.

Args:
    name: Provider name
    max_len: Maximum length (default 28)

Returns:
    str: Shortened name or "Unknown Provider" if None

#### `_format_date(date_str) -> str`

Accepts many formats, returns YYYY-MM-DD or YYYY-MM

#### `make_user_friendly_document_id(facts, fallback_index) -> str`

Generate user-friendly document ID from facts.

Creates readable label like "Provider · Date · Type".

Args:
    facts: Document facts dictionary
    fallback_index: Optional index for disambiguation

Returns:
    str: User-friendly document label

#### `render_document_inputs()`

Render dynamic document input fields with validation.

Allows users to paste multiple documents. Validates for duplicates and
returns list of document dicts ready for analysis.

Returns:
    list[dict]: List of document dicts with 'raw_text', 'facts', 'analysis', 'document_id' keys.
               Returns empty list if validation fails.


## Module: `_modules.ui.ui_pipeline_dag`

**Source:** `_modules/ui/ui_pipeline_dag.py`

### Description

Pipeline DAG Visualization - Visual representation of document analysis workflow.

Displays a directed acyclic graph showing the data pipeline stages for each
document's analysis: classification → extraction → phase-2 parsing → analysis.

### Functions

#### `create_pipeline_dag_container(document_id)`

Create an empty expandable container for live pipeline updates.

Returns the container and placeholder objects for progressive updates.

Args:
    document_id: Optional document identifier for display
    
Returns:
    tuple: (expander, placeholder) for updating the DAG

#### `update_pipeline_dag(placeholder, workflow_log, document_id)`

Update an existing pipeline DAG placeholder with current workflow state.

Args:
    placeholder: Streamlit placeholder object to update
    workflow_log: Current workflow log dict with pipeline stages
    document_id: Optional friendly document identifier for display

#### `render_pipeline_dag(workflow_log, document_id)`

Render a visual DAG showing the document processing pipeline.

Displays the complete workflow stages with status indicators:
- Pre-extraction (classification & feature detection)
- Extraction (fact extraction with chosen extractor)
- Phase-2 parsing (line-item extraction by document type)
- Analysis (issue detection with chosen analyzer)

Args:
    workflow_log: Workflow log dict from OrchestratorAgent containing pipeline stages
    document_id: Optional document identifier for display

#### `_build_dag_html(pre_extraction, extraction, analysis, live_update) -> str`

Build HTML representation of the DAG with status indicators.

Args:
    pre_extraction: Pre-extraction stage data
    extraction: Extraction stage data
    analysis: Analysis stage data
    live_update: Whether this is a live update (shows in-progress states)
    
Returns:
    HTML string with styled DAG visualization

#### `_build_phase2_node(label, count, doc_type, extraction, has_extraction) -> str`

Build Phase-2 parsing node HTML if line items were extracted.

Args:
    label: Display label for the phase-2 stage
    count: Number of line items extracted
    doc_type: Document type
    extraction: Extraction stage data for error checking
    has_extraction: Whether extraction stage is complete
    
Returns:
    HTML string for the phase-2 node

#### `_render_detailed_logs(pre_extraction, extraction, analysis)`

Render detailed logs in expandable JSON format.

Args:
    pre_extraction: Pre-extraction stage data
    extraction: Extraction stage data
    analysis: Analysis stage data

#### `render_pipeline_comparison(workflow_logs)`

Render side-by-side comparison of multiple document pipelines.

Useful for batch analysis to compare processing paths across documents.

Args:
    workflow_logs: List of workflow log dicts from multiple document analyses


## Module: `_modules.utils.config`

**Source:** `_modules/utils/config.py`

### Description

Application Configuration Manager.

Loads and provides access to application configuration from app_config.yaml.
Provides fallback defaults if config file is missing or incomplete.

### Classes

#### `AppConfig`

Application configuration manager with fallback defaults.

**Methods:**

- **`__init__(self, config_path)`**
  - Initialize configuration manager.

- **`_load_config(self) -> Dict[str, Any]`**
  - Load configuration from YAML file with fallback to defaults.

- **`_deep_merge(self, base, override) -> Dict`**
  - Deep merge two dictionaries, with override taking precedence.

- **`get(self, key_path, default) -> Any`**
  - Get configuration value by dot-notation path.

- **`is_feature_enabled(self, feature_name) -> bool`**
  - Check if a feature is enabled.

- **`reload(self)`**
  - Reload configuration from file.


### Functions

#### `get_config() -> AppConfig`

Get the global configuration instance.

Returns:
    AppConfig instance

#### `reload_config()`

Reload the global configuration from file.

#### `is_assistant_enabled() -> bool`

Check if documentation assistant feature is enabled.

#### `is_dag_enabled() -> bool`

Check if pipeline DAG visualization is enabled.

#### `is_debug_enabled() -> bool`

Check if debug mode is enabled.

#### `is_privacy_ui_enabled() -> bool`

Check if privacy UI is enabled.

#### `is_coverage_matrix_enabled() -> bool`

Check if coverage matrix feature is enabled.


## Module: `_modules.utils.runtime_flags`

**Source:** `_modules/utils/runtime_flags.py`

### Description

Runtime flags and feature toggles.

Provides utility functions for checking runtime flags via query parameters.

### Functions

#### `debug_enabled() -> bool`

Check if debug mode is enabled via query parameter.

Debug mode can be activated by adding ?debug=1 to the URL.

Returns:
    bool: True if debug mode is enabled, False otherwise


## Module: `_modules.utils.serialization`

**Source:** `_modules/utils/serialization.py`

### Description

Serialization utilities for converting analysis objects to dicts.

Provides duck-typed serialization functions that work with various analysis
result objects without requiring explicit imports.

### Functions

#### `issue_to_dict(issue)`

Convert an Issue object to a dictionary.

Uses duck typing to extract attributes without importing domain models.

Args:
    issue: Issue object with type, summary, description, confidence attributes

Returns:
    dict: Dictionary representation of the issue

#### `analysis_to_dict(result) -> dict`

Convert an AnalysisResult object into a pure dict.

Duck-typed to avoid importing domain models. Extracts issues and metadata.

Args:
    result: AnalysisResult object with issues and meta attributes

Returns:
    dict: Dictionary with 'issues' list and 'meta' dict


## Module: `app`

**Source:** `app.py`

### Description

MedBillDozer - Medical billing error detection application.

Main Streamlit application that orchestrates document analysis, provider registration,
and UI rendering for detecting billing, pharmacy, dental, and insurance claim issues.

### Constants

- **`ENGINE_OPTIONS`**: `{'Smart (Recommended)': None, 'gpt-4o-mini': 'gpt-4o-mini', 'gemini-3-flash-preview': 'gemini-3-flash-preview', 'Local (Offline)': 'heuristic'}`

### Functions

#### `render_total_savings_summary(total_potential_savings, per_document_savings)`

Render aggregate savings summary across all analyzed documents.

Args:
    total_potential_savings: Total potential savings amount
    per_document_savings: Dict mapping document IDs to their savings amounts

#### `bootstrap_ui()`

Initialize and render core UI components.

Sets up page configuration, CSS styles, header, and demo documents.
Must be called at the start of the application.

#### `register_providers()`

Register available LLM analysis providers.

Attempts to register MedGemma, Gemini, and OpenAI providers.
Only registers providers that pass health checks.

#### `main()`

Main application entry point.

Orchestrates the complete workflow:
1. Bootstrap UI and register providers
2. Render privacy dialog
3. Collect document inputs
4. Analyze documents with selected provider
5. Display results and savings summary
6. Render coverage matrix and debug info


### Dependencies

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
- `_modules.ui.health_profile`
- `_modules.ui.privacy_ui`
- `_modules.ui.ui`
- `_modules.ui.ui_coverage_matrix`
- `_modules.ui.ui_documents`
- `_modules.ui.ui_pipeline_dag`
- `_modules.utils.config`
- `_modules.utils.runtime_flags`
- `_modules.utils.serialization`
