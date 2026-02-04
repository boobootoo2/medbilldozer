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

from _modules.providers.medgemma_hosted_provider import MedGemmaHostedProvider
from _modules.providers.openai_analysis_provider import OpenAIAnalysisProvider
from _modules.providers.gemini_analysis_provider import GeminiAnalysisProvider
from _modules.providers.llm_interface import LocalHeuristicProvider


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


class PatientBenchmarkRunner:
    """Runs cross-document patient-level benchmarks."""
    
    def __init__(self, model: str):
        self.model = model
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
Please analyze ALL documents together for this patient, using the medical history for context.
Look for:
1. Procedures that don't match the patient's gender (e.g., male receiving obstetric care)
2. Procedures that don't match the patient's age (e.g., child receiving adult screening)
3. Procedures that are medically inappropriate given patient demographics
4. Any procedures that contradict the patient's medical history
5. Any duplicate charges across documents
6. Any billing inconsistencies across the patient's documents

Focus especially on gender-specific and age-specific procedures that require medical domain knowledge.
"""
            
            # Call provider with combined patient context
            # Pass None for facts since the context is already embedded in the text
            result = self.provider.analyze_document(patient_context, facts=None)
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            # Extract detected issues from AnalysisResult object
            detected_issues = []
            if result and hasattr(result, 'issues'):
                # Convert Issue objects to dicts for evaluation
                detected_issues = [
                    {
                        'type': issue.type,
                        'summary': issue.summary,
                        'evidence': issue.evidence,
                        'code': issue.code,
                        'max_savings': issue.max_savings
                    }
                    for issue in result.issues
                ]
            
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
    
    def evaluate_detection(self, expected: List[ExpectedIssue], detected: List[Dict]) -> tuple:
        """
        Evaluate detection accuracy.
        Returns: (true_positives, false_positives, false_negatives, domain_knowledge_score)
        """
        if not expected:
            # No issues expected, any detection is false positive
            return 0, len(detected), 0, 0.0
        
        # Track which expected issues were matched to avoid double-counting
        matched_expected_indices = set()
        matched_detected_indices = set()
        domain_knowledge_detections = 0
        
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
                    break  # Move to next detected issue
        
        true_positives = len(matched_expected_indices)
        false_positives = len(detected) - len(matched_detected_indices)
        false_negatives = len(expected) - len(matched_expected_indices)
        
        # Calculate domain knowledge score
        domain_knowledge_issues = sum(1 for e in expected if e.requires_domain_knowledge)
        domain_knowledge_score = (domain_knowledge_detections / domain_knowledge_issues * 100) if domain_knowledge_issues > 0 else 0.0
        
        return true_positives, false_positives, false_negatives, domain_knowledge_score
    
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
                # Evaluate detection
                tp, fp, fn, domain_score = self.evaluate_detection(expected_issues, detected_issues)
                
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
                    domain_knowledge_score=domain_score
                )
                
                total_precision += precision
                total_recall += recall
                total_f1 += f1
                total_domain_score += domain_score
                successful += 1
                
                status = "✅" if fn == 0 else "⚠️"
                print(f"{status} {latency_ms:.0f}ms | Issues: {tp}/{len(expected_issues)} | Domain: {domain_score:.0f}%")
            
            results.append(result)
        
        # Calculate aggregated metrics
        avg_precision = total_precision / successful if successful > 0 else 0.0
        avg_recall = total_recall / successful if successful > 0 else 0.0
        avg_f1 = total_f1 / successful if successful > 0 else 0.0
        avg_domain_score = total_domain_score / successful if successful > 0 else 0.0
        avg_latency = sum(r.analysis_latency_ms for r in results) / len(results) if results else 0.0
        
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
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return metrics
    
    def print_summary(self, metrics: PatientBenchmarkMetrics):
        """Print benchmark summary."""
        precise_name = self._get_precise_model_name()
        print("\n" + "=" * 70)
        print(f"PATIENT BENCHMARK SUMMARY: {precise_name}")
        print("=" * 70)
        print(f"Patients Analyzed: {metrics.successful_analyses}/{metrics.total_patients}")
        print(f"Avg Precision: {metrics.avg_precision:.2f}")
        print(f"Avg Recall: {metrics.avg_recall:.2f}")
        print(f"Avg F1 Score: {metrics.avg_f1_score:.2f}")
        print(f"Domain Knowledge Detection Rate: {metrics.domain_knowledge_detection_rate:.1f}%")
        print(f"Avg Analysis Time: {metrics.avg_latency_ms:.0f}ms ({metrics.avg_latency_ms/1000:.2f}s)")
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
            runner = PatientBenchmarkRunner(model)
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
                    # nosec B603 B607 - safe git command with hardcoded args
                    result = subprocess.run(
                        ['git', 'rev-parse', 'HEAD'],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    commit_sha = result.stdout.strip()
                except Exception:
                    commit_sha = None
            
            branch_name = None
            try:
                # nosec B603 B607 - safe git command with hardcoded args
                result = subprocess.run(
                    ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                branch_name = result.stdout.strip()
            except Exception:  # nosec B110 - acceptable to ignore git errors
                pass
            
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
                    
                    subprocess.run(cmd, check=True)  # nosec B603 - safe, controlled script execution
            
            print("✅ All results pushed to Supabase successfully!")
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to push to Supabase: {e}")
            print("   Results are still saved locally in benchmarks/results/")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
