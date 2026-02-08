# How The Entity Picker Works (or Should Work) in the UI

## Current State vs Desired State

### ❌ Current Profile Editor Flow (What You Have Now)

```
User Journey:
1. Click "📥 Import Data" button
2. Step 1: Choose source TYPE
   ├─ "📄 EOB (Explanation of Benefits)"
   ├─ "📊 Insurance CSV Export"
   ├─ "📝 Paste Insurance Text"
   ├─ "🧾 Itemized Medical Bill"
   └─ etc.
3. Step 2: Upload PDF, paste CSV, or paste text
4. Step 3: Review mock-extracted data (not real!)
5. Step 4: Success screen

❌ PROBLEM: No entity selection, uses mock extraction
```

The current system asks "HOW do you want to upload?" but never asks "FROM WHICH insurance company/provider?"

### ✅ Desired Flow (With Entity Picker)

```
User Journey:
1. Click "📥 Import Data" button
2. Step 1: Choose ENTITY (the picker!)

   ┌─────────────────────────────────────────┐
   │ Import From:                            │
   │ ○ Insurance Company  ○ Medical Provider │
   │                                          │
   │ Select Entity:                          │
   │ ▼ [Beacon Life (DEMO)               ]  │
   │   ├─ Beacon Life (DEMO)                 │
   │   ├─ Trust Prime (DEMO)                 │
   │   ├─ Metropolitan Classic Group (DEMO)  │
   │   └─ ...27 more                         │
   │                                          │
   │ Details:                                │
   │ • Network: National                     │
   │ • Plan Types: HMO, PPO, EPO             │
   │                                          │
   │ Transactions to import: [5 ]            │
   │                                          │
   │         [🚀 Import Data]                │
   └─────────────────────────────────────────┘

3. System generates data (no upload needed!)
4. Display results in table
5. Done!

✅ BENEFIT: Simulates portal connection, generates realistic data
```

---

## Visual Comparison

### Current Wizard (Step 1)

```python
# What the current code does:
def render_importer_step1():
    st.subheader("Step 1: Choose Data Source")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏥 Insurance Data")
        if st.button("📄 EOB (Explanation of Benefits)"):
            st.session_state.import_source_type = 'insurance_eob'
            st.session_state.import_wizard_step = 2

        if st.button("📊 Insurance CSV Export"):
            st.session_state.import_source_type = 'insurance_csv'
            st.session_state.import_wizard_step = 2

    with col2:
        st.markdown("### 👨‍⚕️ Provider Data")
        if st.button("🧾 Itemized Medical Bill"):
            st.session_state.import_source_type = 'provider_bill'
            st.session_state.import_wizard_step = 2
```

**UI Output:**
```
┌────────────────────────────────────────────┐
│ Step 1: Choose Data Source                │
│                                            │
│ 🏥 Insurance Data  │  👨‍⚕️ Provider Data    │
│ ──────────────────│──────────────────────  │
│ [📄 EOB (Explanation..)] │ [🧾 Itemized Bill] │
│ [📊 Insurance CSV]       │ [📊 Provider CSV]  │
│ [📝 Paste Text]          │ [📝 Paste Text]    │
└────────────────────────────────────────────┘
```

This asks "WHAT format?" but not "FROM WHERE?"

---

### Desired Entity Picker (Replacement)

```python
# What it SHOULD do:
def render_entity_picker():
    """Let user pick a fictional entity to import from."""

    from _modules.data.fictional_entities import get_all_fictional_entities
    from _modules.ingest.api import ingest_document

    st.subheader("📥 Import Healthcare Data")

    # Get entities
    entities = get_all_fictional_entities()

    # Entity type selector
    entity_type = st.radio(
        "Import From:",
        ["insurance", "provider"],
        format_func=lambda x: "💳 Insurance Company" if x == "insurance" else "🏥 Medical Provider",
        horizontal=True
    )

    # Get appropriate list
    if entity_type == "insurance":
        entity_list = entities['insurance']
    else:
        entity_list = entities['providers'][:100]  # Show first 100 for performance

    # Dropdown selector
    entity_names = [e['name'] for e in entity_list]
    selected_name = st.selectbox(
        "Select Entity",
        options=entity_names,
        help="Choose a fictional entity to simulate data import"
    )

    # Find the selected entity
    selected_entity = next(e for e in entity_list if e['name'] == selected_name)

    # Show entity details
    with st.expander("📋 Entity Details"):
        if entity_type == "insurance":
            st.write(f"**ID:** {selected_entity['id']}")
            st.write(f"**Network:** {selected_entity['network_size'].title()}")
            st.write(f"**Plan Types:** {', '.join(selected_entity['plan_types'])}")
        else:
            st.write(f"**ID:** {selected_entity['id']}")
            st.write(f"**Specialty:** {selected_entity['specialty']}")
            st.write(f"**Location:** {selected_entity['location_city']}, {selected_entity['location_state']}")

    # Number of items slider
    num_items = st.slider(
        "Number of transactions to import",
        min_value=1,
        max_value=20,
        value=5,
        help="How many billing line items to generate"
    )

    # Import button
    if st.button("🚀 Import Data", type="primary", use_container_width=True):
        with st.spinner(f"Importing from {selected_name}..."):
            # Call the ingestion API
            payload = {
                "user_id": st.session_state.get('user_id', 'demo_user_123'),
                "entity_type": entity_type,
                "entity_id": selected_entity['id'],
                "num_line_items": num_items,
                "metadata": {"source": "profile_editor"}
            }

            response = ingest_document(payload)

            if response.success:
                st.success(f"✅ Imported {response.line_items_created} transactions!")
                st.balloons()
                st.session_state.last_import_job_id = response.job_id
                st.rerun()
            else:
                st.error(f"❌ Import failed: {response.message}")
                for error in response.errors:
                    st.error(f"  • {error}")
```

**UI Output:**
```
┌────────────────────────────────────────────────────┐
│ 📥 Import Healthcare Data                         │
│                                                    │
│ Import From:                                       │
│ ⚪ Insurance Company   ⚪ Medical Provider          │
│                                                    │
│ Select Entity:                                     │
│ ┌──────────────────────────────────────────────┐ │
│ │ Beacon Life (DEMO)                        ▼ │ │
│ └──────────────────────────────────────────────┘ │
│                                                    │
│ ▶ 📋 Entity Details                               │
│   • ID: demo_ins_001                              │
│   • Network: National                             │
│   • Plan Types: HMO, PPO, EPO                     │
│                                                    │
│ Number of transactions to import:                 │
│ ├──────●──────────────────┤ 5                    │
│ 1                        20                        │
│                                                    │
│ ┌──────────────────────────────────────────────┐ │
│ │          🚀 Import Data                      │ │
│ └──────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘
```

---

## How The Dropdown Works

### The Dropdown Component

```python
# This is a Streamlit selectbox
selected_name = st.selectbox(
    "Select Entity",
    options=entity_names,  # List of all entity names
    help="Choose a fictional entity"
)

# entity_names looks like:
[
    "Beacon Life (DEMO)",
    "Trust Prime (DEMO)",
    "Metropolitan Classic Group (DEMO)",
    "State Standard (DEMO)",
    "Liberty Shield LLC (DEMO)",
    # ... 25 more
]
```

When rendered, Streamlit creates an interactive dropdown:

```
┌────────────────────────────────────────┐
│ Select Entity                          │
│ ┌────────────────────────────────────┐ │
│ │ Beacon Life (DEMO)              ▼ │ │ ← Click to expand
│ └────────────────────────────────────┘ │
└────────────────────────────────────────┘

When clicked:
┌────────────────────────────────────────┐
│ Select Entity                          │
│ ┌────────────────────────────────────┐ │
│ │ Beacon Life (DEMO)              ▲ │ │ ← Currently selected
│ ├────────────────────────────────────┤ │
│ │ Trust Prime (DEMO)                 │ │ ← Hover to preview
│ │ Metropolitan Classic Group (DEMO)  │ │
│ │ State Standard (DEMO)              │ │
│ │ Liberty Shield LLC (DEMO)          │ │
│ │ ... (scroll for more)              │ │
│ └────────────────────────────────────┘ │
└────────────────────────────────────────┘
```

### Behind The Scenes

```python
# 1. Get all entities (cached, so fast)
entities = get_all_fictional_entities()
# Returns: {"insurance": [30 items], "providers": [10,000 items]}

# 2. Extract names for dropdown
entity_names = [e['name'] for e in entities['insurance']]
# Returns: ["Beacon Life (DEMO)", "Trust Prime (DEMO)", ...]

# 3. User selects from dropdown
selected_name = st.selectbox("Select Entity", entity_names)
# User picks: "Beacon Life (DEMO)"

# 4. Find the full entity object
selected_entity = next(e for e in entities['insurance'] if e['name'] == selected_name)
# Returns: {
#     "id": "demo_ins_001",
#     "name": "Beacon Life (DEMO)",
#     "entity_type": "insurance",
#     "network_size": "national",
#     "plan_types": ["HMO", "PPO", "EPO"]
# }

# 5. Use the entity ID to import
payload = {
    "entity_id": selected_entity['id']  # "demo_ins_001"
}
```

---

## Alternative Picker Styles

### Style 1: Simple Dropdown (Shown Above)
- ✅ Best for: Quick selection from many options
- ✅ Works well on mobile
- ❌ Less visual, can't see details at a glance

### Style 2: Radio Buttons (Few Options)

```python
# Good for 3-10 options
selected = st.radio(
    "Choose Insurance Company",
    options=[e['name'] for e in entities['insurance'][:5]],
    captions=[
        f"{e['network_size']} network"
        for e in entities['insurance'][:5]
    ]
)
```

**UI Output:**
```
Choose Insurance Company:
◉ Beacon Life (DEMO)
  national network
○ Trust Prime (DEMO)
  national network
○ Metropolitan Classic Group (DEMO)
  local network
```

### Style 3: Card Grid (Most Visual)

```python
# Shows entities as clickable cards
for i in range(0, len(entities['insurance']), 3):
    cols = st.columns(3)
    for idx, col in enumerate(cols):
        if i + idx < len(entities['insurance']):
            entity = entities['insurance'][i + idx]
            with col:
                with st.container(border=True):
                    st.markdown(f"### {entity['name']}")
                    st.caption(f"Network: {entity['network_size']}")
                    if st.button("Import", key=entity['id']):
                        trigger_import(entity)
```

**UI Output:**
```
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Beacon Life      │ │ Trust Prime      │ │ Metropolitan     │
│ (DEMO)           │ │ (DEMO)           │ │ Classic (DEMO)   │
│ Network: national│ │ Network: national│ │ Network: local   │
│  [Import →]      │ │  [Import →]      │ │  [Import →]      │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

### Style 4: Searchable Multi-Select (Advanced)

```python
# With search and filters
search = st.text_input("🔍 Search entities", "")

# Filter by network
network_filter = st.multiselect(
    "Network Type",
    ["national", "regional", "local"]
)

# Apply filters
filtered = [
    e for e in entities['insurance']
    if (not search or search.lower() in e['name'].lower())
    and (not network_filter or e['network_size'] in network_filter)
]

# Show results
selected = st.selectbox("Select from results", [e['name'] for e in filtered])
```

---

## Complete Working Example

Here's a **drop-in replacement** for Step 1 of the wizard:

```python
def render_importer_step1_with_entity_picker():
    """Step 1: Pick entity (replaces old source type picker)."""

    from _modules.data.fictional_entities import get_all_fictional_entities
    from _modules.ingest.api import ingest_document

    st.subheader("Step 1: Choose Entity to Import From")

    st.info("💡 This simulates connecting to a healthcare portal and importing your billing data.")

    # Get entities
    entities = get_all_fictional_entities()

    # Layout: 2 columns
    col1, col2 = st.columns([2, 1])

    with col1:
        # Entity type
        entity_type = st.radio(
            "What type of entity?",
            ["insurance", "provider"],
            format_func=lambda x: "💳 Insurance Company (EOBs, Claims)" if x == "insurance" else "🏥 Medical Provider (Bills, Invoices)",
            help="Insurance companies provide EOBs and claim history. Providers send itemized bills."
        )

        # Get list
        if entity_type == "insurance":
            entity_list = entities['insurance']
            icon = "💳"
        else:
            entity_list = entities['providers'][:50]  # Limit for performance
            icon = "🏥"

        # Dropdown
        st.write(f"**{icon} Select Entity:**")
        entity_names = [e['name'] for e in entity_list]
        selected_name = st.selectbox(
            "Select Entity",
            options=entity_names,
            label_visibility="collapsed",
            help=f"Choose from {len(entity_list)} fictional entities"
        )

        # Find entity
        selected_entity = next(e for e in entity_list if e['name'] == selected_name)

        # Number of items
        num_items = st.slider(
            "📊 How many transactions to import?",
            min_value=1,
            max_value=20,
            value=5,
            help="Number of billing line items to generate"
        )

    with col2:
        # Entity details card
        st.markdown("**📋 Entity Info:**")
        with st.container(border=True):
            st.write(f"**ID:** `{selected_entity['id']}`")

            if entity_type == "insurance":
                st.write(f"**Network:** {selected_entity['network_size'].title()}")
                st.write(f"**Plans:**")
                for plan in selected_entity['plan_types']:
                    st.write(f"  • {plan}")
            else:
                st.write(f"**Specialty:** {selected_entity['specialty']}")
                st.write(f"**Location:** {selected_entity['location_city']}, {selected_entity['location_state']}")

        # Preview button
        if st.button("👁️ Preview Portal", use_container_width=True):
            st.session_state.show_portal_preview = selected_entity['id']

    st.markdown("---")

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.profile_page = 'overview'
            st.rerun()

    with col3:
        if st.button("🚀 Import Now", type="primary", use_container_width=True):
            # Do the import!
            with st.spinner(f"Importing from {selected_name}..."):
                payload = {
                    "user_id": st.session_state.get('user_id', 'demo_user_123'),
                    "entity_type": entity_type,
                    "entity_id": selected_entity['id'],
                    "num_line_items": num_items,
                    "metadata": {
                        "source": "profile_editor",
                        "entity_name": selected_name
                    }
                }

                response = ingest_document(payload)

                if response.success:
                    st.success(f"✅ Successfully imported {response.line_items_created} transactions!")
                    st.balloons()

                    # Save job ID and advance to results
                    st.session_state.last_import_job_id = response.job_id
                    st.session_state.import_wizard_step = 3  # Skip to results
                    st.rerun()
                else:
                    st.error(f"❌ Import failed: {response.message}")
                    with st.expander("Error Details"):
                        for error in response.errors:
                            st.write(f"• {error}")

    # Optional: Portal preview
    if st.session_state.get('show_portal_preview'):
        with st.expander("🌐 Portal Preview", expanded=True):
            entity = next(e for e in entity_list if e['id'] == st.session_state.show_portal_preview)
            components.html(entity['demo_portal_html'], height=600, scrolling=True)
```

---

## Key Takeaways

### How The Picker Works:

1. **Load entities** → `get_all_fictional_entities()` (30 insurance + 10k providers)
2. **Display dropdown** → `st.selectbox()` with entity names
3. **User selects** → Clicks dropdown, picks "Beacon Life (DEMO)"
4. **Find entity** → Look up full entity object by name
5. **Import data** → Call `ingest_document()` with entity ID
6. **Show results** → Display imported transactions

### Why This Is Better:

- ❌ **Old way:** Upload PDF → Extract (mock) → Review fake data
- ✅ **New way:** Pick entity → Generate real demo data → Review realistic data

### What You Get:

- 30 insurance companies to pick from
- 10,000 providers to pick from
- Realistic CPT codes, amounts, dates
- Proper insurance plan details
- All data marked as "(DEMO)"

Ready to integrate this into the Profile Editor! 🚀

