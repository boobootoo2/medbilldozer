# Documentation Scripts

## Automatic Documentation Generator

The `generate_docs.py` script automatically generates comprehensive documentation by analyzing the codebase itself. No manual documentation writing required!

### Features

- **AST-based Analysis**: Parses Python source code using Abstract Syntax Trees to extract facts
- **Comprehensive Coverage**: Documents modules, classes, functions, dependencies, and APIs
- **Multiple Output Formats**: Generates Markdown docs and JSON manifest
- **Dependency Tracking**: Maps internal dependencies between modules
- **Zero Configuration**: Works out of the box, no setup needed

### Usage

```bash
# Generate all documentation
python3 scripts/generate_docs.py

# Or use the convenience commands
make docs          # Generate documentation
make docs-view     # Generate and view in browser
```

### Generated Documentation

The script creates the following files in the `docs/` directory:

1. **README.md** - Project overview and module categorization
2. **MODULES.md** - Detailed documentation for each module
3. **API.md** - Public API reference for key interfaces
4. **DEPENDENCIES.md** - Module dependency graph
5. **manifest.json** - Machine-readable metadata for programmatic access

### What Gets Documented

The generator extracts these facts from the code:

- Module docstrings and descriptions
- Function signatures (name, parameters, return types)
- Class definitions (inheritance, attributes, methods)
- Decorators and async functions
- Module-level constants
- Internal dependencies (_modules imports)
- File locations and line numbers

### Philosophy

**Documentation is derived from code-owned facts, not written by hand.**

This ensures:
- Documentation stays in sync with code
- No documentation drift or staleness
- Single source of truth (the code)
- Automated updates on every change
- Consistent format and structure

### Extending the Generator

To add new documentation sections, extend the `DocumentationGenerator` class:

```python
def generate_custom_section(self) -> str:
    """Add your custom documentation logic"""
    lines = ["## Custom Section", ""]
    # Your logic here
    return "\n".join(lines)
```

Then call it in the `generate_all()` method.

### Integration with CI/CD

Add to your CI pipeline to auto-generate docs on every commit:

```yaml
# .github/workflows/docs.yml
- name: Generate Documentation
  run: python3 scripts/generate_docs.py
  
- name: Commit Updated Docs
  run: |
    git add docs/
    git commit -m "Auto-update documentation [skip ci]" || true
```
