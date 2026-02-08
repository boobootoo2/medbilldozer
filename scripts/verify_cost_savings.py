#!/usr/bin/env python3
"""
Verify cost savings data locally and in Supabase.
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_local_files():
    """Check if local benchmark files have cost savings."""
    print("=" * 70)
    print("LOCAL BENCHMARK FILES")
    print("=" * 70)
    
    results_dir = Path("benchmarks/results")
    files = list(results_dir.glob("patient_benchmark_*.json"))
    
    if not files:
        print("❌ No benchmark files found")
        return False
    
    all_have_savings = True
    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)
        
        model = data.get('model_name', 'Unknown')
        has_savings = 'total_potential_savings' in data
        savings = data.get('total_potential_savings', 0)
        capture_rate = data.get('savings_capture_rate', 0)
        
        status = "✅" if has_savings else "❌"
        print(f"{status} {file.name}")
        print(f"   Model: {model}")
        if has_savings:
            print(f"   Savings: ${savings:,.2f} (Capture: {capture_rate:.1f}%)")
        else:
            print(f"   Missing cost savings metrics - needs re-run")
            all_have_savings = False
    
    return all_have_savings

def check_supabase():
    """Check if Supabase has cost savings columns and data."""
    load_dotenv()
    
    print("\n" + "=" * 70)
    print("SUPABASE DATABASE")
    print("=" * 70)
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    try:
        from supabase import create_client
        client = create_client(url, key)
        
        # Try to select cost savings columns
        response = client.table('benchmark_snapshots').select(
            'model_version, total_potential_savings, savings_capture_rate'
        ).eq('is_current', True).limit(5).execute()
        
        if response.data:
            print("✅ Cost savings columns exist in database\n")
            print("Current data:")
            for row in response.data:
                model = row['model_version']
                savings = row.get('total_potential_savings', 0) or 0
                rate = row.get('savings_capture_rate', 0) or 0
                print(f"  {model}: ${savings:,.2f} ({rate:.1f}%)")
            return True
        else:
            print("⚠️  Columns exist but no current snapshots found")
            return True
            
    except Exception as e:
        error_msg = str(e)
        if 'column' in error_msg.lower() and 'does not exist' in error_msg.lower():
            print("❌ Cost savings columns DO NOT exist in database")
            print("\n📋 You need to run the database migration:")
            print("   1. Open Supabase SQL Editor")
            print("   2. Run: sql/combined_cost_savings_migration.sql")
            return False
        else:
            print(f"❌ Error checking database: {error_msg}")
            return False

def main():
    print("\n🔍 COST SAVINGS VERIFICATION\n")
    
    local_ok = check_local_files()
    supabase_ok = check_supabase()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if local_ok and supabase_ok:
        print("✅ Everything is set up correctly!")
        print("\n📊 Restart your dashboard to see cost savings:")
        print("   python3 -m streamlit run pages/production_stability.py --server.port 8502")
    elif local_ok and not supabase_ok:
        print("⚠️  Local files have cost savings, but database needs migration")
        print("\n📋 Next steps:")
        print("   1. Run migration: sql/combined_cost_savings_migration.sql in Supabase")
        print("   2. Re-push data: ./scripts/push_local_benchmarks.sh")
        print("   3. Restart dashboard")
    elif not local_ok:
        print("⚠️  Local benchmark files need to be regenerated")
        print("\n📋 Next steps:")
        print("   1. Re-run benchmarks: python3 scripts/generate_patient_benchmarks.py --model all")
        print("   2. Run migration: sql/combined_cost_savings_migration.sql in Supabase")
        print("   3. Push data: ./scripts/push_local_benchmarks.sh")
        print("   4. Restart dashboard")
    
    print("=" * 70)
    return 0 if (local_ok and supabase_ok) else 1

if __name__ == '__main__':
    sys.exit(main())
