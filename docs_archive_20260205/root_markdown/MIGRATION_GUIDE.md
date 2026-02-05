# Migration Guide: _modules/ → src/medbilldozer/

## Overview

This guide documents the incremental migration from `_modules/` to the Python best-practices `src/medbilldozer/` layout.

## Migration Strategy: Incremental with Backward Compatibility

**Phase 1: Structure Creation** ✅ CURRENT PHASE
- Create `src/medbilldozer/` directory structure
- Add package `__init__.py` files
- Set up backward compatibility shims
- No breaking changes yet

**Phase 2: Module-by-Module Migration** (NEXT)
- Migrate one submodule at a time
- Update internal imports within migrated modules
- Add re-exports in old location for compatibility
- Validate tests pass after each migration

**Phase 3: Consumer Updates**
- Update scripts/ to use new imports
- Update pages/ to use new imports
- Update tests/ to use new imports
- Update documentation

**Phase 4: Cleanup**
- Deprecation warnings for old imports
- Remove _modules/ after full migration
- Update CI/CD workflows

## Current Status

### ✅ Completed
- Created `src/medbilldozer/` directory structure
- Added root package `__init__.py` files
- Documented migration strategy

### 🔄 In Progress
- Phase 1: Structure creation

### ⏳ Pending
- Module file copies/moves
- Import updates
- Test validation
- Consumer updates

## Directory Mapping

```
OLD LOCATION              →  NEW LOCATION
_modules/                 →  src/medbilldozer/
_modules/core/            →  src/medbilldozer/core/
_modules/providers/       →  src/medbilldozer/providers/
_modules/ui/              →  src/medbilldozer/ui/
_modules/data/            →  src/medbilldozer/data/
_modules/extractors/      →  src/medbilldozer/extractors/
_modules/ingest/          →  src/medbilldozer/ingest/
_modules/prompts/         →  src/medbilldozer/prompts/
_modules/utils/           →  src/medbilldozer/utils/
```

## Import Changes

### Old Style (Deprecated)
```python
from _modules.core.auth import authenticate
from _modules.providers.gemini_analysis_provider import GeminiAnalysisProvider
from _modules.ui.ui import render_dashboard
```

### New Style (Preferred)
```python
from medbilldozer.core.auth import authenticate
from medbilldozer.providers.gemini_analysis_provider import GeminiAnalysisProvider
from medbilldozer.ui.ui import render_dashboard
```

## Installation Changes

### Current (Development)
No changes needed - package is not yet installed as a proper package.

### Future (After Migration)
```bash
# Install in editable mode for development
pip install -e .
```

This requires adding a `pyproject.toml` or `setup.py` file.

## Testing Strategy

### After Each Module Migration
1. Run full test suite: `pytest tests/`
2. Verify benchmark scripts work: `python3 scripts/generate_patient_benchmarks.py --model medgemma --subset high_signal`
3. Test dashboard launches: `streamlit run app.py`
4. Check imports in Python REPL:
   ```python
   # Both should work during transition
   from _modules.core import auth  # Old
   from medbilldozer.core import auth  # New
   ```

### Validation Checklist
- [ ] All 134 tests pass
- [ ] Benchmark generation works
- [ ] Dashboard renders correctly
- [ ] No import errors in any module
- [ ] Both old and new imports work (during transition)

## Module Migration Order (Recommended)

1. **utils/** - Few dependencies, used by others
2. **data/** - Data access layer, isolated
3. **prompts/** - Prompt templates, no complex dependencies
4. **extractors/** - Text extraction utilities
5. **ingest/** - Document ingestion
6. **core/** - Core business logic
7. **providers/** - LLM provider implementations
8. **ui/** - User interface components (most dependencies)

## Backward Compatibility Approach

During migration, maintain compatibility using re-exports in `_modules/__init__.py`:

```python
# _modules/core/__init__.py
# Backward compatibility shim
import sys
from medbilldozer.core import *

# Deprecation warning (optional, add in Phase 3)
# import warnings
# warnings.warn("_modules.core is deprecated, use medbilldozer.core", DeprecationWarning)
```

This allows old code to continue working while new code uses the modern import style.

## Configuration Updates Needed

### pyproject.toml (To Be Created)
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "medbilldozer"
version = "0.2.0"
description = "Medical Bill Analysis and Error Detection"
requires-python = ">=3.11"
dependencies = [
    # Will be extracted from requirements.txt
]

[tool.setuptools.packages.find]
where = ["src"]
```

### GitHub Actions Updates
- Update `PYTHONPATH` if needed
- Verify test discovery still works
- Check import paths in workflow files

### Streamlit Configuration
- Verify page discovery works with new structure
- Test imports in all pages/*.py files
- Ensure `app.py` finds modules correctly

## Risk Mitigation

### Branch Strategy
```bash
# Current work in: develop branch
# Migration work: Create migration branch
git checkout -b refactor/incremental-src-layout

# After validation, merge back to develop
git checkout develop
git merge refactor/incremental-src-layout
```

### Rollback Plan
If issues arise:
1. Git history preserved - can revert commits
2. Old `_modules/` remains functional during transition
3. Can pause migration at any phase
4. No breaking changes until Phase 4

## Timeline Estimate

- **Phase 1**: 30 minutes ✅ COMPLETE
- **Phase 2**: 2-3 hours (migrate 8 submodules)
- **Phase 3**: 2-4 hours (update ~100+ consumer files)
- **Phase 4**: 1 hour (cleanup and deprecation)

**Total**: 6-8 hours with testing and validation

## Questions/Decisions Needed

1. **When to start Phase 2?** 
   - Recommendation: After current benchmark features stabilize
   
2. **Deprecation timeline?**
   - Recommendation: Keep `_modules/` for 1-2 months after Phase 3

3. **Version bump?**
   - Current: 0.1.x
   - After migration: 0.2.0 (minor version bump)

## References

- [Python Packaging Guide](https://packaging.python.org/en/latest/)
- [src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [Structuring Python Applications](https://docs.python-guide.org/writing/structure/)

## Contact

For questions about this migration, consult the team or check commit history.
