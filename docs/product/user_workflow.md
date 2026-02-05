# User Workflow

medBillDozer provides an intuitive workflow for analyzing medical bills and detecting billing errors.

## Typical User Journey

### 1. First Launch

1. **Privacy Policy**: User accepts privacy policy (one-time)
2. **Guided Tour** (optional): Interactive walkthrough of key features
3. **Demo Documents**: Pre-loaded sample documents available

### 2. Setup (Optional)

Users can configure their profile for personalized analysis:

- **Identity**: Name, DOB, address
- **Insurance Plans**: Carrier, policy numbers, coverage details
- **Provider Directory**: Doctors, hospitals, pharmacies

Profile data enables:
- Deductible tracking
- Network status validation
- Provider cross-reference
- Historical analysis

### 3. Document Analysis

#### Option A: Demo Documents
- Select from pre-loaded examples:
  - 🏥 Colonoscopy Bill ($2,450 with known upcoding)
  - 🦷 Dental Cleaning ($285 with duplicate charge)
  - 💊 Pharmacy Receipt ($145 FSA claim)
- Click "Analyze with medBillDozer"
- Review detected issues and potential savings (typically 3-8 seconds)

#### Option B: Upload Own Documents
1. Copy text from PDF or image (use external OCR if needed)
2. Paste into document input area
3. Optionally add multiple documents for cross-document analysis
4. Click "Analyze with medBillDozer"
5. Wait for analysis to complete

### 4. Review Results

#### Issue Summary
Issues are organized by severity:

- 🔴 **High Severity**: Significant overcharges, fraud indicators ($100+)
- 🟡 **Medium Severity**: Policy violations, missing info ($20-$100)
- 🟢 **Low Severity**: Minor discrepancies, documentation issues (<$20)

Each issue includes:
- **Title**: Brief summary (e.g., "Duplicate Anesthesia Charge")
- **Explanation**: Plain-language description of the problem
- **Max Savings**: Estimated refund potential
- **Category**: Issue type (upcoding, duplicate, missing_info, etc.)
- **Affected Line Items**: Specific CPT/CDT codes or charges

#### Aggregate Savings
- **Total Potential Savings**: Sum across all issues
- **Deterministic Savings**: Rule-based detections (high confidence)
- **LLM Savings**: AI-detected issues (requires verification)

#### DAG Pipeline Visualization (Optional)
Expand "📊 Pipeline Workflow" to see:
- Document classification (medical bill, dental, pharmacy, etc.)
- Extractor selection (OpenAI, Gemini, local)
- Fact extraction statistics
- Line-item parsing results
- Analyzer choice and execution time
- Workflow UUID for reproducibility

#### Coverage Matrix (Multiple Documents)
When analyzing multiple documents:
- Cross-document transaction matching
- Insurance plan application
- Duplicate charge detection across documents
- Aggregate savings across all documents

### 5. Take Action

Based on detected issues:

#### 🔴 High Severity Issues
1. **Call Provider**: Question specific charges immediately
2. **Request Itemized Bill**: Get detailed breakdown
3. **File Formal Dispute**: Submit written objection
4. **Report to Insurance**: Notify carrier of suspected fraud

#### 🟡 Medium Severity Issues
1. **Verify Coverage**: Check insurance plan documents
2. **Request Clarification**: Ask provider to explain charges
3. **Review Medical Records**: Confirm procedures performed
4. **Appeal if Denied**: Submit insurance appeal

#### 🟢 Low Severity Issues
1. **Document for Records**: Note discrepancies
2. **Request Correction**: Ask for billing adjustment
3. **Monitor Future Bills**: Watch for pattern

## Advanced Workflows

### Cross-Document Analysis

Analyze multiple related documents together:

1. Upload in sequence:
   - Original medical bill
   - Insurance Explanation of Benefits (EOB)
   - Payment receipt or remittance

2. System automatically:
   - Normalizes transactions across documents
   - Builds coverage matrix
   - Detects duplicate charges
   - Validates insurance payment calculations
   - Calculates aggregate savings

3. Review consolidated results:
   - See which bill corresponds to which EOB
   - Identify discrepancies between provider bill and insurance payment
   - Detect charges that appear on multiple documents

### Profile-Driven Analysis

Configure insurance plan for automated validation:

1. **Set Up Insurance Profile**:
   - Carrier name
   - Policy/group numbers
   - Deductible amount and amount met
   - Co-insurance percentage
   - Out-of-pocket maximum
   - In-network vs out-of-network rates

2. **Upload Bill or EOB**:
   - System validates against your plan

3. **Automatic Checks**:
   - Deductible application correct?
   - Co-insurance calculated properly?
   - Out-of-network penalties applied?
   - Annual limits enforced?

### Historical Analysis

Track bills over time:

1. **Persistence** (optional Supabase):
   - Enable cloud storage in settings
   - All analyses saved with timestamps

2. **Trend Detection**:
   - Recurring overcharges from same provider
   - Pattern of billing errors
   - Savings realized over time

3. **Export Reports**:
   - CSV export of all issues
   - Summary reports for tax purposes
   - FSA/HSA claim documentation

## Privacy Model

- **Local-First**: All analysis runs locally (no data leaves your machine by default)
- **No Account Required**: Use immediately without registration
- **Session-Based**: Data cleared when browser closes (unless persistence enabled)
- **Optional Cloud Sync**: Enable Supabase for cross-device access (user-controlled)
- **No Tracking**: No analytics, no cookies, no third-party services

## Common Questions

**Q: How accurate is the analysis?**
A: medBillDozer achieves 85-95% accuracy on benchmark tests. High severity issues are typically deterministic (rule-based). Medium/low issues may require human verification.

**Q: Do I need an API key?**
A: No. You can use the "Local Heuristic" mode without any API keys. For enhanced accuracy, add OpenAI or Google Gemini API keys.

**Q: Can I analyze scanned PDFs?**
A: You'll need to extract text first using an OCR tool. We recommend Adobe Acrobat, Tesseract OCR, or online OCR services.

**Q: Is my data shared with insurance companies?**
A: No. medBillDozer does not share any data. It's a local analysis tool. You decide what to do with the results.

**Q: Can this replace talking to my insurance?**
A: No. medBillDozer identifies potential issues, but you should always verify with your provider and insurance company before taking action.

## Next Steps

- [Analysis Model Details](analysis_model.md)
- [Cross-Document Reasoning](cross_document_reasoning.md)
- [Setup Guide](../development/setup.md)
