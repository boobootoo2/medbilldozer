"""
Benchmark Data Access Layer for Streamlit Dashboard
====================================================

Clean separation of data access logic from presentation.
Provides typed, cached queries for the dashboard.

Features:
- Cached queries for performance
- Typed return values
- Time-series aggregation
- Filtering and comparison utilities

Author: Senior MLOps Engineer
Date: 2026-02-03
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd

try:
    from supabase import create_client, Client
except ImportError as e:
    print(f"Error importing supabase: {e}")
    print("Please install: pip install supabase>=2.3.0")
    # Define dummy types so module still loads

    def create_client(*args, **kwargs):
        raise ImportError("supabase package not installed. Run: pip install supabase>=2.3.0")

    Client = Any

# ============================================================================
# Data Access Layer
# ============================================================================

class BenchmarkDataAccess:
    """Encapsulates all Supabase queries for the dashboard."""
    
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """
        Initialize data access layer.
        
        Args:
            supabase_url: Supabase project URL (defaults to env var)
            supabase_key: Supabase anon/service key (defaults to env var)
        """
        url = supabase_url or os.getenv('SUPABASE_URL')
        key = supabase_key or os.getenv('SUPABASE_ANON_KEY')
        
        if not url or not key:
            raise ValueError("Supabase credentials not provided")
        
        self.client: Client = create_client(url, key)
    
    # ========================================================================
    # Snapshot Queries
    # ========================================================================
    
    def get_latest_snapshots(
        self,
        environment: Optional[str] = None,
        active_only: bool = True
    ) -> pd.DataFrame:
        """
        Fetch latest benchmark snapshots (current versions only).
        
        Args:
            environment: Filter by environment (None = all)
            active_only: Only return active configurations
        
        Returns:
            DataFrame with latest snapshots
        """
        query = self.client.table('benchmark_snapshots').select('*')
        
        # Only get current versions
        query = query.eq('is_current', True)
        
        if environment:
            query = query.eq('environment', environment)
        
        if active_only:
            query = query.eq('is_active', True)
        
        query = query.order('f1_score', desc=True)
        
        response = query.execute()
        
        if not response.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        
        # Parse timestamps
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
        
        return df
    
    def get_snapshot_history(
        self,
        model_version: str,
        dataset_version: str,
        prompt_version: str,
        environment: str,
        limit: int = 10
    ) -> pd.DataFrame:
        """
        Get version history for a specific configuration.
        
        Args:
            model_version: Model version
            dataset_version: Dataset version
            prompt_version: Prompt version
            environment: Environment
            limit: Maximum number of versions to return
        
        Returns:
            DataFrame with snapshot history, ordered by version DESC
        """
        response = self.client.rpc('get_snapshot_history', {
            'p_model_version': model_version,
            'p_dataset_version': dataset_version,
            'p_prompt_version': prompt_version,
            'p_environment': environment,
            'p_limit': limit
        }).execute()
        
        if not response.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
        
        return df
    
    def checkout_snapshot(
        self,
        model_version: str,
        dataset_version: str,
        prompt_version: str,
        environment: str,
        snapshot_version: int
    ) -> bool:
        """
        Checkout (revert to) a specific snapshot version.
        
        This makes the specified version the "current" version,
        useful for rolling back to a previous good state.
        
        Args:
            model_version: Model version
            dataset_version: Dataset version
            prompt_version: Prompt version
            environment: Environment
            snapshot_version: Version number to checkout
        
        Returns:
            True if successful
        
        Raises:
            Exception if snapshot version doesn't exist
        """
        response = self.client.rpc('checkout_snapshot', {
            'p_model_version': model_version,
            'p_dataset_version': dataset_version,
            'p_prompt_version': prompt_version,
            'p_environment': environment,
            'p_snapshot_version': snapshot_version
        }).execute()
        
        return response.data if response.data is not None else True
    
    def compare_snapshot_versions(
        self,
        model_version: str,
        dataset_version: str,
        prompt_version: str,
        environment: str,
        version_a: int,
        version_b: int
    ) -> pd.DataFrame:
        """
        Compare two snapshot versions side-by-side.
        
        Args:
            model_version: Model version
            dataset_version: Dataset version
            prompt_version: Prompt version
            environment: Environment
            version_a: First version to compare
            version_b: Second version to compare
        
        Returns:
            DataFrame with comparison metrics
        """
        response = self.client.rpc('compare_snapshots', {
            'p_model_version': model_version,
            'p_dataset_version': dataset_version,
            'p_prompt_version': prompt_version,
            'p_environment': environment,
            'p_version_a': version_a,
            'p_version_b': version_b
        }).execute()
        
        if not response.data:
            return pd.DataFrame()
        
        return pd.DataFrame(response.data)
    
    def get_baseline_comparisons(self) -> pd.DataFrame:
        """
        Compare current snapshots to their baselines.
        
        Returns:
            DataFrame with baseline comparisons including deltas
        """
        # Fetch all snapshots
        response = self.client.table('benchmark_snapshots') \
            .select('model_version, environment, f1_score, is_baseline, last_updated_at') \
            .execute()
        
        if not response.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        
        # Separate baselines and current
        baselines = df[df['is_baseline']].copy()
        current = df[~df['is_baseline']].copy()
        
        # Merge to compare
        comparison = current.merge(
            baselines[['model_version', 'environment', 'f1_score']],
            on=['model_version', 'environment'],
            suffixes=('_current', '_baseline')
        )
        
        # Calculate delta
        comparison['f1_delta'] = comparison['f1_score_current'] - comparison['f1_score_baseline']
        comparison['f1_delta_pct'] = (comparison['f1_delta'] / comparison['f1_score_baseline']) * 100
        
        return comparison
    
    def get_top_performers(
        self,
        metric: str = 'f1_score',
        limit: int = 10,
        environment: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get top performing model configurations.
        
        Args:
            metric: Metric to rank by
            limit: Number of top performers to return
            environment: Filter by environment
        
        Returns:
            DataFrame with top performers
        """
        query = self.client.table('benchmark_snapshots') \
            .select('*') \
            .eq('is_active', True)
        
        if environment:
            query = query.eq('environment', environment)
        
        query = query.order(metric, desc=True).limit(limit)
        
        response = query.execute()
        
        if not response.data:
            return pd.DataFrame()
        
        return pd.DataFrame(response.data)
    
    # ========================================================================
    # Transaction Queries (Historical Analysis)
    # ========================================================================
    
    def get_transactions(
        self,
        model_version: Optional[str] = None,
        environment: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetch transaction history with optional filters.
        
        Args:
            model_version: Filter by model version
            environment: Filter by environment
            start_date: Filter transactions after this date
            end_date: Filter transactions before this date
            limit: Maximum number of transactions to return
        
        Returns:
            DataFrame with transaction history
        """
        query = self.client.table('benchmark_transactions').select('*')
        
        if model_version:
            query = query.eq('model_version', model_version)
        
        if environment:
            query = query.eq('environment', environment)
        
        if start_date:
            query = query.gte('created_at', start_date.isoformat())
        
        if end_date:
            query = query.lte('created_at', end_date.isoformat())
        
        query = query.order('created_at', desc=True)
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        
        if not response.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        
        # Parse timestamps
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Expand metrics JSONB into columns
        if 'metrics' in df.columns:
            metrics_df = pd.json_normalize(df['metrics'])
            df = pd.concat([df.drop('metrics', axis=1), metrics_df], axis=1)
        
        return df
    
    def get_time_series(
        self,
        model_version: str,
        metric: str = 'f1',
        granularity: str = 'day',
        days_back: int = 30,
        environment: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get time-series data for a specific model and metric.
        
        Args:
            model_version: Model version to analyze
            metric: Metric name (must be in metrics JSONB)
            granularity: Time bucket ('hour', 'day', 'week')
            days_back: How many days of history to fetch
            environment: Filter by environment
        
        Returns:
            DataFrame with time-bucketed aggregations
        """
        start_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Fetch raw transactions
        df = self.get_transactions(
            model_version=model_version,
            environment=environment,
            start_date=start_date
        )
        
        if df.empty:
            return pd.DataFrame()
        
        # Set index for resampling
        df = df.set_index('created_at')
        
        # Resample and aggregate
        if granularity == 'hour':
            freq = 'H'
        elif granularity == 'day':
            freq = 'D'
        elif granularity == 'week':
            freq = 'W'
        else:
            raise ValueError(f"Unsupported granularity: {granularity}")
        
        # Aggregate the metric
        if metric in df.columns:
            resampled = df[metric].resample(freq).agg(['mean', 'std', 'count'])
            resampled = resampled.reset_index()
            return resampled
        else:
            return pd.DataFrame()
    
    def get_performance_trends(
        self,
        days_back: int = 30,
        environment: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get aggregated performance trends across all models.
        
        Args:
            days_back: How many days of history to fetch
            environment: Filter by environment
        
        Returns:
            DataFrame with daily aggregated metrics
        """
        response = self.client.table('v_performance_trends') \
            .select('*') \
            .gte('date', (datetime.utcnow() - timedelta(days=days_back)).date().isoformat())
        
        if environment:
            response = response.eq('environment', environment)
        
        response = response.order('date', desc=True).execute()
        
        if not response.data:
            return pd.DataFrame()
        
        df = pd.DataFrame(response.data)
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    # ========================================================================
    # Comparison & Analysis
    # ========================================================================
    
    def compare_models(
        self,
        model_versions: List[str],
        metric: str = 'f1',
        days_back: int = 30,
        environment: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Compare multiple models over time.
        
        Args:
            model_versions: List of model versions to compare
            metric: Metric to compare
            days_back: How many days of history
            environment: Filter by environment
        
        Returns:
            DataFrame with model comparisons
        """
        start_date = datetime.utcnow() - timedelta(days=days_back)
        
        all_data = []
        
        for model_version in model_versions:
            df = self.get_transactions(
                model_version=model_version,
                environment=environment,
                start_date=start_date
            )
            
            if not df.empty and metric in df.columns:
                df['model_version'] = model_version
                all_data.append(df[['created_at', 'model_version', metric]])
        
        if not all_data:
            return pd.DataFrame()
        
        comparison = pd.concat(all_data, ignore_index=True)
        return comparison.sort_values('created_at')
    
    def detect_regressions(
        self,
        model_version: str,
        threshold: float = 0.05
    ) -> Dict[str, Any]:
        """
        Check for performance regressions.
        
        Args:
            model_version: Model to check
            threshold: F1 drop threshold (0.05 = 5%)
        
        Returns:
            Dictionary with regression analysis
        """
        response = self.client.rpc('detect_regression', {
            'p_model_version': model_version,
            'p_threshold': threshold
        }).execute()
        
        if response.data:
            return response.data[0] if isinstance(response.data, list) else response.data
        
        return {}
    
    # ========================================================================
    # Metadata & Discovery
    # ========================================================================
    
    def get_available_models(self, environment: Optional[str] = None) -> List[str]:
        """Get list of unique model versions."""
        query = self.client.table('benchmark_snapshots') \
            .select('model_version')
        
        if environment:
            query = query.eq('environment', environment)
        
        response = query.execute()
        
        if not response.data:
            return []
        
        return sorted(set(item['model_version'] for item in response.data))
    
    def get_available_environments(self) -> List[str]:
        """Get list of unique environments."""
        response = self.client.table('benchmark_snapshots') \
            .select('environment') \
            .execute()
        
        if not response.data:
            return []
        
        return sorted(set(item['environment'] for item in response.data))
    
    def get_model_metadata(self, model_version: str) -> Dict[str, Any]:
        """
        Get metadata about a specific model.
        
        Args:
            model_version: Model version to query
        
        Returns:
            Dictionary with model metadata
        """
        response = self.client.table('benchmark_transactions') \
            .select('model_provider, dataset_version, prompt_version, environment') \
            .eq('model_version', model_version) \
            .order('created_at', desc=True) \
            .limit(1) \
            .execute()
        
        if response.data:
            return response.data[0]
        
        return {}

# ============================================================================
# Utility Functions for Dashboard
# ============================================================================

def format_metric(value: float, metric_type: str) -> str:
    """
    Format metric for display.
    
    Args:
        value: Metric value
        metric_type: Type of metric (percentage, currency, time)
    
    Returns:
        Formatted string
    """
    if metric_type == 'percentage':
        return f"{value * 100:.2f}%"
    elif metric_type == 'currency':
        return f"${value:.4f}"
    elif metric_type == 'time':
        return f"{value:.0f}ms"
    else:
        return f"{value:.4f}"

def calculate_delta(current: float, baseline: float) -> tuple:
    """
    Calculate delta and direction.
    
    Args:
        current: Current value
        baseline: Baseline value
    
    Returns:
        Tuple of (delta, percentage_change, direction)
    """
    delta = current - baseline
    pct_change = (delta / baseline) * 100 if baseline != 0 else 0
    direction = 'up' if delta > 0 else 'down' if delta < 0 else 'neutral'
    
    return delta, pct_change, direction

def aggregate_metrics(df: pd.DataFrame, metric_cols: List[str]) -> Dict[str, float]:
    """
    Aggregate multiple metrics from DataFrame.
    
    Args:
        df: DataFrame with metric columns
        metric_cols: List of metric column names
    
    Returns:
        Dictionary with aggregated metrics
    """
    agg_dict = {}
    
    for col in metric_cols:
        if col in df.columns:
            agg_dict[f'{col}_mean'] = df[col].mean()
            agg_dict[f'{col}_std'] = df[col].std()
            agg_dict[f'{col}_min'] = df[col].min()
            agg_dict[f'{col}_max'] = df[col].max()
    
    return agg_dict
