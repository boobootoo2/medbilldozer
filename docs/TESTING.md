# Testing Guide

## Overview

This project uses **pytest** for Python tests and **pre-commit hooks** to ensure code quality and prevent common issues like CORS misconfigurations.

---

## Test Categories

Tests are organized by markers:

- **`unit`**: Fast, isolated tests with no external dependencies
- **`integration`**: Tests that interact with external services (GCS, databases, APIs)
- **`slow`**: Tests that take more than 1 second

---

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Only unit tests (fast)
pytest -m unit

# Only integration tests (requires GCS credentials)
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Run CORS Configuration Tests

```bash
# Fast unit tests (validates config file only)
pytest tests/test_cors_config.py::TestCORSConfigFile -v

# Integration tests (checks actual GCS bucket)
pytest tests/test_cors_config.py::TestGCSBucketCORS -v -m integration
```

### Run Specific Test File

```bash
pytest tests/test_cors_config.py -v
```

---

## CORS Configuration Tests

### Why These Tests Exist

The CORS tests prevent file upload failures by ensuring:
- ✅ CORS config file exists and is valid JSON
- ✅ Localhost origins are allowed (for development)
- ✅ PUT method is allowed (required for uploads)
- ✅ Production origins are configured
- ✅ GCS bucket matches the config file (integration test)

### Test Structure

```
tests/test_cors_config.py
├── TestCORSConfigFile (unit tests - fast)
│   ├── Validates config/gcs-cors.json
│   ├── Checks required fields and methods
│   └── Ensures development/production origins
└── TestGCSBucketCORS (integration tests - requires GCS auth)
    ├── Verifies actual GCS bucket has CORS
    ├── Checks bucket allows PUT requests
    └── Ensures bucket matches config file
```

### What Each Test Validates

| Test | Purpose | Failure Impact |
|------|---------|----------------|
| `test_cors_config_file_exists` | Config file is present | Setup incomplete |
| `test_cors_allows_localhost_development` | Dev origins configured | Local uploads fail |
| `test_cors_allows_put_method` | PUT method allowed | All uploads fail |
| `test_cors_allows_required_headers` | Headers configured | Upload failures |
| `test_cors_includes_production_origin` | Production ready | Production uploads fail |
| `test_gcs_bucket_has_cors_configured` | GCS bucket configured | All uploads fail |
| `test_gcs_cors_matches_config_file` | Config is synced | Inconsistent behavior |

---

## Pre-Commit Hooks

Pre-commit hooks run automatically before each commit to catch issues early.

### Setup Pre-Commit Hooks

```bash
# One-time setup
./scripts/setup_pre_commit.sh
```

This installs:
- ✅ Code formatters (black, isort)
- ✅ Linters (flake8)
- ✅ Security checks (bandit)
- ✅ CORS validation (custom)
- ✅ JSON/YAML validators
- ✅ Large file detection

### What Runs on Each Commit

1. **File Quality**
   - Removes trailing whitespace
   - Ensures files end with newline
   - Checks for merge conflicts
   - Detects private keys

2. **Python Code**
   - Formats with black (line length 100)
   - Sorts imports with isort
   - Lints with flake8
   - Scans for security issues with bandit

3. **CORS Configuration** ⭐
   - Validates CORS config file exists
   - Checks PUT method is allowed
   - Runs on every commit (fast smoke test)
   - Full validation when `config/gcs-cors.json` changes

4. **Frontend Code**
   - Lints TypeScript/React with ESLint
   - Auto-fixes issues when possible

### Running Hooks Manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run validate-cors-config

# Run CORS smoke test
pre-commit run cors-config-smoke-test
```

### Skipping Hooks (Not Recommended)

```bash
# Skip all hooks for a commit (use sparingly!)
git commit --no-verify
```

### Updating Hooks

```bash
# Update to latest versions
pre-commit autoupdate

# Re-run after updating
pre-commit run --all-files
```

---

## Writing New Tests

### Test Naming Convention

```python
# File: tests/test_<feature>.py
# Class: Test<Feature>
# Method: test_<what_it_tests>

class TestUploadService:
    def test_upload_generates_signed_url(self):
        """Test should describe what it validates."""
        pass
```

### Using Markers

```python
import pytest

@pytest.mark.unit
def test_fast_function():
    """Unit test - no external dependencies."""
    pass

@pytest.mark.integration
def test_gcs_upload():
    """Integration test - requires GCS credentials."""
    pass

@pytest.mark.slow
def test_large_file_processing():
    """Slow test - takes >1 second."""
    pass
```

### Using Fixtures

```python
@pytest.fixture
def sample_config():
    """Reusable test data."""
    return {"key": "value"}

def test_with_fixture(sample_config):
    assert sample_config["key"] == "value"
```

---

## Test Coverage

### Generate Coverage Report

```bash
# Install coverage
pip install pytest-cov

# Run with coverage
pytest --cov=backend --cov-report=html

# View report
open htmlcov/index.html
```

### Coverage Goals

- **Critical paths**: 90%+ coverage
  - Authentication
  - File uploads
  - Payment processing
- **Business logic**: 80%+ coverage
- **UI components**: 70%+ coverage

---

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- Pull requests
- Pushes to `main` and release branches
- Pre-commit hooks run via pre-commit.ci

### Running Locally Before Push

```bash
# Recommended workflow
pre-commit run --all-files  # Check code quality
pytest -m "not integration"  # Run fast tests
pytest -m integration        # Run integration tests (if you have GCS auth)
```

---

## Troubleshooting Tests

### CORS Tests Fail

**Problem**: `test_cors_config_file_exists` fails

**Solution**:
```bash
# Create CORS config
./scripts/setup_gcs_cors.sh
```

**Problem**: `test_gcs_bucket_has_cors_configured` fails

**Solution**:
```bash
# Apply CORS to GCS bucket
gcloud storage buckets update gs://medbilldozer-documents \
    --cors-file=config/gcs-cors.json
```

### Pre-Commit Hook Fails

**Problem**: Hook exits with error

**Solution**:
```bash
# Update hooks
pre-commit autoupdate

# Clear cache and retry
pre-commit clean
pre-commit run --all-files
```

**Problem**: Black/isort conflicts

**Solution**: Both are configured with compatible settings. Run:
```bash
black backend/ tests/
isort backend/ tests/
```

### Import Errors in Tests

**Problem**: Cannot import backend modules

**Solution**:
```bash
# Install backend in development mode
cd backend
pip install -e .
```

---

## Best Practices

### ✅ Do

- Write tests for new features before implementation (TDD)
- Use descriptive test names that explain what's tested
- Keep unit tests fast (<100ms each)
- Mock external dependencies in unit tests
- Run pre-commit hooks before pushing

### ❌ Don't

- Skip tests with `@pytest.mark.skip` without a good reason
- Commit failing tests
- Use `--no-verify` regularly (bypasses safety checks)
- Test implementation details (test behavior, not internals)
- Make tests dependent on external state

---

## Quick Reference

```bash
# Setup
./scripts/setup_pre_commit.sh        # One-time setup

# Testing
pytest                                # Run all tests
pytest -v                             # Verbose output
pytest tests/test_cors_config.py     # Specific file
pytest -m unit                        # Only unit tests
pytest -k "upload"                    # Tests matching name

# Pre-commit
pre-commit run --all-files           # Run all hooks
pre-commit run cors-config-smoke-test # CORS check
git commit --no-verify               # Skip hooks (emergency only)

# Coverage
pytest --cov=backend --cov-report=html
```

---

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pre-commit documentation](https://pre-commit.com/)
- [CORS Troubleshooting](TROUBLESHOOTING.md#-cors-errors-with-file-uploads)
