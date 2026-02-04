#!/usr/bin/env python3
"""
Populate test snapshots for demonstration of snapshot versioning.

This script creates multiple snapshots with different versions for various models
to demonstrate the snapshot history and checkout functionality.
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
import random

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """Get authenticated Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env")
    
    return create_client(url, key)

def generate_test_snapshot(
    model_version: str,
    snapshot_version: int,
    base_f1: float,
    days_ago: int,
    is_current: bool = False,
    existing_transaction_id: str = None
):
    """Generate a test snapshot with realistic variations."""
    # Add some random variation
    variation = random.uniform(-0.05, 0.05)
    f1_score = max(0.0, min(1.0, base_f1 + variation))
    
    # Calculate precision and recall from F1 (approximate)
    precision_offset = random.uniform(-0.03, 0.03)
    precision_score = max(0.0, min(1.0, f1_score + precision_offset))
    
    # Calculate recall to be consistent with F1
    if precision_score > 0 and f1_score > 0:
        # F1 = 2 * (P * R) / (P + R), solve for R
        recall_score = (f1_score * precision_score) / (2 * precision_score - f1_score)
        recall_score = max(0.0, min(1.0, recall_score))
    else:
        recall_score = f1_score
    
    accuracy_score = round(f1_score + random.uniform(-0.02, 0.02), 4)
    latency = round(random.uniform(500, 2000))
    timestamp = datetime.now() - timedelta(days=days_ago)
    commit_sha = f"abc{random.randint(1000, 9999)}def"
    
    # Build metrics JSONB
    metrics = {
        "precision": round(precision_score, 4),
        "recall": round(recall_score, 4),
        "f1": round(f1_score, 4),
        "accuracy": accuracy_score,
        "latency_ms": latency,
        "total_samples": 100,
        "error_count": 0,
        "success_count": 100
    }
    
    snapshot = {
        "model_version": model_version,
        "dataset_version": "benchmark-set-v1",
        "prompt_version": "v1",
        "environment": "github-actions",
        "snapshot_version": snapshot_version,
        "commit_sha": commit_sha,
        "metrics": json.dumps(metrics),
        "f1_score": round(f1_score, 4),
        "precision_score": round(precision_score, 4),
        "recall_score": round(recall_score, 4),
        "latency_ms": latency,
        "cost_per_analysis": round(random.uniform(0.001, 0.01), 6),
        "is_current": is_current,
        "is_baseline": snapshot_version == 1,
        "created_at": timestamp.isoformat()
    }
    
    # Add transaction_id if provided
    if existing_transaction_id:
        snapshot["transaction_id"] = existing_transaction_id
    
    return snapshot, metrics, commit_sha, timestamp

def populate_snapshots():
    """Populate database with test snapshots."""
    client = get_supabase_client()
    
    test_data = [
        # OpenAI GPT-4 - 4 versions (showing improvement)
        ("openai-gpt4-v1.0", 1, 0.8500, 30, False),
        ("openai-gpt4-v1.0", 2, 0.8650, 20, False),
        ("openai-gpt4-v1.0", 3, 0.8800, 10, False),
        ("openai-gpt4-v1.0", 4, 0.8950, 1, True),
        
        # Google Gemini - 3 versions (showing regression then recovery)
        ("gemini-pro-v1.5", 1, 0.8700, 25, False),
        ("gemini-pro-v1.5", 2, 0.8500, 15, False),  # Regression
        ("gemini-pro-v1.5", 3, 0.8900, 1, True),   # Recovery
        
        # Claude - 2 versions
        ("claude-3-opus", 1, 0.8600, 20, False),
        ("claude-3-opus", 2, 0.8850, 1, True),
        
        # MedGemma (existing) - add more versions
        ("medgemma-v1.2", 2, 0.9000, 5, False),
        ("medgemma-v1.2", 3, 0.9150, 1, True),
        
        # Baseline model - 1 version
        ("baseline-v1.0", 1, 0.7500, 35, True),
    ]
    
    print("🚀 Populating test snapshots...\n")
    
    for model_version, snapshot_version, base_f1, days_ago, is_current in test_data:
        try:
            # Generate snapshot data
            snapshot, metrics, commit_sha, timestamp = generate_test_snapshot(
                model_version, snapshot_version, base_f1, days_ago, is_current
            )
            
            # First, create a transaction record
            transaction = {
                "model_version": model_version,
                "dataset_version": "benchmark-set-v1",
                "prompt_version": "v1",
                "environment": "github-actions",
                "commit_sha": commit_sha,
                "branch_name": "main" if is_current else "develop",
                "metrics": json.dumps(metrics),
                "error_count": 0,
                "success_count": 100,
                "created_at": timestamp.isoformat()
            }
            
            # Insert transaction
            trans_result = client.table("benchmark_transactions").insert(transaction).execute()
            transaction_id = trans_result.data[0]['id']
            
            # Add transaction_id to snapshot
            snapshot["transaction_id"] = transaction_id
            
            # Insert snapshot
            snap_result = client.table("benchmark_snapshots").insert(snapshot).execute()
            
            print(f"✅ Created {model_version} v{snapshot_version} - F1: {snapshot['f1_score']:.4f} "
                  f"({'CURRENT' if is_current else 'historical'})")
            
        except Exception as e:
            print(f"❌ Error creating {model_version} v{snapshot_version}: {str(e)}")
    
    print("\n✅ Test data population complete!")
    print("\n📊 Summary:")
    
    # Query and display summary
    snapshots = client.table("benchmark_snapshots").select("*").execute()
    
    models = set(s['model_version'] for s in snapshots.data)
    total_snapshots = len(snapshots.data)
    current_snapshots = sum(1 for s in snapshots.data if s['is_current'])
    
    print(f"   Total Models: {len(models)}")
    print(f"   Total Snapshots: {total_snapshots}")
    print(f"   Current Snapshots: {current_snapshots}")
    print("\n   Models:")
    for model in sorted(models):
        model_snaps = [s for s in snapshots.data if s['model_version'] == model]
        versions = len(model_snaps)
        current = next((s for s in model_snaps if s['is_current']), None)
        current_version = f"v{current['snapshot_version']}" if current else "N/A"
        print(f"   - {model}: {versions} versions (current: {current_version})")

if __name__ == "__main__":
    try:
        populate_snapshots()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        exit(1)
