# Module Reference Guide

Quick reference for the refactored codebase modules.

## Core Modules

### `_modules/core/auth.py`
**Purpose**: Application access control and authentication

**Functions**:
- `check_access_password() -> bool`: Validates user access via password gate

**Usage**:
```python
from _modules.core.auth import check_access_password

if not check_access_password():
    return  # User hasn't entered correct password
```

---

### `_modules/core/analysis_runner.py`
**Purpose**: Document analysis workflow orchestration

**Functions**:
- `run_document_analysis(documents, agent, analyze_clicked) -> dict`: Runs analysis on all documents
- `render_total_savings_summary(total_savings, per_doc_savings)`: Displays savings summary
- `render_cached_results(documents, total_savings, per_doc_savings)`: Renders cached analysis results

**Usage**:
```python
from _modules.core.analysis_runner import run_document_analysis

result = run_document_analysis(documents, agent, True)
if result:
    total_savings = result["total_savings"]
    per_document_savings = result["per_document_savings"]
```

---

## UI Modules

### `_modules/ui/bootstrap.py`
**Purpose**: UI initialization and setup

**Functions**:
- `bootstrap_ui_minimal()`: Sets up page config, CSS, and header (for all pages)
- `bootstrap_home_page()`: Home page specific initialization (demo docs, help)
- `should_enable_guided_tour() -> bool`: Checks if guided tour should be enabled

**Usage**:
```python
from _modules.ui.bootstrap import bootstrap_ui_minimal, bootstrap_home_page

bootstrap_ui_minimal()  # Always call first
bootstrap_home_page()   # Only on home page
```

---

### `_modules/ui/page_router.py`
**Purpose**: Page navigation and routing

**Functions**:
- `render_page_navigation() -> str`: Renders navigation UI, returns current page
- `route_to_page(page) -> bool`: Routes to page, returns True if page was rendered

**Usage**:
```python
from _modules.ui.page_router import render_page_navigation, route_to_page

current_page = render_page_navigation()
if route_to_page(current_page):
    return  # Non-home page was rendered, stop here
```

---

## Provider Modules

### `_modules/providers/provider_registry.py`
**Purpose**: LLM provider registration and management

**Constants**:
- `ENGINE_OPTIONS`: Dict mapping user-facing names to provider IDs

**Functions**:
- `register_providers()`: Registers all available LLM providers

**Usage**:
```python
from _modules.providers.provider_registry import register_providers, ENGINE_OPTIONS

register_providers()  # Call once at startup

# For provider selection
engine_label = st.selectbox("Engine", list(ENGINE_OPTIONS.keys()))
selected_provider = ENGINE_OPTIONS[engine_label]
```

---

## Import Patterns

### Typical medBillDozer.py imports:
```python
# Core
from _modules.core.auth import check_access_password
from _modules.core.orchestrator_agent import OrchestratorAgent
from _modules.core.analysis_runner import run_document_analysis, render_cached_results

# UI
from _modules.ui.bootstrap import bootstrap_ui_minimal, bootstrap_home_page
from _modules.ui.page_router import render_page_navigation, route_to_page

# Providers
from _modules.providers.provider_registry import register_providers, ENGINE_OPTIONS
```

---

## Module Dependencies

```
(medBillDozer.py)
├── core/
│   ├── auth.py                    (no dependencies)
│   └── analysis_runner.py         (depends on: orchestrator_agent, ui modules, utils)
├── ui/
│   ├── bootstrap.py               (depends on: ui.ui, config)
│   └── page_router.py             (depends on: ui modules, audio_controls)
└── providers/
    └── provider_registry.py       (depends on: llm_interface, provider implementations)
```

---

## Testing Checklist

When modifying these modules, verify:

- [ ] `auth.py`: Password gate works, environment variable override works
- [ ] `bootstrap.py`: UI initializes correctly on all pages, tour toggle works
- [ ] `page_router.py`: Navigation works, pages render correctly
- [ ] `provider_registry.py`: Providers register successfully, selection UI works
- [ ] `analysis_runner.py`: Document analysis completes, results render, caching works

---

## Quick Start for Contributors

Adding a new feature typically involves:

1. **Authentication feature**: Add to `_modules/core/auth.py`
2. **UI initialization**: Add to `_modules/ui/bootstrap.py`
3. **New page**: Add routing in `_modules/ui/page_router.py`
4. **New provider**: Register in `_modules/providers/provider_registry.py`
5. **Analysis feature**: Add to `_modules/core/analysis_runner.py`

Then update `medBillDozer.py` to call your new functions.
