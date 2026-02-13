# Troubleshooting Guide

**Having issues? We've got you covered!**

---

## 🔍 Quick Diagnostic

**Choose your problem:**

1. [App won't start](#app-wont-start)
2. [Analysis fails or errors](#analysis-fails-or-errors)
3. [No results or empty results](#no-results-or-empty-results)
4. [API key issues](#api-key-issues)
5. [Slow performance](#slow-performance)
6. [Results don't make sense](#results-dont-make-sense)
7. [UI issues / blank page](#ui-issues--blank-page)

---

## 🚫 App Won't Start

### Symptoms:
- Command fails
- Import errors
- Dependency errors

### Solutions:

#### 1. Check Python Version
```bash
python3 --version
```
**Need:** Python 3.9 or higher

#### 2. Reinstall Dependencies
```bash
pip install -r requirements.txt --upgrade
```

#### 3. Try Clean Install
```bash
pip uninstall streamlit
pip cache purge
pip install -r requirements.txt
```

#### 4. Check for Port Conflicts
```bash
# Kill existing Streamlit processes
pkill -f streamlit
# Or use different port
streamlit run medBillDozer.py --server.port 8502
```

---

## ❌ Analysis Fails or Errors

### Symptoms:
- "Analysis failed" message
- Error messages during analysis
- Crashes during processing

### Common Causes & Fixes:

### **Error: "API key not found"**

**Solution:**
```bash
# For MedGemma
export HF_TOKEN="your-token-here"
export HF_MODEL_ID="google/medgemma-4b-it"

# For OpenAI
export OPENAI_API_KEY="your-key-here"

# For Gemini
export GOOGLE_API_KEY="your-key-here"
```

Or use **Local Heuristic** (no key needed)!

---

### **Error: "Rate limit exceeded"**

**Cause:** Too many API requests  
**Solution:**
- Wait 60 seconds and try again
- Check your API provider's rate limits
- Consider upgrading API plan

---

### **Error: "JSON parsing failed"**

**Cause:** AI returned malformed response  
**Solution:**
- Try different AI provider
- Simplify your input (remove special characters)
- Use shorter text
- Try again (sometimes it's temporary)

---

### **Error: "Context length exceeded"**

**Cause:** Document too long for AI model  
**Solution:**
- Split document into sections
- Remove unnecessary text
- Analyze one page at a time

---

## 📭 No Results or Empty Results

### Symptoms:
- Analysis completes but no issues found
- Empty results page
- Only see "No issues detected"

### Possible Reasons:

### 1. **Clean Bill (Unlikely but possible!)**
- Some bills truly have no errors
- Try different document to test

### 2. **AI Provider Limitations**
**Solution:** Try different provider:
- Local Heuristic → Try MedGemma
- MedGemma → Try GPT-4
- GPT-4 → Try Gemini

### 3. **Input Format Issues**
**Check:**
- [ ] Text is readable (not garbled)
- [ ] Contains line items with amounts
- [ ] Has dates and descriptions
- [ ] Includes CPT/CDT codes (if available)

**Fix:** Add more structure:
```
Better format:
Date: 01/15/2026
Service: Office Visit
CPT: 99213
Billed: $150.00
Patient Pays: $30.00
```

---

## 🔑 API Key Issues

### **Issue: "Invalid API key"**

#### For MedGemma (Hugging Face):
1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create new token with "Read" permission
3. Copy and export:
   ```bash
   export HF_TOKEN="hf_xxxxxxxxxxxxx"
   ```

#### For OpenAI:
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create new secret key
3. Copy and export:
   ```bash
   export OPENAI_API_KEY="sk-xxxxxxxxxxxxx"
   ```

#### For Google Gemini:
1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Create API key
3. Copy and export:
   ```bash
   export GOOGLE_API_KEY="AIzaxxxxxxxxxxxxx"
   ```

### **Issue: "Quota exceeded"**

**Solution:**
- Check your API provider's dashboard
- Verify billing is set up
- Upgrade plan if needed
- Wait for quota reset (usually monthly)

---

## 🐌 Slow Performance

### Analysis taking >60 seconds?

### Causes & Fixes:

#### 1. **Large Document**
- **Solution:** Break into smaller chunks
- Analyze one page at a time

#### 2. **Slow API Provider**
- **Solution:** Try different provider
- MedGemma often faster than GPT-4

#### 3. **Network Issues**
- **Solution:** Check internet connection
- Try again during off-peak hours

#### 4. **Cold Start (First Use)**
- **Solution:** First analysis may be slow
- Subsequent analyses will be faster

---

## 🤔 Results Don't Make Sense

### Symptoms:
- Issues don't match document
- Hallucinated charges
- Wrong amounts

### Causes & Fixes:

### **1. AI Hallucination**
**Symptoms:**
- Mentions charges not in document
- Makes up CPT codes

**Solution:**
- Try more conservative provider (MedGemma)
- Check evidence field - if vague, ignore
- Use different AI model

### **2. Context Confusion**
**Symptoms:**
- Mixes up line items
- Wrong date associations

**Solution:**
- Simplify document format
- Remove extra whitespace
- Clear formatting

### **3. Language/OCR Issues**
**Symptoms:**
- Misreads numbers
- Wrong interpretations

**Solution:**
- Clean up document text
- Fix obvious OCR errors (0 vs O, 1 vs l)
- Add clear labels

---

## 🖥️ UI Issues / Blank Page

### **Issue: Sidebar links open blank page**

**Solution:**
- Use the in-app documentation viewer
- Click "📖 Open in Sidebar" button instead of direct links
- Check that docs exist: `ls docs/`

### **Issue: Page won't load**

**Solution:**
```bash
# Clear Streamlit cache
streamlit cache clear
# Restart app
streamlit run medBillDozer.py
```

### **Issue: Buttons don't work**

**Solution:**
- Refresh page (Cmd+R or Ctrl+R)
- Clear browser cache
- Try different browser

---

## 🔧 Advanced Troubleshooting

### Enable Debug Mode

```bash
# Run with verbose logging
streamlit run medBillDozer.py --logger.level=debug
```

### Check Logs

Look for error messages in terminal where you ran the app.

### Test API Connection

```python
# Test HuggingFace
import os
from huggingface_hub import InferenceClient
client = InferenceClient(token=os.getenv("HF_TOKEN"))
print("Connected!")

# Test OpenAI
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("Connected!")
```

---

## 🆘 Still Having Issues?

### 1. **Check GitHub Issues**
- [github.com/boobootoo2/medbilldozer/issues](https://github.com/boobootoo2/medbilldozer/issues)
- Search for your problem
- See if others have solutions

### 2. **Create New Issue**
Include:
- Error message (full text)
- Steps to reproduce
- Python version (`python3 --version`)
- OS (Mac, Windows, Linux)
- Which AI provider you're using

### 3. **Workarounds**

**Can't get any AI working?**
- Use **Local Heuristic** mode (no API needed)
- Limited but works offline

**Need immediate help?**
- Ask the AI assistant in the sidebar
- Type your exact problem

---

## ✅ Preventive Maintenance

### Keep Your System Healthy:

#### 1. **Update Regularly**
```bash
git pull
pip install -r requirements.txt --upgrade
```

#### 2. **Clear Cache Periodically**
```bash
streamlit cache clear
pip cache purge
```

#### 3. **Monitor API Usage**
- Check your API provider dashboards
- Set up usage alerts
- Track spending

#### 4. **Backup Important Results**
- Download JSON reports
- Save to local drive
- Don't rely on session state

---

## 📋 Troubleshooting Checklist

Before asking for help, try:

- [ ] Restart the app
- [ ] Clear Streamlit cache
- [ ] Check API keys are exported
- [ ] Try different AI provider
- [ ] Test with demo document
- [ ] Check internet connection
- [ ] Update dependencies
- [ ] Read error message carefully
- [ ] Search GitHub issues
- [ ] Try Local Heuristic mode

---

## 💡 Common Mistakes

### ❌ Don't Do This:
- Set API key in code (security risk!)
- Paste PHI into public forums
- Ignore error messages
- Use outdated Python (<3.9)
- Mix different virtual environments

### ✅ Do This Instead:
- Export keys as environment variables
- Redact sensitive info before sharing
- Read errors carefully
- Keep Python updated
- Use clean environment

---

**Remember:** 90% of issues are API key problems or network issues. Check those first! 🔑

**Still stuck?** Ask the AI assistant in the sidebar - it can help troubleshoot your specific issue!
