# Streamlit Deployment

Deploy medBillDozer to Streamlit Cloud.

## Overview

medBillDozer is built as a Streamlit application with multi-page architecture:

```
medBillDozer.py                              # Main application entry
pages/
├── 1_📊_Snapshot_View.py          # Quick analysis view
├── 2_🔬_Analysis_View.py          # Detailed analysis
├── 3_💬_Chat_Assistant.py         # Conversational interface
├── 4_📈_Benchmark_Dashboard.py    # Performance metrics
└── 5_⚙️_Settings.py               # Configuration
```

## Local Testing

Before deployment, test locally:

```bash
# Activate environment
source venv/bin/activate

# Set environment variables
export OPENAI_API_KEY="sk-proj-..."
export GOOGLE_API_KEY="AIza..."

# Run app
streamlit run medBillDozer.py

# App available at: http://localhost:8501
```

**Verify**:
- ✓ Main page loads
- ✓ All 5 pages accessible via sidebar
- ✓ File upload works
- ✓ AI providers respond
- ✓ No errors in terminal

## Streamlit Cloud Deployment

### Prerequisites

1. **GitHub Repository**: Code must be in GitHub
2. **Streamlit Account**: Sign up at https://streamlit.io/cloud
3. **API Keys**: OpenAI and/or Google API keys

### Step 1: Prepare Repository

Ensure these files exist:

**requirements.txt**:
```txt
streamlit==1.28.1
openai==1.5.0
google-generativeai==0.3.2
pydantic==2.5.0
rich==13.7.0
anthropic==0.7.8
supabase==2.0.3
pillow==10.1.0
pandas==2.1.4
plotly==5.18.0
```

**app_config.yaml**:
```yaml
providers:
  gpt-4o-mini:
    enabled: true
    display_name: "GPT-4o Mini"
    cost_per_1k_tokens: 0.00015
  
  gemini-2.0-flash:
    enabled: true
    display_name: "Gemini 2.0 Flash"
    cost_per_1k_tokens: 0.0001
  
  heuristic:
    enabled: true
    display_name: "Rule-Based"
    cost_per_1k_tokens: 0.0

default_provider: "gpt-4o-mini"
max_file_size_mb: 10
enable_audio: false
```

**README.md**: Include deployment badge
```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://medbilldozer.streamlit.app)
```

### Step 2: Deploy from Streamlit Cloud

1. **Go to**: https://share.streamlit.io/
2. **Click**: "New app"
3. **Configure**:
   - **Repository**: `yourusername/medbilldozer`
   - **Branch**: `main`
   - **Main file path**: `medBillDozer.py`
   - **App URL**: `medbilldozer` (or custom subdomain)

4. **Advanced settings**:
   - **Python version**: 3.11
   - **Requirements file**: `requirements.txt`

### Step 3: Add Secrets

In Streamlit Cloud app settings, add secrets:

**Secrets format** (TOML):
```toml
# .streamlit/secrets.toml (for local testing)
# Or paste directly in Streamlit Cloud UI

OPENAI_API_KEY = "sk-proj-..."
GOOGLE_API_KEY = "AIza..."

# Optional
SUPABASE_URL = "https://xxx.supabase.co"
SUPABASE_KEY = "eyJhbG..."
MEDGEMMA_ENDPOINT = "https://..."
MEDGEMMA_API_KEY = "..."

# App configuration
DEFAULT_PROVIDER = "gpt-4o-mini"
MAX_FILE_SIZE_MB = "10"
ENABLE_AUDIO = "false"
```

**Access secrets in code**:
```python
# medBillDozer.py
import streamlit as st

# Streamlit Cloud automatically loads secrets
api_key = st.secrets["OPENAI_API_KEY"]
```

### Step 4: Deploy

1. **Click**: "Deploy!"
2. **Wait**: 2-5 minutes for build
3. **Monitor**: Build logs in real-time
4. **Access**: `https://medbilldozer.streamlit.app`

## Configuration

### App Configuration

Create `.streamlit/config.toml` for app settings:

```toml
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[runner]
magicEnabled = true
fastReruns = true
```

### Performance Tuning

**Enable caching**:
```python
# medBillDozer.py
import streamlit as st
from medbilldozer.core import OrchestratorAgent

@st.cache_resource
def get_orchestrator(provider_key):
    """Cache orchestrator instance."""
    return OrchestratorAgent(provider_key=provider_key)

@st.cache_data(ttl=3600)
def load_config():
    """Cache configuration for 1 hour."""
    return yaml.safe_load(open("app_config.yaml"))
```

**Memory management**:
```python
# Limit file upload size
st.file_uploader(
    "Upload document",
    type=["pdf", "txt", "png", "jpg"],
    accept_multiple_files=False,
    key="uploader"
)

# Clear cache when needed
st.cache_data.clear()
st.cache_resource.clear()
```

## Custom Domain

### Option 1: Streamlit Cloud Custom Domain

1. **Upgrade** to Teams or Enterprise plan
2. **Go to**: App settings → Custom domain
3. **Add**: `medbilldozer.example.com`
4. **Configure DNS**:
   - Type: CNAME
   - Name: `medbilldozer`
   - Value: `medbilldozer.streamlit.app`

### Option 2: Reverse Proxy

Use Cloudflare, Nginx, or Apache:

**Nginx example**:
```nginx
server {
    listen 80;
    server_name medbilldozer.example.com;
    
    location / {
        proxy_pass https://medbilldozer.streamlit.app;
        proxy_set_header Host medbilldozer.streamlit.app;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring

### Built-in Metrics

Streamlit Cloud provides:
- **Resource usage**: CPU, memory
- **Request count**: Number of sessions
- **Errors**: Runtime exceptions
- **Build logs**: Deployment history

**Access**: App settings → Metrics

### Custom Monitoring

Add health check endpoint:

```python
# pages/health.py
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Health Check", page_icon="✅")

def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.2.0"
    }

st.json(health_check())
```

### Error Tracking

Use Sentry for error tracking:

```python
# medBillDozer.py
import sentry_sdk

if "SENTRY_DSN" in st.secrets:
    sentry_sdk.init(
        dsn=st.secrets["SENTRY_DSN"],
        traces_sample_rate=0.1,
        environment="production"
    )
```

## Troubleshooting

### Build Fails

**Error**: `ModuleNotFoundError`
```
Solution:
1. Check requirements.txt includes all dependencies
2. Verify package names are correct (case-sensitive)
3. Pin versions: streamlit==1.28.1 (not streamlit>=1.28.1)
```

**Error**: `Python version mismatch`
```
Solution:
1. Add runtime.txt with: python-3.11.0
2. Or specify in Streamlit Cloud UI: Advanced → Python version
```

### Secrets Not Loading

**Error**: `KeyError: 'OPENAI_API_KEY'`
```
Solution:
1. Check secrets are added in Streamlit Cloud UI
2. Restart app after adding secrets
3. Verify TOML syntax (quotes required for strings)
4. Use st.secrets["KEY"] not os.getenv("KEY")
```

### App Crashes

**Error**: `Memory limit exceeded`
```
Solution:
1. Reduce max file size in config
2. Clear cache more frequently
3. Use st.cache_data with TTL
4. Upgrade to higher resource tier
```

**Error**: `Connection timeout`
```
Solution:
1. Increase timeout for API calls
2. Add retry logic
3. Use async where possible
4. Implement request queuing
```

### Slow Performance

```
Solutions:
1. Enable st.cache_resource for expensive objects
2. Enable st.cache_data for data loading
3. Lazy load heavy modules
4. Use st.experimental_fragment for partial reruns
5. Minimize widget state changes
```

## Security Best Practices

### 1. Secrets Management

```python
# ✓ Good: Use Streamlit secrets
api_key = st.secrets["OPENAI_API_KEY"]

# ✗ Bad: Hardcode secrets
api_key = "sk-proj-..."  # Never do this!

# ✗ Bad: Commit secrets to repo
# .env file with API keys in git
```

### 2. Input Validation

```python
# Validate file uploads
uploaded_file = st.file_uploader("Upload", type=["pdf", "txt"])

if uploaded_file:
    # Check size
    if uploaded_file.size > 10 * 1024 * 1024:  # 10 MB
        st.error("File too large")
        st.stop()
    
    # Check content type
    if uploaded_file.type not in ["application/pdf", "text/plain"]:
        st.error("Invalid file type")
        st.stop()
```

### 3. Rate Limiting

```python
# Implement simple rate limiting
from time import time
from collections import defaultdict

if "rate_limit" not in st.session_state:
    st.session_state.rate_limit = defaultdict(list)

def check_rate_limit(user_id, max_requests=10, window=60):
    """Allow max_requests per window seconds."""
    now = time()
    requests = st.session_state.rate_limit[user_id]
    
    # Remove old requests
    requests = [t for t in requests if now - t < window]
    
    if len(requests) >= max_requests:
        return False
    
    requests.append(now)
    st.session_state.rate_limit[user_id] = requests
    return True
```

### 4. HTTPS Only

Streamlit Cloud automatically provides HTTPS.

**Verify**:
```python
# Check connection is secure
if st.runtime.exists() and not st.runtime.scriptrunner.get_script_run_ctx().is_ssl:
    st.warning("⚠️ Use HTTPS for secure connection")
```

## Cost Management

### Optimize API Usage

```python
# Use cheaper models for initial analysis
provider_key = st.selectbox(
    "AI Provider",
    options=["gpt-4o-mini", "gemini-2.0-flash", "heuristic"],
    index=0  # Default to gpt-4o-mini ($0.15 per 1M tokens)
)

# Show estimated cost
if provider_key != "heuristic":
    st.info(f"💰 Estimated cost: $0.01 per analysis")
```

### Monitor Usage

```python
# Track API calls
if "api_calls" not in st.session_state:
    st.session_state.api_calls = 0

def track_api_call():
    st.session_state.api_calls += 1
    
    # Log to external service
    if st.session_state.api_calls % 100 == 0:
        log_usage_metrics(st.session_state.api_calls)

# Display in sidebar
st.sidebar.metric("API Calls", st.session_state.api_calls)
```

## Next Steps

- [Environment Variables](environment_variables.md) - Configuration reference
- [GitHub Actions](github_actions.md) - CI/CD automation
- [Security Guide](../security/privacy.md) - Privacy best practices
