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
    """Convert aggregated metrics to monitoring format."""
    
    with open(input_file, 'r') as f:
        metrics = json.load(f)
    
    # Extract version info (you can customize this)
    model_version = f"{model_name}-v1.0"
    dataset_version = "benchmark-set-v1"
    prompt_version = metrics.get('prompt_version', 'v1')
    
    # Convert metrics
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
