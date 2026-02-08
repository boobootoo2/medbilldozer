# MedBillDozer.py Refactoring Diagram

## Before Refactoring

```
medBillDozer.py (788 lines)
├── Imports (100+ lines)
├── check_access_password() 
├── should_enable_guided_tour()
├── ENGINE_OPTIONS constant
├── render_total_savings_summary()
├── bootstrap_ui_minimal()
├── bootstrap_home_page()
├── register_providers()
├── main()
│   ├── Access control
│   ├── Splash screen
│   ├── Page navigation (inline)
│   ├── Page routing (inline)
│   ├── UI bootstrap
│   ├── Provider registration
│   ├── Tour initialization
│   ├── Privacy dialog
│   ├── Doc assistant
│   ├── Health profile
│   ├── Document input
│   ├── Provider selection
│   ├── Coverage matrix
│   ├── Debug controls
│   ├── Orchestrator setup
│   ├── Analysis workflow (200+ lines)
│   │   ├── Billdozer widget
│   │   ├── For each document:
│   │   │   ├── DAG rendering
│   │   │   ├── Analysis execution
│   │   │   ├── Identity enhancement
│   │   │   ├── Transaction normalization
│   │   │   ├── De-duplication
│   │   │   ├── Savings calculation
│   │   │   └── Results rendering
│   │   ├── Aggregate metrics
│   │   ├── Coverage matrix
│   │   └── Pipeline comparison
│   ├── Cached results rendering
│   ├── Debug output
│   └── Footer
└── __main__
```

## After Refactoring

```
medBillDozer.py (368 lines) - Clean orchestration layer
├── Imports (organized by category)
└── main()
    ├── check_access_password() ───────────────────────> _modules/core/auth.py
    ├── Splash screen
    ├── bootstrap_ui_minimal() ────────────────────────> _modules/ui/bootstrap.py
    ├── initialize_audio_state()
    ├── render_page_navigation() ──────────────────────> _modules/ui/page_router.py
    ├── route_to_page() ───────────────────────────────> _modules/ui/page_router.py
    ├── bootstrap_home_page() ─────────────────────────> _modules/ui/bootstrap.py
    ├── register_providers() ──────────────────────────> _modules/providers/provider_registry.py
    ├── Tour initialization
    ├── Privacy dialog
    ├── Doc assistant
    ├── Health profile
    ├── Document input
    ├── Provider selection (using ENGINE_OPTIONS) ─────> _modules/providers/provider_registry.py
    ├── Coverage matrix
    ├── Debug controls
    ├── Orchestrator setup
    ├── run_document_analysis() ───────────────────────> _modules/core/analysis_runner.py
    ├── render_cached_results() ───────────────────────> _modules/core/analysis_runner.py
    ├── Debug output
    └── Footer

_modules/core/auth.py (56 lines)
└── check_access_password()

_modules/ui/bootstrap.py (51 lines)
├── should_enable_guided_tour()
├── bootstrap_ui_minimal()
└── bootstrap_home_page()

_modules/providers/provider_registry.py (52 lines)
├── ENGINE_OPTIONS
└── register_providers()

_modules/ui/page_router.py (68 lines)
├── render_page_navigation()
└── route_to_page()

_modules/core/analysis_runner.py (275 lines)
├── render_total_savings_summary()
├── run_document_analysis()
│   ├── Document validation
│   ├── Billdozer widget setup
│   ├── For each document:
│   │   ├── DAG container creation
│   │   ├── Analysis execution with progress
│   │   ├── Session persistence
│   │   ├── Identity enhancement
│   │   ├── Transaction normalization
│   │   ├── De-duplication
│   │   ├── Savings aggregation
│   │   └── Results rendering
│   ├── Aggregate metrics
│   ├── Coverage matrix
│   └── Pipeline comparison
└── render_cached_results()
```

## Flow Diagram

### Main Application Flow

```
┌─────────────────────────────────────────────────┐
│              User Access medBillDozer.py                 │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  Access Control Gate │ ◄─── auth.py
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │   Splash Screen?     │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  Bootstrap UI        │ ◄─── bootstrap.py
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  Page Navigation     │ ◄─── page_router.py
         └──────────┬───────────┘
                    │
                    ├─── Profile? ──> route_to_page() ──> Render Profile
                    ├─── API? ──────> route_to_page() ──> Render API Docs
                    │
                    ▼
         ┌──────────────────────┐
         │  Home Page           │
         └──────────┬───────────┘
                    │
                    ├──> Bootstrap Home ───────────────> bootstrap.py
                    ├──> Register Providers ───────────> provider_registry.py
                    ├──> Guided Tour Init
                    ├──> Privacy Dialog
                    ├──> Document Input
                    │
                    ▼
         ┌──────────────────────┐
         │  Analyze Button?     │
         └──────────┬───────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  Run Analysis        │ ◄─── analysis_runner.py
         └──────────┬───────────┘
                    │
                    ├──> Document Analysis Loop
                    ├──> Savings Calculation
                    ├──> Results Rendering
                    │
                    ▼
         ┌──────────────────────┐
         │  Render Footer       │
         └──────────────────────┘
```

## Module Interaction Map

```
                    (medBillDozer.py)
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
    core/         ui/          providers/
        │             │             │
        ├─ auth       ├─ bootstrap  └─ provider_registry
        └─ analysis   └─ page_router
           _runner
              │
              ├──> orchestrator_agent
              ├──> document_identity
              ├──> transaction_normalization
              ├──> coverage_matrix
              ├──> ui modules (ui, ui_coverage_matrix, ui_pipeline_dag)
              └──> utils (serialization, config)
```

## Benefits Visualization

### Code Complexity Reduction

```
Before:
medBillDozer.py ████████████████████████████████████████ 788 lines

After:
medBillDozer.py ████████████████████ 368 lines (53% reduction!)
       + 5 new focused modules
```

### Separation of Concerns

```
Before:
┌────────────────────────────────┐
│         medBillDozer.py                 │
│  - Auth + UI + Analysis +      │
│    Providers + Routing +       │
│    Everything else             │
└────────────────────────────────┘

After:
┌──────────┐ ┌──────────┐ ┌──────────┐
│   Auth   │ │    UI    │ │ Providers│
│ (auth.py)│ │(bootstrap│ │(registry)│
└──────────┘ │page_route│ └──────────┘
             │  r.py)   │
             └──────────┘
                  │
        ┌─────────┴─────────┐
        │   Analysis        │
        │(analysis_runner)  │
        └───────────────────┘
                  │
        ┌─────────┴─────────┐
        │   Orchestration   │
        │     ((medBillDozer.py))      │
        └───────────────────┘
```

## Lines of Code Distribution

| Module                    | Lines | Purpose              |
|---------------------------|-------|----------------------|
| `medBillDozer.py`                  | 368   | Orchestration        |
| `auth.py`                 | 56    | Access control       |
| `bootstrap.py`            | 51    | UI initialization    |
| `provider_registry.py`    | 52    | Provider management  |
| `page_router.py`          | 68    | Page navigation      |
| `analysis_runner.py`      | 275   | Analysis workflow    |
| **Total**                 | **870** | **(was 788)**      |

*Net increase of 82 lines (10%) for much better organization*
