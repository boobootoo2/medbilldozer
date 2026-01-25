# CI/CD Setup Guide for GitHub Actions

## Overview

This repository is configured to automatically run tests on every push and pull request using GitHub Actions. No API keys or secrets are required!

## What's Been Set Up

### 1. GitHub Actions Workflow (`.github/workflows/tests.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests targeting `main` or `develop`
- Manual runs from GitHub Actions UI

**Test Matrix:**
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

All versions must pass independently.

### 2. Test Dependencies (`requirements-test.txt`)

Minimal dependencies for running tests:
- `pytest==8.3.4`
- `pytest-mock==3.14.0`
- `PyYAML>=6.0`

This keeps CI fast and avoids installing heavy dependencies like Streamlit, OpenAI SDK, etc.

### 3. Test Suite

**60 tests** across 2 modules:
- `test_config.py` - 29 tests (Configuration system)
- `test_doc_assistant.py` - 31 tests (Documentation Assistant)

All tests are:
- ✅ Fully mocked (no real API calls)
- ✅ No secrets needed
- ✅ Fast (<2 seconds)
- ✅ Deterministic (same results every time)

## How to Use

### View Test Results in GitHub

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Select the latest workflow run
4. View results for all Python versions

### Add Status Badge to README

Add this to the top of your `README.md`:

```markdown
![Tests](https://github.com/boobootoo2/medbilldozer/actions/workflows/python-app.yml/badge.svg)
```

This shows a badge indicating whether tests are passing or failing.

### Run Tests Locally (Same as CI)

```bash
# Install minimal test dependencies
pip install -r requirements-test.txt

# Run all tests
python3 -m pytest tests/ -v

# Run with short traceback (like CI)
python3 -m pytest tests/ -v --tb=short
```

### Manually Trigger Workflow

1. Go to **Actions** tab
2. Select "Run Tests" workflow
3. Click "Run workflow" button
4. Choose branch and click "Run workflow"

## What Happens on Each Push

```
1. Code pushed to GitHub
   ↓
2. GitHub Actions triggered
   ↓
3. Workflow starts (4 parallel jobs, one per Python version)
   ↓
4. For each Python version:
   - Checkout code
   - Setup Python environment
   - Install test dependencies (pip cache used for speed)
   - Run pytest with verbose output
   - Generate test summary
   ↓
5. Results shown in GitHub Actions UI
   ↓
6. Badge updates to show pass/fail status
```

## Troubleshooting

### Test Fails Locally but Passes in CI (or vice versa)

- Ensure you're using `requirements-test.txt` locally
- Check Python version matches one in CI matrix
- Look for environment-specific issues

### CI is Slow

- Workflow uses pip caching (should be fast after first run)
- Only minimal dependencies installed
- Tests run in ~1-2 seconds
- Matrix jobs run in parallel

### Need to Add More Tests

1. Add test file to `tests/` directory
2. Follow existing patterns (mock external APIs)
3. Run locally: `python3 -m pytest tests/test_yourfile.py -v`
4. Push to GitHub - CI will automatically pick up new tests

### Need Different Python Versions

Edit `.github/workflows/tests.yml`:

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']  # Remove versions as needed
```

## Best Practices

### ✅ DO

- Keep tests fast (<5 seconds total)
- Mock all external APIs
- Use `requirements-test.txt` for minimal dependencies
- Write descriptive test names
- Check CI results before merging PRs

### ❌ DON'T

- Add secrets/API keys to tests
- Make real API calls in tests
- Test UI rendering (Streamlit specific)
- Add heavy dependencies to `requirements-test.txt`
- Skip tests locally before pushing

## Files Added

```
.github/
  workflows/
    tests.yml              # GitHub Actions workflow definition
  README.md                # Workflow documentation

requirements-test.txt      # Minimal test dependencies
CI-CD-GUIDE.md            # This file
```

## Next Steps

1. **Push to GitHub** to trigger first workflow run
2. **Add status badge** to README.md
3. **Enable branch protection** (optional):
   - Go to Settings → Branches → Branch protection rules
   - Add rule for `main` branch
   - Enable "Require status checks to pass before merging"
   - Select "test" status check
4. **Review test results** in Actions tab

## Status

✅ Workflow configured
✅ Test dependencies minimal
✅ 60 tests ready to run
✅ Multi-version support (Python 3.10-3.13)
✅ No secrets required
✅ Ready to push!

---

**Need help?** Check `.github/README.md` for workflow-specific details or `TESTING.md` for test suite documentation.
