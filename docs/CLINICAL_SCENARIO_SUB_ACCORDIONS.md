# Clinical Scenario Sub-Accordions Feature

**Date**: February 15, 2026  
**Status**: ✅ **IMPLEMENTED**

---

## 🎯 Overview

Enhanced the "View Full" panel in the Clinical Data Sets section to display detailed clinical scenarios associated with each medical image as expandable sub-accordions.

### Problem Solved

**Before:**
- Image viewer showed only basic attribution (source, license, URL)
- No connection between images and their clinical validation scenarios
- Users couldn't understand what each image tests

**After:**
- Each image displays all associated clinical scenarios
- Expandable sub-accordions show full scenario details
- Complete patient context, findings, and expected outcomes
- Clear link between images and validation tests

---

## 📊 Feature Details

### Location
**Production Stability → Clinical Validation (BETA) → 📚 Clinical Data Sets → 🔍 View Full**

### What's Displayed

When you click "🔍 View Full" on any image, you now see:

1. **Full-size Image** (as before)
2. **Attribution Information** (as before)
3. **📋 Associated Clinical Scenarios** (NEW)
   - Number of scenarios using this image
   - Expandable sub-accordion for each scenario

### Scenario Information Displayed

Each sub-accordion shows:

#### Left Column: Scenario Details
- **ID**: Unique scenario identifier
- **Type**: Treatment Matching or ICD Coding
- **Modality**: X-Ray, Histopathology, MRI, Ultrasound
- **Image Type**: Positive (disease present) or Negative (normal)
- **Error Type**: Overtreatment, unnecessary procedure, etc.
- **Severity**: High, Moderate, Low
- **Cost Impact**: Dollar amount of potential savings

#### Right Column: Patient Context
- **Age**: Patient age
- **Gender**: Patient gender
- **Chief Complaint**: Reason for visit
- **Vital Signs**: Key measurements or biopsy location

#### Clinical Information
- **🔬 Clinical Finding**: What the imaging shows
- **💊 Prescribed Treatment**: What treatment was prescribed
- **✅ Expected Determination**: Whether treatment matches imaging
  - Green box: CORRECT matches
  - Red box: ERROR mismatches

#### ICD Scenarios (when applicable)
- **Diagnosis**: Clinical diagnosis
- **Provided ICD Code**: The ICD-10 code being validated
- Color-coded: Green ✅ for correct codes, Red ❌ for incorrect codes

---

## 🎨 Visual Design

### Layout Structure

```
┌────────────────────────────────────────────────────────┐
│  [Full Size Medical Image]                             │
│                                                         │
│  Attribution: Source | License | URL | Citation        │
├────────────────────────────────────────────────────────┤
│  📋 Associated Clinical Scenarios                      │
│  2 validation scenario(s) using this image             │
│                                                         │
│  ▶ 📝 Scenario 1: xray_001_treatment ──────────────────┤
│  │  📊 Scenario Details    │  👤 Patient Context       │
│  │  ────────────────────   │  ─────────────────       │
│  │  ID: clinical_001       │  Age: 45                  │
│  │  Type: Treatment Match  │  Gender: Female           │
│  │  Modality: Xray         │  Chief Complaint: ...     │
│  │  Image Type: Negative   │  Vital Signs: Normal      │
│  │  Error Type: Overtreat  │                           │
│  │  Severity: High         │                           │
│  │  Cost Impact: $15,000   │                           │
│  │  ─────────────────────────────────────────────────  │
│  │  🔬 Clinical Finding                                │
│  │  Clear lung fields, no infiltrates, no effusion     │
│  │  ─────────────────────────────────────────────────  │
│  │  💊 Prescribed Treatment                            │
│  │  IV antibiotics for pneumonia + hospitalization     │
│  │  ─────────────────────────────────────────────────  │
│  │  ✅ Expected Determination                          │
│  │  ERROR - Treatment does not match imaging           │
│  └─────────────────────────────────────────────────────┘
│                                                         │
│  ▶ 📝 Scenario 2: xray_001_icd ────────────────────────┤
│  │  [Similar layout for ICD validation scenario]       │
│  └─────────────────────────────────────────────────────┘
│                                                         │
│  [✖ Close]                                              │
└────────────────────────────────────────────────────────┘
```

### Color Coding

- **Blue Info Box** (🔬): Clinical findings (neutral information)
- **Yellow Warning Box** (💊): Prescribed treatment (caution)
- **Green Success Box** (✅): Correct determinations
- **Red Error Box** (❌): Incorrect determinations or errors
- **Gray Expander**: Collapsible scenario details

---

## 🔧 Technical Implementation

### Files Modified

1. **pages/production_stability.py** (Lines 906-988)
   - Added scenario display logic to View Full modal
   - Created sub-accordions for each scenario
   - Added conditional formatting for ICD vs treatment scenarios

2. **scripts/enhance_manifest_with_scenarios.py** (NEW)
   - Script to enhance manifest.json with scenario data
   - Reads CLINICAL_SCENARIOS from benchmark script
   - Maps scenarios to images by filename
   - Writes updated manifest

### Data Flow

```
┌──────────────────────────────────────────────┐
│  1. run_clinical_validation_benchmarks.py   │
│     CLINICAL_SCENARIOS dictionary           │
│     - 48 scenarios                          │
│     - Image files referenced                │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  2. enhance_manifest_with_scenarios.py       │
│     - Reads CLINICAL_SCENARIOS               │
│     - Maps to images by filename            │
│     - Enhances manifest.json                │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  3. manifest.json                            │
│     Each image now has:                      │
│     {                                        │
│       "filename": "xray_positive.png",       │
│       "scenarios": [                         │
│         {                                    │
│           "scenario_id": "...",              │
│           "validation_type": "...",          │
│           "patient_context": {...},          │
│           "clinical_finding": "...",         │
│           ...                                │
│         }                                    │
│       ]                                      │
│     }                                        │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  4. production_stability.py                  │
│     Dashboard reads manifest                 │
│     Displays scenarios in View Full panel    │
│     Creates sub-accordions                   │
└──────────────────────────────────────────────┘
```

### Code Highlights

**Scenario Display Logic:**
```python
# Clinical Scenarios Sub-Accordions
scenarios = img_data.get('scenarios', [])
if scenarios:
    st.markdown("### 📋 Associated Clinical Scenarios")
    st.caption(f"{len(scenarios)} validation scenario(s) using this image")
    
    for idx, scenario in enumerate(scenarios, 1):
        with st.expander(f"📝 Scenario {idx}: {scenario.get('scenario_id', 'Unknown')}", expanded=False):
            # Display scenario details...
```

**Conditional Formatting:**
```python
# Color-code expected determination
expected = scenario.get('expected_determination', 'N/A')
if 'ERROR' in expected:
    st.error(expected)  # Red box
else:
    st.success(expected)  # Green box
```

---

## 📈 Use Cases

### 1. Understanding Validation Tests

**Scenario**: You want to understand what each image tests.

**Workflow:**
1. Navigate to Clinical Data Sets
2. Click "🔍 View Full" on an image
3. Expand scenario sub-accordions
4. Read patient context and expected outcomes

**Value**: Clear understanding of test coverage and scenarios

### 2. Debugging Validation Failures

**Scenario**: A model fails a specific scenario, you want to understand why.

**Workflow:**
1. Check the scenario ID in validation results
2. Find the associated image in Clinical Data Sets
3. View full details to see patient context
4. Understand what the model should have detected

**Value**: Faster debugging with complete context

### 3. Training Data Review

**Scenario**: You're adding new training data and want to ensure diversity.

**Workflow:**
1. Review all images in Clinical Data Sets
2. Check scenarios for each image
3. Identify gaps (e.g., missing modalities or error types)
4. Add missing scenarios

**Value**: Comprehensive, balanced validation coverage

### 4. Stakeholder Communication

**Scenario**: You need to explain validation methodology to non-technical stakeholders.

**Workflow:**
1. Show an example image with scenarios
2. Walk through patient context and findings
3. Explain why certain treatments are errors
4. Demonstrate cost impact

**Value**: Clear communication with concrete examples

### 5. Quality Assurance

**Scenario**: Verify that scenarios are realistic and medically accurate.

**Workflow:**
1. Review each scenario with clinical team
2. Check patient contexts are appropriate
3. Verify expected determinations are correct
4. Validate cost impact estimates

**Value**: Confidence in validation methodology

---

## 🧪 Testing & Validation

### How to Test

1. **Refresh Dashboard:**
   ```bash
   streamlit run medBillDozer.py
   ```

2. **Navigate to:**
   - Production Stability page
   - 🏥 Clinical Validation (BETA) tab
   - 📚 Clinical Data Sets expander

3. **Test Steps:**
   - Click "🔍 View Full" on any image
   - Verify "📋 Associated Clinical Scenarios" section appears
   - Expand scenario sub-accordions
   - Verify all fields display correctly
   - Check color coding (green/red boxes)
   - Test with multiple images

### Expected Behavior

✅ **Images with scenarios:**
- Shows "📋 Associated Clinical Scenarios"
- Displays scenario count
- Sub-accordions expand/collapse properly
- All fields populated correctly

✅ **Treatment scenarios:**
- Show patient context (age, gender, vital signs)
- Display clinical finding, prescribed treatment
- Expected determination color-coded

✅ **ICD scenarios:**
- Show diagnosis and provided ICD code
- Code color-coded (green/red)
- Display correct vs incorrect classification

### Troubleshooting

**Issue**: No scenarios showing
- **Cause**: Manifest not enhanced
- **Fix**: Run `python3 scripts/enhance_manifest_with_scenarios.py`

**Issue**: Some images missing scenarios
- **Cause**: Image filename doesn't match CLINICAL_SCENARIOS
- **Fix**: Check filename mapping in benchmark script

**Issue**: Scenario fields showing "N/A"
- **Cause**: Scenario data incomplete in CLINICAL_SCENARIOS
- **Fix**: Update scenario definitions in benchmark script

---

## 📊 Statistics

### Coverage
- **Total Images**: 23
- **Images with Scenarios**: 23 (100%)
- **Total Scenarios**: 48
- **Scenarios per Image**: 1-3

### Scenario Types
- **Treatment Matching**: 24 scenarios
- **ICD Coding Validation**: 24 scenarios

### Modality Distribution
- **X-Ray**: 6 images, 12 scenarios (6 treatment + 6 ICD)
- **Histopathology**: 6 images, 12 scenarios (6 treatment + 6 ICD)
- **MRI**: 6 images, 12 scenarios (6 treatment + 6 ICD)
- **Ultrasound**: 6 images, 12 scenarios (6 treatment + 6 ICD)

---

## ✅ Implementation Checklist

- [x] Update `production_stability.py` to display scenarios in View Full panel
- [x] Create sub-accordion layout for scenarios
- [x] Add patient context display
- [x] Add clinical finding, treatment, expected determination
- [x] Add ICD-specific fields for ICD scenarios
- [x] Color-code determinations (green/red)
- [x] Create `enhance_manifest_with_scenarios.py` script
- [x] Run script to enhance manifest.json
- [x] Verify all 23 images enhanced
- [x] Test dashboard display
- [x] Documentation complete

---

## 🚀 Future Enhancements

### Short-term
1. Add "Download Scenario" button (export as JSON)
2. Add "Copy to Clipboard" for scenario details
3. Show scenario results if available (model performance on this scenario)
4. Add filters (show only treatment or ICD scenarios)

### Medium-term
1. Link to benchmark results for this specific scenario
2. Show historical performance trends for scenario
3. Add scenario difficulty rating
4. Compare model responses side-by-side

### Long-term
1. Interactive scenario editor
2. Community-contributed scenarios
3. Scenario versioning and history
4. Automated scenario generation from real cases

---

## 📚 Related Documentation

- **Clinical Validation**: `CLINICAL_VALIDATION_COMPLETE.md`
- **ICD Validation**: `docs/ICD_VALIDATION_INTEGRATION.md`
- **ICD Dashboard Features**: `docs/ICD_DASHBOARD_FEATURES.md`
- **ICD Model Comparison**: `docs/ICD_MODEL_COMPARISON.md`

---

## 🎉 Impact

### Before
- ❌ Images displayed without context
- ❌ No link to validation scenarios
- ❌ Manual lookup required to understand tests
- ❌ Difficult to explain methodology

### After
- ✅ Full scenario context in View Full panel
- ✅ Expandable sub-accordions for details
- ✅ Complete patient and clinical information
- ✅ Clear expected outcomes and cost impact
- ✅ Easy to understand and communicate

---

**Status**: ✅ **PRODUCTION READY**  
**Files Changed**: 2 (production_stability.py, new enhance_manifest script)  
**Lines Added**: ~130 lines  
**Images Enhanced**: 23/23 (100%)  
**Scenarios Mapped**: 48 total  
**Next Action**: Refresh dashboard and click "🔍 View Full" to see scenarios! 🚀
