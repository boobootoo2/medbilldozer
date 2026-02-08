# Health Data Ingestion - Quick Start

## 5-Minute Overview

The ingestion system generates **fictional healthcare data** from simulated portals and normalizes it into database-ready records.

---

## Core Function

```python
from _modules.data import import_sample_data

# Get a fictional healthcare entity (insurance or provider)
from _modules.data import generate_fictional_insurance_companies
entity = generate_fictional_insurance_companies(count=1, seed=42)[0]

# Import sample data
import_job = import_sample_data(entity, num_line_items=5)

# Result:
# - 1 ImportJob record
# - 1 Document record
# - 5 NormalizedLineItem records (with CPT codes, amounts, dates)
```

---

## What You Get

### ImportJob

```python
{
    "job_id": "uuid",
    "source_type": "insurance_portal",  # or "provider_portal"
    "source_method": "demo_sample",     # Always "demo_sample"
    "status": "completed",
    "documents": [Document],
    "line_items": [NormalizedLineItem, ...],
    "created_at": "2026-01-25T10:00:00Z",
    "completed_at": "2026-01-25T10:00:00Z"
}
```

### NormalizedLineItem (Example)

```python
{
    "line_item_id": "uuid",
    "service_date": "2025-12-15",
    "procedure_code": "99213",
    "procedure_description": "Office Visit - Established Patient, Level 3",
    "provider_name": "Dr. Sarah Johnson (DEMO)",
    "provider_npi": "1234567890",
    "billed_amount": 1500.00,
    "allowed_amount": 1200.00,
    "paid_by_insurance": 1020.00,
    "patient_responsibility": 180.00,
    "claim_number": "CLM-DEMO-123456"
}
```

---

## Key Features

✅ **Realistic Data**: Proper CPT codes, realistic amounts, valid date ranges
✅ **Proper Relationships**: `allowed <= billed`, `patient_resp = allowed - paid`
✅ **Demo Markers**: All data clearly marked as DEMO/FICTIONAL
✅ **No I/O**: Pure data generation, no file/API operations
✅ **Deterministic**: Same seed = same output
✅ **Fast**: <1ms with Streamlit caching

---

## Common Use Cases

### 1. Import from Insurance

```python
from _modules.data import (
    generate_fictional_insurance_companies,
    import_sample_data,
    extract_insurance_plan_from_entity
)

# Get entity
companies = generate_fictional_insurance_companies(count=1)
insurance = companies[0]

# Import data
job = import_sample_data(insurance, num_line_items=5)

# Extract plan info (optional)
plan = extract_insurance_plan_from_entity(insurance)
```

### 2. Import from Provider

```python
from _modules.data import (
    generate_fictional_healthcare_providers,
    import_sample_data,
    extract_provider_from_entity
)

# Get entity
providers = generate_fictional_healthcare_providers(count=1)
provider_entity = providers[0]

# Import data
job = import_sample_data(provider_entity, num_line_items=3)

# Extract provider info (optional)
provider = extract_provider_from_entity(provider_entity)
```

### 3. Batch Import

```python
from _modules.data import (
    generate_fictional_insurance_companies,
    import_multiple_entities
)

# Get multiple entities
companies = generate_fictional_insurance_companies(count=5)

# Import all at once
jobs = import_multiple_entities(companies, items_per_entity=3)
# Result: 5 ImportJobs with 15 total line items
```

### 4. Store in Session State

```python
from _modules.data import (
    import_sample_data,
    store_import_job_in_session
)

# Import data
job = import_sample_data(entity)

# Store in session
store_import_job_in_session(job)

# Access later:
# st.session_state["health_profile"]["import_jobs"]
# st.session_state["health_profile"]["line_items"]
```

---

## Testing

```bash
python3 scripts/test_health_data_ingestion.py

# Expected: 🎉 ALL TESTS PASSED ✓
```

---

## What's Included

- ✅ **30 fictional insurance companies** (via fictional_entities.py)
- ✅ **10,000 fictional providers** (via fictional_entities.py)
- ✅ **Realistic CPT codes** (99213, 80053, 45378, etc.)
- ✅ **Realistic claim amounts** (proper relationships)
- ✅ **Complete data models** (ImportJob, Document, NormalizedLineItem)
- ✅ **Extraction functions** (insurance plans, providers)
- ✅ **Helper utilities** (dates, amounts, claim numbers)

---

## Data Flow

```
Fictional Entity (insurance/provider)
        ↓
import_sample_data()
        ↓
    ImportJob
    ├── Documents (1)
    └── Line Items (3-5)
        ↓
store_in_session() [optional]
        ↓
st.session_state["health_profile"]
```

---

## Next Steps

1. ✅ **Use the ingestion logic** in your UI layer
2. 🔜 **Create service layer** (`health_data_connector.py`) to orchestrate
3. 🔜 **Create UI layer** (`data_connector.py`) with Plaid-like wizard
4. 🔜 **Integrate portals** (use `portal_templates.py` for iframe rendering)

---

## Full Documentation

See `docs/HEALTH_DATA_INGESTION.md` for complete API reference, examples, and details.

---

**Status**: Production-ready ✅
**Tests**: All passing ✓
**Safety**: All data clearly marked as DEMO

