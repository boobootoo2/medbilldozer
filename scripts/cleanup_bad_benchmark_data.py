#!/usr/bin/env python3
"""
Clean up bad benchmark data from Supabase.

This script removes:
1. Entries where Heuristic Baseline F1 score went above 0
2. Entries where other models have 0 F1 score
"""

import os
import sys
from datetime import datetime
from supabase import create_client


def main():
    """Clean up bad benchmark data."""
    # Initialize Supabase client
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        sys.exit(1)
    
    supabase = create_client(url, key)
    
    print("🔍 Fetching all benchmark transactions...")
    
    # Fetch all transactions
    response = supabase.table('benchmark_transactions').select('*').execute()
    
    if not response.data:
        print("No data found.")
        return
    
    print(f"📊 Found {len(response.data)} total transactions")
    
    to_delete = []
    
    for transaction in response.data:
        transaction_id = transaction.get('id')
        model_version = transaction.get('model_version', '')
        metrics = transaction.get('metrics', {})
        created_at = transaction.get('created_at', '')
        
        # Get F1 score from metrics
        f1_score = None
        if isinstance(metrics, dict):
            f1_score = metrics.get('f1_score')
            if f1_score is None:
                f1_score = metrics.get('f1')
        
        if f1_score is None:
            continue
            
        # Rule 1: Delete if Heuristic Baseline has F1 > 0
        if 'heuristic' in model_version.lower() or 'baseline' in model_version.lower():
            if f1_score > 0:
                to_delete.append({
                    'id': transaction_id,
                    'model': model_version,
                    'f1': f1_score,
                    'reason': 'Heuristic Baseline F1 > 0',
                    'created_at': created_at
                })
        
        # Rule 2: Delete if any other model has F1 == 0
        else:
            if f1_score == 0:
                to_delete.append({
                    'id': transaction_id,
                    'model': model_version,
                    'f1': f1_score,
                    'reason': 'Model F1 == 0',
                    'created_at': created_at
                })
    
    if not to_delete:
        print("✅ No bad data found to delete!")
        return
    
    print(f"\n🗑️  Found {len(to_delete)} transactions to delete:\n")
    
    # Group by reason
    by_reason = {}
    for item in to_delete:
        reason = item['reason']
        if reason not in by_reason:
            by_reason[reason] = []
        by_reason[reason].append(item)
    
    for reason, items in by_reason.items():
        print(f"  {reason}: {len(items)} transactions")
        for item in items[:5]:  # Show first 5 examples
            print(f"    - {item['model']} (F1={item['f1']}, {item['created_at']})")
        if len(items) > 5:
            print(f"    ... and {len(items) - 5} more")
        print()
    
    # Confirm deletion
    response = input(f"\n⚠️  Delete these {len(to_delete)} transactions? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Cancelled.")
        return
    
    # Delete transactions (and related snapshots via CASCADE or manual deletion)
    print("\n🗑️  Deleting transactions and related snapshots...")
    deleted_count = 0
    failed_count = 0
    
    for item in to_delete:
        try:
            # First, delete related snapshots
            supabase.table('benchmark_snapshots').delete().eq('transaction_id', item['id']).execute()
            
            # Then delete the transaction
            supabase.table('benchmark_transactions').delete().eq('id', item['id']).execute()
            deleted_count += 1
            if deleted_count % 10 == 0:
                print(f"  Deleted {deleted_count}/{len(to_delete)}...")
        except Exception as e:
            print(f"  ❌ Failed to delete {item['id']}: {e}")
            failed_count += 1
    
    print(f"\n✅ Cleanup complete!")
    print(f"   Deleted: {deleted_count}")
    if failed_count > 0:
        print(f"   Failed: {failed_count}")
    
    # Show remaining transactions
    response = supabase.table('benchmark_transactions').select('model_version').execute()
    remaining_models = {}
    for t in response.data:
        model = t.get('model_version', 'unknown')
        remaining_models[model] = remaining_models.get(model, 0) + 1
    
    print(f"\n📊 Remaining transactions by model:")
    for model, count in sorted(remaining_models.items()):
        print(f"   {model}: {count}")


if __name__ == '__main__':
    main()
