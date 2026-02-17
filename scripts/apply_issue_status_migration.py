#!/usr/bin/env python3
"""Apply issue status migration to Supabase database."""
import os
import sys
from pathlib import Path
from supabase import create_client

def apply_migration():
    """Apply the issue status migration."""
    # Get Supabase credentials from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        sys.exit(1)

    # Read migration SQL
    migration_path = Path(__file__).parent.parent / "sql" / "migration_add_issue_status.sql"
    with open(migration_path) as f:
        migration_sql = f.read()

    # Connect to Supabase
    print(f"Connecting to Supabase: {supabase_url}")
    supabase = create_client(supabase_url, supabase_key)

    # Execute migration
    print("Applying migration...")
    try:
        # Note: Supabase client doesn't directly support SQL execution
        # This is a placeholder - in production, use Supabase SQL Editor or psycopg2
        print("\nMigration SQL:")
        print("=" * 80)
        print(migration_sql)
        print("=" * 80)
        print("\n⚠️  MANUAL STEP REQUIRED:")
        print("Copy the SQL above and execute it in the Supabase SQL Editor at:")
        print(f"{supabase_url.replace('https://', 'https://app.')}/project/_/sql")
        print("\nOr use psycopg2 to execute directly:")
        print("  psql 'postgresql://postgres:[password]@[host]:5432/postgres' -f sql/migration_add_issue_status.sql")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    apply_migration()
