# MedBillDozer Documentation

*Auto-generated from codebase analysis*

## Project Overview

**Total Modules:** 38

### Application (5 modules)

- **_modules.data.fictional_entities**: Fictional Healthcare Entity Generator
- **_modules.data.health_data_ingestion**: Healthcare Data Ingestion Logic
- **_modules.data.portal_templates**: Simulated Healthcare Portal Templates
- **_modules.ingest.api**: Demo-Only Healthcare Data Ingestion API
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

### UI Components (11 modules)

- **_modules.ui.billdozer_widget**: No description
- **_modules.ui.doc_assistant**: Documentation Assistant - AI-powered help sidebar.
- **_modules.ui.guided_tour**: Guided Tour - Interactive tutorial using Intro.js.
- **_modules.ui.health_profile**: Health profile management for policy holder and dependents.
- **_modules.ui.privacy_ui**: Privacy dialog and cookie preferences UI.
- **_modules.ui.profile_editor**: Profile Editor - User identity, insurance, and provider management with importer.
- **_modules.ui.splash_screen**: Splash Screen - Welcome screen with Billdozer introduction.
- **_modules.ui.ui**: No description
- **_modules.ui.ui_coverage_matrix**: Coverage matrix UI rendering.
- **_modules.ui.ui_documents**: Document input and management UI.
- **_modules.ui.ui_pipeline_dag**: Pipeline DAG Visualization - Visual representation of document analysis workflow.

### Utilities (4 modules)

- **_modules.utils.config**: Application Configuration Manager.
- **_modules.utils.image_paths**: Image path utilities for handling local vs production CDN URLs.
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

- **`__init__(self, extractor_override, analyzer_override, profile_context)`**

- **`run(self, raw_text, progress_callback) -> Dict`**
  - Run document analysis pipeline with optional progress callbacks.


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


## Module: `_modules.data.fictional_entities`

**Source:** `_modules/data/fictional_entities.py`

### Description

Fictional Healthcare Entity Generator

This module generates deterministic fictional healthcare entities for demo purposes.
ALL entities are completely fictional and not affiliated with any real organizations.

Uses seeded randomness to ensure consistent data generation across sessions.

### Constants

- **`AVAILABLE_SPECIALTIES`**: `<complex value>`
- **`AVAILABLE_STATES`**: `<complex value>`
- **`CITIES`**: `['Springfield', 'Riverside', 'Greenville', 'Fairview', 'Madison', 'Georgetown', 'Arlington', 'Franklin', 'Clinton', 'Salem', 'Oxford', 'Manchester', 'Bristol', 'Clayton', 'Milton', 'Newport', 'Ashland', 'Richmond', 'Brookfield', 'Chester']`
- **`DEFAULT_INSURANCE_COUNT`**: `30`
- **`DEFAULT_PROVIDER_COUNT`**: `10000`
- **`DEFAULT_SEED`**: `42`
- **`ENTITY_TYPE_INSURANCE`**: `insurance`
- **`ENTITY_TYPE_PROVIDER`**: `provider`
- **`INSURANCE_PREFIXES`**: `['American', 'United', 'National', 'Pacific', 'Atlantic', 'Mountain', 'Great Lakes', 'Sunshine', 'Liberty', 'Eagle', 'Guardian', 'Premier', 'Mutual', 'Federal', 'State', 'Regional', 'Metropolitan', 'Capital', 'Commonwealth', 'Horizon', 'Beacon', 'Summit', 'Alliance', 'Trust', 'Heritage', 'Advantage', 'Choice', 'First', 'Primary', 'Select']`
- **`INSURANCE_ROOTS`**: `['Health', 'Medical', 'Care', 'Life', 'Shield', 'Cross', 'Star', 'Benefit', 'Assurance', 'Security', 'Wellness', 'Family', 'Community', 'Partner', 'Plus', 'Pro', 'Elite', 'Prime', 'Standard', 'Classic']`
- **`INSURANCE_SUFFIXES`**: `['Group', 'Corp', 'Inc', 'LLC', 'Plan', 'Network', 'System', 'Association', 'Fund', 'Cooperative', 'Alliance', 'Partners']`
- **`PROVIDER_FIRST_NAMES`**: `['James', 'Maria', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Patricia', 'David', 'Elizabeth', 'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa', 'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra', 'Donald', 'Ashley', 'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna', 'Joshua', 'Michelle', 'Kenneth', 'Carol', 'Kevin', 'Amanda', 'Brian', 'Dorothy', 'George', 'Melissa', 'Timothy', 'Deborah', 'Ronald', 'Stephanie', 'Edward', 'Rebecca', 'Jason', 'Sharon', 'Jeffrey', 'Laura']`
- **`PROVIDER_LAST_NAMES`**: `['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker', 'Cruz', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris']`
- **`PROVIDER_PRACTICE_TYPES`**: `['Medical Group', 'Health Center', 'Clinic', 'Associates', 'Medical Center', 'Healthcare', 'Physicians', 'Practice', 'Specialists', 'Care Center', 'Medical Associates', 'Health Partners', 'Wellness Center', 'Family Practice']`
- **`PROVIDER_SPECIALTIES`**: `['Family Medicine', 'Internal Medicine', 'Pediatrics', 'Cardiology', 'Dermatology', 'Orthopedics', 'Neurology', 'Psychiatry', 'Oncology', 'Radiology', 'Anesthesiology', 'Emergency Medicine', 'Surgery', 'Obstetrics and Gynecology', 'Ophthalmology', 'Otolaryngology', 'Urology', 'Gastroenterology', 'Endocrinology', 'Rheumatology', 'Pulmonology', 'Nephrology', 'Hematology', 'Infectious Disease', 'Allergy and Immunology', 'Physical Medicine', 'Pathology', 'General Practice', 'Urgent Care', 'Sports Medicine']`
- **`US_STATES`**: `['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']`

### Classes

#### `HealthcareEntity`

**Inherits from:** `TypedDict`

Base type for healthcare entities.

**Attributes:**
- `id`
- `name`
- `entity_type`
- `demo_portal_html`

#### `InsuranceCompany`

**Inherits from:** `HealthcareEntity`

Fictional insurance company entity.

**Attributes:**
- `entity_type`
- `network_size`
- `plan_types`

#### `HealthcareProvider`

**Inherits from:** `HealthcareEntity`

Fictional healthcare provider entity.

**Attributes:**
- `entity_type`
- `specialty`
- `location_city`
- `location_state`
- `accepts_insurance`


### Functions

#### `generate_fictional_insurance_companies(count, seed) -> List[InsuranceCompany]`

**Decorators:** `@st.cache_data(ttl=None)`

Generate deterministic fictional insurance companies.

Args:
    count: Number of insurance companies to generate (default: 30)
    seed: Random seed for deterministic generation (default: 42)

Returns:
    List of fictional insurance company entities

Example:
    >>> companies = generate_fictional_insurance_companies(30)
    >>> len(companies)
    30
    >>> companies[0]['entity_type']
    'insurance'

#### `generate_fictional_healthcare_providers(count, seed, insurance_company_ids) -> List[HealthcareProvider]`

**Decorators:** `@st.cache_data(ttl=None)`

Generate deterministic fictional healthcare providers.

Args:
    count: Number of providers to generate (default: 10,000)
    seed: Random seed for deterministic generation (default: 42)
    insurance_company_ids: List of insurance company IDs to randomly assign

Returns:
    List of fictional healthcare provider entities

Example:
    >>> providers = generate_fictional_healthcare_providers(100)
    >>> len(providers)
    100
    >>> providers[0]['entity_type']
    'provider'

#### `get_all_fictional_entities(insurance_count, provider_count, seed) -> dict`

**Decorators:** `@st.cache_data(ttl=None)`

Generate all fictional entities in one call.

Args:
    insurance_count: Number of insurance companies (default: 30)
    provider_count: Number of healthcare providers (default: 10,000)
    seed: Random seed for deterministic generation (default: 42)

Returns:
    Dictionary with 'insurance' and 'providers' keys

Example:
    >>> entities = get_all_fictional_entities(30, 100)
    >>> len(entities['insurance'])
    30
    >>> len(entities['providers'])
    100

#### `get_entity_by_id(entity_id, entities) -> HealthcareEntity | None`

Find an entity by ID.

Args:
    entity_id: The entity ID to search for
    entities: List of entities to search in

Returns:
    Entity dict if found, None otherwise

Example:
    >>> companies = generate_fictional_insurance_companies(30)
    >>> entity = get_entity_by_id('demo_ins_001', companies)
    >>> entity['entity_type']
    'insurance'

#### `filter_providers_by_specialty(providers, specialty) -> List[HealthcareProvider]`

Filter providers by specialty.

Args:
    providers: List of provider entities
    specialty: Specialty to filter by

Returns:
    Filtered list of providers

Example:
    >>> providers = generate_fictional_healthcare_providers(1000)
    >>> cardiologists = filter_providers_by_specialty(providers, 'Cardiology')
    >>> all(p['specialty'] == 'Cardiology' for p in cardiologists)
    True

#### `filter_providers_by_insurance(providers, insurance_id) -> List[HealthcareProvider]`

Filter providers by accepted insurance.

Args:
    providers: List of provider entities
    insurance_id: Insurance company ID to filter by

Returns:
    Filtered list of providers that accept this insurance

Example:
    >>> entities = get_all_fictional_entities(30, 1000)
    >>> in_network = filter_providers_by_insurance(
    ...     entities['providers'],
    ...     'demo_ins_001'
    ... )
    >>> all('demo_ins_001' in p['accepts_insurance'] for p in in_network)
    True

#### `get_entity_stats(entities) -> dict`

Calculate statistics about generated entities.

Args:
    entities: Dictionary from get_all_fictional_entities()

Returns:
    Dictionary with statistics

Example:
    >>> entities = get_all_fictional_entities(30, 1000)
    >>> stats = get_entity_stats(entities)
    >>> stats['total_insurance_companies']
    30
    >>> stats['total_providers']
    1000

#### `validate_entity_uniqueness(entities) -> bool`

Validate that all entity IDs are unique.

Args:
    entities: List of entities to validate

Returns:
    True if all IDs are unique, False otherwise

#### `validate_entity_structure(entity) -> bool`

Validate that an entity has required fields.

Args:
    entity: Entity to validate

Returns:
    True if entity is valid, False otherwise


## Module: `_modules.data.health_data_ingestion`

**Source:** `_modules/data/health_data_ingestion.py`

### Description

Healthcare Data Ingestion Logic

This module handles the generation of fake healthcare data from simulated portals
and normalizes it into the proper data models for storage in session state.

DEMO ONLY - All data is fictional and clearly marked.

### Constants

- **`CPT_CODES`**: `{'99213': 'Office Visit - Established Patient, Level 3', '99214': 'Office Visit - Established Patient, Level 4', '99215': 'Office Visit - Established Patient, Level 5', '99203': 'Office Visit - New Patient, Level 3', '99204': 'Office Visit - New Patient, Level 4', '80053': 'Comprehensive Metabolic Panel', '85025': 'Complete Blood Count with Differential', '36415': 'Routine Venipuncture', '45378': 'Colonoscopy with Biopsy', '93000': 'Electrocardiogram (EKG)', '73610': 'X-ray Ankle, 3 Views', '70450': 'CT Head without Contrast', '71020': 'Chest X-ray, 2 Views', '81001': 'Urinalysis, Manual', '90471': 'Immunization Administration, First Vaccine', 'J3490': 'Unclassified Drug Injection', 'G0438': 'Annual Wellness Visit - Initial', 'G0439': 'Annual Wellness Visit - Subsequent'}`
- **`ICD10_CODES`**: `{'Z00.00': 'Encounter for general adult medical examination', 'E11.9': 'Type 2 diabetes mellitus without complications', 'I10': 'Essential (primary) hypertension', 'E78.5': 'Hyperlipidemia, unspecified', 'Z23': 'Encounter for immunization', 'R51.9': 'Headache, unspecified', 'J06.9': 'Acute upper respiratory infection', 'K21.9': 'Gastro-esophageal reflux disease', 'M79.3': 'Panniculitis, unspecified'}`

### Functions

#### `generate_fake_claim_number() -> str`

Generate a fake claim number.

#### `generate_fake_date(days_ago) -> str`

Generate a fake date in ISO format (YYYY-MM-DD).

#### `generate_fake_amount(min_amount, max_amount) -> float`

Generate a fake dollar amount.

#### `generate_realistic_claim_amounts() -> Dict[str, float]`

Generate realistic claim amounts with proper relationships.

Returns:
    Dict with billed_amount, allowed_amount, paid_by_insurance, patient_responsibility

#### `generate_npi() -> str`

Generate a fake but valid-looking NPI number (10 digits).

#### `generate_tax_id() -> str`

Generate a fake EIN/Tax ID (XX-XXXXXXX format).

#### `generate_fake_document(job_id, source_type, entity) -> Document`

Generate a fake ImportedDocument record.

Args:
    job_id: Import job ID
    source_type: Type of source (insurance_portal, provider_portal, etc.)
    entity: The healthcare entity (insurance or provider)

Returns:
    Document record

#### `generate_line_items_from_insurance(job_id, insurance_entity, num_items) -> List[NormalizedLineItem]`

Generate fake line items from an insurance EOB/claim.

Args:
    job_id: Import job ID
    insurance_entity: Insurance company entity
    num_items: Number of line items to generate (default 5)

Returns:
    List of NormalizedLineItem records

#### `generate_line_items_from_provider(job_id, provider_entity, num_items) -> List[NormalizedLineItem]`

Generate fake line items from a provider bill/statement.

Args:
    job_id: Import job ID
    provider_entity: Healthcare provider entity
    num_items: Number of line items to generate (default 3)

Returns:
    List of NormalizedLineItem records

#### `import_sample_data(selected_entity, num_line_items) -> ImportJob`

Generate fake healthcare data and prepare for storage.

This is the main ingestion function that:
1. Generates fake ImportedDocument records
2. Normalizes into NormalizedLineItem records
3. Packages everything into an ImportJob

The caller is responsible for storing the result in st.session_state.

Args:
    selected_entity: The insurance or provider entity selected by user
    num_line_items: Number of line items to generate (optional, uses defaults)

Returns:
    ImportJob with all generated documents and line items

Notes:
    - All records have source = "demo_sample"
    - No UI rendering occurs in this function
    - No actual API calls or file I/O

#### `extract_insurance_plan_from_entity(insurance_entity) -> InsurancePlan`

Extract an InsurancePlan record from an insurance entity.

Args:
    insurance_entity: Insurance company entity

Returns:
    InsurancePlan record

#### `extract_provider_from_entity(provider_entity) -> Provider`

Extract a Provider record from a provider entity.

Args:
    provider_entity: Healthcare provider entity

Returns:
    Provider record

#### `import_multiple_entities(entities, items_per_entity) -> List[ImportJob]`

Import data from multiple entities in batch.

Args:
    entities: List of insurance or provider entities
    items_per_entity: Number of line items to generate per entity

Returns:
    List of ImportJob records

#### `store_import_job_in_session(import_job, session_state_key) -> None`

Store ImportJob data in Streamlit session state.

This helper function handles the proper storage of import job data
in the session state structure expected by the profile editor.

Args:
    import_job: The import job to store
    session_state_key: Session state key (default: "health_profile")

Notes:
    This function DOES interact with st.session_state.
    It's separated here for clarity but uses Streamlit internally.


### Dependencies

- `_modules.data.fictional_entities`
- `_modules.ui.profile_editor`

## Module: `_modules.data.portal_templates`

**Source:** `_modules/data/portal_templates.py`

### Description

Simulated Healthcare Portal Templates

This module generates HTML templates for fictional insurance and provider portals.
ALL data is simulated and clearly marked as DEMO ONLY.

These templates are designed to be rendered in iframes to demonstrate
a Plaid-like connection experience without connecting to real systems.

### Functions

#### `generate_fake_claim_number() -> str`

Generate a fake claim number.

#### `generate_fake_date(days_ago) -> str`

Generate a fake date in the past.

#### `generate_fake_cpt_code() -> str`

Generate a fake CPT procedure code.

#### `generate_fake_amount() -> float`

Generate a fake dollar amount.

#### `generate_insurance_portal_html(company_name, member_id, plan_name) -> str`

Generate a simulated insurance company portal.

Args:
    company_name: Name of the fictional insurance company
    member_id: Fake member ID
    plan_name: Fake plan name

Returns:
    HTML string for insurance portal

#### `generate_provider_portal_html(provider_name, patient_name, account_number) -> str`

Generate a simulated healthcare provider portal.

Args:
    provider_name: Name of the fictional provider
    patient_name: Fake patient name
    account_number: Fake account number

Returns:
    HTML string for provider portal

#### `generate_pharmacy_portal_html(pharmacy_name, patient_name, rx_number) -> str`

Generate a simulated pharmacy portal.

Args:
    pharmacy_name: Name of the fictional pharmacy
    patient_name: Fake patient name
    rx_number: Fake prescription number

Returns:
    HTML string for pharmacy portal


## Module: `_modules.extractors.extraction_prompt`

**Source:** `_modules/extractors/extraction_prompt.py`

### Description

Core fact extraction prompt builder.

Provides provider-agnostic prompts for extracting structured facts from
healthcare documents including bills, receipts, and claim histories.

### Functions

#### `_load_contextual_docs() -> str`

Load contextual documentation files to help guide the LLM.

Loads HAI-DEF alignment, competitive landscape, and cost analysis docs
to provide context about medBillDozer's purpose and methodology.

Returns:
    str: Concatenated documentation content or empty string if files not found

#### `build_fact_extraction_prompt(document_text, include_context) -> str`

Build provider-agnostic prompt for structured healthcare fact extraction.

Compatible with OpenAI, Gemini, MedGemma, or local LLMs.
Optionally includes contextual documentation about medBillDozer's purpose.

Args:
    document_text: Raw document text
    include_context: Whether to include contextual documentation (default: True)

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

## Module: `_modules.ingest.api`

**Source:** `_modules/ingest/api.py`

### Description

Demo-Only Healthcare Data Ingestion API

This module provides API-style functions for ingesting healthcare data
from fictional entities and retrieving normalized results.

IMPORTANT: This is a DEMO-ONLY interface with no real networking,
authentication, or HIPAA compliance. It's designed to demonstrate
how a Plaid-like healthcare data connector API might work.

Future Deployment: These functions could be exposed via FastAPI:
    - POST /api/v1/ingest/document -> ingest_document()
    - GET /api/v1/imports?user_id=xxx -> list_imports()
    - GET /api/v1/data?user_id=xxx -> get_normalized_data()
    - GET /api/v1/imports/{job_id} -> get_import_status()

Authentication (Future): Would use OAuth 2.0 or API keys
Storage (Current): In-memory dictionary (replace with database in production)

### Classes

#### `IngestRequest`

Request payload for document ingestion.

This represents the data a client application would send to ingest
healthcare data from a connected entity.

Future FastAPI equivalent:
    class IngestRequest(BaseModel):
        user_id: str
        entity_type: Literal["insurance", "provider"]
        entity_id: str
        raw_text: Optional[str] = None
        metadata: Dict[str, Any] = Field(default_factory=dict)

**Attributes:**
- `user_id`
- `entity_type`
- `entity_id`
- `raw_text`
- `metadata`
- `num_line_items`

**Methods:**

- **`validate(self) -> List[str]`**
  - Validate request payload.

#### `IngestResponse`

Response from document ingestion.

Future FastAPI equivalent:
    class IngestResponse(BaseModel):
        success: bool
        job_id: str
        message: str
        documents_created: int
        line_items_created: int
        timestamp: str

**Attributes:**
- `success`
- `job_id`
- `message`
- `documents_created`
- `line_items_created`
- `timestamp`
- `errors`

#### `ImportSummary`

Summary of an import job.

Used in list_imports() response.

**Attributes:**
- `job_id`
- `user_id`
- `entity_type`
- `entity_id`
- `entity_name`
- `status`
- `documents_count`
- `line_items_count`
- `created_at`
- `completed_at`

#### `ImportListResponse`

Response from list_imports().

Future FastAPI equivalent:
    class ImportListResponse(BaseModel):
        success: bool
        user_id: str
        total_imports: int
        imports: List[ImportSummary]

**Attributes:**
- `success`
- `user_id`
- `total_imports`
- `imports`

#### `NormalizedDataResponse`

Response from get_normalized_data().

Returns all normalized line items for a user.

Future FastAPI equivalent:
    class NormalizedDataResponse(BaseModel):
        success: bool
        user_id: str
        total_line_items: int
        line_items: List[Dict[str, Any]]
        metadata: Dict[str, Any]

**Attributes:**
- `success`
- `user_id`
- `total_line_items`
- `line_items`
- `metadata`

#### `ImportStatusResponse`

Response from get_import_status().

Returns detailed status of a specific import job.

Future FastAPI equivalent:
    class ImportStatusResponse(BaseModel):
        success: bool
        job_id: str
        status: ImportStatus
        import_job: Dict[str, Any]

**Attributes:**
- `success`
- `job_id`
- `status`
- `import_job`
- `error_message`

#### `InMemoryStorage`

In-memory storage for import jobs.

Thread-safe operations would be needed in production.
In a real deployment, this would be:
- SQLAlchemy models + PostgreSQL
- MongoDB collections
- Redis cache for session data

**Methods:**

- **`__init__(self)`**

- **`store_import(self, user_id, import_job) -> None`**
  - Store an import job.

- **`get_imports_by_user(self, user_id) -> List[Dict[str, Any]]`**
  - Get all imports for a user.

- **`get_import_by_job_id(self, job_id) -> Optional[Dict[str, Any]]`**
  - Get a specific import job by ID.

- **`get_all_line_items_by_user(self, user_id) -> List[Dict[str, Any]]`**
  - Get all line items across all imports for a user.

- **`clear(self) -> None`**
  - Clear all storage (for testing).


### Functions

#### `ingest_document(payload) -> IngestResponse`

Ingest a healthcare document and normalize the data.

This is the main ingestion endpoint. It accepts a payload with entity
information and generates normalized line items using the existing
ingestion logic.

Args:
    payload: Dictionary matching IngestRequest schema

Returns:
    IngestResponse with job_id and results

Example:
    >>> payload = {
    ...     "user_id": "demo_user_123",
    ...     "entity_type": "insurance",
    ...     "entity_id": "demo_ins_001",
    ...     "metadata": {"source": "web_app"}
    ... }
    >>> response = ingest_document(payload)
    >>> response.success
    True
    >>> response.job_id
    'uuid-...'

Future FastAPI deployment:
    @app.post("/api/v1/ingest/document", response_model=IngestResponse)
    async def api_ingest_document(request: IngestRequest):
        return ingest_document(request.dict())

#### `list_imports(user_id) -> ImportListResponse`

List all import jobs for a user.

Args:
    user_id: User identifier

Returns:
    ImportListResponse with list of import summaries

Example:
    >>> response = list_imports("demo_user_123")
    >>> response.total_imports
    3
    >>> response.imports[0].entity_name
    'Beacon Life (DEMO)'

Future FastAPI deployment:
    @app.get("/api/v1/imports", response_model=ImportListResponse)
    async def api_list_imports(user_id: str):
        return list_imports(user_id)

#### `get_normalized_data(user_id, job_id) -> NormalizedDataResponse`

Get normalized line items for a user.

If job_id is provided, returns line items for that specific job.
Otherwise, returns all line items across all jobs.

Args:
    user_id: User identifier
    job_id: Optional import job ID to filter by

Returns:
    NormalizedDataResponse with line items

Example:
    >>> response = get_normalized_data("demo_user_123")
    >>> response.total_line_items
    15
    >>> response.line_items[0]['procedure_code']
    '99213'

Future FastAPI deployment:
    @app.get("/api/v1/data", response_model=NormalizedDataResponse)
    async def api_get_normalized_data(
        user_id: str,
        job_id: Optional[str] = None
    ):
        return get_normalized_data(user_id, job_id)

#### `get_import_status(job_id) -> ImportStatusResponse`

Get status of a specific import job.

Args:
    job_id: Import job identifier

Returns:
    ImportStatusResponse with job details

Example:
    >>> response = get_import_status("uuid-...")
    >>> response.status
    'completed'
    >>> response.import_job['line_items_count']
    5

Future FastAPI deployment:
    @app.get("/api/v1/imports/{job_id}", response_model=ImportStatusResponse)
    async def api_get_import_status(job_id: str):
        return get_import_status(job_id)

#### `clear_storage() -> None`

Clear all stored data (for testing).

In production, this would not be exposed as an API endpoint.

#### `get_storage_stats() -> Dict[str, Any]`

Get statistics about stored data (for debugging).

Example:
    >>> stats = get_storage_stats()
    >>> stats['total_users']
    5


### Dependencies

- `_modules.data.fictional_entities`
- `_modules.data.health_data_ingestion`

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
Also stores message in session state transcript.

#### `render_billdozer_sidebar_widget()`

Render billdozer widget in sidebar with bubble styling.


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

Render contextual help banners with a dismiss button.
Safe against multiple renders in a single Streamlit run.


### Dependencies

- `_modules.utils.image_paths`

## Module: `_modules.ui.guided_tour`

**Source:** `_modules/ui/guided_tour.py`

### Description

Guided Tour - Interactive tutorial using Intro.js.

Provides step-by-step guidance for first-time users through the app's
main features using the Intro.js library.

### Functions

#### `initialize_tour_state()`

Initialize tour-related session state variables.

#### `maybe_launch_tour()`

Launch tour if conditions are met (called after splash screen).

#### `install_introjs_library()`

Install Intro.js CSS and JS files into parent document.

#### `render_tour_steps()`

Add data-intro attributes to elements for the guided tour.

#### `start_introjs_tour()`

Start the Intro.js tour.

#### `run_guided_tour_runtime()`

Runs guided tour using Intro.js.
Call ONCE per rerun, AFTER main UI render.

#### `activate_tour()`

Activate the guided tour (called after splash screen dismissal).

#### `check_tour_progression()`

Compatibility - no longer needed with Intro.js.

#### `render_tour_widget()`

Compatibility - Intro.js handles tour UI.

#### `render_tour_controls()`

Compatibility - Intro.js handles controls.

#### `advance_tour_step()`

Compatibility - Intro.js handles step advancement.

#### `open_sidebar_for_tour()`

Compatibility - manual sidebar control if needed.

#### `install_paste_detector()`

Compatibility - no longer needed.

#### `install_copy_button_detector()`

Compatibility - no longer needed.

#### `check_pharmacy_copy_click()`

Compatibility - no longer needed.

#### `install_tour_highlight_styles()`

Compatibility - Intro.js handles highlighting.

#### `highlight_tour_elements()`

Compatibility - Intro.js handles highlighting.

#### `open_and_scroll_pipeline_workflow_step6()`

Compatibility - Intro.js handles scrolling.


## Module: `_modules.ui.health_profile`

**Source:** `_modules/ui/health_profile.py`

### Description

Health profile management for policy holder and dependents.

Provides pre-loaded patient profiles with medical history, insurance details,
and demographic information for demo and testing purposes.

### Constants

- **`SAMPLE_PROFILES`**: `{'policyholder': {'id': 'PH-001', 'name': 'John Sample', 'date_of_birth': '01/15/1975', 'age': 51, 'gender': 'Male', 'relationship': 'Policy Holder', 'insurance': {'provider': 'Horizon PPO Plus', 'member_id': 'HPP-8743920', 'group_number': 'G-1234567', 'plan_type': 'PPO', 'effective_date': '01/01/2025', 'deductible_annual': 1500.0, 'deductible_met': 1500.0, 'oop_max': 3000.0, 'oop_met': 1500.0, 'in_network_providers': ['Valley Medical Center', 'Dr. Sarah Mitchell', 'Dr. Michael Reynolds', 'HealthFirst Medical Group', 'BrightSmile Dental', 'Dr. Laura Chen, DDS'], 'out_of_network_providers': ['GreenLeaf Pharmacy', 'QuickCare Urgent Care'], 'in_network_codes': [{'code': '99213', 'description': 'Office Visit - Established Patient (15 min)', 'accepted_fee': 125.0}, {'code': '99214', 'description': 'Office Visit - Established Patient (25 min)', 'accepted_fee': 185.0}, {'code': '99215', 'description': 'Office Visit - Established Patient (40 min)', 'accepted_fee': 245.0}, {'code': '45378', 'description': 'Colonoscopy - Diagnostic', 'accepted_fee': 1200.0}, {'code': '80053', 'description': 'Comprehensive Metabolic Panel', 'accepted_fee': 45.0}, {'code': '85025', 'description': 'Complete Blood Count (CBC)', 'accepted_fee': 35.0}, {'code': '93000', 'description': 'Electrocardiogram (EKG)', 'accepted_fee': 85.0}, {'code': '71045', 'description': 'Chest X-Ray - Single View', 'accepted_fee': 120.0}], 'out_of_network_codes': [{'code': '99213', 'description': 'Office Visit - Established Patient (15 min)', 'accepted_fee': 100.0}, {'code': '99214', 'description': 'Office Visit - Established Patient (25 min)', 'accepted_fee': 148.0}, {'code': '99215', 'description': 'Office Visit - Established Patient (40 min)', 'accepted_fee': 196.0}, {'code': '45378', 'description': 'Colonoscopy - Diagnostic', 'accepted_fee': 960.0}, {'code': '80053', 'description': 'Comprehensive Metabolic Panel', 'accepted_fee': 36.0}, {'code': '85025', 'description': 'Complete Blood Count (CBC)', 'accepted_fee': 28.0}, {'code': '93000', 'description': 'Electrocardiogram (EKG)', 'accepted_fee': 68.0}, {'code': '71045', 'description': 'Chest X-Ray - Single View', 'accepted_fee': 96.0}]}, 'medical_history': {'conditions': ['Hypertension (controlled)', 'Type 2 Diabetes', 'Hyperlipidemia'], 'medications': ['Lisinopril 10mg daily', 'Metformin 500mg twice daily', 'Atorvastatin 20mg at bedtime'], 'allergies': ['Penicillin (rash)', 'Sulfa drugs (hives)'], 'recent_procedures': [{'date': '01/12/2026', 'procedure': 'Screening Colonoscopy', 'provider': 'Valley Medical Center', 'cpt_code': '45378', 'cost': 1200.0, 'out_of_pocket': 100.0}, {'date': '11/05/2025', 'procedure': 'Annual Physical Exam', 'provider': 'Dr. Sarah Mitchell', 'cpt_code': '99396', 'cost': 350.0, 'out_of_pocket': 0.0}], 'upcoming_appointments': [{'date': '03/15/2026', 'type': 'Follow-up', 'provider': 'Dr. Michael Reynolds', 'reason': 'Post-colonoscopy review'}]}, 'fsa_hsa': {'account_type': 'FSA', 'plan_year': 2026, 'annual_contribution': 2850.0, 'balance_remaining': 2247.5, 'claims_submitted': 5, 'claims_approved': 4, 'claims_pending': 0, 'claims_denied': 1, 'eligible_expenses': ['Medical copays and deductibles', 'Prescription medications', 'Dental treatments and cleanings', 'Vision exams and eyeglasses', 'Contact lenses and solution', 'Over-the-counter medications (with prescription)', 'Medical equipment (blood pressure monitors, diabetic supplies)', 'Physical therapy copays', 'Chiropractic services', 'Mental health services', 'Laboratory tests and diagnostic services', 'Hearing aids and batteries', 'Orthodontia (braces)', 'Wheelchair and mobility aids', 'First aid supplies', 'Sunscreen (SPF 15+)', 'Prenatal vitamins (with prescription)', 'Smoking cessation programs', 'Weight loss programs (for specific medical conditions)'], 'ineligible_expenses': ['Vitamins and supplements (without prescription)', 'Cosmetic procedures', 'Gym memberships (unless prescribed)', 'Health club dues', 'Cosmetic dentistry (teeth whitening)', 'Hair transplants', 'Nutritional supplements']}}, 'dependent': {'id': 'DEP-001', 'name': 'Jane Sample', 'date_of_birth': '08/22/1986', 'age': 39, 'gender': 'Female', 'relationship': 'Spouse', 'insurance': {'provider': 'Horizon PPO Plus', 'member_id': 'HPP-8743921', 'group_number': 'G-1234567', 'plan_type': 'PPO', 'effective_date': '01/01/2025', 'deductible_annual': 1500.0, 'deductible_met': 450.0, 'oop_max': 3000.0, 'oop_met': 850.0, 'in_network_providers': ['Valley Medical Center', 'Dr. Sarah Mitchell', 'Dr. Michael Reynolds', 'HealthFirst Medical Group', 'BrightSmile Dental', 'Dr. Laura Chen, DDS', 'Dr. Jennifer Adams'], 'out_of_network_providers': ['GreenLeaf Pharmacy', 'QuickCare Urgent Care'], 'in_network_codes': [{'code': '99213', 'description': 'Office Visit - Established Patient (15 min)', 'accepted_fee': 125.0}, {'code': '99214', 'description': 'Office Visit - Established Patient (25 min)', 'accepted_fee': 185.0}, {'code': '99215', 'description': 'Office Visit - Established Patient (40 min)', 'accepted_fee': 245.0}, {'code': '45378', 'description': 'Colonoscopy - Diagnostic', 'accepted_fee': 1200.0}, {'code': '80053', 'description': 'Comprehensive Metabolic Panel', 'accepted_fee': 45.0}, {'code': '85025', 'description': 'Complete Blood Count (CBC)', 'accepted_fee': 35.0}, {'code': '93000', 'description': 'Electrocardiogram (EKG)', 'accepted_fee': 85.0}, {'code': '71045', 'description': 'Chest X-Ray - Single View', 'accepted_fee': 120.0}], 'out_of_network_codes': [{'code': '99213', 'description': 'Office Visit - Established Patient (15 min)', 'accepted_fee': 100.0}, {'code': '99214', 'description': 'Office Visit - Established Patient (25 min)', 'accepted_fee': 148.0}, {'code': '99215', 'description': 'Office Visit - Established Patient (40 min)', 'accepted_fee': 196.0}, {'code': '45378', 'description': 'Colonoscopy - Diagnostic', 'accepted_fee': 960.0}, {'code': '80053', 'description': 'Comprehensive Metabolic Panel', 'accepted_fee': 36.0}, {'code': '85025', 'description': 'Complete Blood Count (CBC)', 'accepted_fee': 28.0}, {'code': '93000', 'description': 'Electrocardiogram (EKG)', 'accepted_fee': 68.0}, {'code': '71045', 'description': 'Chest X-Ray - Single View', 'accepted_fee': 96.0}]}, 'medical_history': {'conditions': ['Seasonal Allergies', 'Mild Asthma (controlled)'], 'medications': ['Cetirizine 10mg as needed', 'Albuterol inhaler as needed', 'Multivitamin daily'], 'allergies': ['Shellfish (anaphylaxis)', 'Cat dander'], 'recent_procedures': [{'date': '01/20/2026', 'procedure': 'Dental Crown (Tooth #14)', 'provider': 'BrightSmile Dental', 'cdt_code': 'D2740', 'cost': 2500.0, 'out_of_pocket': 1625.0}, {'date': '01/18/2026', 'procedure': 'Prescription Refill', 'provider': 'GreenLeaf Pharmacy', 'medication': 'Albuterol Inhaler', 'cost': 45.0, 'out_of_pocket': 15.0}, {'date': '10/12/2025', 'procedure': 'Annual Gynecological Exam', 'provider': 'Dr. Jennifer Adams', 'cpt_code': '99385', 'cost': 285.0, 'out_of_pocket': 0.0}], 'upcoming_appointments': [{'date': '02/28/2026', 'type': 'Dental Follow-up', 'provider': 'Dr. Laura Chen, DDS', 'reason': 'Crown check-up'}, {'date': '04/10/2026', 'type': 'Annual Physical', 'provider': 'Dr. Sarah Mitchell', 'reason': 'Preventive care'}]}, 'fsa_hsa': {'account_type': 'FSA', 'plan_year': 2026, 'annual_contribution': 2850.0, 'balance_remaining': 2247.5, 'claims_submitted': 5, 'claims_approved': 4, 'claims_pending': 0, 'claims_denied': 1, 'eligible_expenses': ['Medical copays and deductibles', 'Prescription medications', 'Dental treatments and cleanings', 'Vision exams and eyeglasses', 'Contact lenses and solution', 'Over-the-counter medications (with prescription)', 'Medical equipment (blood pressure monitors, diabetic supplies)', 'Physical therapy copays', 'Chiropractic services', 'Mental health services', 'Laboratory tests and diagnostic services', 'Hearing aids and batteries', 'Orthodontia (braces)', 'Wheelchair and mobility aids', 'First aid supplies', 'Sunscreen (SPF 15+)', 'Prenatal vitamins (with prescription)', 'Smoking cessation programs', 'Weight loss programs (for specific medical conditions)'], 'ineligible_expenses': ['Vitamins and supplements (without prescription)', 'Cosmetic procedures', 'Gym memberships (unless prescribed)', 'Health club dues', 'Cosmetic dentistry (teeth whitening)', 'Hair transplants', 'Nutritional supplements']}}}`

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


## Module: `_modules.ui.profile_editor`

**Source:** `_modules/ui/profile_editor.py`

### Description

Profile Editor - User identity, insurance, and provider management with importer.

Provides a Plaid-like experience for importing health insurance and provider data,
with structured field extraction and normalization into a consistent schema.

### Classes

#### `UserProfile`

**Inherits from:** `TypedDict`

User identity information.

**Attributes:**
- `user_id`
- `full_name`
- `date_of_birth`
- `email`
- `phone`
- `address`
- `created_at`
- `updated_at`

#### `InsurancePlan`

**Inherits from:** `TypedDict`

Health insurance plan details.

**Attributes:**
- `plan_id`
- `carrier_name`
- `plan_name`
- `member_id`
- `group_number`
- `policy_holder`
- `effective_date`
- `termination_date`
- `plan_type`
- `deductible`
- `out_of_pocket_max`
- `copay`
- `coinsurance`
- `created_at`
- `updated_at`

#### `Provider`

**Inherits from:** `TypedDict`

Healthcare provider information.

**Attributes:**
- `provider_id`
- `name`
- `specialty`
- `npi`
- `tax_id`
- `address`
- `phone`
- `fax`
- `in_network`
- `created_at`
- `updated_at`

#### `NormalizedLineItem`

**Inherits from:** `TypedDict`

Normalized billing line item from imported documents.

**Attributes:**
- `line_item_id`
- `import_job_id`
- `service_date`
- `procedure_code`
- `procedure_description`
- `provider_name`
- `provider_npi`
- `billed_amount`
- `allowed_amount`
- `paid_by_insurance`
- `patient_responsibility`
- `claim_number`
- `created_at`

#### `Document`

**Inherits from:** `TypedDict`

Uploaded or imported document metadata.

**Attributes:**
- `document_id`
- `import_job_id`
- `file_name`
- `file_path`
- `file_type`
- `raw_text`
- `status`
- `created_at`

#### `ImportJob`

**Inherits from:** `TypedDict`

Import job tracking.

**Attributes:**
- `job_id`
- `source_type`
- `source_method`
- `status`
- `documents`
- `line_items`
- `created_at`
- `completed_at`
- `error_message`


### Functions

#### `is_profile_editor_enabled() -> bool`

Check if profile editor is enabled via environment variable.

#### `is_importer_enabled() -> bool`

Check if importer feature is enabled via environment variable.

#### `get_data_dir() -> Path`

Get or create data directory for profile storage.

#### `atomic_write_json(file_path, data) -> None`

Atomically write JSON data to file using temp file + rename.

#### `load_profile() -> Optional[UserProfile]`

Load user profile from disk.

#### `save_profile(profile) -> None`

Save user profile to disk with atomic write.

#### `load_insurance_plans() -> List[InsurancePlan]`

Load insurance plans from disk.

#### `save_insurance_plans(plans) -> None`

Save insurance plans to disk with atomic write.

#### `load_providers() -> List[Provider]`

Load providers from disk.

#### `save_providers(providers) -> None`

Save providers to disk with atomic write.

#### `load_import_jobs() -> List[ImportJob]`

Load import jobs from disk.

#### `save_import_jobs(jobs) -> None`

Save import jobs to disk with atomic write.

#### `load_line_items() -> List[NormalizedLineItem]`

Load normalized line items from disk.

#### `save_line_items(items) -> None`

Save normalized line items to disk with atomic write.

#### `initialize_profile_state()`

Initialize profile editor session state variables.

#### `render_profile_overview()`

Render profile overview page with quick stats and actions.

#### `render_identity_editor()`

Render user identity editor form.

#### `render_insurance_editor()`

Render insurance plan management interface.

#### `render_insurance_plan_form(plans)`

Render insurance plan edit/create form.

#### `render_provider_editor()`

Render healthcare provider management interface.

#### `render_provider_form(providers)`

Render provider edit/create form.

#### `render_importer_step1()`

Render Step 1: Choose entity to import from (entity picker).

#### `render_importer_step2()`

Render Step 2: Display imported results.

#### `render_pdf_upload()`

Render PDF upload interface.

#### `render_csv_upload()`

Render CSV upload interface.

#### `render_text_paste()`

Render text paste interface.

#### `extract_and_normalize_data()`

Extract structured data from import input and normalize to line items.

This is a placeholder that demonstrates the extraction flow.
In production, this would integrate with your existing extraction pipeline.

#### `render_importer_step3()`

Render Step 3: Preview extracted data and allow inline edits.

#### `save_import_job()`

Save the import job and normalized line items to disk.

#### `render_importer_step4()`

Render Step 4: Success confirmation.

#### `render_importer()`

Render importer wizard based on current step.

#### `render_profile_editor()`

Main entry point for profile editor interface.

Provides navigation between different profile sections and
the data importer wizard.


## Module: `_modules.ui.splash_screen`

**Source:** `_modules/ui/splash_screen.py`

### Description

Splash Screen - Welcome screen with Billdozer introduction.

Shows a fullscreen welcome screen with Billy and Billie explaining the app
when GUIDED_TOUR=TRUE. Animation runs once and user can dismiss to proceed.

### Functions

#### `should_show_splash_screen() -> bool`

Check if splash screen should be shown.

Returns:
    bool: True if splash screen has not been dismissed yet

#### `dismiss_splash_screen()`

Mark splash screen as dismissed.

#### `render_splash_screen()`

Render fullscreen splash screen with Billdozer widget.

Shows Billy and Billie introducing the app with animation.
User can click dismiss button to proceed to main app.


### Dependencies

- `_modules.ui.billdozer_widget`

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
Opens sidebar by default if guided tour is active.

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
Shows a brief success message after copying.

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

#### `render_clear_history_button() -> bool`

Render a button to clear analysis history.

Returns:
    bool: True if button was clicked, False otherwise

#### `clear_analysis_history()`

Clear all analysis-related data from session state.

Removes:
- Analysis results and workflow logs
- Extracted facts and normalized transactions
- Aggregate metrics and savings data
- Billdozer widget state

#### `render_results(result)`

Render analysis results including flagged issues and savings breakdown.

Args:
    result: AnalysisResult object or dict containing issues and metadata

#### `render_footer()`

Render application footer with disclaimer.


### Dependencies

- `_modules.ui.ui_pipeline_dag`
- `_modules.utils.image_paths`
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

#### `_build_initial_plan_html() -> str`

Build HTML showing the initial analysis plan with all steps in pending state.

#### `update_pipeline_dag(placeholder, workflow_log, document_id, step_status)`

Update an existing pipeline DAG placeholder with current workflow state.

Args:
    placeholder: Streamlit placeholder object to update
    workflow_log: Current workflow log dict with pipeline stages
    document_id: Optional friendly document identifier for display
    step_status: Optional current step status ('pre_extraction_active', 'extraction_active', 'line_items_active', 'analysis_active', 'complete')

#### `_build_progress_html(pre_extraction, extraction, analysis, step_status) -> str`

Build HTML showing progressive analysis status with current step highlighted.

Args:
    pre_extraction: Pre-extraction stage data
    extraction: Extraction stage data
    analysis: Analysis stage data
    step_status: Current step ('pre_extraction_active', 'extraction_active', 'line_items_active', 'analysis_active', 'complete')

Returns:
    HTML string with styled progress visualization

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

#### `is_guided_tour_enabled() -> bool`

Check if guided tour feature is enabled.

#### `is_privacy_ui_enabled() -> bool`

Check if privacy UI is enabled.

#### `is_coverage_matrix_enabled() -> bool`

Check if coverage matrix feature is enabled.


## Module: `_modules.utils.image_paths`

**Source:** `_modules/utils/image_paths.py`

### Description

Image path utilities for handling local vs production CDN URLs.

Provides functionality to determine if the app is running locally and return
appropriate image paths (local static files vs GitHub CDN URLs).

### Functions

#### `is_local_environment() -> bool`

Check if the app is running in a local environment.

Returns:
    bool: True if running on localhost/127.0.0.1 or any IP address, False otherwise

#### `get_image_url(relative_path) -> str`

Get the appropriate image URL based on environment.

Args:
    relative_path: Relative path from project root (e.g., 'images/avatars/billy.png')

Returns:
    str: Full GitHub CDN URL (works for both local and production)

Example:
    >>> get_image_url('images/avatars/billie__eyes_open__ready.png')
    # Returns: 'https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static/images/avatars/billie__eyes_open__ready.png'

#### `get_avatar_url(avatar_filename) -> str`

Get the appropriate avatar image URL.

Args:
    avatar_filename: Just the filename (e.g., 'billie__eyes_open__ready.png')

Returns:
    str: Full URL for the avatar image

#### `get_transparent_avatar_url(avatar_filename) -> str`

Get the appropriate transparent avatar image URL.

Args:
    avatar_filename: Just the filename (e.g., 'billie__eyes_closed__billdozer_down.png')

Returns:
    str: Full URL for the transparent avatar image


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

#### `check_access_password() -> bool`

Check if access password is required and validate user input.

Returns:
    bool: True if access is granted, False if password gate should be shown

#### `should_enable_guided_tour() -> bool`

Check if guided tour should be enabled based on environment variable.

Returns:
    bool: True if tour should be enabled

#### `render_total_savings_summary(total_potential_savings, per_document_savings)`

Render aggregate savings summary across all analyzed documents.

Args:
    total_potential_savings: Total potential savings amount
    per_document_savings: Dict mapping document IDs to their savings amounts

#### `bootstrap_ui_minimal()`

Initialize minimal UI components for all pages.

Sets up page configuration, CSS styles, and header.
Should be called on all pages (home and profile).

#### `bootstrap_home_page()`

Initialize home page specific UI components.

Renders demo documents and contextual help.
Should only be called on the home page.

#### `register_providers()`

Register available LLM analysis providers.

Attempts to register MedGemma, Gemini, and OpenAI providers.
Only registers providers that pass health checks.

#### `main()`

Main application entry point.

Orchestrates the complete workflow:
1. Bootstrap UI and register providers
2. Initialize guided tour state
3. Render privacy dialog
4. Collect document inputs
5. Analyze documents with selected provider
6. Display results and savings summary
7. Render coverage matrix and debug info


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
- `_modules.ui.guided_tour`
- `_modules.ui.health_profile`
- `_modules.ui.privacy_ui`
- `_modules.ui.profile_editor`
- `_modules.ui.splash_screen`
- `_modules.ui.ui`
- `_modules.ui.ui_coverage_matrix`
- `_modules.ui.ui_documents`
- `_modules.ui.ui_pipeline_dag`
- `_modules.utils.config`
- `_modules.utils.runtime_flags`
- `_modules.utils.serialization`
