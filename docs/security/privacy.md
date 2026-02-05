# Privacy & Data Handling

Protect sensitive medical and financial information.

## Overview

medBillDozer processes sensitive documents containing:
- **Protected Health Information (PHI)**: Patient names, diagnoses, procedures
- **Financial data**: Credit card numbers, bank accounts, insurance info
- **Personal Identifiable Information (PII)**: Addresses, phone numbers, SSNs

**Privacy principles**:
1. **Local-first**: Documents processed in-browser/locally
2. **No permanent storage**: Data not saved unless explicitly requested
3. **Minimal transmission**: Only necessary data sent to AI providers
4. **User control**: Users decide what data to share

## Local-First Architecture

### How It Works

```
┌─────────────────────┐
│  User's Browser     │
│  ┌───────────────┐  │
│  │ Upload File   │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ Parse & Clean │  │ ← All processing happens locally
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ Send to AI    │  │ ← Only text sent to OpenAI/Google
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ Display Results│  │ ← Results shown immediately
│  └───────────────┘  │
│                     │
│  ❌ No database    │
│  ❌ No file storage│
│  ❌ No logging     │
└─────────────────────┘
```

**Key features**:
- Documents uploaded via Streamlit's `file_uploader` (in-memory only)
- No files saved to disk on server
- Results displayed immediately, then discarded
- No permanent storage of user data

### What Gets Stored

**✅ Stored**:
- App configuration (public, no user data)
- Benchmark test cases (public, synthetic data)

**❌ NOT Stored**:
- Uploaded documents
- Extracted data (patient info, charges)
- Analysis results
- User session data (beyond Streamlit's temporary session state)

## Data Transmission

### What Gets Sent to AI Providers

When analyzing a document, only the **text content** is sent to AI providers (OpenAI, Google, etc.).

**Sent**:
```python
# Example: Text extracted from medical bill
text = """
MEDICAL BILL
Provider: Dr. Jane Doe
Patient: John Smith
Date: 2024-01-15

CPT 45385 - Colonoscopy ............ $2,450.00
CPT 00810 - Anesthesia ............. $400.00
"""

# This text is sent to OpenAI/Google for analysis
response = provider.generate(prompt + text)
```

**NOT sent**:
- Original file (PDF, image)
- File metadata (filename, upload timestamp)
- User information (IP address, session ID)
- Previous uploads or results

### AI Provider Privacy Policies

**OpenAI**:
- API data NOT used for training (as of March 2023)
- Data retained for 30 days for abuse monitoring
- Zero data retention available for Enterprise

**Google Gemini**:
- API data NOT used for training
- Data retained temporarily for service improvement
- Can opt out via API settings

**Best practice**: Review provider policies before production use.

## PII/PHI Handling

### Identification

medBillDozer may encounter:

**PHI (Protected Health Information)**:
- Patient name
- Date of birth
- Medical record number
- Diagnosis codes
- Procedure codes
- Provider names

**PII (Personal Identifiable Information)**:
- Social Security Number
- Driver's license number
- Insurance ID number
- Credit card number
- Bank account number
- Address, phone, email

### Redaction (Optional)

For maximum privacy, redact PII before analysis:

```python
# src/medbilldozer/utils/redaction.py
import re

def redact_pii(text: str) -> str:
    """
    Redact common PII patterns from text.
    
    Args:
        text: Raw document text
    
    Returns:
        Text with PII redacted
    """
    # SSN: 123-45-6789
    text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_REDACTED]", text)
    
    # Credit card: 1234 5678 9012 3456
    text = re.sub(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[CARD_REDACTED]", text)
    
    # Phone: (123) 456-7890 or 123-456-7890
    text = re.sub(r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b", "[PHONE_REDACTED]", text)
    
    # Email: user@example.com
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL_REDACTED]", text)
    
    return text

def redact_patient_name(text: str, patient_name: str) -> str:
    """Redact specific patient name."""
    return text.replace(patient_name, "[PATIENT_NAME]")
```

**Usage**:
```python
# Optional redaction before analysis
if st.checkbox("Redact personal information"):
    text = redact_pii(text)
    st.info("✓ PII redacted")

# Analyze redacted text
result = orchestrator.run(text)
```

**Note**: Redaction may reduce analysis accuracy (e.g., can't detect patient name mismatches).

## User Control

### Opt-in for Data Sharing

Give users explicit control:

```python
# app.py
import streamlit as st

st.markdown("### Privacy Settings")

# Provider selection
provider = st.selectbox(
    "AI Provider",
    options=["gpt-4o-mini", "gemini-2.0-flash", "heuristic"],
    help="gpt-4o-mini and gemini-2.0-flash send data to external APIs. Heuristic processes locally."
)

if provider != "heuristic":
    st.warning(f"""
    ⚠️ **Privacy Notice**
    
    Using {provider} will send your document text to an external AI provider.
    - Your document is processed in real-time
    - No data is permanently stored by medBillDozer
    - Review AI provider's privacy policy for their data handling
    
    For maximum privacy, use the "Rule-Based (Free)" provider.
    """)
    
    consent = st.checkbox("I understand and consent to sending data to AI provider")
    
    if not consent:
        st.info("Select 'Rule-Based (Free)' for local-only processing.")
        st.stop()
```

### Data Export

Allow users to export their results:

```python
# After analysis
if result:
    st.markdown("### Export Results")
    
    # JSON export
    json_data = json.dumps(result, indent=2)
    st.download_button(
        label="📥 Download as JSON",
        data=json_data,
        file_name="analysis_results.json",
        mime="application/json"
    )
    
    # CSV export (issues only)
    if "issues" in result:
        csv_data = issues_to_csv(result["issues"])
        st.download_button(
            label="📥 Download Issues as CSV",
            data=csv_data,
            file_name="issues.csv",
            mime="text/csv"
        )
```

## Supabase Integration (Optional)

If using Supabase for persistence:

### Data Stored

```sql
-- analyses table
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,           -- Anonymous session ID
    created_at TIMESTAMP DEFAULT NOW(),
    document_type TEXT,              -- "medical_bill", "eob", etc.
    issue_count INTEGER,
    potential_savings DECIMAL(10,2),
    provider_used TEXT               -- "gpt-4o-mini", etc.
    -- NO document text stored
    -- NO patient names stored
    -- NO extracted data stored
);

-- Optional: Store anonymized issues
CREATE TABLE issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analyses(id),
    category TEXT,                   -- "overcharge", "duplicate", etc.
    severity TEXT,                   -- "high", "medium", "low"
    max_savings DECIMAL(10,2)
    -- NO detailed explanation stored
    -- NO CPT codes stored (could identify patient)
);
```

### Anonymization

```python
# src/medbilldozer/data/supabase_storage.py
from supabase import create_client
import hashlib

def anonymize_user_id(session_id: str) -> str:
    """Hash session ID for anonymity."""
    return hashlib.sha256(session_id.encode()).hexdigest()[:16]

def save_analysis_summary(result: dict, session_id: str):
    """Save only anonymized summary, not full data."""
    supabase = create_client(url, key)
    
    # Anonymize user
    anon_id = anonymize_user_id(session_id)
    
    # Save only aggregate data
    supabase.table("analyses").insert({
        "user_id": anon_id,
        "document_type": result.get("document_type"),
        "issue_count": len(result.get("issues", [])),
        "potential_savings": sum(i["max_savings"] for i in result.get("issues", [])),
        "provider_used": result.get("provider")
        # NO document text
        # NO patient info
        # NO detailed results
    }).execute()
```

## HIPAA Compliance Considerations

**Important**: medBillDozer is NOT HIPAA-compliant by default.

For HIPAA compliance, you would need:

### Technical Safeguards

- [ ] **Encryption at rest**: Encrypted database (Supabase encryption)
- [ ] **Encryption in transit**: HTTPS only (automatic on Streamlit Cloud)
- [ ] **Access controls**: Authentication required
- [ ] **Audit logs**: Log all data access
- [ ] **Automatic logout**: Session timeout
- [ ] **Secure deletion**: Permanent data erasure

### Organizational Safeguards

- [ ] **Business Associate Agreement (BAA)**: With OpenAI, Google (available for Enterprise)
- [ ] **Privacy policy**: Published and accessible
- [ ] **Data breach response**: Incident response plan
- [ ] **Staff training**: HIPAA training for all staff
- [ ] **Risk assessment**: Annual security risk assessment

### For HIPAA Compliance

**Option 1**: Use only local processing
```python
# Force heuristic provider (no external APIs)
DEFAULT_PROVIDER = "heuristic"
ALLOWED_PROVIDERS = ["heuristic"]
```

**Option 2**: Sign BAAs with providers
- OpenAI Enterprise: BAA available
- Google Cloud: BAA available for Healthcare API
- Host MedGemma yourself

**Option 3**: Use on-premises deployment
- Self-host Streamlit app
- Self-host AI models (MedGemma)
- Use encrypted database

## Security Best Practices

### 1. Minimize Data Retention

```python
# Clear session state after analysis
def clear_sensitive_data():
    """Clear sensitive data from session state."""
    keys_to_clear = [
        "uploaded_file",
        "extracted_text",
        "analysis_result",
        "patient_info"
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

# Call after user downloads results
if st.button("Clear Session Data"):
    clear_sensitive_data()
    st.success("✓ Session data cleared")
```

### 2. Secure Logging

```python
# src/medbilldozer/utils/logging_config.py
import logging

def configure_logging():
    """Configure logging to exclude sensitive data."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Never log these fields
    SENSITIVE_FIELDS = [
        "patient_name",
        "ssn",
        "credit_card",
        "api_key"
    ]

def sanitize_log_message(message: str) -> str:
    """Remove sensitive data from log messages."""
    # Replace common PII patterns
    message = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED]", message)
    message = re.sub(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[REDACTED]", message)
    return message

# Usage
logger.info(sanitize_log_message(f"Processing document: {filename}"))
```

### 3. Session Security

```python
# Implement session timeout
from datetime import datetime, timedelta

SESSION_TIMEOUT_MINUTES = 30

def check_session_timeout():
    """Check if session has timed out."""
    if "last_activity" not in st.session_state:
        st.session_state.last_activity = datetime.now()
        return
    
    last_activity = st.session_state.last_activity
    now = datetime.now()
    
    if now - last_activity > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        # Session timed out
        clear_sensitive_data()
        st.warning("⏱️ Session timed out for security. Please upload document again.")
        st.stop()
    
    # Update last activity
    st.session_state.last_activity = now

# Call at start of each page
check_session_timeout()
```

## Privacy Policy Template

Create `PRIVACY_POLICY.md`:

```markdown
# Privacy Policy - medBillDozer

**Last Updated**: [Date]

## What Data We Collect

- Document text (temporarily, for analysis only)
- Session ID (anonymous, for rate limiting)
- Usage analytics (aggregate only)

## What We Do NOT Collect

- Your uploaded documents (not saved)
- Personal health information
- Payment information
- Contact information

## How We Use Data

- **Document text**: Sent to AI provider (OpenAI/Google) for analysis, then discarded
- **Session ID**: Used for rate limiting, then discarded
- **Usage analytics**: Aggregate metrics only (no individual data)

## Data Sharing

- **AI Providers**: Document text sent to OpenAI or Google API (see provider selection)
- **No other sharing**: We do not sell or share your data

## Data Retention

- **During session**: Data kept in memory during analysis
- **After session**: All data discarded immediately
- **No permanent storage**: Documents and results are not saved

## Your Rights

- **Access**: No data stored to access
- **Deletion**: All data auto-deleted after session
- **Export**: Download your results anytime during session

## Security

- HTTPS encryption for all data transmission
- No permanent storage of sensitive data
- Rate limiting to prevent abuse

## Changes

We may update this policy. Check this page for latest version.

## Contact

Questions? Email: [your-email]
```

## Compliance Checklist

### Before Launch

- [ ] Privacy policy published
- [ ] User consent mechanism implemented
- [ ] PII redaction available (optional)
- [ ] Local-only processing option available
- [ ] Data transmission disclosed to users
- [ ] Session timeout implemented
- [ ] Sensitive data cleared after use
- [ ] Logging excludes PII/PHI
- [ ] API keys secured
- [ ] HTTPS enforced

### If Using Supabase

- [ ] Only anonymized data stored
- [ ] No document text stored
- [ ] No patient names stored
- [ ] User IDs hashed
- [ ] Database encrypted
- [ ] Access controls configured
- [ ] Audit logging enabled

### If HIPAA Required

- [ ] BAA signed with AI providers
- [ ] On-premises deployment OR
- [ ] Local-only processing
- [ ] All HIPAA technical safeguards implemented
- [ ] Privacy policy updated for HIPAA
- [ ] Staff HIPAA training complete
- [ ] Annual risk assessment scheduled

## Next Steps

- [Sanitization Guide](sanitization.md) - Input security
- [Streamlit Deployment](../deployment/streamlit.md) - Secure deployment
- [Environment Variables](../deployment/environment_variables.md) - Configuration security
