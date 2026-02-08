# Development Setup

Complete guide to setting up medBillDozer for local development.

## Prerequisites

- **Python 3.11+** (3.13 recommended)
- **pip** (Python package manager)
- **git** (version control)
- **macOS, Linux, or Windows** (WSL recommended for Windows)

Optional:
- **virtualenv** or **conda** for environment management
- **VS Code** with Python extension
- **Docker** for containerized development

## Quick Setup

```bash
# 1. Clone repository
git clone https://github.com/boobootoo2/medbilldozer.git
cd medbilldozer

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install package in editable mode
pip install -e .

# 4. Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt      # For testing
pip install -r requirements-benchmarks.txt  # For benchmarks

# 5. Set up environment variables (optional)
cp .env.example .env
# Edit .env with your API keys

# 6. Verify installation
python -c "import medbilldozer; print(medbilldozer.__version__)"

# 7. Run tests
pytest tests/ -v

# 8. Launch application
streamlit run medBillDozer.py
```

## Detailed Setup

### 1. Python Version

Check your Python version:

```bash
python3 --version
```

If you don't have Python 3.11+, install it:

**macOS** (using Homebrew):
```bash
brew install python@3.13
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3.13 python3.13-venv
```

**Windows**:
Download from [python.org](https://www.python.org/downloads/)

### 2. Virtual Environment

Create isolated Python environment:

**Using venv** (built-in):
```bash
python3 -m venv venv
source venv/bin/activate
```

**Using conda**:
```bash
conda create -n medbilldozer python=3.13
conda activate medbilldozer
```

### 3. Install Package

Install medBillDozer in editable mode:

```bash
pip install -e .
```

This creates a `medbilldozer.egg-info` directory and allows you to edit source code without reinstalling.

**Verify**:
```bash
python -c "import medbilldozer; print(medbilldozer.__version__)"
# Output: 0.2.0
```

### 4. Install Dependencies

Install required packages:

```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-test.txt

# Benchmark dependencies  
pip install -r requirements-benchmarks.txt

# Optional: Monitoring dependencies
pip install -r requirements-monitoring.txt
```

**requirements.txt** includes:
- streamlit (UI framework)
- openai (GPT-4 provider)
- google-generativeai (Gemini provider)
- supabase (optional persistence)
- pandas, numpy (data processing)

**requirements-test.txt** includes:
- pytest (test runner)
- pytest-cov (coverage)
- pytest-mock (mocking)

### 5. Environment Variables

Create `.env` file for configuration:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# AI Provider Keys
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_gemini_key_here

# Optional: Access Control
APP_ACCESS_PASSWORD=your_password

# Optional: Feature Flags
GUIDED_TOUR=TRUE
PROFILE_EDITOR_ENABLED=TRUE
IMPORTER_ENABLED=TRUE

# Optional: Supabase (persistence)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Optional: MedGemma
MEDGEMMA_ENDPOINT=your_endpoint
MEDGEMMA_API_KEY=your_key
```

**Get API Keys**:
- OpenAI: https://platform.openai.com/api-keys
- Google Gemini: https://ai.google.dev/

### 6. Verify Installation

Run verification script:

```bash
python scripts/verify_setup.py
```

Or manually:

```python
# Test imports
python -c "
from medbilldozer.core import OrchestratorAgent
from medbilldozer.providers import ProviderRegistry
from medbilldozer.ui import ui
print('✅ All imports successful')
"

# Test provider registration
python -c "
from medbilldozer.providers import ProviderRegistry
providers = ProviderRegistry.list_providers()
print(f'✅ {len(providers)} providers registered: {providers}')
"
```

### 7. Run Tests

Execute test suite:

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/medbilldozer --cov-report=html

# Specific test file
pytest tests/test_orchestrator_agent.py -v

# Specific test
pytest tests/test_orchestrator_agent.py::TestOrchestratorAgent::test_run_basic_workflow -v
```

**Expected output**:
```
tests/test_config.py ............... PASSED
tests/test_image_paths.py .......... PASSED
tests/test_orchestrator_agent.py ... PASSED
tests/test_sanitize.py ............. PASSED
tests/test_ui.py ................... PASSED

134 passed in 12.5s
```

### 8. Launch Application

Start Streamlit server:

```bash
streamlit run medBillDozer.py
```

Application opens at: http://localhost:8501

**Launch clinical performance dashboard**:
```bash
streamlit run clinical_performance.py
```

Opens at: http://localhost:8502

## Development Tools

### Code Formatting

**Black** (auto-formatter):
```bash
pip install black
black src/ tests/ scripts/
```

**flake8** (linter):
```bash
pip install flake8
flake8 src/ tests/ scripts/
```

Configuration in `.flake8` and `pyproject.toml`

### Type Checking

**mypy** (static type checker):
```bash
pip install mypy
mypy src/
```

Configuration in `pyproject.toml`

### Pre-commit Hooks

Install git hooks:

```bash
pip install pre-commit
pre-commit install
```

Hooks run automatically on `git commit`:
- Black formatting
- flake8 linting
- Trailing whitespace removal
- YAML validation

## IDE Setup

### VS Code

Recommended extensions:
- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **Black Formatter** (ms-python.black-formatter)
- **GitLens** (eamodio.gitlens)

Settings (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

### PyCharm

1. Open project directory
2. Configure interpreter: Settings → Project → Python Interpreter
3. Select virtual environment: `venv/bin/python`
4. Enable pytest: Settings → Tools → Python Integrated Tools → Testing
5. Set default test runner to pytest

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'medbilldozer'`

**Solution**:
```bash
# Ensure package installed in editable mode
pip install -e .

# Verify installation
pip list | grep medbilldozer
```

### API Key Issues

**Problem**: `openai.AuthenticationError: Invalid API key`

**Solution**:
1. Verify `.env` file exists
2. Check API key is correct
3. Restart application to reload environment

**Alternative**: Set environment variables directly
```bash
export OPENAI_API_KEY="your_key"
streamlit run medBillDozer.py
```

### Port Already in Use

**Problem**: `Address already in use: Port 8501`

**Solution**:
```bash
# Find process using port
lsof -i :8501

# Kill process
kill -9 <PID>

# Or use different port
streamlit run medBillDozer.py --server.port 8503
```

### Test Failures

**Problem**: Tests fail with import errors

**Solution**:
```bash
# Ensure test dependencies installed
pip install -r requirements-test.txt

# Run from project root
cd /path/to/medbilldozer
pytest tests/ -v
```

## Docker Setup (Optional)

Build Docker image:

```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 8501

CMD ["streamlit", "run", "medBillDozer.py", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t medbilldozer .
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key medbilldozer
```

## Next Steps

- [Testing Guide](testing.md) - Run and write tests
- [Package Structure](package_structure.md) - Understand codebase
- [Scripts Reference](scripts.md) - CLI tools
- [Architecture Overview](../architecture/system_overview.md) - System design
