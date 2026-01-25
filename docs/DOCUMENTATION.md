# MedBillDozer Documentation System

## Overview

MedBillDozer uses an **automatic documentation generation system** that derives all documentation from code-owned facts, not hand-written text. This ensures documentation is always accurate and up-to-date.

## Philosophy

> **Documentation is derived from code-owned facts, not written by hand.**

### Benefits

- **Always Up-to-Date**: Documentation regenerates from source code automatically
- **Single Source of Truth**: Code is the authoritative source
- **No Documentation Drift**: Impossible for docs to become stale
- **Zero Maintenance**: No manual documentation updates required
- **Consistent Format**: Automated generation ensures uniform structure

## Quick Start

### Generate Documentation

```bash
# Generate all documentation
make docs

# Generate and view
make docs-view
```

### Install Pre-Commit Hook

The pre-commit hook automatically regenerates documentation on every commit:

```bash
# Install the hook
make install-hooks

# Now documentation updates automatically on every commit!
git commit -m "Your changes"
```

## Generated Documentation

The system generates the following files in `docs/`:

### 1. README.md
**Purpose**: Project overview and module categorization

**Contains**:
- Total module count
- Modules grouped by category (Providers, Extractors, UI, etc.)
- Quick summary of each module's purpose

### 2. MODULES.md
**Purpose**: Comprehensive module reference

**Contains**:
- Detailed documentation for each module
- Function signatures with parameters and return types
- Class definitions with methods and attributes
- Module docstrings
- Internal dependencies

### 3. API.md
**Purpose**: Public API reference

**Contains**:
- Provider interface specifications
- Key public classes and their contracts
- Usage patterns for external consumers

### 4. DEPENDENCIES.md
**Purpose**: Module dependency graph

**Contains**:
- Which modules depend on which others
- Internal dependency mapping
- Helps understand module coupling

### 5. manifest.json
**Purpose**: Machine-readable metadata

**Contains**:
- Module statistics (function count, class count, etc.)
- Dependency information
- Programmatic access to documentation data

## What Gets Documented

The documentation generator extracts these facts from the codebase:

### From Modules
- Module name and file path
- Module-level docstrings
- Import statements
- Internal dependencies (_modules.* imports)
- Module-level constants (uppercase variables)

### From Functions
- Function name and signature
- Parameter names and types (if annotated)
- Return type (if annotated)
- Docstrings
- Decorators (e.g., @property, @staticmethod)
- Async functions (async def)
- Line numbers in source file

### From Classes
- Class name and inheritance hierarchy
- Class docstrings
- Attributes (typed class variables)
- All methods with full signatures
- Method docstrings
- Line numbers in source file

## How It Works

### 1. AST Parsing

The generator uses Python's Abstract Syntax Tree (AST) parser to analyze source code:

```python
tree = ast.parse(source_code)
visitor.visit(tree)  # Extract facts
```

### 2. Metadata Extraction

Facts are extracted and stored in structured dataclasses:

```python
@dataclass
class ModuleInfo:
    filepath: str
    module_name: str
    docstring: Optional[str]
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    dependencies: Set[str]
```

### 3. Markdown Generation

Structured data is converted to human-readable Markdown:

```python
def generate_module_docs(module: ModuleInfo) -> str:
    lines = [f"## Module: `{module.module_name}`"]
    # Format classes, functions, dependencies...
    return "\n".join(lines)
```

### 4. JSON Manifest

Machine-readable metadata enables programmatic documentation access:

```json
{
  "total_modules": 25,
  "modules": [
    {
      "name": "_modules.providers.llm_interface",
      "num_classes": 3,
      "num_functions": 2
    }
  ]
}
```

## Pre-Commit Hook

The pre-commit hook ensures documentation is never out of sync:

### Installation

```bash
make install-hooks
```

### How It Works

1. You run `git commit`
2. Hook executes `make docs` automatically
3. If docs changed, they're staged with your commit
4. Commit proceeds with updated documentation
5. Documentation is always current!

### Bypass (Not Recommended)

If you absolutely must skip the hook:

```bash
git commit --no-verify
```

## Manual Generation

If you prefer not to use the hook, generate manually:

```bash
# Via Makefile
make docs

# Or directly
python3 scripts/generate_docs.py
```

## Extending the System

### Add New Documentation Sections

Edit `scripts/generate_docs.py` and add a new method:

```python
def generate_custom_section(self) -> str:
    """Generate custom documentation"""
    lines = ["## Custom Section", ""]
    # Your logic here
    return "\n".join(lines)
```

Then call it in `generate_all()`:

```python
def generate_all(self, output_dir):
    # ... existing code ...

    # Add your custom section
    custom = self.generate_custom_section()
    (output_dir / "CUSTOM.md").write_text(custom)
```

### Extract Additional Facts

Extend the `CodeAnalyzer` visitor to extract more information:

```python
def visit_YourNode(self, node):
    """Extract custom facts from AST"""
    # Your extraction logic
    self.custom_facts.append(extracted_data)
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Auto-Generate Documentation

on:
  push:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Generate Documentation
        run: python3 scripts/generate_docs.py

      - name: Commit Changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/
          git diff --staged --quiet || git commit -m "Auto-update documentation [skip ci]"
          git push
```

## Troubleshooting

### Hook Not Running

```bash
# Check if hook exists
ls -la .git/hooks/pre-commit

# Make it executable
chmod +x .git/hooks/pre-commit

# Reinstall
make install-hooks
```

### Documentation Not Updating

```bash
# Manually regenerate
make docs

# Check for errors
python3 scripts/generate_docs.py
```

### Module Not Documented

Ensure the module:
1. Is a `.py` file in `_modules/` or `app.py`
2. Has valid Python syntax
3. Is not `__init__.py` (these are skipped)

## Best Practices

### Writing Code for Documentation

1. **Add Docstrings**: Module, class, and function docstrings become documentation
   ```python
   def analyze_document(doc: str) -> Result:
       """Analyze a medical billing document for errors."""
       pass
   ```

2. **Use Type Hints**: They appear in generated documentation
   ```python
   def process(items: List[Item]) -> Dict[str, Any]:
       pass
   ```

3. **Document Constants**: Use uppercase for auto-extraction
   ```python
   MAX_RETRIES = 3  # Appears in docs
   ```

4. **Write Clear Class Docstrings**: They're shown prominently
   ```python
   class Provider(ABC):
       """Base class for all LLM providers."""
       pass
   ```

### Committing Changes

1. Write your code with good docstrings
2. Commit normally: `git commit -m "Add new feature"`
3. Hook auto-generates docs and includes them
4. Push with confidence that docs are current

## Architecture

```
scripts/generate_docs.py
├── CodeAnalyzer (AST visitor)
│   ├── visit_Module()
│   ├── visit_FunctionDef()
│   ├── visit_ClassDef()
│   └── analyze() → ModuleInfo
│
└── DocumentationGenerator
    ├── scan_codebase()
    ├── generate_overview() → README.md
    ├── generate_module_docs() → MODULES.md
    ├── generate_api_reference() → API.md
    ├── generate_dependency_graph() → DEPENDENCIES.md
    └── generate_all() → JSON manifest
```

## Summary

The automatic documentation system ensures MedBillDozer's documentation is:

✅ **Accurate** - Derived directly from source code
✅ **Current** - Regenerated on every commit
✅ **Comprehensive** - Covers all modules, classes, and functions
✅ **Zero-Effort** - No manual maintenance required
✅ **Consistent** - Uniform format across all docs

**Result**: Documentation that developers can trust and rely on.

