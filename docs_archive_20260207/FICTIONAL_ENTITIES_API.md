# Fictional Healthcare Entities API Documentation

**Module:** `_modules.data.fictional_entities`
**Purpose:** Generate deterministic fictional healthcare entities for demo purposes
**Status:** ✅ Production-ready for demo/hackathon use

---

## Overview

This module provides functions to generate realistic-looking but completely **fictional** healthcare entities:
- ~30 insurance companies
- ~10,000 healthcare providers

All data is:
- ✅ **Deterministic** (same seed = same output)
- ✅ **Cached** with `@st.cache_data` for performance
- ✅ **Fictional** with clear `(DEMO)` markers
- ✅ **Safe** for hackathons and educational demos

---

## Quick Start

### Basic Usage

```python
from _modules.data import (
    generate_fictional_insurance_companies,
    generate_fictional_healthcare_providers,
    get_all_fictional_entities,
)

# Generate 30 insurance companies
insurance = generate_fictional_insurance_companies(30, seed=42)

# Generate 10,000 providers
providers = generate_fictional_healthcare_providers(10000, seed=42)

# Or get everything at once
entities = get_all_fictional_entities(
    insurance_count=30,
    provider_count=10000,
    seed=42
)

print(f"Generated {len(entities['insurance'])} insurance companies")
print(f"Generated {len(entities['providers'])} providers")
```

### In Streamlit UI

```python
import streamlit as st
from _modules.data import get_all_fictional_entities

# This is automatically cached by Streamlit
entities = get_all_fictional_entities()

# Display in UI
st.selectbox(
    "Choose Insurance Company",
    options=[c['name'] for c in entities['insurance']]
)
```

---

## API Reference

### Main Generation Functions

#### `generate_fictional_insurance_companies(count=30, seed=42)`

Generate fictional insurance companies.

**Parameters:**
- `count` (int): Number of companies to generate (default: 30)
- `seed` (int): Random seed for deterministic output (default: 42)

**Returns:** `List[InsuranceCompany]`

**Example:**
```python
companies = generate_fictional_insurance_companies(30, seed=42)

# Sample output
{
    'id': 'demo_ins_001',
    'name': 'Beacon Life (DEMO)',
    'entity_type': 'insurance',
    'network_size': 'national',
    'plan_types': ['HMO', 'PPO', 'EPO'],
    'demo_portal_html': '<div>...</div>'
}
```

---

#### `generate_fictional_healthcare_providers(count=10000, seed=42, insurance_company_ids=None)`

Generate fictional healthcare providers.

**Parameters:**
- `count` (int): Number of providers to generate (default: 10,000)
- `seed` (int): Random seed for deterministic output (default: 42)
- `insurance_company_ids` (List[str], optional): Insurance IDs to randomly assign

**Returns:** `List[HealthcareProvider]`

**Example:**
```python
providers = generate_fictional_healthcare_providers(1000, seed=42)

# Sample output
{
    'id': 'demo_prov_000001',
    'name': 'Dr. Maria Mitchell (DEMO)',
    'entity_type': 'provider',
    'specialty': 'Cardiology',
    'location_city': 'Springfield',
    'location_state': 'CA',
    'accepts_insurance': ['demo_ins_001', 'demo_ins_005'],
    'demo_portal_html': '<div>...</div>'
}
```

---

#### `get_all_fictional_entities(insurance_count=30, provider_count=10000, seed=42)`

Generate all entities in one call.

**Parameters:**
- `insurance_count` (int): Number of insurance companies (default: 30)
- `provider_count` (int): Number of providers (default: 10,000)
- `seed` (int): Random seed (default: 42)

**Returns:** `dict` with keys `'insurance'` and `'providers'`

**Example:**
```python
entities = get_all_fictional_entities()

# Access entities
for company in entities['insurance']:
    print(f"Insurance: {company['name']}")

for provider in entities['providers'][:10]:
    print(f"Provider: {provider['name']}, {provider['specialty']}")
```

---

### Utility Functions

#### `get_entity_by_id(entity_id, entities)`

Find an entity by ID.

```python
companies = generate_fictional_insurance_companies(30)
entity = get_entity_by_id('demo_ins_001', companies)
print(entity['name'])  # 'Beacon Life (DEMO)'
```

---

#### `filter_providers_by_specialty(providers, specialty)`

Filter providers by specialty.

```python
entities = get_all_fictional_entities()
cardiologists = filter_providers_by_specialty(
    entities['providers'],
    'Cardiology'
)
print(f"Found {len(cardiologists)} cardiologists")
```

---

#### `filter_providers_by_insurance(providers, insurance_id)`

Filter providers by accepted insurance.

```python
entities = get_all_fictional_entities()
in_network = filter_providers_by_insurance(
    entities['providers'],
    'demo_ins_001'
)
print(f"{len(in_network)} providers accept this insurance")
```

---

#### `get_entity_stats(entities)`

Get statistics about generated entities.

```python
entities = get_all_fictional_entities()
stats = get_entity_stats(entities)

print(f"Total providers: {stats['total_providers']}")
print(f"Unique specialties: {stats['unique_specialties']}")
print(f"Avg insurances per provider: {stats['avg_insurances_per_provider']:.2f}")

# Distribution data
for specialty, count in stats['specialty_distribution'].items():
    print(f"{specialty}: {count} providers")
```

---

### Validation Functions

#### `validate_entity_uniqueness(entities)`

Check that all entity IDs are unique.

```python
companies = generate_fictional_insurance_companies(30)
assert validate_entity_uniqueness(companies)
```

---

#### `validate_entity_structure(entity)`

Check that entity has required fields.

```python
entity = companies[0]
assert validate_entity_structure(entity)
```

---

## Data Models

### `InsuranceCompany` (TypedDict)

```python
{
    'id': str,                    # e.g., 'demo_ins_001'
    'name': str,                  # e.g., 'Beacon Life (DEMO)'
    'entity_type': str,           # Always 'insurance'
    'network_size': str,          # 'national' | 'regional' | 'local'
    'plan_types': List[str],      # ['HMO', 'PPO', 'EPO', etc.]
    'demo_portal_html': str       # HTML snippet for UI display
}
```

---

### `HealthcareProvider` (TypedDict)

```python
{
    'id': str,                    # e.g., 'demo_prov_000001'
    'name': str,                  # e.g., 'Dr. Maria Mitchell (DEMO)'
    'entity_type': str,           # Always 'provider'
    'specialty': str,             # e.g., 'Cardiology'
    'location_city': str,         # e.g., 'Springfield'
    'location_state': str,        # e.g., 'CA'
    'accepts_insurance': List[str], # Insurance IDs
    'demo_portal_html': str       # HTML snippet for UI display
}
```

---

## Constants

### Available Specialties (30 total)

```python
from _modules.data import AVAILABLE_SPECIALTIES

specialties = AVAILABLE_SPECIALTIES
# ['Allergy and Immunology', 'Anesthesiology', 'Cardiology', ...]
```

### Available States (50 total)

```python
from _modules.data import AVAILABLE_STATES

states = AVAILABLE_STATES
# ['AL', 'AK', 'AZ', ...]
```

### Defaults

```python
from _modules.data import (
    DEFAULT_INSURANCE_COUNT,   # 30
    DEFAULT_PROVIDER_COUNT,    # 10000
    DEFAULT_SEED,              # 42
)
```

---

## Performance

### Caching

All generation functions use `@st.cache_data(ttl=None)`:
- First call: ~1-2 seconds for 10,000 providers
- Subsequent calls: < 1ms (cached)
- Cache persists across Streamlit reruns

### Memory Usage

- 30 insurance companies: ~15 KB
- 10,000 providers: ~2.5 MB
- Total: ~2.5 MB cached in memory

### Determinism

Same seed = same output every time:

```python
# These will be identical
entities1 = get_all_fictional_entities(seed=42)
entities2 = get_all_fictional_entities(seed=42)

assert entities1 == entities2  # ✓ True
```

---

## Safety Features

### Demo Markers

All entities have `(DEMO)` in their names:

```python
company['name']   # 'Beacon Life (DEMO)'
provider['name']  # 'Dr. Maria Mitchell (DEMO)'
```

### Portal Disclaimers

All `demo_portal_html` includes:
- ⚠️ "DEMO ONLY" warning
- "Fictional" or "educational purposes" language
- "No real credentials or PHI transmitted" notice

### Example Portal HTML

```html
<div style="padding: 20px; border: 2px dashed #ccc;">
    <h3>🛡️ Beacon Life (DEMO)</h3>
    <p><strong>Portal Type:</strong> Insurance Company Demo</p>
    <p><em>⚠️ DEMO ONLY - Fictional insurance company for educational purposes</em></p>
    <p style="font-size: 12px; color: #666;">
        This is a simulated connection. No real credentials or PHI are transmitted.
    </p>
</div>
```

---

## Examples

### Example 1: Provider Directory

```python
import streamlit as st
from _modules.data import get_all_fictional_entities, AVAILABLE_SPECIALTIES

# Load entities
entities = get_all_fictional_entities()

# Filter UI
specialty = st.selectbox("Filter by Specialty", AVAILABLE_SPECIALTIES)
state = st.selectbox("Filter by State", ['All'] + AVAILABLE_STATES)

# Filter providers
providers = entities['providers']

if specialty != 'All':
    providers = [p for p in providers if p['specialty'] == specialty]

if state != 'All':
    providers = [p for p in providers if p['location_state'] == state]

# Display
st.write(f"Found {len(providers)} providers")
for provider in providers[:10]:
    st.markdown(f"**{provider['name']}**")
    st.write(f"{provider['specialty']} - {provider['location_city']}, {provider['location_state']}")
```

### Example 2: Insurance Network Checker

```python
from _modules.data import get_all_fictional_entities, filter_providers_by_insurance

entities = get_all_fictional_entities()

# User selects insurance
selected_insurance = st.selectbox(
    "Your Insurance",
    options=entities['insurance'],
    format_func=lambda c: c['name']
)

# Find in-network providers
in_network = filter_providers_by_insurance(
    entities['providers'],
    selected_insurance['id']
)

st.success(f"{len(in_network)} providers accept {selected_insurance['name']}")
```

### Example 3: Statistics Dashboard

```python
from _modules.data import get_all_fictional_entities, get_entity_stats

entities = get_all_fictional_entities()
stats = get_entity_stats(entities)

# Display metrics
col1, col2, col3 = st.columns(3)
col1.metric("Insurance Companies", stats['total_insurance_companies'])
col2.metric("Healthcare Providers", stats['total_providers'])
col3.metric("Specialties", stats['unique_specialties'])

# Chart: Providers by Specialty
import pandas as pd
df = pd.DataFrame([
    {'Specialty': k, 'Count': v}
    for k, v in stats['specialty_distribution'].items()
]).sort_values('Count', ascending=False)

st.bar_chart(df.set_index('Specialty')['Count'])
```

---

## Testing

Run the included test suite:

```bash
python3 scripts/test_fictional_entities.py
```

**Tests include:**
- ✅ Generation works correctly
- ✅ All IDs are unique
- ✅ All structures are valid
- ✅ Filtering works
- ✅ Determinism (same seed = same output)
- ✅ Demo markers present
- ✅ Portal disclaimers present

---

## Integration with UI

### In `data_connector.py` (Streamlit UI)

```python
from _modules.data import get_all_fictional_entities

def render_provider_selection():
    """Render provider selection UI."""
    # Load entities (cached automatically)
    entities = get_all_fictional_entities()

    st.markdown("### Choose a Healthcare Provider to Connect")

    # Display insurance companies
    st.markdown("#### Insurance Companies")
    for company in entities['insurance'][:10]:
        if st.button(f"Connect to {company['name']}", key=company['id']):
            # Handle connection...
            pass

    # Display healthcare systems
    st.markdown("#### Healthcare Systems")
    hospital_providers = [
        p for p in entities['providers']
        if 'Medical Center' in p['name'] or 'Hospital' in p['name']
    ]

    for provider in hospital_providers[:10]:
        if st.button(f"Connect to {provider['name']}", key=provider['id']):
            # Handle connection...
            pass
```

---

## Limitations & Non-Goals

### What This Module Does

✅ Generate realistic-looking fictional data
✅ Provide deterministic output (seeded)
✅ Cache results for performance
✅ Support filtering and searching
✅ Include demo disclaimers

### What This Module Does NOT Do

❌ Connect to real healthcare APIs
❌ Validate real insurance policy numbers
❌ Store or transmit PHI
❌ Implement OAuth flows
❌ Generate claim data (see ingestion service for that)

---

## Future Enhancements

Potential additions (not yet implemented):

- [ ] Provider credentials (fictional NPI numbers)
- [ ] Insurance plan details (deductibles, copays)
- [ ] Geographic clustering (providers near each other)
- [ ] Network hierarchies (parent/child organizations)
- [ ] Time-based availability (office hours)
- [ ] Ratings/reviews (fictional patient feedback)

---

## Related Documentation

- [Data Connector Architecture](./DATA_CONNECTOR_ARCHITECTURE.md) - System architecture
- [Profile Editor Integration](./PROFILE_EDITOR_INTEGRATION.md) - UI integration patterns
- [Demo Disclaimer](./DEMO_DISCLAIMER.md) - Legal disclaimers

---

**Last Updated:** January 25, 2026
**Module Location:** `_modules/data/fictional_entities.py`
**Test Suite:** `scripts/test_fictional_entities.py`

