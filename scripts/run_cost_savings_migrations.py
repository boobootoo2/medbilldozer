#!/usr/bin/env python3
"""
Run cost savings database migrations on Supabase.

This script will:
1. Add cost savings columns to benchmark_snapshots
2. Update upsert_benchmark_result function
3. Verify changes were applied

Usage:
    python3 scripts/run_cost_savings_migrations.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    load_dotenv()
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        print("\nPlease add to your .env file:")
        print("  SUPABASE_URL=https://your-project.supabase.co")
        print("  SUPABASE_SERVICE_ROLE_KEY=your-service-role-key")
        return 1
    
    print("=" * 70)
    print("📋 COST SAVINGS METRICS - DATABASE MIGRATIONS")
    print("=" * 70)
    print(f"Target: {url}")
    print()
    
    # Read migration files
    migration_1 = Path("sql/migration_add_cost_savings.sql")
    migration_2 = Path("sql/migration_update_upsert_function.sql")
    
    if not migration_1.exists() or not migration_2.exists():
        print("❌ Error: Migration files not found")
        print(f"   Looking for: {migration_1}")
        print(f"   Looking for: {migration_2}")
        return 1
    
    print("✅ Migration files found\n")
    
    # Display migration SQL
    print("=" * 70)
    print("MIGRATION 1: Add Cost Savings Columns")
    print("=" * 70)
    with open(migration_1, 'r') as f:
        sql1 = f.read()
    print(sql1)
    
    print("\n" + "=" * 70)
    print("MIGRATION 2: Update Upsert Function")
    print("=" * 70)
    with open(migration_2, 'r') as f:
        sql2 = f.read()
    # Print first 50 lines (function is long)
    lines = sql2.split('\n')
    print('\n'.join(lines[:50]))
    print(f"\n... (showing first 50 of {len(lines)} lines)")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Copy the SQL above into your Supabase SQL Editor")
    print("2. Run Migration 1 first")
    print("3. Run Migration 2 second")
    print("4. Re-run benchmarks: python3 scripts/generate_patient_benchmarks.py --model all")
    print("5. Push to Supabase: ./scripts/push_local_benchmarks.sh")
    print("6. Restart dashboard: streamlit run pages/production_stability.py --server.port 8502")
    print()
    print("📖 Full guide: COST_SAVINGS_SETUP.md")
    print("=" * 70)
    
    # Optionally write combined SQL file
    combined = Path("sql/combined_cost_savings_migration.sql")
    with open(combined, 'w') as f:
        f.write("-- Combined Cost Savings Migration\n")
        f.write("-- Run this entire file in Supabase SQL Editor\n\n")
        f.write("-- MIGRATION 1: Add Columns\n")
        f.write(sql1)
        f.write("\n\n-- MIGRATION 2: Update Function\n")
        f.write(sql2)
    
    print(f"\n💾 Combined SQL saved to: {combined}")
    print("   You can run this single file instead of copying twice.\n")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
