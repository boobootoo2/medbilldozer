# Configuration Folder Migration

**Date**: January 31, 2026  
**Status**: ✅ Complete

## Summary

Created a new `config/` package to centralize application configuration constants and settings, improving code organization and maintainability.

## Changes Made

### New Structure

```
config/
├── __init__.py          # Package exports
├── constants.py         # Application-level constants
├── widget_config.py     # UI widget configuration
└── README.md           # Documentation
```

### Files Created

1. **`config/__init__.py`** - Package initialization with exports
2. **`config/constants.py`** - Application constants:
   - `DEFAULT_INSURANCE_COUNT = 30`
   - `DEFAULT_PROVIDER_COUNT = 10000`
   - `DEFAULT_SEED = 42`
   - `ENTITY_TYPE_INSURANCE = "insurance"`
   - `ENTITY_TYPE_PROVIDER = "provider"`

3. **`config/widget_config.py`** - Widget settings:
   - `BILLDOZER_TOKEN = "BILLDOZER_v1"`
   - `WIDGET_HEIGHT = 180`
   - `WIDGET_SCROLLING = False`

4. **`config/README.md`** - Documentation for the config package

### Files Modified

1. **`_modules/ui/billdozer_widget.py`**
   - Removed: Local `BILLDOZER_TOKEN` definition
   - Added: `from config import BILLDOZER_TOKEN`

2. **`_modules/data/fictional_entities.py`**
   - Removed: Local constant definitions
   - Added: Imports from `config` package

3. **`_modules/data/__init__.py`**
   - Added: Import constants from `config` package
   - Modified: Re-export constants for backward compatibility

## Benefits

### 1. **Centralized Configuration**
- All constants in one location
- Easier to find and modify settings
- Clear separation between config and implementation

### 2. **Better Organization**
- Widget settings grouped together
- Application constants separated from data modules
- Clear module responsibilities

### 3. **Improved Maintainability**
- Single source of truth for constants
- Documentation in dedicated README
- Easier to add new configuration

### 4. **Backward Compatibility**
- Existing imports still work via re-exports
- No breaking changes to public API
- Gradual migration path available

## Usage

### Before
```python
# Constants scattered across files
from _modules.ui.billdozer_widget import BILLDOZER_TOKEN
from _modules.data.fictional_entities import DEFAULT_INSURANCE_COUNT
```

### After
```python
# All constants from one place
from config import (
    BILLDOZER_TOKEN,
    DEFAULT_INSURANCE_COUNT,
    ENTITY_TYPE_INSURANCE,
)
```

## Testing

- ✅ All 134 tests pass
- ✅ Bandit security scan passes (0 issues)
- ✅ Import tests successful
- ✅ Backward compatibility verified

## Security Notes

All `# nosec` comments have been properly migrated:
- `BILLDOZER_TOKEN` - Correctly marked as version identifier, not password
- Placed on same line as assignment for proper detection

## Future Enhancements

### Potential Additions
1. **`config/api_config.py`** - API endpoints and settings
2. **`config/ui_config.py`** - More UI constants
3. **`config/security_config.py`** - Security-related settings
4. **`config/limits.py`** - Rate limits and thresholds

### Migration Candidates
Consider moving these to `config/` in future:
- Image CDN URLs and paths
- Default timeouts and retries
- Cache settings
- Feature flag defaults (if not in YAML)

## Documentation

- Configuration package documented in `config/README.md`
- Usage examples provided
- Migration guide included

## Related Files

- **Configuration Guide**: `docs/CONFIG_README.md` (for YAML config)
- **Module Reference**: `docs/MODULES.md` (for code modules)
- **Environment Variables**: `docs/ENVIRONMENT_VARIABLES.md` (for env vars)

## Notes

This migration maintains clear separation:
- **`config/` package**: Hardcoded constants, version identifiers, system defaults
- **`app_config.yaml`**: User-configurable settings, feature flags, preferences
- **Environment Variables**: Secrets, API keys, deployment-specific settings

---

**Migration completed successfully with zero breaking changes.** ✅
