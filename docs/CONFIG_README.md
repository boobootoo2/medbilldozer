# Configuration Guide

medBillDozer uses a YAML configuration file (`app_config.yaml`) to control optional features and application behavior.

## Configuration File Location

The configuration file should be placed in the project root directory:
```
medbilldozer/
├── app_config.yaml  ← Configuration file
├── app.py
├── requirements.txt
└── ...
```

## Quick Start

### Disable a Feature

To disable any feature, edit `app_config.yaml` and set `enabled: false`:

```yaml
features:
  assistant:
    enabled: false  # Disables the AI documentation assistant

  dag:
    enabled: false  # Disables pipeline DAG visualization

  debug:
    enabled: true   # Enables debug mode with extra developer options
```

### Common Configurations

#### Minimal UI (No Assistant, No DAG)
```yaml
features:
  assistant:
    enabled: false
  dag:
    enabled: false
  debug:
    enabled: false
```

#### Debug/Developer Mode
```yaml
features:
  debug:
    enabled: true
    show_orchestration: true
    show_workflow_logs: true
    show_raw_analysis: true

developer:
  show_technical_errors: true
  enable_profiling: true
  log_level: "DEBUG"
```

#### Production Mode (Minimal Debug)
```yaml
features:
  debug:
    enabled: false

developer:
  show_technical_errors: false
  log_level: "WARNING"
```

## Configuration Sections

### Features

Control major application features:

#### `features.assistant`
- **enabled**: Show/hide AI documentation assistant (Billy/Billie)
- **default_provider**: Default AI provider for assistant (`"openai"` or `"gemini"`)
- **default_character**: Default avatar character (`"billy"` or `"billie"`)

#### `features.dag`
- **enabled**: Show/hide pipeline workflow DAG visualization
- **expanded_by_default**: Whether DAG accordions start expanded
- **show_comparison_table**: Show multi-document comparison table

#### `features.debug`
- **enabled**: Enable debug mode with extra developer controls
- **show_orchestration**: Show orchestration decision details
- **show_workflow_logs**: Show detailed workflow execution logs
- **show_raw_analysis**: Show raw analysis JSON output

#### `features.privacy_ui`
- **enabled**: Show/hide privacy information dialog

#### `features.coverage_matrix`
- **enabled**: Show/hide insurance coverage matrix feature

### UI Preferences

Customize the user interface:

```yaml
ui:
  page_title: "medBillDozer"
  page_icon: "�"
  layout: "wide"  # or "centered"

  sidebar:
    show_logo: true
    show_quick_help_buttons: true
    max_conversation_history: 3

  results:
    show_savings_estimate: true
    show_line_items: true
    show_detailed_facts: true
    expand_issues_by_default: true
```

### AI Provider Configuration

```yaml
ai_providers:
  default_analysis_provider: "openai"  # Default for document analysis
  available_providers:
    - "openai"
    - "gemini"

  models:
    openai:
      analysis: "gpt-4o-mini"
      assistant: "gpt-4o-mini"
    gemini:
      analysis: "gemini-2.0-flash-exp"
      assistant: "gemini-2.0-flash-exp"
```

### Processing Limits

```yaml
limits:
  max_documents_per_batch: 10
  max_document_size_chars: 100000
  analysis_timeout_seconds: 120
```

### Developer Options

```yaml
developer:
  show_technical_errors: false  # Show full error stack traces
  enable_profiling: false       # Enable performance profiling
  log_level: "INFO"             # DEBUG, INFO, WARNING, ERROR
```

## Using Configuration in Code

### Import Configuration Functions

```python
from _modules.utils.config import (
    get_config,
    is_assistant_enabled,
    is_dag_enabled,
    is_debug_enabled,
)
```

### Check Feature Flags

```python
# Simple feature check
if is_assistant_enabled():
    render_doc_assistant()

if is_dag_enabled():
    render_pipeline_dag(workflow_log)

if is_debug_enabled():
    show_debug_info()
```

### Access Configuration Values

```python
from _modules.utils.config import get_config

config = get_config()

# Get nested values with dot notation
page_title = config.get("ui.page_title", "Default Title")
max_docs = config.get("limits.max_documents_per_batch", 5)

# Get entire sections
ui_config = config.get("ui", {})
sidebar_config = config.get("ui.sidebar", {})
```

### Reload Configuration at Runtime

```python
from _modules.utils.config import reload_config

# Force reload from file (useful for testing)
reload_config()
```

## Default Behavior

If `app_config.yaml` is missing or incomplete:
- ✅ The app uses sensible defaults (all features enabled)
- ✅ A warning is logged to console
- ✅ Application continues to function normally

## Environment-Specific Configurations

You can maintain multiple configuration files for different environments:

```bash
# Development
cp app_config.yaml app_config.dev.yaml

# Production
cp app_config.yaml app_config.prod.yaml

# Switch configurations
cp app_config.prod.yaml app_config.yaml
```

## Troubleshooting

### Configuration Not Loading

1. **Check file location**: Must be `app_config.yaml` in project root
2. **Check YAML syntax**: Use a YAML validator to verify syntax
3. **Check permissions**: Ensure file is readable
4. **View console**: Look for warning messages about config loading

### Feature Not Responding to Config Changes

1. **Restart Streamlit**: Configuration is loaded at startup
2. **Clear cache**: Streamlit may cache some values
3. **Check spelling**: Feature names are case-sensitive

### Invalid Configuration Values

If configuration values are invalid, defaults are used automatically. Check console for warnings about invalid values.

## Examples

### Disable Everything for Testing

```yaml
features:
  assistant:
    enabled: false
  dag:
    enabled: false
  debug:
    enabled: false
  privacy_ui:
    enabled: false
  coverage_matrix:
    enabled: false
```

### Enable Debug Mode

```yaml
features:
  debug:
    enabled: true
    show_orchestration: true
    show_workflow_logs: true
    show_raw_analysis: true

developer:
  show_technical_errors: true
  log_level: "DEBUG"
```

### Minimal UI for Demos

```yaml
features:
  assistant:
    enabled: false
  dag:
    enabled: true
    show_comparison_table: false
  debug:
    enabled: false

ui:
  layout: "centered"
  results:
    expand_issues_by_default: false
```

## Best Practices

1. **Version control**: Commit your config file to git
2. **Documentation**: Comment your changes in the YAML file
3. **Testing**: Test configuration changes in development first
4. **Backup**: Keep a backup of working configurations
5. **Minimal changes**: Only change what you need

## Need Help?

- See `docs/QUICKSTART.md` for general application help
- See `docs/USER_GUIDE.md` for detailed usage instructions
- Check console output for configuration loading warnings
- Restore defaults by deleting custom values from YAML file

