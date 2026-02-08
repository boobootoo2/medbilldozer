# Profile Editor Architecture

## Navigation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                       medBillDozer.py (main)                         │
│                                                             │
│  1. Check access password (APP_ACCESS_PASSWORD)            │
│  2. Initialize page navigation state                       │
│  3. Render sidebar navigation buttons                      │
│  4. Route to selected page                                 │
└─────────────────────────────────────────────────────────────┘
                          │
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
┌──────────────────┐          ┌──────────────────────┐
│   🏠 Home Page   │          │  📋 Profile Editor   │
│                  │          │                      │
│  - Document      │          │  - Identity          │
│    analysis      │          │  - Insurance         │
│  - Results       │          │  - Providers         │
│  - Coverage      │          │  - Importer          │
│  - Guided tour   │          │                      │
└──────────────────┘          └──────────────────────┘
```

## Profile Editor Page Structure

```
┌───────────────────────────────────────────────────────────────┐
│                    Profile Editor Pages                       │
└───────────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┬──────────────┐
          │               │               │              │
          ▼               ▼               ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ Overview │   │ Identity │   │Insurance │   │Providers │
    │          │   │          │   │          │   │          │
    │ - Stats  │   │ - Name   │   │ - Plans  │   │ - Docs   │
    │ - Quick  │   │ - DOB    │   │ - CRUD   │   │ - NPI    │
    │   Actions│   │ - Address│   │          │   │ - CRUD   │
    └──────────┘   └──────────┘   └──────────┘   └──────────┘
          │
          └──────────────────┐
                             ▼
                      ┌──────────────┐
                      │   Importer   │
                      │              │
                      │  4-Step      │
                      │  Wizard      │
                      └──────────────┘
```

## Import Wizard Flow

```
┌────────────────────────────────────────────────────────────┐
│                  Import Wizard (4 Steps)                   │
└────────────────────────────────────────────────────────────┘

Step 1: Choose Source
┌────────────────────┐
│ - Insurance EOB    │
│ - Claim History    │──┐
│ - Bill/Receipt     │  │
└────────────────────┘  │
                        ▼
Step 2: Provide Data
┌────────────────────┐
│ - PDF Upload       │
│ - CSV Paste        │──┐
│ - Text Input       │  │
└────────────────────┘  │
                        ▼
Step 3: Review & Edit
┌────────────────────┐
│ - Extracted Data   │
│ - Inline Edit      │──┐
│ - Add/Remove Items │  │
└────────────────────┘  │
                        ▼
Step 4: Complete
┌────────────────────┐
│ - Success Message  │
│ - View Profile     │
│ - Import More      │
└────────────────────┘
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      User Actions                           │
└─────────────────────────────────────────────────────────────┘
                          │
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
┌──────────────────┐          ┌──────────────────────┐
│   UI Components  │          │   Session State      │
│   (Streamlit)    │◄─────────│   (st.session_state) │
└──────────────────┘          └──────────────────────┘
          │                               │
          │                               │
          ▼                               ▼
┌──────────────────┐          ┌──────────────────────┐
│  Profile Editor  │          │   Atomic Write       │
│  Module          │──────────►│   (tempfile +        │
│                  │          │    os.replace)       │
└──────────────────┘          └──────────────────────┘
                                          │
                                          ▼
                              ┌──────────────────────┐
                              │   JSON Files         │
                              │   (./data/)          │
                              │                      │
                              │  - user_profile.json │
                              │  - insurance_plans   │
                              │  - providers.json    │
                              │  - import_jobs.json  │
                              │  - normalized_items  │
                              └──────────────────────┘
```

## Module Structure

```
_modules/ui/profile_editor.py
│
├── TypedDict Models (Lines 1-100)
│   ├── UserProfile
│   ├── InsurancePlan
│   ├── Provider
│   ├── ImportJob
│   ├── Document
│   └── NormalizedLineItem
│
├── Feature Flags (Lines 101-120)
│   ├── is_profile_editor_enabled()
│   └── is_importer_enabled()
│
├── Data Directory (Lines 121-130)
│   └── get_data_dir()
│
├── Persistence Layer (Lines 131-220)
│   ├── atomic_write_json()
│   ├── load_profile()
│   ├── save_profile()
│   ├── load_insurance_plans()
│   ├── save_insurance_plans()
│   ├── load_providers()
│   ├── save_providers()
│   ├── load_import_jobs()
│   ├── save_import_jobs()
│   └── load_normalized_line_items()
│
├── UI Renderers (Lines 221-1900)
│   ├── render_profile_overview()
│   ├── render_identity_editor()
│   ├── render_insurance_editor()
│   ├── render_provider_editor()
│   └── render_importer()
│       ├── render_choose_source()
│       ├── render_provide_data()
│       ├── render_review_edit()
│       └── render_complete()
│
└── Main Entry Point (Lines 1901-2000)
    └── render_profile_editor()
```

## Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│                         medBillDozer.py                              │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ imports
                          ▼
┌─────────────────────────────────────────────────────────────┐
│         from _modules.ui.profile_editor import:             │
│                                                             │
│  - render_profile_editor()    [Main entry point]           │
│  - is_profile_editor_enabled() [Feature flag check]        │
│  - load_profile()              [Get user identity]         │
│  - load_insurance_plans()      [Get insurance data]        │
│  - load_providers()            [Get provider directory]    │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ used by
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  Analysis Orchestrator                      │
│                                                             │
│  Uses profile data to enhance document analysis:            │
│  - Verify insurance coverage                                │
│  - Check provider network status                            │
│  - Match patient information                                │
│  - Calculate expected vs actual charges                     │
└─────────────────────────────────────────────────────────────┘
```

## Environment Variables

```
┌─────────────────────────────────────────────────────────────┐
│                    .env Configuration                       │
└─────────────────────────────────────────────────────────────┘

PROFILE_EDITOR_ENABLED=TRUE
         │
         ├──► Controls visibility of Profile button
         ├──► Enables/disables profile editor module
         └──► Checked by: is_profile_editor_enabled()

IMPORTER_ENABLED=TRUE
         │
         ├──► Controls import wizard visibility
         ├──► Requires PROFILE_EDITOR_ENABLED=TRUE
         └──► Checked by: is_importer_enabled()
```

## Security & Privacy Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Privacy Layers                          │
└─────────────────────────────────────────────────────────────┘

Layer 1: Local Storage
    │
    ├──► All data in ./data/ directory
    ├──► No cloud, no external APIs
    └──► User controls data location

Layer 2: Git Protection
    │
    ├──► data/*.json in .gitignore
    ├──► Prevents accidental commits
    └──► Automatic setup in enable script

Layer 3: File Permissions
    │
    ├──► Standard filesystem permissions
    └──► User controls who can access

Layer 4: Feature Flags
    │
    ├──► Can disable entire feature
    └──► Environment variable control
```

## Type Safety Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TypedDict Models                         │
└─────────────────────────────────────────────────────────────┘

UserProfile
    ├── full_name: str
    ├── date_of_birth: str
    ├── address: dict
    │   ├── street: str
    │   ├── city: str
    │   ├── state: str
    │   └── zip_code: str
    └── created_at: str

InsurancePlan
    ├── plan_id: str
    ├── carrier_name: str
    ├── plan_name: str
    ├── member_id: str
    ├── group_number: str
    ├── coverage_start_date: str
    ├── coverage_end_date: str
    ├── is_active: bool
    ├── plan_type: str
    ├── network_status: str
    ├── deductible: dict
    │   ├── individual: float
    │   └── family: float
    ├── out_of_pocket_max: dict
    │   ├── individual: float
    │   └── family: float
    └── copays: dict

Provider
    ├── provider_id: str
    ├── name: str
    ├── npi: str
    ├── specialty: str
    ├── practice_name: str
    ├── in_network: bool
    └── notes: str
```

## Atomic Write Pattern

```
┌─────────────────────────────────────────────────────────────┐
│             Atomic Write Sequence                           │
└─────────────────────────────────────────────────────────────┘

1. Create temp file
   tempfile.NamedTemporaryFile()
            │
            ▼
2. Write data to temp
   json.dump(data, tmp)
            │
            ▼
3. Atomic rename
   os.replace(tmp, final)
            │
            ▼
4. Success or rollback
   (OS guarantees atomicity)

Benefits:
✅ No partial writes
✅ No data corruption
✅ Crash-safe
✅ Concurrent-safe
```

## Performance Characteristics

```
Operation           Time Complexity   Space Complexity
─────────────────────────────────────────────────────
Load Profile        O(1)             O(1)
Save Profile        O(1)             O(1)
Load All Plans      O(n)             O(n)
Save All Plans      O(n)             O(n)
Add Plan            O(n)             O(n)
Update Plan         O(n)             O(n)
Delete Plan         O(n)             O(n)
Load All Providers  O(n)             O(n)
Save All Providers  O(n)             O(n)
Import Job          O(m)             O(m)

where:
n = number of plans or providers (typically < 10)
m = number of line items in import (typically < 1000)

Note: For m > 10,000 line items, consider database migration
```

## Future Enhancement Paths

```
Current: JSON Files
         │
         ├──► Simple, portable, human-readable
         ├──► Good for < 10,000 line items
         └──► No dependencies

Future: SQLite
         │
         ├──► Better for > 10,000 line items
         ├──► Complex queries
         └──► Still local, no server

Future: PostgreSQL
         │
         ├──► Production scale
         ├──► Multi-user support
         └──► Advanced queries

Future: Authentication
         │
         ├──► User accounts
         ├──► Multi-tenant
         └──► Role-based access
```

---

## Quick Reference: Key Functions

### Feature Flags
```python
is_profile_editor_enabled() -> bool  # Check if profile editor is enabled
is_importer_enabled() -> bool        # Check if importer is enabled
```

### Data Access
```python
load_profile() -> Optional[UserProfile]           # Get user identity
save_profile(profile: UserProfile) -> bool        # Save user identity
load_insurance_plans() -> List[InsurancePlan]     # Get all plans
save_insurance_plans(plans: List) -> bool         # Save all plans
load_providers() -> List[Provider]                # Get all providers
save_providers(providers: List) -> bool           # Save all providers
```

### Main Entry Point
```python
render_profile_editor() -> None  # Render entire profile editor UI
```

---

## Architecture Principles

1. **Separation of Concerns**
   - UI layer (Streamlit components)
   - Data layer (JSON persistence)
   - Business logic (validation, CRUD)

2. **Type Safety**
   - TypedDict for all data models
   - IDE autocomplete support
   - Runtime validation

3. **Privacy First**
   - Local storage only
   - No external APIs
   - Git protection

4. **Atomic Operations**
   - No partial writes
   - Crash-safe persistence
   - Data integrity guaranteed

5. **Progressive Enhancement**
   - Works without profile data
   - Enhances analysis when available
   - Graceful degradation

6. **Accessibility**
   - Keyboard navigation
   - Screen reader support
   - Clear visual hierarchy
   - No color-only indicators

---

This architecture provides a solid foundation for profile management while maintaining the privacy-first, local-first principles of medBillDozer.

