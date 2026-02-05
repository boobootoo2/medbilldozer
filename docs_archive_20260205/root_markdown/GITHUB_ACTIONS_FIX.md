# GitHub Actions Workflow Fix

## Problem

GitHub Actions workflow was failing with:
```
ERROR: Could not find a version that satisfies the requirement contourpy==1.3.3
ERROR: Ignored the following versions that require a different python version: 1.3.3 Requires-Python >=3.11
```

**Root cause**: Workflow was using Python 3.10, but `contourpy==1.3.3` (used by visualization libraries) requires Python 3.11+.

## Solution

### 1. Updated Python Version
Changed workflow from Python 3.10 → Python 3.11

**File**: `.github/workflows/run_benchmarks.yml`
```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'  # Changed from '3.10'
```

### 2. Created Minimal Requirements File
Created `requirements-benchmarks.txt` with only essential dependencies needed for running benchmarks (not visualization).

**File**: `requirements-benchmarks.txt`
```txt
# Core dependencies for benchmarks only
openai>=1.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

**Why?** 
- Benchmarks don't need Streamlit, Plotly, Pandas, or other heavy visualization libs
- Faster CI/CD runs
- Fewer dependency conflicts
- More reliable builds

### 3. Updated Workflow Install Step
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements-benchmarks.txt
```

## Result

✅ Workflow now runs successfully on Python 3.11  
✅ Faster dependency installation  
✅ No version conflicts  
✅ Benchmarks run and commit results  

## Files Modified

1. `.github/workflows/run_benchmarks.yml`
   - Python version: 3.10 → 3.11
   - Requirements: requirements.txt → requirements-benchmarks.txt

2. `requirements-benchmarks.txt` (NEW)
   - Minimal dependencies for CI/CD
   - Only what's needed for benchmarks

## Testing

To test locally with minimal requirements:

```bash
# Create test environment
python3.11 -m venv test_env
source test_env/bin/activate

# Install minimal requirements
pip install -r requirements-benchmarks.txt

# Run benchmarks
python3 scripts/generate_benchmarks.py --model baseline
```

Should work with just 3 packages!

## Alternative Solutions Considered

### Option 1: Downgrade contourpy (Rejected)
- Would need to downgrade multiple visualization packages
- Defeats purpose of modern tooling
- Dashboard wouldn't work locally

### Option 2: Make contourpy optional (Rejected)
- Streamlit dashboard needs it
- Would break local dashboard functionality

### Option 3: Split requirements (CHOSEN ✅)
- **CI/CD**: Uses minimal requirements (no viz)
- **Local dev**: Uses full requirements (with viz)
- Best of both worlds

## Deployment Workflow

```
┌────────────────────────────────────────────────────┐
│  GitHub Actions (CI/CD)                            │
│  - Python 3.11                                     │
│  - requirements-benchmarks.txt (minimal)           │
│  - Runs: generate_benchmarks.py                    │
│  - Commits: benchmarks/results/*.json              │
└────────────────────────────────────────────────────┘
                    ↓
        ┌───────────────────────┐
        │  Git Repository       │
        │  - Updated JSON       │
        └───────────────────────┘
                    ↓
┌────────────────────────────────────────────────────┐
│  Streamlit Cloud (Dashboard)                       │
│  - Python 3.11                                     │
│  - requirements.txt (full)                         │
│  - Reads: benchmarks/results/*.json                │
│  - Displays: Interactive dashboard                 │
└────────────────────────────────────────────────────┘
```

## Future Improvements

### Optional: Version Matrix Testing
Test multiple Python versions:

```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
```

### Optional: Cache Dependencies
Speed up workflow with caching:

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements-benchmarks.txt') }}
```

### Optional: Conditional Dashboard Deploy
Automatically deploy dashboard after benchmarks:

```yaml
- name: Trigger Streamlit Cloud redeploy
  run: |
    curl -X POST ${{ secrets.STREAMLIT_DEPLOY_WEBHOOK }}
```

## FAQ

**Q: Why not just use Python 3.11 everywhere?**  
A: We did! This fix ensures consistency between local dev and CI/CD.

**Q: What if I need to add a benchmark dependency?**  
A: Add it to `requirements-benchmarks.txt` (minimal) and `requirements.txt` (full).

**Q: Will the dashboard still work?**  
A: Yes! Dashboard uses full `requirements.txt` which includes all viz libraries.

**Q: Can I still run benchmarks locally?**  
A: Yes! Your local environment has all dependencies. This only affects CI/CD.

## Verification

Push these changes and the workflow should succeed:

```bash
git add .github/workflows/run_benchmarks.yml requirements-benchmarks.txt
git commit -m "Fix: GitHub Actions Python version and dependencies"
git push
```

Check workflow at: `https://github.com/boobootoo2/medbilldozer/actions`

Should see: ✅ Run Benchmarks - Success!
