#!/usr/bin/env python3
"""
Fetch all transactions from Supabase benchmark_transactions table.

Usage:
    python scripts/get_supabase_transactions.py [--limit N] [--format json|table]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

def get_all_transactions(limit: int = None, model_version: str = None):
    """Fetch all transactions from Supabase."""
    
    # Get Supabase credentials
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        sys.exit(1)
    
    # Create Supabase client
    supabase: Client = create_client(url, key)
    
    print(f"📊 Fetching transactions from Supabase...")
    print("=" * 80)
    
    try:
        # Build query
        query = supabase.table('benchmark_transactions').select('*')
        
        if model_version:
            query = query.eq('model_version', model_version)
        
        query = query.order('created_at', desc=True)
        
        if limit:
            query = query.limit(limit)
        
        # Execute query
        response = query.execute()
        
        transactions = response.data
        count = len(transactions)
        
        print(f"✅ Found {count} transaction(s)\n")
        
        return transactions
        
    except Exception as e:
        print(f"❌ Error fetching transactions: {e}")
        sys.exit(1)

def print_as_table(transactions):
    """Print transactions in table format."""
    if not transactions:
        print("No transactions found.")
        return
    
    print(f"{'ID':<36} {'Model Version':<30} {'Environment':<15} {'Created At':<20}")
    print("-" * 105)
    
    for tx in transactions:
        tx_id = tx.get('id', 'N/A')
        model_version = tx.get('model_version', 'N/A')
        environment = tx.get('environment', 'N/A')
        created_at = tx.get('created_at', 'N/A')[:19] if tx.get('created_at') else 'N/A'
        
        print(f"{tx_id:<36} {model_version:<30} {environment:<15} {created_at:<20}")
    
    print(f"\nTotal: {len(transactions)} transaction(s)")

def print_as_json(transactions):
    """Print transactions as JSON."""
    print(json.dumps(transactions, indent=2))

def main():
    parser = argparse.ArgumentParser(
        description='Fetch all transactions from Supabase benchmark_transactions table'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of results (default: all)'
    )
    parser.add_argument(
        '--model',
        type=str,
        help='Filter by model_version'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'table'],
        default='table',
        help='Output format (default: table)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Save to file instead of stdout'
    )
    
    args = parser.parse_args()
    
    # Fetch transactions
    transactions = get_all_transactions(limit=args.limit, model_version=args.model)
    
    # Format output
    if args.format == 'json':
        output = json.dumps(transactions, indent=2)
    else:
        # Capture table output
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            print_as_table(transactions)
        output = f.getvalue()
    
    # Write to file or stdout
    if args.output:
        with open(args.output, 'w') as f:
            if args.format == 'json':
                f.write(output)
            else:
                f.write(output)
        print(f"\n✅ Output saved to {args.output}")
    else:
        if args.format == 'json':
            print(output)
        else:
            print_as_table(transactions)

if __name__ == '__main__':
    main()
