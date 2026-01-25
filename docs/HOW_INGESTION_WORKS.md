# How the Ingestion API Works

## Overview

The Ingestion API is a **demo-only system** that simulates connecting to healthcare portals (like insurance companies or medical providers) and importing billing data. It generates realistic but completely fictional data locally without any network calls.

Think of it like **Plaid for healthcare billing** - but it's a demo that shows what the experience would be like.

---

## The Simple Flow

```text
1. Your app calls → ingest_document(payload)
2. API picks a fictional entity (e.g., "BlueWave Health (DEMO)")
3. API generates realistic billing data for that entity
4. API stores the data in memory
5. Your app gets back normalized line items
```

---

## Working Example

### Step 1: Pick a Fictional Entity

First, you choose from our pre-built fictional entities:

```python
from _modules.data.fictional_entities import get_all_fictional_entities

entities = get_all_fictional_entities()

# Returns:
{
    "insurance": [
        {
            "id": "demo_ins_001",
            "name": "BlueWave Health (DEMO)",
            "type": "insurance",
            "plan_type": "PPO",
            ...
        },
        {
            "id": "demo_ins_002",
            "name": "CarePlus Insurance (DEMO)",
            ...
        }
    ],
    "providers": [
        {
            "id": "demo_prov_000001",
            "name": "Dr. Sarah Johnson (DEMO)",
            "specialty": "Family Medicine",
            ...
        }
    ]
}
```

### Step 2: Call the Ingestion API

```python
from _modules.ingest.api import ingest_document

# Create your request
payload = {
    "user_id": "demo_user_123",           # Your user's ID
    "entity_type": "insurance",            # "insurance" or "provider"
    "entity_id": "demo_ins_001",          # Which entity to simulate
    "num_line_items": 5                   # How many transactions to generate
}

# Call the API
response = ingest_document(payload)

# Check the result
if response.success:
    print(f"✅ Success! Created {response.line_items_created} line items")
    print(f"Job ID: {response.job_id}")
else:
    print(f"❌ Failed: {response.message}")
    print(f"Errors: {response.errors}")
```

### Step 3: What Happens Behind The Scenes

When you call `ingest_document()`, here's what happens:

```python
# 1. Validate the request
errors = request.validate()
if errors:
    return IngestResponse(success=False, errors=errors)

# 2. Find the fictional entity
entity = get_entity_by_id("demo_ins_001", entities['insurance'])
# Returns: {"id": "demo_ins_001", "name": "BlueWave Health (DEMO)", ...}

# 3. Generate realistic billing data
import_job = import_sample_data(entity, num_line_items=5)

# This creates:
# - 1 fake document (simulated EOB/bill)
# - 5 line items with CPT codes, amounts, dates
# - Realistic provider names, claim numbers
# - All marked as "(DEMO)" or "CLM-DEMO-xxx"

# 4. Store it in memory (user_id → job_id → data)
_storage.store_import("demo_user_123", import_job)

# 5. Return success response
return IngestResponse(
    success=True,
    job_id="uuid-generated-job-id",
    line_items_created=5,
    ...
)
```

### Step 4: Retrieve Your Data

```python
from _modules.ingest.api import get_normalized_data

# Get all data for your user
data = get_normalized_data(user_id="demo_user_123")

print(f"Total line items: {data.total_line_items}")

# Look at the data
for item in data.line_items:
    print(f"{item['service_date']}: {item['procedure_description']}")
    print(f"  Billed: ${item['billed_amount']}")
    print(f"  You pay: ${item['patient_responsibility']}")
```

**Example output:**

```text
2026-01-15: Office Visit - Established Patient (99213)
  Billed: $150.00
  You pay: $30.00

2026-01-16: Complete Blood Count (85025)
  Billed: $45.00
  You pay: $12.00

2026-01-18: X-Ray Chest 2 Views (71046)
  Billed: $120.00
  You pay: $36.00
```

---

## What Makes It "Demo-Only"?

### ✅ What It DOES

1. **Generates realistic data** - Uses real CPT codes, realistic amounts, proper date formats
2. **Simulates entity connections** - Acts like you connected to "BlueWave Health" portal
3. **Normalizes data** - Converts different source formats into consistent schema
4. **Multi-user support** - Keeps each user's data isolated
5. **Job tracking** - Tracks import jobs, statuses, timestamps

### ❌ What It DOESN'T Do

1. **No real portals** - Doesn't connect to actual insurance/provider websites
2. **No authentication** - No OAuth, no API keys, no user login
3. **No network calls** - Everything happens locally in memory
4. **No database** - Uses in-memory dictionary (lost when app restarts)
5. **No HIPAA compliance** - Not for real patient data

---

## The Data Generation Process

### Insurance Entity Example

```python
# When you select: "BlueWave Health (DEMO)"
# The system generates:

import_job = {
    "job_id": "uuid-abc123",
    "user_id": "demo_user_123",
    "entity_id": "demo_ins_001",
    "entity_name": "BlueWave Health (DEMO)",
    "status": "completed",
    "created_at": "2026-01-25T10:30:00Z",

    "documents": [
        {
            "document_id": "doc_xyz789",
            "file_name": "BlueWave_Health_EOB_20260125.pdf",
            "file_type": "eob",
            "status": "extracted"
        }
    ],

    "line_items": [
        {
            "line_item_id": "item_001",
            "service_date": "2026-01-15",
            "procedure_code": "99213",
            "procedure_description": "Office Visit - Established Patient",
            "provider_name": "Dr. Emily Chen",
            "provider_npi": "1234567890",
            "billed_amount": 150.00,
            "allowed_amount": 120.00,
            "paid_by_insurance": 90.00,
            "patient_responsibility": 30.00,
            "claim_number": "CLM-DEMO-001234",
            "source": "demo_sample"
        },
        # ... 4 more line items
    ],

    "insurance_plan": {
        "carrier_name": "BlueWave Health (DEMO)",
        "plan_name": "BlueWave PPO Plus",
        "member_id": "BWH123456789",
        "deductible_individual": 1500.00,
        ...
    },

    "summary": {
        "total_billed": 750.00,
        "total_allowed": 600.00,
        "total_insurance_paid": 480.00,
        "total_patient_responsibility": 120.00,
        "unique_providers": 3,
        "date_range": {"start": "2026-01-15", "end": "2026-01-20"}
    }
}
```

### Provider Entity Example

```python
# When you select: "Dr. Sarah Johnson (DEMO)"
# The system generates:

import_job = {
    "job_id": "uuid-def456",
    "entity_name": "Dr. Sarah Johnson (DEMO)",

    "line_items": [
        {
            "procedure_code": "99214",
            "procedure_description": "Office Visit - Detailed",
            "provider_name": "Dr. Sarah Johnson",
            "provider_npi": "9876543210",
            "billed_amount": 200.00,
            "source": "demo_sample"
        }
    ],

    "provider": {
        "name": "Dr. Sarah Johnson (DEMO)",
        "specialty": "Family Medicine",
        "npi": "9876543210",
        "address": {
            "street": "123 Medical Plaza",
            "city": "Springfield",
            "state": "IL",
            "zip": "62701"
        }
    }
}
```

---

## All Available API Functions

### 1. `ingest_document(payload)` - Import Data

**Purpose**: Simulate connecting to an entity and importing billing data

```python
payload = {
    "user_id": "demo_user_123",
    "entity_type": "insurance",  # or "provider"
    "entity_id": "demo_ins_001",
    "num_line_items": 5,  # Optional, defaults to random 3-8
    "metadata": {"source": "mobile_app"}  # Optional
}

response = ingest_document(payload)
# Returns: IngestResponse(success=True, job_id="...", line_items_created=5)
```

### 2. `list_imports(user_id)` - See All Imports

**Purpose**: Get a list of all import jobs for a user

```python
response = list_imports("demo_user_123")

print(f"Total imports: {response.total_imports}")
for imp in response.imports:
    print(f"- {imp.entity_name}: {imp.line_items_count} items")
```

### 3. `get_normalized_data(user_id, job_id)` - Get The Data

**Purpose**: Retrieve normalized line items

```python
# Get all data for user
data = get_normalized_data("demo_user_123")

# Or get data from specific job
data = get_normalized_data("demo_user_123", job_id="uuid-abc123")

# Access the data
for item in data.line_items:
    print(f"{item['procedure_description']}: ${item['patient_responsibility']}")

# Get metadata
print(f"Total billed: ${data.metadata['total_billed']}")
print(f"Providers: {data.metadata['unique_providers']}")
```

### 4. `get_import_status(job_id)` - Check Job Status

**Purpose**: Get detailed info about a specific import job

```python
status = get_import_status("uuid-abc123")

print(f"Status: {status.status}")
print(f"Entity: {status.entity_name}")
print(f"Created: {status.created_at}")
print(f"Line items: {status.line_items_count}")
```

---

## Storage: How Data Is Kept

### In-Memory Storage (Current)

```python
class InMemoryStorage:
    def __init__(self):
        # Simple nested dictionary
        self._data = {}  # user_id -> job_id -> import_job

    def store_import(self, user_id, import_job):
        if user_id not in self._data:
            self._data[user_id] = {}
        self._data[user_id][import_job['job_id']] = import_job

    def get_user_imports(self, user_id):
        return self._data.get(user_id, {}).values()
```

**Pros**: Fast, simple, no setup
**Cons**: Lost when app restarts, not scalable

### Production Storage (Future)

```python
# Would use PostgreSQL or MongoDB:

# PostgreSQL schema:
CREATE TABLE import_jobs (
    job_id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    entity_id VARCHAR(255),
    status VARCHAR(50),
    created_at TIMESTAMP,
    INDEX idx_user_id (user_id)
);

CREATE TABLE line_items (
    line_item_id UUID PRIMARY KEY,
    job_id UUID REFERENCES import_jobs(job_id),
    service_date DATE,
    procedure_code VARCHAR(10),
    billed_amount DECIMAL(10,2),
    ...
);
```

---

## How To Use From Streamlit UI

### Current Profile Editor (Needs Update)

The existing profile editor has a **wizard interface** but uses **mock extraction**. Here's how to connect it to the real ingestion API:

```python
# In profile_editor.py, replace mock extraction with:

def render_entity_selector():
    """Let user pick a fictional entity to import from."""
    st.subheader("📥 Import Healthcare Data")

    # Get entities
    entities = get_all_fictional_entities()

    # Entity type
    entity_type = st.selectbox(
        "Source Type",
        ["insurance", "provider"],
        format_func=lambda x: "Insurance Company" if x == "insurance" else "Medical Provider"
    )

    # Entity selection
    entity_list = entities['insurance'] if entity_type == 'insurance' else entities['providers']
    entity_options = {e['name']: e['id'] for e in entity_list}

    selected_name = st.selectbox("Select Entity", options=list(entity_options.keys()))
    selected_id = entity_options[selected_name]

    # Number of line items
    num_items = st.slider("Number of transactions to import", 1, 20, 5)

    # Import button
    if st.button("🚀 Import Data", type="primary"):
        with st.spinner(f"Importing from {selected_name}..."):
            # Call the ingestion API
            payload = {
                "user_id": st.session_state.user_id,
                "entity_type": entity_type,
                "entity_id": selected_id,
                "num_line_items": num_items,
                "metadata": {"source": "profile_editor"}
            }

            response = ingest_document(payload)

            if response.success:
                st.success(f"✅ Imported {response.line_items_created} transactions!")
                st.session_state.last_import_job_id = response.job_id
            else:
                st.error(f"❌ Import failed: {response.message}")


def render_imported_data():
    """Display imported data."""
    if 'last_import_job_id' not in st.session_state:
        st.info("No data imported yet. Use the importer above.")
        return

    # Get the data
    data = get_normalized_data(
        st.session_state.user_id,
        job_id=st.session_state.last_import_job_id
    )

    st.subheader(f"📊 Imported Data ({data.total_line_items} items)")

    # Show metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Billed", f"${data.metadata['total_billed']:.2f}")
    with col2:
        st.metric("You Pay", f"${data.metadata['total_patient_responsibility']:.2f}")
    with col3:
        st.metric("Providers", data.metadata['unique_providers'])

    # Show line items table
    import pandas as pd
    df = pd.DataFrame(data.line_items)
    st.dataframe(
        df[['service_date', 'procedure_description', 'billed_amount',
            'patient_responsibility', 'provider_name']],
        use_container_width=True
    )
```

---

## Testing The API

Run the test suite to see it in action:

```bash
python3 scripts/test_ingestion_api.py
```

**Expected output:**

```text
================================================================================
TEST 1: Document Ingestion API
================================================================================
✓ Created payload for user: demo_user_123
  Entity: insurance - demo_ins_001
✓ Ingestion response:
  Success: True
  Job ID: a1b2c3d4-...
  Message: Successfully ingested data from BlueWave Health (DEMO)
  Documents created: 1
  Line items created: 5
✓ All assertions passed

================================================================================
TEST 2: List Imports API
================================================================================
✓ Created 3 import jobs
✓ List imports response:
  Success: True
  User ID: demo_user_456
  Total imports: 3

  Import 1:
    Job ID: x1y2z3...
    Entity: BlueWave Health (DEMO)
    Type: insurance
    Status: completed
    Line items: 5

... (and so on)

🎉 ALL TESTS PASSED ✓
```

---

## Key Takeaways

### What You Need To Know

1. **It's a complete system** - Generates realistic healthcare billing data
2. **It's demo-only** - Uses fictional entities, no real connections
3. **It's production-ready architecture** - Shows how real system would work
4. **It's easy to use** - Simple function calls, clear responses
5. **It's not connected to UI yet** - Needs integration with profile_editor.py

### Next Steps To Make It Useful

1. **Connect to Profile Editor** - Replace mock extraction with real ingestion API
2. **Add entity selector UI** - Let users pick fictional entities to import from
3. **Display imported data** - Show line items in tables with filtering/sorting
4. **Add persistence** - Replace in-memory storage with JSON files or database
5. **Create dedicated page** - Add "💳 Data Connector" button to sidebar

### Why This Is Valuable

- **Demonstrates real patterns** - Shows how Plaid-like healthcare integration works
- **Safe for development** - No risk of touching real patient data
- **Educational** - Teaches healthcare data structures (CPT codes, EOBs, claims)
- **Production-ready** - Architecture can scale to real implementation

---

## Questions?

- **Full API Reference**: `docs/INGESTION_API.md`
- **How Data Is Generated**: `docs/HEALTH_DATA_INGESTION.md`
- **Architecture**: `docs/INGESTION_SERVICE_README.md`
- **Quick Reference**: `API_QUICKREF.md`

**Status**: Fully functional, tested, ready for UI integration
**Last Updated**: January 25, 2026

