"""
Benchmark Monitoring Dashboard
================================

Streamlit page for visualizing benchmark performance over time.

Features:
- Latest snapshot view
- Historical trends
- Model comparison
- Regression detection
- Time-range filtering

Author: Senior MLOps Engineer
Date: 2026-02-03
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

try:
    from benchmark_data_access import BenchmarkDataAccess, format_metric, calculate_delta
except ImportError:
    st.error("Could not import benchmark_data_access. Please ensure the module exists.")
    st.stop()

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="Benchmark Monitoring",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Benchmark Monitoring Dashboard")
st.markdown("Real-time ML model performance tracking and regression detection")

# ============================================================================
# Initialize Data Access
# ============================================================================

@st.cache_resource
def get_data_access():
    """Initialize data access layer with caching."""
    try:
        return BenchmarkDataAccess()
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        st.info("Please ensure SUPABASE_URL and SUPABASE_ANON_KEY are set in your environment.")
        st.stop()

data_access = get_data_access()

# ============================================================================
# Sidebar Filters
# ============================================================================

st.sidebar.header("⚙️ Filters")

# Environment filter
environments = data_access.get_available_environments()
selected_environment = st.sidebar.selectbox(
    "Environment",
    options=['All'] + environments,
    index=0
)
env_filter = None if selected_environment == 'All' else selected_environment

# Time range filter
time_range = st.sidebar.selectbox(
    "Time Range",
    options=['Last 7 days', 'Last 30 days', 'Last 90 days', 'All time'],
    index=1
)

days_back_map = {
    'Last 7 days': 7,
    'Last 30 days': 30,
    'Last 90 days': 90,
    'All time': 365 * 10  # 10 years
}
days_back = days_back_map[time_range]

# Model filter
available_models = data_access.get_available_models(env_filter)
selected_models = st.sidebar.multiselect(
    "Model Versions",
    options=available_models,
    default=available_models[:min(3, len(available_models))] if available_models else []
)

# Refresh button
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Last Updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# ============================================================================
# Tab Layout
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Current Snapshot",
    "📈 Performance Trends",
    "🔄 Model Comparison",
    "⚠️ Regression Detection"
])

# ============================================================================
# TAB 1: Current Snapshot
# ============================================================================

with tab1:
    st.header("Current Performance Snapshot")
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def load_snapshots(environment):
        return data_access.get_latest_snapshots(environment=environment)
    
    snapshots_df = load_snapshots(env_filter)
    
    if snapshots_df.empty:
        st.warning("No benchmark data available.")
    else:
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_f1 = snapshots_df['f1_score'].mean()
            st.metric(
                "Average F1 Score",
                f"{avg_f1:.4f}",
                delta=None
            )
        
        with col2:
            avg_precision = snapshots_df['precision_score'].mean()
            st.metric(
                "Average Precision",
                f"{avg_precision:.4f}",
                delta=None
            )
        
        with col3:
            avg_recall = snapshots_df['recall_score'].mean()
            st.metric(
                "Average Recall",
                f"{avg_recall:.4f}",
                delta=None
            )
        
        with col4:
            avg_latency = snapshots_df['latency_ms'].mean()
            st.metric(
                "Average Latency",
                f"{avg_latency:.0f}ms",
                delta=None
            )
        
        st.markdown("---")
        
        # Top performers
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top Performers by F1")
            top_f1 = snapshots_df.nlargest(5, 'f1_score')[
                ['model_version', 'f1_score', 'precision_score', 'recall_score', 'latency_ms']
            ]
            st.dataframe(top_f1, use_container_width=True)
        
        with col2:
            st.subheader("⚡ Fastest by Latency")
            top_speed = snapshots_df.nsmallest(5, 'latency_ms')[
                ['model_version', 'latency_ms', 'f1_score', 'cost_per_analysis']
            ]
            st.dataframe(top_speed, use_container_width=True)
        
        st.markdown("---")
        
        # Full snapshot table
        st.subheader("📋 All Active Configurations")
        
        # Format display
        display_df = snapshots_df[[
            'model_version',
            'dataset_version',
            'prompt_version',
            'environment',
            'f1_score',
            'precision_score',
            'recall_score',
            'latency_ms',
            'cost_per_analysis',
            'created_at'
        ]].copy()
        
        display_df['created_at'] = display_df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "f1_score": st.column_config.NumberColumn("F1", format="%.4f"),
                "precision_score": st.column_config.NumberColumn("Precision", format="%.4f"),
                "recall_score": st.column_config.NumberColumn("Recall", format="%.4f"),
                "latency_ms": st.column_config.NumberColumn("Latency (ms)", format="%.0f"),
                "cost_per_analysis": st.column_config.NumberColumn("Cost", format="$%.4f"),
            }
        )

# ============================================================================
# TAB 2: Performance Trends
# ============================================================================

with tab2:
    st.header("Performance Trends Over Time")
    
    if not selected_models:
        st.info("Please select at least one model from the sidebar.")
    else:
        for model_version in selected_models:
            st.subheader(f"📈 {model_version}")
            
            @st.cache_data(ttl=300)
            def load_timeseries(model, days, environment):
                return data_access.get_time_series(
                    model_version=model,
                    metric='f1',
                    granularity='day',
                    days_back=days,
                    environment=environment
                )
            
            ts_df = load_timeseries(model_version, days_back, env_filter)
            
            if ts_df.empty:
                st.warning(f"No historical data for {model_version}")
                continue
            
            # Create metrics
            col1, col2 = st.columns(2)
            
            with col1:
                # F1 trend chart
                fig_f1 = go.Figure()
                
                fig_f1.add_trace(go.Scatter(
                    x=ts_df['created_at'],
                    y=ts_df['mean'],
                    mode='lines+markers',
                    name='Mean F1',
                    line=dict(color='#1f77b4', width=2),
                    marker=dict(size=6)
                ))
                
                # Add confidence band
                if 'std' in ts_df.columns:
                    fig_f1.add_trace(go.Scatter(
                        x=ts_df['created_at'],
                        y=ts_df['mean'] + ts_df['std'],
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                    
                    fig_f1.add_trace(go.Scatter(
                        x=ts_df['created_at'],
                        y=ts_df['mean'] - ts_df['std'],
                        mode='lines',
                        line=dict(width=0),
                        fill='tonexty',
                        fillcolor='rgba(31, 119, 180, 0.2)',
                        name='±1 Std Dev',
                        hoverinfo='skip'
                    ))
                
                fig_f1.update_layout(
                    title="F1 Score Over Time",
                    xaxis_title="Date",
                    yaxis_title="F1 Score",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig_f1, use_container_width=True)
            
            with col2:
                # Run count
                fig_count = go.Figure()
                
                fig_count.add_trace(go.Bar(
                    x=ts_df['created_at'],
                    y=ts_df['count'],
                    name='Run Count',
                    marker_color='#2ca02c'
                ))
                
                fig_count.update_layout(
                    title="Daily Run Count",
                    xaxis_title="Date",
                    yaxis_title="Number of Runs",
                    height=400
                )
                
                st.plotly_chart(fig_count, use_container_width=True)
            
            st.markdown("---")

# ============================================================================
# TAB 3: Model Comparison
# ============================================================================

with tab3:
    st.header("Model Comparison")
    
    if len(selected_models) < 2:
        st.info("Please select at least 2 models from the sidebar to compare.")
    else:
        @st.cache_data(ttl=300)
        def load_comparison(models, days, environment):
            return data_access.compare_models(
                model_versions=models,
                metric='f1',
                days_back=days,
                environment=environment
            )
        
        comparison_df = load_comparison(selected_models, days_back, env_filter)
        
        if comparison_df.empty:
            st.warning("No comparison data available.")
        else:
            # Line chart comparison
            fig_comparison = go.Figure()
            
            for model in selected_models:
                model_data = comparison_df[comparison_df['model_version'] == model]
                
                fig_comparison.add_trace(go.Scatter(
                    x=model_data['created_at'],
                    y=model_data['f1'],
                    mode='lines+markers',
                    name=model,
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
            
            fig_comparison.update_layout(
                title="F1 Score Comparison",
                xaxis_title="Date",
                yaxis_title="F1 Score",
                hovermode='x unified',
                height=500,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            # Summary statistics
            st.subheader("📊 Comparison Statistics")
            
            summary_data = []
            for model in selected_models:
                model_data = comparison_df[comparison_df['model_version'] == model]['f1']
                summary_data.append({
                    'Model': model,
                    'Mean F1': model_data.mean(),
                    'Std Dev': model_data.std(),
                    'Min': model_data.min(),
                    'Max': model_data.max(),
                    'Samples': len(model_data)
                })
            
            import pandas as pd
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(
                summary_df,
                use_container_width=True,
                column_config={
                    "Mean F1": st.column_config.NumberColumn(format="%.4f"),
                    "Std Dev": st.column_config.NumberColumn(format="%.4f"),
                    "Min": st.column_config.NumberColumn(format="%.4f"),
                    "Max": st.column_config.NumberColumn(format="%.4f"),
                }
            )

# ============================================================================
# TAB 4: Regression Detection
# ============================================================================

with tab4:
    st.header("⚠️ Regression Detection")
    
    st.markdown("""
    This tab checks for performance regressions by comparing current performance
    against established baselines. A regression is flagged when F1 score drops
    by more than the specified threshold.
    """)
    
    threshold = st.slider(
        "Regression Threshold (%)",
        min_value=1.0,
        max_value=10.0,
        value=5.0,
        step=0.5,
        help="Alert when F1 drops by more than this percentage"
    )
    
    st.markdown("---")
    
    if not selected_models:
        st.info("Please select at least one model from the sidebar.")
    else:
        for model_version in selected_models:
            with st.expander(f"🔍 {model_version}", expanded=True):
                @st.cache_data(ttl=300)
                def check_regression(model, thresh):
                    return data_access.detect_regressions(
                        model_version=model,
                        threshold=thresh / 100  # Convert percentage to decimal
                    )
                
                regression_result = check_regression(model_version, threshold)
                
                if not regression_result:
                    st.warning("No baseline configured for this model.")
                    continue
                
                current_f1 = regression_result.get('current_f1', 0)
                baseline_f1 = regression_result.get('baseline_f1', 0)
                f1_drop = regression_result.get('f1_drop', 0)
                is_regression = regression_result.get('is_regression', False)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Current F1",
                        f"{current_f1:.4f}",
                        delta=f"{-f1_drop:.4f}" if f1_drop > 0 else f"+{abs(f1_drop):.4f}",
                        delta_color="inverse"
                    )
                
                with col2:
                    st.metric(
                        "Baseline F1",
                        f"{baseline_f1:.4f}"
                    )
                
                with col3:
                    pct_drop = (f1_drop / baseline_f1 * 100) if baseline_f1 > 0 else 0
                    st.metric(
                        "Drop %",
                        f"{pct_drop:.2f}%"
                    )
                
                if is_regression:
                    st.error(f"🚨 **REGRESSION DETECTED** - F1 dropped by {pct_drop:.2f}%")
                    st.markdown("**Recommended Actions:**")
                    st.markdown("- Review recent code changes")
                    st.markdown("- Check for data drift")
                    st.markdown("- Verify prompt modifications")
                    st.markdown("- Inspect model configuration")
                else:
                    st.success("✅ No regression detected - performance within expected range")

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>Benchmark Monitoring Dashboard v1.0 | MLOps Team</p>
    <p>Data refreshes every 5 minutes | Last refresh: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
