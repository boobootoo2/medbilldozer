#!/usr/bin/env python3
"""
Delete a specific model version from Supabase benchmark tables.

Usage:
    python scripts/delete_model_from_supabase.py --model "gemma3-v1.0"
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

def delete_model_records(model_version: str, dry_run: bool = False) -> None:
    """Delete all records for a specific model version from Supabase."""
    
    # Get Supabase credentials
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        sys.exit(1)
    
    # Create Supabase client
    supabase: Client = create_client(url, key)
    
    print(f"\n{'🔍 DRY RUN - ' if dry_run else ''}Deleting records for model: {model_version}")
    print("=" * 80)
    
    # Check snapshots table
    try:
        snapshots_response = supabase.table('benchmark_snapshots')\
            .select('id, model_version, created_at', count='exact')\
            .eq('model_version', model_version)\
            .execute()
        
        snapshot_count = len(snapshots_response.data) if snapshots_response.data else 0
        print(f"\n📊 benchmark_snapshots: {snapshot_count} records found")
        
        if snapshot_count > 0 and not dry_run:
            delete_result = supabase.table('benchmark_snapshots')\
                .delete()\
                .eq('model_version', model_version)\
                .execute()
            print(f"   ✅ Deleted {snapshot_count} snapshot(s)")
        elif snapshot_count > 0:
            print(f"   🔍 Would delete {snapshot_count} snapshot(s)")
            
    except Exception as e:
        print(f"   ❌ Error checking snapshots: {e}")
    
    # Check transactions table
    try:
        transactions_response = supabase.table('benchmark_transactions')\
            .select('id, model_version, created_at', count='exact')\
            .eq('model_version', model_version)\
            .execute()
        
        transaction_count = len(transactions_response.data) if transactions_response.data else 0
        print(f"\n📝 benchmark_transactions: {transaction_count} records found")
        
        if transaction_count > 0 and not dry_run:
            delete_result = supabase.table('benchmark_transactions')\
                .delete()\
                .eq('model_version', model_version)\
                .execute()
            print(f"   ✅ Deleted {transaction_count} transaction(s)")
        elif transaction_count > 0:
            print(f"   🔍 Would delete {transaction_count} transaction(s)")
            
    except Exception as e:
        print(f"   ❌ Error checking transactions: {e}")
    
    print("\n" + "=" * 80)
    if dry_run:
        print("🔍 DRY RUN complete - no records were deleted")
        print("Run without --dry-run to actually delete the records")
    else:
        print("✅ Deletion complete")
    print()

def main():
    parser = argparse.ArgumentParser(
        description='Delete a specific model version from Supabase benchmark tables'
    )
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Model version to delete (e.g., "gemma3-v1.0")'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    
    args = parser.parse_args()
    
    # Confirm deletion
    if not args.dry_run:
        print(f"\n⚠️  WARNING: This will permanently delete all records for '{args.model}'")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            sys.exit(0)
    
    delete_model_records(args.model, args.dry_run)

if __name__ == '__main__':
    main()
