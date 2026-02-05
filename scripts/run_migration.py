#!/usr/bin/env python3
"""
Run database migration to add benchmark_type column.

This script applies the migration using psycopg2 for direct PostgreSQL access.
Alternatively, you can run the SQL manually in Supabase SQL Editor.

Usage:
    python scripts/run_migration.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration_manual_instructions():
    """Provide manual instructions for running migration."""
    print("=" * 70)
    print("🔄 DATABASE MIGRATION REQUIRED")
    print("=" * 70)
    print("\nThe benchmark_type column needs to be added to support patient benchmarks.")
    print("\n📝 MANUAL STEPS:")
    print("\n1. Go to your Supabase Dashboard:")
    print("   https://supabase.com/dashboard/project/YOUR_PROJECT_ID")
    print("\n2. Navigate to: SQL Editor")
    print("\n3. Create a new query and paste this SQL:")
    print("\n" + "-" * 70)
    
    migration_file = Path(__file__).parent.parent / 'sql' / 'migration_add_benchmark_type.sql'
    if migration_file.exists():
        sql = migration_file.read_text()
        # Print just the essential parts
        lines = sql.split('\n')
        in_essential = False
        for line in lines:
            if 'ALTER TABLE' in line or 'CREATE INDEX' in line or in_essential:
                print(line)
                in_essential = True
                if line.strip().endswith(';'):
                    in_essential = False
    
    print("-" * 70)
    print("\n4. Click 'Run' to execute the migration")
    print("\n5. Verify success by running:")
    print("   SELECT benchmark_type FROM benchmark_transactions LIMIT 1;")
    print("\n6. Then re-run your benchmark push command")
    print("\n" + "=" * 70)

def try_psycopg2_migration():
    """Try to run migration using psycopg2 if available."""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Parse Supabase URL to get connection details
        supabase_url = os.getenv('SUPABASE_URL')
        if not supabase_url:
            return False
        
        # Supabase connection string format
        db_url = os.getenv('SUPABASE_DB_URL') or os.getenv('DATABASE_URL')
        if not db_url:
            print("⚠️  SUPABASE_DB_URL not found in .env")
            print("   Add your database connection string to .env:")
            print("   SUPABASE_DB_URL=postgresql://postgres:[password]@[host]:5432/postgres")
            return False
        
        print("🔄 Connecting to Supabase database...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        migration_file = Path(__file__).parent.parent / 'sql' / 'migration_add_benchmark_type.sql'
        sql = migration_file.read_text()
        
        print("📝 Running migration...")
        cursor.execute(sql)
        conn.commit()
        
        print("✅ Migration completed successfully!")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM benchmark_transactions")
        count = cursor.fetchone()[0]
        print(f"✅ Verified: benchmark_transactions has {count} records")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("⚠️  psycopg2 not installed")
        print("   Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Main entry point."""
    print("\n🔄 Benchmark Monitoring Migration Tool\n")
    
    # Try automated migration first
    if try_psycopg2_migration():
        print("\n🎉 Migration complete! You can now push patient benchmarks.")
        return 0
    
    # Fall back to manual instructions
    print("\n")
    run_migration_manual_instructions()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
