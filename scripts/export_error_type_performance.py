#!/usr/bin/env python3
"""
Export Error Type Performance Data

This script extracts the error type performance heatmap data from Supabase
and exports it to CSV format for analysis.

Usage:
    python3 scripts/export_error_type_performance.py [--environment ENV] [--output FILE]

Examples:
    # Export local environment data
    python3 scripts/export_error_type_performance.py --environment local

    # Export all environments
    python3 scripts/export_error_type_performance.py

    # Custom output file
    python3 scripts/export_error_type_performance.py --output my_data.csv
"""

import sys
from pathlib import Path
import argparse
import pandas as pd
from dotenv import load_dotenv
import os

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from supabase import create_client


def export_error_type_performance(environment=None, output_file='error_type_performance.csv'):
    """
    Export error type performance data from Supabase to CSV.
    
    Args:
        environment: Filter by environment (None for all)
        output_file: Output CSV filename
    """
    load_dotenv()
    
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    )
    
    # Build query
    query = supabase.table('benchmark_transactions').select('model_version, metrics, created_at')
    
    if environment:
        query = query.eq('environment', environment)
    
    query = query.order('created_at', desc=True).limit(100)
    response = query.execute()
    
    if not response.data:
        print("⚠️  No benchmark data found")
        return
    
    # Build error type performance matrix - use latest result per model
    model_error_performance = {}
    
    for transaction in response.data:
        model = transaction['model_version']
        
        # Skip old short-name models
        if model in ['medgemma', 'openai', 'gemini', 'baseline', 'medgemma-v1.0', 'openai-v1.0', 'baseline-v1.0']:
            continue
        
        # Only take the first (latest) result for each model
        if model in model_error_performance:
            continue
        
        metrics = transaction.get('metrics', {})
        error_type_perf = metrics.get('error_type_performance', {})
        
        if error_type_perf:
            model_error_performance[model] = error_type_perf
    
    if not model_error_performance:
        print("⚠️  No error type performance data found")
        return
    
    # Get all unique error types
    all_error_types = set()
    for model_data in model_error_performance.values():
        all_error_types.update(model_data.keys())
    
    # Create DataFrame with percentage data
    percentage_data = []
    for error_type in sorted(all_error_types):
        row = {'error_type': error_type}
        for model in sorted(model_error_performance.keys()):
            perf = model_error_performance[model].get(error_type, {})
            detection_rate = perf.get('detection_rate', 0.0) * 100
            row[f'{model}_pct'] = detection_rate
        percentage_data.append(row)
    
    # Create DataFrame with detailed data (detected/total)
    detailed_data = []
    for error_type in sorted(all_error_types):
        row = {'error_type': error_type}
        for model in sorted(model_error_performance.keys()):
            perf = model_error_performance[model].get(error_type, {})
            detection_rate = perf.get('detection_rate', 0.0) * 100
            detected = perf.get('detected', 0)
            total = perf.get('total', 0)
            row[model] = f'{detection_rate:.1f}% ({detected}/{total})'
        detailed_data.append(row)
    
    df_detailed = pd.DataFrame(detailed_data)
    df_percentage = pd.DataFrame(percentage_data)
    
    # Display the data
    print('=' * 100)
    print('Performance by Error Type - Detection Rates')
    print('=' * 100)
    print()
    print(df_detailed.to_string(index=False))
    print()
    
    # Export both formats
    detailed_file = output_file.replace('.csv', '_detailed.csv')
    percentage_file = output_file.replace('.csv', '_percentages.csv')
    
    df_detailed.to_csv(detailed_file, index=False)
    df_percentage.to_csv(percentage_file, index=False)
    
    print(f'✅ Detailed data exported to: {detailed_file}')
    print(f'✅ Percentage data exported to: {percentage_file}')
    
    # Summary statistics
    print()
    print('=' * 100)
    print('Summary Statistics')
    print('=' * 100)
    
    for model in sorted(model_error_performance.keys()):
        rates = [perf.get('detection_rate', 0.0) * 100
                 for perf in model_error_performance[model].values()]
        avg_rate = sum(rates) / len(rates) if rates else 0
        print(f'{model:30s} Avg: {avg_rate:5.1f}%  Min: {min(rates):5.1f}%  Max: {max(rates):5.1f}%')


def main():
    parser = argparse.ArgumentParser(
        description='Export error type performance data from benchmark results'
    )
    parser.add_argument(
        '--environment',
        type=str,
        default='local',
        help='Filter by environment (default: local, use "all" for no filter)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='error_type_performance.csv',
        help='Output CSV filename (default: error_type_performance.csv)'
    )
    
    args = parser.parse_args()
    
    env = None if args.environment == 'all' else args.environment
    
    print(f'📊 Exporting error type performance data...')
    if env:
        print(f'   Environment: {env}')
    else:
        print(f'   Environment: All')
    print()
    
    export_error_type_performance(environment=env, output_file=args.output)
    print()
    print('✅ Export complete!')


if __name__ == '__main__':
    main()
