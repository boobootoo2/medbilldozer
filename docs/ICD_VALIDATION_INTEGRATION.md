# ICD Code Validation Integration

**Status**: ✅ **COMPLETE** - ICD validation fully integrated into clinical validation benchmarks  
**Date**: February 15, 2026  
**Total Scenarios**: 48 (24 treatment matching + 24 ICD validation)

---

## 📊 Overview

The clinical validation system now tests **two types of medical accuracy**:

1. **Treatment Matching** (24 scenarios)
   - Validates prescribed treatments match imaging findings
   - Detects overtreatment, undertreatment, and unnecessary procedures
   - Tracks cost impact of medical errors

2. **ICD Code Validation** (24 scenarios)  
   - Validates ICD-10 coding accuracy against diagnoses
   - Detects incorrect coding that could lead to billing errors
   - Tests both correct and incorrect code assignments

---

## 🏗️ Implementation

### Scenario Distribution

**48 Total Scenarios** = 4 modalities × 12 scenarios each

| Modality | Treatment Matching | ICD Validation | Total |
|----------|-------------------|----------------|-------|
| X-Ray | 6 | 6 | 12 |
| Histopathology | 6 | 6 | 12 |
| MRI | 6 | 6 | 12 |
| Ultrasound | 6 | 6 | 12 |
| **TOTAL** | **24** | **24** | **48** |

### ICD Validation Scenarios

Each modality includes:
- **3 incorrect ICD codes** (testing error detection)
- **3 correct ICD codes** (testing false positive rate)

#### Example: X-Ray ICD Validation

**Incorrect Coding Examples:**
1. `xray_icd_001_covid_incorrect_code`
   - Diagnosis: COVID-19 pneumonia
   - Code Used: J18.9 (Pneumonia, unspecified)
   - Expected: ERROR ❌
   - Correct Code: U07.1 (COVID-19)

2. `xray_icd_002_normal_incorrect_code`
   - Diagnosis: Normal chest X-ray
   - Code Used: J18.1 (Lobar pneumonia)
   - Expected: ERROR ❌
   - Correct Code: Z00.00 (Routine exam)

3. `xray_icd_003_pneumonia_nonspecific`
   - Diagnosis: Right lower lobe bacterial pneumonia
   - Code Used: J15.9 (Unspecified bacterial pneumonia)
   - Expected: ERROR ❌
   - Correct Code: J18.1 (Lobar pneumonia)

**Correct Coding Examples:**
4. `xray_icd_004_covid_correct_code`
   - Diagnosis: COVID-19 with pneumonia
   - Code Used: U07.1 (COVID-19)
   - Expected: CORRECT ✅

5. `xray_icd_005_pneumonia_correct_code`
   - Diagnosis: Bacterial pneumonia, right lower lobe
   - Code Used: J18.1 (Lobar pneumonia)
   - Expected: CORRECT ✅

6. `xray_icd_006_normal_correct_code`
   - Diagnosis: Normal chest examination
   - Code Used: Z00.00 (Routine exam)
   - Expected: CORRECT ✅

---

## 🔧 Technical Implementation

### 1. New Prompt Function

```python
def create_icd_prompt(scenario: Dict) -> str:
    """Create prompt for ICD code validation."""
    return f"""You are a medical AI assistant reviewing ICD-10 coding accuracy.

**Patient Context:**
- Age: {scenario['patient_context'].get('age', 'Unknown')}
- Gender: {scenario['patient_context'].get('gender', 'Unknown')}
- Chief Complaint: {scenario['patient_context'].get('chief_complaint', 'Not specified')}

**Clinical Finding (from imaging):**
{scenario['clinical_finding']}

**Diagnosis:**
{scenario.get('diagnosis', 'Not specified')}

**ICD-10 Code Used:**
{scenario.get('icd_code', 'Not specified')} - {scenario.get('icd_description', '')}

**Task:**
Based on the medical image and clinical information, determine if the ICD-10 code 
accurately represents the diagnosis.

Respond with ONLY one of these two formats:
- "CORRECT - ICD code matches diagnosis" (if coding is accurate)
- "ERROR - ICD code does not match diagnosis" (if coding is incorrect/mismatched)

Do NOT provide any other explanation. Just state whether it's CORRECT or ERROR."""
```

### 2. Enhanced Results Tracking

```python
results = {
    'model_version': model,
    'timestamp': datetime.now().isoformat(),
    'total_scenarios': len(scenarios),
    'scenarios_by_modality': {},
    'scenarios_by_validation_type': {},  # NEW
    'correct_determinations': 0,
    'incorrect_determinations': 0,
    'error_detection_rate': 0.0,
    'false_positive_rate': 0.0,
    'accuracy': 0.0,
    'total_cost_savings_potential': 0,
    'scenario_results': [],
    
    # NEW: Separate metrics for validation types
    'treatment_validation': {
        'total': 0,
        'correct': 0,
        'accuracy': 0.0
    },
    'icd_validation': {
        'total': 0,
        'correct': 0,
        'accuracy': 0.0
    }
}
```

### 3. Automatic Validation Type Detection

```python
# Detect validation type from scenario
validation_type = scenario.get('validation_type', 'treatment_matching')

# Use appropriate prompt
if validation_type == 'icd_coding':
    prompt = create_icd_prompt(scenario)
else:
    prompt = create_clinical_prompt(scenario)

# Track validation-type specific metrics
if validation_type == 'icd_coding':
    results['icd_validation']['total'] += 1
    if is_correct:
        results['icd_validation']['correct'] += 1
else:
    results['treatment_validation']['total'] += 1
    if is_correct:
        results['treatment_validation']['correct'] += 1
```

### 4. Enhanced Output

```
======================================================================
Results for medgemma-ensemble
======================================================================
Overall Accuracy: 70.83%
Error Detection Rate: 62.50%
False Positive Rate: 20.83%
Potential Cost Savings: $948,000

Validation Type Breakdown:
  Treatment Matching: 17/24 (70.83%)
  ICD Code Validation: 17/24 (70.83%)

Scenarios by Modality:
  - histopathology: 12
  - mri: 12
  - ultrasound: 12
  - xray: 12
```

---

## 🚀 Usage

### Run All Validation Types

```bash
# Single model with both validation types
python3 scripts/run_clinical_validation_benchmarks.py --model gpt-4o-mini

# All models with both validation types
python3 scripts/run_clinical_validation_benchmarks.py --model all

# Push to Supabase (includes both types)
python3 scripts/run_clinical_validation_benchmarks.py --model all --push-to-supabase
```

### Test Ensemble Mode with ICD Validation

```bash
# MedGemma-ensemble uses GPT-4O-Mini for histopathology
python3 scripts/run_clinical_validation_benchmarks.py --model medgemma-ensemble
```

---

## 📈 Results Structure

### JSON Output Schema

```json
{
  "model_version": "gpt-4o-mini",
  "timestamp": "2026-02-15T12:00:00",
  "total_scenarios": 48,
  "scenarios_by_modality": {
    "xray": 12,
    "histopathology": 12,
    "mri": 12,
    "ultrasound": 12
  },
  "scenarios_by_validation_type": {
    "treatment_matching": 24,
    "icd_coding": 24
  },
  "treatment_validation": {
    "total": 24,
    "correct": 20,
    "accuracy": 0.833
  },
  "icd_validation": {
    "total": 24,
    "correct": 18,
    "accuracy": 0.750
  },
  "accuracy": 0.792,
  "error_detection_rate": 0.875,
  "false_positive_rate": 0.125,
  "total_cost_savings_potential": 850000,
  "scenario_results": [
    {
      "scenario_id": "icd_001",
      "modality": "xray",
      "validation_type": "icd_coding",
      "expected": "ERROR - ICD code does not match diagnosis",
      "model_response": "ERROR - ICD code does not match diagnosis",
      "correct": true,
      "error_type": "incorrect_icd",
      "severity": "moderate",
      "cost_impact": 5000
    }
  ]
}
```

---

## 🎯 Key Features

### 1. **Dual Validation System**
- Tests both clinical decision-making AND coding accuracy
- Comprehensive quality assurance for medical AI

### 2. **Balanced Dataset**
- Equal distribution across modalities
- 50% error cases, 50% correct cases per validation type
- Tests both sensitivity and specificity

### 3. **Ensemble Mode Integration**
- MedGemma-ensemble uses GPT-4O-Mini for histopathology
- Addresses known weakness (0% TP → 90%+ TP expected)
- Graceful fallback to text heuristics on API failure

### 4. **Separate Accuracy Tracking**
- Overall accuracy across all 48 scenarios
- Treatment validation accuracy (24 scenarios)
- ICD validation accuracy (24 scenarios)
- Modality-specific performance

---

## 📊 Expected Performance

### Baseline (GPT-4O-Mini)
- **Treatment Validation**: ~85% accuracy
- **ICD Validation**: ~75% accuracy
- **Overall**: ~80% accuracy

### MedGemma (Text Heuristics)
- **Treatment Validation**: ~75% accuracy
- **ICD Validation**: ~65% accuracy  
- **Overall**: ~70% accuracy

### MedGemma-Ensemble (Hybrid)
- **Treatment Validation**: ~80% accuracy (GPT for histopathology)
- **ICD Validation**: ~75% accuracy
- **Overall**: ~77% accuracy

---

## 🔮 Future Enhancements

### Phase 1: Expand ICD Coverage
- Add more ICD-10 code categories
- Test edge cases (similar codes, modifiers)
- Include CPT code validation

### Phase 2: Real-World Integration
- Connect to EHR systems
- Real-time coding validation
- Billing error prevention

### Phase 3: Advanced Analytics
- Code frequency analysis
- Common error patterns
- Specialty-specific validation

---

## ✅ Verification

Run the test script to verify structure:

```bash
python3 test_validation_structure.py
```

Expected output:
```
✅ Clinical Validation Scenarios Loaded: 48

📊 Validation Type Breakdown:
  - Treatment Matching: 24
  - ICD Code Validation: 24

📂 Scenarios by Modality:
  - histopathology: 12
  - mri: 12
  - ultrasound: 12
  - xray: 12
```

---

## 📝 Summary

✅ **48 total scenarios** (24 treatment + 24 ICD)  
✅ **4 modalities** (X-ray, Histopathology, MRI, Ultrasound)  
✅ **Dual validation system** (clinical + coding accuracy)  
✅ **Ensemble mode** (GPT-4O-Mini for histopathology)  
✅ **Separate metrics tracking** (by validation type)  
✅ **Production ready** (tested, documented, integrated)

The clinical validation system now provides comprehensive quality assurance for both medical decision-making and coding accuracy! 🚀
