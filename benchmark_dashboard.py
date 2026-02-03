#!/usr/bin/env python3
"""
Standalone Streamlit dashboard for benchmark metrics visualization.

This is a separate service that reads benchmark results and displays them.
Deploy this to Streamlit Cloud for live benchmark metrics.

Usage:
    streamlit run benchmark_dashboard.py

Can be deployed to Streamlit Cloud pointing to this file directly.
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="medBillDozer Benchmarks",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("📊 medBillDozer Benchmark Metrics")
st.markdown("Real-time performance comparison of medical billing analysis providers")

# Load results
results_dir = Path("benchmarks/results")

if not results_dir.exists():
    st.error("❌ Benchmark results directory not found. Run benchmarks first.")
    st.info("Run: `python3 scripts/generate_benchmarks.py --model all`")
    st.stop()

# Find all aggregated metrics files
metrics_files = sorted(results_dir.glob("aggregated_metrics_*.json"))

if not metrics_files:
    st.warning("⚠️ No benchmark results found. Run benchmarks first.")
    st.info("Run: `python3 scripts/generate_benchmarks.py --model all`")
    st.stop()

# Load all results
results = {}
for file in metrics_files:
    try:
        data = json.loads(file.read_text())
        model_name = data.get("model_name", file.stem)
        results[model_name] = data
    except Exception as e:
        st.warning(f"Could not load {file.name}: {e}")

if not results:
    st.error("❌ Could not load any benchmark results")
    st.stop()

# Sidebar filters
st.sidebar.header("📋 Filters & Options")
selected_models = st.sidebar.multiselect(
    "Select models to compare:",
    options=list(results.keys()),
    default=list(results.keys())
)

if not selected_models:
    st.warning("Please select at least one model")
    st.stop()

filtered_results = {k: v for k, v in results.items() if k in selected_models}

# ============================================================================
# MAIN METRICS COMPARISON
# ============================================================================

st.header("🎯 Overall Metrics Comparison")

# Prepare comparison data
comparison_data = []
for model_name, data in filtered_results.items():
    comparison_data.append({
        "Model": model_name.replace("_", " ").title(),
        "Precision": data.get("issue_precision", 0),
        "Recall": data.get("issue_recall", 0),
        "F1 Score": data.get("issue_f1_score", 0),
        "Documents": data.get("total_documents", 0),
        "Successful": data.get("successful_extractions", 0),
        "Latency (s)": data.get("avg_pipeline_latency_ms", 0) / 1000,
    })

comparison_df = pd.DataFrame(comparison_data)

# Display as table
col1, col2 = st.columns([2, 3])
with col1:
    st.markdown("### Performance Metrics")
    metrics_display = comparison_df[[
        "Model", "Precision", "Recall", "F1 Score"
    ]].copy()
    
    # Format as percentage and styled
    for col in ["Precision", "Recall", "F1 Score"]:
        metrics_display[col] = metrics_display[col].apply(lambda x: f"{x:.2%}" if x is not None else "N/A")
    
    st.dataframe(
        metrics_display,
        width='stretch',
        hide_index=True
    )

with col2:
    st.markdown("### Efficiency Metrics")
    efficiency_display = comparison_df[[
        "Model", "Latency (s)", "Successful"
    ]].copy()
    efficiency_display["Latency (s)"] = efficiency_display["Latency (s)"].apply(lambda x: f"{x:.2f}s")
    
    st.dataframe(
        efficiency_display,
        width='stretch',
        hide_index=True
    )

# ============================================================================
# VISUALIZATIONS
# ============================================================================

st.header("📈 Visual Comparisons")

col1, col2 = st.columns(2)

# Precision vs Recall scatter
with col1:
    st.markdown("### Precision vs Recall")
    fig = px.scatter(
        comparison_df,
        x="Recall",
        y="Precision",
        size="F1 Score",
        hover_data=["Model", "Latency (s)"],
        labels={"Recall": "Recall (%)", "Precision": "Precision (%)"},
        title="Accuracy Trade-off",
        color="Model",
        size_max=300,
    )
    fig.update_layout(
        xaxis=dict(tickformat=".0%"),
        yaxis=dict(tickformat=".0%"),
        height=400,
        showlegend=True,
    )
    st.plotly_chart(fig, width='stretch')

# F1 Score comparison
with col2:
    st.markdown("### F1 Score Comparison")
    fig = go.Figure(data=[
        go.Bar(
            x=comparison_df["Model"],
            y=comparison_df["F1 Score"],
            text=comparison_df["F1 Score"].apply(lambda x: f"{x:.2%}"),
            textposition="auto",
            marker=dict(
                color=comparison_df["F1 Score"],
                colorscale="Viridis",
                showscale=False,
            )
        )
    ])
    fig.update_layout(
        title="Overall Effectiveness (F1 Score)",
        xaxis_title="Model",
        yaxis_title="F1 Score",
        height=400,
        yaxis=dict(tickformat=".0%"),
    )
    st.plotly_chart(fig, width='stretch')

# Speed vs Accuracy
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Speed Comparison")
    fig = go.Figure(data=[
        go.Bar(
            x=comparison_df["Model"],
            y=comparison_df["Latency (s)"],
            text=comparison_df["Latency (s)"].apply(lambda x: f"{x:.2f}s"),
            textposition="auto",
            marker_color="lightblue"
        )
    ])
    fig.update_layout(
        title="Average Latency per Document",
        xaxis_title="Model",
        yaxis_title="Latency (seconds)",
        height=400,
    )
    st.plotly_chart(fig, width='stretch')

with col2:
    st.markdown("### Speed vs Accuracy")
    fig = px.scatter(
        comparison_df,
        x="Latency (s)",
        y="F1 Score",
        size="Precision",
        hover_data=["Model", "Recall"],
        title="Cost/Benefit Trade-off",
        color="Model",
        size_max=300,
    )
    fig.update_layout(
        yaxis=dict(tickformat=".0%"),
        height=400,
    )
    st.plotly_chart(fig, width='stretch')

# ============================================================================
# DETAILED BREAKDOWN
# ============================================================================

st.header("🔍 Detailed Breakdown")

# Tabs for each model
tabs = st.tabs([model for model in selected_models])

for tab, model_name in zip(tabs, selected_models):
    with tab:
        data = filtered_results[model_name]
        
        # Header
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Precision",
                f"{data.get('issue_precision', 0):.1%}",
                help="True positives / (True positives + False positives)"
            )
        
        with col2:
            st.metric(
                "Recall",
                f"{data.get('issue_recall', 0):.1%}",
                help="True positives / (True positives + False negatives)"
            )
        
        with col3:
            st.metric(
                "F1 Score",
                f"{data.get('issue_f1_score', 0):.1%}",
                help="Harmonic mean of precision and recall"
            )
        
        with col4:
            st.metric(
                "Latency",
                f"{data.get('avg_pipeline_latency_ms', 0)/1000:.2f}s",
                help="Average analysis time per document"
            )
        
        st.divider()
        
        # Extraction stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total = data.get("total_documents", 0)
            successful = data.get("successful_extractions", 0)
            st.metric(
                "Documents Processed",
                f"{successful}/{total}",
                help=f"Extraction success rate: {data.get('extraction_accuracy', 0):.1%}"
            )
        
        with col2:
            st.metric(
                "Extraction Time",
                f"{data.get('avg_extraction_latency_ms', 0):.1f}ms",
                help="Average fact extraction latency"
            )
        
        with col3:
            st.metric(
                "JSON Validity",
                f"{data.get('json_validity_rate', 0):.1%}",
                help="Percentage of valid JSON outputs"
            )
        
        st.divider()
        
        # Token usage (if available)
        if data.get("avg_input_tokens", 0) > 0:
            st.markdown("### Token Usage")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Avg Input Tokens", f"{data.get('avg_input_tokens', 0):.0f}")
            
            with col2:
                st.metric("Avg Output Tokens", f"{data.get('avg_output_tokens', 0):.0f}")
            
            with col3:
                st.metric("Avg Total Tokens", f"{data.get('avg_total_tokens', 0):.0f}")
            
            st.divider()
        
        # Individual document results
        st.markdown("### Individual Document Results")
        
        individual_results = data.get("individual_results", [])
        if individual_results:
            individual_df = pd.DataFrame(individual_results)
            
            # Show only relevant columns
            display_cols = [
                "document_name",
                "extraction_success",
                "issues_detected",
                "issues_expected",
                "true_positives",
                "false_positives",
                "false_negatives",
                "pipeline_latency_ms"
            ]
            
            # Filter to available columns
            display_cols = [col for col in display_cols if col in individual_df.columns]
            
            # Rename for display
            display_df = individual_df[display_cols].copy()
            display_df.columns = [col.replace("_", " ").title() for col in display_df.columns]
            
            st.dataframe(display_df, width='stretch', hide_index=True)
        
        # Stats
        if individual_results:
            st.markdown("### Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_tp = sum(r.get("true_positives", 0) for r in individual_results)
                total_fp = sum(r.get("false_positives", 0) for r in individual_results)
                total_fn = sum(r.get("false_negatives", 0) for r in individual_results)
                
                st.metric("Total True Positives", total_tp)
            
            with col2:
                st.metric("Total False Positives", total_fp)
            
            with col3:
                st.metric("Total False Negatives", total_fn)

# ============================================================================
# RECOMMENDATIONS & INFO
# ============================================================================

st.divider()
st.header("💡 Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Use Baseline When:
    - ⚡ Speed is critical
    - 🎯 High precision needed (no false positives)
    - 📋 Only duplicate detection required
    - 🔌 No API dependencies
    """)

with col2:
    st.markdown("""
    ### Use OpenAI/MedGemma When:
    - 🧠 Comprehensive analysis needed
    - 🏥 Medical context matters
    - ✅ Users can verify findings
    - 💰 API costs acceptable
    """)

st.markdown("---")

# Last update info
if filtered_results:
    model = list(filtered_results.values())[0]
    generated_at = model.get("generated_at", "Unknown")
    st.caption(f"📅 Metrics generated: {generated_at}")

st.markdown("""
---
### 📖 More Information

- **Benchmark System**: `scripts/generate_benchmarks.py`
- **Ground Truth Annotations**: `benchmarks/expected_outputs/`
- **Documentation**: See project README and docs/
- **Configuration**: Edit `benchmarks/` to customize tests

---
*This dashboard updates automatically when benchmarks are re-run and results are committed to the repository.*
""")
