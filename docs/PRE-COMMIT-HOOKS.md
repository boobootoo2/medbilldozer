# Pre-Commit Hooks

This repository uses Git pre-commit hooks to ensure code quality and maintain consistency.

## What Gets Checked

Before each commit, the following checks are automatically run:

### 1. 🔍 Linting (flake8)
- Checks Python code style and quality
- Only runs on Python files being committed
- Configuration: `.flake8`
- **Commit will be blocked if linting fails**

### 2. 🧪 Unit Tests
- Runs the full test suite in `tests/`
- Ensures all tests pass before commit
- **Commit will be blocked if any tests fail**

### 3. 📚 Documentation Generation
- Automatically generates/updates documentation
- Adds updated docs to the commit
- Never blocks commits

## Installation

The pre-commit hook is installed by default. To reinstall:

```bash
make install-hooks
```

Or manually:

```bash
bash scripts/install-hooks.sh
```

## Bypassing the Hook

⚠️ **Not recommended**, but if you need to commit without running checks:

```bash
git commit --no-verify -m "Your message"
```

## What to Do When Checks Fail

### Linting Failures

```bash
# Check a specific file
flake8 path/to/file.py

# Check all Python files
flake8 .

# See linting config
cat .flake8
```

Common linting issues:
- Line too long (max 120 characters)
- Unused imports
- Undefined variables
- Indentation issues

### Test Failures

```bash
# Run tests with verbose output
make test

# Or directly with pytest
pytest tests/ -v

# Run a specific test file
pytest tests/test_app.py -v

# Run a specific test
pytest tests/test_app.py::TestClass::test_method -v
```

## Requirements

The pre-commit hook requires:
- `python3` in PATH
- `pytest` installed (for testing)
- `flake8` installed (for linting, auto-installed if missing)
- `make` (for documentation generation)

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

## Hook Location

The actual hook file is located at:
```
.git/hooks/pre-commit
```

This file is not tracked in the repository. To update it, modify the template in `scripts/install-hooks.sh`.

## Disabling Hooks Temporarily

If you need to disable hooks for your local repository:

```bash
# Rename the hook
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled

# To re-enable
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
```

## CI/CD Integration

The same checks run in CI/CD:
- GitHub Actions runs linting and tests on all pull requests
- Ensures code quality across all contributions
- See `.github/workflows/` for CI configuration
