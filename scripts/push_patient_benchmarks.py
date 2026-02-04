#!/usr/bin/env python3
"""
Push Patient Benchmark Results to Supabase

Uploads cross-document patient benchmark results to Supabase for historical tracking
and dashboard visualization. This tracks medical domain knowledge detection over time.

Usage:
    python scripts/push_patient_benchmarks.py --input benchmarks/results/patient_benchmark_medgemma.json
    python scripts/push_patient_benchmarks.py --model medgemma --commit-sha abc123
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent


def get_supabase_client() -> Client:
    """Get authenticated Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        raise ValueError(
            "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables.\n"
            "Please set them in your .env file."
        )
    
    return create_client(url, key)


def load_patient_benchmark_results(file_path: Path) -> dict:
    """Load patient benchmark results from JSON file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Benchmark results file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def push_patient_benchmark(
    client: Client,
    results: dict,
    model_name: str,
    environment: str = "local",
    commit_sha: Optional[str] = None,
    branch_name: Optional[str] = None,
    triggered_by: Optional[str] = None
) -> str:
    """
    Push patient benchmark results to Supabase.
    
    Returns:
        Transaction ID from the database
    """
    
    # Extract metrics
    model_version = results.get('model_name', model_name)
    total_patients = results.get('total_patients', 0)
    successful = results.get('successful_analyses', 0)
    avg_precision = results.get('avg_precision', 0.0)
    avg_recall = results.get('avg_recall', 0.0)
    avg_f1 = results.get('avg_f1_score', 0.0)
    domain_knowledge_rate = results.get('domain_knowledge_detection_rate', 0.0)
    avg_latency_ms = results.get('avg_latency_ms', 0.0)
    
    # Build metrics JSONB
    metrics = {
        "precision": round(avg_precision, 4),
        "recall": round(avg_recall, 4),
        "f1": round(avg_f1, 4),
        "domain_knowledge_detection_rate": round(domain_knowledge_rate, 4),
        "latency_ms": round(avg_latency_ms, 2),
        "total_patients": total_patients,
        "successful_analyses": successful,
        "success_rate": round(successful / total_patients, 4) if total_patients > 0 else 0.0
    }
    
    # Add individual patient results for detailed analysis
    if 'individual_results' in results:
        patient_results = []
        for patient in results['individual_results']:
            patient_results.append({
                'patient_id': patient.get('patient_id'),
                'patient_name': patient.get('patient_name'),
                'age': patient.get('age'),
                'sex': patient.get('sex'),
                'true_positives': patient.get('true_positives', 0),
                'false_positives': patient.get('false_positives', 0),
                'false_negatives': patient.get('false_negatives', 0),
                'domain_knowledge_score': patient.get('domain_knowledge_score', 0.0),
                'latency_ms': patient.get('analysis_latency_ms', 0.0)
            })
        metrics['patient_results'] = patient_results
    
    # Insert transaction record
    transaction_data = {
        "model_version": model_version,
        "benchmark_type": "patient_cross_document",
        "dataset_version": "patient-profiles-v1",
        "prompt_version": "cross-document-v1",
        "environment": environment,
        "commit_sha": commit_sha,
        "branch_name": branch_name,
        "triggered_by": triggered_by,
        "metrics": json.dumps(metrics),
        "error_count": total_patients - successful,
        "success_count": successful,
        "created_at": datetime.utcnow().isoformat()
    }
    
    print(f"📤 Pushing patient benchmark to Supabase...")
    print(f"   Model: {model_version}")
    print(f"   Patients: {successful}/{total_patients}")
    print(f"   Domain Knowledge Detection: {domain_knowledge_rate:.1f}%")
    print(f"   F1 Score: {avg_f1:.3f}")
    
    try:
        # Insert transaction
        trans_response = client.table('benchmark_transactions').insert(transaction_data).execute()
        transaction_id = trans_response.data[0]['id']
        
        print(f"✅ Transaction created: {transaction_id}")
        
        # Upsert snapshot using stored procedure
        snapshot_data = {
            "p_model_version": model_version,
            "p_dataset_version": "patient-profiles-v1",
            "p_prompt_version": "cross-document-v1",
            "p_environment": environment,
            "p_transaction_id": transaction_id,
            "p_commit_sha": commit_sha,
            "p_metrics": json.dumps(metrics),
            "p_f1_score": avg_f1,
            "p_precision_score": avg_precision,
            "p_recall_score": avg_recall,
            "p_latency_ms": avg_latency_ms,
            "p_cost_per_analysis": 0.0  # Can be calculated if needed
        }
        
        client.rpc('upsert_benchmark_result', snapshot_data).execute()
        print(f"✅ Snapshot upserted for {model_version}")
        
        return transaction_id
        
    except Exception as e:
        print(f"❌ Error pushing to Supabase: {e}")
        raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Push patient benchmark results to Supabase"
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Path to patient benchmark JSON file'
    )
    parser.add_argument(
        '--model',
        type=str,
        help='Model name (if not using --input)'
    )
    parser.add_argument(
        '--environment',
        type=str,
        default='local',
        choices=['local', 'github-actions', 'staging', 'production'],
        help='Execution environment'
    )
    parser.add_argument(
        '--commit-sha',
        type=str,
        help='Git commit SHA'
    )
    parser.add_argument(
        '--branch-name',
        type=str,
        help='Git branch name'
    )
    parser.add_argument(
        '--triggered-by',
        type=str,
        help='Who/what triggered this benchmark run'
    )
    
    args = parser.parse_args()
    
    # Determine input file
    if args.input:
        input_file = Path(args.input)
    elif args.model:
        input_file = PROJECT_ROOT / 'benchmarks' / 'results' / f'patient_benchmark_{args.model}.json'
    else:
        print("❌ Error: Must provide either --input or --model")
        return 1
    
    if not input_file.exists():
        print(f"❌ Error: File not found: {input_file}")
        return 1
    
    # Load results
    print(f"📂 Loading patient benchmark results from: {input_file}")
    results = load_patient_benchmark_results(input_file)
    
    # Get model name
    model_name = results.get('model_name', args.model)
    
    # Get Supabase client
    try:
        client = get_supabase_client()
    except ValueError as e:
        print(f"❌ {e}")
        return 1
    
    # Push to Supabase
    try:
        transaction_id = push_patient_benchmark(
            client=client,
            results=results,
            model_name=model_name,
            environment=args.environment,
            commit_sha=args.commit_sha,
            branch_name=args.branch_name,
            triggered_by=args.triggered_by
        )
        
        print(f"\n🎉 Successfully pushed patient benchmark results!")
        print(f"   Transaction ID: {transaction_id}")
        print(f"   View in dashboard: http://localhost:8501")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Failed to push results: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
