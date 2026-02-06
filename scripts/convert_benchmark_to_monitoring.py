#!/usr/bin/env python3
"""
Convert benchmark results to monitoring format for Supabase persistence.

Usage:
    python scripts/convert_benchmark_to_monitoring.py \
        --input benchmarks/results/aggregated_metrics_openai.json \
        --output benchmark_results.json \
        --model openai
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

def convert_to_monitoring_format(input_file: Path, model_name: str) -> dict:
    """Convert aggregated metrics or patient benchmark results to monitoring format."""
    
    with open(input_file, 'r') as f:
        metrics = json.load(f)
    
    # Detect format: patient benchmark vs aggregated metrics
    is_patient_benchmark = 'total_patients' in metrics
    
    # Extract version info (you can customize this)
    # Model version should match the display name for consistency
    model_display_names = {
        'medgemma': 'Google MedGemma-4B-IT',
        'gemma3': 'Google Gemma-3-27B-IT',
        'gemini': 'Google Gemini 1.5 Pro',
        'openai': 'OpenAI GPT-4',
        'baseline': 'Heuristic Baseline'
    }
    model_version = model_display_names.get(model_name, f"{model_name}-v1.0")
    dataset_version = "patient-benchmark-v2" if is_patient_benchmark else "benchmark-set-v1"
    prompt_version = metrics.get('prompt_version', 'v2-structured-reasoning' if is_patient_benchmark else 'v1')
    
    if is_patient_benchmark:
        # Convert patient benchmark format
        base_metrics = {
            "precision": metrics.get('avg_precision', 0),
            "recall": metrics.get('avg_recall', 0),
            "f1": metrics.get('avg_f1_score', 0),
            "latency_ms": metrics.get('avg_latency_ms', 0),
            "analysis_cost": 0.0,  # Not tracked in patient benchmarks yet
            "total_documents": metrics.get('total_patients', 0),
            "total_issues_detected": sum(r.get('true_positives', 0) for r in metrics.get('individual_results', [])),
            "total_issues_expected": sum(len(r.get('expected_issues', [])) for r in metrics.get('individual_results', [])),
            "domain_recall": metrics.get('domain_recall', 0),
            "domain_precision": metrics.get('domain_precision', 0),
            "generic_recall": metrics.get('generic_recall', 0),
            "cross_document_recall": metrics.get('cross_document_recall', 0),
            "domain_knowledge_detection_rate": metrics.get('domain_knowledge_detection_rate', 0),
            "total_potential_savings": metrics.get('total_potential_savings', 0),
            "total_missed_savings": metrics.get('total_missed_savings', 0),
            "avg_savings_per_patient": metrics.get('avg_savings_per_patient', 0),
            "savings_capture_rate": metrics.get('savings_capture_rate', 0)
        }
        
        # Add advanced metrics if present (backward compatible)
        if 'advanced_metrics' in metrics and metrics['advanced_metrics']:
            adv_metrics = metrics['advanced_metrics']
            base_metrics.update({
                "true_positives": adv_metrics.get('true_positives', 0),
                "false_positives": adv_metrics.get('false_positives', 0),
                "false_negatives": adv_metrics.get('false_negatives', 0),
                "risk_weighted_recall": adv_metrics.get('risk_weighted_recall', 0),
                "conservatism_index": adv_metrics.get('conservatism_index', 0),
                "p95_latency_ms": adv_metrics.get('p95_latency_ms', 0),
                "roi_ratio": adv_metrics.get('roi_ratio', 0),
                "inference_cost_usd": adv_metrics.get('inference_cost_usd', 0),
            })
            
            # Add hybrid metrics if present
            if 'unique_detections' in adv_metrics:
                base_metrics.update({
                    "unique_detections": adv_metrics.get('unique_detections'),
                    "overlap_detections": adv_metrics.get('overlap_detections'),
                    "complementarity_gain": adv_metrics.get('complementarity_gain')
                })
        
        monitoring_format = {
            "model_version": model_version,
            "model_provider": model_name,
            "dataset_version": dataset_version,
            "dataset_size": metrics.get('total_patients', 0),
            "prompt_version": prompt_version,
            "metrics": base_metrics,
            "duration_seconds": metrics.get('avg_latency_ms', 0) / 1000,
            "error_count": metrics.get('total_patients', 0) - metrics.get('successful_analyses', 0),
            "success_count": metrics.get('successful_analyses', 0),
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "domain_breakdown": metrics.get('domain_breakdown', {}),
            "aggregated_categories": metrics.get('aggregated_categories', {}),
            # Add category metrics for database insertion (if advanced metrics present)
            "category_metrics": metrics.get('advanced_metrics', {}).get('category_metrics', {}) if 'advanced_metrics' in metrics else {}
        }
    else:
        # Convert aggregated metrics format (old format)
        monitoring_format = {
            "model_version": model_version,
            "model_provider": model_name,
            "dataset_version": dataset_version,
            "dataset_size": metrics.get('total_documents', 0),
            "prompt_version": prompt_version,
            "metrics": {
                "precision": metrics.get('issue_precision', 0),
                "recall": metrics.get('issue_recall', 0),
                "f1": metrics.get('issue_f1_score', 0),
                "latency_ms": metrics.get('avg_pipeline_latency_ms', 0),
                "analysis_cost": metrics.get('total_cost', 0) / max(metrics.get('total_documents', 1), 1),
                "total_documents": metrics.get('total_documents', 0),
                "total_issues_detected": metrics.get('total_issues_detected', 0),
                "total_issues_expected": metrics.get('total_issues_expected', 0)
            },
            "duration_seconds": metrics.get('avg_pipeline_latency_ms', 0) / 1000,
            "error_count": metrics.get('error_count', 0),
            "success_count": metrics.get('total_documents', 0) - metrics.get('error_count', 0),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
    
    return monitoring_format

def main():
    parser = argparse.ArgumentParser(description='Convert benchmark to monitoring format')
    parser.add_argument('--input', required=True, help='Input aggregated metrics file')
    parser.add_argument('--output', required=True, help='Output monitoring format file')
    parser.add_argument('--model', required=True, help='Model name (openai, gemini, etc.)')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1
    
    monitoring_data = convert_to_monitoring_format(input_path, args.model)
    
    # Save to output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(monitoring_data, f, indent=2)
    
    print(f"✅ Converted {input_path} → {output_path}")
    print(f"   Model: {monitoring_data['model_version']}")
    print(f"   F1: {monitoring_data['metrics']['f1']:.4f}")
    
    return 0

if __name__ == '__main__':
    exit(main())
