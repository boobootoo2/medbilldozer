# Fix: Gemini 0% Detection Rate Issue

**Date:** 2026-02-05  
**Issue:** Google Gemini 1.5 Pro showing 0% precision/recall/F1 across all benchmark runs  
**Root Cause:** Provider not extracting CPT codes for issue matching

---

## Problem Analysis

### Symptoms
- Gemini completing all 46 patient analyses successfully
- `detected_issues` arrays returning empty `[]`
- All metrics (precision, recall, F1) = 0.0
- High latency (~30 seconds/patient) but no detections

### Root Cause
The benchmark matching logic (in `generate_patient_benchmarks.py` lines 850-920) relies on **CPT code matching**:

```python
# Line 860: Check for CPT code match
if expected_issue.cpt_code and expected_issue.cpt_code.lower() in issue_text:
    matched = True
```

**Problem:** Gemini's provider prompt asked for generic issue types but did NOT request CPT codes, so the `code` field was always `None`.

**Result:** No matches possible → 0% detection

---

## Solution Implemented

### 1. Updated Gemini Provider Prompt
**File:** `src/medbilldozer/providers/gemini_analysis_provider.py`

**Changes:**
- Added CPT code extraction to prompt: `"code": "CPT code or procedure code if mentioned"`
- Added healthcare domain issue types: `gender_mismatch`, `age_inappropriate_procedure`, `anatomical_contradiction`, etc.
- Added explicit instruction to flag demographic mismatches

**Before:**
```python
For each issue:
- type: one of duplicate_charge, billing_error, non_covered_service, overbilling, ...
- summary: short description
- evidence: brief supporting explanation
- max_savings: numeric dollar amount
```

**After:**
```python
For each issue:
- type: one of duplicate_charge, billing_error, gender_mismatch,
        age_inappropriate_procedure, anatomical_contradiction,
        procedure_inconsistent_with_health_history, ...
- summary: short description
- evidence: brief supporting explanation
- code: CPT code or procedure code if mentioned (e.g., "CPT 76805", "99213")
- max_savings: numeric dollar amount

IMPORTANT: If you find procedures that don't match the patient's demographics 
(e.g., male patient with obstetric procedures), flag them and include the CPT code.
```

### 2. Updated Issue Creation
**File:** `src/medbilldozer/providers/gemini_analysis_provider.py`

**Before:**
```python
issues.append(Issue(
    type=item.get("type", "other"),
    summary=item.get("summary", "Potential issue identified"),
    evidence=item.get("evidence"),
    max_savings=max_savings,
))
```

**After:**
```python
issues.append(Issue(
    type=item.get("type", "other"),
    summary=item.get("summary", "Potential issue identified"),
    evidence=item.get("evidence"),
    code=item.get("code"),  # Include CPT code for matching
    max_savings=max_savings,
))
```

### 3. Updated OpenAI Provider (Consistency)
**File:** `src/medbilldozer/providers/openai_analysis_provider.py`

Applied same fixes to ensure all providers:
- Extract CPT codes
- Support healthcare domain issue types
- Populate the `code` field in Issue objects

---

## Testing

### Before Fix
```
Google Gemini 1.5 Pro:
- Precision: 0.00
- Recall: 0.00
- F1: 0.00
- Domain Knowledge Detection: 0.0%
- Detected Issues: [] (empty)
```

### After Fix (Expected)
```
Google Gemini 1.5 Pro:
- Should now detect issues with CPT codes
- Matching logic can find expected issues
- Non-zero precision/recall/F1
- Actual detection rates will depend on Gemini's analysis quality
```

---

## Verification Commands

```bash
# Re-run Gemini benchmarks
python3 scripts/generate_patient_benchmarks.py --model gemini

# Check a sample result for CPT codes
cat benchmarks/results/patient_benchmark_gemini.json | jq '.individual_results[0].detected_issues'

# Verify code field is populated
cat benchmarks/results/patient_benchmark_gemini.json | jq '.individual_results[0].detected_issues[].code'

# Push updated results to Supabase
./scripts/push_local_benchmarks.sh gemini
```

---

## Files Modified

1. **`src/medbilldozer/providers/gemini_analysis_provider.py`**
   - Updated prompt to request CPT codes
   - Added healthcare domain issue types
   - Added `code` parameter to Issue creation

2. **`src/medbilldozer/providers/openai_analysis_provider.py`**
   - Added same CPT code extraction
   - Added healthcare domain issue types  
   - Added `code` parameter to Issue creation

---

## Related Issues

### Why This Wasn't Caught Earlier
- Other models (MedGemma, Baseline) were already extracting CPT codes correctly
- Gemini and OpenAI providers were created earlier before patient benchmark matching logic
- The matching logic evolved to require CPT codes for precision
- No failing tests because providers were technically returning valid (empty) Issue arrays

### Impact
- **7+ Gemini benchmark runs** recorded as 0% detection
- False conclusion that "Gemini can't detect issues"
- Dashboard showing incorrect Gemini performance
- Need to re-run benchmarks to get accurate Gemini metrics

---

## Next Steps

1. ✅ Fix applied to both Gemini and OpenAI providers
2. ⏳ Re-run benchmarks for accurate metrics
3. ⏳ Push corrected results to Supabase
4. ⏳ Update dashboard summary with new data
5. ⏳ Consider adding unit tests for CPT code extraction

---

## Lessons Learned

1. **Provider Interface Contract:** All providers must extract the same fields (type, summary, evidence, **code**, max_savings)
2. **Schema Evolution:** When matching logic changes, update all providers
3. **Sanity Checks:** Empty detection arrays should trigger warnings
4. **Test Coverage:** Need integration tests that verify CPT code extraction across all providers

---

**Status:** ✅ Fixed (awaiting re-run for confirmation)
