# Fictional Healthcare Entities - Quick Reference

## Import

```python
from _modules.data import (
    get_all_fictional_entities,
    filter_providers_by_specialty,
    filter_providers_by_insurance,
    AVAILABLE_SPECIALTIES,
    AVAILABLE_STATES,
)
```

## Generate Data

```python
# Get everything (cached automatically)
entities = get_all_fictional_entities()

# Access entities
insurance = entities['insurance']      # 30 companies
providers = entities['providers']      # 10,000 providers
```

## Filter Data

```python
# By specialty
cardiologists = filter_providers_by_specialty(providers, 'Cardiology')

# By insurance
in_network = filter_providers_by_insurance(providers, 'demo_ins_001')

# By state (manual filter)
ca_providers = [p for p in providers if p['location_state'] == 'CA']
```

## Entity Structure

```python
# Insurance Company
{
    'id': 'demo_ins_001',
    'name': 'Beacon Life (DEMO)',
    'entity_type': 'insurance',
    'network_size': 'national',
    'plan_types': ['HMO', 'PPO'],
    'demo_portal_html': '<div>...</div>'
}

# Healthcare Provider  
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

## Constants

```python
AVAILABLE_SPECIALTIES  # 30 medical specialties
AVAILABLE_STATES      # 50 US state codes
```

## Testing

```bash
python3 scripts/test_fictional_entities.py
```

## Docs

- `docs/FICTIONAL_ENTITIES_API.md` - Full API reference
- `docs/FICTIONAL_ENTITIES_SUMMARY.md` - Implementation summary
- `docs/DATA_CONNECTOR_ARCHITECTURE.md` - Overall architecture
