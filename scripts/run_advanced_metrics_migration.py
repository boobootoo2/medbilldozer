#!/usr/bin/env python3
"""
Run Advanced Metrics Migration on Supabase

This script executes the advanced metrics database migration on your Supabase instance.
It adds:
- benchmark_category_metrics table for per-category tracking
- Regression detection functions
- Advanced metrics views
- Category delta calculation

Usage:
    python3 scripts/run_advanced_metrics_migration.py
    
Environment Variables Required:
    SUPABASE_URL - Your Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY - Your Supabase service role key
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_supabase_client() -> Client:
    """Create Supabase client from environment variables."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        print("\nSet them with:")
        print("  export SUPABASE_URL='https://your-project.supabase.co'")
        print("  export SUPABASE_SERVICE_ROLE_KEY='your-service-role-key'")
        sys.exit(1)
    
    return create_client(url, key)


def run_migration(client: Client, sql_path: Path) -> bool:
    """
    Run SQL migration file on Supabase.
    
    Note: Supabase Python client doesn't have direct SQL execution,
    so we'll use the RPC function approach or guide manual execution.
    """
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(f"📄 Loaded migration from: {sql_path}")
    print(f"📊 SQL content size: {len(sql_content)} bytes")
    print()
    
    # Split SQL into individual statements
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]
    
    print(f"🔍 Found {len(statements)} SQL statements to execute")
    print()
    
    # Supabase Python SDK doesn't support direct SQL execution via client
    # We need to use the SQL editor in Supabase Dashboard or psql
    print("⚠️  The Supabase Python SDK doesn't support direct SQL execution.")
    print("📋 You have two options to run the migration:\n")
    
    print("OPTION 1: Use Supabase Dashboard (Recommended)")
    print("-" * 60)
    print("1. Go to: https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Click 'SQL Editor' in the left sidebar")
    print("4. Click 'New Query'")
    print("5. Copy the contents of:")
    print(f"   {sql_path}")
    print("6. Paste into the SQL editor")
    print("7. Click 'Run' (or press Cmd+Enter)")
    print()
    
    print("OPTION 2: Use psql command line")
    print("-" * 60)
    print("Extract database connection details from SUPABASE_URL:")
    
    # Try to parse connection details from URL
    url = os.getenv('SUPABASE_URL', '')
    if 'supabase.co' in url:
        # Extract project ID from URL
        project_id = url.replace('https://', '').replace('.supabase.co', '')
        print(f"""
psql "postgresql://postgres:[YOUR_DB_PASSWORD]@db.{project_id}.supabase.co:5432/postgres" \\
     -f {sql_path}

Your database password can be found in:
Supabase Dashboard > Project Settings > Database > Connection string
""")
    else:
        print(f"psql [YOUR_CONNECTION_STRING] -f {sql_path}")
    
    print()
    print("=" * 60)
    print("After running the migration, verify with:")
    print("=" * 60)
    print("SELECT * FROM benchmark_category_metrics LIMIT 1;")
    print("SELECT * FROM v_advanced_benchmark_metrics LIMIT 1;")
    print("SELECT * FROM v_category_regression_tracking LIMIT 5;")
    print()
    
    return False  # Return False since we're not actually executing


def verify_migration(client: Client) -> bool:
    """Verify the migration was successful."""
    print("🔍 Verifying migration...")
    
    try:
        # Try to query the new table
        result = client.table('benchmark_category_metrics').select('*').limit(1).execute()
        print("✅ benchmark_category_metrics table exists")
        
        # Try to query the views (views appear as regular selects in Supabase)
        # We can check if data is structured correctly
        result = client.table('benchmark_transactions').select('metrics').limit(1).execute()
        if result.data:
            print("✅ benchmark_transactions table accessible")
        
        print()
        print("🎉 Migration verification successful!")
        print()
        print("Next steps:")
        print("1. Run a benchmark: python3 scripts/generate_patient_benchmarks.py --model baseline")
        print("2. Push to Supabase: ./scripts/push_local_benchmarks.sh baseline")
        print("3. Check advanced metrics in dashboard")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration verification failed: {e}")
        print()
        print("This likely means the migration hasn't been run yet.")
        print("Please follow the instructions above to run the migration.")
        return False


def main():
    """Main execution."""
    print("=" * 60)
    print("Advanced Metrics Migration for Supabase")
    print("=" * 60)
    print()
    
    # Get Supabase client
    client = get_supabase_client()
    print("✅ Connected to Supabase")
    print()
    
    # Locate migration file
    migration_path = PROJECT_ROOT / "sql" / "migration_advanced_metrics.sql"
    
    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_path}")
        sys.exit(1)
    
    # Run migration (will provide instructions)
    run_migration(client, migration_path)
    
    # Offer to verify
    print()
    response = input("Have you run the migration? (y/N): ").strip().lower()
    
    if response == 'y':
        verify_migration(client)
    else:
        print()
        print("Run the migration using one of the options above, then:")
        print("  python3 scripts/run_advanced_metrics_migration.py")
        print()


if __name__ == "__main__":
    main()
