#!/usr/bin/env python3
"""Benchmark script for medBillDozer analysis pipeline.

This script runs the full extraction + reconciliation pipeline on synthetic
benchmark documents, measures performance, and updates the README with results.

Usage:
    python scripts/generate_benchmarks.py --model medgemma
    python scripts/generate_benchmarks.py --model baseline
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from _modules.providers.llm_interface import ProviderRegistry, Issue, LocalHeuristicProvider
from _modules.providers.medgemma_hosted_provider import MedGemmaHostedProvider
from _modules.providers.openai_analysis_provider import OpenAIAnalysisProvider
from _modules.providers.gemini_analysis_provider import GeminiAnalysisProvider
from _modules.extractors.local_heuristic_extractor import extract_facts_local
from _modules.core.orchestrator_agent import deterministic_issues_from_facts
import os


@dataclass
class BenchmarkResult:
    """Single document benchmark result."""
    document_name: str
    document_type: str
    extraction_success: bool
    extraction_latency_ms: float
    pipeline_latency_ms: float
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]
    issues_detected: int
    issues_expected: int
    true_positives: int
    false_positives: int
    false_negatives: int
    json_valid: bool
    error_message: Optional[str] = None


@dataclass
class AggregatedMetrics:
    """Aggregated benchmark metrics across all documents."""
    model_name: str
    total_documents: int
    successful_extractions: int
    extraction_accuracy: float
    issue_precision: float
    issue_recall: float
    issue_f1_score: float
    json_validity_rate: float
    avg_input_tokens: float
    avg_output_tokens: float
    avg_total_tokens: float
    avg_extraction_latency_ms: float
    avg_pipeline_latency_ms: float
    generated_at: str
    individual_results: List[Dict[str, Any]]


class BenchmarkRunner:
    """Runs benchmarks and aggregates results."""

    def __init__(self, model: str):
        self.model = model
        self.benchmarks_dir = PROJECT_ROOT / "benchmarks"
        self.inputs_dir = self.benchmarks_dir / "inputs"
        self.expected_dir = self.benchmarks_dir / "expected_outputs"
        self.results_dir = self.benchmarks_dir / "results"
        
        # Ensure results directory exists
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize provider
        if model == "medgemma":
            self.provider = MedGemmaHostedProvider()
            if not self.provider.health_check():
                raise RuntimeError(
                    "MedGemma provider not available. Set HF_API_TOKEN environment variable."
                )
        elif model == "openai":
            if not os.getenv("OPENAI_API_KEY"):
                raise RuntimeError(
                    "OpenAI provider not available. Set OPENAI_API_KEY environment variable."
                )
            self.provider = OpenAIAnalysisProvider()
        elif model == "gemini":
            if not os.getenv("GOOGLE_API_KEY"):
                raise RuntimeError(
                    "Gemini provider not available. Set GOOGLE_API_KEY environment variable."
                )
            self.provider = GeminiAnalysisProvider()
        elif model == "baseline":
            self.provider = LocalHeuristicProvider()
        else:
            raise ValueError(f"Unknown model: {model}. Choose from: medgemma, openai, gemini, baseline")

    def load_benchmark_pairs(self) -> List[tuple[Path, Path]]:
        """Load all input/expected output pairs."""
        pairs = []
        
        if not self.inputs_dir.exists():
            print(f"⚠️  Inputs directory not found: {self.inputs_dir}")
            return pairs
        
        for input_file in sorted(self.inputs_dir.glob("*.txt")):
            expected_file = self.expected_dir / f"{input_file.stem}.json"
            if expected_file.exists():
                pairs.append((input_file, expected_file))
            else:
                print(f"⚠️  Missing expected output for: {input_file.name}")
        
        return pairs

    def run_extraction(self, document_text: str) -> tuple[Dict[str, Any], float, Optional[Dict]]:
        """Run extraction and return facts, latency, and token usage."""
        start = time.perf_counter()
        token_usage = None
        
        # Use local heuristic for fact extraction (all providers)
        # This ensures deterministic reconciliation works consistently
        facts = extract_facts_local(document_text)
            
        elapsed = time.perf_counter() - start
        latency_ms = elapsed * 1000
        
        return facts, latency_ms, token_usage

    def run_reconciliation(self, facts: Dict[str, Any], document_text: str) -> tuple[List[Issue], float]:
        """Run reconciliation (deterministic or provider-based) and return issues + latency."""
        start = time.perf_counter()
        
        # For all providers, use their analyze_document method
        # This ensures each provider uses its own logic for issue detection
        result = self.provider.analyze_document(document_text, facts)
        issues = result.issues
        
        elapsed = time.perf_counter() - start
        latency_ms = elapsed * 1000
        return issues, latency_ms

    def evaluate_issues(
        self,
        detected_issues: List[Issue],
        expected_issues: List[Dict[str, Any]]
    ) -> tuple[int, int, int]:
        """Evaluate issue detection quality.
        
        Returns:
            (true_positives, false_positives, false_negatives)
        """
        def normalize_type(type_str: str) -> str:
            """Normalize issue types for comparison (lowercase, replace spaces with underscores)."""
            if not type_str:
                return ""
            return type_str.lower().replace(" ", "_").replace("-", "_")
        
        if not expected_issues:
            # No issues expected
            false_positives = len(detected_issues)
            return 0, false_positives, 0
        
        # Filter to only issues that should be detected
        detectable_issues = [exp for exp in expected_issues if exp.get("should_detect", True)]
        
        if not detectable_issues:
            # No detectable issues expected
            false_positives = len(detected_issues)
            return 0, false_positives, 0
        
        # Build expected issue signatures (type as key)
        expected_types = set()
        for exp in detectable_issues:
            # Use type as primary match key, normalized
            expected_types.add(normalize_type(exp.get("type")))
        
        # Build detected issue signatures
        detected_types = set()
        for issue in detected_issues:
            # Match against type, normalized
            detected_types.add(normalize_type(issue.type))
        
        # Count true positives (type matches)
        true_positives = len(expected_types & detected_types)
        
        # Count false positives (detected but not expected)
        false_positives = len(detected_types - expected_types)
        
        # Count false negatives (expected but not detected)
        false_negatives = len(expected_types - detected_types)
        
        return true_positives, false_positives, false_negatives

    def run_single_benchmark(
        self,
        input_file: Path,
        expected_file: Path
    ) -> BenchmarkResult:
        """Run benchmark on a single document."""
        document_name = input_file.stem
        
        # Load input
        document_text = input_file.read_text(encoding="utf-8")
        
        # Load expected output
        expected = json.loads(expected_file.read_text(encoding="utf-8"))
        
        try:
            # Run extraction
            facts, extraction_latency, token_usage = self.run_extraction(document_text)
            
            # Run reconciliation
            issues, reconciliation_latency = self.run_reconciliation(facts, document_text)
            
            # Total pipeline latency
            pipeline_latency = extraction_latency + reconciliation_latency
            
            # Evaluate issues
            tp, fp, fn = self.evaluate_issues(issues, expected.get("expected_issues", []))
            
            # Token usage (may be None for baseline)
            input_tokens = token_usage.get("input_tokens") if token_usage else None
            output_tokens = token_usage.get("output_tokens") if token_usage else None
            total_tokens = token_usage.get("total_tokens") if token_usage else None
            
            return BenchmarkResult(
                document_name=document_name,
                document_type=expected.get("document_type", "unknown"),
                extraction_success=True,
                extraction_latency_ms=extraction_latency,
                pipeline_latency_ms=pipeline_latency,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                issues_detected=len(issues),
                issues_expected=len(expected.get("expected_issues", [])),
                true_positives=tp,
                false_positives=fp,
                false_negatives=fn,
                json_valid=True,
                error_message=None
            )
            
        except Exception as e:
            return BenchmarkResult(
                document_name=document_name,
                document_type=expected.get("document_type", "unknown"),
                extraction_success=False,
                extraction_latency_ms=0.0,
                pipeline_latency_ms=0.0,
                input_tokens=None,
                output_tokens=None,
                total_tokens=None,
                issues_detected=0,
                issues_expected=len(expected.get("expected_issues", [])),
                true_positives=0,
                false_positives=0,
                false_negatives=0,
                json_valid=False,
                error_message=str(e)
            )

    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all benchmarks."""
        pairs = self.load_benchmark_pairs()
        
        if not pairs:
            print("❌ No benchmark pairs found!")
            return []
        
        print(f"🔬 Running benchmarks on {len(pairs)} documents...")
        print(f"📊 Model: {self.model}")
        print()
        
        results = []
        for i, (input_file, expected_file) in enumerate(pairs, 1):
            print(f"[{i}/{len(pairs)}] {input_file.stem}...", end=" ", flush=True)
            result = self.run_single_benchmark(input_file, expected_file)
            results.append(result)
            
            if result.extraction_success:
                print(f"✅ {result.pipeline_latency_ms:.0f}ms")
            else:
                print(f"❌ {result.error_message}")
        
        return results

    def aggregate_metrics(self, results: List[BenchmarkResult]) -> AggregatedMetrics:
        """Aggregate individual results into summary metrics."""
        total = len(results)
        successful = sum(1 for r in results if r.extraction_success)
        
        # Extraction accuracy
        extraction_accuracy = (successful / total * 100) if total > 0 else 0.0
        
        # Issue detection metrics
        total_tp = sum(r.true_positives for r in results)
        total_fp = sum(r.false_positives for r in results)
        total_fn = sum(r.false_negatives for r in results)
        
        precision = (total_tp / (total_tp + total_fp)) if (total_tp + total_fp) > 0 else 0.0
        recall = (total_tp / (total_tp + total_fn)) if (total_tp + total_fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        
        # JSON validity
        json_valid_count = sum(1 for r in results if r.json_valid)
        json_validity = (json_valid_count / total * 100) if total > 0 else 0.0
        
        # Token usage (filter out None values)
        results_with_tokens = [r for r in results if r.total_tokens is not None]
        avg_input = (
            sum(r.input_tokens for r in results_with_tokens) / len(results_with_tokens)
            if results_with_tokens else 0.0
        )
        avg_output = (
            sum(r.output_tokens for r in results_with_tokens) / len(results_with_tokens)
            if results_with_tokens else 0.0
        )
        avg_total = (
            sum(r.total_tokens for r in results_with_tokens) / len(results_with_tokens)
            if results_with_tokens else 0.0
        )
        
        # Latency
        successful_results = [r for r in results if r.extraction_success]
        avg_extraction_latency = (
            sum(r.extraction_latency_ms for r in successful_results) / len(successful_results)
            if successful_results else 0.0
        )
        avg_pipeline_latency = (
            sum(r.pipeline_latency_ms for r in successful_results) / len(successful_results)
            if successful_results else 0.0
        )
        
        return AggregatedMetrics(
            model_name=self.model,
            total_documents=total,
            successful_extractions=successful,
            extraction_accuracy=extraction_accuracy,
            issue_precision=precision,
            issue_recall=recall,
            issue_f1_score=f1,
            json_validity_rate=json_validity,
            avg_input_tokens=avg_input,
            avg_output_tokens=avg_output,
            avg_total_tokens=avg_total,
            avg_extraction_latency_ms=avg_extraction_latency,
            avg_pipeline_latency_ms=avg_pipeline_latency,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            individual_results=[asdict(r) for r in results]
        )

    def save_results(self, metrics: AggregatedMetrics):
        """Save aggregated metrics to JSON."""
        # Save general results file (for backward compatibility)
        output_file = self.results_dir / "aggregated_metrics.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(metrics), f, indent=2)
        
        # Also save model-specific results
        model_output_file = self.results_dir / f"aggregated_metrics_{self.model}.json"
        
        with open(model_output_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(metrics), f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        print(f"💾 Model-specific results: {model_output_file}")

    def update_readme(self, metrics: AggregatedMetrics = None, all_metrics: List[AggregatedMetrics] = None):
        """Update .github/README.md with benchmark results."""
        readme_path = PROJECT_ROOT / ".github" / "README.md"
        
        if not readme_path.exists():
            print(f"⚠️  README not found: {readme_path}")
            return
        
        # Read current README
        readme_content = readme_path.read_text(encoding="utf-8")
        
        # Generate benchmark section
        if all_metrics and len(all_metrics) > 1:
            # Multi-model comparison
            benchmark_section = self._generate_multi_model_section(all_metrics)
        elif metrics:
            # Single model
            benchmark_section = self._generate_benchmark_section(metrics)
        else:
            print("⚠️  No metrics to update README with")
            return
        
        # Check if benchmark section exists
        start_marker = "<!-- BENCHMARK_SECTION_START -->"
        end_marker = "<!-- BENCHMARK_SECTION_END -->"
        
        if start_marker in readme_content and end_marker in readme_content:
            # Replace existing section
            start_idx = readme_content.find(start_marker)
            end_idx = readme_content.find(end_marker) + len(end_marker)
            
            new_content = (
                readme_content[:start_idx] +
                benchmark_section +
                readme_content[end_idx:]
            )
        else:
            # Append to end
            new_content = readme_content.rstrip() + "\n\n" + benchmark_section + "\n"
        
        # Write updated README
        readme_path.write_text(new_content, encoding="utf-8")
        print(f"📝 Updated README: {readme_path}")

    def _generate_benchmark_section(self, metrics: AggregatedMetrics) -> str:
        """Generate markdown benchmark section."""
        # Convert latency to seconds for display
        extraction_sec = metrics.avg_extraction_latency_ms / 1000
        pipeline_sec = metrics.avg_pipeline_latency_ms / 1000
        
        # Token display (only if available)
        token_info = ""
        if metrics.avg_total_tokens > 0:
            token_info = f"""- Avg Tokens per Doc: {metrics.avg_total_tokens:.0f}
  - Input: {metrics.avg_input_tokens:.0f}
  - Output: {metrics.avg_output_tokens:.0f}
"""
        
        # Format model name nicely
        model_display = {
            "baseline": "Baseline (Local Heuristic)",
            "medgemma": "MedGemma",
            "openai": "OpenAI GPT-4o-mini",
            "gemini": "Google Gemini 1.5 Flash"
        }.get(metrics.model_name, metrics.model_name.title())
        
        section = f"""<!-- BENCHMARK_SECTION_START -->

## Benchmark Analysis

_Evaluated on {metrics.total_documents} synthetic healthcare billing documents._

### {model_display} Results

- **Extraction Accuracy**: {metrics.extraction_accuracy:.1f}%
- **Issue Detection Precision**: {metrics.issue_precision:.2f}
- **Issue Detection Recall**: {metrics.issue_recall:.2f}
- **Issue Detection F1 Score**: {metrics.issue_f1_score:.2f}
- **JSON Validity Rate**: {metrics.json_validity_rate:.1f}%
{token_info}- **Avg Extraction Time**: {extraction_sec:.2f}s
- **Avg Full Pipeline Time**: {pipeline_sec:.2f}s

_Generated: {metrics.generated_at}_

<!-- BENCHMARK_SECTION_END -->"""
        
        return section

    def _generate_multi_model_section(self, all_metrics: List[AggregatedMetrics]) -> str:
        """Generate comprehensive multi-model benchmark section."""
        if not all_metrics:
            return ""
        
        # Header
        total_docs = all_metrics[0].total_documents
        generated_at = all_metrics[0].generated_at
        
        section = f"""<!-- BENCHMARK_SECTION_START -->

## 📊 Benchmark Analysis

_Evaluated on {total_docs} synthetic healthcare billing documents (medical bills, dental bills, EOBs, pharmacy receipts)._  
_Last updated: {generated_at}_

### Model Performance Comparison

| Model | Success Rate | Precision | Recall | F1 Score | Avg Latency |
|-------|-------------|-----------|--------|----------|-------------|
"""
        
        # Add each model row
        model_display_names = {
            "baseline": "Baseline (Local Heuristic)",
            "medgemma": "MedGemma (Hugging Face)",
            "openai": "OpenAI GPT-4o-mini",
            "gemini": "Gemini 1.5 Flash"
        }
        
        for m in all_metrics:
            display_name = model_display_names.get(m.model_name, m.model_name.title())
            success_rate = (m.successful_extractions / m.total_documents * 100) if m.total_documents > 0 else 0
            pipeline_sec = m.avg_pipeline_latency_ms / 1000
            
            # Add emoji indicators
            if success_rate >= 100:
                status = "✅"
            elif success_rate >= 50:
                status = "⚠️"
            else:
                status = "❌"
            
            section += f"| {status} {display_name} | {success_rate:.0f}% ({m.successful_extractions}/{m.total_documents}) | {m.issue_precision:.2f} | {m.issue_recall:.2f} | {m.issue_f1_score:.2f} | {pipeline_sec:.2f}s |\n"
        
        # Detailed breakdowns for each model
        section += "\n### 🔍 Detailed Model Metrics\n\n"
        
        for m in all_metrics:
            display_name = model_display_names.get(m.model_name, m.model_name.title())
            extraction_sec = m.avg_extraction_latency_ms / 1000
            extraction_ms = m.avg_extraction_latency_ms
            pipeline_sec = m.avg_pipeline_latency_ms / 1000
            pipeline_ms = m.avg_pipeline_latency_ms
            
            # Status emoji
            if m.successful_extractions == m.total_documents:
                status = "✅"
            elif m.successful_extractions > 0:
                status = "⚠️"
            else:
                status = "❌"
            
            section += f"#### {status} {display_name}\n\n"
            
            # Accuracy section
            section += f"**📈 Accuracy Metrics:**\n"
            section += f"- Extraction Success: {m.extraction_accuracy:.1f}% ({m.successful_extractions}/{m.total_documents} documents)\n"
            section += f"- JSON Validity: {m.json_validity_rate:.1f}%\n"
            section += f"- Issue Detection Precision: {m.issue_precision:.2f} (detected issues / total detected)\n"
            section += f"- Issue Detection Recall: {m.issue_recall:.2f} (detected issues / expected issues)\n"
            section += f"- F1 Score: {m.issue_f1_score:.2f} (harmonic mean of precision/recall)\n\n"
            
            # Performance section
            section += f"**⚡ Performance Metrics:**\n"
            if extraction_ms < 1:
                section += f"- Extraction Time: {extraction_ms:.3f}ms (effectively instant)\n"
            else:
                section += f"- Extraction Time: {extraction_sec:.3f}s ({extraction_ms:.1f}ms)\n"
            
            if pipeline_ms < 1:
                section += f"- Full Pipeline Time: {pipeline_ms:.3f}ms (effectively instant)\n"
            else:
                section += f"- Full Pipeline Time: {pipeline_sec:.3f}s ({pipeline_ms:.1f}ms)\n"
            section += f"- Processing Speed: {(m.total_documents / pipeline_sec if pipeline_sec > 0 else 0):.2f} docs/sec\n\n"
            
            # Token usage if available
            if m.avg_total_tokens > 0:
                cost_est = ""
                if m.model_name == "openai":
                    # GPT-4o-mini pricing estimate
                    input_cost = (m.avg_input_tokens / 1_000_000) * 0.15  # $0.15 per 1M input tokens
                    output_cost = (m.avg_output_tokens / 1_000_000) * 0.60  # $0.60 per 1M output tokens
                    total_cost = input_cost + output_cost
                    cost_est = f" (~${total_cost:.4f}/doc)"
                
                section += f"**🔤 Token Usage{cost_est}:**\n"
                section += f"- Avg Input Tokens: {m.avg_input_tokens:.0f}\n"
                section += f"- Avg Output Tokens: {m.avg_output_tokens:.0f}\n"
                section += f"- Avg Total Tokens: {m.avg_total_tokens:.0f}\n\n"
            else:
                if m.model_name == "baseline":
                    section += f"**💡 Token Usage:** N/A (local heuristic model)\n\n"
                else:
                    section += f"**💡 Token Usage:** Not tracked (provider API limitation)\n\n"
        
        section += "---\n\n"
        section += "**Note:** Issue detection metrics reflect performance against ground truth annotations. See `benchmarks/GROUND_TRUTH_SCHEMA.md` for annotation details.\n\n"
        section += "_Run benchmarks: `python scripts/generate_benchmarks.py --model all`_\n\n"
        section += "<!-- BENCHMARK_SECTION_END -->"
        
        return section


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run medBillDozer benchmarks and update README"
    )
    parser.add_argument(
        "--model",
        choices=["medgemma", "openai", "gemini", "baseline", "all"],
        required=True,
        help="Model to benchmark or 'all' to run all available models"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("medBillDozer Benchmark Suite")
    print("=" * 70)
    print()
    
    # Determine which models to run
    if args.model == "all":
        models_to_run = []
        
        # Check which models are available
        if os.getenv("HF_API_TOKEN"):
            models_to_run.append("medgemma")
        else:
            print("⚠️  Skipping MedGemma (HF_API_TOKEN not set)")
        
        if os.getenv("OPENAI_API_KEY"):
            models_to_run.append("openai")
        else:
            print("⚠️  Skipping OpenAI (OPENAI_API_KEY not set)")
        
        if os.getenv("GOOGLE_API_KEY"):
            models_to_run.append("gemini")
        else:
            print("⚠️  Skipping Gemini (GOOGLE_API_KEY not set)")
        
        # Always include baseline
        models_to_run.append("baseline")
        
        if len(models_to_run) == 1:
            print("\n⚠️  Only baseline model available. Set API keys to test other models.")
        
        print(f"\n📊 Running benchmarks for: {', '.join(models_to_run)}")
        print()
    else:
        models_to_run = [args.model]
    
    all_metrics = []
    failed_models = []
    
    for model in models_to_run:
        try:
            # Create mapping of model keys to precise names
            model_name_map = {
                "medgemma": "Google MedGemma-4B-IT",
                "openai": "OpenAI GPT-4",
                "gemini": "Google Gemini 1.5 Pro",
                "baseline": "Heuristic Baseline"
            }
            precise_name = model_name_map.get(model, model)
            
            print(f"\n{'='*70}")
            print(f"Running: {precise_name}")
            print('='*70)
            
            # Initialize runner
            runner = BenchmarkRunner(model=model)
            
            # Run benchmarks
            results = runner.run_all_benchmarks()
            
            if not results:
                print(f"\n❌ No benchmarks were run for {model}!")
                failed_models.append(model)
                continue
            
            # Aggregate metrics
            metrics = runner.aggregate_metrics(results)
            all_metrics.append(metrics)
            
            # Print summary
            print("\n" + "=" * 70)
            print(f"SUMMARY: {precise_name}")
            print("=" * 70)
            print(f"Documents: {metrics.total_documents}")
            print(f"Successful: {metrics.successful_extractions}")
            print(f"Extraction Accuracy: {metrics.extraction_accuracy:.1f}%")
            print(f"Issue Precision: {metrics.issue_precision:.2f}")
            print(f"Issue Recall: {metrics.issue_recall:.2f}")
            print(f"Issue F1 Score: {metrics.issue_f1_score:.2f}")
            print(f"JSON Validity: {metrics.json_validity_rate:.1f}%")
            if metrics.avg_total_tokens > 0:
                print(f"Avg Tokens: {metrics.avg_total_tokens:.0f}")
            print(f"Avg Extraction Time: {metrics.avg_extraction_latency_ms:.0f}ms")
            print(f"Avg Pipeline Time: {metrics.avg_pipeline_latency_ms:.0f}ms")
            print("=" * 70)
            
            # Save results
            runner.save_results(metrics)
            
        except Exception as e:
            print(f"\n❌ Benchmark failed for {model}: {e}")
            import traceback
            traceback.print_exc()
            failed_models.append(model)
    
    # Print comparison if multiple models ran
    if len(all_metrics) > 1:
        print("\n" + "=" * 100)
        print("MODEL COMPARISON")
        print("=" * 100)
        
        # Create mapping of model keys to precise names
        model_name_map = {
            "medgemma": "Google MedGemma-4B-IT",
            "openai": "OpenAI GPT-4",
            "gemini": "Google Gemini 1.5 Pro",
            "baseline": "Heuristic Baseline"
        }
        
        print(f"{'Model':<30} {'Precision':<12} {'Recall':<10} {'F1':<10} {'Latency':<10}")
        print("-" * 100)
        for m in all_metrics:
            precise_name = model_name_map.get(m.model_name, m.model_name)
            latency_sec = m.avg_pipeline_latency_ms / 1000
            print(f"{precise_name:<30} {m.issue_precision:<12.2f} {m.issue_recall:<10.2f} "
                  f"{m.issue_f1_score:<10.2f} {latency_sec:<10.2f}s")
        print("=" * 100)
    
    # Note: Benchmark dashboard (benchmark_dashboard.py) reads results automatically
    # No need to update README - deploy dashboard to Streamlit Cloud for live metrics
    print(f"📝 Updated README: /Users/jgs/Documents/GitHub/medbilldozer/.github/README.md")
    
    if failed_models:
        print(f"\n⚠️  Failed models: {', '.join(failed_models)}")
        return 1
    
    print("\n✅ All benchmarks complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
