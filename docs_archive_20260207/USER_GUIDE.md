# medBillDozer User Guide

**Version:** 1.0
**Last Updated:** January 21, 2026

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Using the Application](#using-the-application)
4. [Understanding Results](#understanding-results)
5. [Privacy & Data Security](#privacy--data-security)
6. [Sample Documents](#sample-documents)
7. [Tips & Best Practices](#tips--best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Important Disclaimers](#important-disclaimers)

---

## Introduction

### What is medBillDozer?

**medBillDozer** is an AI-powered assistant designed to help patients audit their medical bills, Explanations of Benefits (EOBs), dental bills, pharmacy receipts, and FSA/HSA claim statements. The application automatically:

- ✅ Detects duplicate charges and billing errors
- ✅ Identifies math inconsistencies and calculation errors
- ✅ Highlights potential coverage mismatches
- ✅ Flags unusual or questionable charges
- ✅ Calculates potential savings opportunities
- ✅ Generates patient-friendly dispute checklists

### Who Should Use This?

medBillDozer is designed for:

- **Patients** reviewing medical, dental, or pharmacy bills
- **Insurance subscribers** checking Explanation of Benefits (EOB) statements
- **FSA/HSA participants** auditing claim histories
- **Healthcare advocates** helping others understand billing
- **Anyone** who wants to verify their healthcare charges are accurate

### What Makes It Different?

- 🔒 **Privacy-First**: No data is stored, collected, or transmitted to external servers
- 🤖 **AI-Powered**: Uses advanced language models trained on medical billing patterns
- 📊 **Multi-Document Analysis**: Compare multiple bills to find cross-document duplicates
- 💰 **Savings Calculator**: Quantifies potential dollar savings from each issue
- 📝 **Plain Language**: Explains complex billing issues in easy-to-understand terms

---

## Getting Started

### System Requirements

- **Web Browser**: Chrome, Firefox, Safari, or Edge (latest version)
- **Internet Connection**: Required for initial load and AI analysis
- **Screen Resolution**: 1280x720 or higher recommended

### First Time Setup

1. **Launch the Application**
   ```bash
   streamlit run medBillDozer.py
   ```
   The application will open in your default web browser at `http://localhost:8501`

2. **Review Privacy Policy**
   - On first visit, you'll see a privacy & cookie preferences dialog
   - Read the disclaimer and privacy policy
   - Check "I agree" to accept the privacy terms
   - Optionally configure cookie preferences:
     - **Essential Cookies** (Required): Enable core functionality
     - **Preference Cookies** (Optional): Remember your UI settings
     - **Analytics Cookies** (Optional): Help improve the application
   - Click "Accept" to continue

3. **Choose Your AI Provider**
   - Select your preferred AI analysis provider from the dropdown:
     - **OpenAI (GPT)**: Most accurate, requires OpenAI API key
     - **Google Gemini**: Fast and reliable, requires Google AI API key
     - **MedGemma**: Medical-specialized model, requires Hugging Face setup
     - **Local Heuristic**: No API required, basic pattern matching

4. **You're Ready!**
   - The main interface will load with demo documents and input area

---

## Using the Application

### Step 1: Prepare Your Document

medBillDozer accepts text from any healthcare billing document. You can:

#### Option A: Use Demo Documents

Perfect for first-time users to see how the system works:

1. Scroll to the **"Try Demo Documents"** section
2. Click the checkbox next to any demo document:
   - 🏥 **Colonoscopy Bill** - Medical procedure with duplicate charges
   - 🦷 **Dental Crown Bill** - Dental treatment with coverage issues
   - 💊 **Pharmacy Receipt** - FSA-eligible prescription purchase
   - 📋 **Insurance Claim (Zero OOP)** - EOB with $0 patient responsibility
   - 🏦 **FSA Claim History** - Flexible spending account statement
3. Selected document will automatically populate in the input area
4. You can select multiple demo documents for cross-document analysis

#### Option B: Paste Your Own Document

For analyzing your real bills:

1. **Obtain the Document**:
   - Open your bill PDF, EOB, or online statement
   - Copy all the text (Ctrl+A / Cmd+A, then Ctrl+C / Cmd+C)
   - Or screenshot and use OCR to extract text

2. **Prepare the Text**:
   - Include all visible information: headers, line items, totals, dates
   - Keep formatting intact if possible (tables, line breaks)
   - Remove any personally identifying information if desired (optional - data stays local)

3. **Paste into medBillDozer**:
   - Click in the **"Document Input #1"** text area
   - Paste your document text (Ctrl+V / Cmd+V)
   - The text area will expand automatically

4. **Add More Documents** (Optional):
   - Click **"+ Add another document"** to compare multiple bills
   - Paste additional documents in the new text areas
   - Great for finding duplicate charges across multiple statements

### Step 2: Run the Analysis

1. **Review Your Input**
   - Verify all documents are pasted correctly
   - Check that important details are visible (dates, amounts, provider names)

2. **Click "Analyze with medBillDozer"**
   - Large blue button at the bottom of the input section
   - Processing typically takes 5-30 seconds depending on:
     - Number of documents
     - Document length
     - Selected AI provider
     - API response time

3. **Wait for Analysis**
   - Progress indicator shows analysis is running
   - Do not refresh the page during analysis
   - Multi-document analysis may take longer

### Step 3: Review Results

After analysis completes, you'll see comprehensive results organized into sections.

---

## Understanding Results

### Results Overview Section

The top of the results shows a summary card:

```
✅ Analysis complete
Analyzed X document(s)
Provider: [Your selected AI model]
```

### Savings Summary

The most important section - shows potential dollar savings:

#### 💰 Total Potential Savings

Displays the total maximum savings across all documents:

```
💰 Total Potential Savings: $XXX.XX

Per-Document Breakdown:
• Document 1 (Medical Bill): $XX.XX
• Document 2 (Dental Bill): $XX.XX
```

**What this means**: This is the maximum amount you could potentially save if all identified issues are valid billing errors that can be successfully disputed.

**Important**: This is a *potential maximum*, not a guarantee. Actual savings depend on:
- Verification with your insurance company
- Provider willingness to adjust charges
- Contractual agreements and coverage terms

### Issues Found

Each document gets its own analysis section:

#### Document Header

```
📄 Document #1: Medical Bill - Provider Name
Date of Service: January 15, 2026
Patient: [Name if available]
```

#### Issue Cards

Each identified issue appears as a card with:

**1. Issue Type Badge**
- `🔴 duplicate_charge` - Same service billed multiple times
- `🟡 math_error` - Calculation doesn't add up correctly
- `🟠 coverage_mismatch` - Insurance coverage seems incorrect
- `🔵 unusual_charge` - Charge amount is suspicious
- `⚪ administrative_issue` - Paperwork or processing problem

**2. Issue Summary**
Clear, plain-language description of what's wrong:
```
"Duplicate medical procedure billed"
```

**3. Evidence**
Specific details from your document that support this issue:
```
"CPT 45378 appears more than once on 01/15/2026
with patient responsibility $250.00"
```

**4. Recommended Action**
What you should do about this issue:
```
"Contact billing department and request removal of duplicate charge.
Reference CPT code and date of service."
```

**5. Potential Savings**
Dollar amount you might save:
```
💰 Max Savings: $250.00
```

**6. Confidence Level** (when available)
How certain the AI is about this issue:
- `High (90%+)`: Very likely a real error
- `Medium (60-89%)`: Probable issue, worth investigating
- `Low (<60%)`: Possible concern, may need expert review

**7. Issue Source**
How this issue was detected:
- `deterministic`: Found by rule-based logic (high confidence)
- `llm`: Identified by AI analysis (review recommended)

### Coverage Matrix (Multi-Document)

When analyzing multiple documents, you'll see a coverage matrix showing which facts were extracted from each document:

```
📊 Cross-Document Coverage

                        Doc 1    Doc 2    Doc 3
Patient Name            ✓        ✓        ✓
Date of Service         ✓        ✓        ✗
Provider Name           ✓        ✓        ✓
Total Amount            ✓        ✗        ✓
Patient Responsibility  ✓        ✓        ✓
```

**What this shows**:
- ✓ = Information found in this document
- ✗ = Information missing or not detected
- Helps identify incomplete documents or extraction issues

### Line Item Details

For medical and dental bills, expanded sections show parsed line items:

```
📋 Medical Line Items (3 found)

1. CPT 45378 - Colonoscopy
   Date: 01/15/2026
   Billed: $1,250.00
   Allowed: $800.00
   Patient Responsibility: $250.00

2. CPT 45380 - Colonoscopy with biopsy
   Date: 01/15/2026
   Billed: $450.00
   Allowed: $300.00
   Patient Responsibility: $100.00
```

### Copy to Clipboard

Each document section has a **"Copy Full Analysis"** button:
- Click to copy all issues and details to clipboard
- Perfect for emailing to your insurance company
- Includes formatted text ready to paste

---

## Privacy & Data Security

### Your Data is Safe

medBillDozer is designed with privacy as the #1 priority:

#### ✅ What We DO:
- Process your documents **locally in your browser session**
- Send document text to your chosen AI provider for analysis
- Store cookie preferences **only in your browser**
- Clear all data when you close the browser tab

#### ❌ What We DON'T DO:
- We do **NOT** store your medical bills on any server
- We do **NOT** save your personal health information
- We do **NOT** transmit data to third parties (except your chosen AI provider)
- We do **NOT** create user accounts or databases
- We do **NOT** track or profile users

### HIPAA Compliance Notice

**Important**: medBillDozer is a demonstration application and is **not a HIPAA-covered service**.

- This tool is for educational and informational purposes
- It does not create a healthcare provider-patient relationship
- It does not provide medical, legal, or financial advice
- For HIPAA-compliant billing review, consult your healthcare provider or a professional medical billing advocate

### Cookie Policy

medBillDozer uses cookies for three purposes:

1. **Essential Cookies** (Required)
   - Session management
   - Privacy preferences
   - Cannot be disabled

2. **Preference Cookies** (Optional)
   - UI theme and layout settings
   - AI provider selection
   - Can be disabled in privacy settings

3. **Analytics Cookies** (Optional)
   - Usage patterns (anonymous)
   - Performance metrics
   - Can be disabled in privacy settings

To change cookie preferences:
1. Click the settings icon in the sidebar
2. Select "Privacy Preferences"
3. Toggle cookie categories on/off
4. Click "Save Preferences"

### AI Provider Data Policies

When you analyze documents, the text is sent to your selected AI provider:

- **OpenAI (GPT)**: Subject to [OpenAI's privacy policy](https://openai.com/privacy)
- **Google Gemini**: Subject to [Google's privacy policy](https://policies.google.com/privacy)
- **MedGemma**: Hosted on Hugging Face, check your deployment's data policy
- **Local Heuristic**: No external API calls, 100% local processing

**Recommendation**: For maximum privacy, use the "Local Heuristic" provider, though it has limited detection capabilities.

---

## Sample Documents

medBillDozer includes 5 realistic demo documents for testing:

### 🏥 Colonoscopy Bill

**Document Type**: Medical Procedure Bill
**Key Features**:
- Multiple CPT codes
- Insurance adjustments
- Patient responsibility calculations

**Common Issues Detected**:
- Duplicate procedure charges
- Math errors in totals
- Coverage verification needed

**Best For**: Learning how medical procedure analysis works

---

### 🦷 Dental Crown Bill

**Document Type**: Dental Treatment Bill
**Key Features**:
- CDT dental procedure codes
- Insurance coverage breakdown
- Out-of-pocket costs

**Common Issues Detected**:
- Coverage percentage discrepancies
- Unusual fee amounts
- Documentation requirements

**Best For**: Understanding dental billing review

---

### 💊 Pharmacy Receipt (FSA)

**Document Type**: Prescription Receipt
**Key Features**:
- Medication details
- FSA/HSA eligible markers
- Copay amounts

**Common Issues Detected**:
- FSA eligibility verification
- Copay vs. insurance coordination
- Pricing inconsistencies

**Best For**: FSA/HSA claim preparation

---

### 📋 Insurance Claim (Zero OOP)

**Document Type**: Explanation of Benefits (EOB)
**Key Features**:
- Insurance payment details
- Zero patient responsibility
- Claim processing dates

**Common Issues Detected**:
- Coordination of benefits questions
- Deductible application
- Network status verification

**Best For**: Learning EOB analysis

---

### 🏦 FSA Claim History

**Document Type**: FSA Transaction Statement
**Key Features**:
- Multiple claim entries
- Approval/denial status
- Reimbursement amounts

**Common Issues Detected**:
- Denied claims needing documentation
- Duplicate submissions
- Eligibility date mismatches

**Best For**: FSA/HSA account reconciliation

---

## Tips & Best Practices

### For Best Results

#### ✅ DO:

1. **Include Complete Information**
   - Copy the entire document, including headers and footers
   - Include all line items, codes, and amounts
   - Keep dates, provider names, and patient information

2. **Use High-Quality Text**
   - Copy text directly from PDFs when possible
   - If using OCR, verify text is accurate
   - Fix obvious OCR errors (like "0" vs "O")

3. **Analyze Related Documents Together**
   - Upload multiple EOBs from the same treatment
   - Compare original bill with EOB
   - Include follow-up statements

4. **Review Results Carefully**
   - Read each issue's evidence section
   - Check recommended actions
   - Verify amounts against your original documents

5. **Follow Up on Findings**
   - Contact billing departments promptly
   - Reference specific CPT/CDT codes and dates
   - Keep records of all communications

#### ❌ DON'T:

1. **Don't Rely Solely on AI**
   - Always verify findings with original documents
   - Consult insurance company for coverage questions
   - Consider professional billing advocate for complex cases

2. **Don't Assume All Issues Are Errors**
   - Some "issues" may be correct based on your plan
   - Insurance coordination can be complex
   - Deductibles and coinsurance vary by plan

3. **Don't Ignore Context**
   - Some charges may be legitimate despite appearing duplicate
   - Billing codes have specific meanings
   - Provider contracts affect allowed amounts

4. **Don't Share Sensitive Data Carelessly**
   - Redact SSN and account numbers if desired
   - Be aware of your chosen AI provider's data policy
   - Use Local Heuristic for maximum privacy

### Maximizing Savings Detection

1. **Multi-Document Analysis**
   - Upload all related bills from the same provider
   - Include EOBs and original bills together
   - Compare multiple dates of service

2. **Complete Text Extraction**
   - Longer documents provide more context
   - Include itemized line items
   - Don't skip fine print or notes sections

3. **Choose the Right AI Provider**
   - OpenAI GPT: Best for complex medical terminology
   - Google Gemini: Fast and good for standard bills
   - MedGemma: Specialized in medical content
   - Local Heuristic: Basic but private

### Understanding False Positives

The AI may occasionally flag items that aren't actually errors:

**Common False Positives**:
- Separate procedures on same day (not duplicates)
- Pre-authorization vs. actual claim (different events)
- Coordination of benefits (appears as coverage issue)
- Bundled services (may look like unusual pricing)

**How to Verify**:
1. Check the evidence section carefully
2. Compare with your insurance plan details
3. Call your insurance company for clarification
4. Review provider's itemized statement

---

## Troubleshooting

### Common Issues and Solutions

#### "Analysis is taking too long"

**Possible Causes**:
- Large document or multiple documents
- Slow AI provider API response
- Internet connection issues

**Solutions**:
1. Wait up to 60 seconds for complex analyses
2. Try a faster AI provider (Gemini is typically quickest)
3. Check your internet connection
4. Reduce number of documents or document length

---

#### "No issues found"

**Possible Causes**:
- Document may be correct
- Text extraction was incomplete
- AI provider couldn't parse the format

**Solutions**:
1. Verify complete text was pasted
2. Try a different AI provider
3. Check that numbers and dates are clearly visible
4. Consider that the bill may actually be correct

---

#### "Error: API key not configured"

**Cause**: Selected AI provider requires an API key that isn't set

**Solution**:
1. Set environment variable for your chosen provider:
   - OpenAI: `OPENAI_API_KEY=your_key_here`
   - Gemini: `GOOGLE_API_KEY=your_key_here`
   - MedGemma: `HF_TOKEN=your_token_here`
2. Restart the application
3. Or switch to "Local Heuristic" (no API key needed)

---

#### "Privacy dialog won't close"

**Cause**: Must check "I agree" before proceeding

**Solution**:
1. Check the "I agree" checkbox
2. Click "Accept" button
3. If still stuck, clear browser cache and reload

---

#### "Document text disappeared"

**Cause**: Session state may have been cleared

**Solutions**:
1. Don't refresh the page during analysis
2. Re-paste your document text
3. Consider copying text to a file as backup before analyzing

---

#### "Copy button doesn't work"

**Cause**: Browser clipboard permissions

**Solutions**:
1. Allow clipboard access when browser prompts
2. Manually select and copy text instead
3. Try a different browser

---

#### "Savings amount seems wrong"

**Possible Causes**:
- AI misinterpreted amounts
- Didn't account for insurance payments
- Sum of potential savings, not guaranteed savings

**Solutions**:
1. Read the evidence section for each issue
2. Verify amounts against original document
3. Remember: "max potential" is theoretical maximum
4. Contact your insurance company for actual amounts

---

## Important Disclaimers

### ⚠️ Not Medical or Legal Advice

medBillDozer is an **educational tool only**. It does NOT provide:

- ❌ Medical advice or diagnosis
- ❌ Legal advice or representation
- ❌ Financial advice or planning
- ❌ Insurance coverage determinations
- ❌ Guaranteed savings or outcomes

**Always consult qualified professionals** for:
- Medical billing disputes
- Insurance coverage questions
- Legal rights and obligations
- Healthcare financial planning

### ⚠️ Prototype Status

This is a **demonstration application** created for the MedGemma Impact Challenge:

- Built for educational purposes
- Not intended for production healthcare use
- May contain bugs or inaccuracies
- No warranty or guarantee of results
- Use at your own risk

### ⚠️ AI Limitations

Artificial Intelligence has inherent limitations:

- **May generate false positives**: Flag correct charges as errors
- **May miss real errors**: Not all mistakes will be detected
- **Depends on input quality**: Garbage in = garbage out
- **Lacks context**: Doesn't know your specific insurance plan
- **Probabilistic, not deterministic**: Makes educated guesses

**Always verify AI findings** with:
- Your insurance company
- Healthcare provider's billing department
- Professional medical billing advocate
- Your plan's coverage documents

### ⚠️ Privacy Considerations

While medBillDozer doesn't store your data:

- **AI providers receive your document text**: Check their privacy policies
- **Browser history may retain data**: Use private/incognito mode if concerned
- **No encryption in transit to AI APIs**: Standard HTTPS only
- **Not HIPAA compliant**: Not suitable for covered entities

For maximum privacy:
- Use "Local Heuristic" provider
- Redact personal information before analysis
- Clear browser data after use
- Don't analyze documents on public/shared computers

### ⚠️ Financial Outcomes

Savings estimates are **theoretical maximums only**:

- Not a guarantee of actual savings
- Requires successful dispute resolution
- Subject to insurance policy terms
- May require provider agreement
- Could take weeks or months to realize

**Do not make financial decisions** based solely on medBillDozer analysis.

---

## Getting Help

### Resources

- **Documentation**: See `docs/` folder for technical documentation
- **Issues**: Report bugs on the GitHub repository
- **Updates**: Check repository for latest version

### Contact

This is an open-source demonstration project. For:

- **Technical issues**: Open a GitHub issue
- **Billing advice**: Contact a professional medical billing advocate
- **Insurance questions**: Contact your insurance company directly
- **Medical concerns**: Consult your healthcare provider

### Professional Help

For complex billing issues, consider consulting:

- **Medical Billing Advocates**: Professional billing reviewers
- **Patient Advocates**: Hospital or insurance ombudsmen
- **Healthcare Attorneys**: For legal billing disputes
- **Financial Counselors**: For healthcare payment planning

---

## Version History

### v1.0 (January 2026)
- Initial release for MedGemma Impact Challenge
- Multi-document analysis support
- 5 demo documents included
- OpenAI, Gemini, and MedGemma provider support
- Privacy-first architecture
- Deterministic + LLM hybrid analysis

---

**Thank you for using medBillDozer!**
*Helping patients understand and verify their healthcare charges.*

🏥 **Stay healthy, stay informed, pay fairly.** 💰

