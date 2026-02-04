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
import pandas as pd
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
        # Use service role key for dashboard (needs full read access)
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ANON_KEY')
        return BenchmarkDataAccess(supabase_url=url, supabase_key=key)
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        st.info("Please ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set in your environment.")
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

tab6, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏥 Patient Benchmarks",
    "📊 Current Snapshot",
    "📈 Performance Trends",
    "🔄 Model Comparison",
    "⚠️ Regression Detection",
    "🕐 Snapshot History"
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
                
                st.plotly_chart(fig_f1, use_container_width=True, key=f"f1_chart_{model_version}")
            
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
                
                st.plotly_chart(fig_count, use_container_width=True, key=f"count_chart_{model_version}")
            
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
            
            st.plotly_chart(fig_comparison, use_container_width=True, key="comparison_chart")
            
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
# ============================================================================
# TAB 5: Snapshot History & Version Management
# ============================================================================

with tab5:
    st.header("Snapshot History & Version Control")
    
    st.markdown("""
    View and manage snapshot versions for each model configuration. 
    You can checkout (rollback to) previous snapshots to compare or restore older versions.
    """)
    
    # Model selection for history
    available_models_history = data_access.get_available_models()
    
    if not available_models_history:
        st.info("No models found. Run benchmarks to create snapshots.")
    else:
        selected_model_history = st.selectbox(
            "Select Model",
            options=available_models_history,
            key="history_model"
        )
        
        # Get snapshot history for selected model
        history_df = data_access.get_snapshot_history(
            model_version=selected_model_history,
            dataset_version="benchmark-set-v1",  # You might want to make this dynamic
            prompt_version="v1",  # You might want to make this dynamic
            environment=env_filter or "github-actions",
            limit=50
        )
        
        if history_df.empty:
            st.warning(f"No snapshot history found for {selected_model_history}")
        else:
            st.subheader(f"📜 Version History: {selected_model_history}")
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Versions", len(history_df))
            with col2:
                current_version = history_df[history_df['is_current']]['snapshot_version'].iloc[0] if any(history_df['is_current']) else "N/A"
                st.metric("Current Version", f"v{current_version}")
            with col3:
                baseline_count = sum(history_df['is_baseline'])
                st.metric("Baselines", baseline_count)
            with col4:
                latest_f1 = history_df.iloc[0]['f1_score'] if not history_df.empty else 0
                st.metric("Latest F1", f"{latest_f1:.4f}")
            
            st.markdown("---")
            
            # History table with actions
            st.subheader("📊 All Snapshot Versions")
            
            # Format the display
            display_history = history_df.copy()
            display_history['created_at_display'] = pd.to_datetime(display_history['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            display_history['version'] = 'v' + display_history['snapshot_version'].astype(str)
            display_history['status'] = display_history.apply(
                lambda row: '✅ CURRENT' if row['is_current'] else ('⭐ BASELINE' if row['is_baseline'] else ''),
                axis=1
            )
            
            # Select columns to display
            display_cols = [
                'version', 'status', 'f1_score', 'precision_score', 'recall_score',
                'latency_ms', 'created_at_display', 'commit_sha'
            ]
            
            st.dataframe(
                display_history[display_cols],
                use_container_width=True,
                column_config={
                    "version": "Version",
                    "status": "Status",
                    "f1_score": st.column_config.NumberColumn("F1", format="%.4f"),
                    "precision_score": st.column_config.NumberColumn("Precision", format="%.4f"),
                    "recall_score": st.column_config.NumberColumn("Recall", format="%.4f"),
                    "latency_ms": st.column_config.NumberColumn("Latency (ms)", format="%.0f"),
                    "created_at_display": "Created At",
                    "commit_sha": st.column_config.TextColumn("Commit", width="small")
                }
            )
            
            st.markdown("---")
            
            # Checkout/Rollback section
            st.subheader("🔄 Checkout Snapshot Version")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                available_versions = history_df['snapshot_version'].tolist()
                selected_version = st.selectbox(
                    "Select version to checkout",
                    options=available_versions,
                    format_func=lambda x: f"v{x}" + (" (Current)" if history_df[history_df['snapshot_version'] == x]['is_current'].iloc[0] else "")
                )
                
                if selected_version:
                    version_info = history_df[history_df['snapshot_version'] == selected_version].iloc[0]
                    st.info(f"""
                    **Version {selected_version} Details:**
                    - F1 Score: {version_info['f1_score']:.4f}
                    - Precision: {version_info['precision_score']:.4f}
                    - Recall: {version_info['recall_score']:.4f}
                    - Created: {version_info['created_at']}
                    - Commit: {version_info['commit_sha'][:8]}
                    """)
            
            with col2:
                st.markdown("### Actions")
                if st.button("🔄 Checkout This Version", type="primary", key="checkout_btn"):
                    try:
                        success = data_access.checkout_snapshot(
                            model_version=selected_model_history,
                            dataset_version="benchmark-set-v1",
                            prompt_version="v1",
                            environment=env_filter or "github-actions",
                            snapshot_version=selected_version
                        )
                        if success:
                            st.success(f"✅ Successfully checked out version {selected_version}!")
                            st.info("The dashboard will now show this version as current. Refresh the page to see changes.")
                            st.rerun()
                        else:
                            st.error("Failed to checkout version.")
                    except Exception as e:
                        st.error(f"Error checking out version: {str(e)}")
                
                if st.button("⭐ Set as Baseline", key="baseline_btn"):
                    st.info("Baseline setting feature coming soon!")
            
            # Version comparison
            st.markdown("---")
            st.subheader("📊 Compare Versions")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                version_a = st.selectbox("Version A", options=available_versions, key="ver_a")
            
            with col2:
                version_b = st.selectbox("Version B", options=available_versions, index=min(1, len(available_versions)-1) if len(available_versions) > 1 else 0, key="ver_b")
            
            with col3:
                st.markdown("###")
                if st.button("Compare", type="secondary"):
                    if version_a == version_b:
                        st.warning("Please select different versions to compare.")
                    else:
                        comparison = data_access.compare_snapshot_versions(
                            model_version=selected_model_history,
                            dataset_version="benchmark-set-v1",
                            prompt_version="v1",
                            environment=env_filter or "github-actions",
                            version_a=version_a,
                            version_b=version_b
                        )
                        
                        if not comparison.empty:
                            st.markdown(f"### Comparison: v{version_a} vs v{version_b}")
                            
                            # Format comparison table
                            comparison_display = comparison.copy()
                            comparison_display['delta'] = comparison_display.apply(
                                lambda row: f"{row['delta']:+.4f}" if row['metric'] != 'latency_ms' else f"{row['delta']:+.2f}",
                                axis=1
                            )
                            comparison_display['percent_change'] = comparison_display['percent_change'].apply(
                                lambda x: f"{x:+.2f}%" if pd.notnull(x) else "N/A"
                            )
                            
                            st.dataframe(
                                comparison_display,
                                use_container_width=True,
                                column_config={
                                    "metric": "Metric",
                                    "version_a_value": st.column_config.NumberColumn(f"v{version_a}", format="%.4f"),
                                    "version_b_value": st.column_config.NumberColumn(f"v{version_b}", format="%.4f"),
                                    "delta": "Δ",
                                    "percent_change": "% Change"
                                }
                            )
                            
                            # Highlight improvements
                            improvements = comparison_display[
                                (comparison_display['metric'].isin(['f1_score', 'precision', 'recall'])) &
                                (comparison_display['delta'].str.contains(r'\+'))
                            ]
                            
                            if not improvements.empty:
                                st.success(f"✅ {len(improvements)} metric(s) improved in v{version_b}")
                        else:
                            st.warning("No comparison data available.")

# Footer
# ============================================================================

# ============================================================================
# TAB 6: Patient Benchmarks (Cross-Document Domain Knowledge)
# ============================================================================

with tab6:
    st.header("🏥 Patient Cross-Document Benchmarks")
    st.markdown("""
    **Domain Knowledge Detection:** Testing models' ability to identify gender/age-inappropriate 
    medical procedures that require healthcare domain knowledge (e.g., male patient billed for 
    pregnancy ultrasound, 8-year-old billed for colonoscopy).
    """)
    
    @st.cache_data(ttl=300)
    def load_patient_benchmarks():
        """Load patient benchmark results from transactions table."""
        # Calculate start_date from days_back
        start_date = datetime.now() - timedelta(days=days_back)
        
        # Get all transactions (metrics are already expanded into columns)
        df = data_access.get_transactions(start_date=start_date, environment=env_filter)
        
        if df.empty:
            return pd.DataFrame()
        
        # Filter to only patient benchmarks (have total_patients column)
        if 'total_patients' not in df.columns:
            return pd.DataFrame()
        
        patient_df = df[df['total_patients'].notna()].copy()
        
        if patient_df.empty:
            return pd.DataFrame()
        
        # Filter out old short-name models (keep only full model names with version numbers)
        # Old names: medgemma, openai, gemini, baseline
        # New names: Google MedGemma-4B-IT, OpenAI GPT-4, Google Gemini 1.5 Pro, Heuristic Baseline
        short_names = ['medgemma', 'openai', 'gemini', 'baseline', 'medgemma-v1.0', 'openai-v1.0', 'baseline-v1.0']
        patient_df = patient_df[~patient_df['model_version'].isin(short_names)].copy()
        
        if patient_df.empty:
            return pd.DataFrame()
        
        # Create clean dataset with required columns
        # Handle both decimal (0.667) and percentage (66.7) formats for backwards compatibility
        domain_rates = patient_df.get('domain_knowledge_detection_rate', 0)
        # If values are > 1, they're already percentages; if <= 1, they're decimals needing conversion
        domain_detection = domain_rates.apply(lambda x: x if x > 1 else x * 100)
        
        result_df = pd.DataFrame({
            'model_version': patient_df['model_version'],
            'created_at': patient_df['created_at'],
            'domain_detection': domain_detection,
            'f1_score': patient_df.get('f1', 0),
            'precision': patient_df.get('precision', 0),
            'recall': patient_df.get('recall', 0),
            'latency_ms': patient_df.get('latency_ms', 0),
            'total_patients': patient_df.get('total_patients', 0),
            'successful': patient_df.get('successful_analyses', 0)
        })
        
        return result_df
    
    patient_df = load_patient_benchmarks()
    
    if patient_df.empty:
        st.warning("No patient benchmark data available. Run patient benchmarks with: `python3 scripts/generate_patient_benchmarks.py --model all --push-to-supabase`")
    else:
        # Get latest result per model
        latest_results = patient_df.sort_values('created_at').groupby('model_version').last().reset_index()
        latest_results = latest_results.sort_values('domain_detection', ascending=False)
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            best_model = latest_results.iloc[0]['model_version'] if not latest_results.empty else "N/A"
            best_score = latest_results.iloc[0]['domain_detection'] if not latest_results.empty else 0
            st.metric(
                "🏆 Top Model",
                best_model,
                f"{best_score:.1f}% domain detection"
            )
        
        with col2:
            # Calculate average excluding models with 0% (non-functional models)
            functional_models = latest_results[latest_results['domain_detection'] > 0]
            avg_domain = functional_models['domain_detection'].mean() if not functional_models.empty else 0
            model_count = len(functional_models)
            st.metric(
                f"Avg Domain Detection ({model_count} models)",
                f"{avg_domain:.1f}%",
                help="Average across models that detect domain issues (excludes 0% scores)"
            )
        
        with col3:
            # Use same functional models filter for consistency
            avg_f1 = functional_models['f1_score'].mean() if not functional_models.empty else 0
            st.metric(
                f"Avg F1 Score ({model_count} models)",
                f"{avg_f1:.3f}",
                help="Average F1 across functional models (excludes 0% scores)"
            )
        
        with col4:
            total_runs = len(patient_df)
            st.metric(
                "Total Benchmark Runs",
                f"{total_runs}"
            )
        
        st.markdown("---")
        
        # Leaderboard
        st.subheader("📊 Domain Knowledge Leaderboard (Latest Run)")
        
        display_df = latest_results[[
            'model_version', 'domain_detection', 'f1_score', 
            'precision', 'recall', 'total_patients', 'successful'
        ]].copy()
        
        display_df.columns = [
            'Model', 'Domain Detection %', 'F1 Score', 
            'Precision', 'Recall', 'Total Patients', 'Successful'
        ]
        
        # Format percentages and decimals
        display_df['Domain Detection %'] = display_df['Domain Detection %'].apply(lambda x: f"{x:.1f}%")
        display_df['F1 Score'] = display_df['F1 Score'].apply(lambda x: f"{x:.3f}")
        display_df['Precision'] = display_df['Precision'].apply(lambda x: f"{x:.3f}")
        display_df['Recall'] = display_df['Recall'].apply(lambda x: f"{x:.3f}")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Historical trends
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Domain Detection Over Time")
            
            if len(patient_df) > 1:
                fig = px.line(
                    patient_df,
                    x='created_at',
                    y='domain_detection',
                    color='model_version',
                    markers=True,
                    labels={
                        'created_at': 'Date',
                        'domain_detection': 'Domain Detection Rate (%)',
                        'model_version': 'Model'
                    }
                )
                fig.update_layout(height=400, hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True, key="patient_domain_trend")
            else:
                st.info("Run multiple benchmarks over time to see trends")
        
        with col2:
            st.subheader("📊 F1 Score Comparison")
            
            fig = go.Figure()
            for model in latest_results['model_version'].unique():
                model_data = latest_results[latest_results['model_version'] == model]
                fig.add_trace(go.Bar(
                    name=model,
                    x=['F1 Score'],
                    y=[model_data['f1_score'].values[0]],
                    text=[f"{model_data['f1_score'].values[0]:.3f}"],
                    textposition='auto'
                ))
            
            fig.update_layout(
                height=400,
                yaxis_title="F1 Score",
                showlegend=True,
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True, key="patient_f1_comparison")
        
        # Detailed metrics
        st.markdown("---")
        st.subheader("🔍 Detailed Performance Metrics")
        
        # Heatmap of performance across models
        heatmap_df = latest_results[['model_version', 'domain_detection', 'f1_score', 'precision', 'recall']].set_index('model_version')
        heatmap_df.columns = ['Domain Detection %', 'F1', 'Precision', 'Recall']
        
        fig = px.imshow(
            heatmap_df.T,
            labels=dict(x="Model", y="Metric", color="Score"),
            x=heatmap_df.index,
            y=heatmap_df.columns,
            color_continuous_scale='RdYlGn',
            aspect='auto',
            text_auto='.2f'
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True, key="patient_heatmap")
        
        # Error Type Performance Heatmap
        st.markdown("---")
        st.subheader("🎯 Performance by Error Type")
        st.markdown("Detection accuracy for different types of billing errors that require medical domain knowledge.")
        
        # Load detailed patient results from transactions to analyze error types
        try:
            from supabase import create_client
            import os
            import numpy as np
            
            supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
            
            # Get latest transaction for each model with error_type_performance data
            query = supabase.table('benchmark_transactions').select('model_version, metrics, created_at').eq('environment', env_filter or 'local').order('created_at', desc=True).limit(100)
            response = query.execute()
            
            if response.data:
                # Build error type performance matrix - use latest result per model
                model_error_performance = {}
                
                for transaction in response.data:
                    model = transaction['model_version']
                    
                    # Skip old short-name models
                    if model in ['medgemma', 'openai', 'gemini', 'baseline', 'medgemma-v1.0', 'openai-v1.0', 'baseline-v1.0']:
                        continue
                    
                    # Only take the first (latest) result for each model
                    if model in model_error_performance:
                        continue
                    
                    metrics = transaction.get('metrics', {})
                    error_type_perf = metrics.get('error_type_performance', {})
                    
                    if error_type_perf:
                        model_error_performance[model] = error_type_perf
                
                if model_error_performance:
                    # Build heatmap dataframe
                    # Get all unique error types
                    all_error_types = set()
                    for model_data in model_error_performance.values():
                        all_error_types.update(model_data.keys())
                    
                    # Create matrix
                    heatmap_data = []
                    models_list = sorted(model_error_performance.keys())
                    error_types_list = sorted(all_error_types)
                    
                    for error_type in error_types_list:
                        row = []
                        for model in models_list:
                            perf = model_error_performance[model].get(error_type, {})
                            detection_rate = perf.get('detection_rate', 0.0) * 100  # Convert to percentage
                            row.append(detection_rate)
                        heatmap_data.append(row)
                    
                    # Create heatmap
                    heatmap_array = np.array(heatmap_data)
                    
                    # Format error type names for display
                    formatted_error_types = [et.replace('_', ' ').title() for et in error_types_list]
                    
                    fig = px.imshow(
                        heatmap_array,
                        labels=dict(x="Model", y="Error Type", color="Detection Rate (%)"),
                        x=models_list,
                        y=formatted_error_types,
                        color_continuous_scale='RdYlGn',
                        aspect='auto',
                        text_auto='.1f'
                    )
                    fig.update_layout(
                        height=max(400, len(error_types_list) * 30),
                        xaxis={'side': 'bottom'},
                        yaxis={'side': 'left'}
                    )
                    fig.update_xaxes(tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True, key="error_type_heatmap")
                    
                    # Summary statistics
                    st.markdown("**Summary:**")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Best performing error type
                        avg_by_error = heatmap_array.mean(axis=1)
                        best_error_idx = avg_by_error.argmax()
                        st.metric(
                            "Easiest to Detect",
                            formatted_error_types[best_error_idx],
                            f"{avg_by_error[best_error_idx]:.1f}% avg detection"
                        )
                    
                    with col2:
                        # Most challenging error type
                        worst_error_idx = avg_by_error.argmin()
                        st.metric(
                            "Most Challenging",
                            formatted_error_types[worst_error_idx],
                            f"{avg_by_error[worst_error_idx]:.1f}% avg detection"
                        )
                else:
                    st.info("No error-type performance data available yet. Re-push benchmark results to collect this data.")
            else:
                st.warning("No transaction data available for error type analysis.")
        except Exception as e:
            st.error(f"Error loading error type performance: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
        
        # Insights
        st.markdown("---")
        st.subheader("💡 Key Insights")
        
        if not latest_results.empty:
            best = latest_results.iloc[0]
            worst = latest_results.iloc[-1]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.success(f"""
                **Best Performer: {best['model_version']}**
                - Domain Detection: {best['domain_detection']:.1f}%
                - F1 Score: {best['f1_score']:.3f}
                - Successfully analyzed {best['successful']}/{best['total_patients']} patients
                """)
            
            with col2:
                if worst['domain_detection'] < best['domain_detection']:
                    gap = best['domain_detection'] - worst['domain_detection']
                    st.warning(f"""
                    **Performance Gap**
                    - {best['model_version']} outperforms {worst['model_version']} by {gap:.1f}% in domain detection
                    - Medical domain knowledge is critical for accurate billing issue detection
                    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>Benchmark Monitoring Dashboard v1.0 | MLOps Team</p>
    <p>Data refreshes every 5 minutes | Last refresh: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
