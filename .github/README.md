 [![Run Tests](https://github.com/boobootoo2/medbilldozer/actions/workflows/python-app.yml/badge.svg)](https://github.com/boobootoo2/medbilldozer/actions/workflows/python-app.yml)

![CodeQL](https://github.com/boobootoo2/medbilldozer/actions/workflows/codeql.yml/badge.svg)

![Security Audit](https://github.com/boobootoo2/medbilldozer/actions/workflows/security.yml/badge.svg)

[![Run Benchmarks](https://github.com/boobootoo2/medbilldozer/actions/workflows/run_benchmarks.yml/badge.svg)](https://github.com/boobootoo2/medbilldozer/actions/workflows/run_benchmarks.yml)

# medBillDozer

**medBillDozer** is an AI-powered assistant that helps patients audit medical bills
and explanations of benefits (EOBs) by detecting likely billing errors and
explaining them in plain language.

## 📚 Documentation

- **📖 [README](https://github.com/boobootoo2/medbilldozer/blob/main/README.md)** – Complete user guide and quick start
- **🔬 [Technical Writeup](https://github.com/boobootoo2/medbilldozer/blob/main/docs/TECHNICAL_WRITEUP.md)** – Architecture and design
- **⚙️ [API Reference](https://github.com/boobootoo2/medbilldozer/blob/main/docs/API.md)** – Developer documentation
- **📦 [Module Documentation](https://github.com/boobootoo2/medbilldozer/blob/main/docs/MODULES.md)** – Code structure
- **🔗 [Dependencies](https://github.com/boobootoo2/medbilldozer/blob/main/docs/DEPENDENCIES.md)** – Third-party libraries


## Why medBillDozer Is Different

Most consumer medical billing tools are manual, partial, or reactive.  
medBillDozer is built to systematically reconcile bills, claims, EOBs, and receipts — the point where most billing errors actually occur.

📄 **Learn more:**  
- [Technical Writeup](https://github.com/boobootoo2/medbilldozer/blob/main/docs/TECHNICAL_WRITEUP.md)  
- [MedGemma Impact Challenge](https://github.com/boobootoo2/medbilldozer/blob/main/docs/MEDGEMMA_IMPACT_CHALLENGE_WRITEUP.md)




## Quick Start

### Installation

```bash
pip install -r requirements.txt
streamlit run medBillDozer.py
```

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

## Benchmark Results

📊 **Live benchmark dashboard:** [https://medbilldozer.streamlit.app/production_stability](https://medbilldozer.streamlit.app/production_stability)

For the latest model performance metrics, accuracy analysis, and regression tracking.

**Run locally:**
```bash
streamlit run pages/production_stability.py
```

View historical benchmark data in [`benchmarks/results/`](../benchmarks/results/) directory.

---

## Disclaimer

This project is a **prototype for educational purposes only**.

⚠️ medBillDozer does NOT provide:
- Medical, legal, or financial advice
- HIPAA-compliant healthcare services
- Guaranteed savings or outcomes
- Professional billing review

**Always verify findings** with your insurance company and consult qualified professionals for billing disputes.

---

**Built with ❤️ for patients navigating the complex world of medical billing.**
