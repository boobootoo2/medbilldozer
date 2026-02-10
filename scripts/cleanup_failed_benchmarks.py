#!/usr/bin/env python3
"""
Cleanup Failed Benchmark Results from Supabase

This script removes benchmark entries with 0% domain detection rates, which
indicate endpoint failures (503 errors, DNS failures, etc.) rather than
legitimate model performance.

Usage:
    # Dry run (preview only)
    python scripts/cleanup_failed_benchmarks.py --dry-run

    # Delete medgemma entries with 0% domain detection
    python scripts/cleanup_failed_benchmarks.py --model medgemma

    # Delete medgemma-ensemble entries
    python scripts/cleanup_failed_benchmarks.py --model medgemma-ensemble

    # Delete both
    python scripts/cleanup_failed_benchmarks.py --model medgemma --model medgemma-ensemble

    # Delete all models with 0% domain detection
    python scripts/cleanup_failed_benchmarks.py --all
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
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


def find_failed_benchmarks(
    client: Client, 
    model_patterns: List[str] = None,
    all_models: bool = False
) -> List[Dict[str, Any]]:
    """
    Find benchmark entries with 0% domain detection (indicating endpoint failures).
    
    Args:
        client: Supabase client
        model_patterns: List of model name patterns to search for
        all_models: If True, search across all models
    
    Returns:
        List of failed benchmark records with transaction IDs and snapshot IDs
    """
    print("\n🔍 Searching for failed benchmarks (0% domain detection)...")
    
    # Query benchmark_snapshots for 0% recall
    # Domain detection is stored as 'recall' or 'domain_knowledge_detection_rate' in metrics
    query = client.table('benchmark_snapshots').select('*')
    
    # Filter by model if specified
    if model_patterns and not all_models:
        # Build OR conditions for multiple model patterns
        # Format: "model_version.ilike.%pattern1%,model_version.ilike.%pattern2%"
        or_conditions = ','.join([f'model_version.ilike.%{pattern}%' for pattern in model_patterns])
        query = query.or_(or_conditions)
    
    response = query.execute()
    
    if not response.data:
        print("   No benchmark snapshots found.")
        return []
    
    # Filter for 0% domain detection
    failed_records = []
    for record in response.data:
        metrics = record.get('metrics', {})
        
        # Check multiple possible metric fields for 0% domain detection
        recall = metrics.get('recall', None)
        domain_rate = metrics.get('domain_knowledge_detection_rate', None)
        
        # Consider it failed if recall = 0 OR domain_knowledge_detection_rate = 0
        is_failed = False
        if recall is not None and recall == 0.0:
            is_failed = True
        if domain_rate is not None and domain_rate == 0.0:
            is_failed = True
        
        if is_failed:
            failed_records.append({
                'snapshot_id': record['id'],
                'transaction_id': record['transaction_id'],
                'model_version': record['model_version'],
                'dataset_version': record['dataset_version'],
                'prompt_version': record['prompt_version'],
                'environment': record['environment'],
                'created_at': record['created_at'],
                'recall': recall,
                'domain_rate': domain_rate,
                'f1_score': record.get('f1_score'),
                'metrics': metrics
            })
    
    return failed_records


def display_failed_records(records: List[Dict[str, Any]]) -> None:
    """Display failed records in a readable format."""
    if not records:
        print("   ✅ No failed benchmarks found!")
        return
    
    print(f"\n📋 Found {len(records)} failed benchmark(s):\n")
    
    for i, record in enumerate(records, 1):
        print(f"   {i}. Model: {record['model_version']}")
        print(f"      Dataset: {record['dataset_version']}")
        print(f"      Prompt: {record['prompt_version']}")
        print(f"      Environment: {record['environment']}")
        print(f"      Created: {record['created_at']}")
        print(f"      Recall: {record['recall']}")
        print(f"      Domain Rate: {record['domain_rate']}")
        print(f"      F1: {record['f1_score']}")
        print(f"      Snapshot ID: {record['snapshot_id']}")
        print(f"      Transaction ID: {record['transaction_id']}")
        
        # Show some metrics context
        metrics = record.get('metrics', {})
        total = metrics.get('total_patients', 0)
        successful = metrics.get('successful_analyses', 0)
        print(f"      Patients: {successful}/{total} successful")
        print()


def delete_failed_benchmarks(
    client: Client,
    records: List[Dict[str, Any]],
    dry_run: bool = True
) -> None:
    """
    Delete failed benchmark records from both snapshots and transactions tables.
    
    Args:
        client: Supabase client
        records: List of failed records to delete
        dry_run: If True, only preview what would be deleted
    """
    if not records:
        print("   ✅ Nothing to delete.")
        return
    
    if dry_run:
        print(f"\n🔎 DRY RUN MODE - Would delete {len(records)} records")
        print("   Run without --dry-run to actually delete")
        return
    
    print(f"\n🗑️  Deleting {len(records)} failed benchmark(s)...")
    
    snapshot_ids = [r['snapshot_id'] for r in records]
    transaction_ids = list(set([r['transaction_id'] for r in records]))  # Unique transaction IDs
    
    deleted_snapshots = 0
    deleted_transactions = 0
    
    # Delete from benchmark_snapshots first (child table with FK constraint)
    try:
        for snapshot_id in snapshot_ids:
            response = client.table('benchmark_snapshots').delete().eq('id', snapshot_id).execute()
            if response.data:
                deleted_snapshots += 1
                print(f"   ✓ Deleted snapshot: {snapshot_id}")
    except Exception as e:
        print(f"   ❌ Error deleting snapshots: {e}")
    
    # Delete from benchmark_transactions (parent table)
    try:
        for transaction_id in transaction_ids:
            # Check if any snapshots still reference this transaction
            check_response = client.table('benchmark_snapshots') \
                .select('id') \
                .eq('transaction_id', transaction_id) \
                .execute()
            
            if not check_response.data:
                # Safe to delete transaction (no more snapshots reference it)
                response = client.table('benchmark_transactions').delete().eq('id', transaction_id).execute()
                if response.data:
                    deleted_transactions += 1
                    print(f"   ✓ Deleted transaction: {transaction_id}")
            else:
                print(f"   ⚠️  Skipping transaction {transaction_id} (still has snapshots)")
    except Exception as e:
        print(f"   ❌ Error deleting transactions: {e}")
    
    print(f"\n✅ Cleanup complete!")
    print(f"   Deleted {deleted_snapshots} snapshot(s)")
    print(f"   Deleted {deleted_transactions} transaction(s)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clean up failed benchmark results with 0%% domain detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Dry run - preview what would be deleted
    python scripts/cleanup_failed_benchmarks.py --dry-run

    # Delete medgemma entries with 0%% domain detection
    python scripts/cleanup_failed_benchmarks.py --model medgemma

    # Delete both medgemma and medgemma-ensemble
    python scripts/cleanup_failed_benchmarks.py --model medgemma --model medgemma-ensemble

    # Delete all models with 0%% domain detection
    python scripts/cleanup_failed_benchmarks.py --all

Notes:
    - 0%% domain detection indicates endpoint failures (503, DNS errors, etc.)
    - This does NOT delete legitimate benchmark results
    - Use --dry-run first to preview deletions
        """
    )
    
    parser.add_argument(
        '--model',
        action='append',
        help='Model name pattern to clean up (can specify multiple times). Example: medgemma'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Clean up all models with 0%% domain detection'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be deleted without actually deleting'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.model and not args.all:
        print("❌ Error: Must specify either --model or --all")
        parser.print_help()
        return 1
    
    # Get Supabase client
    try:
        client = get_supabase_client()
        print("✅ Connected to Supabase")
    except ValueError as e:
        print(f"❌ {e}")
        return 1
    
    # Find failed benchmarks
    try:
        failed_records = find_failed_benchmarks(
            client=client,
            model_patterns=args.model,
            all_models=args.all
        )
    except Exception as e:
        print(f"❌ Error searching for failed benchmarks: {e}")
        return 1
    
    # Display results
    display_failed_records(failed_records)
    
    # Delete if not dry run
    if failed_records:
        if args.dry_run:
            print("\n💡 Tip: Run without --dry-run to actually delete these records")
        else:
            # Confirm deletion
            confirm = input("\n⚠️  Are you sure you want to DELETE these records? (yes/no): ")
            if confirm.lower() != 'yes':
                print("❌ Deletion cancelled")
                return 1
        
        delete_failed_benchmarks(
            client=client,
            records=failed_records,
            dry_run=args.dry_run
        )
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
