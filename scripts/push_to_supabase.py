#!/usr/bin/env python3
"""
Benchmark Persistence Script for MLOps Pipeline
================================================

This script pushes benchmark results to Supabase in a transactional manner.
Designed for CI/CD integration with GitHub Actions.

Features:
- Atomic transaction + snapshot upsert
- Comprehensive error handling
- Structured logging
- Retry logic for network failures
- Validation of benchmark data

Author: Senior MLOps Engineer
Date: 2026-02-03
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from supabase import create_client, Client
    from dotenv import load_dotenv
except ImportError:
    print("Error: Required packages not installed. Run: pip install supabase python-dotenv")
    sys.exit(1)

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# Configuration
# ============================================================================

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# ============================================================================
# Data Models
# ============================================================================

class BenchmarkResult:
    """Validated benchmark result with metadata."""
    
    def __init__(
        self,
        model_version: str,
        dataset_version: str,
        prompt_version: str,
        metrics: Dict[str, Any],
        model_provider: Optional[str] = None,
        dataset_size: Optional[int] = None,
        domain_breakdown: Optional[Dict[str, Any]] = None,
        category_metrics: Optional[Dict[str, Any]] = None,
    ):
        self.model_version = model_version
        self.dataset_version = dataset_version
        self.prompt_version = prompt_version
        self.metrics = metrics
        self.model_provider = model_provider
        self.dataset_size = dataset_size
        self.domain_breakdown = domain_breakdown or {}
        self.category_metrics = category_metrics or {}
        
        self._validate()
    
    def _validate(self):
        """Validate required fields."""
        required_fields = ['model_version', 'dataset_version', 'prompt_version', 'metrics']
        for field in required_fields:
            if not getattr(self, field):
                raise ValueError(f"Missing required field: {field}")
        
        # Validate metrics structure
        required_metrics = ['precision', 'recall', 'f1', 'latency_ms', 'analysis_cost']
        for metric in required_metrics:
            if metric not in self.metrics:
                logger.warning(f"Missing recommended metric: {metric}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API call."""
        return {
            'model_version': self.model_version,
            'dataset_version': self.dataset_version,
            'prompt_version': self.prompt_version,
            'metrics': self.metrics,
            'model_provider': self.model_provider,
            'dataset_size': self.dataset_size,
            'domain_breakdown': self.domain_breakdown,
            'category_metrics': self.category_metrics,
        }

# ============================================================================
# Supabase Client
# ============================================================================

class BenchmarkPersistence:
    """Handles persistence of benchmark results to Supabase."""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """
        Initialize Supabase client.
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase service role key
        """
        self.client: Client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")
    
    def push_benchmark(
        self,
        result: BenchmarkResult,
        commit_sha: str,
        environment: str,
        branch_name: Optional[str] = None,
        run_id: Optional[str] = None,
        triggered_by: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        tags: Optional[list] = None,
        notes: Optional[str] = None,
    ) -> str:
        """
        Push benchmark result to Supabase using stored procedure.
        
        This function atomically:
        1. Inserts a transaction record (append-only log)
        2. Upserts a snapshot record (current state)
        
        Args:
            result: Validated benchmark result
            commit_sha: Git commit SHA
            environment: Runtime environment (github-actions, local, etc.)
            branch_name: Git branch name
            run_id: CI/CD run identifier
            triggered_by: User or automation trigger
            duration_seconds: Benchmark execution time
            tags: Optional tags for filtering/experimentation
            notes: Optional notes
        
        Returns:
            Transaction UUID
        
        Raises:
            Exception: If persistence fails after retries
        """
        logger.info(f"Pushing benchmark: {result.model_version} @ {commit_sha[:8]}")
        
        # Prepare RPC parameters
        # Embed domain_breakdown and category_metrics into metrics JSONB
        # for backward compatibility with current database schema
        metrics_with_domain = result.metrics.copy()
        if result.domain_breakdown:
            metrics_with_domain['domain_breakdown'] = result.domain_breakdown
        if result.category_metrics:
            metrics_with_domain['category_metrics'] = result.category_metrics
        
        params = {
            'p_commit_sha': commit_sha,
            'p_branch_name': branch_name,
            'p_model_version': result.model_version,
            'p_model_provider': result.model_provider,
            'p_dataset_version': result.dataset_version,
            'p_dataset_size': result.dataset_size,
            'p_prompt_version': result.prompt_version,
            'p_environment': environment,
            'p_run_id': run_id,
            'p_triggered_by': triggered_by,
            'p_metrics': metrics_with_domain,
            'p_duration_seconds': duration_seconds,
            'p_tags': tags,
            'p_notes': notes,
        }
        
        # Execute with retry logic
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.client.rpc('upsert_benchmark_result', params).execute()
                
                if response.data:
                    transaction_id = response.data
                    logger.info(f"✓ Benchmark persisted successfully: {transaction_id}")
                    return transaction_id
                else:
                    raise Exception("No transaction ID returned from database")
                    
            except Exception as e:
                logger.error(f"Attempt {attempt}/{MAX_RETRIES} failed: {str(e)}")
                
                if attempt < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error("Max retries exceeded. Persistence failed.")
                    raise
    
    def verify_persistence(self, transaction_id: str) -> bool:
        """
        Verify that the transaction was persisted correctly.
        
        Args:
            transaction_id: UUID of the transaction
        
        Returns:
            True if verification succeeds
        """
        try:
            response = self.client.table('benchmark_transactions') \
                .select('id') \
                .eq('id', transaction_id) \
                .execute()
            
            if response.data:
                logger.info(f"✓ Verification passed: Transaction {transaction_id} exists")
                return True
            else:
                logger.error(f"✗ Verification failed: Transaction {transaction_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return False

# ============================================================================
# File I/O
# ============================================================================

def load_benchmark_results(filepath: str) -> Dict[str, Any]:
    """
    Load benchmark results from JSON file.
    
    Args:
        filepath: Path to benchmark_results.json
    
    Returns:
        Parsed JSON data
    
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"Benchmark results not found: {filepath}")
    
    logger.info(f"Loading benchmark results from: {filepath}")
    
    with open(path, 'r') as f:
        data = json.load(f)
    
    logger.info(f"Loaded benchmark data: {json.dumps(data, indent=2)}")
    return data

# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Push benchmark results to Supabase',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # CI/CD usage (GitHub Actions)
  python push_to_supabase.py \\
    --input benchmark_results.json \\
    --environment github-actions \\
    --commit-sha $GITHUB_SHA \\
    --branch-name $GITHUB_REF \\
    --run-id $GITHUB_RUN_ID \\
    --triggered-by $GITHUB_ACTOR
  
  # Local development
  python push_to_supabase.py \\
    --input benchmark_results.json \\
    --environment local \\
    --commit-sha $(git rev-parse HEAD) \\
    --triggered-by $(whoami)
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to benchmark_results.json'
    )
    parser.add_argument(
        '--environment',
        type=str,
        required=True,
        choices=['github-actions', 'local', 'staging', 'production'],
        help='Runtime environment'
    )
    parser.add_argument(
        '--commit-sha',
        type=str,
        required=True,
        help='Git commit SHA'
    )
    
    # Optional arguments
    parser.add_argument(
        '--branch-name',
        type=str,
        help='Git branch name'
    )
    parser.add_argument(
        '--run-id',
        type=str,
        help='CI/CD run identifier'
    )
    parser.add_argument(
        '--triggered-by',
        type=str,
        help='User or automation trigger'
    )
    parser.add_argument(
        '--duration',
        type=float,
        help='Benchmark execution time in seconds'
    )
    parser.add_argument(
        '--tags',
        type=str,
        nargs='+',
        help='Tags for filtering/experimentation'
    )
    parser.add_argument(
        '--notes',
        type=str,
        help='Optional notes about this run'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify persistence after push'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("Missing required environment variables:")
        logger.error("  - SUPABASE_URL")
        logger.error("  - SUPABASE_SERVICE_ROLE_KEY")
        sys.exit(1)
    
    try:
        # Load benchmark results
        data = load_benchmark_results(args.input)
        
        # Parse into validated model
        result = BenchmarkResult(
            model_version=data.get('model_version'),
            dataset_version=data.get('dataset_version'),
            prompt_version=data.get('prompt_version'),
            metrics=data.get('metrics'),
            model_provider=data.get('model_provider'),
            dataset_size=data.get('dataset_size'),
            domain_breakdown=data.get('domain_breakdown'),
            category_metrics=data.get('category_metrics'),
        )
        
        # Initialize persistence layer
        persistence = BenchmarkPersistence(supabase_url, supabase_key)
        
        # Push to Supabase
        transaction_id = persistence.push_benchmark(
            result=result,
            commit_sha=args.commit_sha,
            environment=args.environment,
            branch_name=args.branch_name,
            run_id=args.run_id,
            triggered_by=args.triggered_by,
            duration_seconds=args.duration,
            tags=args.tags,
            notes=args.notes,
        )
        
        # Verify if requested
        if args.verify:
            if not persistence.verify_persistence(transaction_id):
                logger.error("Verification failed!")
                sys.exit(1)
        
        # Success output
        logger.info("=" * 60)
        logger.info("SUCCESS: Benchmark results persisted to Supabase")
        logger.info(f"Transaction ID: {transaction_id}")
        logger.info(f"Model: {result.model_version}")
        logger.info(f"Environment: {args.environment}")
        logger.info(f"Commit: {args.commit_sha[:8]}")
        logger.info("=" * 60)
        
        # Output JSON for GitHub Actions step summary
        output = {
            'success': True,
            'transaction_id': transaction_id,
            'timestamp': datetime.utcnow().isoformat(),
            'model_version': result.model_version,
            'environment': args.environment,
            'commit_sha': args.commit_sha,
        }
        
        # Write output for GitHub Actions (using modern GITHUB_OUTPUT method)
        github_output = os.environ.get('GITHUB_OUTPUT')
        if github_output:
            with open(github_output, 'a') as f:
                f.write(f"result={json.dumps(output)}\n")
        
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
