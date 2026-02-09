#!/usr/bin/env python3
"""Debug script to check domain_knowledge_detection_rate in Supabase."""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not url or not key:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    sys.exit(1)

client = create_client(url, key)

# Query recent medgemma-ensemble transactions
print("=" * 70)
print("Checking domain_knowledge_detection_rate in Supabase...")
print("=" * 70)

response = client.table('benchmark_transactions')\
    .select('id, model_version, created_at, environment, metrics')\
    .eq('model_version', 'medgemma-ensemble-v1.0')\
    .order('created_at', desc=True)\
    .limit(5)\
    .execute()

if not response.data:
    print("\n❌ No data found for medgemma-ensemble-v1.0")
    sys.exit(0)

print(f"\n✅ Found {len(response.data)} recent transactions\n")

for i, transaction in enumerate(response.data, 1):
    print(f"\n{'='*70}")
    print(f"Transaction {i}: {transaction['id']}")
    print(f"Created: {transaction['created_at']}")
    print(f"Environment: {transaction['environment']}")
    print(f"Model: {transaction['model_version']}")
    
    metrics = transaction['metrics']
    
    # Check for domain_knowledge_detection_rate
    if 'domain_knowledge_detection_rate' in metrics:
        rate = metrics['domain_knowledge_detection_rate']
        print(f"\n✅ domain_knowledge_detection_rate: {rate}")
    else:
        print(f"\n❌ domain_knowledge_detection_rate: NOT FOUND")
    
    # Check for domain_recall as fallback
    if 'domain_recall' in metrics:
        rate = metrics['domain_recall']
        print(f"✅ domain_recall: {rate}")
    
    # Show what IS in metrics
    print(f"\n📋 Available metrics keys:")
    for key in sorted(metrics.keys()):
        if 'domain' in key.lower() or 'detection' in key.lower():
            print(f"  ✓ {key}: {metrics[key]}")

print("\n" + "=" * 70)

# Also check snapshots
print("\n\nChecking benchmark_snapshots...")
print("=" * 70)

response = client.table('benchmark_snapshots')\
    .select('id, model_version, created_at, is_current, metrics')\
    .eq('model_version', 'medgemma-ensemble-v1.0')\
    .eq('is_current', True)\
    .limit(3)\
    .execute()

if response.data:
    print(f"\n✅ Found {len(response.data)} current snapshots\n")
    for snapshot in response.data:
        print(f"\nSnapshot: {snapshot['id']}")
        print(f"Created: {snapshot['created_at']}")
        metrics = snapshot['metrics']
        
        if 'domain_knowledge_detection_rate' in metrics:
            print(f"✅ domain_knowledge_detection_rate: {metrics['domain_knowledge_detection_rate']}")
        else:
            print(f"❌ domain_knowledge_detection_rate: NOT FOUND")
            
        # Show domain-related metrics
        print(f"\n📋 Domain-related metrics:")
        for key in sorted(metrics.keys()):
            if 'domain' in key.lower() or 'detection' in key.lower():
                print(f"  ✓ {key}: {metrics[key]}")
else:
    print("\n❌ No current snapshots found")

print("\n" + "=" * 70)
