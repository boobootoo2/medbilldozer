# Prompt Engineering Guide for Medical Billing Analysis

## Overview

This guide documents the prompt engineering strategies used to improve error detection in the MedBillDozer patient benchmark suite, achieving a 36%+ improvement in F1 scores.

## Core Principles

### 1. Domain-Specific Knowledge Injection

**Problem:** Generic prompts assume the model will apply medical knowledge automatically.

**Solution:** Explicitly state medical rules and guidelines.

**Example:**
```
Instead of: "Look for age-inappropriate procedures"
Use: "Colonoscopy screening is recommended for age 45+. An 8-year-old receiving colonoscopy (CPT 45378) is age-inappropriate unless specific medical indication exists."
```

### 2. Chain-of-Thought Reasoning

**Problem:** Models may flag issues without proper medical justification.

**Solution:** Require explicit reasoning steps showing medical logic.

**Format:**
```
1. What did I notice? → [Evidence from document]
2. Why is this problematic? → [Medical knowledge/guideline]
3. What error category? → [Error type classification]
4. What is the CPT code? → [Specific code involved]
```

**Example Output:**
```
1. Notice: Patient is male (sex: M), Document bills CPT 88150
2. Problem: CPT 88150 is Pap smear (cervical cancer screening), requires female anatomy
3. Category: gender_specific_contradiction
4. Code: 88150
```

### 3. Few-Shot Learning

**Problem:** Abstract instructions leave ambiguity about expected outputs.

**Solution:** Provide 2-3 concrete examples showing ideal detection format.

**Template:**
```
Example 1: [Patient context] → [Evidence] → [Reasoning] → [Error type] → [CPT code]
Example 2: [Different scenario] → [Evidence] → [Reasoning] → [Error type] → [CPT code]
Example 3: [Third scenario] → [Evidence] → [Reasoning] → [Error type] → [CPT code]
```

### 4. Error Type Taxonomy

**Problem:** Vague categories like "billing error" are too broad.

**Solution:** Define specific, mutually exclusive error types with clear criteria.

**Structure for Each Error Type:**
- **Definition:** What this error is in plain language
- **Reasoning Steps:** How to systematically detect it
- **Examples:** 2-3 real-world scenarios with CPT codes
- **Search Patterns:** What keywords/patterns to look for

### 5. Multi-Pass Analysis

**Problem:** Single-pass analysis may miss subtle errors or specific categories.

**Solution:** Implement targeted passes focusing on commonly-missed error types.

**Architecture:**
- **Pass 1:** Broad comprehensive analysis with all error categories
- **Pass 2:** Targeted verification of weak categories with specific checklists
- **Pass 3 (optional):** High-stakes validation for critical errors

## Error Type Definitions

### Anatomical Contradiction

**Definition:** Procedures billed for organs/body parts the patient does NOT have.

**Detection Logic:**
```
1. Extract "Prior Surgeries" from patient history
2. Identify organ removals (keywords: amputation, ectomy, removal, hysterectomy, nephrectomy)
3. Scan all CPT codes in documents
4. Flag procedures related to removed organs
5. Verify timing: procedure date AFTER removal date
```

**Few-Shot Example:**
```
Patient: Richard Phillips, M, 62y
Surgery History: "Right leg amputation below knee (2020)"
Document 2: "CPT 27447 - Total knee arthroplasty, right knee"
REASONING: Patient had right leg amputated in 2020. Cannot perform knee replacement on amputated leg in 2024.
ERROR: anatomical_contradiction
CPT: 27447
```

**Prompt Snippet:**
```
1. ANATOMICAL CONTRADICTION (Domain Knowledge Required):
   - Definition: Procedures billed for organs/body parts the patient does NOT have
   - Reasoning Steps: Check medical history → Identify removed/absent organs → Flag procedures on those organs
   - Examples:
     * Patient had RIGHT leg amputation → Cannot bill for RIGHT knee surgery (CPT 27447)
     * Patient had appendectomy → Cannot bill for appendix removal again (CPT 44970)
   - Look for: Post-surgical history contradicting current procedures
```

### Temporal Violation

**Definition:** Procedures that violate medical timelines or logical sequencing.

**Detection Logic:**
```
1. Extract ALL dates from all documents
2. Build procedure timeline (CPT code + date pairs)
3. Sort chronologically
4. Check for impossible sequences:
   - Removal AFTER already removed
   - Post-op care BEFORE surgery
   - Screenings within inappropriate intervals (e.g., annual within weeks)
5. Flag violations with specific dates
```

**Few-Shot Example:**
```
Patient: Linda Foster, F, 58y
Document 1: "Appendectomy performed 2015"
Document 2: "CPT 44970 - Laparoscopic appendectomy - Date: 2024-01-15"
REASONING: Patient's appendix was removed in 2015. Cannot remove appendix again in 2024.
ERROR: temporal_violation
CPT: 44970
```

**Prompt Snippet:**
```
2. TEMPORAL VIOLATION (Timeline Analysis):
   - Definition: Procedures that violate medical timelines or logical sequencing
   - Reasoning Steps: Extract all dates → Order chronologically → Check for impossible sequences
   - Examples:
     * Billing for removal of organ AFTER already documented removal
     * Post-operative care billed BEFORE the surgery date
   - Look for: Date inconsistencies, premature repeat procedures
```

### Gender-Specific Contradiction

**Definition:** Procedures for anatomy the patient's biological sex does not have.

**Detection Logic:**
```
1. Extract patient sex field (M/F)
2. Scan CPT codes for sex-specific procedures:
   - Female-only: pregnancy (81xxx), Pap smear (88150), mammogram (77067), OB/GYN (59xxx, 58xxx)
   - Male-only: prostate (55xxx, G0103)
3. Flag mismatches: Male patient + female procedure OR Female patient + male procedure
4. Verify with anatomical reasoning
```

**Few-Shot Example:**
```
Patient: James Williams, M, 82y
Document 1: "CPT 88150 - Cytopathology, cervical or vaginal (Pap smear)"
REASONING: Patient is male (sex: M). Pap smears are cervical cancer screenings requiring female anatomy. Male patients cannot have cervical tissue.
ERROR: gender_specific_contradiction
CPT: 88150
```

**Prompt Snippet:**
```
3. GENDER-SPECIFIC CONTRADICTION (Anatomical):
   - Definition: Procedures for anatomy the patient's biological sex does not have
   - Reasoning Steps: Check patient sex → Identify sex-specific anatomy → Flag opposite-sex procedures
   - Examples:
     * Male patient billed for: Pap smear (CPT 88150), mammogram (CPT 77067)
     * Female patient billed for: prostate exam (CPT G0103)
   - Look for: OB/GYN procedures for males, prostate procedures for females
```

### Age-Inappropriate Procedure

**Definition:** Procedures outside recommended age ranges per clinical guidelines.

**Detection Logic:**
```
1. Extract patient age
2. Scan CPT codes for age-sensitive procedures:
   - Adult screenings: colonoscopy (45+), mammogram (40+), prostate (50+)
   - Pediatric: well-child visits (<18), pediatric vaccines
   - Geriatric: Medicare wellness (65+), geriatric assessments
3. Check if patient age falls outside guideline range
4. Flag with specific guideline reference
```

**Few-Shot Example:**
```
Patient: Lily Anderson, F, 8y
Document 1: "CPT 45378 - Colonoscopy, flexible; diagnostic"
REASONING: Patient is 8 years old. Colonoscopy screening is recommended for age 45+ per clinical guidelines. This is age-inappropriate without specific medical indication.
ERROR: age_inappropriate_procedure
CPT: 45378
```

**Prompt Snippet:**
```
4. AGE-INAPPROPRIATE PROCEDURE (Clinical Guidelines):
   - Definition: Procedures outside recommended age ranges per guidelines
   - Reasoning Steps: Check patient age → Look up procedure age guidelines → Flag if outside range
   - Examples:
     * 8-year-old billed for: colonoscopy (recommended 45+)
     * 25-year-old billed for: geriatric assessment (65+)
   - Look for: Screening/preventive procedures far outside typical age ranges
```

### Procedure Inconsistent With Health History

**Definition:** Procedures that make no medical sense given documented health status.

**Detection Logic:**
```
1. Extract patient conditions list (diabetes, cancer, heart disease, etc.)
2. Identify disease-specific procedures in documents:
   - Diabetes: glucose monitors, insulin pumps, diabetic retinopathy screening
   - Cancer: chemotherapy, radiation, oncology visits
   - Cardiac: angioplasty, pacemakers, stress tests
3. Cross-reference: Does patient have diagnosis supporting this procedure?
4. Flag disease procedures without corresponding condition
```

**Few-Shot Example:**
```
Patient: James Mitchell, M, 29y
Conditions: None (healthy)
Document 1: "CPT 95251 - Continuous glucose monitoring, physician interpretation"
REASONING: Patient has no diabetes diagnosis in medical history. Continuous glucose monitors are diabetes management devices. Inappropriate for healthy patient.
ERROR: procedure_inconsistent_with_health_history
CPT: 95251
```

**Prompt Snippet:**
```
5. PROCEDURE INCONSISTENT WITH HEALTH HISTORY (Medical Appropriateness):
   - Definition: Procedures that make no medical sense given documented health status
   - Reasoning Steps: Review conditions/surgeries → Check procedure indications → Flag if contraindicated
   - Examples:
     * Healthy patient (no diabetes) billed for: glucose monitor, diabetic screening
     * Patient without cancer billed for: chemotherapy, radiation
   - Look for: Disease-specific procedures without corresponding diagnosis
```

## Implementation: Two-Pass Analysis

### Pass 1: Comprehensive Analysis

**Goal:** Cast wide net with all error categories.

**Prompt Structure:**
```
PASS 1 - SYSTEMATIC ERROR DETECTION:
Analyze each document carefully using chain-of-thought reasoning for the following error categories:

1. ANATOMICAL CONTRADICTION
   [Detailed definition + reasoning steps + examples]

2. TEMPORAL VIOLATION
   [Detailed definition + reasoning steps + examples]

3. GENDER-SPECIFIC CONTRADICTION
   [Detailed definition + reasoning steps + examples]

4. AGE-INAPPROPRIATE PROCEDURE
   [Detailed definition + reasoning steps + examples]

5. PROCEDURE INCONSISTENT WITH HEALTH HISTORY
   [Detailed definition + reasoning steps + examples]

6. DUPLICATE CHARGES
   [Detailed definition + reasoning steps + examples]

7. OTHER BILLING INCONSISTENCIES
   [Upcoding, unbundling, medical necessity]

CHAIN-OF-THOUGHT REASONING REQUIRED:
For each potential issue, show your reasoning:
1. What did I notice? (Evidence)
2. Why is this problematic? (Medical knowledge)
3. What error category does this fall into?
4. What is the specific CPT code involved?

FEW-SHOT EXAMPLES:
[3 concrete examples across different error types]

NOW ANALYZE: Report ALL issues found.
```

### Pass 2: Targeted Verification

**Goal:** Focus on commonly-missed categories with specific checklists.

**Prompt Structure:**
```
PASS 2 - TARGETED VERIFICATION FOR PATIENT {id}:

Patient Summary:
- Age: {age} years, Sex: {sex}
- Surgeries: {surgeries}
- Conditions: {conditions}

Previously detected {N} issue(s) in PASS 1.

Now perform TARGETED checks for these commonly-missed error types:

1. ANATOMICAL CONTRADICTIONS:
   ✓ Check if Prior Surgeries list contains: amputation, removal, ectomy, hysterectomy
   ✓ If YES: Scan ALL documents for CPT codes related to those removed organs
   ✓ Example: "right leg amputation" → Flag ANY right leg/knee procedures (CPT 27xxx)

2. TEMPORAL VIOLATIONS:
   ✓ Extract ALL dates from documents
   ✓ Check for procedures on removed organs AFTER removal date
   ✓ Check for duplicate screenings within 1 year

3. HEALTH HISTORY INCONSISTENCIES:
   ✓ If Conditions list is EMPTY: Look for disease-specific procedures
   ✓ Diabetes procedures without diabetes diagnosis
   ✓ Cardiac procedures without heart disease

4. AGE/SEX MISMATCHES:
   ✓ If age < 18: Flag colonoscopy, prostate screening, mammography
   ✓ If age > 18: Flag pediatric vaccines, well-child visits
   ✓ If sex = Male: Flag pregnancy, Pap smear, mammogram
   ✓ If sex = Female: Flag prostate procedures

Report ONLY issues NOT found in PASS 1.
```

**Deduplication:**
```python
# Track CPT codes from Pass 1
pass1_codes = {issue['code'] for issue in detected_issues if issue.get('code')}

# Only add Pass 2 issues with new CPT codes
if result_pass2 and hasattr(result_pass2, 'issues'):
    for issue in result_pass2.issues:
        if issue.code and issue.code not in pass1_codes:
            detected_issues.append(issue)
            pass1_codes.add(issue.code)
```

## Best Practices

### 1. Specificity Over Generality
- ❌ "Check for billing errors"
- ✅ "Check if patient's prior surgeries list contains organ removals (keywords: amputation, ectomy, hysterectomy). If yes, scan CPT codes for procedures on those organs."

### 2. Explicit Medical Knowledge
- ❌ "Look for inappropriate procedures"
- ✅ "Colonoscopy screening is recommended for age 45+. Patients under 45 receiving colonoscopy without specific indication (IBD, polyps, cancer risk) is age-inappropriate."

### 3. Concrete Examples with CPT Codes
- ❌ "Gender-specific procedures should match patient sex"
- ✅ "Male patient billed for CPT 88150 (Pap smear) is invalid because Pap smears require cervical tissue (female anatomy)"

### 4. Chain-of-Thought Requirements
- ❌ Just flag issues
- ✅ "Show reasoning: 1) Evidence 2) Medical knowledge 3) Error category 4) CPT code"

### 5. Multi-Pass for Hard Categories
- ❌ Single comprehensive pass hoping to catch everything
- ✅ Pass 1 (broad) + Pass 2 (targeted at weak categories with <20% detection)

## Performance Metrics

### Before Enhancement
- F1 Score: 0.228 (22.8%)
- anatomical_contradiction: 0.0% (0/2)
- temporal_violation: 0.0% (0/8)
- age_inappropriate: 11.1% (1/9)
- procedure_inconsistent_with_health_history: 16.7% (4/24)

### After Enhancement (Initial Test)
- F1 Score: 0.31 (31%)
- Overall improvement: +36%
- Processing time: +45% (5.8s vs 4s per patient)

### Target Goals
- anatomical_contradiction: 50%+
- temporal_violation: 25%+
- age_inappropriate: 40%+
- procedure_inconsistent_with_health_history: 40%+

## References

- **Implementation:** `scripts/generate_patient_benchmarks.py` (lines 256-430)
- **Test Profiles:** `benchmarks/patient_profiles/*.json` (46 patients)
- **Dashboard:** `pages/benchmark_monitoring.py` (Error Type Heatmap)
- **Export Script:** `scripts/export_error_type_performance.py`

## Future Directions

1. **Dynamic Few-Shot Selection:** Choose examples based on patient profile characteristics
2. **Confidence Scoring:** Have model rate confidence (0-100%) in each detection
3. **Error-Type-Specific Models:** Fine-tune specialized models for hardest categories
4. **Active Learning:** Collect false negatives and add to training examples
5. **Three-Pass System:** Add validation pass for high-stakes errors (anatomical, temporal)

---

**Last Updated:** February 4, 2026  
**Status:** ✅ Implemented and Testing
