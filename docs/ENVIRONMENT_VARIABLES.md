# Environment Variables Guide

This document describes all environment variables supported by medBillDozer.

## Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values

3. Restart the Streamlit app to apply changes

## Available Environment Variables

### Access Control

#### `APP_ACCESS_PASSWORD`

**Purpose**: Soft gate password protection for the application

**Type**: String (optional)

**Behavior**:
- If **set**: Users must enter the correct password before accessing the app
- If **unset or empty**: App is open to all users (no password required)

**Example**:
```bash
export APP_ACCESS_PASSWORD="SecurePass123"
```

**Use Cases**:
- Demo deployments where you want controlled access
- Internal testing environments
- Sharing with specific users while maintaining public URL

---

### Feature Flags

#### `GUIDED_TOUR`

**Purpose**: Enable/disable the interactive guided tour for new users

**Type**: Boolean string

**Behavior**:
- **Overrides** the `app_config.yaml` setting if set
- If **unset**: Falls back to `app_config.yaml` configuration
- Accepted values (case-insensitive):
  - Enable: `TRUE`, `1`, `YES`, `ON`
  - Disable: `FALSE`, `0`, `NO`, `OFF`

**Example**:
```bash
export GUIDED_TOUR=TRUE
```

**Use Cases**:
- Enable tour for demo deployments
- Disable tour for experienced users
- A/B testing different onboarding experiences
- Quick override without editing config files

---

### AI Provider Keys

#### `OPENAI_API_KEY`

**Purpose**: API key for OpenAI GPT models (gpt-4o-mini, etc.)

**Required**: For OpenAI-based analysis

**Get Key**: https://platform.openai.com/api-keys

**Example**:
```bash
export OPENAI_API_KEY="sk-..."
```

---

#### `GOOGLE_API_KEY`

**Purpose**: API key for Google Gemini models

**Required**: For Gemini-based analysis

**Get Key**: https://aistudio.google.com/app/apikey

**Example**:
```bash
export GOOGLE_API_KEY="AI..."
```

---

## Deployment Examples

### Local Development
```bash
# .env file
APP_ACCESS_PASSWORD=
GUIDED_TOUR=TRUE
OPENAI_API_KEY=sk-your-key-here
```

### Production Demo
```bash
# Set via hosting platform (Streamlit Cloud, Heroku, etc.)
APP_ACCESS_PASSWORD=DemoAccess2024
GUIDED_TOUR=FALSE
OPENAI_API_KEY=sk-prod-key-here
```

### Testing Environment
```bash
# Quick testing without editing config
export GUIDED_TOUR=FALSE
streamlit run app.py
```

---

## Security Best Practices

1. ✅ **Never commit `.env` files** - Already in `.gitignore`
2. ✅ **Use strong passwords** - At least 12 characters with mixed case, numbers, symbols
3. ✅ **Rotate API keys** - Regularly update production API keys
4. ✅ **Use different keys per environment** - Separate dev/staging/prod keys
5. ✅ **Set via platform settings** - For production, use hosting platform's environment variable UI

---

## Troubleshooting

### Password Gate Not Showing
- Check that `APP_ACCESS_PASSWORD` is actually set
- Restart the Streamlit app after setting the variable
- Clear browser cache/session if previously accessed without password

### Guided Tour Not Enabling/Disabling
- Ensure `GUIDED_TOUR` value is exactly `TRUE` or `FALSE` (case-insensitive)
- If unset, check `app_config.yaml` → `features.guided_tour.enabled`
- Restart app after changing environment variable

### API Keys Not Working
- Verify key format (OpenAI: `sk-...`, Gemini: `AI...`)
- Check for extra spaces or quotes in environment variable
- Ensure keys have sufficient credits/quota
- Test keys using provider's playground/testing tools first

---

## Migration from Config File

If you previously set these in `app_config.yaml`:

```yaml
# OLD (still works, but env vars override)
features:
  guided_tour:
    enabled: true
```

You can now use environment variables for easier deployment:

```bash
# NEW (takes precedence)
export GUIDED_TOUR=TRUE
```

The environment variable approach is recommended for:
- Deployment environments (Streamlit Cloud, Heroku, Docker)
- Quick testing/debugging
- Per-environment configuration

The config file approach is recommended for:
- Development defaults
- Shared team settings
- Version-controlled configuration
