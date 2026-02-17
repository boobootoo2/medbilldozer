#!/usr/bin/env python3
"""
Test Supabase connection using beta credentials from environment
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from supabase import create_client

def test_connection():
    """Test Supabase connection"""
    print("🔍 Testing Supabase Connection")
    print("=" * 50)

    # Show which credentials are being used
    print(f"\n📊 Configuration:")
    print(f"  URL: {settings.supabase_url}")
    print(f"  Key: {settings.supabase_service_role_key[:20]}...")

    # Check if beta credentials are loaded
    beta_url = os.getenv("SUPABASE_BETA_URL")
    beta_key = os.getenv("SUPABASE_BETA_KEY")

    if beta_url:
        print(f"\n✅ Using BETA Supabase credentials from environment")
        print(f"  SUPABASE_BETA_URL: {beta_url}")
    else:
        print(f"\n⚠️  No SUPABASE_BETA_URL found in environment")
        print(f"  Using SUPABASE_URL: {settings.supabase_url}")

    print("\n🔌 Attempting connection...")

    try:
        # Create client
        client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )

        # Test query - list tables
        response = client.table("user_profiles").select("count", count="exact").limit(0).execute()

        print(f"✅ Connection successful!")
        print(f"\n📋 Database Info:")
        print(f"  user_profiles table exists: Yes")

        # Try to count records in each table
        tables = ["user_profiles", "documents", "analyses", "issues"]
        for table in tables:
            try:
                result = client.table(table).select("count", count="exact").limit(0).execute()
                count = result.count if hasattr(result, 'count') else 0
                print(f"  {table}: {count} records")
            except Exception as e:
                print(f"  {table}: Table may not exist yet")

        return True

    except Exception as e:
        print(f"❌ Connection failed!")
        print(f"Error: {str(e)}")
        print(f"\n💡 Troubleshooting:")
        print(f"  1. Check that SUPABASE_BETA_URL and SUPABASE_BETA_KEY are set in .zprofile")
        print(f"  2. Run: source ~/.zprofile")
        print(f"  3. Verify credentials are loaded: echo $SUPABASE_BETA_URL")
        print(f"  4. Make sure schema is created in Supabase")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
