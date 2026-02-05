# GitHub Actions CI/CD

Automated testing, linting, and deployment workflows.

## Overview

medBillDozer uses GitHub Actions for:
- ✅ **Automated Testing**: Run pytest on every push
- 🔍 **Linting**: Check code quality with flake8, black
- 🔒 **Security Scanning**: Detect vulnerabilities with bandit
- 📊 **Benchmark Validation**: Verify benchmark results
- 🚀 **Deployment**: (Optional) Auto-deploy to Streamlit Cloud

## Workflows

```
.github/
└── workflows/
    ├── test.yml              # Main test suite
    ├── lint.yml              # Code quality checks
    ├── security.yml          # Security scanning
    ├── benchmarks.yml        # Benchmark validation
    └── deploy.yml            # Deployment (optional)
```

## test.yml - Main Test Suite

Run tests on every push and pull request.

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
          pip install -r requirements-test.txt
      
      - name: Run tests
        run: |
          pytest --cov=src/medbilldozer \
                 --cov-report=xml \
                 --cov-report=term \
                 --junitxml=junit.xml
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
      
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-${{ matrix.python-version }}
          path: junit.xml
```

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main`

**Matrix**: Tests against Python 3.11, 3.12, 3.13

**Artifacts**: Coverage reports, test results

## lint.yml - Code Quality

Enforce code style and quality standards.

```yaml
# .github/workflows/lint.yml
name: Lint

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install linters
        run: |
          pip install flake8 black isort mypy
      
      - name: Run flake8
        run: |
          flake8 src/ tests/ --max-line-length=100 \
                            --exclude=__pycache__,*.pyc \
                            --count --statistics
      
      - name: Check black formatting
        run: |
          black --check src/ tests/
      
      - name: Check import sorting
        run: |
          isort --check-only src/ tests/
      
      - name: Run mypy type checking
        run: |
          mypy src/ --ignore-missing-imports
        continue-on-error: true  # Type checking is advisory
```

**Checks**:
- **flake8**: PEP 8 compliance, code complexity
- **black**: Code formatting
- **isort**: Import statement ordering
- **mypy**: Type annotations (advisory)

**Fix locally**:
```bash
# Auto-format code
black src/ tests/
isort src/ tests/

# Check before commit
flake8 src/ tests/
mypy src/
```

## security.yml - Security Scanning

Detect security vulnerabilities.

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  security:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install dependencies
        run: |
          pip install bandit safety
      
      - name: Run bandit security scan
        run: |
          bandit -r src/ -f json -o bandit-report.json
          bandit -r src/ -f screen
        continue-on-error: true
      
      - name: Check dependencies for vulnerabilities
        run: |
          safety check --json > safety-report.json
          safety check
        continue-on-error: true
      
      - name: Upload security reports
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
```

**Scans**:
- **bandit**: Python code security issues
- **safety**: Known vulnerabilities in dependencies

**Schedule**: Weekly scans + on push to main

## benchmarks.yml - Benchmark Validation

Validate benchmark test cases.

```yaml
# .github/workflows/benchmarks.yml
name: Benchmark Validation

on:
  push:
    paths:
      - 'benchmarks/**'
      - 'src/medbilldozer/core/benchmark.py'
  pull_request:
    paths:
      - 'benchmarks/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install -r requirements-benchmarks.txt
      
      - name: Validate benchmark schemas
        run: |
          python scripts/annotate_benchmarks.py --validate
      
      - name: Check benchmark count
        run: |
          EXPECTED=50
          ACTUAL=$(ls benchmarks/inputs/*.txt | wc -l)
          echo "Expected: $EXPECTED benchmarks"
          echo "Found: $ACTUAL benchmarks"
          if [ $ACTUAL -ne $EXPECTED ]; then
            echo "❌ Benchmark count mismatch"
            exit 1
          fi
          echo "✓ All benchmarks present"
      
      - name: Run heuristic baseline
        run: |
          python scripts/run_benchmarks.py --provider heuristic
        continue-on-error: true
```

**Triggers**: Changes to benchmark files or benchmark engine

**Validates**:
- Schema conformance
- Benchmark count
- Ground truth completeness

## deploy.yml - Streamlit Deployment

Optional: Auto-deploy to Streamlit Cloud.

```yaml
# .github/workflows/deploy.yml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]
  workflow_dispatch:  # Manual trigger

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Trigger Streamlit Cloud deployment
        run: |
          echo "Deployment triggered by push to main"
          echo "Streamlit Cloud will auto-deploy from GitHub"
      
      - name: Notify deployment
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.repos.createCommitStatus({
              owner: context.repo.owner,
              repo: context.repo.repo,
              sha: context.sha,
              state: 'success',
              target_url: 'https://medbilldozer.streamlit.app',
              description: 'Deployed to Streamlit Cloud',
              context: 'deployment'
            })
```

**Note**: Streamlit Cloud auto-deploys from GitHub when connected. This workflow is for notifications only.

## Secrets Configuration

Configure secrets in GitHub repo settings.

**Path**: Repository → Settings → Secrets and variables → Actions

### Required Secrets

For testing with real APIs (optional):

```
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIza...
```

**Add secret**:
```bash
# Via GitHub CLI
gh secret set OPENAI_API_KEY

# Or via UI: Settings → Secrets → New repository secret
```

### Using Secrets in Workflows

```yaml
- name: Run integration tests
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
  run: |
    pytest tests/integration/ --requires-api
```

## Status Badges

Add to README.md:

```markdown
# medBillDozer

[![Test Suite](https://github.com/yourusername/medbilldozer/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/medbilldozer/actions/workflows/test.yml)
[![Lint](https://github.com/yourusername/medbilldozer/actions/workflows/lint.yml/badge.svg)](https://github.com/yourusername/medbilldozer/actions/workflows/lint.yml)
[![Security](https://github.com/yourusername/medbilldozer/actions/workflows/security.yml/badge.svg)](https://github.com/yourusername/medbilldozer/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/yourusername/medbilldozer/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/medbilldozer)
```

## Local Testing

Test workflows locally with `act`:

```bash
# Install act
brew install act  # macOS
# or: https://github.com/nektos/act

# Run test workflow
act -j test

# Run specific job
act -j lint

# With secrets
act -j test -s OPENAI_API_KEY="sk-..."

# Dry run
act -n
```

## Troubleshooting

### Tests Fail in CI but Pass Locally

**Common causes**:
1. **Missing dependencies**: Update requirements.txt
2. **Environment differences**: Check Python version in matrix
3. **Path issues**: Use absolute imports
4. **Cached data**: Clear pytest cache

**Debug**:
```yaml
- name: Debug environment
  run: |
    python --version
    pip list
    pwd
    ls -la
```

### Workflow Not Triggering

**Check**:
1. Workflow file is in `.github/workflows/`
2. YAML syntax is valid (use yamllint)
3. Trigger conditions match (branch name, paths)
4. Workflow is enabled (Actions → Workflow → Enable)

**Test syntax**:
```bash
# Install yamllint
pip install yamllint

# Check workflow file
yamllint .github/workflows/test.yml
```

### Rate Limits

GitHub Actions has rate limits for API calls.

**Solution**:
```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

### Slow Workflows

**Optimize**:
1. **Cache dependencies**: Use actions/cache
2. **Skip unchanged**: Use path filters
3. **Parallel jobs**: Use matrix strategy
4. **Fail fast**: Set fail-fast: false for matrix

```yaml
strategy:
  fail-fast: false  # Continue other jobs if one fails
  matrix:
    python-version: ["3.11", "3.12", "3.13"]
```

## Best Practices

### 1. Run Tests Before Merge

```yaml
# Branch protection rules
Settings → Branches → Add rule
✓ Require status checks to pass
  ✓ test
  ✓ lint
```

### 2. Use Matrix Builds

```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12", "3.13"]
    os: [ubuntu-latest, macos-latest, windows-latest]
```

### 3. Cache Dependencies

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.11"
    cache: 'pip'  # Automatically cache pip packages
```

### 4. Fail Fast for Quick Feedback

```yaml
- name: Quick checks first
  run: |
    flake8 --select=E9,F63,F7,F82  # Syntax errors only
    
- name: Full lint (if quick checks pass)
  run: |
    flake8 src/ tests/
```

### 5. Separate Fast and Slow Tests

```yaml
jobs:
  fast-tests:
    steps:
      - run: pytest -m "not slow"
  
  slow-tests:
    needs: fast-tests
    steps:
      - run: pytest -m slow
```

## Advanced Workflows

### Conditional Deployment

Only deploy if tests pass:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest
  
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying..."
```

### Matrix with Exclusions

```yaml
strategy:
  matrix:
    python-version: ["3.11", "3.12", "3.13"]
    os: [ubuntu-latest, macos-latest]
    exclude:
      - python-version: "3.13"
        os: macos-latest  # Skip 3.13 on macOS
```

### Scheduled Benchmarks

Run benchmarks nightly:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily

jobs:
  benchmark:
    steps:
      - run: python scripts/run_benchmarks.py --all
```

## Next Steps

- [Streamlit Deployment](streamlit.md) - Deploy application
- [Testing Guide](../development/testing.md) - Write tests
- [Environment Variables](environment_variables.md) - Configuration
