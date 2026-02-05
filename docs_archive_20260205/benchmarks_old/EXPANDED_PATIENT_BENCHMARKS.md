# Expanded Patient Benchmark Suite - 30 Patients

## Overview
Comprehensive medical billing error detection benchmark covering 6 major issue categories across 30 diverse patient profiles.

## Issue Coverage Summary

### A. Gender & Reproductive Inconsistencies (18 issues)
- Pregnancy ultrasound → male patient (P001, P011)
- Prostate biopsy → female patient (P004, P030)
- Hysterectomy → male patient (P005, P027)
- Pap smear → male patient (P005, P023)
- Testicular ultrasound → female patient (P012)
- Labor & delivery → male patient (P011)
- Mammogram → male patient (P023)
- Obstetric care → male patient (P025)
- Transvaginal ultrasound → male patient (P007, P029)
- Cervical biopsy → male patient (P027)

### B. Age-Inappropriate Procedures (12 issues)
- Colonoscopy → child under 10 (P003, P013, P024)
- Pediatric vaccine → elderly (P014)
- Neonatal intensive care → adult/child (P016)
- Geriatric cognitive screening → pediatric/young adult (P016, P028)
- Bone density scan → young adult (P006, P013, P026)
- PSA screening → child (P003)
- Geriatric assessment → child (P003)

### C. Anatomical & Surgical History Contradictions (9 issues)
- Appendectomy after prior appendectomy (P002, P011)
- Gallbladder removal after cholecystectomy (P012)
- Procedure on amputated limb (P017)
- Left knee surgery when diagnosis is right knee (P019)
- Coronary bypass billed multiple times too soon (P021, P025)
- Hysterectomy after prior hysterectomy (P022)

### D. Diagnosis–Procedure Mismatch (11 issues)
- Chemotherapy without oncology diagnosis (P003, P014, P022, P026)
- Dialysis without kidney disease (P014, P030)
- Cardiac catheterization for common cold (P015)
- ICU care for minor outpatient complaint (P015)
- Oncology infusion without cancer (P022)

### E. Care Setting Inconsistencies (7 issues)
- ICU charges on same-day outpatient discharge (P001, P015)
- Ambulance transport but patient self-arrived (P020)
- Inpatient stay without admission note (P020)
- Skilled nursing care without transfer (P024)

### F. Temporal & Frequency Violations (10 issues)
- Duplicate charge for same service (P002, P005, P010)
- Duplicate same-day MRI/imaging (P017, P028)
- Two annual physicals within 3 months (P018, P029)
- Preventive screening repeated too soon (P018)
- Multiple anesthesia base units for single procedure (P019)
- Overlapping hospital stays at different facilities (P021)

## Total Statistics
- **Total Patients**: 30
- **Total Billing Issues**: 67
- **Average Issues per Patient**: 2.2
- **Domain Knowledge Required**: 100% of issues

## Issue Distribution
| Category | Count | Percentage |
|----------|-------|------------|
| Gender & Reproductive | 18 | 26.9% |
| Age-Inappropriate | 12 | 17.9% |
| Surgical History Contradictions | 9 | 13.4% |
| Diagnosis-Procedure Mismatch | 11 | 16.4% |
| Care Setting Inconsistencies | 7 | 10.4% |
| Temporal & Frequency Violations | 10 | 14.9% |

## Complexity Distribution
- **1 issue**: 0 patients (0%)
- **2 issues**: 30 patients (100%)
- **Severity**: All issues are High or Critical

## Expected Model Performance
- **Medical Domain Models** (MedGemma): Expected 70-90% detection rate
- **General LLMs** (GPT-4, Claude): Expected 40-60% detection rate  
- **Generic Models** (Gemini, Baseline): Expected 0-20% detection rate

## Running the Expanded Benchmark

```bash
# Run all models
python3 scripts/generate_patient_benchmarks.py --model all --push-to-supabase --environment local

# Run specific model
python3 scripts/generate_patient_benchmarks.py --model medgemma --push-to-supabase

# View results in dashboard
# Navigate to: http://localhost:8501 → Patient Benchmarks tab
```

## Key Insights
This expanded suite provides:
1. **Comprehensive coverage** of all major billing error categories
2. **Realistic complexity** with 2 issues per patient
3. **Medical domain knowledge requirements** that expose weaknesses in generic models
4. **Diverse demographics** (ages 2-82, male/female)
5. **Various care settings** (inpatient, outpatient, ED, specialty)
6. **Temporal and longitudinal** tracking requirements

## Created
February 4, 2026
