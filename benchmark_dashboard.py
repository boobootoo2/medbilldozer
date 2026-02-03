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

# Model name mapping
def get_full_model_name(model_key: str) -> str:
    """Convert model key to full display name."""
    name_map = {
        "baseline": "Heuristic Baseline",
        "openai": "OpenAI GPT-4o-mini",
        "gemini": "Google Gemini 1.5 Flash",
        "medgemma": "Google MedGemma 4B-IT"
    }
    return name_map.get(model_key, model_key.replace("_", " ").title())

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
        "Model": get_full_model_name(model_name),
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
# CROSS-DOCUMENT ANALYSIS
# ============================================================================

st.header("📋 Cross-Document Analysis Results 🏥")

# Overall summary table
st.subheader("📊 Model Performance Summary")

summary_data = []
for model_name, data in filtered_results.items():
    full_name = get_full_model_name(model_name)
    
    # Calculate domain knowledge detection rate (documents with at least 1 TP)
    docs_with_detection = 0
    total_docs = 0
    for doc_result in data.get("individual_results", []):
        if doc_result.get("issues_expected", 0) > 0:
            total_docs += 1
            if doc_result.get("true_positives", 0) > 0:
                docs_with_detection += 1
    
    domain_detection_rate = (docs_with_detection / total_docs * 100) if total_docs > 0 else 0
    
    # Get average token usage
    avg_input_tokens = data.get("avg_input_tokens", 0)
    avg_output_tokens = data.get("avg_output_tokens", 0)
    avg_total_tokens = data.get("avg_total_tokens", 0)
    
    # Format token display
    if avg_total_tokens > 0:
        token_display = f"{avg_total_tokens:.0f}"
        token_detail = f"(In: {avg_input_tokens:.0f}, Out: {avg_output_tokens:.0f})"
    else:
        token_display = "N/A"
        token_detail = "(No API calls)"
    
    summary_data.append({
        "Model": full_name,
        "Precision": data.get("issue_precision", 0),
        "Recall": data.get("issue_recall", 0),
        "F1": data.get("issue_f1_score", 0),
        "Domain Detection": f"{domain_detection_rate:.1f}%",
        "Avg Tokens/Request": token_display,
        "Token Breakdown": token_detail
    })

summary_df = pd.DataFrame(summary_data)

# Format percentages for display
display_df = summary_df.copy()
for col in ["Precision", "Recall", "F1"]:
    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if x > 0 else "0.00")

st.dataframe(
    display_df,
    width='stretch',
    hide_index=True,
    column_config={
        "Model": st.column_config.TextColumn("Model", width="large"),
        "Precision": st.column_config.TextColumn("Precision", width="small"),
        "Recall": st.column_config.TextColumn("Recall", width="small"),
        "F1": st.column_config.TextColumn("F1 Score", width="small"),
        "Domain Detection": st.column_config.TextColumn("Domain Knowledge Detection", width="medium"),
        "Avg Tokens/Request": st.column_config.TextColumn("Avg Tokens", width="small"),
        "Token Breakdown": st.column_config.TextColumn("Token Details", width="medium")
    }
)

st.markdown("---")
st.markdown(
    "**Domain Knowledge Detection**: Percentage of documents with billing issues where the model detected at least one issue correctly."
)
st.markdown(
    "**Token Usage**: Average tokens per request (Input: prompt tokens, Output: response tokens). Baseline uses no API."
)

st.markdown("---")

# Collect per-document results across all models
document_performance = {}
for model_name, data in filtered_results.items():
    full_name = get_full_model_name(model_name)
    for doc_result in data.get("individual_results", []):
        doc_name = doc_result.get("document_name", "Unknown")
        if doc_name not in document_performance:
            document_performance[doc_name] = {
                "document": doc_name,
                "type": doc_result.get("document_type", "Unknown"),
                "expected_issues": doc_result.get("issues_expected", 0)
            }
        
        # Add model-specific metrics
        document_performance[doc_name][f"{full_name}_detected"] = doc_result.get("issues_detected", 0)
        document_performance[doc_name][f"{full_name}_tp"] = doc_result.get("true_positives", 0)
        document_performance[doc_name][f"{full_name}_fp"] = doc_result.get("false_positives", 0)
        document_performance[doc_name][f"{full_name}_fn"] = doc_result.get("false_negatives", 0)

# Convert to DataFrame
doc_df = pd.DataFrame(list(document_performance.values()))

if not doc_df.empty:
    # Group by document type
    doc_types = doc_df["type"].unique()
    
    # Summary by document type
    st.subheader("📊 Performance by Document Type")
    
    type_summary = []
    for doc_type in sorted(doc_types):
        type_docs = doc_df[doc_df["type"] == doc_type]
        summary = {
            "Document Type": doc_type.replace("_", " ").title(),
            "# Documents": len(type_docs),
            "Total Expected Issues": type_docs["expected_issues"].sum()
        }
        
        # Add per-model detection rates
        for model_key in filtered_results.keys():
            full_name = get_full_model_name(model_key)
            tp_col = f"{full_name}_tp"
            if tp_col in type_docs.columns:
                total_tp = type_docs[tp_col].sum()
                total_expected = type_docs["expected_issues"].sum()
                detection_rate = (total_tp / total_expected * 100) if total_expected > 0 else 0
                summary[f"{full_name} Detection"] = f"{detection_rate:.0f}%"
        
        type_summary.append(summary)
    
    type_df = pd.DataFrame(type_summary)
    st.dataframe(type_df, width='stretch', hide_index=True)
    
    # Detailed per-document results
    st.subheader("📄 Detailed Document Results")
    
    # Create display columns
    display_cols = ["document", "type", "expected_issues"]
    for model_key in filtered_results.keys():
        full_name = get_full_model_name(model_key)
        if f"{full_name}_detected" in doc_df.columns:
            display_cols.extend([
                f"{full_name}_detected",
                f"{full_name}_tp",
                f"{full_name}_fp",
                f"{full_name}_fn"
            ])
    
    # Filter to existing columns
    available_cols = [col for col in display_cols if col in doc_df.columns]
    detail_df = doc_df[available_cols].copy()
    
    # Rename for clarity
    rename_map = {"document": "Document", "type": "Type", "expected_issues": "Expected"}
    for model_key in filtered_results.keys():
        full_name = get_full_model_name(model_key)
        rename_map.update({
            f"{full_name}_detected": f"{full_name} Detected",
            f"{full_name}_tp": f"{full_name} TP",
            f"{full_name}_fp": f"{full_name} FP",
            f"{full_name}_fn": f"{full_name} FN"
        })
    
    detail_df = detail_df.rename(columns=rename_map)
    st.dataframe(detail_df, width='stretch', hide_index=True)
    
    # Visualization: Detection heatmap
    st.subheader("🔥 Issue Detection Heatmap")
    
    # Prepare heatmap data
    heatmap_data = []
    for _, row in doc_df.iterrows():
        for model_key in filtered_results.keys():
            full_name = get_full_model_name(model_key)
            tp_col = f"{full_name}_tp"
            if tp_col in row:
                expected = row["expected_issues"]
                detected = row.get(f"{full_name}_tp", 0)
                accuracy = (detected / expected * 100) if expected > 0 else 100 if detected == 0 else 0
                heatmap_data.append({
                    "Document": row["document"],
                    "Model": full_name,
                    "Detection Rate %": accuracy
                })
    
    if heatmap_data:
        heatmap_df = pd.DataFrame(heatmap_data)
        pivot_df = heatmap_df.pivot(index="Document", columns="Model", values="Detection Rate %")
        
        fig_heatmap = px.imshow(
            pivot_df,
            labels=dict(x="Model", y="Document", color="Detection Rate %"),
            color_continuous_scale="RdYlGn",
            aspect="auto",
            title="Issue Detection Rate by Document and Model"
        )
        fig_heatmap.update_xaxes(side="top")
        st.plotly_chart(fig_heatmap, width='stretch')
else:
    st.info("No per-document results available in current benchmark data.")

# ============================================================================
# DETAILED BREAKDOWN
# ============================================================================

st.header("🔍 Detailed Breakdown")

# Tabs for each model  
tabs = st.tabs([get_full_model_name(model) for model in selected_models])

for tab, model_name in zip(tabs, selected_models):
    with tab:
        data = filtered_results[model_name]
        full_name = get_full_model_name(model_name)
        st.subheader(f"📊 {full_name}")
        
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
