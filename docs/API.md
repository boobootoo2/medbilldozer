## API Reference

Public interfaces and their usage patterns.

### Data Ingestion API

**Module:** `medbilldozer.ingest.api`

The ingestion API provides functions for importing healthcare data from fictional entities (insurance companies and providers) and retrieving normalized billing information.

#### Core Functions

##### `ingest_document(payload: Dict[str, Any]) -> IngestResponse`

Ingests a healthcare document from a fictional entity.

**Parameters:**
- `payload` (Dict): Contains:
  - `user_id` (str): Unique user identifier
  - `entity_type` (str): Either "insurance" or "provider"
  - `entity_id` (str): Entity identifier from fictional entities database
  - `raw_text` (Optional[str]): Raw document text (auto-generated if None)
  - `metadata` (Optional[Dict]): Additional metadata
  - `num_line_items` (Optional[int]): Number of line items to generate

**Returns:** `IngestResponse` with:
- `job_id` (str): Unique import job identifier
- `status` (str): "completed" or "failed"
- `message` (str): Status message
- `line_items_count` (int): Number of imported line items
- `errors` (List[str]): Any validation errors

**Example:**
```python
from medbilldozer.ingest.api import ingest_document

response = ingest_document({
    "user_id": "user_123",
    "entity_type": "insurance",
    "entity_id": "ins_001",
    "num_line_items": 5
})
print(f"Import job: {response.job_id}")
```

##### `list_imports(user_id: str) -> ImportListResponse`

Retrieve all import jobs for a specific user.

**Parameters:**
- `user_id` (str): User identifier

**Returns:** `ImportListResponse` with:
- `user_id` (str): User identifier
- `imports` (List[ImportSummary]): List of import summaries
- `total_count` (int): Total number of imports

##### `get_normalized_data(user_id: str, job_id: Optional[str] = None) -> NormalizedDataResponse`

Retrieve normalized billing data for a user.

**Parameters:**
- `user_id` (str): User identifier
- `job_id` (Optional[str]): Specific import job ID (returns all if None)

**Returns:** `NormalizedDataResponse` with:
- `user_id` (str): User identifier
- `line_items` (List[Dict]): Normalized line items
- `total_count` (int): Total number of line items
- `job_ids` (List[str]): Related job IDs

##### `get_import_status(job_id: str) -> ImportStatusResponse`

Get status of a specific import job.

**Parameters:**
- `job_id` (str): Import job identifier

**Returns:** `ImportStatusResponse` with job details and status.

---

### Extraction API

**Module:** `medbilldozer.extractors`

#### OpenAI Extraction

##### `extract_facts_openai(raw_text: str) -> Dict[str, Optional[str]]`

Extract structured facts from raw document text using OpenAI.

**Parameters:**
- `raw_text` (str): Raw document text

**Returns:** Dictionary with extracted facts:
- `claim_number`, `service_date`, `provider_name`, `billed_amount`, etc.

##### `run_prompt_openai(prompt: str) -> str`

Run a custom prompt through OpenAI.

**Parameters:**
- `prompt` (str): Custom prompt text

**Returns:** Model response as string

#### Gemini Extraction

##### `extract_facts_gemini(raw_text: str) -> Dict[str, Optional[str]]`

Extract structured facts using Google Gemini.

**Parameters:**
- `raw_text` (str): Raw document text

**Returns:** Dictionary with extracted facts

##### `run_prompt_gemini(prompt: str) -> str`

Run a custom prompt through Gemini.

---

### Fictional Entities API

**Module:** `medbilldozer.data.fictional_entities`

##### `get_all_fictional_entities(insurance_count: int = 30, provider_count: int = 50, seed: int = 42) -> Dict`

Generate all fictional healthcare entities.

**Parameters:**
- `insurance_count` (int): Number of insurance companies
- `provider_count` (int): Number of healthcare providers
- `seed` (int): Random seed for reproducibility

**Returns:** Dictionary with:
- `insurance_companies` (List[InsuranceCompany])
- `healthcare_providers` (List[HealthcareProvider])

##### `get_entity_by_id(entity_id: str, entities: List[HealthcareEntity]) -> Optional[HealthcareEntity]`

Find entity by ID.

##### `filter_providers_by_specialty(providers: List[HealthcareProvider], specialty: str) -> List[HealthcareProvider]`

Filter providers by medical specialty.

##### `filter_providers_by_insurance(providers: List[HealthcareProvider], insurance_id: str) -> List[HealthcareProvider]`

Filter providers that accept a specific insurance.

---

### Utilities API

**Module:** `medbilldozer.utils`

#### Sanitization (`medbilldozer.utils.sanitize`)

##### `sanitize_text(text: Any, allow_newlines: bool = True) -> str`

Sanitize user input text.

##### `sanitize_html_content(content: Any, max_length: Optional[int] = None) -> str`

Sanitize HTML content.

##### `sanitize_dict(data: dict, keys_to_sanitize: Optional[list] = None) -> dict`

Sanitize dictionary values.

##### `sanitize_amount(amount: Any) -> float`

Sanitize and validate monetary amounts.

##### `sanitize_date(date: Any) -> str`

Sanitize and validate date strings.

#### Configuration (`medbilldozer.utils.config`)

##### `AppConfig(config_path: Optional[Path] = None)`

Application configuration manager.

**Methods:**
- `get(key_path: str, default: Any = None) -> Any`: Get config value by path

**Example:**
```python
from medbilldozer.utils.config import AppConfig

config = AppConfig()
model_name = config.get("model.name", "gpt-4")
```

---

### Analysis Providers API

**Module:** `medbilldozer.providers`

#### `OpenAIAnalysisProvider`

OpenAI-based analysis provider.

**Methods:**
- `analyze(context: Dict) -> AnalysisResult`: Run billing analysis

#### `MedGemmaEnsembleProvider`

MedGemma ensemble analysis provider.

**Methods:**
- `analyze(context: Dict) -> AnalysisResult`: Run ensemble analysis

---

### Future: FastAPI REST Endpoints

These functions are designed to be easily exposed as REST endpoints:

```python
from fastapi import FastAPI
from medbilldozer.ingest.api import (
    IngestRequestModel,
    api_ingest_document,
    api_list_imports,
    api_get_normalized_data,
    api_get_import_status
)

app = FastAPI()

app.post("/api/v1/ingest/document")(api_ingest_document)
app.get("/api/v1/imports")(api_list_imports)
app.get("/api/v1/data")(api_get_normalized_data)
app.get("/api/v1/imports/{job_id}")(api_get_import_status)
```

**Note:** Current implementation is demo-only with in-memory storage. Production deployment would require:
- Database persistence (PostgreSQL, MongoDB)
- OAuth 2.0 authentication
- HIPAA compliance measures
- Rate limiting and API keys
- Audit logging
