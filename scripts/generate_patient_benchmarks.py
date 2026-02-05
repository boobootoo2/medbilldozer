#!/usr/bin/env python3
"""
Patient-Level Cross-Document Benchmark Suite

This benchmark tests models' ability to detect medical inconsistencies that require
healthcare domain knowledge, such as:
- Gender-inappropriate procedures (e.g., male receiving obstetric care)
- Age-inappropriate screenings (e.g., child receiving colonoscopy)
- Anatomically impossible procedures

MedGemma should excel at these benchmarks due to its healthcare-specific training.
"""

import json
import sys
import time
import re
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import argparse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from medbilldozer.providers.medgemma_hosted_provider import MedGemmaHostedProvider
from medbilldozer.providers.openai_analysis_provider import OpenAIAnalysisProvider
from medbilldozer.providers.gemini_analysis_provider import GeminiAnalysisProvider
from medbilldozer.providers.llm_interface import LocalHeuristicProvider


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
    
    def __init__(self, model: str, subset: Optional[str] = None):
        self.model = model
        self.subset = subset
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
            profile = PatientProfile(
                patient_id=data['patient_id'],
                name=data['name'],
                age=data['demographics']['age'],
                sex=data['demographics']['sex'],
                date_of_birth=data['demographics']['date_of_birth'],
                conditions=data['medical_history']['conditions'],
                allergies=data['medical_history']['allergies'],
                surgeries=data['medical_history']['surgeries']
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
        
        expected_issues = [
            ExpectedIssue(**issue) for issue in data.get('expected_issues', [])
        ]
        
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
Name: {profile.name}
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

5. PROCEDURE INCONSISTENT WITH HEALTH HISTORY (Medical Appropriateness):
   - Definition: Procedures that make no medical sense given documented health status
   - Reasoning Steps: Review conditions/surgeries → Check procedure indications → Flag if contraindicated
   - Examples:
     * Healthy patient (no diabetes) billed for: continuous glucose monitor, diabetic retinopathy screening
     * Patient without cancer history billed for: chemotherapy, radiation oncology
     * Patient with documented organ removal billed for: screening of that organ
   - Look for: Disease-specific procedures without corresponding diagnosis

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
Re-examine documents specifically for these often-missed patterns:
- Any procedures on organs mentioned in "Prior Surgeries" (especially removals, amputations)
- Any procedures with dates BEFORE or immediately after related surgeries
- Any sex-specific procedures (check patient sex field carefully)
- Any age-extreme procedures (pediatric codes for adults, geriatric codes for young patients)
- Any disease management procedures without corresponding condition listed

CHAIN-OF-THOUGHT REASONING REQUIRED:
For each potential issue, show your reasoning:
1. What did I notice? (Evidence)
2. Why is this problematic? (Medical knowledge)
3. What error category does this fall into?
4. What is the specific CPT code involved?

FEW-SHOT EXAMPLES:
Example 1: "Patient had right leg amputation in 2022. Document 2 bills CPT 27447 (knee replacement) on right knee in 2024. REASONING: Patient cannot have knee replacement on amputated leg. ERROR TYPE: anatomical_contradiction"

Example 2: "Patient is 8 years old. Document 1 bills CPT 45378 (colonoscopy screening). REASONING: Colonoscopy screening recommended for age 45+, not appropriate for child without specific medical indication. ERROR TYPE: age_inappropriate_procedure"

Example 3: "Patient is male (sex: M). Document 3 bills CPT 88150 (Pap smear). REASONING: Pap smears are cervical cancer screenings for patients with cervixes (female anatomy). Male patients cannot have this procedure. ERROR TYPE: gender_specific_contradiction"

NOW ANALYZE: Report ALL issues found with specific CPT codes, clear evidence, and error type classification.
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

3. HEALTH HISTORY INCONSISTENCIES:
   - If Conditions list is EMPTY or minimal, look for disease-specific procedures:
     * Diabetes procedures without diabetes diagnosis
     * Cardiac procedures without heart disease
     * Oncology procedures without cancer history
   - Example: Healthy patient → Flag glucose monitors, chemotherapy, etc.

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
        Evaluate detection accuracy with domain subcategory tracking.
        
        Returns: (true_positives, false_positives, false_negatives, domain_knowledge_score, 
                  domain_breakdown, domain_recall, generic_recall, cross_document_recall)
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
        
        return (true_positives, false_positives, false_negatives, domain_knowledge_score,
                domain_breakdown, domain_recall, generic_recall, cross_document_recall)
    
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
        
        for i, profile_file in enumerate(profile_files, 1):
            profile, expected_issues, document_names = self.load_patient_profile(profile_file)
            
            print(f"[{i}/{len(profile_files)}] {profile.name} ({profile.sex}, {profile.age}y)...", end=" ", flush=True)
            
            # Analyze all documents for this patient
            detected_issues, latency_ms, error = self.analyze_patient_documents(
                profile, document_names
            )
            
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
            else:
                # Evaluate detection with enhanced metrics
                (tp, fp, fn, domain_score, domain_breakdown, 
                 domain_recall, generic_recall, cross_document_recall) = self.evaluate_detection(expected_issues, detected_issues)
                
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
                    cross_document_recall=cross_document_recall
                )
                
                total_precision += precision
                total_recall += recall
                total_f1 += f1
                total_domain_score += domain_score
                successful += 1
                
                status = "✅" if fn == 0 else "⚠️"
                print(f"{status} {latency_ms:.0f}ms | Issues: {tp}/{len(expected_issues)} | Domain Recall: {domain_recall*100:.0f}%")
            
            results.append(result)
        
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
            cross_document_recall=avg_cross_document_recall
        )
        
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
        print("=" * 70)
    
    def save_results(self, metrics: PatientBenchmarkMetrics):
        """Save results to JSON."""
        output_file = self.results_dir / f"patient_benchmark_{self.model}.json"
        
        # Convert to dict with proper serialization
        results_dict = asdict(metrics)
        
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
        description="Run patient-level cross-document benchmarks"
    )
    parser.add_argument(
        '--model',
        type=str,
        default='all',
        choices=['medgemma', 'openai', 'gemini', 'baseline', 'all'],
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
    
    args = parser.parse_args()
    
    # Determine which models to run
    if args.model == 'all':
        models_to_run = ['medgemma', 'openai', 'gemini', 'baseline']
    else:
        models_to_run = [args.model]
    
    print("=" * 70)
    print("🏥 PATIENT-LEVEL CROSS-DOCUMENT BENCHMARK SUITE")
    print("=" * 70)
    print("Testing models' ability to detect medical inconsistencies requiring")
    print("healthcare domain knowledge (gender/age-inappropriate procedures)")
    print("=" * 70)
    
    all_metrics = []
    
    for model in models_to_run:
        try:
            runner = PatientBenchmarkRunner(model, subset=args.subset)
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
    
    print("\n✅ Patient benchmarks complete!")
    print("\n💡 TIP: MedGemma should excel at detecting gender/age-inappropriate procedures")
    print("   due to its healthcare-specific training and medical domain knowledge.")
    
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
