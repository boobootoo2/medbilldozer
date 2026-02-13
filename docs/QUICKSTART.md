# medBillDozer Quick Start Guide

**Get up and running in 5 minutes!**

---

## 🚀 Installation & Launch

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys (Optional)

Choose one AI provider and set its API key:

**For OpenAI (GPT):**

```bash
export OPENAI_API_KEY="your-api-key-here"
```

**For Google Gemini:**

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

**For MedGemma (Hugging Face):**

```bash
export HF_TOKEN="your-huggingface-token"
export HF_MODEL_ID="google/medgemma-4b-it"
```

**Or skip API setup** and use the free "Local Heuristic" provider (no key needed, but limited capabilities).

### 3. Launch the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📋 Basic Usage (3 Steps)

### Step 1: Accept Privacy Policy

On first launch:
1. Read the privacy notice
2. Check "I agree"
3. Click "Accept"

### Step 2: Try a Demo Document

The easiest way to see how it works:
1. Scroll to **"Try Demo Documents"**
2. Check the box next to **"🏥 Colonoscopy Bill"**
3. The document will auto-load into the input area

### Step 3: Analyze

1. Click the big blue **"Analyze with medBillDozer"** button
2. Wait 5-15 seconds
3. Review the results!

---

## 💡 What You'll See

### Results Include:

**💰 Savings Summary**
- Total potential dollar savings
- Breakdown per document

**🔍 Issues Detected**
- Duplicate charges
- Math errors
- Coverage mismatches
- Unusual charges

**📊 Detailed Evidence**
- Specific line items
- CPT/CDT codes
- Dates and amounts

**✅ Recommended Actions**
- What to do about each issue
- Who to contact
- What to reference

---

## 📝 Analyzing Your Own Bills

### What Documents Work Best?

✅ **Medical Bills** - Procedure bills with CPT codes  
✅ **Dental Bills** - Treatment bills with CDT codes  
✅ **Pharmacy Receipts** - Prescription receipts  
✅ **EOBs** - Explanation of Benefits from insurance  
✅ **FSA/HSA Statements** - Claim history reports  

### How to Prepare Your Document:

1. **Open your bill** (PDF, online portal, or paper copy)
2. **Copy all the text** (Ctrl+A / Cmd+A, then Ctrl+C / Cmd+C)
3. **Paste into medBillDozer** (in the "Document Input #1" box)
4. **Click "Analyze"**

### Pro Tips:

- ✅ Include **everything** - headers, line items, totals, fine print
- ✅ Use **multiple documents** for cross-document duplicate detection
- ✅ Keep **dates and codes** intact (they're critical for analysis)
- ❌ Don't edit or summarize - paste the complete text

---

## 🎯 Choosing an AI Provider

### Quick Comparison:

| Provider | Speed | Accuracy | Privacy | Cost | Best For |
|----------|-------|----------|---------|------|----------|
| **OpenAI GPT** | Medium | ⭐⭐⭐⭐⭐ | Medium | $$ | Complex medical bills |
| **Google Gemini** | Fast | ⭐⭐⭐⭐ | Medium | $ | Standard bills |
| **MedGemma** | Medium | ⭐⭐⭐⭐ | Medium | $ | Medical-specific content |
| **Local Heuristic** | Very Fast | ⭐⭐ | ⭐⭐⭐⭐⭐ | Free | Simple pattern matching |

### Recommendation:

- **First time?** Use **OpenAI GPT** for best results
- **Privacy concerned?** Use **Local Heuristic** (no external API)
- **Budget conscious?** Use **Google Gemini** (cheaper)
- **Medical specialist?** Use **MedGemma** (trained on medical data)

---

## 🔒 Privacy & Security

### Your data is safe:

✅ **No storage** - Documents are never saved to disk  
✅ **No database** - No user accounts or data retention  
✅ **No tracking** - We don't collect usage data  
✅ **Session-only** - Everything clears when you close the tab  

### Where does data go?

- **Your chosen AI provider** receives document text for analysis
- **That's it!** No other third parties

### For maximum privacy:

1. Use **"Local Heuristic"** provider (100% local, no API calls)
2. Or **redact** personal info before pasting (names, SSN, account numbers)
3. Use **private browsing mode** (incognito)

---

## ❓ Common Questions

### "How accurate is this?"

medBillDozer uses state-of-the-art AI models, but:
- ✅ Good at catching **obvious errors** (duplicates, math mistakes)
- ⚠️ May **miss subtle issues** or flag false positives
- ❌ Cannot know **your specific insurance plan details**

**Always verify findings** with your insurance company!

### "Can I trust the savings amounts?"

The savings shown are **maximum potential**, not guaranteed:
- Requires verification with insurance
- Subject to your plan's terms
- May need provider cooperation
- Could take time to resolve

Think of it as: **"Up to $XXX if all issues are valid and resolved"**

### "What if no issues are found?"

That's great! It could mean:
- ✅ Your bill is accurate
- ✅ No obvious errors detected
- ℹ️ Or the AI couldn't parse the format (try a different provider)

### "Is this HIPAA compliant?"

**No** - medBillDozer is a demo application, not a HIPAA-covered service.
- Safe for personal use
- Not for healthcare providers to use on patient data
- See full privacy policy in the app

---

## 🆘 Troubleshooting

### "API key error"

**Solution:** Set the environment variable for your chosen provider (see step 2 above), or switch to "Local Heuristic"

### "Analysis failed"

**Try:**
1. Check internet connection
2. Verify document text pasted correctly
3. Try a different AI provider
4. Reduce document length

### "No issues found"

**Try:**
1. Verify complete text was pasted
2. Try a different AI provider (OpenAI is most thorough)
3. Check that your document may actually be correct!

### "Stuck on privacy dialog"

**Solution:** Check the "I agree" box before clicking "Accept"

---

## 📚 Learn More

- **Full User Guide**: See `docs/USER_GUIDE.md` for comprehensive documentation
- **Technical Docs**: See `docs/MODULES.md` for developer documentation
- **API Reference**: See `docs/API.md` for code documentation

---

## ⚖️ Important Disclaimer

medBillDozer is an **educational tool only**. It is NOT:
- ❌ Medical, legal, or financial advice
- ❌ A substitute for professional billing review
- ❌ A guarantee of savings or outcomes
- ❌ HIPAA-compliant healthcare software

**Always consult qualified professionals** for:
- Medical billing disputes
- Insurance coverage questions
- Legal matters
- Financial planning

---

## 🎉 Ready to Go!

You're all set! Here's what to do next:

1. ✅ Launch the app: `streamlit run app.py`
2. ✅ Try a demo document
3. ✅ Analyze your own bills
4. ✅ Save money! 💰

**Questions?** Check the full user guide in `docs/USER_GUIDE.md`

---

**Happy bill auditing!** 🏥📊💪
