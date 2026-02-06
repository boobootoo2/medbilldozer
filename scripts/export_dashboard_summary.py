#!/usr/bin/env python3
"""
Export Dashboard Summary Report

Generates a JSON summary report with all key metrics used in the benchmark dashboard.
Includes model comparison, cost savings, category performance, and trend analysis.

Usage:
    python3 scripts/export_dashboard_summary.py
    python3 scripts/export_dashboard_summary.py --output report.json
    python3 scripts/export_dashboard_summary.py --days 30
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from supabase import create_client

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_supabase_client():
    """Create Supabase client."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        sys.exit(1)
    
    return create_client(url, key)


def fetch_transactions(client, days=None):
    """Fetch benchmark transactions."""
    query = client.table('benchmark_transactions').select('*').order('created_at', desc=True)
    
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        query = query.gte('created_at', cutoff)
    
    response = query.execute()
    return response.data


def is_failed_run(txn):
    """Check if a transaction represents a failed run."""
    metrics = txn.get('metrics', {})
    
    f1 = float(metrics.get('f1', 0))
    recall = float(metrics.get('recall', 0))
    precision = float(metrics.get('precision', 0))
    success_rate = float(metrics.get('success_rate', 1))
    dataset_size = int(metrics.get('dataset_size', 0))
    
    return (f1 == 0 and recall == 0 and precision == 0 and 
            (success_rate == 0 or dataset_size == 0))


def estimate_model_cost(model_version, dataset_size):
    """Estimate model cost per run based on provider and dataset size."""
    model_lower = model_version.lower()
    
    # Tokens per patient estimate
    tokens_per_patient = 3000
    total_tokens = dataset_size * tokens_per_patient
    
    # Cost per 1K tokens
    if 'openai' in model_lower or 'gpt' in model_lower:
        cost_per_1k = 0.03
    elif 'gemini' in model_lower or 'google' in model_lower or 'gemma' in model_lower:
        cost_per_1k = 0.01
    elif 'baseline' in model_lower or 'heuristic' in model_lower:
        # Near-zero cost for rule-based systems
        return 0.0001
    else:
        # Default assumption
        cost_per_1k = 0.02
    
    return round((total_tokens / 1000) * cost_per_1k, 4)


def compute_model_summary(transactions):
    """Compute per-model summary statistics."""
    model_stats = defaultdict(lambda: {
        'runs': 0,
        'failed_runs': 0,
        'precision': [],
        'recall': [],
        'f1': [],
        'latency_ms': [],
        'total_savings': 0,
        'savings_capture_rate': [],
        'risk_weighted_recall': [],
        'conservatism_index': [],
        'roi_data': [],
        'p95_latency_ms': [],
        'latest_run': None
    })
    
    for txn in transactions:
        model = txn.get('model_version', 'Unknown')
        metrics = txn.get('metrics', {})
        
        stats = model_stats[model]
        stats['runs'] += 1
        
        # Check if failed run
        if is_failed_run(txn):
            stats['failed_runs'] += 1
            continue
        
        # Standard metrics (exclude failed runs)
        if 'precision' in metrics:
            stats['precision'].append(float(metrics['precision']))
        if 'recall' in metrics:
            stats['recall'].append(float(metrics['recall']))
        if 'f1' in metrics:
            stats['f1'].append(float(metrics['f1']))
        if 'latency_ms' in metrics:
            stats['latency_ms'].append(float(metrics['latency_ms']))
        
        # Cost savings
        total_potential_savings = float(metrics.get('total_potential_savings', 0))
        stats['total_savings'] += total_potential_savings
        
        if 'savings_capture_rate' in metrics:
            stats['savings_capture_rate'].append(float(metrics['savings_capture_rate']))
        
        # Advanced metrics
        if 'risk_weighted_recall' in metrics:
            stats['risk_weighted_recall'].append(float(metrics['risk_weighted_recall']))
        if 'conservatism_index' in metrics:
            stats['conservatism_index'].append(float(metrics['conservatism_index']))
        if 'p95_latency_ms' in metrics:
            stats['p95_latency_ms'].append(float(metrics['p95_latency_ms']))
        
        # Compute ROI
        dataset_size = int(metrics.get('dataset_size', 0))
        if total_potential_savings > 0:
            # Fallback: infer dataset size from successful_analyses if dataset_size missing
            if dataset_size == 0:
                dataset_size = int(metrics.get('successful_analyses', 46))
            
            estimated_cost = estimate_model_cost(model, dataset_size)
            if estimated_cost > 0:
                roi_ratio = total_potential_savings / estimated_cost
                stats['roi_data'].append(roi_ratio)
        
        # Track latest run
        if not stats['latest_run'] or txn['created_at'] > stats['latest_run']:
            stats['latest_run'] = txn['created_at']
    
    # Compute averages
    summary = {}
    for model, stats in model_stats.items():
        successful_runs = stats['runs'] - stats['failed_runs']
        failure_rate = round(stats['failed_runs'] / stats['runs'], 4) if stats['runs'] > 0 else 0.0
        
        summary[model] = {
            'total_runs': stats['runs'],
            'successful_runs': successful_runs,
            'failed_runs': stats['failed_runs'],
            'failure_rate': failure_rate,
            'latest_run': stats['latest_run'],
            'avg_precision': round(sum(stats['precision']) / len(stats['precision']), 4) if stats['precision'] else None,
            'avg_recall': round(sum(stats['recall']) / len(stats['recall']), 4) if stats['recall'] else None,
            'avg_f1': round(sum(stats['f1']) / len(stats['f1']), 4) if stats['f1'] else None,
            'avg_latency_ms': round(sum(stats['latency_ms']) / len(stats['latency_ms']), 2) if stats['latency_ms'] else None,
            'total_potential_savings': round(stats['total_savings'], 2),
            'avg_savings_capture_rate': round(sum(stats['savings_capture_rate']) / len(stats['savings_capture_rate']), 4) if stats['savings_capture_rate'] else None,
            'avg_risk_weighted_recall': round(sum(stats['risk_weighted_recall']) / len(stats['risk_weighted_recall']), 4) if stats['risk_weighted_recall'] else None,
            'avg_conservatism_index': round(sum(stats['conservatism_index']) / len(stats['conservatism_index']), 4) if stats['conservatism_index'] else None,
            'avg_roi_ratio': round(sum(stats['roi_data']) / len(stats['roi_data']), 2) if stats['roi_data'] else None,
            'avg_p95_latency_ms': round(sum(stats['p95_latency_ms']) / len(stats['p95_latency_ms']), 2) if stats['p95_latency_ms'] else None,
        }
    
    return summary


def compute_category_performance(transactions):
    """Compute category-level performance across all models."""
    # Structure: model -> category -> aggregated stats
    model_category_stats = defaultdict(lambda: defaultdict(lambda: {
        'total_cases': 0,
        'total_detected': 0,
        'detection_rates': []
    }))
    
    for txn in transactions:
        model = txn.get('model_version', 'Unknown')
        metrics = txn.get('metrics', {})
        benchmark_type = txn.get('benchmark_type', 'standard')
        successful_analyses = int(metrics.get('successful_analyses', 0))
        
        # Only include standard benchmark runs with successful analyses
        if benchmark_type != 'standard' or successful_analyses == 0:
            continue
        
        # Skip failed runs
        if is_failed_run(txn):
            continue
        
        # Extract from error_type_performance (preferred) or category_metrics (legacy)
        error_type_perf = metrics.get('error_type_performance', {})
        category_metrics = metrics.get('category_metrics', {})
        
        # Combine both sources
        all_categories = {}
        for category, cat_data in error_type_perf.items():
            all_categories[category] = {
                'total': cat_data.get('total', 0),
                'detected': cat_data.get('detected', 0),
                'detection_rate': cat_data.get('detection_rate', 0.0)
            }
        
        for category, cat_data in category_metrics.items():
            if category not in all_categories:
                total = cat_data.get('total', 0)
                detected = cat_data.get('detected', 0)
                all_categories[category] = {
                    'total': total,
                    'detected': detected,
                    'detection_rate': detected / total if total > 0 else 0.0
                }
        
        # Aggregate by model and category
        for category, cat_data in all_categories.items():
            stats = model_category_stats[model][category]
            stats['total_cases'] += cat_data['total']
            stats['total_detected'] += cat_data['detected']
            if cat_data['total'] > 0:
                stats['detection_rates'].append(cat_data['detection_rate'])
    
    # Compute final aggregates
    category_performance = {}
    for model, categories in model_category_stats.items():
        category_performance[model] = {}
        for category, stats in categories.items():
            avg_detection_rate = round(
                sum(stats['detection_rates']) / len(stats['detection_rates']), 
                4
            ) if stats['detection_rates'] else 0.0
            
            category_performance[model][category] = {
                'total_cases': stats['total_cases'],
                'total_detected': stats['total_detected'],
                'avg_detection_rate': avg_detection_rate
            }
    
    return category_performance


def compute_trend_analysis(transactions, models):
    """Compute time-series trends for key metrics."""
    trends = {}
    
    for model in models:
        model_txns = [t for t in transactions if t.get('model_version') == model and not is_failed_run(t)]
        model_txns.sort(key=lambda x: x['created_at'])
        
        trends[model] = {
            'dates': [],
            'precision': [],
            'recall': [],
            'f1': [],
            'risk_weighted_recall': [],
            'roi_ratio': [],
            'savings_capture_rate': []
        }
        
        for txn in model_txns[-30:]:  # Last 30 runs
            metrics = txn.get('metrics', {})
            dataset_size = int(metrics.get('dataset_size', 0))
            total_potential_savings = float(metrics.get('total_potential_savings', 0))
            
            # Compute ROI for this run
            roi_ratio = 0.0
            if total_potential_savings > 0:
                # Fallback: infer dataset size from successful_analyses if dataset_size missing
                if dataset_size == 0:
                    dataset_size = int(metrics.get('successful_analyses', 46))
                
                estimated_cost = estimate_model_cost(model, dataset_size)
                if estimated_cost > 0:
                    roi_ratio = round(total_potential_savings / estimated_cost, 2)
            
            trends[model]['dates'].append(txn['created_at'])
            trends[model]['precision'].append(round(float(metrics.get('precision', 0)), 4))
            trends[model]['recall'].append(round(float(metrics.get('recall', 0)), 4))
            trends[model]['f1'].append(round(float(metrics.get('f1', 0)), 4))
            trends[model]['risk_weighted_recall'].append(round(float(metrics.get('risk_weighted_recall', 0)), 4))
            trends[model]['roi_ratio'].append(roi_ratio)
            trends[model]['savings_capture_rate'].append(round(float(metrics.get('savings_capture_rate', 0)), 4))
    
    return trends


def compute_category_regressions(transactions, model_category_stats):
    """Detect category-level regressions for each model."""
    regressions = {}
    
    for model, categories in model_category_stats.items():
        model_txns = [t for t in transactions 
                      if t.get('model_version') == model 
                      and not is_failed_run(t)
                      and t.get('benchmark_type', 'standard') == 'standard']
        model_txns.sort(key=lambda x: x['created_at'])
        
        if len(model_txns) < 3:
            continue
        
        regressions[model] = {}
        
        for category in categories.keys():
            # Extract detection rates for this category across runs
            category_history = []
            for txn in model_txns:
                metrics = txn.get('metrics', {})
                error_type_perf = metrics.get('error_type_performance', {})
                category_metrics = metrics.get('category_metrics', {})
                
                cat_data = error_type_perf.get(category) or category_metrics.get(category)
                if cat_data:
                    total = cat_data.get('total', 0)
                    detected = cat_data.get('detected', 0)
                    if total > 0:
                        detection_rate = detected / total
                        category_history.append(detection_rate)
            
            if len(category_history) < 3:
                continue
            
            # Latest vs trailing mean
            latest = category_history[-1]
            trailing_mean = sum(category_history[:-1]) / len(category_history[:-1])
            delta = latest - trailing_mean
            
            # Regression threshold: drop of more than 0.10 (10%)
            if delta < -0.10:
                regressions[model][category] = {
                    'previous_avg': round(trailing_mean, 4),
                    'current': round(latest, 4),
                    'delta': round(delta, 4)
                }
    
    return regressions


def compute_leaderboard(model_summary):
    """Generate model leaderboard rankings."""
    leaderboard = {
        'by_recall': [],
        'by_precision': [],
        'by_f1': [],
        'by_risk_weighted_recall': [],
        'by_roi': [],
        'by_speed': []
    }
    
    models = list(model_summary.keys())
    
    # Rank by recall
    leaderboard['by_recall'] = sorted(
        [(m, model_summary[m]['avg_recall']) for m in models if model_summary[m]['avg_recall'] is not None],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Rank by precision
    leaderboard['by_precision'] = sorted(
        [(m, model_summary[m]['avg_precision']) for m in models if model_summary[m]['avg_precision'] is not None],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Rank by F1
    leaderboard['by_f1'] = sorted(
        [(m, model_summary[m]['avg_f1']) for m in models if model_summary[m]['avg_f1'] is not None],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Rank by risk-weighted recall
    leaderboard['by_risk_weighted_recall'] = sorted(
        [(m, model_summary[m]['avg_risk_weighted_recall']) for m in models if model_summary[m]['avg_risk_weighted_recall'] is not None],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Rank by ROI (descending)
    leaderboard['by_roi'] = sorted(
        [(m, model_summary[m]['avg_roi_ratio']) for m in models if model_summary[m]['avg_roi_ratio'] is not None],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Rank by speed (lower latency is better)
    leaderboard['by_speed'] = sorted(
        [(m, model_summary[m]['avg_latency_ms']) for m in models if model_summary[m]['avg_latency_ms'] is not None],
        key=lambda x: x[1]
    )
    
    return leaderboard


def generate_report(client, days=None):
    """Generate complete dashboard summary report."""
    print("📊 Generating dashboard summary report...")
    
    # Fetch transactions
    transactions = fetch_transactions(client, days)
    print(f"✅ Loaded {len(transactions)} transactions")
    
    # Compute summaries
    print("📈 Computing model summaries...")
    model_summary = compute_model_summary(transactions)
    
    print("📊 Computing category performance...")
    category_performance = compute_category_performance(transactions)
    
    # Build intermediate stats for regression detection
    model_category_stats = defaultdict(lambda: defaultdict(dict))
    for model, categories in category_performance.items():
        for category in categories.keys():
            model_category_stats[model][category] = {}
    
    print("🔍 Detecting category regressions...")
    category_regressions = compute_category_regressions(transactions, model_category_stats)
    
    print("📉 Computing trend analysis...")
    models = list(model_summary.keys())
    trends = compute_trend_analysis(transactions, models)
    
    print("🏆 Generating leaderboard...")
    leaderboard = compute_leaderboard(model_summary)
    
    # Overall statistics
    total_savings = sum(m['total_potential_savings'] for m in model_summary.values())
    total_runs = sum(m['total_runs'] for m in model_summary.values())
    total_categories = sum(len(cats) for cats in category_performance.values())
    
    # Build report
    report = {
        'generated_at': datetime.now().isoformat(),
        'time_window_days': days,
        'total_transactions': len(transactions),
        'total_benchmark_runs': total_runs,
        'models_tracked': len(models),
        'total_potential_savings': round(total_savings, 2),
        
        'model_summary': model_summary,
        'category_performance': category_performance,
        'category_regressions': category_regressions,
        'leaderboard': leaderboard,
        'trends': trends,
        
        'metadata': {
            'categories_tracked': total_categories,
            'regressions_detected': sum(len(regs) for regs in category_regressions.values()),
            'earliest_transaction': transactions[-1]['created_at'] if transactions else None,
            'latest_transaction': transactions[0]['created_at'] if transactions else None,
        }
    }
    
    return report


def main():
    parser = argparse.ArgumentParser(description='Export dashboard summary report')
    parser.add_argument('--output', '-o', default=None, help='Output file path (default: auto-generated)')
    parser.add_argument('--days', '-d', type=int, default=None, help='Only include last N days of data')
    args = parser.parse_args()
    
    # Get client
    client = get_supabase_client()
    
    # Generate report
    report = generate_report(client, args.days)
    
    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        suffix = f'_last_{args.days}_days' if args.days else '_all_time'
        output_file = f'dashboard_summary{suffix}_{timestamp}.json'
    
    # Save report
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print()
    print("=" * 70)
    print("✅ Dashboard Summary Report Generated")
    print("=" * 70)
    print(f"📄 File: {output_file}")
    print(f"📊 Transactions: {report['total_transactions']}")
    print(f"🎯 Models: {report['models_tracked']}")
    print(f"📈 Categories: {report['metadata']['categories_tracked']}")
    print(f"💰 Total Savings: ${report['total_potential_savings']:,.2f}")
    print(f"⚠️  Regressions: {report['metadata']['regressions_detected']}")
    print()
    print("🏆 Leaderboard (Top 3):")
    if report['leaderboard']['by_recall']:
        print(f"   Recall:     {', '.join([m for m, _ in report['leaderboard']['by_recall'][:3]])}")
    if report['leaderboard']['by_precision']:
        print(f"   Precision:  {', '.join([m for m, _ in report['leaderboard']['by_precision'][:3]])}")
    if report['leaderboard']['by_roi']:
        print(f"   ROI:        {', '.join([m for m, _ in report['leaderboard']['by_roi'][:3]])}")
    print()
    
    # Show failure rates if any
    failed_models = [(m, s['failure_rate']) for m, s in report['model_summary'].items() if s['failure_rate'] > 0]
    if failed_models:
        print("⚠️  Models with Failed Runs:")
        for model, rate in failed_models:
            print(f"   {model}: {rate*100:.1f}%")
        print()
    
    print("=" * 70)


if __name__ == "__main__":
    main()
