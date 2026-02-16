"""
Migrate Clinical Validation Benchmark Data from Beta to Production
===================================================================

This script migrates benchmark data from the beta database to production,
supporting the transition from BETA-gated features to generally available.

Usage:
    python scripts/migrate_beta_to_prod.py [--dry-run] [--skip-duplicates]

Environment Variables Required:
    - SUPABASE_BETA_URL (or SUPABASE_CLINICAL_URL): Beta/source database URL
    - SUPABASE_BETA_KEY (or SUPABASE_CLINICAL_KEY): Beta/source database key
    - SUPABASE_URL: Production database URL
    - SUPABASE_SERVICE_ROLE_KEY: Production database key (needs write access)
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Error: supabase package not installed")
    print("Install with: pip install supabase")
    sys.exit(1)


class BenchmarkDataMigrator:
    """Handles migration of benchmark data from beta to production."""

    def __init__(self, dry_run: bool = False, skip_duplicates: bool = True):
        """Initialize the migrator.

        Args:
            dry_run: If True, only simulate the migration without writing data
            skip_duplicates: If True, skip records that already exist in production
        """
        self.dry_run = dry_run
        self.skip_duplicates = skip_duplicates

        # Initialize source (beta) client
        beta_url = os.getenv('SUPABASE_CLINICAL_URL') or os.getenv('SUPABASE_BETA_URL')
        beta_key = os.getenv('SUPABASE_CLINICAL_KEY') or os.getenv('SUPABASE_BETA_KEY')

        if not beta_url or not beta_key:
            raise ValueError(
                "Beta database credentials not found. Set SUPABASE_CLINICAL_URL/KEY "
                "or SUPABASE_BETA_URL/KEY environment variables."
            )

        self.beta_client: Client = create_client(beta_url, beta_key)
        print(f"✅ Connected to source database: {beta_url}")

        # Initialize destination (production) client
        prod_url = os.getenv('SUPABASE_URL')
        prod_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not prod_url or not prod_key:
            raise ValueError(
                "Production database credentials not found. Set SUPABASE_URL "
                "and SUPABASE_SERVICE_ROLE_KEY environment variables."
            )

        self.prod_client: Client = create_client(prod_url, prod_key)
        print(f"✅ Connected to destination database: {prod_url}")

    def get_beta_snapshots(self) -> List[Dict]:
        """Fetch all clinical validation snapshots from beta database.

        Returns:
            List of snapshot records
        """
        print("\n📊 Fetching snapshots from beta database...")

        try:
            response = self.beta_client.table('clinical_validation_snapshots') \
                .select('*') \
                .order('created_at', desc=False) \
                .execute()

            snapshots = response.data
            print(f"✅ Found {len(snapshots)} snapshots in beta database")
            return snapshots

        except Exception as e:
            print(f"❌ Error fetching beta snapshots: {e}")
            raise

    def get_existing_prod_snapshots(self) -> set:
        """Get set of snapshot fingerprints that already exist in production.

        Uses (model_version, created_at) as fingerprint since IDs differ between databases.

        Returns:
            Set of existing snapshot fingerprints (model, created_at tuples)
        """
        print("\n🔍 Checking for existing snapshots in production...")

        try:
            response = self.prod_client.table('clinical_validation_snapshots') \
                .select('model_version, created_at') \
                .execute()

            # Create fingerprint set using (model_version, created_at)
            existing_fingerprints = {
                (record['model_version'], record['created_at'])
                for record in response.data
            }
            print(f"✅ Found {len(existing_fingerprints)} existing snapshots in production")
            return existing_fingerprints

        except Exception as e:
            print(f"⚠️  Error fetching production snapshots: {e}")
            print("   Assuming table is empty or doesn't exist yet")
            return set()

    def migrate_snapshot(self, snapshot: Dict) -> bool:
        """Migrate a single snapshot to production.

        Args:
            snapshot: Snapshot record to migrate

        Returns:
            True if migration successful, False otherwise
        """
        old_id = snapshot.get('id')
        created_at = snapshot.get('created_at', 'unknown')
        model_version = snapshot.get('model_version', 'unknown')

        if self.dry_run:
            print(f"  [DRY RUN] Would migrate snapshot (model: {model_version}, created: {created_at})")
            return True

        try:
            # Remove the old integer ID - let PostgreSQL generate new UUID
            snapshot_copy = snapshot.copy()
            snapshot_copy.pop('id', None)  # Remove old integer ID
            snapshot_copy.pop('updated_at', None)  # Will be set by trigger

            # Insert into production database (will get new UUID)
            self.prod_client.table('clinical_validation_snapshots') \
                .insert(snapshot_copy) \
                .execute()

            print(f"  ✅ Migrated snapshot (model: {model_version}, created: {created_at})")
            return True

        except Exception as e:
            print(f"  ❌ Failed to migrate snapshot (model: {model_version}): {e}")
            return False

    def run_migration(self) -> Dict[str, int]:
        """Run the complete migration process.

        Returns:
            Dictionary with migration statistics
        """
        stats = {
            'total': 0,
            'skipped': 0,
            'migrated': 0,
            'failed': 0
        }

        print("\n" + "=" * 70)
        print("🚀 Starting Clinical Validation Data Migration")
        print("=" * 70)

        if self.dry_run:
            print("⚠️  DRY RUN MODE - No data will be written to production")

        # Fetch all snapshots from beta
        beta_snapshots = self.get_beta_snapshots()
        stats['total'] = len(beta_snapshots)

        if stats['total'] == 0:
            print("\n⚠️  No snapshots found in beta database. Nothing to migrate.")
            return stats

        # Get existing production snapshots
        existing_fingerprints = self.get_existing_prod_snapshots()

        # Migrate each snapshot
        print(f"\n📦 Migrating {stats['total']} snapshots...")
        print("-" * 70)

        for i, snapshot in enumerate(beta_snapshots, 1):
            model_version = snapshot.get('model_version', 'unknown')
            created_at = snapshot.get('created_at')

            # Create fingerprint for this snapshot
            fingerprint = (model_version, created_at)

            # Check if already exists in production
            if fingerprint in existing_fingerprints:
                if self.skip_duplicates:
                    print(f"  ⏭️  Skipping snapshot (model: {model_version}, created: {created_at}) - already exists")
                    stats['skipped'] += 1
                    continue
                else:
                    print(f"  ⚠️  Duplicate detected (model: {model_version}) - will create new record with different ID")

            # Migrate the snapshot
            success = self.migrate_snapshot(snapshot)

            if success:
                stats['migrated'] += 1
            else:
                stats['failed'] += 1

            # Progress indicator
            if i % 10 == 0:
                print(f"\n  Progress: {i}/{stats['total']} snapshots processed...")

        return stats

    def print_summary(self, stats: Dict[str, int]):
        """Print migration summary.

        Args:
            stats: Migration statistics dictionary
        """
        print("\n" + "=" * 70)
        print("📊 Migration Summary")
        print("=" * 70)
        print(f"Total snapshots in beta:    {stats['total']}")
        print(f"Skipped (already exist):    {stats['skipped']}")
        print(f"Successfully migrated:      {stats['migrated']}")
        print(f"Failed:                     {stats['failed']}")
        print("=" * 70)

        if self.dry_run:
            print("\n⚠️  This was a DRY RUN. No data was actually migrated.")
            print("Run without --dry-run to perform the actual migration.")
        elif stats['failed'] > 0:
            print("\n⚠️  Some snapshots failed to migrate. Check the logs above for details.")
        elif stats['migrated'] > 0:
            print("\n✅ Migration completed successfully!")
        else:
            print("\n✅ No new data to migrate.")


def verify_table_schema(client: Client, table_name: str) -> bool:
    """Verify that the table exists and has the expected schema.

    Args:
        client: Supabase client
        table_name: Name of table to verify

    Returns:
        True if table exists and is accessible
    """
    try:
        # Try to query the table
        client.table(table_name).select('id').limit(1).execute()
        return True
    except Exception as e:
        print(f"❌ Error accessing table '{table_name}': {e}")
        return False


def main():
    """Main migration script."""
    parser = argparse.ArgumentParser(
        description='Migrate clinical validation benchmark data from beta to production'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate migration without writing data'
    )
    parser.add_argument(
        '--skip-duplicates',
        action='store_true',
        default=True,
        help='Skip records that already exist in production (default: True)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing records in production'
    )

    args = parser.parse_args()

    # Override skip_duplicates if --force is specified
    skip_duplicates = not args.force

    print("🔄 Clinical Validation Data Migration")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE MIGRATION'}")
    print(f"Duplicate handling: {'SKIP' if skip_duplicates else 'OVERWRITE'}")

    try:
        # Initialize migrator
        migrator = BenchmarkDataMigrator(
            dry_run=args.dry_run,
            skip_duplicates=skip_duplicates
        )

        # Verify tables exist
        print("\n🔍 Verifying database tables...")
        if not verify_table_schema(migrator.beta_client, 'clinical_validation_snapshots'):
            print("❌ Source table not accessible. Aborting migration.")
            sys.exit(1)

        if not verify_table_schema(migrator.prod_client, 'clinical_validation_snapshots'):
            print("❌ Destination table not accessible. Aborting migration.")
            print("   Make sure the table exists in production database.")
            sys.exit(1)

        print("✅ Tables verified successfully")

        # Run migration
        stats = migrator.run_migration()

        # Print summary
        migrator.print_summary(stats)

        # Exit with appropriate code
        if stats['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
