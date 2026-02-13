# Privacy & Data Security

**Your privacy is our top priority.**

---

## 🔒 What Data Do We Collect?

### Short Answer: **Nothing is stored permanently!**

When you use medBillDozer:

✅ **Your bills stay on your device**  
✅ **No data sent to our servers**  
✅ **No account registration required**  
✅ **No tracking or analytics**

---

## 🔐 How Your Data is Used

### During Analysis:

1. **You paste or type your bill** → Stays in your browser's memory
2. **Click "Analyze"** → Sent directly to the AI provider YOU chose
3. **Results displayed** → Shown in your browser only
4. **Close the app** → All data cleared from memory

**We are just the middleman** - your data goes directly to the AI provider you select (OpenAI, Google, or Hugging Face).

---

## 🏥 HIPAA & Medical Privacy

### Important Disclaimers:

⚠️ **This is NOT a HIPAA-compliant system**
- medBillDozer is a consumer tool, not a healthcare provider
- Not designed for healthcare providers or covered entities

⚠️ **Protect Your PHI (Protected Health Information)**
- Remove patient names before analysis (optional but recommended)
- Remove Social Security Numbers
- Remove medical record numbers

**Why?** Even though we don't store data, the AI providers (OpenAI, Google, HuggingFace) may temporarily process it according to their own privacy policies.

---

## 🤝 Third-Party AI Providers

When you analyze a bill, it's sent to one of these providers:

### **MedGemma via Hugging Face**
- Privacy Policy: [huggingface.co/privacy](https://huggingface.co/privacy)
- Data Retention: Per their policy
- Control: You control API key

### **GPT-4 via OpenAI**
- Privacy Policy: [openai.com/privacy](https://openai.com/privacy)
- Data Retention: 30 days for API calls
- Control: You control API key

### **Gemini via Google**
- Privacy Policy: [google.com/privacy](https://google.com/privacy)
- Data Retention: Per their policy
- Control: You control API key

### **Local Heuristic (No AI)**
- No external API used
- All processing local
- No data leaves your device

**Want maximum privacy?** Use **Local Heuristic** mode!

---

## 🛡️ What We Do to Protect You

### Security Measures:

✅ **No Server-Side Storage**
- We don't run databases
- Nothing saved to disk
- No user accounts or logins

✅ **Session-Only Memory**
- Data exists only while app is open
- Cleared when you refresh or close
- No cookies or local storage

✅ **Encrypted Connections**
- All API calls use HTTPS
- Secure communication with AI providers

✅ **Input Sanitization**
- Remove dangerous code patterns
- Prevent injection attacks
- Validate all inputs

✅ **Open Source**
- Full code available on GitHub
- Community reviewed
- Transparent operations

---

## 🎯 Best Practices for Privacy

### Before You Upload:

1. **Redact Personal Info** (optional)
   - Patient names
   - Social Security Numbers
   - Medical Record Numbers
   - Addresses

2. **Keep Financial Details**
   - CPT codes, amounts, dates are needed
   - Provider names help the analysis

3. **Save Results Locally**
   - Download JSON reports to your device
   - Don't share screenshots with PHI

### What to Keep:
✅ Charges, amounts, dates  
✅ CPT/CDT codes  
✅ Provider names  
✅ Service descriptions

### What to Redact:
❌ Patient full name (use initials if needed)  
❌ SSN, Medical Record #  
❌ Addresses  
❌ Insurance ID numbers (unless needed for analysis)

---

## 📋 Our Privacy Commitments

### We Promise:

1. ✅ **No Data Sale or Sharing**
   - We never sell your data
   - We don't share with third parties
   - We don't use it for advertising

2. ✅ **No Profiling or Tracking**
   - No user accounts
   - No behavior tracking
   - No analytics collection

3. ✅ **Transparent Operations**
   - Open source code
   - Clear documentation
   - No hidden features

4. ✅ **You Are In Control**
   - Choose your AI provider
   - Delete data anytime (refresh page)
   - Use offline mode (Local Heuristic)

---

## ⚖️ Legal & Regulatory

### Disclaimers:

**Not a Covered Entity**
- medBillDozer is not a healthcare provider
- Not subject to HIPAA regulations
- Not providing medical or legal advice

**User Responsibility**
- You control what data you input
- You choose the AI provider
- You own your results

**No Warranty**
- Tool provided "as-is"
- No guarantees of accuracy
- User assumes all risk

---

## 🆘 Privacy Questions?

### Common Questions:

**Q: Can I use this at work (healthcare facility)?**  
A: No! This is for consumer/patient use only. Healthcare facilities should use HIPAA-compliant systems.

**Q: What if I accidentally pasted sensitive info?**  
A: Refresh the page to clear memory. The data was only sent to the AI provider you selected (per their policies).

**Q: How do I know you're not storing data?**  
A: Check our open-source code on GitHub! You can verify we have no database or storage systems.

**Q: Which AI provider is most private?**  
A: "Local Heuristic" keeps everything on your device. Otherwise, review each provider's privacy policy.

**Q: Can I run this completely offline?**  
A: Yes! Use "Local Heuristic" mode - no internet connection required for analysis.

---

## 📧 Contact & Concerns

For privacy concerns or questions:
- Review our code: [github.com/boobootoo2/medbilldozer](https://github.com/boobootoo2/medbilldozer)
- Check issues: [github.com/boobootoo2/medbilldozer/issues](https://github.com/boobootoo2/medbilldozer/issues)

---

**Last Updated:** February 13, 2026

**Remember:** When in doubt, redact personal information before analysis!
