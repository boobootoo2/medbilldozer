# Ingestion API - Quick Reference

## Import

```python
from _modules.ingest.api import (
    ingest_document,
    list_imports,
    get_normalized_data,
    get_import_status
)
```

## Basic Usage

### Ingest Document

```python
payload = {
    "user_id": "demo_user_123",
    "entity_type": "insurance",      # or "provider"
    "entity_id": "demo_ins_001",
    "num_line_items": 5              # optional
}

response = ingest_document(payload)
# response.success → bool
# response.job_id → str
# response.line_items_created → int
```

### List Imports

```python
response = list_imports("demo_user_123")
# response.total_imports → int
# response.imports → List[ImportSummary]
```

### Get Data

```python
# All data for user
response = get_normalized_data("demo_user_123")

# Filtered by job
response = get_normalized_data("demo_user_123", job_id="uuid-...")

# response.total_line_items → int
# response.line_items → List[dict]
# response.metadata → dict
```

### Get Status

```python
response = get_import_status("uuid-...")
# response.status → "completed" | "pending" | "failed"
# response.import_job → dict with job details
```

## Response Structure

### IngestResponse

```python
{
    "success": bool,
    "job_id": str,
    "message": str,
    "documents_created": int,
    "line_items_created": int,
    "timestamp": str,
    "errors": []
}
```

### NormalizedDataResponse

```python
{
    "success": bool,
    "total_line_items": int,
    "line_items": [
        {
            "line_item_id": str,
            "service_date": str,
            "procedure_code": str,
            "procedure_description": str,
            "provider_name": str,
            "billed_amount": float,
            "patient_responsibility": float,
            ...
        }
    ],
    "metadata": {
        "total_billed_amount": float,
        "total_patient_responsibility": float,
        "unique_providers": int,
        "unique_procedure_codes": int,
        "date_range": {"earliest": str, "latest": str}
    }
}
```

## Test

```bash
python3 scripts/test_ingestion_api.py
```

## Documentation

- **Full API Ref**: `docs/INGESTION_API.md`
- **Delivery Summary**: `API_DELIVERY_SUMMARY.md`

## Status

✅ Production-ready functions  
❌ Not deployed (demo only)  
🔜 Ready for FastAPI
