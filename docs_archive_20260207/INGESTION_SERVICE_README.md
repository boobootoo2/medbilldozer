# Healthcare Data Ingestion Service

## Overview

The ingestion service provides a programmatic interface for importing healthcare billing data from fictional entities and normalizing it into a consistent schema. This system demonstrates how healthcare data aggregation might work in a production environment, using completely fictional data for educational and development purposes.

---

## Architecture

### Three-Layer Design

```text
┌─────────────────────────────────────────────────────────────┐
│                    Consumer Layer                           │
│  • Streamlit UI (current)                                   │
│  • External applications (future)                           │
│  • CLI tools, notebooks, integrations                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Ingestion API Layer                        │
│  Module: _modules/ingest/api.py                             │
│                                                              │
│  Functions:                                                  │
│    • ingest_document(payload) → IngestResponse              │
│    • list_imports(user_id) → ImportListResponse             │
│    • get_normalized_data(user_id) → NormalizedDataResponse  │
│    • get_import_status(job_id) → ImportStatusResponse       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               Data Generation Layer                         │
│  Module: _modules/data/health_data_ingestion.py             │
│                                                              │
│  Functions:                                                  │
│    • import_sample_data() - Generate ImportJob              │
│    • generate_line_items_from_insurance()                   │
│    • generate_line_items_from_provider()                    │
│    • extract_insurance_plan_from_entity()                   │
│    • extract_provider_from_entity()                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Storage Layer                              │
│  Current: InMemoryStorage (demo)                            │
│  Production: PostgreSQL/MongoDB                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Clean Separation**: Each layer has a single responsibility and well-defined interfaces
2. **Reusable Logic**: Normalization happens once, consumed by multiple interfaces
3. **Testable**: Each layer can be tested independently
4. **Production-Ready**: Architecture supports migration to FastAPI + database

---

## Current Consumer: Streamlit UI

The Streamlit application uses the ingestion service through direct function calls:

```python
# In Streamlit UI code
from _modules.ingest.api import ingest_document, get_normalized_data

# User selects an entity from the UI
selected_entity = st.selectbox("Choose insurance company", entities)

# Trigger ingestion
if st.button("Import Data"):
    payload = {
        "user_id": st.session_state.user_id,
        "entity_type": "insurance",
        "entity_id": selected_entity['id'],
        "num_line_items": 5
    }

    response = ingest_document(payload)

    if response.success:
        st.success(f"Imported {response.line_items_created} line items")
        # Display data
        data = get_normalized_data(st.session_state.user_id)
        st.dataframe(data.line_items)
```

**Benefits of this approach**:

- No network latency (same process)
- Type-safe interfaces (dataclasses)
- Easy debugging
- Simple deployment (single app)

---

## Future Consumer: External Applications

The same API functions can be exposed as REST endpoints via FastAPI:

```python
# Future: api_server.py
from fastapi import FastAPI, HTTPException
from _modules.ingest.api import (
    ingest_document,
    list_imports,
    get_normalized_data
)

app = FastAPI()

@app.post("/api/v1/ingest/document")
async def api_ingest(request: IngestRequest):
    response = ingest_document(request.dict())
    if not response.success:
        raise HTTPException(status_code=400, detail=response.errors)
    return response

@app.get("/api/v1/data")
async def api_get_data(user_id: str, job_id: Optional[str] = None):
    return get_normalized_data(user_id, job_id)
```

**External apps would consume it like**:

```python
import requests

# Ingest document
response = requests.post(
    "https://api.example.com/api/v1/ingest/document",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "user_id": "user_123",
        "entity_type": "insurance",
        "entity_id": "demo_ins_001"
    }
)

job_id = response.json()["job_id"]

# Get normalized data
data = requests.get(
    "https://api.example.com/api/v1/data",
    params={"user_id": "user_123"}
).json()
```

This approach enables:

- Mobile apps, web apps, CLI tools
- Third-party integrations
- Batch processing systems
- Analytics dashboards

---

## What This System Does

✅ **Demonstrates healthcare data aggregation patterns**
✅ **Generates realistic but fictional billing data**
✅ **Normalizes across different source types** (insurance EOBs, provider bills)
✅ **Provides clean programmatic interfaces**
✅ **Supports multi-user data isolation**
✅ **Shows production-ready architecture patterns**

---

## What Is Intentionally Out of Scope

### ❌ No Real Portal Connections

This system does **not** connect to real healthcare portals. All data is generated locally using deterministic algorithms with fictional entities.

**Why**: Real portal connections require:

- OAuth implementations for each provider
- Portal-specific scraping or API integrations
- Credential management and secure storage
- CAPTCHA handling and session management
- Rate limiting and retry logic
- Legal agreements with each provider

**What we do instead**: Generate realistic data that mimics what would be retrieved from real portals, allowing UI and integration development without the complexity of actual connections.

### ❌ No HIPAA Compliance Claims

This system makes **no claims of HIPAA compliance** and should not be used with real patient data.

**Why**: HIPAA compliance requires:

- Business Associate Agreements (BAAs)
- Comprehensive security controls (encryption at rest/transit, access controls, audit logging)
- Privacy policies and user consent workflows
- Breach notification procedures
- Regular security audits and risk assessments
- Employee training and policy enforcement

**What we do instead**: Use clearly marked fictional data (all names end with "(DEMO)", claim numbers have "CLM-DEMO-" prefix) to avoid any confusion about data authenticity.

### ❌ No Production Authentication or Authorization

This system has **no authentication or authorization** mechanisms.

**Why**: Production auth requires:

- OAuth 2.0 or API key infrastructure
- User identity management
- Role-based access control (RBAC)
- Rate limiting per user/application
- Token refresh and revocation
- Security monitoring and intrusion detection

**What we do instead**: Provide a clean API surface that can be wrapped with authentication when deployed to production.

### ❌ No Live Access to Real Healthcare Systems

This system **cannot and does not** access real healthcare provider systems, insurance portals, or health information exchanges (HIEs).

**Why**: Real access requires:

- Legal agreements with providers
- Integration with proprietary APIs or HL7/FHIR interfaces
- Compliance with data use agreements
- Network security and VPN connections
- Provider credentialing and verification
- Ongoing relationship management

**What we do instead**: Simulate what such integrations would produce, enabling development and testing without the operational overhead.

---

## Intended Use Cases

### ✅ Appropriate Uses

- **Education**: Learn healthcare data integration patterns
- **Development**: Build UIs and analytics without real data
- **Demonstrations**: Show stakeholders how aggregation might work
- **Prototyping**: Validate product concepts before production investment
- **Testing**: Develop and test downstream systems with realistic data shapes

### ❌ Inappropriate Uses

- Processing real patient data
- Production healthcare applications
- Systems subject to HIPAA or other healthcare regulations
- Financial decision-making based on generated data
- Claiming this is a production-ready healthcare system

---

## Migration Path to Production

To convert this demo system to production:

1. **Add Real Data Sources**
   - Implement OAuth flows for real portals
   - Build scrapers or API clients for each provider
   - Add credential management (encrypted at rest)

2. **Add Database Persistence**
   - Replace `InMemoryStorage` with PostgreSQL
   - Implement proper data retention policies
   - Add backup and disaster recovery

3. **Add Security**
   - Implement OAuth 2.0 for API authentication
   - Add encryption at rest and in transit (TLS 1.3)
   - Implement audit logging for all data access
   - Add rate limiting and DDoS protection

4. **Add Compliance**
   - Conduct security audit and penetration testing
   - Implement HIPAA administrative, physical, and technical safeguards
   - Create privacy policies and consent workflows
   - Obtain BAAs from any service providers

5. **Add Monitoring**
   - Application performance monitoring (APM)
   - Error tracking and alerting
   - Security information and event management (SIEM)
   - Uptime monitoring and on-call rotation

6. **Legal & Operational**
   - Engage legal counsel for healthcare regulations
   - Establish data use agreements with providers
   - Create incident response plan
   - Set up customer support infrastructure

---

## Technical Stack

### Current Implementation

- **Language**: Python 3.11+
- **UI Framework**: Streamlit
- **Storage**: In-memory dictionaries
- **Testing**: Native Python assertions
- **Data Models**: Dataclasses

### Production Migration Options

- **API Framework**: FastAPI (OpenAPI + async)
- **Database**: PostgreSQL (relational) or MongoDB (document)
- **Cache**: Redis (session data, rate limiting)
- **Queue**: Celery + RabbitMQ (background jobs)
- **Deployment**: Docker + Kubernetes or AWS ECS

---

## Testing

```bash
# Test the ingestion logic
python3 scripts/test_health_data_ingestion.py

# Test the API layer
python3 scripts/test_ingestion_api.py

# Expected: All tests pass ✓
```

---

## Documentation

- **API Reference**: `docs/INGESTION_API.md` - Complete function reference
- **Architecture Contract**: `docs/DATA_CONNECTOR_ARCHITECTURE.md` - Design decisions
- **Quick Start**: `docs/INGESTION_QUICKSTART.md` - 5-minute overview
- **Delivery Summary**: `API_DELIVERY_SUMMARY.md` - What was delivered

---

## Responsible Disclosure

**This is a demonstration system with fictional data.**

We've designed this system to be:

- **Honest**: Clear about what it does and doesn't do
- **Educational**: Teaches real patterns with safe data
- **Responsible**: Cannot be mistaken for a production healthcare system

All data is clearly marked as "(DEMO)" and "fictional". No real patient data, real providers, or real insurance companies are used or accessed.

If you're building a production healthcare system, please:

1. Engage with healthcare legal counsel
2. Conduct proper security audits
3. Obtain necessary compliance certifications
4. Create real data use agreements with providers
5. Never use this demo code with real patient data

---

## Questions?

See additional documentation:

- `docs/INGESTION_API.md` - API function reference
- `docs/HEALTH_DATA_INGESTION.md` - Data generation details
- `docs/DATA_CONNECTOR_ARCHITECTURE.md` - Architecture decisions

**Status**: Demo system, production architecture patterns
**Last Updated**: January 25, 2026

