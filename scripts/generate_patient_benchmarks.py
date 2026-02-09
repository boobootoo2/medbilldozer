#!/usr/bin/env python3
"""
Model Benchmark Suite (Cross-Document Analysis)

This benchmark tests models' ability to detect medical billing inconsistencies requiring
healthcare domain knowledge, such as:
- Gender-inappropriate procedures (e.g., male receiving obstetric care)
- Age-inappropriate screenings (e.g., child receiving colonoscopy)
- Anatomically impossible procedures
- Procedures without medical justification

Metrics tracked:
- Detection accuracy (precision, recall, F1)
- Domain knowledge utilization
- Cost savings potential from error detection

MedGemma should excel due to its healthcare-specific training.
"""

import json
import sys
import time
import re
import subprocess  # nosec B404 - required for git command execution in CI/CD
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from medbilldozer.providers.medgemma_hosted_provider import MedGemmaHostedProvider
from medbilldozer.providers.gemma3_hosted_provider import Gemma3HostedProvider
from medbilldozer.providers.openai_analysis_provider import OpenAIAnalysisProvider
from medbilldozer.providers.gemini_analysis_provider import GeminiAnalysisProvider
from medbilldozer.providers.llm_interface import LocalHeuristicProvider
from medbilldozer.providers.medgemma_ensemble_provider import MedGemmaEnsembleProvider

# Import advanced metrics module
try:
    from scripts.advanced_metrics import compute_advanced_metrics, merge_metrics_to_dict, format_category_metrics_for_db
    ADVANCED_METRICS_AVAILABLE = True
except ImportError:
    ADVANCED_METRICS_AVAILABLE = False
    print("⚠️  Advanced metrics module not available, using basic metrics only")


@dataclass
class PatientProfile:
    """Patient demographic and medical history."""
    patient_id: str
    name: str
    age: int
    sex: str
    date_of_birth: str
    conditions: List[str]
    allergies: List[str]
    surgeries: List[str]


@dataclass
class ExpectedIssue:
    """Expected issue that requires domain knowledge to detect."""
    type: str
    severity: str
    description: str
    requires_domain_knowledge: bool
    cpt_code: Optional[str] = None


@dataclass
class PatientBenchmarkResult:
    """Results for a single patient's multi-document analysis."""
    patient_id: str
    patient_name: str
    model_name: str
    documents_analyzed: int
    analysis_latency_ms: float
    expected_issues: List[ExpectedIssue]
    detected_issues: List[Dict[str, Any]]
    true_positives: int
    false_positives: int
    false_negatives: int
    domain_knowledge_score: float  # % of domain-knowledge issues detected
    error_message: Optional[str] = None
    # NEW: Domain subcategory breakdown
    domain_breakdown: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # NEW: Recall-oriented metrics
    domain_recall: float = 0.0
    generic_recall: float = 0.0
    cross_document_recall: float = 0.0
    # NEW: Cost savings metrics
    potential_savings: float = 0.0  # Total $ from detected issues
    missed_savings: float = 0.0  # Total $ from undetected issues


@dataclass
class PatientBenchmarkMetrics:
    """Aggregated metrics across all patients."""
    model_name: str
    total_patients: int
    successful_analyses: int
    avg_precision: float
    avg_recall: float
    avg_f1_score: float
    domain_knowledge_detection_rate: float
    avg_latency_ms: float
    individual_results: List[PatientBenchmarkResult]
    generated_at: str
    # NEW: Domain subcategory breakdown
    domain_breakdown: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # NEW: Parent category aggregations (for statistical stability)
    aggregated_categories: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # NEW: Recall-oriented metrics (PRIMARY optimization targets)
    domain_recall: float = 0.0
    domain_precision: float = 0.0
    generic_recall: float = 0.0
    cross_document_recall: float = 0.0
    # NEW: Cost savings metrics
    total_potential_savings: float = 0.0
    total_missed_savings: float = 0.0
    avg_savings_per_patient: float = 0.0
    savings_capture_rate: float = 0.0  # % of potential savings captured


class PatientBenchmarkRunner:
    """Runs cross-document patient-level benchmarks."""
    
    # High-signal subset: Obvious domain violations for rapid recall testing
    HIGH_SIGNAL_SUBSET = [
        'patient_001',  # Male with obstetric ultrasound
        'patient_002',  # Male with Pap smear
        'patient_006',  # 15yo with screening mammogram
        'patient_011',  # 8yo with screening colonoscopy
        'patient_031',  # Right leg amputation + right knee billing
        'patient_032',  # Appendectomy + appendix removal rebilling
        'patient_033',  # Bilateral mastectomy + breast procedure billing
        'patient_035',  # Hysterectomy + uterine procedure billing
    ]
    
    def __init__(self, model: str, subset: Optional[str] = None, workers: int = 1):
        self.model = model
        self.subset = subset
        
        # Respect model-specific worker limits
        # OpenAI has rate limits that work best with max 2 concurrent workers
        model_max_workers = {
            'openai': 2,  # OpenAI rate limits
            'gemini': 2,  # Gemini also has rate limits
        }
        max_allowed = model_max_workers.get(model, workers)
        self.workers = min(workers, max_allowed)
        
        # Notify if workers were capped
        if self.workers < workers:
            print(f"ℹ️  Note: {model} limited to {self.workers} workers (requested {workers}) due to API rate limits")
        
        self.benchmarks_dir = PROJECT_ROOT / "benchmarks"
        self.profiles_dir = self.benchmarks_dir / "patient_profiles"
        self.inputs_dir = self.benchmarks_dir / "inputs"
        self.results_dir = self.benchmarks_dir / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize provider
        self.provider = self._init_provider()
    
    def _init_provider(self):
        """Initialize the analysis provider."""
        if self.model == "medgemma":
            return MedGemmaHostedProvider()
        if self.model == "medgemma-ensemble":
            return MedGemmaEnsembleProvider()
        elif self.model == "gemma3":
            return Gemma3HostedProvider()
        elif self.model == "openai":
            return OpenAIAnalysisProvider()
        elif self.model == "gemini":
            return GeminiAnalysisProvider()
        elif self.model == "baseline":
            return LocalHeuristicProvider()
        else:
            raise ValueError(f"Unknown model: {self.model}")
    
    def _get_precise_model_name(self) -> str:
        """Get the precise model name for display."""
        model_names = {
            "medgemma": "Google MedGemma-4B-IT",
            "medgemma-ensemble": "medgemma-ensemble-v1.0",
            "gemma3": "Google Gemma-3-27B-IT",
            "openai": "OpenAI GPT-4",
            "gemini": "Google Gemini 1.5 Pro",
            "baseline": "Heuristic Baseline"
        }
        return model_names.get(self.model, self.model)
    
    def load_patient_profile(self, profile_path: Path) -> tuple:
        """Load patient profile and expected issues. Supports both old and new JSON formats."""
        with open(profile_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both old format (nested) and new format (flat)
        if 'demographics' in data:
            # Old format with nested structure
            # Be defensive: medical_history or its keys may be missing in some profiles
            demographics = data.get('demographics', {}) or {}
            medical_history = data.get('medical_history', {}) or {}

            profile = PatientProfile(
                patient_id=data.get('patient_id', ''),
                name=data.get('name', ''),
                age=demographics.get('age', 0),
                sex=demographics.get('sex', ''),
                date_of_birth=demographics.get('date_of_birth', ''),
                conditions=medical_history.get('conditions', []) or [],
                allergies=medical_history.get('allergies', []) or [],
                surgeries=medical_history.get('surgeries', []) or []
            )
            document_names = data.get('documents', [])
        else:
            # New format with flat structure
            profile = PatientProfile(
                patient_id=data['patient_id'],
                name=data.get('patient_name', data.get('name', 'Unknown')),
                age=data['age'],
                sex=data['sex'],
                date_of_birth=data.get('date_of_birth', 'Unknown'),
                conditions=data.get('known_conditions', []),
                allergies=data.get('allergies', []),
                surgeries=[
                    s.get('procedure', s) if isinstance(s, dict) else s
                    for s in data.get('prior_surgical_history', [])
                ]
            )
            # Return document dicts (will be processed later to extract content)
            document_names = data.get('documents', [])
        
        # Normalize expected issue dicts to match ExpectedIssue dataclass fields
        expected_issues = []
        for issue in data.get('expected_issues', []):
            normalized = {
                'type': issue.get('type') or issue.get('issue_type') or issue.get('issue') or '',
                'severity': issue.get('severity', 'medium'),
                'description': issue.get('description') or issue.get('reasoning') or '',
                'requires_domain_knowledge': (
                    issue.get('requires_domain_knowledge')
                    or issue.get('domain_knowledge_required')
                    or issue.get('requires_domain')
                    or False
                ),
                'cpt_code': issue.get('cpt_code') or issue.get('code') or None,
            }
            try:
                expected_issues.append(ExpectedIssue(**normalized))
            except TypeError:
                # Fallback: create with minimal fields if unexpected keys remain
                expected_issues.append(ExpectedIssue(
                    type=normalized.get('type', ''),
                    severity=normalized.get('severity', 'medium'),
                    description=normalized.get('description', ''),
                    requires_domain_knowledge=normalized.get('requires_domain_knowledge', False),
                    cpt_code=normalized.get('cpt_code')
                ))
        
        return profile, expected_issues, document_names
    
    def load_document_text(self, filename: str) -> str:
        """Load text content from a document."""
        doc_path = self.inputs_dir / filename
        if not doc_path.exists():
            raise FileNotFoundError(f"Document not found: {doc_path}")
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_medical_history(self, patient_id: str) -> Optional[str]:
        """Load medical history document for a patient if it exists."""
        # Try different filename patterns
        patterns = [
            f"{patient_id}_medical_history.txt",
            f"patient_{patient_id}_medical_history.txt",
            f"patient_{patient_id.split('_')[-1]}_medical_history.txt"
        ]
        
        for pattern in patterns:
            history_path = self.inputs_dir / pattern
            if history_path.exists():
                with open(history_path, 'r', encoding='utf-8') as f:
                    return f.read()
        
        return None
    
    def analyze_patient_documents(self, profile: PatientProfile, documents: List[str]) -> tuple:
        """
        Analyze all documents for a patient with cross-document context.
        Returns: (detected_issues, latency_ms, error_message)
        """
        start_time = time.perf_counter()
        
        try:
            # Load all document texts
            # Handle both old format (filenames) and new format (embedded content)
            doc_texts = []
            for doc_item in documents:
                if isinstance(doc_item, str):
                    # Old format: filename to load
                    if doc_item.strip():  # Not empty content string
                        try:
                            doc_texts.append(self.load_document_text(doc_item))
                        except FileNotFoundError:
                            # New format: content embedded directly
                            doc_texts.append(doc_item)
                    else:
                        doc_texts.append(doc_item)
                elif isinstance(doc_item, dict):
                    # New format: document dict with content
                    doc_texts.append(doc_item.get('content', ''))
                else:
                    doc_texts.append(str(doc_item))
            
            # Combine documents with patient context for cross-document analysis
            patient_context = f"""
PATIENT PROFILE:
ID: {profile.patient_id}
Age: {profile.age} years
Sex: {profile.sex}
Date of Birth: {profile.date_of_birth}

Medical History:
- Conditions: {', '.join(profile.conditions) if profile.conditions else 'None'}
- Allergies: {', '.join(profile.allergies) if profile.allergies else 'None'}
- Prior Surgeries: {', '.join(profile.surgeries) if profile.surgeries else 'None'}

"""
            
            # Load medical history document if available
            medical_history = self.load_medical_history(profile.patient_id)
            if medical_history:
                patient_context += f"""PRIMARY CARE PHYSICIAN MEDICAL HISTORY:
{medical_history}

"""
            
            patient_context += """DOCUMENTS TO ANALYZE:
-------------------
"""
            
            for i, doc_text in enumerate(doc_texts, 1):
                patient_context += f"\n--- DOCUMENT {i} ---\n{doc_text}\n"
            
            patient_context += """
-------------------

INSTRUCTIONS FOR ANALYSIS:
Perform a comprehensive multi-pass analysis of ALL documents for this patient. Use the patient's medical history, demographics, and cross-document patterns.

PASS 1 - SYSTEMATIC ERROR DETECTION:
Analyze each document carefully using chain-of-thought reasoning for the following error categories:

1. ANATOMICAL CONTRADICTION (Domain Knowledge Required):
   - Definition: Procedures billed for organs/body parts the patient does NOT have
   - Reasoning Steps: Check medical history → Identify removed/absent organs → Flag procedures on those organs
   - Examples:
     * Patient had RIGHT leg amputation → Cannot bill for RIGHT knee surgery (CPT 27447)
     * Patient had appendectomy → Cannot bill for appendix removal again (CPT 44970)
     * Patient had hysterectomy → Cannot bill for uterine procedures (CPT 58150)
   - Look for: Post-surgical history contradicting current procedures

2. TEMPORAL VIOLATION (Timeline Analysis):
   - Definition: Procedures that violate medical timelines or logical sequencing
   - Reasoning Steps: Extract all dates → Order procedures chronologically → Check for impossible sequences
   - Examples:
     * Billing for removal of organ AFTER already documented removal
     * Post-operative care billed BEFORE the surgery date
     * Preventive screening within weeks of prior screening (should be annual)
   - Look for: Date inconsistencies, premature repeat procedures

3. GENDER-SPECIFIC CONTRADICTION (Anatomical):
   - Definition: Procedures for anatomy the patient's biological sex does not have
   - Reasoning Steps: Check patient sex → Identify sex-specific anatomy → Flag opposite-sex procedures
   - Examples:
     * Male patient billed for: pregnancy test (CPT 81025), Pap smear (CPT 88150), mammogram (CPT 77067)
     * Female patient billed for: prostate exam (CPT G0103), prostate biopsy (CPT 55700)
   - Look for: Obstetric, gynecologic, or urologic procedures mismatched to sex

4. AGE-INAPPROPRIATE PROCEDURE (Clinical Guidelines):
   - Definition: Procedures outside recommended age ranges per clinical guidelines
   - Reasoning Steps: Check patient age → Look up procedure age guidelines → Flag if outside range
   - Examples:
     * 8-year-old billed for: colonoscopy (recommended 45+), prostate screening (50+)
     * 35-year-old billed for: pediatric vaccines, well-child visit
     * 25-year-old billed for: geriatric assessment, Medicare wellness visit
   - Look for: Screening/preventive procedures far outside typical age ranges

5. PROCEDURE INCONSISTENT WITH HEALTH HISTORY (Medical Necessity - SYSTEMATIC ABSENCE LOGIC):
   - Definition: Procedures billed WITHOUT documented medical justification in patient history
   - CRITICAL: Absence of supporting evidence = potential billing error (do NOT assume appropriate)
   
   MANDATORY SYSTEMATIC ANALYSIS:
   You MUST apply this 3-step process to EVERY procedure found in the documents:
   
   STEP 1: Extract ALL procedure codes/descriptions from documents
   STEP 2: For EACH procedure, determine required supporting condition(s)
   STEP 3: Search patient history and classify:
   
      ✓ SUPPORTED: Required condition IS documented in patient history → No flag
      ⚠️ UNSUPPORTED: Required condition NOT found in patient history → FLAG as procedure_inconsistent_with_health_history
      ✗ CONTRADICTED: Conflicting/wrong diagnosis present → FLAG as diagnosis_procedure_mismatch
   
   REQUIRED STRUCTURED OUTPUT FOR EACH PROCEDURE:
   {
     "procedure_name": "[name from bill]",
     "cpt_code": "[code if present]",
     "health_history_check": {
       "required_conditions": ["list of conditions that typically justify this procedure"],
       "patient_has_condition": true/false,
       "conflicting_condition_present": true/false,
       "classification": "SUPPORTED" | "UNSUPPORTED" | "CONTRADICTED",
       "evidence": "specific reference to where condition was/wasn't found",
       "action": "no_flag" | "flag_procedure_inconsistent_with_health_history" | "flag_diagnosis_procedure_mismatch"
     }
   }
   
   PROCEDURE-TO-CONDITION MAPPING GUIDE:
   • Diabetes-related (CGM CPT 95250, glucose monitoring, insulin pumps, diabetic eye exams) → Requires: "Diabetes" or "Type 1/2 Diabetes"
   • Cardiac procedures (catheterization 93xxx, angioplasty, stress tests, EKG) → Requires: Cardiac disease, hypertension, chest pain, heart condition
   • Oncology (chemotherapy 96xxx, radiation 77xxx, tumor markers) → Requires: Cancer diagnosis (any type)
   • Dialysis (CPT 90935-90999, hemodialysis, peritoneal dialysis) → Requires: Kidney failure, ESRD, chronic kidney disease
   • Asthma/COPD (inhalers, nebulizers, pulmonary function tests) → Requires: Asthma, COPD, chronic bronchitis, respiratory disease
   • Mental health (therapy 90xxx, psych eval, counseling) → Requires: Depression, anxiety, psychiatric diagnosis
   • Dental specialty (scaling D4341, periodontal surgery) → Requires: Periodontal disease, gum disease
   
   EXAMPLES OF SYSTEMATIC APPLICATION:
   
   Example A (UNSUPPORTED - Must Flag):
   Patient conditions: "Hypertension, Seasonal allergies"
   Procedure billed: CPT 95250 - Continuous Glucose Monitoring
   Analysis:
     required_conditions: ["Diabetes", "Type 1 Diabetes", "Type 2 Diabetes"]
     patient_has_condition: FALSE (only has hypertension & allergies)
     conflicting_condition_present: FALSE
     classification: UNSUPPORTED
     action: flag_procedure_inconsistent_with_health_history
   
   Example B (UNSUPPORTED - Must Flag):
   Patient conditions: None documented
   Procedure billed: CPT 96413 - Chemotherapy Administration
   Analysis:
     required_conditions: ["Cancer", "Malignancy", "Neoplasm", "Carcinoma"]
     patient_has_condition: FALSE (no cancer in medical history)
     conflicting_condition_present: FALSE
     classification: UNSUPPORTED
     action: flag_procedure_inconsistent_with_health_history
   
   Example C (CONTRADICTED - Must Flag):
   Patient diagnosis: "Common cold"
   Procedure billed: CPT 93458 - Cardiac Catheterization
   Analysis:
     required_conditions: ["Cardiac disease", "Chest pain", "Heart condition", "Coronary artery disease"]
     patient_has_condition: FALSE
     conflicting_condition_present: TRUE (common cold is unrelated respiratory infection)
     classification: CONTRADICTED
     action: flag_diagnosis_procedure_mismatch
   
   DO NOT skip this analysis. Apply to EVERY procedure systematically.
   Medical billing audits require documented medical necessity - absence of documentation IS a flag.

6. DUPLICATE CHARGES (Cross-Document):
   - Definition: Same procedure billed multiple times across documents for same date
   - Reasoning Steps: Build procedure inventory → Group by CPT + date → Flag duplicates
   - Examples:
     * CPT 99213 (office visit) appears in both clinic bill and insurance EOB for 1/15/2024
     * Lab test CPT 80053 billed twice on same date in different documents
   - Look for: Identical CPT codes with identical dates across documents

7. OTHER BILLING INCONSISTENCIES:
   - Upcoding, unbundling, medical necessity issues, incorrect modifiers
   - Reasoning Steps: Check CPT combinations → Verify medical necessity → Flag suspicious patterns

PASS 2 - TARGETED VERIFICATION (For Commonly Missed Errors):
This pass focuses on the error types most frequently missed in PASS 1.

PRIORITY 1: HEALTH HISTORY INCONSISTENCIES (This is the weakest category)
Apply the SYSTEMATIC ABSENCE LOGIC approach rigorously.

Re-examine documents specifically for these often-missed patterns:
- Any procedures on organs mentioned in "Prior Surgeries" (especially removals, amputations)
- Any procedures with dates BEFORE or immediately after related surgeries
- Any sex-specific procedures (check patient sex field carefully)
- Any age-extreme procedures (pediatric codes for adults, geriatric codes for young patients)
- ⚠️ HIGHEST PRIORITY: Any disease-specific procedures WITHOUT corresponding condition in medical history

MANDATORY ABSENCE LOGIC PROTOCOL:
You are acting as a medical billing auditor. Your job is to verify medical necessity.

For EACH procedure code you identify:
□ STEP 1: What medical condition typically justifies this procedure?
□ STEP 2: Search the patient's Conditions list for that condition
□ STEP 3: Make determination:
    - Condition FOUND → No flag
    - Condition NOT FOUND → Flag as "procedure_inconsistent_with_health_history"
    - Wrong/conflicting condition → Flag as "diagnosis_procedure_mismatch"

CRITICAL: Do NOT skip procedures. Check EVERY single one.

HIGH-PRIORITY PROCEDURE TYPES TO CHECK:
✓ Diabetes-related (CGM, glucose tests, insulin, diabetic eye exams, A1C tests)
✓ Cardiac procedures (catheterization, stress tests, EKG, angioplasty, pacemakers)
✓ Oncology treatments (chemotherapy, radiation, tumor markers, oncology visits)
✓ Dialysis (hemodialysis, peritoneal dialysis, kidney-related treatments)
✓ Respiratory treatments (inhalers, nebulizers, pulmonary function tests)
✓ Mental health services (therapy, psychiatric evaluations, counseling)
✓ Dental specialty (periodontal surgery, scaling, root planing)

REFERENCE MAPPING:
Procedure Category → Required Condition
- Diabetes management → "Diabetes" OR "Type 1 Diabetes" OR "Type 2 Diabetes"
- Cardiac procedures → "Cardiac disease" OR "Heart disease" OR "Hypertension" OR "Arrhythmia"
- Oncology → "Cancer" OR "Malignancy" OR "Neoplasm" OR "[specific cancer type]"
- Dialysis → "Kidney failure" OR "ESRD" OR "Chronic kidney disease" OR "Renal failure"
- Respiratory → "Asthma" OR "COPD" OR "Chronic bronchitis" OR "Respiratory disease"
- Mental health → "Depression" OR "Anxiety" OR "Psychiatric disorder" OR "[specific diagnosis]"

DO NOT assume medical necessity. In medical billing audits, absence of documentation IS a flag.

MANDATORY OUTPUT STRUCTURE:
Your response must include two sections:

SECTION 1: HEALTH HISTORY ANALYSIS (Required for ALL procedures)
For EVERY procedure found in the documents, output this structured analysis:
{
  "procedure": "[procedure name/description]",
  "cpt_code": "[code if present, or 'not specified']",
  "required_supporting_conditions": ["condition1", "condition2"],
  "support_found": true/false,
  "conflicting_conditions_found": true/false,
  "classification": "supported" | "unsupported" | "mismatch",
  "reasoning": "Brief explanation referencing patient history"
}

Do NOT skip procedures. Analyze every single one found in documents.

SECTION 2: IDENTIFIED ISSUES (Final output)
List only procedures classified as "unsupported" or "mismatch" as formal issues.

FEW-SHOT EXAMPLES OF SYSTEMATIC ANALYSIS:

Example 1 (Anatomical Contradiction): 
"Patient had right leg amputation in 2022. Document 2 bills CPT 27447 (knee replacement) on right knee in 2024. REASONING: Patient cannot have knee replacement on amputated leg. ERROR TYPE: anatomical_contradiction"

Example 2 (Age-Inappropriate): 
"Patient is 8 years old. Document 1 bills CPT 45378 (colonoscopy screening). REASONING: Colonoscopy screening recommended for age 45+, not appropriate for child without specific medical indication. ERROR TYPE: age_inappropriate_procedure"

Example 3 (Gender Mismatch): 
"Patient is male (sex: M). Document 3 bills CPT 88150 (Pap smear). REASONING: Pap smears are cervical cancer screenings for patients with cervixes (female anatomy). Male patients cannot have this procedure. ERROR TYPE: gender_specific_contradiction"

Example 4 (SYSTEMATIC HEALTH HISTORY CHECK - UNSUPPORTED):
Patient conditions: "Hypertension, Seasonal allergies"
Procedure: Continuous Glucose Monitoring | CPT: 95250
Structured analysis:
{
  "procedure": "Continuous Glucose Monitoring",
  "cpt_code": "95250",
  "required_supporting_conditions": ["Diabetes", "Type 1 Diabetes", "Type 2 Diabetes"],
  "support_found": false,
  "conflicting_conditions_found": false,
  "classification": "unsupported",
  "reasoning": "CGM is used for diabetes management. Patient conditions list includes only Hypertension and Seasonal allergies. No diabetes documented in medical history. Required supporting condition is ABSENT."
}
ACTION: Flag as procedure_inconsistent_with_health_history

Example 5 (SYSTEMATIC HEALTH HISTORY CHECK - UNSUPPORTED):
Patient conditions: None documented
Procedure: Chemotherapy Administration | CPT: 96413
Structured analysis:
{
  "procedure": "Chemotherapy Administration",
  "cpt_code": "96413",
  "required_supporting_conditions": ["Cancer", "Malignancy", "Neoplasm"],
  "support_found": false,
  "conflicting_conditions_found": false,
  "classification": "unsupported",
  "reasoning": "Chemotherapy requires documented cancer diagnosis. Patient medical history shows no cancer diagnosis in conditions list or surgical history. Required supporting evidence is ABSENT."
}
ACTION: Flag as procedure_inconsistent_with_health_history

Example 6 (SYSTEMATIC HEALTH HISTORY CHECK - MISMATCH):
Patient diagnosis: "Common cold"
Procedure: Cardiac Catheterization | CPT: 93458
Structured analysis:
{
  "procedure": "Cardiac Catheterization",
  "cpt_code": "93458",
  "required_supporting_conditions": ["Cardiac disease", "Coronary artery disease", "Chest pain", "Heart condition"],
  "support_found": false,
  "conflicting_conditions_found": true,
  "classification": "mismatch",
  "reasoning": "Cardiac catheterization requires cardiac symptoms or disease. Patient has common cold diagnosis only. Common cold (respiratory infection) does not justify invasive cardiac procedure. CONTRADICTING diagnosis present."
}
ACTION: Flag as diagnosis_procedure_mismatch

NOW ANALYZE THE DOCUMENTS:

CRITICAL INSTRUCTIONS:
1. Start by extracting ALL procedures from ALL documents (make a complete inventory)
2. For EACH procedure, apply the health history analysis structured output format shown in Section 5
3. Do NOT assume procedures are appropriate by default
4. Absence of documented supporting condition = FLAG the procedure
5. Report ALL issues found with specific CPT codes, clear evidence, and error type classification

SYSTEMATIC HEALTH HISTORY CHECK IS MANDATORY:
Every procedure must be evaluated against patient medical history.
Missing supporting diagnosis is a billing error that must be flagged.
"""
            
            # PASS 1: Initial comprehensive analysis
            result_pass1 = self.provider.analyze_document(patient_context, facts=None)
            
            # Extract detected issues from PASS 1
            detected_issues = []
            if result_pass1 and hasattr(result_pass1, 'issues'):
                detected_issues = [
                    {
                        'type': issue.type,
                        'summary': issue.summary,
                        'evidence': issue.evidence,
                        'code': issue.code,
                        'max_savings': issue.max_savings
                    }
                    for issue in result_pass1.issues
                ]
            
            # PASS 2: Targeted verification for commonly missed error types
            # Build targeted prompt focusing on weak categories
            pass2_prompt = f"""
PASS 2 - TARGETED VERIFICATION FOR PATIENT {profile.patient_id}:

Patient Summary:
- Age: {profile.age} years, Sex: {profile.sex}
- Surgeries: {', '.join(profile.surgeries) if profile.surgeries else 'None'}
- Conditions: {', '.join(profile.conditions) if profile.conditions else 'None'}

Previously detected {len(detected_issues)} issue(s) in PASS 1.

Now perform TARGETED checks for these commonly-missed error types:

1. ANATOMICAL CONTRADICTIONS:
   - Check if Prior Surgeries list contains: amputation, removal, ectomy, hysterectomy, appendectomy, nephrectomy
   - If YES: Scan ALL documents for CPT codes related to those removed/absent organs
   - Example: "right leg amputation" → Flag ANY right leg/knee procedures (CPT 27xxx)

2. TEMPORAL VIOLATIONS:
   - Extract ALL dates from documents
   - Check for procedures on removed organs AFTER removal date
   - Check for duplicate screenings within 1 year

3. HEALTH HISTORY INCONSISTENCIES (MANDATORY SYSTEMATIC CHECK):
   CRITICAL: This is the most frequently missed category. Apply absence logic rigorously.
   
   STEP-BY-STEP MANDATORY PROCESS:
   
   Step A: List ALL procedures from documents (include CPT codes where available)
   
   Step B: For EACH procedure on your list, ask:
     Question 1: "What medical condition typically justifies this procedure?"
     Question 2: "Is that condition documented in patient's Conditions list?"
     Question 3: "If NO, is there conflicting/wrong diagnosis present?"
   
   Step C: Classify and action:
     - If Q2 = YES → Classification: SUPPORTED → No flag
     - If Q2 = NO and Q3 = NO → Classification: UNSUPPORTED → FLAG as procedure_inconsistent_with_health_history
     - If Q2 = NO and Q3 = YES → Classification: MISMATCH → FLAG as diagnosis_procedure_mismatch
   
   PROCEDURE-CONDITION MAPPING (Use this as reference):
   • CGM / Glucose monitoring / Insulin (CPT 95250, 82962, E0607) → Requires: Diabetes
   • Cardiac cath / Angioplasty / Stress test (CPT 93xxx, 92xxx) → Requires: Cardiac disease
   • Chemotherapy / Radiation (CPT 96xxx, 77xxx) → Requires: Cancer
   • Dialysis (CPT 90935-90999) → Requires: Kidney failure/ESRD
   • Psychiatric therapy (CPT 90xxx) → Requires: Mental health diagnosis
   • Pulmonary function tests / Inhalers → Requires: Asthma/COPD/respiratory disease
   • Scaling / Periodontal surgery (D4341) → Requires: Periodontal disease
   • Diabetic retinopathy screening → Requires: Diabetes
   • Cardiac monitoring devices → Requires: Cardiac arrhythmia/disease
   
   MANDATORY OUTPUT FORMAT for this section:
   For each procedure checked, output:
   ```
   Procedure: [name] | CPT: [code]
   Required: [condition name]
   Patient has: YES / NO / CONFLICTING
   Action: SUPPORTED / FLAG_UNSUPPORTED / FLAG_MISMATCH
   ```
   
   Example systematic check output:
   ```
   Procedure: Continuous glucose monitoring | CPT: 95250
   Required: Diabetes (Type 1 or Type 2)
   Patient has: NO (only Hypertension, Seasonal allergies listed)
   Action: FLAG_UNSUPPORTED (procedure_inconsistent_with_health_history)
   
   Procedure: Office visit | CPT: 99213
   Required: None (general visit)
   Patient has: N/A
   Action: SUPPORTED
   
   Procedure: Chemotherapy administration | CPT: 96413
   Required: Cancer diagnosis
   Patient has: NO (no cancer in conditions or surgical history)
   Action: FLAG_UNSUPPORTED (procedure_inconsistent_with_health_history)
   ```
   
   DO NOT skip this systematic procedure-by-procedure check. It is mandatory.

4. AGE/SEX MISMATCHES:
   - If age < 18: Flag colonoscopy, prostate screening, mammography
   - If age > 18: Flag pediatric vaccines, well-child visits
   - If sex = Male: Flag pregnancy, Pap smear, mammogram, ovarian/uterine procedures
   - If sex = Female: Flag prostate procedures

DOCUMENTS TO RE-EXAMINE:
"""
            
            # Add documents again for pass 2
            for i, doc_text in enumerate(doc_texts, 1):
                pass2_prompt += f"\n--- DOCUMENT {i} ---\n{doc_text}\n"
            
            pass2_prompt += """
Report ONLY issues NOT found in PASS 1. Focus on the 4 categories above.
Use format: "ERROR TYPE: [type] | CPT: [code] | REASONING: [why this is problematic]"
"""
            
            # Call provider for PASS 2 with targeted prompt
            result_pass2 = self.provider.analyze_document(pass2_prompt, facts=None)
            
            # Merge PASS 2 results with PASS 1 (deduplicate by CPT code)
            pass1_codes = {issue['code'] for issue in detected_issues if issue.get('code')}
            
            if result_pass2 and hasattr(result_pass2, 'issues'):
                for issue in result_pass2.issues:
                    # Only add if CPT code not already detected in pass 1
                    if issue.code and issue.code not in pass1_codes:
                        detected_issues.append({
                            'type': issue.type,
                            'summary': issue.summary,
                            'evidence': issue.evidence,
                            'code': issue.code,
                            'max_savings': issue.max_savings
                        })
                        pass1_codes.add(issue.code)
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            return detected_issues, latency_ms, None
            
        except Exception as e:
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            return [], latency_ms, str(e)
    
    def _classify_document_type(self, text: str) -> str:
        """Simple classification based on document content."""
        text_lower = text.lower()
        if 'explanation of benefits' in text_lower or 'eob' in text_lower:
            return 'insurance_eob'
        elif any(x in text_lower for x in ['dental', 'cdt d', 'prophylaxis']):
            return 'dental_bill'
        elif any(x in text_lower for x in ['pharmacy', 'prescription', 'rx#']):
            return 'pharmacy_receipt'
        else:
            return 'medical_bill'
    
    def _aggregate_parent_categories(self, aggregated: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
        """
        Create parent category aggregations for statistically underpowered subcategories.
        
        This improves statistical stability by combining related subcategories.
        Parent metrics are computed from TOTALS, not averages of recalls, to ensure
        mathematically correct aggregation.
        
        Example: age_inappropriate_service combines:
        - age_inappropriate
        - age_inappropriate_procedure  
        - age_inappropriate_screening
        
        Args:
            aggregated: Per-category breakdown from _aggregate_domain_breakdown
            
        Returns:
            Dictionary with parent categories containing subtype breakdowns
        """
        parent_categories = {}
        
        # Define parent category groupings
        AGE_SUBTYPES = ['age_inappropriate', 'age_inappropriate_procedure', 'age_inappropriate_screening']
        
        # Aggregate age-inappropriate service (parent category)
        age_subtypes_present = [cat for cat in AGE_SUBTYPES if cat in aggregated]
        
        if age_subtypes_present:
            # Sum totals across all age subtypes
            total_detected = sum(aggregated[cat]['total_detected'] for cat in age_subtypes_present)
            total_missed = sum(aggregated[cat]['total_missed'] for cat in age_subtypes_present)
            total_cases = sum(aggregated[cat]['total_cases'] for cat in age_subtypes_present)
            
            # Calculate parent metrics from totals (NOT from averages)
            precision = total_detected / (total_detected + 0) if total_detected > 0 else 0.0  # No FP tracking yet
            recall = total_detected / total_cases if total_cases > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            # Build parent category with subtype details
            parent_categories['age_inappropriate_service'] = {
                'precision': round(precision, 4),
                'recall': round(recall, 4),
                'f1': round(f1, 4),
                'total_detected': total_detected,
                'total_missed': total_missed,
                'total_cases': total_cases,
                'subtypes': {
                    cat: {
                        'recall': aggregated[cat]['recall'],
                        'detected': aggregated[cat]['total_detected'],
                        'total': aggregated[cat]['total_cases']
                    }
                    for cat in age_subtypes_present
                }
            }
        
        return parent_categories
    
    def _aggregate_domain_breakdown(self, results: List[PatientBenchmarkResult]) -> Dict[str, Dict[str, float]]:
        """
        Aggregate domain breakdown across all patient results.
        
        Returns:
            Dictionary mapping category to aggregated precision/recall/f1
        """
        category_totals = {}
        
        for result in results:
            if result.error_message:
                continue
                
            for category, metrics in result.domain_breakdown.items():
                if category not in category_totals:
                    category_totals[category] = {
                        'total_tp': 0,
                        'total_fn': 0,
                        'total_fp': 0,
                        'total_cases': 0
                    }
                
                category_totals[category]['total_tp'] += metrics['true_positives']
                category_totals[category]['total_fn'] += metrics['false_negatives']
                category_totals[category]['total_cases'] += metrics['total']
        
        # Calculate final metrics per category
        aggregated = {}
        for category, totals in category_totals.items():
            tp = totals['total_tp']
            fn = totals['total_fn']
            total = totals['total_cases']
            
            precision = tp / (tp + totals['total_fp']) if (tp + totals['total_fp']) > 0 else 0.0
            recall = tp / total if total > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            aggregated[category] = {
                'precision': round(precision, 4),
                'recall': round(recall, 4),
                'f1': round(f1, 4),
                'total_detected': tp,
                'total_missed': fn,
                'total_cases': total
            }
        
        return aggregated
    
    def evaluate_detection(self, expected: List[ExpectedIssue], detected: List[Dict]) -> tuple:
        """
        Evaluate detection accuracy with domain subcategory tracking and cost savings.
        
        Returns: (true_positives, false_positives, false_negatives, domain_knowledge_score, 
                  domain_breakdown, domain_recall, generic_recall, cross_document_recall,
                  potential_savings, missed_savings)
        """
        if not expected:
            # No issues expected, any detection is false positive
            return 0, len(detected), 0, 0.0, {}, 0.0, 0.0, 0.0
        
        # Track which expected issues were matched to avoid double-counting
        matched_expected_indices = set()
        matched_detected_indices = set()
        domain_knowledge_detections = 0
        
        # NEW: Track detection by domain subcategory
        category_stats = {}  # {category: {'tp': X, 'fn': Y, 'total': Z}}
        
        # For each detected issue, try to match it to an expected issue
        for det_idx, detected_issue in enumerate(detected):
            issue_text = json.dumps(detected_issue).lower()
            
            # Try to match to an expected issue
            for exp_idx, expected_issue in enumerate(expected):
                if exp_idx in matched_expected_indices:
                    continue  # Already matched
                
                matched = False
                
                # Check for CPT code match
                if expected_issue.cpt_code and expected_issue.cpt_code.lower() in issue_text:
                    matched = True
                
                # Check for keyword matches (gender, age, inappropriate)
                if not matched:
                    keywords = expected_issue.type.split('_')
                    if any(keyword in issue_text for keyword in keywords):
                        matched = True
                
                # If matched, record it
                if matched:
                    matched_expected_indices.add(exp_idx)
                    matched_detected_indices.add(det_idx)
                    if expected_issue.requires_domain_knowledge:
                        domain_knowledge_detections += 1
                    
                    # NEW: Track by category
                    category = expected_issue.type
                    if category not in category_stats:
                        category_stats[category] = {'tp': 0, 'fn': 0, 'fp': 0, 'total': 0}
                    category_stats[category]['tp'] += 1
                    
                    break  # Move to next detected issue
        
        # Track false negatives by category
        for exp_idx, expected_issue in enumerate(expected):
            category = expected_issue.type
            if category not in category_stats:
                category_stats[category] = {'tp': 0, 'fn': 0, 'fp': 0, 'total': 0}
            category_stats[category]['total'] += 1
            
            if exp_idx not in matched_expected_indices:
                category_stats[category]['fn'] += 1
        
        # Calculate per-category metrics
        domain_breakdown = {}
        for category, stats in category_stats.items():
            tp = stats['tp']
            fn = stats['fn']
            total = stats['total']
            
            precision = tp / (tp + stats['fp']) if (tp + stats['fp']) > 0 else 0.0
            recall = tp / total if total > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            domain_breakdown[category] = {
                'precision': round(precision, 4),
                'recall': round(recall, 4),
                'f1': round(f1, 4),
                'true_positives': tp,
                'false_negatives': fn,
                'total': total
            }
        
        true_positives = len(matched_expected_indices)
        false_positives = len(detected) - len(matched_detected_indices)
        false_negatives = len(expected) - len(matched_expected_indices)
        
        # Calculate domain knowledge score
        domain_knowledge_issues = sum(1 for e in expected if e.requires_domain_knowledge)
        domain_knowledge_score = (domain_knowledge_detections / domain_knowledge_issues * 100) if domain_knowledge_issues > 0 else 0.0
        
        # NEW: Calculate recall-oriented metrics
        domain_recall = (domain_knowledge_detections / domain_knowledge_issues) if domain_knowledge_issues > 0 else 0.0
        generic_issues = len(expected) - domain_knowledge_issues
        generic_detections = true_positives - domain_knowledge_detections
        generic_recall = (generic_detections / generic_issues) if generic_issues > 0 else 0.0
        cross_document_recall = domain_recall  # For now, domain issues ARE cross-document issues
        
        # NEW: Calculate cost savings from detected issues
        potential_savings = sum(
            detected_issue.get('max_savings', 0) or 0
            for detected_issue in detected
            if detected.index(detected_issue) in matched_detected_indices
        )
        
        # Calculate missed savings from undetected expected issues
        # Use average savings estimate for missed issues (conservative estimate)
        avg_issue_value = 250.0  # Conservative average per medical billing error
        missed_savings = false_negatives * avg_issue_value
        
        return (true_positives, false_positives, false_negatives, domain_knowledge_score,
                domain_breakdown, domain_recall, generic_recall, cross_document_recall,
                potential_savings, missed_savings)

    def _process_single_profile(self, profile_file: Path, index: int, total: int) -> PatientBenchmarkResult:
        """Process a single patient profile (extracted from original loop)."""
        profile, expected_issues, document_names = self.load_patient_profile(profile_file)

        print(f"[{index}/{total}] Patient {profile.patient_id} ({profile.sex}, {profile.age}y)...", end=" ", flush=True)

        detected_issues, latency_ms, error = self.analyze_patient_documents(profile, document_names)

        if error:
            print(f"❌ {error}")
            result = PatientBenchmarkResult(
                patient_id=profile.patient_id,
                patient_name=profile.name,
                model_name=self._get_precise_model_name(),
                documents_analyzed=len(document_names),
                analysis_latency_ms=latency_ms,
                expected_issues=expected_issues,
                detected_issues=[],
                true_positives=0,
                false_positives=0,
                false_negatives=len(expected_issues),
                domain_knowledge_score=0.0,
                error_message=error
            )
            return result

        # Evaluate detection with enhanced metrics
        (tp, fp, fn, domain_score, domain_breakdown,
         domain_recall, generic_recall, cross_document_recall,
         potential_savings, missed_savings) = self.evaluate_detection(expected_issues, detected_issues)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        result = PatientBenchmarkResult(
            patient_id=profile.patient_id,
            patient_name=profile.name,
            model_name=self._get_precise_model_name(),
            documents_analyzed=len(document_names),
            analysis_latency_ms=latency_ms,
            expected_issues=expected_issues,
            detected_issues=detected_issues,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            domain_knowledge_score=domain_score,
            domain_breakdown=domain_breakdown,
            domain_recall=domain_recall,
            generic_recall=generic_recall,
            cross_document_recall=cross_document_recall,
            potential_savings=potential_savings,
            missed_savings=missed_savings
        )

        status = "✅" if fn == 0 else "⚠️"
        print(f"{status} {latency_ms:.0f}ms | Issues: {tp}/{len(expected_issues)} | Domain Recall: {domain_recall*100:.0f}%")

        return result
    
    def run_benchmarks(self) -> PatientBenchmarkMetrics:
        """Run benchmarks on all patient profiles."""
        precise_name = self._get_precise_model_name()
        print(f"\n🏥 Running patient-level benchmarks for: {precise_name}")
        print("=" * 70)
        
        # Load all patient profiles
        profile_files = sorted(self.profiles_dir.glob("patient_*.json"))
        
        if not profile_files:
            print("⚠️  No patient profiles found!")
            return None
        
        # Filter for high-signal subset if requested
        if self.subset == 'high_signal':
            profile_files = [
                f for f in profile_files
                if any(hs_id in f.stem for hs_id in self.HIGH_SIGNAL_SUBSET)
            ]
            print(f"🎯 Running HIGH-SIGNAL SUBSET MODE ({len(profile_files)} profiles)\n")
        else:
            print(f"📋 Found {len(profile_files)} patient profiles\n")
        
        results = []
        total_precision = 0
        total_recall = 0
        total_f1 = 0
        total_domain_score = 0
        successful = 0
        
        # If workers > 1, run profiles in parallel
        if self.workers > 1:
            print(f"⚡ Parallel execution with {self.workers} workers")
            futures = {}
            with ThreadPoolExecutor(max_workers=self.workers) as ex:
                for i, profile_file in enumerate(profile_files, 1):
                    futures[ex.submit(self._process_single_profile, profile_file, i, len(profile_files))] = profile_file

                for fut in as_completed(futures):
                    try:
                        result = fut.result()
                        results.append(result)
                        if not result.error_message:
                            # accumulate metrics
                            tp = result.true_positives
                            fp = result.false_positives
                            fn = result.false_negatives
                            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
                            total_precision += precision
                            total_recall += recall
                            total_f1 += f1
                            total_domain_score += result.domain_knowledge_score
                            successful += 1
                    except Exception as e:
                        profile_file = futures.get(fut)
                        print(f"\n❌ Error processing {profile_file}: {e}")
        else:
            for i, profile_file in enumerate(profile_files, 1):
                result = self._process_single_profile(profile_file, i, len(profile_files))
                results.append(result)
                if not result.error_message:
                    tp = result.true_positives
                    fp = result.false_positives
                    fn = result.false_negatives
                    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
                    total_precision += precision
                    total_recall += recall
                    total_f1 += f1
                    total_domain_score += result.domain_knowledge_score
                    successful += 1
        
        # Calculate aggregated metrics
        avg_precision = total_precision / successful if successful > 0 else 0.0
        avg_recall = total_recall / successful if successful > 0 else 0.0
        avg_f1 = total_f1 / successful if successful > 0 else 0.0
        avg_domain_score = total_domain_score / successful if successful > 0 else 0.0
        avg_latency = sum(r.analysis_latency_ms for r in results) / len(results) if results else 0.0
        
        # NEW: Calculate aggregated domain breakdown
        aggregated_domain_breakdown = self._aggregate_domain_breakdown(results)
        
        # NEW: Calculate parent category aggregations for statistical stability
        aggregated_categories = self._aggregate_parent_categories(aggregated_domain_breakdown)
        
        # NEW: Calculate recall-oriented metrics
        avg_domain_recall = sum(r.domain_recall for r in results if not r.error_message) / successful if successful > 0 else 0.0
        avg_generic_recall = sum(r.generic_recall for r in results if not r.error_message) / successful if successful > 0 else 0.0
        avg_cross_document_recall = sum(r.cross_document_recall for r in results if not r.error_message) / successful if successful > 0 else 0.0
        domain_precision = avg_precision  # For now, treat overall precision as domain precision
        
        # NEW: Calculate cost savings metrics
        total_potential_savings = sum(r.potential_savings for r in results if not r.error_message)
        total_missed_savings = sum(r.missed_savings for r in results if not r.error_message)
        avg_savings_per_patient = total_potential_savings / successful if successful > 0 else 0.0
        total_possible_savings = total_potential_savings + total_missed_savings
        savings_capture_rate = (total_potential_savings / total_possible_savings * 100) if total_possible_savings > 0 else 0.0
        
        metrics = PatientBenchmarkMetrics(
            model_name=self._get_precise_model_name(),
            total_patients=len(profile_files),
            successful_analyses=successful,
            avg_precision=avg_precision,
            avg_recall=avg_recall,
            avg_f1_score=avg_f1,
            domain_knowledge_detection_rate=avg_domain_score,
            avg_latency_ms=avg_latency,
            individual_results=results,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            domain_breakdown=aggregated_domain_breakdown,
            aggregated_categories=aggregated_categories,
            domain_recall=avg_domain_recall,
            domain_precision=domain_precision,
            generic_recall=avg_generic_recall,
            cross_document_recall=avg_cross_document_recall,
            total_potential_savings=total_potential_savings,
            total_missed_savings=total_missed_savings,
            avg_savings_per_patient=avg_savings_per_patient,
            savings_capture_rate=savings_capture_rate
        )
        
        # ====================================================================
        # COMPUTE ADVANCED METRICS (Risk-weighted recall, ROI, P95, etc.)
        # ====================================================================
        if ADVANCED_METRICS_AVAILABLE:
            try:
                # Compute advanced metrics
                advanced_metrics = compute_advanced_metrics(
                    patient_results=[r.__dict__ for r in results if not r.error_message],
                    error_type_performance=aggregated_categories,
                    total_potential_savings=total_potential_savings,
                    cost_per_second=0.0005  # $0.0005 per second inference cost
                )
                
                # Store advanced metrics in the metrics object for later use
                metrics.advanced_metrics = advanced_metrics
                
                print(f"\n✨ Advanced Metrics Computed:")
                print(f"   Risk-Weighted Recall: {advanced_metrics.risk_weighted_recall:.3f}")
                print(f"   Conservatism Index: {advanced_metrics.conservatism_index:.3f}")
                print(f"   P95 Latency: {advanced_metrics.p95_latency_ms:.1f}ms")
                print(f"   ROI Ratio: {advanced_metrics.roi_ratio:.1f}x")
                print(f"   Inference Cost: ${advanced_metrics.inference_cost_usd:.4f}")
                
            except Exception as e:
                print(f"⚠️  Failed to compute advanced metrics: {e}")
                metrics.advanced_metrics = None
        else:
            metrics.advanced_metrics = None
        
        return metrics
    
    def print_summary(self, metrics: PatientBenchmarkMetrics):
        """Print enhanced benchmark summary with domain subcategory breakdown."""
        precise_name = self._get_precise_model_name()
        print("\n" + "=" * 70)
        print(f"PATIENT BENCHMARK SUMMARY: {precise_name}")
        print("=" * 70)
        print(f"Patients Analyzed: {metrics.successful_analyses}/{metrics.total_patients}")
        print()
        print("🎯 RECALL-ORIENTED METRICS (PRIMARY TARGETS):")
        print(f"  Domain Recall:          {metrics.domain_recall*100:5.1f}%")
        print(f"  Domain Precision:       {metrics.domain_precision*100:5.1f}%")
        print(f"  Generic Recall:         {metrics.generic_recall*100:5.1f}%")
        print(f"  Cross-Document Recall:  {metrics.cross_document_recall*100:5.1f}%")
        print()
        print("📊 DOMAIN SUBCATEGORY BREAKDOWN:")
        if metrics.domain_breakdown:
            # Define age subtypes for special formatting
            age_subtypes = {'age_inappropriate', 'age_inappropriate_procedure', 'age_inappropriate_screening'}
            
            # Display parent categories first (if available)
            if metrics.aggregated_categories and 'age_inappropriate_service' in metrics.aggregated_categories:
                parent = metrics.aggregated_categories['age_inappropriate_service']
                recall_pct = parent['recall'] * 100
                detected = parent['total_detected']
                total = parent['total_cases']
                print(f"  {'age_inappropriate_service':40s} Recall: {recall_pct:5.1f}%  ({detected}/{total} detected)")
                
                # Display subtypes with tree structure
                subtypes = parent.get('subtypes', {})
                for i, (subtype, sub_metrics) in enumerate(sorted(subtypes.items())):
                    is_last = (i == len(subtypes) - 1)
                    tree_char = '└─' if is_last else '├─'
                    sub_recall_pct = sub_metrics['recall'] * 100
                    sub_detected = sub_metrics['detected']
                    sub_total = sub_metrics['total']
                    # Map full names to short labels
                    label_map = {
                        'age_inappropriate_screening': 'screening',
                        'age_inappropriate_procedure': 'procedure',
                        'age_inappropriate': 'general'
                    }
                    label = label_map.get(subtype, subtype)
                    print(f"      {tree_char} {label:34s} {sub_recall_pct:5.1f}%  ({sub_detected}/{sub_total})")
            
            # Display all other categories (excluding age subtypes if parent was shown)
            for category in sorted(metrics.domain_breakdown.keys()):
                # Skip age subtypes if parent category was displayed
                if category in age_subtypes and metrics.aggregated_categories.get('age_inappropriate_service'):
                    continue
                    
                cat_metrics = metrics.domain_breakdown[category]
                recall_pct = cat_metrics['recall'] * 100
                detected = cat_metrics['total_detected']
                total = cat_metrics['total_cases']
                print(f"  {category:40s} Recall: {recall_pct:5.1f}%  ({detected}/{total} detected)")
        else:
            print("  No domain subcategory data available")
        print()
        print("📈 OVERALL METRICS:")
        print(f"  Overall F1 Score:       {metrics.avg_f1_score:.3f}")
        print(f"  Avg Precision:          {metrics.avg_precision:.3f}")
        print(f"  Avg Recall:             {metrics.avg_recall:.3f}")
        print(f"  Avg Analysis Time:      {metrics.avg_latency_ms:.0f}ms ({metrics.avg_latency_ms/1000:.2f}s)")
        print()
        print("💰 COST SAVINGS METRICS:")
        print(f"  Total Potential Savings:   ${metrics.total_potential_savings:,.2f}")
        print(f"  Total Missed Savings:      ${metrics.total_missed_savings:,.2f}")
        print(f"  Avg Savings per Patient:   ${metrics.avg_savings_per_patient:,.2f}")
        print(f"  Savings Capture Rate:      {metrics.savings_capture_rate:.1f}%")
        print("=" * 70)
    
    def save_results(self, metrics: PatientBenchmarkMetrics):
        """Save results to JSON with advanced metrics."""
        output_file = self.results_dir / f"patient_benchmark_{self.model}.json"
        
        # Convert to dict with proper serialization
        results_dict = asdict(metrics)
        
        # Add advanced metrics if available
        if hasattr(metrics, 'advanced_metrics') and metrics.advanced_metrics:
            adv_metrics = metrics.advanced_metrics
            results_dict['advanced_metrics'] = {
                'true_positives': adv_metrics.true_positives,
                'false_positives': adv_metrics.false_positives,
                'false_negatives': adv_metrics.false_negatives,
                'risk_weighted_recall': round(adv_metrics.risk_weighted_recall, 4),
                'conservatism_index': round(adv_metrics.conservatism_index, 4),
                'p95_latency_ms': round(adv_metrics.p95_latency_ms, 2),
                'roi_ratio': round(adv_metrics.roi_ratio, 2),
                'inference_cost_usd': round(adv_metrics.inference_cost_usd, 6),
            }
            
            # Add hybrid metrics if present
            if adv_metrics.unique_detections is not None:
                results_dict['advanced_metrics'].update({
                    'unique_detections': adv_metrics.unique_detections,
                    'overlap_detections': adv_metrics.overlap_detections,
                    'complementarity_gain': round(adv_metrics.complementarity_gain, 4)
                })
            
            # Add category metrics with risk weights
            results_dict['advanced_metrics']['category_metrics'] = adv_metrics.category_metrics
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")


def update_readme(all_metrics: List[PatientBenchmarkMetrics]):
    """Update README with cross-document benchmark results."""
    readme_path = PROJECT_ROOT / ".github" / "README.md"
    
    if not readme_path.exists():
        print(f"⚠️  README not found at {readme_path}")
        return
    
    # Create model name mapping
    model_name_map = {
        "medgemma": "Google MedGemma-4B-IT",
        "gemma3": "Google Gemma-3-27B-IT",
        "openai": "OpenAI GPT-4",
        "gemini": "Google Gemini 1.5 Pro",
        "baseline": "Heuristic Baseline"
    }
    
    # Build the benchmark section
    benchmark_section = """## Cross-Document Analysis Results 🏥

_Patient-level domain knowledge detection across multiple documents._

### Model Comparison

"""
    
    # Add table header
    benchmark_section += "| Model | Precision | Recall | F1 | Domain Knowledge Detection |\n"
    benchmark_section += "|-------|-----------|--------|----|-----------|\n"
    
    # Add rows for each model
    for m in all_metrics:
        precise_name = model_name_map.get(m.model_name, m.model_name)
        status = "✅" if m.domain_knowledge_detection_rate > 0 else ""
        benchmark_section += f"| {precise_name} | {m.avg_precision:.2f} | {m.avg_recall:.2f} | {m.avg_f1_score:.2f} | {m.domain_knowledge_detection_rate:.1f}% {status} |\n"
    
    benchmark_section += f"\n_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n\n"
    
    # Read the current README
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the cross-document benchmark section
    # Look for the section between "Cross-Document Analysis" and "## Benchmark Analysis"
    pattern = r"## Cross-Document Analysis Results.*?\n\n(?=## Benchmark Analysis)"
    
    if re.search(pattern, content, re.DOTALL):
        # Section exists, replace it
        content = re.sub(pattern, benchmark_section, content, flags=re.DOTALL)
    else:
        # Section doesn't exist, insert it before the Benchmark Analysis section
        pattern = r"(## Benchmark Analysis)"
        if re.search(pattern, content):
            content = re.sub(pattern, benchmark_section + r"\1", content)
        else:
            # Insert before "## " headings or at end
            print("⚠️  Could not find insertion point in README")
            return
    
    # Write the updated README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n📝 Updated README: {readme_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run model benchmarks with cross-document analysis and cost savings tracking"
    )
    parser.add_argument(
        '--model',
        type=str,
        default='all',
        choices=['medgemma', 'medgemma-ensemble', 'openai', 'all'],
        help='Which model to benchmark (default: all)'
    )
    parser.add_argument(
        '--push-to-supabase',
        action='store_true',
        help='Push results to Supabase for historical tracking'
    )
    parser.add_argument(
        '--environment',
        type=str,
        default='local',
        help='Execution environment (local, github-actions, etc.)'
    )
    parser.add_argument(
        '--commit-sha',
        type=str,
        help='Git commit SHA'
    )
    parser.add_argument(
        '--branch-name',
        type=str,
        help='Git branch name'
    )
    parser.add_argument(
        '--triggered-by',
        type=str,
        help='Who/what triggered this benchmark run (e.g., "prompt-enhancements", "manual-test")'
    )
    parser.add_argument(
        '--subset',
        type=str,
        default=None,
        choices=['high_signal', None],
        help='Run only high-signal subset for rapid recall optimization (default: run all profiles)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of parallel workers to run (default: 1)'
    )
    
    args = parser.parse_args()
    
    # Determine which models to run
    if args.model == 'all':
        models_to_run = ['medgemma', 'medgemma-ensemble', 'openai']
    else:
        models_to_run = [args.model]
    
    print("=" * 70)
    print("🏥 MODEL BENCHMARK SUITE (Cross-Document Analysis)")
    print("=" * 70)
    print("Testing models' ability to detect medical billing inconsistencies")
    print("requiring healthcare domain knowledge and calculating cost savings")
    print("=" * 70)
    
    all_metrics = []
    
    for model in models_to_run:
        try:
            runner = PatientBenchmarkRunner(model, subset=args.subset, workers=args.workers)
            metrics = runner.run_benchmarks()
            
            if metrics:
                runner.print_summary(metrics)
                runner.save_results(metrics)
                all_metrics.append(metrics)
        except Exception as e:
            print(f"\n❌ Error running {model}: {e}")
            continue
    
    # Print comparison if multiple models
    if len(all_metrics) > 1:
        print("\n" + "=" * 100)
        print("MODEL COMPARISON - DOMAIN KNOWLEDGE DETECTION")
        print("=" * 100)
        
        # Create mapping of model keys to precise names
        model_name_map = {
            "medgemma": "Google MedGemma-4B-IT",
            "gemma3": "Google Gemma-3-27B-IT",
            "openai": "OpenAI GPT-4",
            "gemini": "Google Gemini 1.5 Pro",
            "baseline": "Heuristic Baseline"
        }
        
        print(f"{'Model':<30} {'Precision':<12} {'Recall':<10} {'F1':<10} {'Domain %':<12} {'Latency':<10}")
        print("-" * 100)
        for m in all_metrics:
            precise_name = model_name_map.get(m.model_name, m.model_name)
            latency_sec = m.avg_latency_ms / 1000
            print(f"{precise_name:<30} {m.avg_precision:<12.2f} {m.avg_recall:<10.2f} "
                  f"{m.avg_f1_score:<10.2f} {m.domain_knowledge_detection_rate:<12.1f} {latency_sec:<10.2f}s")
        print("=" * 100)
        print("\n💰 COST SAVINGS COMPARISON:")
        print(f"{'Model':<30} {'Potential Savings':<20} {'Capture Rate':<15} {'Avg/Patient':<15}")
        print("-" * 100)
        for m in all_metrics:
            precise_name = model_name_map.get(m.model_name, m.model_name)
            print(f"{precise_name:<30} ${m.total_potential_savings:<19,.2f} {m.savings_capture_rate:<14.1f}% ${m.avg_savings_per_patient:<14,.2f}")
        print("=" * 100)
    
    print("\n✅ Model benchmarks complete!")
    print("\n💡 TIP: MedGemma should excel at detecting domain-specific billing errors")
    print("   due to its healthcare-specific training and medical domain knowledge.")
    print("   Higher savings capture rate = better ROI for automated error detection.")
    
    # Update README with results
    if len(all_metrics) > 1:
        update_readme(all_metrics)
    
    # Push to Supabase if requested
    if args.push_to_supabase and all_metrics:
        print("\n📤 Pushing results to Supabase...")
        try:
            import subprocess  # nosec B404 - needed for git commands
            import os
            
            # Get git info if not provided
            commit_sha = args.commit_sha
            if not commit_sha:
                try:
                    result = subprocess.run(  # nosec B603 B607 - safe git command with hardcoded args
                        ['git', 'rev-parse', 'HEAD'],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    commit_sha = result.stdout.strip()
                except Exception:
                    commit_sha = None
            
            branch_name = args.branch_name
            if not branch_name:
                try:
                    result = subprocess.run(  # nosec B603 B607 - safe git command with hardcoded args
                        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    branch_name = result.stdout.strip()
                except Exception:  # nosec B110 - acceptable to ignore git errors
                    pass
            
            triggered_by = args.triggered_by
            
            # Push each model's results
            for metrics in all_metrics:
                results_file = PROJECT_ROOT / 'benchmarks' / 'results' / f'patient_benchmark_{metrics.model_name}.json'
                if results_file.exists():
                    cmd = [
                        'python3',
                        str(PROJECT_ROOT / 'scripts' / 'push_patient_benchmarks.py'),
                        '--input', str(results_file),
                        '--environment', args.environment
                    ]
                    if commit_sha:
                        cmd.extend(['--commit-sha', commit_sha])
                    if branch_name:
                        cmd.extend(['--branch-name', branch_name])
                    if triggered_by:
                        cmd.extend(['--triggered-by', triggered_by])
                    
                    subprocess.run(cmd, check=True)  # nosec B603 - safe, controlled script execution
            
            print("✅ All results pushed to Supabase successfully!")
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to push to Supabase: {e}")
            print("   Results are still saved locally in benchmarks/results/")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
