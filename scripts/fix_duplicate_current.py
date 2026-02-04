#!/usr/bin/env python3
"""Fix duplicate current versions in database."""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

# Fix medgemma-v1.2: Only v3 should be current
result = client.table('benchmark_snapshots')\
    .update({'is_current': False})\
    .eq('model_version', 'medgemma-v1.2')\
    .eq('snapshot_version', 1)\
    .execute()

print(f"✅ Updated medgemma-v1.2 v1 to is_current=False")
print(f"   Affected rows: {len(result.data)}")
