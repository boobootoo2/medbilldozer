#!/usr/bin/env python3
"""
Verify Benchmark Results in Supabase

This script checks if benchmark results exist in Supabase and displays
recent uploads with their metrics.

Usage:
    # Check latest results for all models
    python3 scripts/verify_supabase_results.py

    # Check specific model
    python3 scripts/verify_supabase_results.py --model medgemma

    # Check results from specific commit
    python3 scripts/verify_supabase_results.py --commit-sha abc123

    # Show last N results
    python3 scripts/verify_supabase_results.py --limit 10
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent


def get_supabase_client() -> Client:
    """Get authenticated Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        raise ValueError(
            "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables.\n"
            "Please set them in your .env file."
        )
    
    return create_client(url, key)


def get_recent_benchmarks(
    client: Client,
    model_pattern: Optional[str] = None,
    commit_sha: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Get recent benchmark results from Supabase.
    
    Args:
        client: Supabase client
        model_pattern: Model name pattern to filter (e.g., 'medgemma')
        commit_sha: Specific commit SHA to filter
        limit: Maximum number of results to return
    
    Returns:
        List of recent benchmark records
    """
    query = client.table('benchmark_snapshots') \
        .select('*') \
        .eq('is_current', True) \
        .order('created_at', desc=True) \
        .limit(limit)
    
    if model_pattern:
        query = query.ilike('model_version', f'%{model_pattern}%')
    
    if commit_sha:
        query = query.eq('commit_sha', commit_sha)
    
    response = query.execute()
    return response.data if response.data else []


def format_timestamp(timestamp_str: str) -> str:
    """Format ISO timestamp to readable string."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except (ValueError, AttributeError):
        return timestamp_str


def display_benchmark(record: Dict[str, Any], index: int) -> None:
    """Display a single benchmark record in readable format."""
    metrics = record.get('metrics', {})
    
    print(f"\n{'='*70}")
    print(f"[{index}] {record.get('model_version', 'Unknown Model')}")
    print(f"{'='*70}")
    
    # Basic info
    print(f"📅 Created:      {format_timestamp(record.get('created_at', 'Unknown'))}")
    print(f"🔗 Commit:       {record.get('commit_sha', 'Unknown')[:8]}")
    print(f"🌍 Environment:  {record.get('environment', 'Unknown')}")
    print(f"📊 Dataset:      {record.get('dataset_version', 'Unknown')}")
    
    # Metrics
    print(f"\n📈 PERFORMANCE METRICS:")
    precision = record.get('precision_score') or metrics.get('precision', 0)
    recall = record.get('recall_score') or metrics.get('recall', 0)
    f1 = record.get('f1_score') or metrics.get('f1', 0)
    # domain_knowledge_detection_rate is already stored as decimal (0-1), convert to percentage
    domain_rate = metrics.get('domain_knowledge_detection_rate', 0) * 100
    
    print(f"   Precision:    {precision*100:.1f}%")
    print(f"   Recall:       {recall*100:.1f}%")
    print(f"   F1 Score:     {f1:.3f}")
    print(f"   Domain Rate:  {domain_rate:.1f}%")
    
    # Additional metrics
    total_patients = metrics.get('total_patients', 0)
    successful = metrics.get('successful_analyses', 0)
    success_rate = metrics.get('success_rate', 0) * 100
    latency = record.get('latency_ms') or metrics.get('latency_ms', 0)
    
    print(f"\n📊 EXECUTION METRICS:")
    print(f"   Patients:     {successful}/{total_patients} ({success_rate:.1f}% success)")
    print(f"   Latency:      {latency:.0f}ms")
    
    # Validation status
    if domain_rate == 0:
        print(f"\n⚠️  WARNING: 0% domain detection - this may indicate endpoint failures")
    elif domain_rate < 10:
        print(f"\n⚠️  CAUTION: Low domain detection rate ({domain_rate:.1f}%)")
    else:
        print(f"\n✅ Validation: PASSED (domain rate > 10%)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify benchmark results in Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Check latest results for all models
    python3 scripts/verify_supabase_results.py

    # Check specific model
    python3 scripts/verify_supabase_results.py --model medgemma

    # Check results from specific commit
    python3 scripts/verify_supabase_results.py --commit-sha abc123

    # Show last 10 results
    python3 scripts/verify_supabase_results.py --limit 10
        """
    )
    
    parser.add_argument(
        '--model',
        type=str,
        help='Model name pattern to filter (e.g., medgemma, openai)'
    )
    parser.add_argument(
        '--commit-sha',
        type=str,
        help='Specific commit SHA to filter'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Maximum number of results to show (default: 5)'
    )
    
    args = parser.parse_args()
    
    # Get Supabase client
    try:
        client = get_supabase_client()
        print("✅ Connected to Supabase\n")
    except ValueError as e:
        print(f"❌ {e}")
        return 1
    
    # Fetch results
    try:
        print(f"🔍 Fetching recent benchmark results...")
        if args.model:
            print(f"   Filter: model contains '{args.model}'")
        if args.commit_sha:
            print(f"   Filter: commit SHA = {args.commit_sha}")
        print(f"   Limit: {args.limit} results\n")
        
        results = get_recent_benchmarks(
            client=client,
            model_pattern=args.model,
            commit_sha=args.commit_sha,
            limit=args.limit
        )
        
        if not results:
            print("❌ No benchmark results found matching your criteria")
            return 1
        
        print(f"✅ Found {len(results)} benchmark result(s)")
        
        # Display results
        for i, record in enumerate(results, 1):
            display_benchmark(record, i)
        
        # Summary
        print(f"\n{'='*70}")
        print(f"📊 SUMMARY")
        print(f"{'='*70}")
        print(f"Total results found: {len(results)}")
        
        # Check for validation issues
        failed_count = sum(1 for r in results
                           if r.get('metrics', {}).get('domain_knowledge_detection_rate', 0) == 0)
        if failed_count > 0:
            print(f"⚠️  Warning: {failed_count} result(s) with 0% domain detection")
            print(f"   These may indicate endpoint failures and should be reviewed.")
        else:
            print(f"✅ All results passed validation checks")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error fetching results: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
