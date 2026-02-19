#!/usr/bin/env python3
"""Apply production API schema to Supabase database."""
import os
from supabase import create_client

# Read schema file
with open('sql/schema_production_api.sql', 'r') as f:
    schema_sql = f.read()

# Connect to Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_key:
    print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")
    print("Run: cd backend && source .env")
    exit(1)

print(f"🔗 Connecting to Supabase: {supabase_url}")
client = create_client(supabase_url, supabase_key)

# Note: Supabase Python client doesn't support raw SQL execution
# You need to apply this schema through the Supabase Dashboard SQL Editor instead

print("\n" + "="*80)
print("⚠️  The Supabase Python client doesn't support raw SQL execution.")
print("="*80)
print("\nTo apply the schema, follow these steps:")
print("\n1. Go to: https://supabase.com/dashboard/project/zrhlpitzonhftigmdvgz/sql/new")
print("\n2. Copy and paste the contents of sql/schema_production_api.sql")
print("\n3. Click 'Run' to apply the schema")
print("\nOR use the Supabase CLI:")
print("\n  supabase db push")
print("\n" + "="*80)
