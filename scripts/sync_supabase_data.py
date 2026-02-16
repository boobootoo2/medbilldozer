#!/usr/bin/env python3
"""
Sync data from main Supabase to beta Supabase.

This script copies all data from the production/main Supabase instance
to the beta Supabase instance for testing and development purposes.

Usage:
    python scripts/sync_supabase_data.py [--dry-run] [--tables TABLE1,TABLE2]

Environment Variables Required:
    - SUPABASE_URL: Main Supabase URL
    - SUPABASE_KEY: Main Supabase service role key
    - SUPABASE_BETA_URL: Beta Supabase URL
    - SUPABASE_BETA_KEY: Beta Supabase service role key
"""

import os
import sys
import argparse
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

try:
    from supabase import create_client, Client
except ImportError:
    print("Error: supabase package not installed")
    print("Install with: pip install supabase")
    sys.exit(1)


class SupabaseSync:
    """Handle syncing data between two Supabase instances."""
    
    # Tables to sync in order (respecting foreign key dependencies)
    # IMPORTANT: benchmark_transactions MUST come before benchmark_snapshots
    # because benchmark_snapshots has a foreign key to benchmark_transactions
    DEFAULT_TABLES = [
        "receipts",
        "providers",
        "insurance_plans",
        "benchmark_transactions",  # Must be synced first (parent table)
        "benchmark_snapshots",     # Must be synced second (has FK to transactions)
    ]
    
    def __init__(
        self,
        source_url: str,
        source_key: str,
        target_url: str,
        target_key: str,
        dry_run: bool = False
    ):
        """Initialize sync clients.
        
        Args:
            source_url: Source Supabase URL
            source_key: Source Supabase service role key
            target_url: Target Supabase URL
            target_key: Target Supabase service role key
            dry_run: If True, only simulate the sync without making changes
        """
        self.source: Client = create_client(source_url, source_key)
        self.target: Client = create_client(target_url, target_key)
        self.dry_run = dry_run
        self.stats = {
            "tables_synced": 0,
            "records_copied": 0,
            "errors": 0,
            "skipped": 0
        }
        
    def table_exists(self, client: Client, table: str) -> bool:
        """Check if a table exists in the database.
        
        Args:
            client: Supabase client to check
            table: Table name
            
        Returns:
            True if table exists, False otherwise
        """
        try:
            # Try to select zero rows - if table exists, this succeeds
            response = client.table(table).select("*").limit(0).execute()
            return True
        except Exception as e:
            error_msg = str(e)
            if "PGRST205" in error_msg or "Could not find the table" in error_msg:
                return False
            # Some other error - assume table exists but has permission issues
            return True
    
    def get_table_data(self, table: str) -> List[Dict[str, Any]]:
        """Fetch all data from a table in source database.
        
        Args:
            table: Table name
            
        Returns:
            List of records as dictionaries
        """
        try:
            response = self.source.table(table).select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"  ❌ Error reading from {table}: {e}")
            self.stats["errors"] += 1
            return []
    
    def clear_table(self, table: str) -> bool:
        """Clear all data from a table in target database.
        
        Args:
            table: Table name
            
        Returns:
            True if successful, False otherwise
        """
        if self.dry_run:
            print(f"  [DRY RUN] Would clear table: {table}")
            return True
            
        try:
            # Delete all records (Supabase doesn't have TRUNCATE via REST API)
            # We'll need to delete in batches if there are many records
            response = self.target.table(table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            return True
        except Exception as e:
            print(f"  ⚠️  Warning: Could not clear {table}: {e}")
            # Continue anyway - table might be empty or have different structure
            return True
    
    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> bool:
        """Insert data into target table.
        
        Args:
            table: Table name
            data: List of records to insert
            
        Returns:
            True if successful, False otherwise
        """
        if not data:
            print(f"  ℹ️  No data to sync for {table}")
            self.stats["skipped"] += 1
            return True
            
        if self.dry_run:
            print(f"  [DRY RUN] Would insert {len(data)} records into {table}")
            self.stats["records_copied"] += len(data)
            return True
        
        try:
            # Insert in batches of 100 to avoid API limits
            batch_size = 100
            total_inserted = 0
            
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                response = self.target.table(table).insert(batch).execute()
                total_inserted += len(batch)
                
                if (i + batch_size) < len(data):
                    print(f"    Progress: {total_inserted}/{len(data)} records...")
            
            print(f"  ✅ Inserted {total_inserted} records into {table}")
            self.stats["records_copied"] += total_inserted
            return True
            
        except Exception as e:
            print(f"  ❌ Error inserting into {table}: {e}")
            self.stats["errors"] += 1
            return False
    
    def sync_table(self, table: str) -> bool:
        """Sync a single table from source to target.
        
        Args:
            table: Table name
            
        Returns:
            True if successful, False otherwise
        """
        print(f"\n📋 Syncing table: {table}")
        
        # Check if table exists in source
        print(f"  🔍 Checking if table exists in source...")
        if not self.table_exists(self.source, table):
            print(f"  ⚠️  Table does not exist in source database - skipping")
            self.stats["skipped"] += 1
            return True
        
        # Check if table exists in target
        print(f"  🔍 Checking if table exists in target...")
        if not self.table_exists(self.target, table):
            print(f"  ⚠️  Table does not exist in target database - skipping")
            print(f"  💡 Create the table in target database first, then re-run sync")
            self.stats["skipped"] += 1
            return True
        
        # Fetch data from source
        print(f"  📥 Fetching data from source...")
        data = self.get_table_data(table)
        
        if not data:
            print(f"  ℹ️  No data found in source table")
            self.stats["skipped"] += 1
            return True
        
        print(f"  📊 Found {len(data)} records")
        
        # Clear target table
        print(f"  🗑️  Clearing target table...")
        if not self.clear_table(table):
            return False
        
        # Insert data into target
        print(f"  📤 Inserting data into target...")
        success = self.insert_data(table, data)
        
        if success:
            self.stats["tables_synced"] += 1
        
        return success
    
    def sync_all(self, tables: Optional[List[str]] = None) -> bool:
        """Sync all specified tables.
        
        Args:
            tables: List of table names to sync (None = all default tables)
            
        Returns:
            True if all syncs successful, False otherwise
        """
        tables_to_sync = tables or self.DEFAULT_TABLES
        
        print("=" * 70)
        print("🔄 SUPABASE DATA SYNC")
        print("=" * 70)
        
        if self.dry_run:
            print("⚠️  DRY RUN MODE - No changes will be made")
        
        print(f"\n📋 Tables to sync: {', '.join(tables_to_sync)}")
        print(f"📊 Total tables: {len(tables_to_sync)}")
        
        start_time = datetime.now()
        
        all_success = True
        for table in tables_to_sync:
            if not self.sync_table(table):
                all_success = False
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 SYNC SUMMARY")
        print("=" * 70)
        print(f"✅ Tables synced: {self.stats['tables_synced']}/{len(tables_to_sync)}")
        print(f"📝 Records copied: {self.stats['records_copied']}")
        print(f"⏭️  Tables skipped: {self.stats['skipped']}")
        print(f"❌ Errors: {self.stats['errors']}")
        print(f"⏱️  Duration: {duration:.2f}s")
        print("=" * 70)
        
        if all_success:
            print("\n✅ Sync completed successfully!")
        else:
            print("\n⚠️  Sync completed with errors")
        
        return all_success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sync data from main Supabase to beta Supabase"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate sync without making changes"
    )
    parser.add_argument(
        "--tables",
        type=str,
        help="Comma-separated list of tables to sync (default: all)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Get environment variables
    source_url = os.getenv("SUPABASE_URL")
    source_key = os.getenv("SUPABASE_KEY")
    target_url = os.getenv("SUPABASE_BETA_URL")
    target_key = os.getenv("SUPABASE_BETA_KEY")
    
    # Validate environment variables
    missing_vars = []
    if not source_url:
        missing_vars.append("SUPABASE_URL")
    if not source_key:
        missing_vars.append("SUPABASE_KEY")
    if not target_url:
        missing_vars.append("SUPABASE_BETA_URL")
    if not target_key:
        missing_vars.append("SUPABASE_BETA_KEY")
    
    if missing_vars:
        print("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables and try again.")
        sys.exit(1)
    
    # Parse tables if specified
    tables = None
    if args.tables:
        tables = [t.strip() for t in args.tables.split(",")]
    
    # Create sync instance
    sync = SupabaseSync(
        source_url=source_url,
        source_key=source_key,
        target_url=target_url,
        target_key=target_key,
        dry_run=args.dry_run
    )
    
    # Run sync
    success = sync.sync_all(tables)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
