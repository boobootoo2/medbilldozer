# Entity Picker Quick Start

## Getting The List of Fictional Entities

You have **30 fictional insurance companies** and **10,000 fictional healthcare providers** available for import simulation.

---

## Simple Usage

### Get All Entities

```python
from _modules.data.fictional_entities import get_all_fictional_entities

# Get entities (cached, so it's fast after first call)
entities = get_all_fictional_entities()

# Returns:
{
    "insurance": [
        {
            "id": "demo_ins_001",
            "name": "Beacon Life (DEMO)",
            "entity_type": "insurance",
            "network_size": "national",
            "plan_types": ["HMO", "PPO", "EPO"],
            "demo_portal_html": "..."
        },
        # ... 29 more insurance companies
    ],
    "providers": [
        {
            "id": "demo_prov_000001",
            "name": "Dr. Maria Mitchell (DEMO)",
            "entity_type": "provider",
            "specialty": "Oncology",
            "location_city": "Franklin",
            "location_state": "IA",
            "accepts_insurance": ["demo_ins_001", "demo_ins_005", ...],
            "demo_portal_html": "..."
        },
        # ... 9,999 more providers
    ]
}
```

---

## Streamlit UI Example

### Option 1: Simple Dropdown Selector

```python
import streamlit as st
from _modules.data.fictional_entities import get_all_fictional_entities
from _modules.ingest.api import ingest_document

def render_entity_picker():
    """Let user pick an entity and import data."""
    
    st.subheader("📥 Import Healthcare Data")
    
    # Get entities
    entities = get_all_fictional_entities()
    
    # Choose entity type
    entity_type = st.radio(
        "Import From:",
        ["Insurance Company", "Medical Provider"],
        horizontal=True
    )
    
    # Get appropriate list
    if entity_type == "Insurance Company":
        entity_list = entities['insurance']
        type_key = "insurance"
    else:
        entity_list = entities['providers']
        type_key = "provider"
    
    # Create dropdown options
    entity_names = [e['name'] for e in entity_list]
    
    selected_name = st.selectbox(
        "Select Entity",
        options=entity_names,
        help="Choose a fictional entity to simulate data import"
    )
    
    # Find selected entity
    selected_entity = next(e for e in entity_list if e['name'] == selected_name)
    
    # Show entity details
    with st.expander("📋 Entity Details"):
        if type_key == "insurance":
            st.write(f"**Network:** {selected_entity['network_size']}")
            st.write(f"**Plan Types:** {', '.join(selected_entity['plan_types'])}")
        else:
            st.write(f"**Specialty:** {selected_entity['specialty']}")
            st.write(f"**Location:** {selected_entity['location_city']}, {selected_entity['location_state']}")
    
    # Import button
    col1, col2 = st.columns([3, 1])
    with col1:
        num_items = st.slider("Transactions to import", 1, 20, 5)
    
    with col2:
        st.write("")  # Spacing
        if st.button("🚀 Import", type="primary", use_container_width=True):
            import_from_entity(selected_entity, type_key, num_items)


def import_from_entity(entity, entity_type, num_items):
    """Trigger the import."""
    
    with st.spinner(f"Importing from {entity['name']}..."):
        # Call ingestion API
        payload = {
            "user_id": st.session_state.get('user_id', 'demo_user_123'),
            "entity_type": entity_type,
            "entity_id": entity['id'],
            "num_line_items": num_items,
            "metadata": {"source": "entity_picker"}
        }
        
        response = ingest_document(payload)
        
        if response.success:
            st.success(f"✅ Imported {response.line_items_created} transactions!")
            st.session_state.last_import_job_id = response.job_id
            st.rerun()
        else:
            st.error(f"❌ Import failed: {response.message}")
            for error in response.errors:
                st.error(f"  • {error}")
```

### Option 2: Card-Based Selector (Prettier)

```python
def render_entity_cards():
    """Display entities as cards with import buttons."""
    
    st.subheader("📥 Import Healthcare Data")
    
    entities = get_all_fictional_entities()
    
    # Tabs for entity types
    tab1, tab2 = st.tabs(["💳 Insurance Companies", "🏥 Medical Providers"])
    
    with tab1:
        st.write("Select an insurance company to import claims data:")
        render_insurance_cards(entities['insurance'])
    
    with tab2:
        st.write("Select a medical provider to import billing data:")
        render_provider_cards(entities['providers'][:20])  # Show first 20


def render_insurance_cards(insurance_list):
    """Render insurance companies as cards."""
    
    # Show 3 per row
    for i in range(0, len(insurance_list), 3):
        cols = st.columns(3)
        
        for idx, col in enumerate(cols):
            if i + idx < len(insurance_list):
                company = insurance_list[i + idx]
                
                with col:
                    with st.container(border=True):
                        st.markdown(f"### {company['name']}")
                        st.caption(f"Network: {company['network_size'].title()}")
                        st.caption(f"Plans: {', '.join(company['plan_types'][:2])}")
                        
                        if st.button(
                            "Import →",
                            key=f"import_{company['id']}",
                            use_container_width=True
                        ):
                            trigger_import(company, "insurance")


def render_provider_cards(provider_list):
    """Render providers as cards."""
    
    # Filter by specialty first
    specialties = sorted(set(p['specialty'] for p in provider_list))
    selected_specialty = st.selectbox("Filter by Specialty", ["All"] + specialties)
    
    if selected_specialty != "All":
        provider_list = [p for p in provider_list if p['specialty'] == selected_specialty]
    
    # Show in cards
    for i in range(0, len(provider_list), 3):
        cols = st.columns(3)
        
        for idx, col in enumerate(cols):
            if i + idx < len(provider_list):
                provider = provider_list[i + idx]
                
                with col:
                    with st.container(border=True):
                        st.markdown(f"### {provider['name']}")
                        st.caption(f"🏥 {provider['specialty']}")
                        st.caption(f"📍 {provider['location_city']}, {provider['location_state']}")
                        
                        if st.button(
                            "Import →",
                            key=f"import_{provider['id']}",
                            use_container_width=True
                        ):
                            trigger_import(provider, "provider")


def trigger_import(entity, entity_type):
    """Trigger import and save to session state."""
    
    payload = {
        "user_id": st.session_state.get('user_id', 'demo_user_123'),
        "entity_type": entity_type,
        "entity_id": entity['id'],
        "num_line_items": 5
    }
    
    response = ingest_document(payload)
    
    if response.success:
        st.success(f"✅ Imported from {entity['name']}")
        st.session_state.last_import_job_id = response.job_id
        st.rerun()
```

### Option 3: Search & Filter

```python
def render_searchable_entities():
    """Searchable entity picker with filters."""
    
    st.subheader("📥 Import Healthcare Data")
    
    entities = get_all_fictional_entities()
    
    # Entity type selector
    entity_type = st.radio(
        "Import From:",
        ["insurance", "provider"],
        format_func=lambda x: "💳 Insurance Company" if x == "insurance" else "🏥 Medical Provider",
        horizontal=True
    )
    
    entity_list = entities['insurance'] if entity_type == 'insurance' else entities['providers']
    
    # Search box
    search_term = st.text_input(
        "🔍 Search",
        placeholder="Search by name, specialty, location...",
        label_visibility="collapsed"
    )
    
    # Filters
    if entity_type == 'insurance':
        col1, col2 = st.columns(2)
        
        with col1:
            network_filter = st.multiselect(
                "Network Size",
                ["national", "regional", "local"],
                default=["national", "regional", "local"]
            )
        
        with col2:
            plan_filter = st.multiselect(
                "Plan Types",
                ["HMO", "PPO", "EPO", "POS", "HDHP"],
                default=["HMO", "PPO", "EPO", "POS", "HDHP"]
            )
        
        # Apply filters
        filtered = [
            e for e in entity_list
            if e['network_size'] in network_filter
            and any(plan in e['plan_types'] for plan in plan_filter)
            and (not search_term or search_term.lower() in e['name'].lower())
        ]
    
    else:  # providers
        col1, col2 = st.columns(2)
        
        with col1:
            specialties = sorted(set(p['specialty'] for p in entity_list))
            specialty_filter = st.multiselect(
                "Specialty",
                specialties,
                default=specialties[:5]
            )
        
        with col2:
            states = sorted(set(p['location_state'] for p in entity_list))
            state_filter = st.multiselect(
                "State",
                states,
                default=states[:10]
            )
        
        # Apply filters
        filtered = [
            e for e in entity_list
            if e['specialty'] in specialty_filter
            and e['location_state'] in state_filter
            and (not search_term or 
                 search_term.lower() in e['name'].lower() or
                 search_term.lower() in e['location_city'].lower())
        ]
    
    # Show results
    st.write(f"**{len(filtered)} entities found**")
    
    if filtered:
        # Display as table with import buttons
        for entity in filtered[:20]:  # Limit to 20 for performance
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**{entity['name']}**")
                    if entity_type == 'insurance':
                        st.caption(f"Network: {entity['network_size']} • Plans: {', '.join(entity['plan_types'][:2])}")
                    else:
                        st.caption(f"{entity['specialty']} • {entity['location_city']}, {entity['location_state']}")
                
                with col2:
                    if st.button("Import", key=f"btn_{entity['id']}", use_container_width=True):
                        trigger_import(entity, entity_type)
```

---

## Helper Functions

### Get Entity By ID

```python
from _modules.data.fictional_entities import get_entity_by_id

# If you have an entity ID and need to look it up
entities = get_all_fictional_entities()
entity = get_entity_by_id("demo_ins_001", entities['insurance'])

print(entity['name'])  # "Beacon Life (DEMO)"
```

### Filter Providers by Specialty

```python
from _modules.data.fictional_entities import filter_providers_by_specialty

entities = get_all_fictional_entities()
cardiologists = filter_providers_by_specialty(entities['providers'], "Cardiology")

print(f"Found {len(cardiologists)} cardiologists")
```

### Filter Providers by Location

```python
from _modules.data.fictional_entities import filter_providers_by_location

entities = get_all_fictional_entities()
california_providers = filter_providers_by_location(entities['providers'], state="CA")

print(f"Found {len(california_providers)} California providers")
```

---

## Complete Working Example

Here's a full working UI page:

```python
import streamlit as st
from _modules.data.fictional_entities import get_all_fictional_entities
from _modules.ingest.api import ingest_document, get_normalized_data

def render_data_connector_page():
    """Complete data connector page with entity picker."""
    
    st.title("💳 Healthcare Data Connector")
    st.write("Import billing data from fictional healthcare entities (demo)")
    
    # Initialize session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 'demo_user_123'
    
    # Two columns: picker and results
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_entity_picker()
    
    with col2:
        render_import_results()


def render_entity_picker():
    """Left column: entity picker."""
    
    st.subheader("📥 Select Entity")
    
    entities = get_all_fictional_entities()
    
    # Entity type
    entity_type = st.radio(
        "Type",
        ["insurance", "provider"],
        format_func=lambda x: "Insurance" if x == "insurance" else "Provider"
    )
    
    # Get list
    entity_list = entities['insurance'] if entity_type == 'insurance' else entities['providers'][:50]
    
    # Dropdown
    entity_names = [e['name'] for e in entity_list]
    selected_name = st.selectbox("Choose Entity", entity_names)
    
    # Find entity
    selected = next(e for e in entity_list if e['name'] == selected_name)
    
    # Details
    with st.expander("Details"):
        st.json({k: v for k, v in selected.items() if k != 'demo_portal_html'})
    
    # Import
    num_items = st.slider("Transactions", 1, 20, 5)
    
    if st.button("🚀 Import Data", type="primary", use_container_width=True):
        with st.spinner("Importing..."):
            payload = {
                "user_id": st.session_state.user_id,
                "entity_type": entity_type,
                "entity_id": selected['id'],
                "num_line_items": num_items
            }
            
            response = ingest_document(payload)
            
            if response.success:
                st.success(f"✅ Imported {response.line_items_created} items!")
                st.session_state.last_job = response.job_id
                st.rerun()
            else:
                st.error(f"❌ {response.message}")


def render_import_results():
    """Right column: results."""
    
    st.subheader("📊 Imported Data")
    
    if 'last_job' not in st.session_state:
        st.info("No data imported yet. Select an entity and click Import.")
        return
    
    # Get data
    data = get_normalized_data(
        st.session_state.user_id,
        job_id=st.session_state.last_job
    )
    
    if not data.success:
        st.error("Failed to load data")
        return
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Items", data.total_line_items)
    with col2:
        st.metric("Total Billed", f"${data.metadata['total_billed']:.2f}")
    with col3:
        st.metric("You Pay", f"${data.metadata['total_patient_responsibility']:.2f}")
    
    # Table
    import pandas as pd
    df = pd.DataFrame(data.line_items)
    
    st.dataframe(
        df[['service_date', 'procedure_description', 'billed_amount', 
            'patient_responsibility', 'provider_name']],
        use_container_width=True,
        hide_index=True
    )
```

---

## Key Points

1. **30 Insurance Companies** - `entities['insurance']` (IDs: `demo_ins_001` through `demo_ins_030`)
2. **10,000 Providers** - `entities['providers']` (IDs: `demo_prov_000001` through `demo_prov_010000`)
3. **All Cached** - First call takes ~2 seconds, subsequent calls are instant
4. **All Fictional** - Every entity name ends with "(DEMO)" for clarity
5. **Deterministic** - Same entities every time (seeded random generation)

---

## Next Steps

1. Add this entity picker to your Profile Editor's import tab
2. Replace the mock extraction with real ingestion API calls
3. Display imported data in a table
4. Add filtering/sorting capabilities

See `docs/HOW_INGESTION_WORKS.md` for complete integration guide.
