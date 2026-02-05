# Migration Quick Start Guide

## TL;DR - What Just Happened

✅ **Phase 1 Complete**: New `src/medbilldozer/` structure created  
⏳ **Phase 2 Ready**: Tools available to migrate modules incrementally  
🔒 **Zero Risk**: All existing code (`_modules/`) unchanged and working

## Current State

```
├── _modules/              ← OLD (still working, unchanged)
│   ├── core/
│   ├── providers/
│   ├── ui/
│   └── ... (8 modules)
│
└── src/                   ← NEW (empty structure, ready for migration)
    └── medbilldozer/
        ├── core/
        ├── providers/
        ├── ui/
        └── ... (8 modules)
```

**Nothing is broken.** Everything works exactly as before.

## Quick Commands

### Verify Phase 1
```bash
# Check structure created
tree src/ -L 3

# Validate package config
python3 -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"
```

### Install Package (Optional)
```bash
# Install in editable/development mode
pip install -e .

# Now you can import (once modules are migrated)
python3 -c "import medbilldozer; print(medbilldozer.__version__)"
```

### Phase 2: Migrate Your First Module

#### 1. Preview what will happen (safe)
```bash
python3 scripts/migrate_module.py --module utils --dry-run
```

#### 2. Execute migration
```bash
python3 scripts/migrate_module.py --module utils --execute
```

#### 3. Create backward compatibility shim
```bash
python3 scripts/migrate_module.py --module utils --create-shim --execute
```

#### 4. Test everything works
```bash
# Test new imports
python3 -c "from medbilldozer.utils import *"

# Test old imports still work (via shim)
python3 -c "from _modules.utils import *"

# Run tests
pytest tests/ -v

# Run benchmarks
python3 scripts/generate_patient_benchmarks.py --model medgemma --subset high_signal
```

## Migration Order (Recommended)

Migrate one at a time, test after each:

1. ✅ **utils** - Lowest risk, few dependencies
2. ✅ **data** - Database layer, isolated
3. ✅ **prompts** - Templates, simple
4. ✅ **extractors** - Text extraction
5. ✅ **ingest** - Document ingestion
6. ✅ **core** - Business logic
7. ✅ **providers** - LLM implementations
8. ✅ **ui** - Most complex, do last

## When to Start Phase 2?

### ✅ Good Time
- Recent features stable
- Tests all passing
- No urgent bugs
- Team has testing capacity

### ⚠️ Wait
- Active development sprint
- Upcoming release/demo
- Failing tests
- Limited bandwidth

**Current Recommendation**: Wait for parent category aggregation and triggered-by features to stabilize (~1-2 weeks), then start with `utils` module.

## What If Something Breaks?

### Rollback Phase 1 (Structure Only)
```bash
rm -rf src/
git checkout pyproject.toml *.md
```

### Rollback Phase 2 (After Module Migration)
```bash
# Remove migrated module
rm -rf src/medbilldozer/<module>/

# Restore shim if modified
git checkout _modules/<module>/__init__.py
```

Everything keeps working because `_modules/` is preserved.

## Key Files

- **MIGRATION_GUIDE.md** - Full documentation (read this for details)
- **PHASE1_MIGRATION_COMPLETE.md** - Phase 1 status and next steps
- **scripts/migrate_module.py** - Automated migration helper
- **pyproject.toml** - Package configuration

## FAQs

**Q: Do I need to change any code right now?**  
A: No. This is Phase 1 (structure only). Code migration is Phase 2.

**Q: Will existing code break?**  
A: No. Old `_modules/` imports continue working.

**Q: When should I update my imports?**  
A: After Phase 2 (module migration) completes and backward compatibility shims are in place. Can be gradual.

**Q: What if I need to add new code now?**  
A: Add to `_modules/` as usual. Migrate it later in Phase 2.

**Q: Can I pause the migration?**  
A: Yes! After any module. Backward compatibility means no pressure.

**Q: How long will this take?**  
A: Phase 2: 4-6 hours total, but can be done incrementally over days/weeks.

## Next Action

**Option A**: Wait for stability (recommended)
- Continue with current work
- Let recent features stabilize
- Revisit migration in 1-2 weeks

**Option B**: Start Phase 2 now (if time permits)
```bash
# Start with utils (lowest risk)
python3 scripts/migrate_module.py --module utils --dry-run
python3 scripts/migrate_module.py --module utils --execute
python3 scripts/migrate_module.py --module utils --create-shim --execute
pytest tests/
```

---

*For detailed information, see: **MIGRATION_GUIDE.md***
