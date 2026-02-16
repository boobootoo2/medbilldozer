"""
Verify Clinical Validation Data Migration Status
================================================

Quick script to check the status of data in both beta and production databases.

Usage:
    python scripts/verify_migration_status.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Optional

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


def get_database_stats(client: Client, db_name: str) -> Optional[Dict]:
    """Get statistics for clinical validation snapshots.

    Args:
        client: Supabase client
        db_name: Name of database (for display)

    Returns:
        Dictionary of statistics or None if error
    """
    try:
        # Get total count
        response = client.table('clinical_validation_snapshots') \
            .select('*') \
            .execute()

        data = response.data

        if not data:
            return {
                'name': db_name,
                'total': 0,
                'earliest': None,
                'latest': None,
                'environments': [],
                'models': []
            }

        # Calculate statistics
        created_dates = [record.get('created_at') for record in data if record.get('created_at')]
        environments = list(set(record.get('environment') for record in data if record.get('environment')))
        models = list(set(record.get('model_version') for record in data if record.get('model_version')))

        return {
            'name': db_name,
            'total': len(data),
            'earliest': min(created_dates) if created_dates else None,
            'latest': max(created_dates) if created_dates else None,
            'environments': sorted(environments),
            'models': sorted(models)
        }

    except Exception as e:
        print(f"⚠️  Error accessing {db_name} database: {e}")
        return None


def print_stats(stats: Dict):
    """Print database statistics in a readable format.

    Args:
        stats: Statistics dictionary
    """
    print(f"\n{'=' * 70}")
    print(f"📊 {stats['name']} Database")
    print('=' * 70)
    print(f"Total Records:      {stats['total']}")

    if stats['total'] > 0:
        print(f"Earliest Record:    {stats['earliest'][:19] if stats['earliest'] else 'N/A'}")
        print(f"Latest Record:      {stats['latest'][:19] if stats['latest'] else 'N/A'}")
        print(f"Environments:       {', '.join(stats['environments']) if stats['environments'] else 'None'}")
        print(f"Models:             {len(stats['models'])} unique models")
        if stats['models']:
            for model in stats['models'][:5]:  # Show first 5
                print(f"                    - {model}")
            if len(stats['models']) > 5:
                print(f"                    ... and {len(stats['models']) - 5} more")
    else:
        print("⚠️  No records found")


def compare_databases(beta_stats: Dict, prod_stats: Dict):
    """Compare beta and production database statistics.

    Args:
        beta_stats: Beta database statistics
        prod_stats: Production database statistics
    """
    print(f"\n{'=' * 70}")
    print("🔄 Migration Status")
    print('=' * 70)

    beta_total = beta_stats['total']
    prod_total = prod_stats['total']

    # Migration percentage
    if beta_total > 0:
        percentage = (prod_total / beta_total) * 100
        print(f"Progress:           {prod_total}/{beta_total} records ({percentage:.1f}%)")

        if percentage >= 100:
            print("Status:             ✅ COMPLETE - All records migrated")
        elif percentage >= 75:
            print("Status:             🟡 IN PROGRESS - Most records migrated")
        elif percentage > 0:
            print("Status:             🟡 IN PROGRESS - Partial migration")
        else:
            print("Status:             ⚠️  NOT STARTED - No records in production")

        # Missing records
        missing = beta_total - prod_total
        if missing > 0:
            print(f"Missing:            {missing} records not yet in production")
        elif missing < 0:
            print(f"Extra:              {abs(missing)} more records in production than beta")
    else:
        print("Status:             ⚠️  No records in beta database")

    # Date range comparison
    print("\nDate Ranges:")
    print(f"  Beta:             {beta_stats['earliest'][:10] if beta_stats['earliest'] else 'N/A'} to "
          f"{beta_stats['latest'][:10] if beta_stats['latest'] else 'N/A'}")
    print(f"  Production:       {prod_stats['earliest'][:10] if prod_stats['earliest'] else 'N/A'} to "
          f"{prod_stats['latest'][:10] if prod_stats['latest'] else 'N/A'}")


def main():
    """Main verification script."""
    print("🔍 Clinical Validation Data Migration Status")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Connect to beta database
    print("\n📡 Connecting to databases...")

    beta_url = os.getenv('SUPABASE_CLINICAL_URL') or os.getenv('SUPABASE_BETA_URL')
    beta_key = os.getenv('SUPABASE_CLINICAL_KEY') or os.getenv('SUPABASE_BETA_KEY')

    if not beta_url or not beta_key:
        print("⚠️  Beta database credentials not found")
        print("   Set SUPABASE_CLINICAL_URL/KEY or SUPABASE_BETA_URL/KEY")
        beta_stats = None
    else:
        beta_client = create_client(beta_url, beta_key)
        print(f"✅ Connected to beta: {beta_url}")
        beta_stats = get_database_stats(beta_client, "Beta")

    # Connect to production database
    prod_url = os.getenv('SUPABASE_URL')
    prod_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ANON_KEY')

    if not prod_url or not prod_key:
        print("⚠️  Production database credentials not found")
        print("   Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        prod_stats = None
    else:
        prod_client = create_client(prod_url, prod_key)
        print(f"✅ Connected to production: {prod_url}")
        prod_stats = get_database_stats(prod_client, "Production")

    # Print statistics
    if beta_stats:
        print_stats(beta_stats)
    if prod_stats:
        print_stats(prod_stats)

    # Compare databases
    if beta_stats and prod_stats:
        compare_databases(beta_stats, prod_stats)

    # Recommendations
    print(f"\n{'=' * 70}")
    print("💡 Next Steps")
    print('=' * 70)

    if not beta_stats and not prod_stats:
        print("❌ Cannot access either database. Check your environment variables.")
    elif not prod_stats or prod_stats['total'] == 0:
        print("1. Run migration dry-run: python scripts/migrate_beta_to_prod.py --dry-run")
        print("2. Run actual migration: python scripts/migrate_beta_to_prod.py")
    elif beta_stats and prod_stats and beta_stats['total'] > prod_stats['total']:
        print("⚠️  Migration incomplete. Run migration script to sync remaining records:")
        print("   python scripts/migrate_beta_to_prod.py")
    else:
        print("✅ Migration appears complete!")
        print("1. Verify dashboard: streamlit run pages/production_stability.py")
        print("2. Check Clinical Validation tab for data")
        print("3. Monitor for any issues over next 7 days")

    print('=' * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
