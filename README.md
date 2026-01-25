# medBillDozer

**medBillDozer** is an AI-powered assistant that helps patients audit medical bills
and explanations of benefits (EOBs) by detecting likely billing errors and
explaining them in plain language.

## Features

- **� AI-Powered Billing Analysis** - Detect errors and overcharges in medical bills
- **📋 Profile Editor** - Manage your identity, insurance plans, and provider directory
- **📥 Data Importer** - Import EOBs, claim histories, and bills with a Plaid-like wizard
- **🎓 Guided Tour** - Interactive onboarding for new users
- **🔒 Privacy-First** - All data stays local (no cloud storage)

### Documentation

- **�📖 [Quick Start Guide](./docs/QUICKSTART.md)** - Get up and running in 5 minutes
- **📋 [Profile Editor Quick Start](./PROFILE_EDITOR_QUICKSTART.md)** - Set up your profile in 3 steps
- **📚 [User Guide](./docs/USER_GUIDE.md)** - Comprehensive end-user documentation
- **⚙️ [Configuration Guide](./CONFIG_README.md)** - Feature flags and app configuration
- **🔧 [Technical Documentation](./docs/)** - API reference, modules, dependencies
- **🔌 [Profile Editor Integration](./PROFILE_EDITOR_INTEGRATION.md)** - Developer integration guide
- **🧠 [MedGemma & HAI-DEF Alignment](./docs/HAI_DEF_ALIGNMENT.md)** - How this project uses healthcare-aligned foundation models
- **📝 [Contributing](./DOCUMENTATION.md)** - How to contribute and maintain docs


## Quick Start

### Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Environment Variables (Optional)

Create a `.env` file or set environment variables:

```bash
# Access Control (optional soft gate)
export APP_ACCESS_PASSWORD="your_password"

# Guided Tour (overrides config)
export GUIDED_TOUR=TRUE

# Profile Editor Features
export PROFILE_EDITOR_ENABLED=TRUE
export IMPORTER_ENABLED=TRUE

# AI Provider Keys
export OPENAI_API_KEY="your-key-here"
export GOOGLE_API_KEY="your-gemini-key"
```

See `.env.example` for full documentation.

### 5-Minute Tutorial

1. **Set up an API key** (optional - or use free "Local Heuristic" mode):
   ```bash
   export OPENAI_API_KEY="your-key-here"
   # or use GOOGLE_API_KEY for Gemini
   ```

2. **Launch and try a demo**:
   - Accept privacy policy
   - Check "🏥 Colonoscopy Bill" in demo section
   - Click "Analyze with medBillDozer"
   - Review savings and issues found!

3. **Analyze your own bills**:
   - Copy text from any medical bill, EOB, or receipt
   - Paste into document input area
   - Click analyze and get instant feedback

## Documentation

- **📖 [Quick Start Guide](docs/QUICKSTART.md)** - Get up and running in 5 minutes
- **📚 [User Guide](docs/USER_GUIDE.md)** - Comprehensive end-user documentation
- **⚙️ [Configuration Guide](CONFIG_README.md)** - Feature flags and app configuration
- **🔧 [Technical Documentation](docs/)** - API reference, modules, dependencies
- **📝 [Contributing](DOCUMENTATION.md)** - How to contribute and maintain docs

## Demo

See the video demo submitted to the MedGemma Impact Challenge.

## What Documents Can I Analyze?

✅ Medical procedure bills (with CPT codes)  
✅ Dental treatment bills (with CDT codes)  
✅ Pharmacy receipts  
✅ Insurance Explanation of Benefits (EOB)  
✅ FSA/HSA claim statements  

## Privacy & Security

Your data never leaves your control:
- ✅ No data storage or databases
- ✅ Session-only processing
- ✅ No user accounts or tracking
- ✅ Clear on browser close

**Note**: Document text is sent to your chosen AI provider for analysis. Use "Local Heuristic" mode for 100% offline processing.

## Disclaimer

This project is a **prototype for educational purposes only**.

⚠️ medBillDozer does NOT provide:
- Medical, legal, or financial advice
- HIPAA-compliant healthcare services
- Guaranteed savings or outcomes
- Professional billing review

**Always verify findings** with your insurance company and consult qualified professionals for billing disputes.

