#!/usr/bin/env python3
from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))

# Get snapshots
snapshots = client.table('benchmark_snapshots').select('model_version,snapshot_version,created_at,is_current,f1_score').order('created_at', desc=True).limit(20).execute()

print('📊 Current Snapshots in Database:')
print('=' * 80)
for s in snapshots.data:
    current_mark = '✅ CURRENT' if s['is_current'] else '  '
    print(f"{current_mark} {s['model_version']:20s} v{s['snapshot_version']} - F1:{s.get('f1_score', 0):.4f} - {s['created_at'][:19]}")

print(f'\n📈 Total snapshots: {len(snapshots.data)}')
print(f'📋 Unique models: {len(set(s["model_version"] for s in snapshots.data))}')
