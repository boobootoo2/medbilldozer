# How to View Clinical Scenarios - Quick Guide

**Issue**: Clinical scenarios not visible in View Full panel  
**Solution**: Follow these steps to see them

---

## ✅ Status Check

- [x] Manifest enhanced with scenarios (23/23 images)
- [x] Dashboard code updated to display scenarios
- [x] ICD fields added (icd_code, icd_description, correct_code)
- [x] Dataset field name fixed (dataset vs dataset_name)

---

## 🔍 How to View Scenarios

### Step 1: Refresh Your Browser
**Important**: You must refresh the browser page to reload the updated manifest.json

1. In your browser showing the dashboard
2. Press `Cmd + R` (Mac) or `Ctrl + R` (Windows/Linux)
3. Or click the refresh button

### Step 2: Navigate to Clinical Data Sets
1. Go to **Production Stability** page (sidebar)
2. Click **🏥 Clinical Validation (BETA)** tab
3. Scroll down to **📚 Clinical Data Sets** expander
4. Click to expand it

### Step 3: View Full Image
1. Find any image (e.g., "xray_positive.png")
2. Click the **🔍 View Full** button
3. **Scroll down** below the image

### Step 4: See Clinical Scenarios
You should now see:
```
─────────────────────────────────
📋 Associated Clinical Scenarios
3 validation scenario(s) using this image

▶ 📝 Scenario 1: xray_004_covid_appropriate_treatment
▶ 📝 Scenario 2: xray_icd_001_covid_incorrect_code
▶ 📝 Scenario 3: xray_icd_004_covid_correct_code
```

### Step 5: Expand Scenarios
Click on any scenario expander to see:
- Patient details (age, gender, complaint, vitals)
- Clinical findings
- Prescribed treatment
- Expected determination (color-coded)
- For ICD scenarios: ICD codes with descriptions

---

## 🐛 Troubleshooting

### Problem: Don't see "📋 Associated Clinical Scenarios"

**Solution 1: Force Refresh**
- Press `Cmd + Shift + R` (Mac) or `Ctrl + Shift + R` (Windows) for hard refresh
- This clears cache and reloads everything

**Solution 2: Clear Streamlit Cache**
1. In the dashboard, press `C` key
2. Or click the menu (top right) → Clear Cache → Rerun

**Solution 3: Restart Streamlit**
```bash
# Stop current Streamlit (Ctrl+C in terminal)
# Then restart:
export BETA=true
streamlit run medBillDozer.py
```

### Problem: Scenarios show but fields are "N/A"

**Check**: Make sure you re-ran the enhancement script (already done ✅)

**Verify**: Check manifest has scenario data
```bash
cat benchmarks/clinical_images/kaggle_datasets/selected/manifest.json | grep -A 5 scenarios
```

### Problem: "View Full" doesn't show anything

**Solution**: The content appears **below the button**. Scroll down after clicking "View Full"

---

## 📊 What You Should See

### For Treatment Scenarios:
```
📝 Scenario 1: xray_004_covid_appropriate_treatment

📊 Scenario Details          👤 Patient Context
ID: clinical_004             Age: 62
Type: Treatment Matching     Gender: Male
Modality: Xray              Chief Complaint: SOB, fever
Image Type: Positive         Vital Signs: Fever 101.5°F

🔬 Clinical Finding
Bilateral ground-glass opacities consistent with COVID-19 pneumonia

💊 Prescribed Treatment  
Supplemental oxygen + antiviral therapy + supportive care

✅ Expected Determination
CORRECT - Treatment matches imaging findings
```

### For ICD Scenarios:
```
📝 Scenario 2: xray_icd_001_covid_incorrect_code

📊 Scenario Details          👤 Patient Context
ID: clinical_004_icd         Age: 62
Type: ICD Coding            Gender: Male
Error Type: Incorrect ICD    Chief Complaint: SOB, fever
Severity: Moderate
Cost Impact: $5,000

🔬 Clinical Finding
Bilateral ground-glass opacities consistent with COVID-19 pneumonia

💊 Prescribed Treatment
None

❌ Expected Determination
ERROR - ICD code does not match diagnosis

🏥 ICD-10 Codes

Diagnosis:                   Provided ICD Code:
COVID-19 pneumonia          ❌ J18.9
                            Pneumonia, unspecified organism
                            ✅ Correct: U07.1 (COVID-19)
```

---

## ✅ Verification Checklist

Try these to confirm scenarios are working:

1. [ ] Refreshed browser page
2. [ ] Navigated to Production Stability → Clinical Validation (BETA)
3. [ ] Expanded "📚 Clinical Data Sets"
4. [ ] Clicked "🔍 View Full" on an image
5. [ ] Scrolled down below the image
6. [ ] See "📋 Associated Clinical Scenarios" heading
7. [ ] See scenario count (e.g., "3 validation scenario(s)")
8. [ ] Can expand/collapse scenario sub-accordions
9. [ ] Scenario details display correctly
10. [ ] ICD codes show with descriptions

---

## 🎯 Quick Test

**Try this specific image**: `xray_positive.png`

This image has **3 scenarios**:
1. Treatment scenario (COVID appropriate treatment)
2. ICD error scenario (wrong code J18.9)
3. ICD correct scenario (correct code U07.1)

If you can see all 3, everything is working! ✅

---

## 📱 Expected Behavior

### When Working Correctly:

1. **View Full button** → Shows full-size image
2. **Scroll down** → See "📋 Associated Clinical Scenarios"
3. **Scenario count** → "2-3 validation scenario(s) using this image"
4. **Expandable** → Each scenario has ▶ icon
5. **Click expander** → Shows full scenario details
6. **Color coding**:
   - Green boxes → Correct determinations
   - Red boxes → Errors
   - Blue boxes → Clinical findings
   - Yellow boxes → Treatments

### Close Button:
- **✖ Close** button at bottom → Closes the View Full modal

---

## 🚀 Summary

**The scenarios ARE there!** You just need to:

1. **Refresh browser** (Cmd+R / Ctrl+R)
2. Click **🔍 View Full**
3. **Scroll down** below the image
4. See **📋 Associated Clinical Scenarios**

The data is loaded (23/23 images, 48 scenarios) - you just need to refresh to see it!

---

**Status**: ✅ All files updated and ready  
**Next Action**: Refresh browser and view! 🎉
