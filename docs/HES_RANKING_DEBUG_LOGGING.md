# HES Ranking Debug Logging Implementation

**Date:** 2026-02-10  
**Issue:** OpenAI GPT-4 ranking higher than MedGemma-Ensemble despite lower domain detection rate  
**Root Cause:** Domain detection normalization error in data loading

## Changes Made

### 1. Fixed Domain Detection Normalization (Line 1294)

**Problem:** Database stores `domain_knowledge_detection_rate` as percentage values (e.g., 43.716 for 43.716%), but code was dividing by incorrect factor.

**Solution:**
```python
# CORRECT: Divide by 100 to normalize percentage to 0-1 range
domain_detection = df['domain_knowledge_detection_rate'].fillna(0).apply(lambda x: x / 100 if x > 1 else x)
```

**Database Values:**
- OpenAI GPT-4: `43.716` → normalized to `0.4372`
- MedGemma-Ensemble: `64.754` → normalized to `0.6475`
- Google MedGemma: `32.240` → normalized to `0.3224`

### 2. Added Debug Mode Toggle

**Location:** Sidebar (line ~90)

```python
debug_mode = st.sidebar.checkbox(
    "🐛 Debug Mode",
    value=True,
    help="Show detailed logging for HES calculations and data loading"
)
```

### 3. Comprehensive Debug Logging

#### Data Loading Phase
- ✅ Rows loaded from Supabase
- ✅ Metrics JSONB expansion status
- ✅ Domain column detection
- 🔍 **Raw domain_knowledge_detection_rate values** (shows DB values)
- ✅ **Normalized domain_detection values** (shows ÷100 result)

#### HES Calculation Phase
Shows breakdown for each model:
- Domain Detection contribution (50%)
- Recall contribution (25%)
- F1 contribution (10%)
- ROI contribution (7.5%)
- Savings Capture contribution (7.5%)
- Failure penalty
- Low-run penalty
- **Total HES score**

#### Final Ranking
- 🏆 Top-ranked model after sorting by HES

## Expected Results

With correct normalization and domain-focused ranking (50% weight):

| Rank | Model | Domain | Recall | F1 | HES |
|------|-------|--------|--------|----|----|
| 🥇 | medgemma-ensemble-v1.0 | 64.75% | 0.6352 | 0.483 | **0.5309** |
| 🥈 | OpenAI GPT-4 | 43.72% | 0.4276 | 0.414 | **0.3669** |
| 🥉 | Google MedGemma-4B-IT | 32.24% | 0.3183 | 0.379 | **0.2787** |

## How to Use Debug Mode

1. **Enable Debug Mode:**
   - Open Streamlit dashboard
   - In sidebar, check "🐛 Debug Mode"
   - Navigate to "Clinical Reasoning Evaluation" tab

2. **Clear Cache:**
   - Click ☰ menu → "Clear cache"
   - Or wait 10 seconds (reduced TTL for testing)

3. **Review Debug Output:**
   - Check raw domain values from database
   - Verify normalization (÷100)
   - Review HES calculation breakdown
   - Confirm top-ranked model

4. **Disable for Production:**
   - Uncheck "🐛 Debug Mode" for cleaner UI
   - Change cache TTL back to 300s (5 minutes)

## Verification Steps

```bash
# 1. Check current database values
python3 scripts/verify_supabase_results.py --limit 3

# 2. Verify normalization in code
grep -n "x / 100 if x > 1" pages/production_stability.py

# 3. Test calculation manually
python3 -c "
data = [
    {'model': 'medgemma-ensemble', 'domain': 64.754, 'recall': 0.6352, 'f1': 0.483},
    {'model': 'OpenAI GPT-4', 'domain': 43.716, 'recall': 0.4276, 'f1': 0.414},
]
for row in data:
    domain_norm = row['domain'] / 100
    hes = (domain_norm * 0.50) + (row['recall'] * 0.25) + (row['f1'] * 0.10)
    print(f\"{row['model']}: HES={hes:.4f}\")
"
```

## Files Modified

1. **pages/production_stability.py**
   - Line ~90: Added debug mode checkbox
   - Line 1221: Updated cache function signature
   - Line 1294: Fixed normalization (÷100)
   - Lines 1225-1300: Added debug logging throughout data loading
   - Lines 1440-1455: Added HES calculation debug output

2. **scripts/verify_supabase_results.py**
   - Already had correct logic (multiplies by 100 for display)

## Troubleshooting

If ranking is still incorrect:

1. **Check cache:** Clear Streamlit cache completely
2. **Verify DB values:** Run `verify_supabase_results.py` to see raw data
3. **Check debug logs:** Enable debug mode and review all outputs
4. **Inspect data flow:** Look for filtering that might exclude models
5. **Test calculation:** Use test script above to verify formula

## Technical Notes

### Why ÷100 Not ÷10000?

Database stores domain detection as:
- **Percentage format**: 43.716 (means 43.716%)
- **Not basis points**: Would be 4371.6 if in basis points
- **Verify script confirms**: Multiplies by 100 for display (43.716 × 100 = 4371.6%)

### HES Formula

```python
HES = (domain_detection * 0.50) +      # PRIMARY metric
      (recall * 0.25) +                 # SECONDARY metric
      (f1 * 0.10) +                     # Balance
      (normalized_roi * 0.075) +        # Efficiency
      (savings_capture * 0.075) -       # Financial impact
      failure_penalty -                 # Reliability
      low_run_penalty                   # Data confidence
```

Domain detection gets 50% weight because medical billing compliance prioritizes detecting healthcare-specific errors (gender mismatches, age-inappropriate procedures, anatomical contradictions) that require medical domain knowledge.
