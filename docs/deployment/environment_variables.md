# Environment Variables Reference

Complete guide to configuring medBillDozer.

## Overview

medBillDozer uses three configuration sources:
1. **Environment variables** (.env file or system)
2. **Streamlit secrets** (.streamlit/secrets.toml)
3. **YAML configuration** (app_config.yaml)

## Required Variables

### AI Provider Keys

#### OpenAI

```bash
OPENAI_API_KEY="sk-proj-..."
```

**Get key**: OpenAI Platform → API Keys → Create new secret key

**Usage**:
- GPT-4o Mini provider
- GPT-4o provider
- Text embeddings (if enabled)

**Cost**: $0.15 per 1M input tokens (gpt-4o-mini)

#### Google Gemini

```bash
GOOGLE_API_KEY="AIza..."
```

**Get key**: Google AI Studio → Get API Key

**Usage**:
- Gemini 2.0 Flash provider
- Gemini Pro provider

**Cost**: $0.10 per 1M input tokens (gemini-2.0-flash)

## Optional Variables

### MedGemma (Medical-Specific Model)

```bash
MEDGEMMA_ENDPOINT="https://api.example.com/v1/medgemma"
MEDGEMMA_API_KEY="..."
```

**Usage**:
- Specialized medical billing model
- Higher accuracy for medical terminology
- Requires self-hosted or third-party deployment

**Setup**:
```bash
# If using Hugging Face Inference API
MEDGEMMA_ENDPOINT="https://api-inference.huggingface.co/models/google/medgemma-2b"
MEDGEMMA_API_KEY="hf_..."
```

### Anthropic Claude

```bash
ANTHROPIC_API_KEY="sk-ant-..."
```

**Get key**: Anthropic Console → API Keys

**Usage**:
- Claude 3.5 Sonnet provider (if enabled)
- Alternative to OpenAI/Google

**Cost**: $3.00 per 1M input tokens

### Supabase (Database)

```bash
SUPABASE_URL="https://xxx.supabase.co"
SUPABASE_KEY="eyJhbG..."
```

**Get credentials**: Supabase Dashboard → Settings → API

**Usage**:
- Store analysis history
- User accounts (if auth enabled)
- Document storage

**Optional**: Not required for core functionality

### Audio Features

```bash
ENABLE_AUDIO="true"
OPENAI_TTS_VOICE="alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer
```

**Usage**:
- Text-to-speech for analysis results
- Voice controls (experimental)

**Cost**: $15 per 1M characters (OpenAI TTS)

## Configuration Priority

```
1. Streamlit Secrets (highest priority)
   ↓
2. Environment Variables
   ↓
3. .env File
   ↓
4. YAML Config Defaults (lowest priority)
```

**Example**:
```python
# Check in order
api_key = (
    st.secrets.get("OPENAI_API_KEY")  # 1. Streamlit secrets
    or os.getenv("OPENAI_API_KEY")     # 2. Environment variable
    or load_from_env_file("OPENAI_API_KEY")  # 3. .env file
    or config.get("default_api_key")   # 4. YAML default
)
```

## Setup Methods

### Method 1: .env File (Development)

Create `.env` in project root:

```bash
# .env
OPENAI_API_KEY="sk-proj-..."
GOOGLE_API_KEY="AIza..."
DEFAULT_PROVIDER="gpt-4o-mini"
MAX_FILE_SIZE_MB="10"
ENABLE_AUDIO="false"
```

**Load in Python**:
```python
from dotenv import load_dotenv
load_dotenv()

import os
api_key = os.getenv("OPENAI_API_KEY")
```

**Security**: Add to .gitignore
```
# .gitignore
.env
.env.local
.env.*.local
```

### Method 2: Streamlit Secrets (Production)

Create `.streamlit/secrets.toml`:

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "sk-proj-..."
GOOGLE_API_KEY = "AIza..."

[app_config]
DEFAULT_PROVIDER = "gpt-4o-mini"
MAX_FILE_SIZE_MB = 10
ENABLE_AUDIO = false
```

**Access in code**:
```python
import streamlit as st

# Simple key
api_key = st.secrets["OPENAI_API_KEY"]

# Nested config
provider = st.secrets["app_config"]["DEFAULT_PROVIDER"]
```

**Streamlit Cloud**: Add secrets in UI (Settings → Secrets)

### Method 3: System Environment (Server)

```bash
# Add to ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY="sk-proj-..."
export GOOGLE_API_KEY="AIza..."

# Reload shell
source ~/.bashrc

# Verify
echo $OPENAI_API_KEY
```

**Docker**:
```dockerfile
# Dockerfile
ENV OPENAI_API_KEY="sk-proj-..."
ENV GOOGLE_API_KEY="AIza..."
```

**Docker Compose**:
```yaml
# docker-compose.yml
services:
  app:
    environment:
      - OPENAI_API_KEY=sk-proj-...
      - GOOGLE_API_KEY=AIza...
```

## app_config.yaml Reference

Main application configuration file.

### Complete Example

```yaml
# app_config.yaml
providers:
  gpt-4o-mini:
    enabled: true
    display_name: "GPT-4o Mini"
    model: "gpt-4o-mini"
    cost_per_1k_tokens: 0.00015
    max_tokens: 16000
    temperature: 0.1
    timeout: 60
  
  gemini-2.0-flash:
    enabled: true
    display_name: "Gemini 2.0 Flash"
    model: "gemini-2.0-flash-exp"
    cost_per_1k_tokens: 0.0001
    max_tokens: 1000000
    temperature: 0.1
    timeout: 60
  
  medgemma:
    enabled: false  # Requires endpoint configuration
    display_name: "MedGemma"
    model: "medgemma-2b"
    cost_per_1k_tokens: 0.0
    endpoint: "${MEDGEMMA_ENDPOINT}"
    api_key: "${MEDGEMMA_API_KEY}"
  
  heuristic:
    enabled: true
    display_name: "Rule-Based (Free)"
    cost_per_1k_tokens: 0.0

default_provider: "gpt-4o-mini"

features:
  enable_audio: false
  enable_chat: true
  enable_benchmarks: true
  enable_supabase: false

upload:
  max_file_size_mb: 10
  allowed_types:
    - "pdf"
    - "txt"
    - "png"
    - "jpg"
    - "jpeg"

ui:
  theme: "light"
  show_cost_estimates: true
  show_model_names: true

benchmark:
  test_directory: "benchmarks/inputs"
  expected_directory: "benchmarks/expected_outputs"
  results_directory: "benchmarks/results"
```

### Provider Configuration

```yaml
providers:
  provider_key:
    enabled: true               # Enable/disable provider
    display_name: "Name"        # UI display name
    model: "model-id"           # Model identifier
    cost_per_1k_tokens: 0.0001  # Cost in USD
    max_tokens: 16000           # Context window size
    temperature: 0.1            # Sampling temperature (0.0-1.0)
    timeout: 60                 # Request timeout (seconds)
```

### Feature Flags

```yaml
features:
  enable_audio: false         # Text-to-speech features
  enable_chat: true           # Chat assistant page
  enable_benchmarks: true     # Benchmark dashboard
  enable_supabase: false      # Database integration
```

### Upload Limits

```yaml
upload:
  max_file_size_mb: 10        # Maximum file size
  allowed_types:              # File extensions
    - "pdf"
    - "txt"
    - "png"
    - "jpg"
```

## Environment Variable Reference

### Complete List

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OPENAI_API_KEY` | string | (required) | OpenAI API key |
| `GOOGLE_API_KEY` | string | (required) | Google API key |
| `ANTHROPIC_API_KEY` | string | optional | Claude API key |
| `MEDGEMMA_ENDPOINT` | string | optional | MedGemma endpoint URL |
| `MEDGEMMA_API_KEY` | string | optional | MedGemma API key |
| `SUPABASE_URL` | string | optional | Supabase project URL |
| `SUPABASE_KEY` | string | optional | Supabase anonymous key |
| `DEFAULT_PROVIDER` | string | "gpt-4o-mini" | Default AI provider |
| `MAX_FILE_SIZE_MB` | integer | 10 | Max upload size (MB) |
| `ENABLE_AUDIO` | boolean | false | Enable audio features |
| `OPENAI_TTS_VOICE` | string | "alloy" | TTS voice selection |
| `DEBUG` | boolean | false | Enable debug logging |
| `LOG_LEVEL` | string | "INFO" | Logging level |

### Type Conversions

**Boolean**:
```python
# Any of these = True
ENABLE_AUDIO="true"
ENABLE_AUDIO="True"
ENABLE_AUDIO="TRUE"
ENABLE_AUDIO="1"
ENABLE_AUDIO="yes"

# Any of these = False
ENABLE_AUDIO="false"
ENABLE_AUDIO="False"
ENABLE_AUDIO="FALSE"
ENABLE_AUDIO="0"
ENABLE_AUDIO="no"
ENABLE_AUDIO=""  # Empty string
```

**Integer**:
```python
MAX_FILE_SIZE_MB="10"  # Converted to int(10)
```

**Float**:
```python
TEMPERATURE="0.1"  # Converted to float(0.1)
```

## Validation

### Check Configuration

```python
# scripts/verify_setup.py
import os
from medbilldozer.core.config import load_config

def validate_environment():
    """Validate all required environment variables."""
    errors = []
    
    # Check required keys
    if not os.getenv("OPENAI_API_KEY"):
        errors.append("OPENAI_API_KEY not set")
    
    if not os.getenv("GOOGLE_API_KEY"):
        errors.append("GOOGLE_API_KEY not set")
    
    # Check key format
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key and not openai_key.startswith("sk-"):
        errors.append("OPENAI_API_KEY has invalid format (should start with 'sk-')")
    
    # Check config file
    try:
        config = load_config()
    except Exception as e:
        errors.append(f"app_config.yaml invalid: {e}")
    
    return errors

# Run validation
errors = validate_environment()
if errors:
    print("❌ Configuration errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✅ Configuration valid")
```

### Test API Keys

```python
# Test OpenAI
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "test"}],
    max_tokens=5
)
print("✓ OpenAI key valid")

# Test Google
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-exp")
response = model.generate_content("test")
print("✓ Google key valid")
```

## Security Best Practices

### 1. Never Commit Secrets

```bash
# .gitignore
.env
.env.*
.streamlit/secrets.toml
app_config.yaml  # If contains secrets
```

### 2. Rotate Keys Regularly

```bash
# Rotate every 90 days
# 1. Generate new key in provider dashboard
# 2. Update environment variable
# 3. Test application
# 4. Revoke old key
```

### 3. Use Minimum Permissions

- OpenAI: Use project-scoped keys, not user keys
- Google: Restrict API key to specific APIs
- Supabase: Use service role key only server-side

### 4. Monitor Usage

```python
# Track API calls and costs
from medbilldozer.utils.cost_tracker import CostTracker

tracker = CostTracker()
tracker.log_call("gpt-4o-mini", tokens=1000)

# Get daily usage
daily_cost = tracker.get_daily_cost()
if daily_cost > 10.0:  # $10 limit
    send_alert(f"High API usage: ${daily_cost:.2f}")
```

## Troubleshooting

### "API key not found"

```bash
# Check if set
echo $OPENAI_API_KEY

# Set temporarily
export OPENAI_API_KEY="sk-proj-..."

# Set permanently
echo 'export OPENAI_API_KEY="sk-proj-..."' >> ~/.bashrc
source ~/.bashrc
```

### "Invalid API key"

```bash
# Check key format
# OpenAI: starts with sk-proj- (new) or sk- (old)
# Google: starts with AIza

# Test key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### "Configuration file not found"

```bash
# Check file exists
ls -la app_config.yaml

# Check current directory
pwd

# Run from project root
cd /path/to/medbilldozer
streamlit run app.py
```

## Next Steps

- [Streamlit Deployment](streamlit.md) - Deploy to production
- [GitHub Actions](github_actions.md) - Automated CI/CD
- [Security Guide](../security/privacy.md) - Privacy best practices
