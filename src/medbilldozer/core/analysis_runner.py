"""Document analysis workflow runner and coordination."""

import streamlit as st
from typing import List, Dict, Optional, Callable, Any

from medbilldozer.core.orchestrator_agent import OrchestratorAgent
from medbilldozer.core.document_identity import maybe_enhance_identity
from medbilldozer.core.transaction_normalization import (
    normalize_line_items,
    deduplicate_transactions,
)
from medbilldozer.core.coverage_matrix import build_coverage_matrix
from medbilldozer.ui.ui_coverage_matrix import render_coverage_matrix
from medbilldozer.ui.ui_pipeline_dag import (
    render_pipeline_comparison,
    create_pipeline_dag_container,
    update_pipeline_dag,
)
from medbilldozer.ui.ui import (
    render_results,
    show_empty_warning,
    show_analysis_success,
    show_analysis_error,
)
from medbilldozer.ui.doc_assistant import render_contextual_help
from medbilldozer.ui.billdozer_widget import (
    install_billdozer_bridge,
    dispatch_widget_message,
)
from medbilldozer.utils.serialization import analysis_to_dict
from medbilldozer.utils.config import (
    get_config,
    is_dag_enabled,
    is_coverage_matrix_enabled,
)
from medbilldozer.ui.document_status_cards import (
    initialize_document_status,
    create_status_card_placeholder,
    update_status_card,
)


def render_total_savings_summary(total_potential_savings: float, per_document_savings: dict):
    """Render aggregate savings summary across all analyzed documents.

    Args:
        total_potential_savings: Total potential savings amount
        per_document_savings: Dict mapping document IDs to their savings amounts
    """
    if total_potential_savings <= 0:
        return

    st.markdown("## 💰 Estimated Total Potential Savings")
    st.metric(
        label="Across all analyzed documents",
        value=f"${total_potential_savings:,.2f}",
    )

    with st.expander("See savings by document"):
        for doc_id, amount in per_document_savings.items():
            st.markdown(f"- **{doc_id}**: ${amount:,.2f}")


def run_document_analysis(
    documents: List[Dict[str, Any]],
    agent: OrchestratorAgent,
    analyze_clicked: bool,
) -> Optional[Dict[str, Any]]:
    """Run analysis on all documents and return aggregate results.

    Args:
        documents: List of document dictionaries with raw_text
        agent: Configured OrchestratorAgent instance
        analyze_clicked: True if analysis was triggered by button click

    Returns:
        Dict with total_savings, per_document_savings, and documents, or None if error
    """
    if not documents:
        show_empty_warning()
        render_contextual_help('error')
        return None

    # Aggregate savings across all documents for this run
    total_potential_savings = 0.0
    per_document_savings = {}

    # Cross-document transaction collection
    all_normalized_transactions = []

    install_billdozer_bridge()
    st.session_state.setdefault("show_billdozer_widget", True)

    # Billdozer widget messaging
    st.session_state.setdefault("billdozer_widget_initialized", False)

    # Greet once per session
    if (
        st.session_state.show_billdozer_widget
        and not st.session_state.billdozer_widget_initialized
    ):
        dispatch_widget_message("billie", "Hi Billy, any more docs?")
        st.session_state.billdozer_widget_initialized = True

    # Analysis start message (ONCE per Analyze click)
    if (
        analyze_clicked
        and st.session_state.get('show_billdozer_widget', False)
        and not st.session_state.get('billdozer_analysis_started', False)
    ):
        dispatch_widget_message("billie", "Bill Dozing Statements")
        st.session_state.billdozer_analysis_started = True

    # Initialize status tracking
    st.session_state.setdefault('doc_status_tracking', {})
    status_placeholders = {}

    for idx, doc in enumerate(documents, 1):
        speaker = "billie" if idx % 2 == 1 else "billy"

        # Use index-based ID initially (will be replaced with friendly ID after facts extraction)
        initial_doc_id = f"Document {idx}"

        # Initialize status tracking for this document
        doc_key = f"doc_{idx}"
        initialize_document_status(doc_key, initial_doc_id)

        # Create status card placeholder (rendered before header)
        status_placeholder = create_status_card_placeholder(doc_key)
        status_placeholders[doc_key] = status_placeholder

        # Render document header first
        st.markdown(f"## 📄 {initial_doc_id}")

        # Create DAG container immediately (shows initial plan) if enabled
        dag_placeholder = None
        if is_dag_enabled():
            dag_expander, dag_placeholder = create_pipeline_dag_container(document_id=str(idx))

        # Progress callback for real-time status updates
        def progress_callback(workflow_log, step_status):
            # Update status card (NEW)
            if status_placeholder:
                update_status_card(status_placeholder, doc_key, step_status, workflow_log)

            # Update DAG (existing)
            if dag_placeholder and is_dag_enabled():
                update_pipeline_dag(dag_placeholder, workflow_log, document_id=str(idx), step_status=step_status)

        # Run analysis with progress callback (wrapped in try-except for error handling)
        try:
            result = agent.run(doc["raw_text"], progress_callback=progress_callback)

            # Mark complete
            st.session_state.doc_status_tracking[doc_key]["status"] = "complete"
            st.session_state.doc_status_tracking[doc_key]["current_phase"] = "complete"
            update_status_card(status_placeholder, doc_key, "complete")

            dispatch_widget_message(
                speaker,
                f"Finished analyzing {initial_doc_id}"
            )
        except Exception as e:
            # Mark failed
            st.session_state.doc_status_tracking[doc_key]["status"] = "failed"
            st.session_state.doc_status_tracking[doc_key]["current_phase"] = "failed"
            st.session_state.doc_status_tracking[doc_key]["error_message"] = str(e)
            update_status_card(status_placeholder, doc_key, "failed")

            # Show error to user
            show_analysis_error(str(e))
            continue  # Skip to next document

        # Session persistence (in-memory, per run)
        st.session_state.setdefault("workflow_logs", {})
        st.session_state["workflow_logs"][doc["document_id"]] = result.get("_workflow_log")

        # Persist results
        doc["facts"] = result.get("facts")
        doc["analysis"] = result.get("analysis")
        doc["analysis_json"] = analysis_to_dict(result["analysis"])
        doc["_orchestration"] = result.get("_orchestration")
        doc["_workflow_log"] = result.get("_workflow_log")

        # Identity AFTER facts
        maybe_enhance_identity(doc)

        # Update friendly name in status tracking
        if doc.get("document_id") != initial_doc_id:
            st.session_state.doc_status_tracking[doc_key]["friendly_name"] = doc["document_id"]
            # Refresh status card with new name
            update_status_card(status_placeholder, doc_key, "complete")

        # Update DAG again with friendly document name now that we have it
        if is_dag_enabled() and dag_placeholder:
            friendly_doc_id = doc.get("document_id") if doc.get("document_id") != initial_doc_id else None
            if friendly_doc_id:
                update_pipeline_dag(dag_placeholder, result.get("_workflow_log"), document_id=friendly_doc_id)

        # Transaction normalization (document-independent)
        line_items = (result.get("facts") or {}).get("line_items", [])

        if not line_items:
            st.warning(f"No line items extracted for document {doc['document_id']}")

        normalized_transactions = normalize_line_items(
            line_items=line_items,
            source_document_id=doc["document_id"],
        )

        all_normalized_transactions.extend(normalized_transactions)

        # Cross-document de-duplication (ONCE per run)
        unique_transactions, transaction_provenance = deduplicate_transactions(
            all_normalized_transactions
        )

        st.session_state["normalized_transactions"] = [
            tx.__dict__ for tx in unique_transactions.values()
        ]

        st.session_state["transaction_provenance"] = transaction_provenance

        # Debug storage
        st.session_state.setdefault("extracted_facts", {})
        st.session_state["extracted_facts"][doc["document_id"]] = doc.get("facts")

        # Savings aggregation
        analysis = doc.get("analysis")

        doc_savings = 0.0
        if analysis and hasattr(analysis, "meta"):
            doc_savings = analysis.meta.get("total_max_savings", 0.0)

        per_document_savings[doc["document_id"]] = doc_savings
        total_potential_savings += doc_savings

        # Render results (unique per doc) - DAG already shown above
        show_analysis_success()
        # Pass dict with just issues (DAG already rendered progressively above)
        render_results({
            "issues": doc["analysis"].issues if doc.get("analysis") else [],
            "_workflow_log": None  # Don't render DAG again
        })

    total_potential_savings = round(total_potential_savings, 2)

    # Persist aggregate metrics (optional, but useful for debug / export later)
    st.session_state.setdefault("aggregate_metrics", {})
    st.session_state["aggregate_metrics"]["total_potential_savings"] = total_potential_savings
    st.session_state["aggregate_metrics"]["per_document_savings"] = per_document_savings

    # Render the aggregate summary ONCE (after all documents)
    render_total_savings_summary(total_potential_savings, per_document_savings)

    # Render coverage matrix if enabled
    if is_coverage_matrix_enabled():
        coverage_rows = build_coverage_matrix(documents)
        render_coverage_matrix(coverage_rows)

    # Render multi-document pipeline comparison if multiple documents and DAG enabled
    if is_dag_enabled() and len(documents) > 1:
        config = get_config()
        show_comparison = config.get("features.dag.show_comparison_table", True)
        if show_comparison:
            st.divider()
            workflow_logs = [doc.get("_workflow_log") for doc in documents if doc.get("_workflow_log")]
            if workflow_logs:
                render_pipeline_comparison(workflow_logs)

    # Show results context help
    render_contextual_help('results')

    return {
        "total_savings": total_potential_savings,
        "per_document_savings": per_document_savings,
        "documents": documents,
    }


def render_cached_results(documents: List[Dict[str, Any]], total_potential_savings: float, per_document_savings: dict):
    """Render previously analyzed results from cache.

    Args:
        documents: List of document dictionaries with analysis results
        total_potential_savings: Total potential savings amount
        per_document_savings: Dict mapping document IDs to their savings amounts
    """
    # Re-render results without re-analyzing
    for doc in documents:
        if doc.get("analysis"):
            show_analysis_success()
            render_results({
                "issues": doc["analysis"].issues,
                "_workflow_log": doc.get("_workflow_log")
            })

    render_total_savings_summary(total_potential_savings, per_document_savings)

    if is_coverage_matrix_enabled():
        coverage_rows = build_coverage_matrix(documents)
        render_coverage_matrix(coverage_rows)
