# Configuration Package

This package centralizes all configuration constants and settings for MedBillDozer.

## Structure

```
config/
├── __init__.py          # Package exports
├── constants.py         # Application-level constants
├── widget_config.py     # UI widget configuration
└── README.md           # This file
```

## Modules

### `constants.py`
Application-level constants used across the system:
- **Data Generation**: `DEFAULT_INSURANCE_COUNT`, `DEFAULT_PROVIDER_COUNT`, `DEFAULT_SEED`
- **Entity Types**: `ENTITY_TYPE_INSURANCE`, `ENTITY_TYPE_PROVIDER`

### `widget_config.py`
UI widget configuration:
- **Token**: `BILLDOZER_TOKEN` - Widget version identifier for iframe communication
- **Display**: `WIDGET_HEIGHT`, `WIDGET_SCROLLING` - Widget display settings

## Usage

Import constants from the config package:

```python
from config import (
    BILLDOZER_TOKEN,
    DEFAULT_INSURANCE_COUNT,
    ENTITY_TYPE_INSURANCE,
)
```

## Adding New Configuration

1. **Determine the appropriate file**:
   - Widget/UI settings → `widget_config.py`
   - Application constants → `constants.py`
   - Feature flags → Use `app_config.yaml` instead

2. **Add the constant** with documentation:
   ```python
   # Description of what this constant controls
   MY_CONSTANT = "value"
   ```

3. **Export in `__init__.py`**:
   ```python
   from .constants import MY_CONSTANT
   
   __all__ = [
       'MY_CONSTANT',
       # ... other exports
   ]
   ```

4. **Update this README** with the new constant

## Configuration Files vs Constants

- **Use `config/` package** for: Hardcoded constants, version identifiers, system defaults
- **Use `app_config.yaml`** for: User-configurable settings, feature flags, preferences

See `docs/CONFIG_README.md` for YAML configuration documentation.
