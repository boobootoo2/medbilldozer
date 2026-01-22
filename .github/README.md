[![Tests](https://github.com/boobootoo2/medbilldozer/actions/workflows/python-app.yml/badge.svg)](
https://github.com/boobootoo2/medbilldozer/actions/workflows/python-app.yml
)

# medBillDozer

**medBillDozer** is an AI-powered application that helps individuals identify potential errors, overcharges, and reconciliation issues in medical bills, insurance claims, and explanations of benefits (EOBs).

Users can paste the text of a medical bill, receipt, or claim history, and medBillDozer analyzes the document to surface:
- Potential billing inconsistencies
- Duplicate or mismatched charges
- Coverage gaps between bills, claims, and EOBs
- Estimated maximum potential savings when issues are resolved

The application is designed to be:
- **Human-centered**: Clear explanations and evidence for every issue
- **Privacy-aware**: No data is stored beyond the current session
- **Explainable**: Findings are backed by extracted facts from the document
- **Extensible**: Supports multiple extraction and analysis providers

medBillDozer is built with Streamlit and uses a hybrid approach combining deterministic rules with large language models for document understanding.

# GitHub Actions Workflows

## python-app.yml - Automated Testing

This workflow runs the test suite automatically on:
- Every push to `main` or `develop` branches
- Every pull request targeting `main` or `develop`
- Manual trigger via GitHub Actions UI

### What it does

1. **Multi-version testing**: Tests run on Python 3.10, 3.11, 3.12, and 3.13
2. **Fast setup**: Uses pip caching for faster dependency installation
3. **Minimal dependencies**: Only installs test dependencies (pytest, pytest-mock, PyYAML)
4. **No secrets needed**: Tests are designed to run without API keys
5. **Clear output**: Verbose test output with summary

### Test Results

Tests run in parallel across all Python versions. Each must pass independently.

Current test coverage:
- `test_config.py`: 29 tests
- `test_doc_assistant.py`: 31 tests
- **Total**: 60 tests

### Viewing Results

1. Go to the **Actions** tab in GitHub
2. Select a workflow run to see results
3. Check the **Test Summary** for quick overview
4. Expand test steps for detailed output

### Local Testing

To run the same tests locally:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
python3 -m pytest tests/ -v
```
