"""Pipeline DAG Visualization - Visual representation of document analysis workflow.

Displays a directed acyclic graph showing the data pipeline stages for each
document's analysis: classification → extraction → phase-2 parsing → analysis.
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, List, Optional, Any
import json


def create_pipeline_dag_container(document_id: Optional[str] = None):
    """Create an empty expandable container for live pipeline updates.
    
    Returns the container and placeholder objects for progressive updates.
    
    Args:
        document_id: Optional document identifier for display
        
    Returns:
        tuple: (expander, placeholder) for updating the DAG
    """
    doc_label = f"Document {document_id}" if document_id else "Document Analysis"
    expander = st.expander(f"📊 Pipeline Workflow: {doc_label}", expanded=True)
    
    with expander:
        st.caption("⏳ Analysis in progress...")
        placeholder = st.empty()
    
    return expander, placeholder


def update_pipeline_dag(placeholder, workflow_log: Dict[str, Any], document_id: Optional[str] = None):
    """Update an existing pipeline DAG placeholder with current workflow state.
    
    Args:
        placeholder: Streamlit placeholder object to update
        workflow_log: Current workflow log dict with pipeline stages
        document_id: Optional friendly document identifier for display
    """
    if not workflow_log:
        return
    
    # Extract pipeline stages
    pre_extraction = workflow_log.get("pre_extraction", {})
    extraction = workflow_log.get("extraction", {})
    analysis = workflow_log.get("analysis", {})
    
    workflow_id = workflow_log.get("workflow_id", "N/A")
    timestamp = workflow_log.get("timestamp", "N/A")
    
    # Build DAG HTML
    dag_html = _build_dag_html(pre_extraction, extraction, analysis, live_update=True)
    
    with placeholder.container():
        # Show friendly document name if available
        if document_id:
            st.markdown(f"### 📄 {document_id}")
        st.caption(f"Workflow ID: `{workflow_id}` | Timestamp: `{timestamp}`")
        components.html(dag_html, height=800, scrolling=True)


def render_pipeline_dag(workflow_log: Dict[str, Any], document_id: Optional[str] = None):
    """Render a visual DAG showing the document processing pipeline.
    
    Displays the complete workflow stages with status indicators:
    - Pre-extraction (classification & feature detection)
    - Extraction (fact extraction with chosen extractor)
    - Phase-2 parsing (line-item extraction by document type)
    - Analysis (issue detection with chosen analyzer)
    
    Args:
        workflow_log: Workflow log dict from OrchestratorAgent containing pipeline stages
        document_id: Optional document identifier for display
    """
    if not workflow_log:
        st.warning("No workflow log available for pipeline visualization.")
        return
    
    # Extract pipeline stages
    pre_extraction = workflow_log.get("pre_extraction", {})
    extraction = workflow_log.get("extraction", {})
    analysis = workflow_log.get("analysis", {})
    
    # Document header
    doc_label = f"Document {document_id}" if document_id else "Document Analysis"
    workflow_id = workflow_log.get("workflow_id", "N/A")
    timestamp = workflow_log.get("timestamp", "N/A")
    
    # Wrap entire pipeline in an expander/accordion
    with st.expander(f"📊 Pipeline Workflow: {doc_label}", expanded=True):
        st.caption(f"Workflow ID: `{workflow_id}` | Timestamp: `{timestamp}`")
        
        # Create DAG visualization with custom CSS
        dag_html = _build_dag_html(pre_extraction, extraction, analysis)
        
        components.html(dag_html, height=800, scrolling=True)
        
        # Expandable detailed logs
        with st.expander("🔍 View Detailed Pipeline Logs", expanded=False):
            _render_detailed_logs(pre_extraction, extraction, analysis)


def _build_dag_html(pre_extraction: Dict, extraction: Dict, analysis: Dict, live_update: bool = False) -> str:
    """Build HTML representation of the DAG with status indicators.
    
    Args:
        pre_extraction: Pre-extraction stage data
        extraction: Extraction stage data
        analysis: Analysis stage data
        live_update: Whether this is a live update (shows in-progress states)
        
    Returns:
        HTML string with styled DAG visualization
    """
    # Extract key information
    classification = pre_extraction.get("classification", {})
    doc_type = classification.get("document_type", "unknown")
    confidence = classification.get("confidence", 0.0)
    
    extractor = pre_extraction.get("extractor_selected", "unknown")
    extractor_reason = pre_extraction.get("extractor_reason", "")
    
    fact_count = extraction.get("fact_count", 0)
    
    # Determine stage completion
    has_pre_extraction = bool(pre_extraction)
    has_extraction = bool(extraction and fact_count > 0)
    has_analysis = bool(analysis.get("result"))
    
    # Phase-2 line item counts
    receipt_items = extraction.get("receipt_item_count", 0)
    medical_items = extraction.get("medical_item_count", 0)
    dental_items = extraction.get("dental_item_count", 0)
    insurance_items = extraction.get("insurance_item_count", 0)
    fsa_items = extraction.get("fsa_item_count", 0)
    
    phase2_count = receipt_items + medical_items + dental_items + insurance_items + fsa_items
    
    analyzer = analysis.get("analyzer", "unknown")
    analysis_mode = analysis.get("mode", "unknown")
    
    result = analysis.get("result")
    issue_count = len(result.issues) if result and hasattr(result, 'issues') else 0
    
    # Determine phase-2 label based on document type
    phase2_label = "Phase-2 Parsing"
    if doc_type == "pharmacy_receipt":
        phase2_label = "Receipt Line Items"
    elif doc_type == "medical_bill":
        phase2_label = "Medical Line Items"
    elif doc_type == "dental_bill":
        phase2_label = "Dental Line Items"
    elif doc_type in ("insurance_eob", "insurance_claim_history", "insurance_document"):
        phase2_label = "Insurance Claims"
    elif doc_type == "fsa_claim_history":
        phase2_label = "FSA Claims"
    
    # Build HTML
    html = f"""
    <style>
        .dag-container {{
            display: flex;
            flex-direction: column;
            gap: 24px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
            border-radius: 12px;
            margin: 16px 0;
        }}
        
        .dag-row {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        
        .dag-node {{
            flex: 1;
            padding: 16px 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
            transition: transform 0.2s;
        }}
        
        .dag-node:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .dag-node-title {{
            font-weight: 700;
            font-size: 14px;
            color: #1a202c;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .dag-node-content {{
            font-size: 13px;
            color: #4a5568;
            line-height: 1.6;
        }}
        
        .dag-arrow {{
            color: #667eea;
            font-size: 24px;
            font-weight: bold;
        }}
        
        .dag-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            background: #e6fffa;
            color: #047857;
        }}
        
        .dag-badge.warning {{
            background: #fef3c7;
            color: #92400e;
        }}
        
        .dag-badge.info {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        .dag-metric {{
            font-weight: 600;
            color: #667eea;
        }}
    </style>
    
    <div class="dag-container">
        <!-- Stage 1: Pre-Extraction -->
        <div class="dag-row">
            <div class="dag-node">
                <div class="dag-node-title">
                    🔍 Stage 1: Pre-Extraction
                </div>
                <div class="dag-node-content">
                    {'<strong>Status:</strong> <span class="dag-badge warning">⏳ In Progress</span>' if not has_pre_extraction else f'''
                    <strong>Document Type:</strong> <span class="dag-badge">{doc_type}</span><br/>
                    <strong>Confidence:</strong> <span class="dag-metric">{confidence:.0%}</span><br/>
                    <strong>Extractor Selected:</strong> <span class="dag-badge info">{extractor}</span><br/>
                    <em style="font-size: 11px;">Reason: {extractor_reason}</em><br/>
                    <strong>Status:</strong> <span class="dag-badge">✓ Complete</span>
                    '''}
                </div>
            </div>
            <div class="dag-arrow">↓</div>
        </div>
        
        <!-- Stage 2: Extraction -->
        <div class="dag-row">
            <div class="dag-node">
                <div class="dag-node-title">
                    🎯 Stage 2: Fact Extraction
                </div>
                <div class="dag-node-content">
                    {'<strong>Status:</strong> <span class="dag-badge warning">⏳ Waiting</span>' if not has_pre_extraction else 
                     '<strong>Status:</strong> <span class="dag-badge warning">⏳ In Progress</span>' if not has_extraction else f'''
                    <strong>Extractor:</strong> <span class="dag-badge">{extraction.get('extractor', 'N/A')}</span><br/>
                    <strong>Facts Extracted:</strong> <span class="dag-metric">{fact_count}</span> fields<br/>
                    <strong>Status:</strong> <span class="dag-badge">✓ Complete</span>
                    '''}
                </div>
            </div>
            <div class="dag-arrow">↓</div>
        </div>
        
        <!-- Stage 3: Phase-2 Line Item Parsing (if applicable) -->
        {_build_phase2_node(phase2_label, phase2_count, doc_type, extraction, has_extraction) if (has_extraction or not live_update) and phase2_count > 0 else ""}
        
        <!-- Stage 4: Analysis -->
        <div class="dag-row">
            <div class="dag-node">
                <div class="dag-node-title">
                    🚨 Stage {"4" if phase2_count > 0 else "3"}: Issue Analysis
                </div>
                <div class="dag-node-content">
                    {'<strong>Status:</strong> <span class="dag-badge warning">⏳ Waiting</span>' if not has_extraction else
                     '<strong>Status:</strong> <span class="dag-badge warning">⏳ In Progress</span>' if not has_analysis else f'''
                    <strong>Analyzer:</strong> <span class="dag-badge info">{analyzer}</span><br/>
                    <strong>Mode:</strong> <span class="dag-badge">{analysis_mode}</span><br/>
                    <strong>Issues Found:</strong> <span class="dag-metric">{issue_count}</span><br/>
                    <strong>Status:</strong> <span class="dag-badge">✓ Complete</span>
                    '''}
                </div>
            </div>
        </div>
    </div>
    """
    
    return html


def _build_phase2_node(label: str, count: int, doc_type: str, extraction: Dict, has_extraction: bool = True) -> str:
    """Build Phase-2 parsing node HTML if line items were extracted.
    
    Args:
        label: Display label for the phase-2 stage
        count: Number of line items extracted
        doc_type: Document type
        extraction: Extraction stage data for error checking
        has_extraction: Whether extraction stage is complete
        
    Returns:
        HTML string for the phase-2 node
    """
    # Check for extraction errors
    error_keys = [
        "receipt_extraction_error",
        "medical_extraction_error",
        "dental_extraction_error",
        "insurance_extraction_error",
        "fsa_extraction_error"
    ]
    
    errors = [extraction.get(key) for key in error_keys if extraction.get(key)]
    
    # Determine status based on completion
    if not has_extraction:
        status = "⏳ Waiting"
        badge_class = "warning"
    elif errors:
        status = "⚠ Error"
        badge_class = "warning"
    else:
        status = "✓ Complete"
        badge_class = ""
    
    return f"""
        <div class="dag-row">
            <div class="dag-node">
                <div class="dag-node-title">
                    📋 Stage 3: {label}
                </div>
                <div class="dag-node-content">
                    {f'<strong>Line Items Extracted:</strong> <span class="dag-metric">{count}</span><br/>' if has_extraction else ''}
                    <strong>Status:</strong> <span class="dag-badge {badge_class}">{status}</span>
                    {f'<br/><em style="color: #dc2626; font-size: 11px;">Error: {errors[0][:80]}...</em>' if errors else ''}
                </div>
            </div>
            <div class="dag-arrow">↓</div>
        </div>
    """


def _render_detailed_logs(pre_extraction: Dict, extraction: Dict, analysis: Dict):
    """Render detailed logs in expandable JSON format.
    
    Args:
        pre_extraction: Pre-extraction stage data
        extraction: Extraction stage data
        analysis: Analysis stage data
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Pre-Extraction Log**")
        # Remove result object for cleaner JSON
        clean_pre = {k: v for k, v in pre_extraction.items() if k != 'result'}
        st.json(clean_pre)
    
    with col2:
        st.markdown("**Extraction Log**")
        # Remove facts for cleaner display (can be large)
        clean_extraction = {k: v for k, v in extraction.items() if k not in ['facts', 'result']}
        st.json(clean_extraction)
    
    with col3:
        st.markdown("**Analysis Log**")
        # Remove full result object
        clean_analysis = {k: v for k, v in analysis.items() if k != 'result'}
        st.json(clean_analysis)
    
    # Show extracted facts separately
    if extraction.get("facts"):
        st.markdown("**Extracted Facts**")
        st.json(extraction.get("facts", {}))


def render_pipeline_comparison(workflow_logs: List[Dict[str, Any]]):
    """Render side-by-side comparison of multiple document pipelines.
    
    Useful for batch analysis to compare processing paths across documents.
    
    Args:
        workflow_logs: List of workflow log dicts from multiple document analyses
    """
    if not workflow_logs:
        st.info("No workflow logs available for comparison.")
        return
    
    st.markdown("### 📊 Multi-Document Pipeline Comparison")
    
    # Create comparison table
    comparison_data = []
    
    for idx, log in enumerate(workflow_logs, 1):
        pre = log.get("pre_extraction", {})
        extraction = log.get("extraction", {})
        analysis = log.get("analysis", {})
        
        classification = pre.get("classification", {})
        
        comparison_data.append({
            "Doc": f"#{idx}",
            "Type": classification.get("document_type", "unknown"),
            "Confidence": f"{classification.get('confidence', 0.0):.0%}",
            "Extractor": pre.get("extractor_selected", "N/A"),
            "Facts": extraction.get("fact_count", 0),
            "Line Items": sum([
                extraction.get("receipt_item_count", 0),
                extraction.get("medical_item_count", 0),
                extraction.get("dental_item_count", 0),
                extraction.get("insurance_item_count", 0),
                extraction.get("fsa_item_count", 0),
            ]),
            "Analyzer": analysis.get("analyzer", "N/A"),
            "Issues": len(analysis.get("result", {}).issues) if hasattr(analysis.get("result", {}), 'issues') else 0,
        })
    
    st.table(comparison_data)
