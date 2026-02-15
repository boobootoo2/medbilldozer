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
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add scripts to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))

# Add src to path for medbilldozer imports
src_path = PROJECT_ROOT / "src"
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from benchmark_data_access import BenchmarkDataAccess, format_metric, calculate_delta
except ImportError:
    st.error("Could not import benchmark_data_access. Please ensure the module exists.")
    st.stop()

# Import benchmark assistant
try:
    from medbilldozer.ui.benchmark_assistant import render_benchmark_assistant
    from medbilldozer.ui.doc_assistant import render_assistant_avatar
    from medbilldozer.utils.config import is_assistant_enabled
except ImportError as e:
    st.warning(f"Benchmark assistant not available: {e}")
    render_benchmark_assistant = None
    is_assistant_enabled = lambda: False

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="🚨 Production Stability",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for metric styling
st.markdown("""
<style>
    /* Increase font size for metric values (model names) */
    [data-testid="stMetricValue"] {
        font-size: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚨 Production Stability")
st.markdown("Real-time ML model performance tracking and regression detection")

# ============================================================================
# BETA Mode Check
# ============================================================================

BETA_MODE = os.getenv('BETA', 'false').lower() in ('true', '1', 'yes')

if BETA_MODE:
    st.info("🧪 **BETA Mode Enabled**: Clinical Validation Dashboard now available!")

# ============================================================================
# Assistant Notification
# ============================================================================

# Show dismissible assistant notification (only once per session)
if (is_assistant_enabled() and
    render_benchmark_assistant is not None and
    not st.session_state.get('benchmark_assistant_notification_dismissed', False)):

    col1, col2 = st.columns([20, 1])

    with col1:
        st.info(
            "💡 **New!** Billy & Billie the document assistants are available in the left side panel to help answer questions about metrics, regressions, and model performance.",
            icon="🤖"
        )

    with col2:
        if st.button("✕", key="dismiss_benchmark_assistant_notification", help="Dismiss"):
            st.session_state.benchmark_assistant_notification_dismissed = True
            st.rerun()

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
# Benchmark Assistant (sidebar)
# ============================================================================

if is_assistant_enabled() and render_benchmark_assistant is not None:
    render_benchmark_assistant()

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

if BETA_MODE:
    tab_clinical, tab6, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏥 Clinical Validation (BETA)",
        "🏥 Clinical Reasoning Evaluation",
        "📊 System Health Overview",
        "📈 Reliability Over Time",
        "⚖️ Model Effectiveness Comparison",
        "🚨 Performance Stability Monitor",
        "🕐 Snapshot History"
    ])
else:
    tab_clinical = None
    tab6, tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏥 Clinical Reasoning Evaluation",
        "📊 System Health Overview",
        "📈 Reliability Over Time",
        "⚖️ Model Effectiveness Comparison",
        "🚨 Performance Stability Monitor",
        "🕐 Snapshot History"
    ])

# ============================================================================
# TAB CLINICAL: Clinical Validation (BETA Mode Only)
# ============================================================================

if BETA_MODE and tab_clinical:
    with tab_clinical:
        st.header("🏥 Clinical Validation Benchmarks")
        st.markdown("Multi-modal clinical error detection performance using real medical images")
        
        # Initialize Beta Data Access
        @st.cache_resource
        def get_beta_data_access():
            """Initialize beta database access for clinical validation."""
            try:
                url = os.getenv('SUPABASE_BETA_URL', 'https://zrhlpitzonhftigmdvgz.supabase.co')
                key = os.getenv('SUPABASE_BETA_KEY')
                if not key:
                    st.warning("🔑 SUPABASE_BETA_KEY not set. Clinical validation data unavailable.")
                    return None
                return BenchmarkDataAccess(supabase_url=url, supabase_key=key)
            except Exception as e:
                st.error(f"Failed to connect to beta database: {e}")
                return None
        
        beta_data_access = get_beta_data_access()
        
        if beta_data_access:
            # Fetch latest clinical validation snapshot
            try:
                # Query clinical_validation_snapshots table directly
                response = beta_data_access.client.table('clinical_validation_snapshots') \
                    .select('*') \
                    .eq('environment', 'beta') \
                    .order('created_at', desc=True) \
                    .limit(30) \
                    .execute()
                
                snapshots = response.data if response.data else []
            
            except Exception as table_error:
                # Table might not exist yet
                if 'does not exist' in str(table_error).lower() or 'relation' in str(table_error).lower():
                    st.info("📊 Clinical validation table not set up yet. Run benchmarks first to create data.")
                    snapshots = []
                else:
                    raise table_error
            
            try:
                
                if snapshots:
                    latest = snapshots[0]
                    
                    # Extract metrics (they're nested in 'metrics' field)
                    metrics = latest.get('metrics', latest)  # Fallback to latest if no 'metrics' key
                    
                    # Header Info
                    col_h1, col_h2, col_h3 = st.columns([2, 2, 2])
                    with col_h1:
                        timestamp = latest.get('created_at') or latest.get('timestamp', 'Unknown')
                        st.markdown(f"**Latest Run:** `{timestamp}`")
                    with col_h2:
                        st.markdown(f"**Model:** `{latest.get('model_version', 'Unknown')}`")
                    with col_h3:
                        total = metrics.get('total_scenarios', 0)
                        st.markdown(f"**Scenarios:** `{total}`")
                    
                    st.markdown("---")
                    
                    # Key Metrics
                    st.subheader("📊 Performance Metrics")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        accuracy = metrics.get('accuracy', 0) * 100
                        st.metric("🎯 Accuracy", f"{accuracy:.1f}%")
                    
                    with col2:
                        error_rate = metrics.get('error_detection_rate', 0) * 100
                        st.metric("🔍 Error Detection", f"{error_rate:.1f}%", 
                                 help="Percentage of actual errors correctly identified")
                    
                    with col3:
                        fpr = metrics.get('false_positive_rate', 0) * 100
                        st.metric("⚠️ False Positive Rate", f"{fpr:.1f}%",
                                 help="Percentage of correct treatments incorrectly flagged as errors")
                    
                    with col4:
                        cost = metrics.get('total_cost_savings_potential', 0)
                        if cost >= 1000:
                            st.metric("💰 Cost Savings Potential", f"${cost/1000:.0f}K")
                        else:
                            st.metric("💰 Cost Savings Potential", f"${cost:.0f}")
                    
                    # Methodology Accordion for Overall Metrics
                    with st.expander("📊 Analysis Methodology & Sample Sizes"):
                        st.markdown("**Data Source:**")
                        timestamp = latest.get('created_at') or latest.get('timestamp', 'Unknown')
                        st.markdown(f"- Validation run: `{timestamp}`")
                        st.markdown(f"- Model: `{latest.get('model_version', 'Unknown')}`")
                        st.markdown(f"- Environment: `{latest.get('environment', 'beta')}`")
                        
                        st.markdown("**Sample Sizes:**")
                        total_scenarios = metrics.get('total_scenarios', 0)
                        correct = metrics.get('correct_determinations', 0)
                        st.markdown(f"- **Total Scenarios**: {total_scenarios}")
                        st.markdown(f"- **Correct Determinations**: {correct}")
                        st.markdown(f"- **Incorrect Determinations**: {total_scenarios - correct}")
                        
                        scenarios_by_mod = metrics.get('scenarios_by_modality', {})
                        if scenarios_by_mod:
                            st.markdown(f"- **By Modality**:")
                            for mod, count in scenarios_by_mod.items():
                                st.markdown(f"  - {mod.title()}: {count} scenarios")
                        
                        st.markdown("**Metric Definitions:**")
                        st.markdown(f"""
                        - **Accuracy**: {correct}/{total_scenarios} = {accuracy:.1f}%
                        - **Error Detection**: Fraction of inappropriate treatments correctly identified
                        - **False Positive Rate**: Fraction of appropriate treatments incorrectly flagged
                        - **Cost Savings**: Sum of costs avoided by detecting errors (overtreatment, unnecessary procedures)
                        """)
                        
                        st.markdown("**Test Design:**")
                        st.markdown("""
                        - Each scenario includes: patient context, medical imaging, clinical finding, and prescribed treatment
                        - Model must determine if treatment matches the imaging findings
                        - Balanced dataset: ~50% appropriate treatments, ~50% inappropriate treatments
                        - Covers 4 imaging modalities: X-Ray, Histopathology, MRI, Ultrasound
                        """)
                    
                    # Validation Type Breakdown
                    st.markdown("---")
                    st.subheader("📋 Validation Type Performance")
                    
                    # Check for validation type metrics (new schema)
                    treatment_val = metrics.get('treatment_validation', {})
                    icd_val = metrics.get('icd_validation', {})
                    
                    if treatment_val or icd_val:
                        col_t1, col_t2 = st.columns(2)
                        
                        with col_t1:
                            st.markdown("#### 💊 Treatment Matching")
                            t_total = treatment_val.get('total', 0)
                            t_correct = treatment_val.get('correct', 0)
                            t_accuracy = treatment_val.get('accuracy', 0) * 100
                            st.metric("Accuracy", f"{t_accuracy:.1f}%")
                            st.caption(f"✅ {t_correct}/{t_total} correct determinations")
                            st.caption("_Validates prescribed treatments match imaging findings_")
                        
                        with col_t2:
                            st.markdown("#### 🏥 ICD Code Validation")
                            i_total = icd_val.get('total', 0)
                            i_correct = icd_val.get('correct', 0)
                            i_accuracy = icd_val.get('accuracy', 0) * 100 if icd_val else 0
                            
                            if i_total > 0:
                                st.metric("Accuracy", f"{i_accuracy:.1f}%")
                                st.caption(f"✅ {i_correct}/{i_total} correct determinations")
                                st.caption("_Validates ICD-10 coding accuracy against diagnoses_")
                            else:
                                st.info("No ICD validation data yet")
                                st.caption("_Run benchmarks with ICD scenarios_")
                        
                        # Detailed ICD Code Performance Analysis
                        if i_total > 0:
                            st.markdown("---")
                            st.subheader("🔍 ICD Code Validation Deep Dive")
                            
                            # Get scenario results for detailed analysis
                            scenario_results = metrics.get('scenario_results', [])
                            icd_scenarios = [s for s in scenario_results if s.get('validation_type') == 'icd_coding']
                            
                            if icd_scenarios:
                                # Calculate ICD-specific metrics
                                icd_by_modality = {}
                                icd_correct_codes = 0
                                icd_incorrect_codes = 0
                                icd_errors_detected = 0
                                icd_errors_missed = 0
                                
                                for scenario in icd_scenarios:
                                    modality = scenario.get('modality', 'unknown')
                                    if modality not in icd_by_modality:
                                        icd_by_modality[modality] = {
                                            'total': 0,
                                            'correct': 0,
                                            'error_detection': 0,
                                            'error_scenarios': 0
                                        }
                                    
                                    icd_by_modality[modality]['total'] += 1
                                    if scenario.get('correct', False):
                                        icd_by_modality[modality]['correct'] += 1
                                    
                                    # Track error detection (scenarios where ERROR is expected)
                                    expected = scenario.get('expected', '')
                                    model_response = scenario.get('model_response', '')
                                    if 'ERROR' in expected:
                                        icd_by_modality[modality]['error_scenarios'] += 1
                                        if 'ERROR' in model_response:
                                            icd_by_modality[modality]['error_detection'] += 1
                                            icd_errors_detected += 1
                                        else:
                                            icd_errors_missed += 1
                                        icd_incorrect_codes += 1
                                    else:
                                        icd_correct_codes += 1
                                
                                # Display key ICD metrics
                                col_icd1, col_icd2, col_icd3, col_icd4 = st.columns(4)
                                
                                with col_icd1:
                                    st.metric("📊 Total ICD Tests", f"{i_total}")
                                    st.caption(f"{icd_correct_codes} correct codes + {icd_incorrect_codes} incorrect codes")
                                
                                with col_icd2:
                                    error_detection_rate = (icd_errors_detected / icd_incorrect_codes * 100) if icd_incorrect_codes > 0 else 0
                                    st.metric("🎯 Error Detection", f"{error_detection_rate:.1f}%")
                                    st.caption(f"Caught {icd_errors_detected}/{icd_incorrect_codes} coding errors")
                                
                                with col_icd3:
                                    false_positive_rate = ((i_total - i_correct - icd_errors_detected) / icd_correct_codes * 100) if icd_correct_codes > 0 else 0
                                    st.metric("⚠️ False Positives", f"{false_positive_rate:.1f}%")
                                    st.caption(f"Incorrectly flagged correct codes")
                                
                                with col_icd4:
                                    specificity = (i_correct - icd_errors_detected) / icd_correct_codes * 100 if icd_correct_codes > 0 else 0
                                    st.metric("✅ Specificity", f"{specificity:.1f}%")
                                    st.caption(f"Correctly validated correct codes")
                                
                                # ICD Performance by Modality
                                st.markdown("#### 🔬 ICD Validation by Imaging Modality")
                                
                                icd_mod_rows = []
                                for mod, stats in icd_by_modality.items():
                                    accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
                                    error_rate = (stats['error_detection'] / stats['error_scenarios'] * 100) if stats['error_scenarios'] > 0 else 0
                                    icd_mod_rows.append({
                                        'Modality': mod.title(),
                                        'Tests': stats['total'],
                                        'Accuracy': f"{accuracy:.1f}%",
                                        'Error Detection': f"{error_rate:.1f}%",
                                        'Correct': f"{stats['correct']}/{stats['total']}"
                                    })
                                
                                icd_mod_df = pd.DataFrame(icd_mod_rows)
                                st.dataframe(icd_mod_df, use_container_width=True, hide_index=True)
                                
                                # Visualization: ICD Accuracy by Modality
                                col_viz1, col_viz2 = st.columns(2)
                                
                                with col_viz1:
                                    icd_mod_df['Accuracy_num'] = icd_mod_df['Accuracy'].str.rstrip('%').astype(float)
                                    fig_icd_acc = px.bar(
                                        icd_mod_df,
                                        x='Modality',
                                        y='Accuracy_num',
                                        title='ICD-10 Validation Accuracy by Modality',
                                        labels={'Accuracy_num': 'Accuracy (%)'},
                                        color='Modality',
                                        text='Accuracy_num'
                                    )
                                    fig_icd_acc.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                                    fig_icd_acc.update_layout(showlegend=False, yaxis_range=[0, 110])
                                    st.plotly_chart(fig_icd_acc, use_container_width=True)
                                
                                with col_viz2:
                                    icd_mod_df['Error_Detection_num'] = icd_mod_df['Error Detection'].str.rstrip('%').astype(float)
                                    fig_icd_err = px.bar(
                                        icd_mod_df,
                                        x='Modality',
                                        y='Error_Detection_num',
                                        title='ICD Coding Error Detection by Modality',
                                        labels={'Error_Detection_num': 'Detection Rate (%)'},
                                        color='Modality',
                                        text='Error_Detection_num'
                                    )
                                    fig_icd_err.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                                    fig_icd_err.update_layout(showlegend=False, yaxis_range=[0, 110])
                                    st.plotly_chart(fig_icd_err, use_container_width=True)
                                
                                # Methodology Accordion for ICD Charts
                                with st.expander("📊 Analysis Methodology & Sample Sizes"):
                                    st.markdown("**Data Source:**")
                                    st.markdown(f"- Latest validation run: `{latest.get('created_at', 'Unknown')}`")
                                    st.markdown(f"- Model: `{latest.get('model_version', 'Unknown')}`")
                                    
                                    st.markdown("**Sample Sizes:**")
                                    st.markdown(f"- **Total ICD Tests**: {i_total} scenarios")
                                    st.markdown(f"  - Correct codes (specificity test): {icd_correct_codes}")
                                    st.markdown(f"  - Incorrect codes (sensitivity test): {icd_incorrect_codes}")
                                    st.markdown(f"- **By Modality**: {len(icd_by_modality)} imaging types")
                                    for mod, stats in icd_by_modality.items():
                                        st.markdown(f"  - {mod.title()}: {stats['total']} tests ({stats['error_scenarios']} incorrect codes)")
                                    
                                    st.markdown("**Calculations:**")
                                    st.markdown(f"""
                                    - **Accuracy**: Correct validations / Total tests
                                    - **Error Detection** (Sensitivity): Incorrect codes caught / Total incorrect codes
                                    - **False Positives**: Correct codes flagged as incorrect / Total correct codes
                                    - **Specificity**: Correct codes validated as correct / Total correct codes
                                    """)
                                    
                                    st.markdown("**Test Design:**")
                                    st.markdown("""
                                    Each modality has 6 ICD validation scenarios:
                                    - 3 with correct ICD-10 codes (test specificity)
                                    - 3 with incorrect ICD-10 codes (test sensitivity)
                                    
                                    Model must determine if the provided ICD code matches the clinical diagnosis shown in the imaging.
                                    """)
                                
                                # Sample ICD Scenarios
                                with st.expander("📋 View Sample ICD Validation Scenarios"):
                                    # Show a few example scenarios
                                    sample_scenarios = icd_scenarios[:6]  # Show first 6
                                    for i, scenario in enumerate(sample_scenarios, 1):
                                        scenario_id = scenario.get('scenario_id', 'Unknown')
                                        modality = scenario.get('modality', 'Unknown').title()
                                        expected = scenario.get('expected', '')
                                        model_response = scenario.get('model_response', '')
                                        is_correct = scenario.get('correct', False)
                                        
                                        status_emoji = "✅" if is_correct else "❌"
                                        st.markdown(f"**{i}. {status_emoji} {scenario_id}** ({modality})")
                                        st.markdown(f"   - Expected: `{expected}`")
                                        st.markdown(f"   - Model: `{model_response}`")
                                        if i < len(sample_scenarios):
                                            st.markdown("---")
                            else:
                                st.info("💡 Run benchmarks to see detailed ICD validation metrics")
                                st.caption("Detailed scenario results will appear here after running validation")
                    
                    # ICD Model Comparison Section
                    if len(snapshots) > 1 and i_total > 0:
                        st.markdown("---")
                        st.subheader("🤖 ICD Validation: Model Comparison")
                        st.caption("Compare how different models perform on ICD-10 coding validation")
                        
                        # Aggregate ICD metrics across all snapshots by model
                        model_icd_stats = {}
                        
                        for snapshot in snapshots:
                            model = snapshot.get('model_version', 'Unknown')
                            snap_metrics = snapshot.get('metrics', snapshot)
                            snap_icd_val = snap_metrics.get('icd_validation', {})
                            snap_scenario_results = snap_metrics.get('scenario_results', [])
                            
                            if snap_icd_val.get('total', 0) > 0:
                                if model not in model_icd_stats:
                                    model_icd_stats[model] = {
                                        'runs': 0,
                                        'total_tests': 0,
                                        'total_correct': 0,
                                        'error_detection': [],
                                        'false_positives': [],
                                        'specificity': [],
                                        'by_modality': {}
                                    }
                                
                                model_icd_stats[model]['runs'] += 1
                                model_icd_stats[model]['total_tests'] += snap_icd_val.get('total', 0)
                                model_icd_stats[model]['total_correct'] += snap_icd_val.get('correct', 0)
                                
                                # Calculate detailed metrics from scenario results
                                icd_scenarios = [s for s in snap_scenario_results if s.get('validation_type') == 'icd_coding']
                                
                                if icd_scenarios:
                                    errors_detected = 0
                                    errors_total = 0
                                    correct_codes = 0
                                    false_positives = 0
                                    
                                    for scenario in icd_scenarios:
                                        expected = scenario.get('expected', '')
                                        model_response = scenario.get('model_response', '')
                                        
                                        if 'ERROR' in expected:
                                            errors_total += 1
                                            if 'ERROR' in model_response:
                                                errors_detected += 1
                                        else:
                                            correct_codes += 1
                                            if 'ERROR' in model_response:
                                                false_positives += 1
                                    
                                    if errors_total > 0:
                                        model_icd_stats[model]['error_detection'].append(errors_detected / errors_total * 100)
                                    if correct_codes > 0:
                                        model_icd_stats[model]['false_positives'].append(false_positives / correct_codes * 100)
                                        model_icd_stats[model]['specificity'].append((correct_codes - false_positives) / correct_codes * 100)
                                    
                                    # Track by modality
                                    for scenario in icd_scenarios:
                                        modality = scenario.get('modality', 'unknown')
                                        if modality not in model_icd_stats[model]['by_modality']:
                                            model_icd_stats[model]['by_modality'][modality] = {'total': 0, 'correct': 0}
                                        
                                        model_icd_stats[model]['by_modality'][modality]['total'] += 1
                                        if scenario.get('correct', False):
                                            model_icd_stats[model]['by_modality'][modality]['correct'] += 1
                        
                        if model_icd_stats:
                            # Build comparison table
                            comparison_rows = []
                            for model, stats in sorted(model_icd_stats.items()):
                                avg_accuracy = (stats['total_correct'] / stats['total_tests'] * 100) if stats['total_tests'] > 0 else 0
                                avg_error_detection = sum(stats['error_detection']) / len(stats['error_detection']) if stats['error_detection'] else 0
                                avg_false_pos = sum(stats['false_positives']) / len(stats['false_positives']) if stats['false_positives'] else 0
                                avg_specificity = sum(stats['specificity']) / len(stats['specificity']) if stats['specificity'] else 0
                                
                                comparison_rows.append({
                                    'Model': model,
                                    'Runs': stats['runs'],
                                    'ICD Tests': stats['total_tests'],
                                    'Avg Accuracy': f"{avg_accuracy:.1f}%",
                                    'Error Detection': f"{avg_error_detection:.1f}%",
                                    'False Positive': f"{avg_false_pos:.1f}%",
                                    'Specificity': f"{avg_specificity:.1f}%"
                                })
                            
                            comparison_df = pd.DataFrame(comparison_rows)
                            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                            
                            # Visual comparison charts
                            st.markdown("#### 📊 Visual Model Comparison")
                            col_comp1, col_comp2 = st.columns(2)
                            
                            with col_comp1:
                                # Accuracy comparison
                                comparison_df['Accuracy_num'] = comparison_df['Avg Accuracy'].str.rstrip('%').astype(float)
                                fig_model_acc = px.bar(
                                    comparison_df,
                                    x='Model',
                                    y='Accuracy_num',
                                    title='ICD Validation Accuracy by Model',
                                    labels={'Accuracy_num': 'Accuracy (%)'},
                                    color='Model',
                                    text='Accuracy_num'
                                )
                                fig_model_acc.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                                fig_model_acc.update_layout(showlegend=False, yaxis_range=[0, 110])
                                st.plotly_chart(fig_model_acc, use_container_width=True)
                            
                            with col_comp2:
                                # Error detection comparison
                                comparison_df['Error_Detection_num'] = comparison_df['Error Detection'].str.rstrip('%').astype(float)
                                fig_model_err = px.bar(
                                    comparison_df,
                                    x='Model',
                                    y='Error_Detection_num',
                                    title='Error Detection Rate by Model',
                                    labels={'Error_Detection_num': 'Detection Rate (%)'},
                                    color='Model',
                                    text='Error_Detection_num'
                                )
                                fig_model_err.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                                fig_model_err.update_layout(showlegend=False, yaxis_range=[0, 110])
                                st.plotly_chart(fig_model_err, use_container_width=True)
                            
                            # Per-modality model comparison (if we have enough data)
                            st.markdown("#### 🔬 ICD Performance by Model & Modality")
                            
                            # Build modality comparison matrix
                            all_modalities = set()
                            for stats in model_icd_stats.values():
                                all_modalities.update(stats['by_modality'].keys())
                            
                            modality_comp_rows = []
                            for model, stats in sorted(model_icd_stats.items()):
                                row = {'Model': model}
                                for modality in sorted(all_modalities):
                                    mod_stats = stats['by_modality'].get(modality, {'total': 0, 'correct': 0})
                                    if mod_stats['total'] > 0:
                                        accuracy = mod_stats['correct'] / mod_stats['total'] * 100
                                        row[modality.title()] = f"{accuracy:.1f}%"
                                    else:
                                        row[modality.title()] = "N/A"
                                modality_comp_rows.append(row)
                            
                            if modality_comp_rows:
                                modality_comp_df = pd.DataFrame(modality_comp_rows)
                                st.dataframe(modality_comp_df, use_container_width=True, hide_index=True)
                                
                                # Recommendation based on data
                                best_model = max(model_icd_stats.items(), 
                                               key=lambda x: x[1]['total_correct'] / x[1]['total_tests'] if x[1]['total_tests'] > 0 else 0)
                                best_model_name = best_model[0]
                                best_accuracy = (best_model[1]['total_correct'] / best_model[1]['total_tests'] * 100) if best_model[1]['total_tests'] > 0 else 0
                                
                                st.success(f"🏆 **Best ICD Validation Performance**: `{best_model_name}` with {best_accuracy:.1f}% accuracy")
                                
                                # Methodology Accordion for Model Comparison
                                with st.expander("📊 Analysis Methodology & Sample Sizes"):
                                    st.markdown("**Data Source:**")
                                    st.markdown(f"- Aggregated from {len(snapshots)} most recent validation runs")
                                    st.markdown(f"- Time range: Last 30 days")
                                    st.markdown(f"- Models analyzed: {len(model_icd_stats)}")
                                    
                                    st.markdown("**Sample Sizes by Model:**")
                                    for model, stats in sorted(model_icd_stats.items()):
                                        st.markdown(f"- **{model}**: {stats['runs']} run(s), {stats['total_tests']} total ICD tests")
                                        if stats['by_modality']:
                                            for mod, mod_stats in sorted(stats['by_modality'].items()):
                                                st.markdown(f"  - {mod.title()}: {mod_stats['total']} tests")
                                    
                                    st.markdown("**Calculations:**")
                                    st.markdown("""
                                    - **Avg Accuracy**: Total correct across all runs / Total tests across all runs
                                    - **Error Detection**: Average of error detection rates from each run
                                    - **False Positive**: Average of false positive rates from each run
                                    - **Specificity**: Average of specificity rates from each run
                                    """)
                                    
                                    st.markdown("**Comparison Method:**")
                                    st.markdown("""
                                    - Models are compared across identical ICD validation scenarios
                                    - Each model processes the same medical images and ICD codes
                                    - Rankings based on cumulative performance across all runs
                                    - Best model determined by highest overall accuracy
                                    """)
                        else:
                            st.info("Run benchmarks with multiple models to see comparison data")
                    
                    # Modality Breakdown
                    st.markdown("---")
                    st.subheader("🔬 Performance by Modality")
                    modality_data = metrics.get('modality_breakdown', {})
                    
                    if modality_data:
                        mod_rows = []
                        for mod, stats in modality_data.items():
                            mod_rows.append({
                                'Modality': mod.title(),
                                'Accuracy': f"{stats.get('accuracy', 0) * 100:.1f}%",
                                'Scenarios': stats.get('total_scenarios', 0),
                                'Errors Detected': stats.get('errors_detected', 0),
                                'False Positives': stats.get('false_positives', 0)
                            })
                        
                        mod_df = pd.DataFrame(mod_rows)
                        st.dataframe(mod_df, use_container_width=True, hide_index=True)
                        
                        # Visualize accuracy by modality
                        fig = px.bar(
                            mod_df,
                            x='Modality',
                            y='Accuracy',
                            title='Accuracy by Medical Imaging Modality',
                            labels={'Accuracy': 'Accuracy (%)'},
                            color='Modality'
                        )
                        # Convert "XX.X%" to float for plotting
                        mod_df['Accuracy_num'] = mod_df['Accuracy'].str.rstrip('%').astype(float)
                        fig = px.bar(
                            mod_df,
                            x='Modality',
                            y='Accuracy_num',
                            title='Accuracy by Medical Imaging Modality',
                            labels={'Accuracy_num': 'Accuracy (%)'},
                            color='Modality'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Methodology Accordion for Modality Breakdown
                        with st.expander("📊 Analysis Methodology & Sample Sizes"):
                            st.markdown("**Data Source:**")
                            st.markdown(f"- Latest validation run from current model")
                            st.markdown(f"- Breakdown across {len(modality_data)} imaging modalities")
                            
                            st.markdown("**Sample Sizes by Modality:**")
                            total_across_modalities = 0
                            for mod, stats in sorted(modality_data.items()):
                                total_scenarios = stats.get('total_scenarios', 0)
                                total_across_modalities += total_scenarios
                                errors_detected = stats.get('errors_detected', 0)
                                false_positives = stats.get('false_positives', 0)
                                st.markdown(f"- **{mod.title()}**: {total_scenarios} scenarios")
                                st.markdown(f"  - Errors caught: {errors_detected}")
                                st.markdown(f"  - False positives: {false_positives}")
                                st.markdown(f"  - Accuracy: {stats.get('accuracy', 0) * 100:.1f}%")
                            
                            st.markdown(f"\n**Total scenarios across all modalities**: {total_across_modalities}")
                            
                            st.markdown("**Modality Types:**")
                            st.markdown("""
                            - **X-Ray**: Chest radiographs for respiratory/cardiac conditions
                            - **Histopathology**: Microscopic tissue analysis for cancer detection
                            - **MRI**: Magnetic resonance imaging for soft tissue/brain
                            - **Ultrasound**: Real-time imaging for vascular/organ assessment
                            """)
                            
                            st.markdown("**Purpose:**")
                            st.markdown("""
                            Modality breakdown helps identify:
                            - Which imaging types the model handles best/worst
                            - Where to focus training improvements
                            - Appropriate use cases for production deployment
                            """)
                    else:
                        st.info("No modality breakdown available.")
                    
                    # Historical Trend
                    if len(snapshots) > 1:
                        st.markdown("---")
                        st.subheader("📈 Accuracy Trend (Last 30 Days)")
                        df = pd.DataFrame([
                            {
                                'timestamp': pd.to_datetime(s.get('created_at') or s.get('timestamp')),
                                'accuracy': (s.get('metrics', s).get('accuracy', 0)) * 100,
                                'model': s.get('model_version', 'Unknown')
                            }
                            for s in snapshots
                        ])
                        
                        fig = px.line(
                            df,
                            x='timestamp',
                            y='accuracy',
                            color='model',
                            title='Clinical Validation Accuracy Over Time',
                            labels={'accuracy': 'Accuracy (%)', 'timestamp': 'Date', 'model': 'Model'},
                            markers=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show all models stats
                        st.markdown("---")
                        st.subheader("🤖 Model Comparison")
                        model_stats = df.groupby('model').agg({
                            'accuracy': ['mean', 'min', 'max', 'count']
                        }).round(1)
                        model_stats.columns = ['Avg Accuracy (%)', 'Min (%)', 'Max (%)', '# Runs']
                        st.dataframe(model_stats, use_container_width=True)
                        
                        # Methodology Accordion for Historical Trends
                        with st.expander("📊 Analysis Methodology & Sample Sizes"):
                            st.markdown("**Data Source:**")
                            st.markdown(f"- **Snapshots analyzed**: {len(snapshots)} validation runs")
                            st.markdown(f"- **Time range**: Last 30 days")
                            st.markdown(f"- **Models tracked**: {df['model'].nunique()} unique model(s)")
                            
                            st.markdown("**Sample Sizes by Model:**")
                            for model_name in sorted(df['model'].unique()):
                                model_runs = df[df['model'] == model_name]
                                st.markdown(f"- **{model_name}**: {len(model_runs)} run(s)")
                                st.markdown(f"  - Date range: {model_runs['timestamp'].min().strftime('%Y-%m-%d')} to {model_runs['timestamp'].max().strftime('%Y-%m-%d')}")
                                st.markdown(f"  - Avg accuracy: {model_runs['accuracy'].mean():.1f}%")
                                st.markdown(f"  - Min/Max: {model_runs['accuracy'].min():.1f}% / {model_runs['accuracy'].max():.1f}%")
                            
                            st.markdown("**Trend Analysis:**")
                            st.markdown("""
                            - Each data point represents one complete validation run
                            - Multiple models can be compared simultaneously
                            - Trends help identify:
                              - Model improvement or degradation over time
                              - Consistency and reliability
                              - Impact of model updates or training changes
                            """)
                            
                            st.markdown("**Model Comparison Stats:**")
                            st.markdown("""
                            - **Avg Accuracy**: Mean across all runs for that model
                            - **Min/Max**: Range of performance observed
                            - **# Runs**: Number of validation runs completed
                            - Higher run count = more statistical confidence
                            """)
                    
                    # Cost Impact Analysis
                    st.markdown("---")
                    st.subheader("💰 Cost Impact Analysis")
                    st.markdown(f"""
                    **Total Potential Savings from Detected Errors:** ${metrics.get('total_cost_savings_potential', 0):,.0f}
                    
                    Each detected clinical error prevents unnecessary or inappropriate treatments:
                    - **Unnecessary Antibiotics**: ~$15,000 per case
                    - **Unnecessary Biopsy**: ~$8,000 per case
                    - **Unnecessary Craniotomy**: ~$85,000 per case
                    - **Unnecessary Chemotherapy**: ~$150,000 per case
                    
                    Early AI-assisted detection of billing and clinical errors can save healthcare systems millions annually.
                    """)
                    
                    # Detection Rate Heatmaps
                    st.markdown("---")
                    st.subheader("🎯 Detection Performance by Modality")
                    st.markdown("Detection accuracy for true positives (valid treatments) and true negatives (inappropriate treatments) across imaging modalities.")
                    
                    # Load latest clinical validation results to build heatmaps
                    results_dir = PROJECT_ROOT / 'benchmarks/clinical_validation_results'
                    
                    if results_dir.exists():
                        try:
                            import numpy as np
                            from collections import defaultdict
                            
                            # Load latest results for each model
                            models = ['gpt-4o-mini', 'gpt-4o', 'medgemma', 'medgemma-ensemble']
                            modalities = ['xray', 'histopathology', 'mri', 'ultrasound']
                            
                            model_results = {}
                            for model in models:
                                model_files = sorted(results_dir.glob(f'{model}_*.json'), reverse=True)
                                if model_files:
                                    import json
                                    with open(model_files[0], 'r') as f:
                                        model_results[model] = json.load(f)
                            
                            if model_results:
                                # Calculate detection rates
                                tp_rates = defaultdict(lambda: defaultdict(lambda: {'correct': 0, 'total': 0}))
                                tn_rates = defaultdict(lambda: defaultdict(lambda: {'correct': 0, 'total': 0}))
                                
                                for model, data in model_results.items():
                                    for scenario in data.get('scenario_results', []):
                                        modality = scenario['modality']
                                        expected = scenario['expected'].upper()
                                        is_correct = scenario.get('correct', False)
                                        
                                        is_positive_case = 'CORRECT' in expected
                                        is_negative_case = 'ERROR' in expected
                                        
                                        if is_positive_case:
                                            tp_rates[model][modality]['total'] += 1
                                            if is_correct:
                                                tp_rates[model][modality]['correct'] += 1
                                        elif is_negative_case:
                                            tn_rates[model][modality]['total'] += 1
                                            if is_correct:
                                                tn_rates[model][modality]['correct'] += 1
                                
                                # Build matrices
                                available_models = [m for m in models if m in model_results]
                                
                                def rates_to_matrix(rates, models_list, modalities_list):
                                    matrix = []
                                    for model in models_list:
                                        row = []
                                        for modality in modalities_list:
                                            stats = rates[model][modality]
                                            if stats['total'] > 0:
                                                row.append((stats['correct'] / stats['total']) * 100)
                                            else:
                                                row.append(None)
                                        matrix.append(row)
                                    return matrix
                                
                                tp_matrix = rates_to_matrix(tp_rates, available_models, modalities)
                                tn_matrix = rates_to_matrix(tn_rates, available_models, modalities)
                                
                                # Display heatmaps side by side
                                col_tp, col_tn = st.columns(2)
                                
                                with col_tp:
                                    st.markdown("**True Positive Detection**")
                                    st.caption("Correctly identifying valid treatments")
                                    
                                    # Create DataFrame for display
                                    tp_df = pd.DataFrame(
                                        tp_matrix,
                                        index=[m.upper() for m in available_models],
                                        columns=[m.title() for m in modalities]
                                    )
                                    
                                    fig_tp = px.imshow(
                                        tp_df.values,
                                        labels=dict(x="Modality", y="Model", color="Rate (%)"),
                                        x=tp_df.columns,
                                        y=tp_df.index,
                                        color_continuous_scale='RdYlGn',
                                        aspect='auto',
                                        text_auto='.0f',
                                        zmin=0,
                                        zmax=100
                                    )
                                    fig_tp.update_layout(
                                        height=max(300, len(available_models) * 60),
                                        xaxis={'side': 'bottom'},
                                        yaxis={'side': 'left'}
                                    )
                                    st.plotly_chart(fig_tp, use_container_width=True, key="tp_heatmap")
                                
                                with col_tn:
                                    st.markdown("**True Negative Detection**")
                                    st.caption("Correctly identifying inappropriate treatments")
                                    
                                    # Create DataFrame for display
                                    tn_df = pd.DataFrame(
                                        tn_matrix,
                                        index=[m.upper() for m in available_models],
                                        columns=[m.title() for m in modalities]
                                    )
                                    
                                    fig_tn = px.imshow(
                                        tn_df.values,
                                        labels=dict(x="Modality", y="Model", color="Rate (%)"),
                                        x=tn_df.columns,
                                        y=tn_df.index,
                                        color_continuous_scale='RdYlGn',
                                        aspect='auto',
                                        text_auto='.0f',
                                        zmin=0,
                                        zmax=100
                                    )
                                    fig_tn.update_layout(
                                        height=max(300, len(available_models) * 60),
                                        xaxis={'side': 'bottom'},
                                        yaxis={'side': 'left'}
                                    )
                                    st.plotly_chart(fig_tn, use_container_width=True, key="tn_heatmap")
                                
                                # Summary statistics
                                st.markdown("**Summary:**")
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    # Best TP modality
                                    tp_avg = np.nanmean(tp_df.values, axis=0)
                                    best_tp_idx = np.nanargmax(tp_avg)
                                    st.metric(
                                        "Best Valid Treatment Detection",
                                        tp_df.columns[best_tp_idx],
                                        f"{tp_avg[best_tp_idx]:.0f}% avg"
                                    )
                                
                                with col2:
                                    # Best TN modality
                                    tn_avg = np.nanmean(tn_df.values, axis=0)
                                    best_tn_idx = np.nanargmax(tn_avg)
                                    st.metric(
                                        "Best Error Detection",
                                        tn_df.columns[best_tn_idx],
                                        f"{tn_avg[best_tn_idx]:.0f}% avg"
                                    )
                                
                                # Add methodology accordion
                                with st.expander("📊 Analysis Methodology & Sample Sizes"):
                                    st.markdown("""
                                    **Data Source:**
                                    - Latest clinical validation benchmark results per model
                                    - Results loaded from `benchmarks/clinical_validation_results/*.json`
                                    - Models analyzed: `gpt-4o-mini`, `gpt-4o`, `medgemma`, `medgemma-ensemble`
                                    - Modalities tested: X-ray, Histopathology, MRI, Ultrasound
                                    
                                    **Sample Sizes:**
                                    - **48 total clinical scenarios** (24 treatment matching + 24 ICD-10 coding)
                                    - **4 modalities per scenario** (192 total modality-specific validations)
                                    - **12 scenarios per modality** (6 treatment + 6 ICD per modality)
                                    - Each model × modality cell represents performance on 12 clinical scenarios
                                    
                                    **Calculations:**
                                    - **TP (True Positive) Rate**: Percentage of valid treatments correctly identified as appropriate
                                      - Formula: `(Correctly approved treatments / Total valid treatments) × 100`
                                      - High TP = Good at recognizing clinically appropriate care
                                    - **TN (True Negative) Rate**: Percentage of inappropriate treatments correctly flagged as errors
                                      - Formula: `(Correctly flagged errors / Total inappropriate treatments) × 100`
                                      - High TN = Good at catching billing errors and overtreatment
                                    - **Color Scale**: 🟢 Green (high) → 🟡 Yellow (moderate) → 🔴 Red (low)
                                    
                                    **Analysis Methodology:**
                                    1. Load latest validation results for each model from benchmark result files
                                    2. Extract `scenario_results` array containing per-scenario validation outcomes
                                    3. Filter for scenarios matching each modality (xray, histopathology, mri, ultrasound)
                                    4. Calculate TP rate: Count scenarios where valid treatment was correctly approved
                                    5. Calculate TN rate: Count scenarios where inappropriate treatment was correctly flagged
                                    6. Build 4×4 heatmap matrices (4 models × 4 modalities) for TP and TN separately
                                    7. Use `np.nanmean()` to handle missing data points gracefully
                                    
                                    **Purpose:**
                                    - **Identify Model Strengths**: Which models excel at specific imaging modalities?
                                    - **Optimize Model Selection**: Route X-ray cases to best X-ray model, etc.
                                    - **Balance TP vs TN**: Some models may prioritize catching errors (high TN) over approving valid care (TP)
                                    - **Training Priorities**: Low-scoring cells indicate where models need improvement
                                    - **Real-World Application**: Informs deployment strategy for production traffic routing
                                    
                                    **Interpretation Guide:**
                                    - **High TP + High TN** (both green): Ideal - model is clinically accurate
                                    - **High TP + Low TN** (green/red): Approves everything - misses billing errors
                                    - **Low TP + High TN** (red/green): Too conservative - denies valid treatments
                                    - **Low TP + Low TN** (both red): Model struggles with this modality - needs retraining
                                    
                                    **Clinical Validation Scenarios:**
                                    - Treatment scenarios test appropriate vs inappropriate interventions
                                    - ICD-10 scenarios validate correct diagnostic code assignment
                                    - Each scenario includes: patient history, imaging findings, proposed treatment, expected outcome
                                    - Scenarios span: Emergency care, chronic conditions, preventive care, procedural codes
                                    """)
                                
                            else:
                                st.info("No detailed results available for heatmap generation. Run benchmarks to collect data.")
                        
                        except Exception as hm_error:
                            st.warning(f"Could not generate heatmaps: {hm_error}")
                            import traceback
                            with st.expander("Show Error Details"):
                                st.code(traceback.format_exc())
                    else:
                        st.info("Results directory not found. Run clinical validation benchmarks first.")
                    
                else:
                    st.info("📊 No clinical validation data available yet. Benchmarks run daily at midnight UTC.")
                    st.markdown("""
                    **Clinical Validation Benchmarks Test:**
                    - 🩺 Multi-modal medical imaging (X-ray, MRI, Histopathology, Ultrasound)
                    - ⚠️ Error detection scenarios (overtreatment, unnecessary procedures)
                    - ✅ Correct treatment validation
                    - 💰 Cost impact analysis
                    
                    Results will appear here after the first automated run.
                    """)
            
            except Exception as e:
                st.error(f"Error loading clinical validation data: {e}")
                import traceback
                with st.expander("Show Error Details"):
                    st.code(traceback.format_exc())
        
        # Clinical Data Sets Section (always show, regardless of beta_data_access)
        st.markdown("---")
        with st.expander("📚 Clinical Data Sets", expanded=False):
            st.markdown("""
            Medical images used in clinical validation benchmarks. All images are sourced from 
            publicly available Kaggle datasets with proper attribution and licensing.
            """)
            
            # Load manifest
            manifest_path = PROJECT_ROOT / 'benchmarks/clinical_images/kaggle_datasets/selected/manifest.json'
            images_dir = PROJECT_ROOT / 'benchmarks/clinical_images/kaggle_datasets/selected'
            
            if manifest_path.exists():
                try:
                    with open(manifest_path) as f:
                        manifest = json.load(f)
                    
                    st.markdown(f"**Total Images:** {manifest.get('total_images', 0)} | "
                               f"**Modalities:** {', '.join([m.title() for m in manifest.get('modalities', [])])}")
                    st.markdown("---")
                    
                    # Create table with thumbnails
                    for img_data in manifest.get('images', []):
                        col1, col2, col3 = st.columns([1, 3, 1])
                        
                        with col1:
                            # Display thumbnail
                            img_path = images_dir / img_data['filename']
                            if img_path.exists():
                                try:
                                    import PIL.Image
                                    img = PIL.Image.open(img_path)
                                    
                                    # Create a unique key for modal
                                    modal_key = f"modal_{img_data['filename'].replace('.', '_')}"
                                    
                                    # Display small thumbnail (clickable)
                                    st.image(img, width=100, use_container_width=False)
                                    
                                    # Modal button
                                    if st.button("🔍 View Full", key=f"btn_{modal_key}"):
                                        st.session_state[modal_key] = True
                                    
                                    # Modal dialog with full width
                                    if st.session_state.get(modal_key, False):
                                        # Use dialog for full-width modal
                                        @st.dialog(f"🔍 {img_data['filename']}", width="large")
                                        def show_full_image():
                                            st.image(img, use_container_width=True)
                                            
                                            # Attribution caption
                                            st.caption(f"""
                                            **Source:** {img_data.get('dataset', img_data.get('dataset_name', 'Unknown'))}  
                                            **License:** {img_data.get('license', 'Unknown')}  
                                            **URL:** {img_data.get('dataset_url', 'N/A')}  
                                            **Citation:** {img_data.get('citation', 'N/A')}
                                            """)
                                            
                                            # Clinical Scenarios Sub-Accordions
                                            scenarios = img_data.get('scenarios', [])
                                            if scenarios:
                                                st.markdown("---")
                                                st.markdown("### 📋 Associated Clinical Scenarios")
                                                st.caption(f"{len(scenarios)} validation scenario(s) using this image")
                                                
                                                for idx, scenario in enumerate(scenarios, 1):
                                                    scenario_key = f"{modal_key}_scenario_{idx}"
                                                    with st.expander(f"📝 Scenario {idx}: {scenario.get('scenario_id', 'Unknown')}", expanded=False):
                                                        col_s1, col_s2 = st.columns([1, 1])
                                                        
                                                        with col_s1:
                                                            st.markdown("**📊 Scenario Details**")
                                                            st.markdown(f"**ID:** `{scenario.get('scenario_id', 'N/A')}`")
                                                            st.markdown(f"**Type:** {scenario.get('validation_type', 'N/A').replace('_', ' ').title()}")
                                                            st.markdown(f"**Modality:** {scenario.get('modality', 'N/A').title()}")
                                                            st.markdown(f"**Image Type:** {scenario.get('image_type', 'N/A').title()}")
                                                            
                                                            if scenario.get('error_type') and scenario.get('error_type') != 'none':
                                                                st.markdown(f"**Error Type:** {scenario.get('error_type', 'N/A').replace('_', ' ').title()}")
                                                                st.markdown(f"**Severity:** {scenario.get('severity', 'N/A').title()}")
                                                                st.markdown(f"**Cost Impact:** ${scenario.get('cost_impact', 0):,}")
                                                        
                                                        with col_s2:
                                                            st.markdown("**👤 Patient Context**")
                                                            patient = scenario.get('patient_context', {})
                                                            if patient:
                                                                st.markdown(f"**Age:** {patient.get('age', 'N/A')}")
                                                                st.markdown(f"**Gender:** {patient.get('gender', 'N/A')}")
                                                                st.markdown(f"**Chief Complaint:** {patient.get('chief_complaint', 'N/A')}")
                                                                vital_signs = patient.get('vital_signs') or patient.get('biopsy_site', 'N/A')
                                                                st.markdown(f"**Vital Signs:** {vital_signs}")
                                                        
                                                        st.markdown("---")
                                                        st.markdown("**🔬 Clinical Finding**")
                                                        st.info(scenario.get('clinical_finding', 'N/A'))
                                                        
                                                        st.markdown("**💊 Prescribed Treatment**")
                                                        st.warning(scenario.get('prescribed_treatment', 'N/A'))
                                                        
                                                        st.markdown("**✅ Expected Determination**")
                                                        expected = scenario.get('expected_determination', 'N/A')
                                                        if 'ERROR' in expected:
                                                            st.error(expected)
                                                        else:
                                                            st.success(expected)
                                                        
                                                        # ICD scenarios have different structure
                                                        if scenario.get('validation_type') == 'icd_coding':
                                                            st.markdown("---")
                                                            st.markdown("**🏥 ICD-10 Codes**")
                                                            
                                                            col_icd1, col_icd2 = st.columns(2)
                                                            with col_icd1:
                                                                st.markdown("**Diagnosis:**")
                                                                st.code(scenario.get('diagnosis', 'N/A'))
                                                            
                                                            with col_icd2:
                                                                st.markdown("**Provided ICD Code:**")
                                                                icd_code = scenario.get('icd_code', scenario.get('provided_icd_code', 'N/A'))
                                                                icd_desc = scenario.get('icd_description', '')
                                                                
                                                                # Color based on whether it's correct or error
                                                                if 'ERROR' in scenario.get('expected_determination', ''):
                                                                    st.error(f"❌ {icd_code}")
                                                                    if icd_desc:
                                                                        st.caption(icd_desc)
                                                                    if scenario.get('correct_code'):
                                                                        st.caption(f"✅ Correct: {scenario.get('correct_code')}")
                                                                else:
                                                                    st.success(f"✅ {icd_code}")
                                                                    if icd_desc:
                                                                        st.caption(icd_desc)
                                        
                                        # Call the dialog function
                                        show_full_image()
                                        # Reset state after dialog closes
                                        st.session_state[modal_key] = False
                                
                                except Exception as e:
                                    st.error(f"Could not load image: {e}")
                            else:
                                st.warning("Image not found")
                        
                        with col2:
                            # Description
                            st.markdown(f"**{img_data['filename']}**")
                            st.markdown(f"**Modality:** {img_data['modality'].title()}")
                            st.markdown(f"**Diagnosis:** {img_data['diagnosis'].title()}")
                            st.markdown(f"**Dataset:** {img_data.get('dataset', img_data.get('dataset_name', 'Unknown'))}")
                            
                            with st.expander("📄 Full Attribution"):
                                st.markdown(f"""
                                **Dataset Name:** {img_data.get('dataset', img_data.get('dataset_name', 'N/A'))}  
                                **License:** {img_data.get('license', 'N/A')}  
                                **Dataset URL:** [{img_data.get('dataset_url', 'N/A')}]({img_data.get('dataset_url', '#')})  
                                **Citation:** {img_data.get('citation', 'N/A')}  
                                **Source File:** `{img_data.get('source_file', 'N/A')}`
                                """)
                        
                        with col3:
                            # Quick stats
                            st.metric("Class", img_data['diagnosis'].upper())
                        
                        st.markdown("---")
                    
                except Exception as e:
                    st.error(f"Error loading manifest: {e}")
                    import traceback
                    with st.expander("Show Error Details"):
                        st.code(traceback.format_exc())
            else:
                st.warning(f"""
                📁 Manifest file not found at: `{manifest_path}`
                
                Run the download script to fetch clinical images:
                ```bash
                python3 scripts/download_kaggle_medical_images.py --select-images
                ```
                """)
        
        if not beta_data_access:
            st.warning("""
            ### 🔧 Configuration Required
            
            Clinical validation dashboard is unavailable. Please configure:
            - `SUPABASE_BETA_KEY`: API key for beta database
            - `SUPABASE_BETA_URL`: Database URL (default: https://zrhlpitzonhftigmdvgz.supabase.co)
            
            Add these to your `.env` file or environment variables.
            """)

# ============================================================================
# TAB 1: System Health Overview
# ============================================================================

with tab1:
    st.header("📊 System Health Overview")
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def load_snapshots(environment):
        return data_access.get_latest_snapshots(environment=environment)
    
    snapshots_df = load_snapshots(env_filter)
    
    if snapshots_df.empty:
        st.warning("No benchmark data available.")
    else:
        # Cost Savings Summary (Top Banner)
        if 'metrics' in snapshots_df.columns:
            # Parse metrics to get savings data
            def extract_savings(metrics_json):
                if isinstance(metrics_json, str):
                    import json
                    metrics = json.loads(metrics_json)
                else:
                    metrics = metrics_json
                return {
                    'potential_savings': metrics.get('total_potential_savings', 0),
                    'savings_capture_rate': metrics.get('savings_capture_rate', 0),
                    'roi_ratio': metrics.get('roi_ratio', 0)
                }
            
            savings_data = snapshots_df['metrics'].apply(extract_savings)
            total_savings = sum(s['potential_savings'] for s in savings_data)
            avg_capture = sum(s['savings_capture_rate'] for s in savings_data if s['savings_capture_rate'] > 0) / max(len([s for s in savings_data if s['savings_capture_rate'] > 0]), 1)
            avg_roi = sum(s['roi_ratio'] for s in savings_data if s['roi_ratio'] > 0) / max(len([s for s in savings_data if s['roi_ratio'] > 0]), 1)
            
            if total_savings > 0:
                st.info("💰 **Cost Savings Impact**: These models have identified **$" + f"{total_savings:,.2f}" + f"** in potential billing errors across all benchmark runs (avg {avg_capture:.1f}% capture rate, {avg_roi:.0f}x ROI)")
        
        # Performance Metrics Row
        st.markdown("### 📊 Performance Metrics")
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
        
        # Top performers with cost savings
        col1, col2, col3 = st.columns(3)
        
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
        
        with col3:
            st.subheader("💰 Top Cost Savers")
            # Extract savings from metrics
            if 'metrics' in snapshots_df.columns:
                savings_list = []
                for _, row in snapshots_df.iterrows():
                    metrics = row['metrics']
                    if isinstance(metrics, str):
                        import json
                        metrics = json.loads(metrics)
                    potential_savings = metrics.get('total_potential_savings', 0)
                    if potential_savings > 0:
                        savings_list.append({
                            'Model': row['model_version'],
                            'Potential Savings': f"${potential_savings:,.0f}",
                            'Capture Rate': f"{metrics.get('savings_capture_rate', 0):.1f}%"
                        })
                
                if savings_list:
                    savings_df = pd.DataFrame(savings_list).sort_values('Potential Savings', ascending=False).head(5)
                    st.dataframe(savings_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No cost savings data available")
            else:
                st.info("No cost savings data available")
        
        st.markdown("---")
        
        # Full snapshot table
        st.subheader("📋 All Active Configurations")
        
        # Format display - select available columns
        base_cols = [
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
        ]
        
        # Add triggered_by if available
        if 'triggered_by' in snapshots_df.columns:
            base_cols.insert(-1, 'triggered_by')  # Insert before created_at
        
        display_df = snapshots_df[base_cols].copy()
        display_df['created_at'] = display_df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
        
        column_config = {
            "f1_score": st.column_config.NumberColumn("F1", format="%.4f"),
            "precision_score": st.column_config.NumberColumn("Precision", format="%.4f"),
            "recall_score": st.column_config.NumberColumn("Recall", format="%.4f"),
            "latency_ms": st.column_config.NumberColumn("Latency (ms)", format="%.0f"),
            "cost_per_analysis": st.column_config.NumberColumn("Cost", format="$%.4f"),
        }
        
        if 'triggered_by' in snapshots_df.columns:
            column_config["triggered_by"] = st.column_config.TextColumn("Triggered By", width="medium")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config=column_config
        )

# ============================================================================
# TAB 2: Reliability Over Time
# ============================================================================

with tab2:
    st.header("📈 Reliability Over Time")
    
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
            
            # Cost Savings Trends (if data available)
            @st.cache_data(ttl=300)
            def load_cost_savings_timeseries(model, days, environment):
                start_date = datetime.now() - timedelta(days=days)
                df = data_access.get_transactions(start_date=start_date, environment=environment)
                if df.empty or 'total_patients' not in df.columns:
                    return None
                
                model_df = df[df['model_version'] == model].copy()
                if model_df.empty or 'total_potential_savings' not in model_df.columns:
                    return None
                
                return model_df[['created_at', 'total_potential_savings', 'savings_capture_rate', 'avg_savings_per_patient']].sort_values('created_at')
            
            savings_ts = load_cost_savings_timeseries(model_version, days_back, env_filter)
            
            if savings_ts is not None and not savings_ts.empty:
                st.subheader("💰 Cost Savings Trends")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=savings_ts['created_at'],
                        y=savings_ts['total_potential_savings'],
                        mode='lines+markers',
                        name='Potential Savings',
                        line=dict(color='green', width=2),
                        marker=dict(size=8)
                    ))
                    fig.update_layout(
                        title="Potential Savings Over Time",
                        xaxis_title="Date",
                        yaxis_title="Amount ($)",
                        height=350
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"savings_trend_{model_version}")
                
                with col2:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=savings_ts['created_at'],
                        y=savings_ts['savings_capture_rate'],
                        mode='lines+markers',
                        name='Capture Rate',
                        line=dict(color='blue', width=2),
                        marker=dict(size=8)
                    ))
                    fig.update_layout(
                        title="Savings Capture Rate Over Time",
                        xaxis_title="Date",
                        yaxis_title="Capture Rate (%)",
                        height=350
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"capture_trend_{model_version}")
            
            # Error Category Performance Trends
            @st.cache_data(ttl=300)
            def load_error_category_timeseries(model, days, environment):
                """Load error category performance over time from snapshots."""
                # Get snapshots for this model
                all_snapshots = data_access.get_snapshot_history(
                    model_version=model,
                    dataset_version="patient-benchmark-v2",  # Adjust as needed
                    prompt_version="v2-structured-reasoning",  # Adjust as needed
                    environment=environment or "local",
                    limit=30
                )
                
                if all_snapshots.empty or 'domain_breakdown' not in all_snapshots.columns:
                    return None
                
                # Parse domain_breakdown from each snapshot
                import json
                category_data = []
                for _, row in all_snapshots.iterrows():
                    breakdown = row['domain_breakdown']
                    if isinstance(breakdown, str):
                        breakdown = json.loads(breakdown)
                    
                    if breakdown and isinstance(breakdown, dict):
                        for category, metrics in breakdown.items():
                            category_data.append({
                                'date': row['created_at'],
                                'category': category.replace('_', ' ').title(),
                                'recall': metrics.get('recall', 0) * 100,
                                'precision': metrics.get('precision', 0) * 100,
                                'detected': metrics.get('total_detected', 0),
                                'total': metrics.get('total_cases', 0)
                            })
                
                if not category_data:
                    return None
                
                return pd.DataFrame(category_data)
            
            category_ts = load_error_category_timeseries(model_version, days_back, env_filter)
            
            if category_ts is not None and not category_ts.empty and len(category_ts['date'].unique()) > 1:
                st.subheader("🎯 Error Category Detection Trends")
                
                # Get all unique categories
                all_categories = category_ts['category'].unique()
                
                # Let user select which categories to show
                default_categories = [c for c in all_categories if any(x in c.lower() for x in ['gender', 'age', 'surgical', 'diagnosis', 'procedure'])]
                if not default_categories:
                    default_categories = list(all_categories)[:5]
                
                selected_categories = st.multiselect(
                    "Select Error Categories to Display",
                    options=sorted(all_categories),
                    default=default_categories,
                    key=f"category_select_{model_version}"
                )
                
                if selected_categories:
                    filtered_df = category_ts[category_ts['category'].isin(selected_categories)]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Recall trends
                        fig_recall = px.line(
                            filtered_df,
                            x='date',
                            y='recall',
                            color='category',
                            markers=True,
                            labels={'date': 'Date', 'recall': 'Recall (%)', 'category': 'Error Category'},
                            title="Recall by Error Category Over Time"
                        )
                        fig_recall.update_layout(height=400, hovermode='x unified')
                        fig_recall.update_yaxis(range=[0, 100])
                        st.plotly_chart(fig_recall, use_container_width=True, key=f"recall_trend_{model_version}")
                    
                    with col2:
                        # Precision trends
                        fig_precision = px.line(
                            filtered_df,
                            x='date',
                            y='precision',
                            color='category',
                            markers=True,
                            labels={'date': 'Date', 'precision': 'Precision (%)', 'category': 'Error Category'},
                            title="Precision by Error Category Over Time"
                        )
                        fig_precision.update_layout(height=400, hovermode='x unified')
                        fig_precision.update_yaxis(range=[0, 100])
                        st.plotly_chart(fig_precision, use_container_width=True, key=f"precision_trend_{model_version}")
                    
                    # Show summary stats for selected categories
                    st.markdown("**Latest Performance by Category:**")
                    latest_date = filtered_df['date'].max()
                    latest_perf = filtered_df[filtered_df['date'] == latest_date].sort_values('recall', ascending=False)
                    
                    summary_df = latest_perf[['category', 'recall', 'precision', 'detected', 'total']].copy()
                    summary_df.columns = ['Category', 'Recall %', 'Precision %', 'Detected', 'Total']
                    st.dataframe(
                        summary_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            'Recall %': st.column_config.NumberColumn('Recall %', format="%.1f%%"),
                            'Precision %': st.column_config.NumberColumn('Precision %', format="%.1f%%")
                        }
                    )
            
            st.markdown("---")

# ============================================================================
# TAB 3: Model Effectiveness Comparison
# ============================================================================

with tab3:
    st.header("⚖️ Model Effectiveness Comparison")
    
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
# TAB 4: Performance Stability Monitor
# ============================================================================

with tab4:
    st.header("🚨 Performance Stability Monitor")
    
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
                # Load historical data for this model
                @st.cache_data(ttl=300)
                def load_model_history(model, days):
                    start_date = datetime.now() - timedelta(days=days)
                    df = data_access.get_transactions(
                        model_version=model,
                        start_date=start_date,
                        environment=env_filter
                    )
                    # Return only necessary columns
                    if not df.empty and 'f1' in df.columns:
                        df = df[['created_at', 'f1']].copy()
                        df.rename(columns={'f1': 'f1_score'}, inplace=True)
                        df = df.sort_values('created_at')
                    return df
                
                history_df = load_model_history(model_version, days_back)
                
                if history_df.empty or len(history_df) < 2:
                    st.warning(f"Insufficient data for regression detection. Need at least 2 benchmark runs. Current: {len(history_df)}")
                    continue
                
                # Use statistical baseline: best historical performance or average of top 25%
                sorted_f1 = history_df['f1_score'].sort_values(ascending=False)
                top_25_percent = max(1, len(sorted_f1) // 4)
                baseline_f1 = sorted_f1.head(top_25_percent).mean()
                
                # Current performance is the latest run
                current_f1 = history_df.iloc[-1]['f1_score']
                
                # Calculate drop
                f1_drop = ((baseline_f1 - current_f1) / baseline_f1) * 100 if baseline_f1 > 0 else 0
                is_regression = f1_drop > threshold
                
                # Display status banner
                if is_regression:
                    st.error(f"🚨 **REGRESSION DETECTED** - F1 dropped by {f1_drop:.1f}% (threshold: {threshold}%)")
                else:
                    st.success(f"✅ **NO REGRESSION** - Performance within expected range (drop: {f1_drop:.1f}%)")
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    delta_display = f"{-f1_drop:.2f}%" if f1_drop > 0 else f"+{abs(f1_drop):.2f}%"
                    st.metric(
                        "Current F1 (Latest)",
                        f"{current_f1:.4f}",
                        delta=delta_display,
                        delta_color="inverse",
                        help="Latest benchmark result"
                    )
                
                with col2:
                    st.metric(
                        "Baseline F1 (Top 25%)",
                        f"{baseline_f1:.4f}",
                        help=f"Average of top {top_25_percent} runs out of {len(history_df)} total"
                    )
                
                with col3:
                    st.metric(
                        "Performance Drop",
                        f"{f1_drop:.2f}%",
                        help="Percentage drop from baseline"
                    )
                
                with col4:
                    st.metric(
                        "Total Runs",
                        len(history_df),
                        help="Number of benchmark runs analyzed"
                    )
                
                # Show trend
                st.markdown("**Performance Trend:**")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=history_df['created_at'],
                    y=history_df['f1_score'],
                    mode='lines+markers',
                    name='F1 Score',
                    line=dict(color='#1f77b4')
                ))
                fig.add_hline(
                    y=baseline_f1,
                    line_dash="dash",
                    line_color="green",
                    annotation_text=f"Baseline ({baseline_f1:.4f})"
                )
                fig.add_hline(
                    y=baseline_f1 * (1 - threshold/100),
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Threshold ({baseline_f1 * (1 - threshold/100):.4f})"
                )
                fig.update_layout(
                    height=300,
                    xaxis_title="Date",
                    yaxis_title="F1 Score",
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True, key=f"regression_trend_{model_version}")
                
                if is_regression:
                    st.markdown("**📋 Recommended Actions:**")
                    st.markdown("- 🔍 Review recent code changes")
                    st.markdown("- 📊 Check for data drift or distribution shifts")
                    st.markdown("- ✏️ Verify prompt modifications")
                    st.markdown("- ⚙️ Inspect model configuration and parameters")
                
                # Cost Savings Regression Check
                st.markdown("---")
                st.subheader("💰 Cost Savings Regression")
                
                @st.cache_data(ttl=300)
                def get_cost_savings_history(model):
                    start_date = datetime.now() - timedelta(days=days_back)
                    df = data_access.get_transactions(start_date=start_date, environment=env_filter)
                    if df.empty or 'total_patients' not in df.columns:
                        return None
                    
                    model_df = df[df['model_version'] == model].copy()
                    if model_df.empty or 'total_potential_savings' not in model_df.columns:
                        return None
                    
                    return model_df.sort_values('created_at')
                
                savings_history = get_cost_savings_history(model_version)
                
                if savings_history is not None and len(savings_history) >= 2:
                    latest = savings_history.iloc[-1]
                    previous = savings_history.iloc[-2]
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        current_savings = latest.get('total_potential_savings', 0)
                        prev_savings = previous.get('total_potential_savings', 0)
                        delta_savings = current_savings - prev_savings
                        st.metric(
                            "Current Potential Savings",
                            f"${current_savings:,.2f}",
                            delta=f"${delta_savings:,.2f}"
                        )
                    
                    with col2:
                        current_capture = latest.get('savings_capture_rate', 0)
                        prev_capture = previous.get('savings_capture_rate', 0)
                        delta_capture = current_capture - prev_capture
                        st.metric(
                            "Capture Rate",
                            f"{current_capture:.1f}%",
                            delta=f"{delta_capture:+.1f}%"
                        )
                    
                    with col3:
                        current_avg = latest.get('avg_savings_per_patient', 0)
                        prev_avg = previous.get('avg_savings_per_patient', 0)
                        delta_avg = current_avg - prev_avg
                        st.metric(
                            "Avg Savings/Patient",
                            f"${current_avg:,.2f}",
                            delta=f"${delta_avg:,.2f}"
                        )
                    
                    with col4:
                        current_missed = latest.get('total_missed_savings', 0)
                        prev_missed = previous.get('total_missed_savings', 0)
                        delta_missed = current_missed - prev_missed
                        st.metric(
                            "Missed Savings",
                            f"${current_missed:,.2f}",
                            delta=f"${delta_missed:,.2f}",
                            delta_color="inverse"
                        )
                    
                    # Alert on savings regression
                    if delta_capture < -5.0:  # More than 5% drop in capture rate
                        st.warning(f"⚠️ Savings capture rate dropped by {abs(delta_capture):.1f}% - ROI declining")
                    elif delta_savings < 0 and abs(delta_savings) > 1000:
                        st.warning(f"⚠️ Potential savings decreased by ${abs(delta_savings):,.2f}")
                    else:
                        st.success("✅ Cost savings metrics stable or improving")
                else:
                    st.info("Run more benchmarks to track cost savings regressions over time")
                
                # Error Category Performance Regression
                st.markdown("---")
                st.subheader("🎯 Error Category Performance Regression")
                
                @st.cache_data(ttl=300)
                def get_category_performance_history(model):
                    # Get latest snapshots for this model
                    df = data_access.get_latest_snapshots(environment=env_filter)
                    if df.empty:
                        return None
                    
                    model_df = df[df['model_version'] == model].copy()
                    if model_df.empty or 'domain_breakdown' not in model_df.columns:
                        return None
                    
                    # Parse domain_breakdown JSONB
                    import json
                    if isinstance(model_df['domain_breakdown'].iloc[0], str):
                        breakdown = json.loads(model_df['domain_breakdown'].iloc[0])
                    else:
                        breakdown = model_df['domain_breakdown'].iloc[0]
                    
                    if not breakdown:
                        return None
                    
                    return breakdown
                
                category_perf = get_category_performance_history(model_version)
                
                if category_perf:
                    st.markdown("**Recall by Error Category:**")
                    
                    # Create a dataframe for display
                    category_data = []
                    for category, metrics in category_perf.items():
                        recall = metrics.get('recall', 0) * 100
                        detected = metrics.get('total_detected', 0)
                        total = metrics.get('total_cases', 0)
                        category_data.append({
                            'Category': category.replace('_', ' ').title(),
                            'Recall %': recall,
                            'Detected': detected,
                            'Total': total,
                            'Status': '✅' if recall >= 80 else ('⚠️' if recall >= 50 else '❌')
                        })
                    
                    category_df = pd.DataFrame(category_data).sort_values('Recall %', ascending=False)
                    
                    # Display table
                    st.dataframe(
                        category_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            'Recall %': st.column_config.NumberColumn('Recall %', format="%.1f%%"),
                            'Detected': st.column_config.NumberColumn('Detected', format="%d"),
                            'Total': st.column_config.NumberColumn('Total Cases', format="%d")
                        }
                    )
                    
                    # Alert on low-performing categories
                    low_performing = category_df[category_df['Recall %'] < 30]
                    if not low_performing.empty:
                        st.error(f"🚨 **{len(low_performing)} categories below 30% recall:**")
                        for _, row in low_performing.iterrows():
                            st.markdown(f"- **{row['Category']}**: {row['Recall %']:.1f}% ({row['Detected']}/{row['Total']})")
                    
                    # Visual chart
                    fig = px.bar(
                        category_df,
                        x='Recall %',
                        y='Category',
                        orientation='h',
                        text='Recall %',
                        title="Recall Performance by Error Category",
                        color='Recall %',
                        color_continuous_scale=['red', 'yellow', 'green'],
                        range_color=[0, 100]
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig.update_layout(height=400, xaxis_title="Recall (%)", yaxis_title="")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No error category breakdown available. Re-run model benchmarks to track category performance.")

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
        
        # Get latest snapshot for this model to determine dataset/prompt versions
        latest_snapshots = data_access.get_latest_snapshots(environment=env_filter)
        model_snapshot = latest_snapshots[latest_snapshots['model_version'] == selected_model_history]
        
        if model_snapshot.empty:
            st.warning(f"No snapshots found for {selected_model_history}")
            history_df = pd.DataFrame()
        else:
            # Use actual dataset and prompt versions from the model's snapshots
            dataset_version = model_snapshot.iloc[0]['dataset_version']
            prompt_version = model_snapshot.iloc[0]['prompt_version']
            
            # Get snapshot history for selected model
            history_df = data_access.get_snapshot_history(
                model_version=selected_model_history,
                dataset_version=dataset_version,
                prompt_version=prompt_version,
                environment=env_filter or "local",  # Default to local if no filter
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
                'latency_ms', 'created_at_display'
            ]
            
            # Add triggered_by if available
            if 'triggered_by' in display_history.columns:
                display_cols.append('triggered_by')
            
            # Add commit_sha if available
            if 'commit_sha' in display_history.columns:
                display_cols.append('commit_sha')
            
            column_config = {
                "version": "Version",
                "status": "Status",
                "f1_score": st.column_config.NumberColumn("F1", format="%.4f"),
                "precision_score": st.column_config.NumberColumn("Precision", format="%.4f"),
                "recall_score": st.column_config.NumberColumn("Recall", format="%.4f"),
                "latency_ms": st.column_config.NumberColumn("Latency (ms)", format="%.0f"),
                "created_at_display": "Created At",
            }
            
            if 'triggered_by' in display_history.columns:
                column_config["triggered_by"] = st.column_config.TextColumn("Triggered By", width="medium")
            
            if 'commit_sha' in display_history.columns:
                column_config["commit_sha"] = st.column_config.TextColumn("Commit", width="small")
            
            st.dataframe(
                display_history[display_cols],
                use_container_width=True,
                column_config=column_config
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
# TAB 6: Clinical Reasoning Evaluation (Cross-Document Domain Knowledge)
# ============================================================================

with tab6:
    st.header("🏥 Clinical Reasoning Evaluation (Cross-Document Analysis)")
    st.markdown("""
    **Domain Knowledge Detection:** Testing models' ability to identify gender/age-inappropriate 
    medical procedures that require healthcare domain knowledge (e.g., male patient billed for 
    pregnancy ultrasound, 8-year-old billed for colonoscopy).
    """)
    
    # Methodology accordion
    with st.expander("📐 Methodology: Healthcare Effectiveness Score (HES)", expanded=False):
        st.markdown("""
        **Healthcare Effectiveness Score (HES)** is a composite metric designed specifically for medical billing 
        compliance, prioritizing error detection over false positives.
        
        **Formula:**
        ```
        HES = (Recall × 60%) + (F1 × 15%) + (ROI × 10%) + (Savings Capture × 10%) + (Stability × 5%)
              - Failure Penalty - Low-Run Penalty
        ```
        
        **Component Weights:**
        - **Recall (60%)** - PRIMARY: Error detection rate. Missing billing errors (false negatives) is 
          more expensive than flagging legitimate bills for review (false positives)
        - **F1 Score (15%)** - Balanced performance (precision + recall)
        - **ROI (10%)** - Efficiency: Total savings ÷ Latency (value per time unit)
        - **Savings Capture (10%)** - Financial impact: % of potential savings actually captured
        - **Stability (5%)** - Performance consistency across runs (1 - standard deviation of F1)
        
        **Penalties:**
        - **Failure Penalty:** Failure Rate × 25% (deducts for failed analyses)
        - **Low-Run Penalty:** 0.15 if fewer than 2 benchmark runs (insufficient data)
        
        **Failure Rate Calculation:**
        ```
        Failure Rate = (Total Patients - Successful Analyses) ÷ Total Patients
        ```
        - Displayed as N/A if insufficient data (total_patients = 0)
        - Only calculated when valid data is available
        
        **Sample Sizes:**
        - Patient cross-document benchmarks typically test 10-50 synthetic patient profiles
        - Each profile contains 3-8 receipts from different providers/dates
        - Models must detect age/gender-inappropriate procedures across documents
        
        **Test Design:**
        - Profiles designed with domain knowledge violations (e.g., male pregnancy ultrasound)
        - Tests medical reasoning, not just receipt parsing
        - Requires cross-document context aggregation
        
        **Why Prioritize Recall?**
        In healthcare billing compliance:
        - **Missing a fraudulent bill costs $1,000-$50,000+** (the fraudulent charge goes through)
        - **Flagging a legitimate bill for review costs $5-$50** (human review time)
        - Therefore, false negatives are 100-1000× more expensive than false positives
        - High recall (catching all errors) is critical even if it means more false positives
        """)
    
    st.markdown("---")
    
    @st.cache_data(ttl=300)
    def load_patient_benchmarks():
        """Load patient benchmark results from snapshots table."""
        # Get latest snapshots (current versions only)
        df = data_access.get_latest_snapshots(environment=env_filter)
        
        if df.empty:
            return pd.DataFrame()
        
        # Filter to only model benchmarks (have domain_knowledge_detection_rate in metrics)
        # Parse metrics JSONB if needed
        if 'metrics' in df.columns:
            import json
            if df['metrics'].dtype == 'object':
                # Expand metrics JSONB into columns
                metrics_expanded = df['metrics'].apply(lambda x: x if isinstance(x, dict) else json.loads(x) if isinstance(x, str) else {})
                metrics_df = pd.json_normalize(metrics_expanded)
                # Drop metrics column and add expanded columns
                df = df.drop('metrics', axis=1)
                # Only add columns that don't already exist
                for col in metrics_df.columns:
                    if col not in df.columns:
                        df[col] = metrics_df[col]
        
        # Check if this is model benchmark data (has domain metrics)
        if 'domain_knowledge_detection_rate' not in df.columns and 'domain_recall' not in df.columns:
            return pd.DataFrame()
        
        # Filter out old short-name models (keep only full model names)
        short_names = ['medgemma', 'openai', 'gemini', 'baseline', 'medgemma-v1.0', 'openai-v1.0', 'baseline-v1.0', 'gemini-v1.0']
        df = df[~df['model_version'].isin(short_names)].copy()
        
        if df.empty:
            return pd.DataFrame()
        
        # Helper function to safely get column value
        def safe_get_col(col_name, default_col_name=None, default_value=0):
            if col_name in df.columns:
                col = df[col_name]
                # Handle None/NaN values
                return col.fillna(default_value)
            elif default_col_name and default_col_name in df.columns:
                col = df[default_col_name]
                return col.fillna(default_value)
            else:
                return pd.Series([default_value] * len(df), index=df.index)
        
        # Handle domain detection rate
        if 'domain_knowledge_detection_rate' in df.columns:
            domain_detection = df['domain_knowledge_detection_rate'].fillna(0).apply(lambda x: x if x > 1 else x * 100)
        else:
            domain_detection = pd.Series([0] * len(df), index=df.index)
        
        # Create clean dataset with required columns
        # Note: Clinical Reasoning benchmarks store total_patients and successful_analyses
        # in the metrics JSONB which gets expanded during the loading phase
        result_df = pd.DataFrame({
            'model_version': df['model_version'].values,
            'created_at': df['created_at'].values,
            'domain_detection': domain_detection.values,
            'f1_score': safe_get_col('f1', 'f1_score', 0).values,
            'precision': safe_get_col('precision', 'precision_score', 0).values,
            'recall': safe_get_col('recall', 'recall_score', 0).values,
            'latency_ms': safe_get_col('latency_ms', default_value=0).values,
            'total_patients': safe_get_col('total_patients', default_value=0).values,
            'successful': safe_get_col('successful_analyses', default_value=0).values,
            'total_potential_savings': safe_get_col('total_potential_savings', default_value=0).values,
            'total_missed_savings': safe_get_col('total_missed_savings', default_value=0).values,
            'avg_savings_per_patient': safe_get_col('avg_savings_per_patient', default_value=0).values,
            'savings_capture_rate': safe_get_col('savings_capture_rate', default_value=0).values
        })
        
        return result_df
    
    patient_df = load_patient_benchmarks()
    
    if patient_df.empty:
        st.warning("No model benchmark data available. Run benchmarks with: `python3 scripts/generate_patient_benchmarks.py --model all --push-to-supabase`")
    else:
        # Get latest result per model
        latest_results = patient_df.sort_values('created_at').groupby('model_version').last().reset_index()
        
        # Calculate Healthcare Effectiveness Score (HES) for each model
        def calculate_healthcare_effectiveness_score(df, history_df):
            """
            Calculate composite Healthcare Effectiveness Score (HES).
            
            PRIORITIZES RECALL (60% weight): In medical billing compliance, missing errors
            (false negatives) is more expensive than false positives. The cost of an undetected
            fraudulent/erroneous medical bill far exceeds the cost of flagging legitimate bills
            for review.
            
            Formula:
            - Recall: 60% (PRIMARY - error detection rate)
            - F1: 15% (balanced performance)
            - ROI: 10% (efficiency - value per latency)
            - Savings Capture: 10% (financial impact)
            - Stability: 5% (performance consistency)
            - Penalties for failures and insufficient data
            """
            import numpy as np
            
            scores = []
            for idx, row in df.iterrows():
                model = row['model_version']
                
                # Base metrics
                avg_f1 = row.get('f1_score', 0) or 0
                avg_recall = row.get('recall', 0) or 0
                
                # Calculate ROI (value per latency unit)
                latency = max(row.get('latency_ms', 1000), 1)  # Avoid div by zero
                savings = row.get('total_potential_savings', 0) or 0
                roi = savings / latency if latency > 0 else 0
                
                # Calculate failure rate (as decimal, not percentage)
                total = row.get('total_patients', 0) or 0
                successful = row.get('successful', 0) or 0
                
                # Only calculate if we have valid data
                if total > 0 and successful <= total:
                    failure_rate = (total - successful) / total
                else:
                    # No data or invalid data - mark as None
                    failure_rate = None
                
                # Savings capture rate
                savings_capture = row.get('savings_capture_rate', 0) or 0
                savings_capture = savings_capture / 100 if savings_capture > 1 else savings_capture
                
                # Stability score from historical data
                model_history = history_df[history_df['model_version'] == model]
                if len(model_history) >= 2:
                    f1_values = model_history['f1_score'].dropna()
                    if len(f1_values) >= 2:
                        f1_std = f1_values.std()
                        stability_score = max(0, 1 - f1_std)
                    else:
                        stability_score = 0.5
                else:
                    stability_score = 0.5
                
                scores.append({
                    'model': model,
                    'avg_f1': avg_f1,
                    'avg_recall': avg_recall,
                    'roi': roi,
                    'stability_score': stability_score,
                    'savings_capture': savings_capture,
                    'failure_rate': failure_rate,
                    'run_count': len(model_history)
                })
            
            scores_df = pd.DataFrame(scores)
            
            # Normalize ROI and savings capture (min-max scaling)
            if len(scores_df) > 1:
                roi_min, roi_max = scores_df['roi'].min(), scores_df['roi'].max()
                if roi_max > roi_min:
                    scores_df['normalized_roi'] = (scores_df['roi'] - roi_min) / (roi_max - roi_min)
                else:
                    scores_df['normalized_roi'] = 0.5
                
                sc_min, sc_max = scores_df['savings_capture'].min(), scores_df['savings_capture'].max()
                if sc_max > sc_min:
                    scores_df['savings_capture_norm'] = (scores_df['savings_capture'] - sc_min) / (sc_max - sc_min)
                else:
                    scores_df['savings_capture_norm'] = scores_df['savings_capture']
            else:
                scores_df['normalized_roi'] = 0.5
                scores_df['savings_capture_norm'] = scores_df['savings_capture']
            
            # Calculate failure penalty (handle None values)
            scores_df['failure_penalty'] = scores_df['failure_rate'].apply(
                lambda x: x * 0.25 if x is not None else 0
            )
            
            # Apply low-run penalty
            scores_df['low_run_penalty'] = scores_df['run_count'].apply(lambda x: 0.15 if x < 2 else 0)
            
            # Calculate composite HES (Healthcare Effectiveness Score)
            # PRIORITIZES RECALL: Missing medical billing errors (false negatives) is more costly
            # than false positives in healthcare compliance scenarios
            scores_df['hes'] = (
                (scores_df['avg_recall'] * 0.60) +        # PRIMARY: Catch errors (false negatives are expensive)
                (scores_df['avg_f1'] * 0.15) +            # Balance: Overall performance
                (scores_df['normalized_roi'] * 0.10) +    # Efficiency: Value per latency
                (scores_df['savings_capture_norm'] * 0.10) +  # Financial: Actual savings captured
                (scores_df['stability_score'] * 0.05) -   # Consistency: Performance variance
                scores_df['failure_penalty'] -
                scores_df['low_run_penalty']
            )
            
            return scores_df
        
        hes_scores = calculate_healthcare_effectiveness_score(latest_results, patient_df)
        
        # Merge HES back into latest_results
        latest_results = latest_results.merge(
            hes_scores[['model', 'hes', 'stability_score', 'roi', 'failure_rate']],
            left_on='model_version',
            right_on='model',
            how='left'
        )
        
        # Sort by HES
        latest_results = latest_results.sort_values('hes', ascending=False)
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        # Store values for use outside columns
        best_model = latest_results.iloc[0]['model_version'] if not latest_results.empty else "N/A"
        best_hes = latest_results.iloc[0]['hes'] if not latest_results.empty else 0
        best_stability = latest_results.iloc[0]['stability_score'] if not latest_results.empty else 0
        best_roi = latest_results.iloc[0]['roi'] if not latest_results.empty else 0
        best_failure = latest_results.iloc[0]['failure_rate'] if not latest_results.empty else 0
        
        with col1:
            st.metric(
                "🏆 Clinical Effectiveness Leader",
                best_model,
                f"HES: {best_hes:.3f}",
                help="Ranking based on composite healthcare-weighted score (F1, recall, ROI, stability, reliability)."
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
        
        # Full-width Score Breakdown expander
        with st.expander("📊 Score Breakdown - Healthcare Effectiveness Score (HES)", expanded=False):
            # Get the actual component values for the best model
            best_model_data = latest_results.iloc[0]
            recall = best_model_data.get('recall', 0)
            f1 = best_model_data.get('f1_score', 0)
            savings_capture = best_model_data.get('savings_capture_rate', 0)
            
            # Full-width header
            st.markdown(f"### 🏆 {best_model} - Healthcare Effectiveness Score: {best_hes:.3f}")
            st.markdown("---")
            
            # Component scores in 6 columns for better space utilization
            st.write("**Component Metrics:**")
            col_a, col_b, col_c, col_d, col_e, col_f = st.columns(6)
            
            with col_a:
                st.metric("Recall (60% weight)", f"{recall:.3f}", help="Error detection rate - PRIMARY metric")
            
            with col_b:
                st.metric("F1 Score (15% weight)", f"{f1:.3f}", help="Balanced precision + recall")
            
            with col_c:
                st.metric("ROI (10% weight)", f"{best_roi:.2f}", help="Savings ÷ Latency")
            
            with col_d:
                st.metric("Savings Capture (10%)", f"{savings_capture:.1f}%", help="% of potential savings captured")
            
            with col_e:
                st.metric("Stability (5% weight)", f"{best_stability:.3f}", help="1 - StdDev of F1 across runs")
            
            with col_f:
                # Handle None failure rate
                if best_failure is not None and not pd.isna(best_failure):
                    st.metric("Failure Rate Penalty", f"{best_failure:.1%}", help="Failed analyses penalty: -25%")
                else:
                    st.metric("Failure Rate Penalty", "N/A", help="Insufficient data")
            
            st.markdown("---")
            
            # Full-width explanation in 2 columns
            exp_col1, exp_col2 = st.columns([1, 1])
            
            with exp_col1:
                st.markdown("**📐 Formula:**")
                st.code("HES = (Recall × 60%) + (F1 × 15%) + (ROI × 10%) + (Savings × 10%) + (Stability × 5%) - Penalties", language="python")
            
            with exp_col2:
                st.markdown("**💡 Why Recall is Prioritized (60%):**")
                st.markdown("""
                In healthcare billing compliance:
                - **Missing fraud:** $1,000-$50,000+ loss
                - **False alarm:** $5-$50 review cost
                - **False negatives are 100-1000× more expensive**
                """)
        
        st.markdown("---")
        
        # Leaderboard - moved here to be right after Score Breakdown
        st.subheader("📊 Domain Knowledge Leaderboard (Latest Run)")
        
        # Methodology accordion for leaderboard
        with st.expander("📐 Methodology: Domain Knowledge Leaderboard", expanded=False):
            total_models = len(latest_results)
            total_patients = latest_results['total_patients'].sum()
            avg_patients_per_model = latest_results['total_patients'].mean()
            
            st.markdown(f"""
            **Sample Sizes:**
            - **Models Tested:** {total_models}
            - **Total Patient Profiles:** {int(total_patients)}
            - **Avg Patients per Model:** {avg_patients_per_model:.1f}
            
            **What is Domain Knowledge Detection?**
            
            Tests AI models' ability to identify gender/age-inappropriate medical procedures that require 
            healthcare domain knowledge. For example:
            - Male patient billed for pregnancy ultrasound
            - 8-year-old billed for colonoscopy screening
            - 25-year-old male billed for mammogram
            
            **Test Design:**
            - Synthetic patient profiles with cross-document billing errors
            - Requires models to understand medical appropriateness, not just coding rules
            - Tests clinical reasoning beyond pattern matching
            
            **Metrics Explained:**
            - **Domain Detection %:** Percentage of domain knowledge errors correctly identified
            - **F1 Score:** Harmonic mean of precision and recall (balanced performance)
            - **Precision:** Of all errors flagged, what % were actual errors (avoid false alarms)
            - **Recall:** Of all actual errors, what % were caught (catch everything)
            - **Total Patients:** Number of patient profiles tested
            - **Successful:** Number of profiles analyzed without API/system failures
            """)
        
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
        
        # Methodology accordion for historical trends
        with st.expander("📐 Methodology: Performance Trends Over Time", expanded=False):
            total_runs = len(patient_df)
            unique_models = patient_df['model_version'].nunique()
            date_range = "N/A"
            if len(patient_df) > 1:
                earliest = patient_df['created_at'].min()
                latest = patient_df['created_at'].max()
                date_range = f"{earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}"
            
            st.markdown(f"""
            **Sample Sizes:**
            - **Total Benchmark Runs:** {total_runs}
            - **Models Tracked:** {unique_models}
            - **Date Range:** {date_range}
            
            **Domain Detection Over Time:**
            - Tracks how well each model identifies domain knowledge errors across benchmark runs
            - Each point represents one complete benchmark run (10-50 patient profiles)
            - Upward trends indicate improving domain knowledge detection
            - Flat lines indicate consistent performance
            
            **F1 Score Comparison:**
            - Compares latest F1 scores across all models
            - F1 = 2 × (Precision × Recall) / (Precision + Recall)
            - Higher F1 means better balanced performance
            - Best for comparing models at a single point in time
            
            **Statistical Confidence:**
            - Single run: Baseline measurement only
            - 2-3 runs: Emerging trend, low confidence
            - 4-5 runs: Moderate confidence in trend direction
            - 6+ runs: High confidence, statistical significance possible
            """)
        
        # Historical trends - moved here to be right after leaderboard
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
        
        st.markdown("---")
        
        # Cost Savings Per Model
        st.subheader("💰 Cost Savings by Model")
        
        # Methodology accordion for cost savings
        with st.expander("📐 Methodology: Cost Savings Calculation", expanded=False):
            if 'total_potential_savings' in latest_results.columns:
                total_potential = latest_results['total_potential_savings'].sum()
                total_missed = latest_results['total_missed_savings'].sum()
                avg_capture_rate = latest_results['savings_capture_rate'].mean()
                
                st.markdown(f"""
                **Sample Sizes (Current Run):**
                - **Models Analyzed:** {len(latest_results)}
                - **Total Potential Savings:** ${total_potential:,.2f}
                - **Total Missed Savings:** ${total_missed:,.2f}
                - **Avg Capture Rate:** {avg_capture_rate:.1f}%
                
                **How Savings are Calculated:**
                
                1. **Potential Savings:** Total value of all billing errors detected by the model
                   - Each detected inappropriate procedure = cost of that procedure
                   - Example: Unnecessary chemotherapy flagged = $50,000 saved
                
                2. **Missed Savings:** Value of errors that existed but were NOT detected
                   - False negatives = errors that slipped through
                   - Higher missed savings = lower detection rate
                
                3. **Avg per Patient:** Total potential savings ÷ Number of patient profiles tested
                   - Shows expected savings per patient profile
                   - Useful for ROI calculations
                
                4. **Savings Capture Rate:** (Potential Savings / Total Possible Savings) × 100
                   - Percentage of all possible savings that were captured
                   - 100% = caught every error
                   - <100% = some errors were missed
                
                **Important Notes:**
                - Based on synthetic test data with known error costs
                - Real-world savings may vary based on actual billing patterns
                - Does not include cost of false positives (human review time)
                - Conservative estimates using Medicare reimbursement rates
                """)
            else:
                st.markdown("""
                **Cost Savings Data Not Available**
                
                Run benchmarks with cost tracking enabled:
                ```bash
                python3 scripts/generate_patient_benchmarks.py --model all
                ```
                """)
        
        # Check if cost savings data exists
        if 'total_potential_savings' in latest_results.columns:
            savings_df = latest_results[[
                'model_version', 'total_potential_savings', 'total_missed_savings',
                'avg_savings_per_patient', 'savings_capture_rate'
            ]].copy()
            
            savings_df = savings_df.sort_values('total_potential_savings', ascending=False)
            savings_df.columns = [
                'Model', 'Potential Savings', 'Missed Savings',
                'Avg per Patient', 'Capture Rate %'
            ]
            
            # Format currency and percentages
            savings_df['Potential Savings'] = savings_df['Potential Savings'].apply(lambda x: f"${x:,.2f}")
            savings_df['Missed Savings'] = savings_df['Missed Savings'].apply(lambda x: f"${x:,.2f}")
            savings_df['Avg per Patient'] = savings_df['Avg per Patient'].apply(lambda x: f"${x:,.2f}")
            savings_df['Capture Rate %'] = savings_df['Capture Rate %'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(savings_df, use_container_width=True, hide_index=True)
            
            # Cost savings visualization
            col1, col2 = st.columns(2)
            
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Potential Savings',
                    x=latest_results['model_version'],
                    y=latest_results['total_potential_savings'],
                    text=latest_results['total_potential_savings'].apply(lambda x: f"${x:,.0f}"),
                    textposition='auto',
                    marker_color='green'
                ))
                fig.add_trace(go.Bar(
                    name='Missed Savings',
                    x=latest_results['model_version'],
                    y=latest_results['total_missed_savings'],
                    text=latest_results['total_missed_savings'].apply(lambda x: f"${x:,.0f}"),
                    textposition='auto',
                    marker_color='red'
                ))
                fig.update_layout(
                    title="Potential vs Missed Savings",
                    yaxis_title="Amount ($)",
                    barmode='group',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    latest_results,
                    x='model_version',
                    y='savings_capture_rate',
                    text=latest_results['savings_capture_rate'].apply(lambda x: f"{x:.1f}%"),
                    labels={'model_version': 'Model', 'savings_capture_rate': 'Capture Rate (%)'},
                    title="Savings Capture Rate by Model",
                    color='savings_capture_rate',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🔄 Re-run benchmarks to see cost savings metrics: `python3 scripts/generate_patient_benchmarks.py --model all`")
        
        st.markdown("---")
        
        # Cost Savings Trends
        if 'total_potential_savings' in patient_df.columns and len(patient_df) > 1:
            st.markdown("---")
            st.subheader("💰 Cost Savings Trends Over Time")
            
            # Methodology accordion for savings trends
            with st.expander("📐 Methodology: Savings Trends Analysis", expanded=False):
                runs_with_savings = patient_df[patient_df['total_potential_savings'].notna()]
                total_trend_runs = len(runs_with_savings)
                models_tracked = runs_with_savings['model_version'].nunique()
                
                st.markdown(f"""
                **Sample Sizes (Historical):**
                - **Total Runs with Savings Data:** {total_trend_runs}
                - **Models Tracked:** {models_tracked}
                - **Time Period:** {runs_with_savings['created_at'].min().strftime('%Y-%m-%d')} to {runs_with_savings['created_at'].max().strftime('%Y-%m-%d')}
                
                **What These Trends Show:**
                
                **Potential Savings Over Time:**
                - Shows how much money each model could save if deployed
                - Increasing trend = model is getting better at detecting expensive errors
                - Stable trend = consistent detection performance
                - Decreasing trend = model regression or easier test cases
                
                **Savings Capture Rate Trend:**
                - Shows the % of possible savings each model captures over time
                - Upward trend = model is catching more errors
                - Target: 80%+ capture rate for production deployment
                - Below 50% = significant errors being missed
                
                **Interpreting the Charts:**
                - Each data point = one complete benchmark run
                - Multiple models = different colored lines
                - Volatility = inconsistent performance (may need more training)
                - Smooth lines = stable, reliable performance
                
                **Business Context:**
                - These are cumulative savings if the model reviewed ALL test cases
                - Real deployment would see similar savings % on actual claims
                - Savings justify model deployment costs when capture rate >70%
                """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.line(
                    patient_df,
                    x='created_at',
                    y='total_potential_savings',
                    color='model_version',
                    markers=True,
                    labels={
                        'created_at': 'Date',
                        'total_potential_savings': 'Potential Savings ($)',
                        'model_version': 'Model'
                    },
                    title="Potential Savings Over Time"
                )
                fig.update_layout(height=400, hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True, key="savings_trend")
            
            with col2:
                fig = px.line(
                    patient_df,
                    x='created_at',
                    y='savings_capture_rate',
                    color='model_version',
                    markers=True,
                    labels={
                        'created_at': 'Date',
                        'savings_capture_rate': 'Capture Rate (%)',
                        'model_version': 'Model'
                    },
                    title="Savings Capture Rate Over Time"
                )
                fig.update_layout(height=400, hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True, key="capture_rate_trend")
        
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
                    
                    # Add methodology accordion
                    with st.expander("📊 Analysis Methodology & Sample Sizes"):
                        st.markdown("""
                        **Data Source:**
                        - Latest benchmark transactions from Supabase `benchmark_transactions` table
                        - Filtered by environment (production/staging/local)
                        - Uses `error_type_performance` field from transaction metrics
                        - Models tracked: `gpt-4o-mini`, `gpt-4o`, `medgemma`, `medgemma-ensemble`
                        
                        **Sample Sizes:**
                        - **Sample size varies by error type** based on clinical validation scenarios
                        - Common error types analyzed:
                          - **Overtreatment**: Medically unnecessary procedures or tests
                          - **Incorrect Procedure Codes**: Wrong CPT codes for services rendered
                          - **Upcoding**: Billing for more expensive service than provided
                          - **Unbundling**: Separately billing for services that should be bundled
                          - **Medical Necessity**: Services not justified by patient condition
                          - **Duplicate Billing**: Charging twice for the same service
                        - Each error type represents multiple clinical scenarios across different specialties
                        - Error types extracted from ground truth data in clinical validation scenarios
                        
                        **Calculations:**
                        - **Detection Rate**: Percentage of scenarios where the model correctly identified the specific error type
                          - Formula: `(Correctly identified errors of type X / Total errors of type X) × 100`
                          - Stored in `error_type_performance[error_type]['detection_rate']`
                        - **Aggregation**: Uses latest transaction per model (most recent benchmark run)
                        - **Color Scale**: 🟢 Green (high detection) → 🟡 Yellow → 🔴 Red (low detection)
                        
                        **Analysis Methodology:**
                        1. Query Supabase for latest 100 transactions, filtered by environment
                        2. Sort by `created_at DESC` to get most recent results first
                        3. For each model, extract the first (latest) transaction with `error_type_performance` data
                        4. Skip legacy model names (medgemma-v1.0, openai-v1.0, etc.) for consistency
                        5. Build union of all error types across all models
                        6. Create detection rate matrix: rows = error types, columns = models
                        7. Handle missing data: Models may not have all error types (shows 0%)
                        8. Generate heatmap with dynamic height based on number of error types
                        
                        **Purpose:**
                        - **Identify Model Specializations**: Which models excel at detecting specific billing errors?
                        - **Training Priorities**: Which error types are hardest to detect across all models?
                        - **Quality Assurance**: Ensure models can catch diverse billing fraud patterns
                        - **Compliance Monitoring**: Track performance on regulatory-critical error types
                        - **Resource Allocation**: Focus improvement efforts on low-detection error types
                        
                        **Interpretation Guide:**
                        - **High Detection (Green)**: Model reliably catches this error type - deploy with confidence
                        - **Medium Detection (Yellow)**: Model catches some cases - requires human review
                        - **Low Detection (Red)**: Model struggles with this error type - manual audit required
                        - **Vertical Patterns**: If entire column is red, model needs retraining
                        - **Horizontal Patterns**: If entire row is red, error type is inherently difficult to detect
                        
                        **Clinical Relevance:**
                        - Error detection requires deep medical domain knowledge
                        - Some errors (e.g., medical necessity) need clinical judgment
                        - Other errors (e.g., duplicate billing) are more rule-based
                        - Performance varies by specialty (cardiology vs dermatology)
                        - Real-world impact: Each missed error = potential fraud or patient harm
                        
                        **Data Quality Notes:**
                        - Error types dynamically discovered from benchmark transactions
                        - New error types added as clinical validation scenarios expand
                        - Historical comparison possible by analyzing older transactions
                        - Missing data (white cells) = model hasn't been tested on that error type yet
                        """)
                    
                else:
                    st.info("No error-type performance data available yet. Re-push benchmark results to collect this data.")
            else:
                st.warning("No transaction data available for error type analysis.")
        except Exception as e:
            st.error(f"Error loading error type performance: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
        
        # Patient Profile Datasets accordion (modeled after Clinical Data Sets)
        st.markdown("---")
        with st.expander("📁 Patient Profile Benchmark Datasets", expanded=False):
            st.markdown("""
            Synthetic patient profiles with cross-document billing data used for domain knowledge 
            detection benchmarks. Each profile contains multiple medical documents that test AI models' 
            ability to identify gender/age-inappropriate procedures.
            """)
            
            # Load patient profiles from disk
            import json
            import glob
            
            profiles_dir = PROJECT_ROOT / 'benchmarks' / 'patient_profiles'
            profile_files = sorted(glob.glob(str(profiles_dir / '*.json')))
            
            if profile_files:
                # Parse and count profiles
                profiles_data = []
                for profile_file in profile_files:
                    try:
                        with open(profile_file, 'r') as f:
                            profile = json.load(f)
                            profiles_data.append({
                                'file': Path(profile_file).name,
                                'data': profile
                            })
                    except Exception as e:
                        st.error(f"Error loading {Path(profile_file).name}: {e}")
                        continue
                
                # Summary stats
                total_profiles = len(profiles_data)
                profiles_with_issues = sum(1 for p in profiles_data if p['data'].get('expected_issues', []))
                total_documents = sum(len(p['data'].get('documents', [])) for p in profiles_data)
                
                st.markdown(f"**Total Profiles:** {total_profiles} | "
                           f"**With Issues:** {profiles_with_issues} | "
                           f"**Total Documents:** {total_documents}")
                st.markdown("---")
                
                # Display each profile as an accordion with View Full button (like Clinical Data Sets)
                for profile_info in profiles_data:
                    profile_data = profile_info['data']
                    patient_id = profile_data.get('patient_id', 'N/A')
                    name = profile_data.get('name', 'Unknown')
                    demographics = profile_data.get('demographics', {})
                    age = demographics.get('age', 'N/A')
                    sex = demographics.get('sex', 'N/A')
                    num_documents = len(profile_data.get('documents', []))
                    expected_issues = profile_data.get('expected_issues', [])
                    num_issues = len(expected_issues)
                    
                    # Create unique modal key
                    modal_key = f"modal_patient_{patient_id.replace('P', '')}"
                    
                    # Accordion for each profile
                    col1, col2, col3 = st.columns([2, 3, 1])
                    
                    with col1:
                        st.markdown(f"**{patient_id}**")
                        st.caption(f"{name}")
                    
                    with col2:
                        st.markdown(f"Age: {age} | Sex: {sex} | Docs: {num_documents} | Issues: {num_issues}")
                    
                    with col3:
                        # View Full button
                        if st.button("🔍 View Full", key=f"btn_{modal_key}"):
                            st.session_state['active_patient_modal'] = patient_id
                            st.rerun()
                    
                    st.markdown("---")  # Separator between profiles
                
                # Handle modal display outside the loop (only one dialog at a time)
                if st.session_state.get('active_patient_modal'):
                    active_patient_id = st.session_state['active_patient_modal']
                    
                    # Find the profile data for the active modal
                    active_profile = None
                    for profile_info in profiles_data:
                        if profile_info['data'].get('patient_id') == active_patient_id:
                            active_profile = profile_info['data']
                            break
                    
                    if active_profile:
                        name = active_profile.get('name', 'Unknown')
                        
                        @st.dialog(f"📋 {name} ({active_patient_id})", width="large")
                        def show_profile_details():
                            # Patient Demographics
                            st.subheader("👤 Patient Demographics")
                            demo = active_profile.get('demographics', {})
                            demo_col1, demo_col2, demo_col3 = st.columns(3)
                            with demo_col1:
                                st.metric("Patient ID", active_profile.get('patient_id', 'N/A'))
                                st.metric("Age", demo.get('age', 'N/A'))
                            with demo_col2:
                                st.metric("Name", active_profile.get('name', 'Unknown'))
                                st.metric("Sex", demo.get('sex', 'N/A'))
                            with demo_col3:
                                st.metric("DOB", demo.get('date_of_birth', 'N/A'))
                            
                            # Medical History
                            st.markdown("---")
                            st.subheader("🏥 Medical History")
                            med_history = active_profile.get('medical_history', {})
                            
                            hist_col1, hist_col2 = st.columns(2)
                            with hist_col1:
                                conditions = med_history.get('conditions', [])
                                st.markdown("**Conditions:**")
                                if conditions:
                                    for condition in conditions:
                                        st.markdown(f"- {condition}")
                                else:
                                    st.markdown("*None reported*")
                            
                            with hist_col2:
                                allergies = med_history.get('allergies', [])
                                st.markdown("**Allergies:**")
                                if allergies:
                                    for allergy in allergies:
                                        st.markdown(f"- {allergy}")
                                else:
                                    st.markdown("*None reported*")
                            
                            # Documents
                            st.markdown("---")
                            st.subheader(f"📄 Documents ({len(active_profile.get('documents', []))} total)")
                            
                            documents = active_profile.get('documents', [])
                            for i, doc in enumerate(documents, 1):
                                with st.expander(f"Document {i}: {doc.get('document_id', 'Unknown')}", expanded=False):
                                    st.markdown(f"**Type:** {doc.get('document_type', 'text')}")
                                    st.markdown("**Content:**")
                                    st.code(doc.get('content', 'No content'), language="text")
                            
                            # Expected Issues (Ground Truth)
                            st.markdown("---")
                            st.subheader(f"🎯 Expected Issues ({len(active_profile.get('expected_issues', []))} total)")
                            
                            expected_issues = active_profile.get('expected_issues', [])
                            if expected_issues:
                                for i, issue in enumerate(expected_issues, 1):
                                    severity_color = {
                                        'critical': '🔴',
                                        'high': '🟠',
                                        'moderate': '🟡',
                                        'low': '🟢'
                                    }.get(issue.get('severity', 'unknown'), '⚪')
                                    
                                    with st.expander(f"{severity_color} Issue {i}: {issue.get('type', 'Unknown').replace('_', ' ').title()}", expanded=True):
                                        st.markdown(f"**Severity:** {issue.get('severity', 'unknown').upper()}")
                                        st.markdown(f"**Description:** {issue.get('description', 'No description')}")
                                        st.markdown(f"**Requires Domain Knowledge:** {'Yes' if issue.get('requires_domain_knowledge', False) else 'No'}")
                                        if issue.get('cpt_code'):
                                            st.markdown(f"**CPT Code:** {issue.get('cpt_code')}")
                            else:
                                st.success("✅ No expected issues - this is a clean profile for testing false positives")
                            
                            # Usage info
                            st.markdown("---")
                            st.info("""
                            **How This Profile is Used in Benchmarks:**
                            
                            1. The AI model receives all documents plus patient demographics
                            2. Model must identify billing errors that require domain knowledge
                            3. Results are compared against the "Expected Issues" above
                            4. Performance metrics (precision, recall, F1) are calculated
                            5. Domain detection rate measures how well the model caught these specific errors
                            """)
                            
                            # Close button
                            if st.button("Close", key="close_patient_modal"):
                                st.session_state['active_patient_modal'] = None
                                st.rerun()
                        
                        show_profile_details()
            else:
                st.warning(f"No patient profile files found in `{profiles_dir}`")
        
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

# ============================================================================
# Documentation Viewer (triggered from sidebar assistant)
# ============================================================================

if 'benchmark_sidebar_doc_view' in st.session_state:
    doc_path = PROJECT_ROOT / st.session_state['benchmark_sidebar_doc_view']
    doc_title = st.session_state.get('benchmark_sidebar_doc_title', 'Documentation')

    # Create a container in the main area for documentation
    st.markdown("---")
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"## {doc_title}")
    with col2:
        if st.button("✖ Close", key="close_benchmark_doc_viewer"):
            del st.session_state['benchmark_sidebar_doc_view']
            if 'benchmark_sidebar_doc_title' in st.session_state:
                del st.session_state['benchmark_sidebar_doc_title']
            st.rerun()

    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            doc_content = f.read()
        st.markdown(doc_content)

        if st.button("✖ Close Document", key="close_benchmark_doc_viewer_bottom"):
            del st.session_state['benchmark_sidebar_doc_view']
            if 'benchmark_sidebar_doc_title' in st.session_state:
                del st.session_state['benchmark_sidebar_doc_title']
            st.rerun()

    except FileNotFoundError:
        st.error(f"📄 Document not found: {doc_path}")
        st.info("This documentation file may not be available.")
        if st.button("✖ Close", key="close_benchmark_doc_viewer_error"):
            del st.session_state['benchmark_sidebar_doc_view']
            if 'benchmark_sidebar_doc_title' in st.session_state:
                del st.session_state['benchmark_sidebar_doc_title']
            st.rerun()

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>Production Stability Monitor v1.0 | MLOps Team</p>
    <p>Data refreshes every 5 minutes | Last refresh: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
