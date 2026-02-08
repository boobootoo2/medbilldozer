#!/usr/bin/env python3
"""
Calculate ROI and cost savings metrics for benchmark results.

This script takes benchmark results and calculates:
- Total potential savings to consumers
- Analysis cost (inference + infrastructure)
- ROI (savings / cost)
- Cost per issue detected
- Net benefit to consumers

Usage:
    python scripts/calculate_roi_metrics.py \
        --results-dir benchmark-artifacts \
        --output roi_summary.json
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List

# Model cost estimates (USD per 1M tokens)
# Based on public pricing as of Feb 2026
MODEL_COSTS = {
    'openai': {
        'input': 5.00,   # GPT-4 Turbo input
        'output': 15.00,  # GPT-4 Turbo output
        'name': 'OpenAI GPT-4 Turbo'
    },
    'gemini': {
        'input': 3.50,   # Gemini 1.5 Pro input
        'output': 10.50,  # Gemini 1.5 Pro output
        'name': 'Google Gemini 1.5 Pro'
    },
    'medgemma': {
        'input': 0.10,   # Hosted MedGemma (estimated)
        'output': 0.15,  # Hosted MedGemma (estimated)
        'name': 'Google MedGemma-4B-IT'
    },
    'gemma3': {
        'input': 0.50,   # Gemma-3-27B (estimated)
        'output': 0.75,  # Gemma-3-27B (estimated)
        'name': 'Google Gemma-3-27B-IT'
    },
    'baseline': {
        'input': 0.00,   # Heuristic baseline (no API cost)
        'output': 0.00,
        'name': 'Heuristic Baseline'
    }
}

# Average tokens per medical bill analysis (estimated from testing)
AVG_INPUT_TOKENS = 2500   # Receipt + context
AVG_OUTPUT_TOKENS = 800   # Analysis + issues

# Infrastructure cost per analysis (hosting, storage, compute)
INFRASTRUCTURE_COST_PER_ANALYSIS = 0.001  # $0.001 per analysis

def calculate_analysis_cost(model: str, num_analyses: int) -> Dict[str, float]:
    """Calculate the total cost of running analyses."""
    if model not in MODEL_COSTS:
        # Default to median cost for unknown models
        input_cost = 2.0
        output_cost = 6.0
    else:
        input_cost = MODEL_COSTS[model]['input']
        output_cost = MODEL_COSTS[model]['output']
    
    # Calculate token costs
    input_token_cost = (AVG_INPUT_TOKENS / 1_000_000) * input_cost * num_analyses
    output_token_cost = (AVG_OUTPUT_TOKENS / 1_000_000) * output_cost * num_analyses
    inference_cost = input_token_cost + output_token_cost
    
    # Add infrastructure cost
    infrastructure_cost = INFRASTRUCTURE_COST_PER_ANALYSIS * num_analyses
    
    total_cost = inference_cost + infrastructure_cost
    
    return {
        'inference_cost': round(inference_cost, 4),
        'infrastructure_cost': round(infrastructure_cost, 4),
        'total_cost': round(total_cost, 4),
        'cost_per_analysis': round(total_cost / num_analyses, 6) if num_analyses > 0 else 0
    }

def calculate_roi_metrics(benchmark_data: dict, model: str) -> Dict:
    """Calculate ROI and savings metrics from benchmark data."""
    metrics = benchmark_data.get('metrics', {})
    
    # Extract key metrics
    num_analyses = metrics.get('total_documents', 0)
    total_savings = metrics.get('total_potential_savings', 0)
    avg_savings_per_patient = metrics.get('avg_savings_per_patient', 0)
    savings_capture_rate = metrics.get('savings_capture_rate', 0)
    
    # Calculate costs
    cost_breakdown = calculate_analysis_cost(model, num_analyses)
    total_cost = cost_breakdown['total_cost']
    
    # Calculate ROI metrics
    roi_ratio = (total_savings / total_cost) if total_cost > 0 else 0
    net_benefit = total_savings - total_cost
    
    # Calculate efficiency metrics
    issues_detected = metrics.get('total_issues_detected', 0)
    cost_per_issue = (total_cost / issues_detected) if issues_detected > 0 else 0
    savings_per_dollar_spent = roi_ratio  # Same as ROI ratio
    
    # Calculate consumer impact
    avg_net_benefit_per_patient = (net_benefit / num_analyses) if num_analyses > 0 else 0
    
    return {
        'model': model,
        'model_name': MODEL_COSTS.get(model, {}).get('name', model),
        'num_analyses': num_analyses,
        'cost_breakdown': cost_breakdown,
        'consumer_savings': {
            'total_potential_savings': round(total_savings, 2),
            'avg_savings_per_patient': round(avg_savings_per_patient, 2),
            'savings_capture_rate': round(savings_capture_rate * 100, 2),
            'total_missed_savings': round(metrics.get('total_missed_savings', 0), 2)
        },
        'roi_metrics': {
            'roi_ratio': round(roi_ratio, 2),
            'net_benefit': round(net_benefit, 2),
            'avg_net_benefit_per_patient': round(avg_net_benefit_per_patient, 2),
            'cost_per_issue_detected': round(cost_per_issue, 4),
            'savings_per_dollar_spent': round(savings_per_dollar_spent, 2)
        },
        'performance_metrics': {
            'precision': round(metrics.get('precision', 0), 4),
            'recall': round(metrics.get('recall', 0), 4),
            'f1': round(metrics.get('f1', 0), 4),
            'issues_detected': issues_detected,
            'issues_expected': metrics.get('total_issues_expected', 0)
        }
    }

def generate_summary_report(all_results: List[Dict]) -> str:
    """Generate a markdown summary report."""
    report = ["# 💰 medBillDozer ROI & Cost Savings Analysis", ""]
    report.append("## Executive Summary")
    report.append("")
    
    # Sort by ROI ratio
    sorted_results = sorted(all_results, key=lambda x: x['roi_metrics']['roi_ratio'], reverse=True)
    
    # Overall totals
    total_savings = sum(r['consumer_savings']['total_potential_savings'] for r in all_results)
    total_cost = sum(r['cost_breakdown']['total_cost'] for r in all_results)
    total_net_benefit = sum(r['roi_metrics']['net_benefit'] for r in all_results)
    total_analyses = sum(r['num_analyses'] for r in all_results)
    
    report.append(f"**Total Consumer Savings Identified**: ${total_savings:,.2f}")
    report.append(f"**Total Analysis Cost**: ${total_cost:,.2f}")
    report.append(f"**Net Benefit to Consumers**: ${total_net_benefit:,.2f}")
    report.append(f"**Overall ROI**: {(total_savings/total_cost):.2f}x" if total_cost > 0 else "N/A")
    report.append(f"**Total Analyses**: {total_analyses:,}")
    report.append("")
    
    # Model comparison table
    report.append("## Model Performance & ROI Comparison")
    report.append("")
    report.append("| Model | Potential Savings | Analysis Cost | Net Benefit | ROI | F1 Score |")
    report.append("|-------|-------------------|---------------|-------------|-----|----------|")
    
    for result in sorted_results:
        model_name = result['model_name']
        savings = result['consumer_savings']['total_potential_savings']
        cost = result['cost_breakdown']['total_cost']
        net = result['roi_metrics']['net_benefit']
        roi = result['roi_metrics']['roi_ratio']
        f1 = result['performance_metrics']['f1']
        
        report.append(f"| {model_name} | ${savings:,.2f} | ${cost:.2f} | ${net:,.2f} | {roi:.1f}x | {f1:.3f} |")
    
    report.append("")
    
    # Detailed breakdown
    report.append("## Detailed Model Analysis")
    report.append("")
    
    for result in sorted_results:
        report.append(f"### {result['model_name']}")
        report.append("")
        
        report.append("**Consumer Impact:**")
        report.append(f"- Potential Savings: ${result['consumer_savings']['total_potential_savings']:,.2f}")
        report.append(f"- Avg Savings/Patient: ${result['consumer_savings']['avg_savings_per_patient']:.2f}")
        report.append(f"- Savings Capture Rate: {result['consumer_savings']['savings_capture_rate']:.1f}%")
        report.append("")
        
        report.append("**Cost Analysis:**")
        report.append(f"- Inference Cost: ${result['cost_breakdown']['inference_cost']:.2f}")
        report.append(f"- Infrastructure Cost: ${result['cost_breakdown']['infrastructure_cost']:.2f}")
        report.append(f"- Total Cost: ${result['cost_breakdown']['total_cost']:.2f}")
        report.append(f"- Cost/Analysis: ${result['cost_breakdown']['cost_per_analysis']:.4f}")
        report.append("")
        
        report.append("**ROI Metrics:**")
        report.append(f"- ROI Ratio: {result['roi_metrics']['roi_ratio']:.2f}x")
        report.append(f"- Net Benefit: ${result['roi_metrics']['net_benefit']:,.2f}")
        report.append(f"- Avg Net Benefit/Patient: ${result['roi_metrics']['avg_net_benefit_per_patient']:.2f}")
        report.append(f"- Cost per Issue Detected: ${result['roi_metrics']['cost_per_issue_detected']:.4f}")
        report.append(f"- Savings per $1 Spent: ${result['roi_metrics']['savings_per_dollar_spent']:.2f}")
        report.append("")
        
        report.append("**Performance:**")
        report.append(f"- Precision: {result['performance_metrics']['precision']:.3f}")
        report.append(f"- Recall: {result['performance_metrics']['recall']:.3f}")
        report.append(f"- F1 Score: {result['performance_metrics']['f1']:.3f}")
        report.append(f"- Issues Detected: {result['performance_metrics']['issues_detected']}")
        report.append("")
    
    # Key insights
    report.append("## Key Insights")
    report.append("")
    
    best_roi = sorted_results[0]
    best_savings = max(all_results, key=lambda x: x['consumer_savings']['total_potential_savings'])
    best_f1 = max(all_results, key=lambda x: x['performance_metrics']['f1'])
    
    report.append(f"🏆 **Best ROI**: {best_roi['model_name']} ({best_roi['roi_metrics']['roi_ratio']:.1f}x)")
    report.append(f"💰 **Highest Savings**: {best_savings['model_name']} (${best_savings['consumer_savings']['total_potential_savings']:,.2f})")
    report.append(f"🎯 **Best Accuracy**: {best_f1['model_name']} (F1: {best_f1['performance_metrics']['f1']:.3f})")
    report.append("")
    
    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description='Calculate ROI and cost savings metrics')
    parser.add_argument('--results-dir', default='benchmark-artifacts', 
                        help='Directory containing benchmark result files')
    parser.add_argument('--output', default='roi_summary.json',
                        help='Output JSON file for ROI metrics')
    parser.add_argument('--report', default='roi_report.md',
                        help='Output markdown report file')
    
    args = parser.parse_args()
    
    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        return 1
    
    # Process all benchmark result files
    all_results = []
    for result_file in results_dir.glob('*_benchmark_results.json'):
        # Extract model name from filename (e.g., "openai_benchmark_results.json" -> "openai")
        model = result_file.stem.replace('_benchmark_results', '')
        
        print(f"📊 Analyzing {model}...")
        
        with open(result_file, 'r') as f:
            benchmark_data = json.load(f)
        
        roi_metrics = calculate_roi_metrics(benchmark_data, model)
        all_results.append(roi_metrics)
        
        print(f"   Potential Savings: ${roi_metrics['consumer_savings']['total_potential_savings']:,.2f}")
        print(f"   Analysis Cost: ${roi_metrics['cost_breakdown']['total_cost']:.2f}")
        print(f"   ROI: {roi_metrics['roi_metrics']['roi_ratio']:.2f}x")
        print()
    
    if not all_results:
        print("Warning: No benchmark results found")
        return 1
    
    # Save JSON summary
    output_data = {
        'timestamp': benchmark_data.get('timestamp', ''),
        'summary': {
            'total_analyses': sum(r['num_analyses'] for r in all_results),
            'total_potential_savings': sum(r['consumer_savings']['total_potential_savings'] for r in all_results),
            'total_cost': sum(r['cost_breakdown']['total_cost'] for r in all_results),
            'total_net_benefit': sum(r['roi_metrics']['net_benefit'] for r in all_results)
        },
        'model_results': all_results
    }
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✅ Saved ROI metrics to {output_path}")
    
    # Generate markdown report
    report = generate_summary_report(all_results)
    report_path = Path(args.report)
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"📄 Saved markdown report to {report_path}")
    print()
    print("=" * 60)
    print(report)
    
    return 0

if __name__ == '__main__':
    exit(main())
