# Root Directory Cleanup Plan

**Goal**: Organize root-level files into logical subdirectories without breaking functionality.

## Current Root Directory Issues

The root has **~20+ miscellaneous files** mixed with critical application files:

### Critical Files (KEEP IN ROOT)
- ✅ `app.py` - Main Streamlit application (referenced everywhere)
- ✅ `benchmark_dashboard.py` - Benchmark dashboard app
- ✅ `pyproject.toml` - Package configuration (required for pip install)
- ✅ `pytest.ini` - Test configuration (pytest looks here)
- ✅ `Makefile` - Build automation (conventional location)
- ✅ `LICENSE` - License file (GitHub/conventional)
- ✅ `README.md` - Main README (GitHub/conventional)
- ✅ `.gitignore`, `.flake8`, `.markdownlint.json` - Config files (tools expect root)

### Files to Move (14 files)

#### 1. Archive/Examples → `examples/`
- `profile_integration_example.py` - Example code
- `fix_linting.py` - One-time utility script

#### 2. Build Artifacts → `.artifacts/` (new directory)
- `bandit-report.json` - Security scan output
- `error_type_performance.csv` - Script output
- `COMMIT_MESSAGE.txt` - Migration artifact

#### 3. Legacy Documentation → `docs_archive_20260205/`
- `README_OLD.md` - Old README (already archived phase 2)

#### 4. Configuration Examples → `config/examples/`
- `app_config.example.yaml` - Keep `app_config.yaml` in root (runtime needs it)

#### 5. Requirements Files → Keep in root (pip expects them)
- ✅ `requirements.txt` - Standard location
- ✅ `requirements-test.txt` - Standard convention
- ✅ `requirements-benchmarks.txt` - Standard convention
- ✅ `requirements-monitoring.txt` - Standard convention

## Proposed New Structure

```
medbilldozer/
├── app.py                          ✅ KEEP (main app)
├── benchmark_dashboard.py          ✅ KEEP (dashboard app)
├── pyproject.toml                  ✅ KEEP (package config)
├── pytest.ini                      ✅ KEEP (test config)
├── Makefile                        ✅ KEEP (build tool)
├── LICENSE                         ✅ KEEP (license)
├── README.md                       ✅ KEEP (main docs)
├── app_config.yaml                 ✅ KEEP (runtime config)
├── requirements*.txt               ✅ KEEP (pip standard)
├── .gitignore, .flake8, etc.       ✅ KEEP (dotfiles)
│
├── .artifacts/                     ✨ NEW
│   ├── bandit-report.json
│   ├── error_type_performance.csv
│   └── COMMIT_MESSAGE.txt
│
├── examples/                       ✨ NEW
│   ├── profile_integration_example.py
│   └── README.md
│
├── config/
│   ├── __init__.py
│   ├── constants.py
│   └── examples/                   ✨ NEW
│       └── app_config.example.yaml
│
└── (existing directories unchanged)
```

## Migration Commands

### Step 1: Create New Directories

```bash
mkdir -p .artifacts
mkdir -p examples
mkdir -p config/examples
```

### Step 2: Move Build Artifacts

```bash
# Move artifacts (add to .gitignore)
git mv bandit-report.json .artifacts/
git mv error_type_performance.csv .artifacts/
git mv COMMIT_MESSAGE.txt .artifacts/

# Update .gitignore
echo "" >> .gitignore
echo "# Build artifacts" >> .gitignore
echo ".artifacts/" >> .gitignore
```

### Step 3: Move Examples

```bash
# Move example files
git mv profile_integration_example.py examples/
git mv fix_linting.py examples/

# Create examples README
cat > examples/README.md << 'EOF'
# Examples

Example code and utility scripts for medBillDozer.

## Files

- **profile_integration_example.py** - Patient profile integration examples
- **fix_linting.py** - Utility for fixing linting issues

## Usage

See individual file documentation for usage instructions.
EOF

git add examples/README.md
```

### Step 4: Move Config Example

```bash
# Move config example
git mv app_config.example.yaml config/examples/

# Create symlink for backward compatibility (optional)
ln -s config/examples/app_config.example.yaml app_config.example.yaml
```

### Step 5: Archive Old README

```bash
# Move to archive (already exists there)
git mv README_OLD.md docs_archive_20260205/root_markdown/
```

### Step 6: Update References

Update documentation that references moved files:

**docs/PROFILE_EDITOR_QUICKSTART.md**:
```diff
-- **[profile_integration_example.py](./profile_integration_example.py)** - Code examples
+- **[profile_integration_example.py](../examples/profile_integration_example.py)** - Code examples
```

**scripts/export_error_type_performance.py**:
```diff
-def export_error_type_performance(environment=None, output_file='error_type_performance.csv'):
+def export_error_type_performance(environment=None, output_file='.artifacts/error_type_performance.csv'):
```

### Step 7: Update .gitignore

```bash
cat >> .gitignore << 'EOF'

# Build artifacts directory
.artifacts/
*.json.bak
*.csv.bak

# Example outputs
examples/output/
examples/*.log
EOF
```

## Files That CANNOT Be Moved

These files **MUST** stay in root:

1. **app.py** - Streamlit expects `streamlit run app.py`
2. **benchmark_dashboard.py** - Alternative entry point
3. **pyproject.toml** - pip looks here for package config
4. **pytest.ini** - pytest looks in root first
5. **requirements.txt** - pip standard location
6. **app_config.yaml** - Application loads from `./app_config.yaml`
7. **LICENSE** - GitHub displays from root
8. **README.md** - GitHub displays from root
9. **.gitignore, .flake8, .markdownlint.json** - Tools expect root
10. **Makefile** - make command expects root

## Breaking Changes Check

### Files with Hardcoded Paths

Check for hardcoded paths that would break:

```bash
# Check for hardcoded references to moved files
grep -r "profile_integration_example\.py" --include="*.py" --include="*.md" .
grep -r "fix_linting\.py" --include="*.py" .
grep -r "bandit-report\.json" --include="*.py" .
grep -r "error_type_performance\.csv" --include="*.py" .
```

### Import Statements

No Python imports from moved files (they're examples/scripts).

## Testing Plan

After migration:

```bash
# 1. Run tests
pytest

# 2. Start app
streamlit run app.py

# 3. Run benchmark dashboard
streamlit run benchmark_dashboard.py

# 4. Check imports work
python -c "from medbilldozer.core import auth"

# 5. Run example (from new location)
python examples/profile_integration_example.py

# 6. Generate artifacts (check new paths)
python scripts/export_error_type_performance.py
ls -la .artifacts/error_type_performance.csv
```

## Benefits

✅ **Cleaner root**: 20+ files → ~12 essential files
✅ **Organized artifacts**: Build outputs in `.artifacts/`
✅ **Clear examples**: Example code in `examples/`
✅ **No breaking changes**: App, tests, imports all work
✅ **Git history preserved**: Using `git mv`
✅ **Backward compatible**: Symlinks for config example

## Rollback Plan

If issues arise:

```bash
# Restore original structure
git mv .artifacts/bandit-report.json .
git mv .artifacts/error_type_performance.csv .
git mv .artifacts/COMMIT_MESSAGE.txt .
git mv examples/profile_integration_example.py .
git mv examples/fix_linting.py .
git mv config/examples/app_config.example.yaml .

# Remove new directories
rmdir .artifacts examples/
```

## Execution Checklist

- [ ] Backup current state: `git stash` or create branch
- [ ] Create new directories
- [ ] Move artifacts to `.artifacts/`
- [ ] Move examples to `examples/`
- [ ] Move config example to `config/examples/`
- [ ] Archive old README
- [ ] Update documentation references (3 files)
- [ ] Update script output paths (1 file)
- [ ] Update .gitignore
- [ ] Test application: `streamlit run app.py`
- [ ] Test benchmarks: `streamlit run benchmark_dashboard.py`
- [ ] Run test suite: `pytest`
- [ ] Verify examples work: `python examples/profile_integration_example.py`
- [ ] Commit changes with detailed message
- [ ] Verify GitHub displays README correctly

## Estimated Impact

- **Risk Level**: LOW
- **Breaking Changes**: 0 (with proper path updates)
- **Files Modified**: 14 moved, 4 updated
- **Time Required**: 10-15 minutes
- **Testing Required**: 5 minutes
