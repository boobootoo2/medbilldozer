"""MedBillDozer - Medical billing error detection application.

Main Streamlit application that orchestrates document analysis, provider registration,
and UI rendering for detecting billing, pharmacy, dental, and insurance claim issues.
"""
# app.py
import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import json


from _modules.ui.privacy_ui import render_privacy_dialog
from _modules.ui.ui_documents import render_document_inputs
from _modules.ui.doc_assistant import render_doc_assistant, render_contextual_help
from _modules.core.document_identity import maybe_enhance_identity
from _modules.core.orchestrator_agent import OrchestratorAgent
from _modules.utils.serialization import analysis_to_dict

from _modules.core.coverage_matrix import build_coverage_matrix
from _modules.ui.ui_coverage_matrix import render_coverage_matrix

from _modules.providers.openai_analysis_provider import OpenAIAnalysisProvider
from _modules.providers.gemini_analysis_provider import GeminiAnalysisProvider


from _modules.core.transaction_normalization import (
    normalize_line_items,
    deduplicate_transactions,
)


from _modules.providers.llm_interface import ProviderRegistry
from _modules.ui.ui import (
    setup_page,
    inject_css,
    render_header,
    render_demo_documents,
    render_provider_selector,
    render_analyze_button,
    render_results,
    render_footer,
    show_empty_warning,
    show_analysis_success,
    show_analysis_error,
)
from _modules.ui.ui_pipeline_dag import (
    render_pipeline_comparison,
    create_pipeline_dag_container,
    update_pipeline_dag,
)

try:
    from _modules.providers.medgemma_hosted_provider import MedGemmaHostedProvider
except Exception:
    MedGemmaHostedProvider = None

from _modules.utils.runtime_flags import debug_enabled
from _modules.utils.config import (
    get_config,
    is_assistant_enabled,
    is_dag_enabled,
    is_debug_enabled,
    is_privacy_ui_enabled,
    is_coverage_matrix_enabled,
)

from _modules.ui.billdozer_widget import (
    install_billdozer_bridge,
    dispatch_widget_message,
)



ENGINE_OPTIONS = {
    "Smart (Recommended)": None,
    "gpt-4o-mini": "gpt-4o-mini",
    "gemini-3-flash-preview": "gemini-3-flash-preview",
    "Local (Offline)": "heuristic",
}


_WIDGET_HTML_CACHE = None  # module scope
BILLDOZER_TOKEN = "BILLDOZER_v1"


def get_billdozer_widget_html() -> str:
    global _WIDGET_HTML_CACHE

    if _WIDGET_HTML_CACHE is None:
        widget_path = (
            Path(__file__).parent
            / "static"
            / "bulldozer_animation.html"
        )
        html = widget_path.read_text(encoding="utf-8")

        # 🔧 Hide controls when embedded in Streamlit
        css_override = """
        <style>
          .controls {
            display: none !important;
          }
        </style>
        """

        # Inject just before </head>
        html = html.replace("</head>", css_override + "\n</head>")

        _WIDGET_HTML_CACHE = html

    return _WIDGET_HTML_CACHE

# ==================================================
# Savings aggregation helpers
# ==================================================


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


# ==================================================
# Bootstrap UI
# ==================================================
def bootstrap_ui():
    """Initialize and render core UI components.
    
    Sets up page configuration, CSS styles, header, and demo documents.
    Must be called at the start of the application.
    """
    setup_page()
    inject_css()
    render_header()
    render_contextual_help('demo')
    render_demo_documents()


# ==================================================
# Provider registration
# ==================================================
def register_providers():
    """Register available LLM analysis providers.
    
    Attempts to register MedGemma, Gemini, and OpenAI providers.
    Only registers providers that pass health checks.
    """
    # --- MedGemma ---
    try:
        provider = MedGemmaHostedProvider()
        if provider.health_check():
            ProviderRegistry.register("medgemma-4b-it", provider)
    except Exception as e:
        print(f"[medgemma] provider registration failed: {e}")

    # --- Gemini ---
    try:
        gemini_provider = GeminiAnalysisProvider("gemini-1.5-flash")
        if gemini_provider.health_check():
            ProviderRegistry.register("gemini-1.5-flash", gemini_provider)
    except Exception as e:
        print(f"[gemini] provider registration failed: {e}")

    # --- OpenAI ---
    try:
        openai_provider = OpenAIAnalysisProvider("gpt-4o-mini")
        if openai_provider.health_check():
            ProviderRegistry.register("gpt-4o-mini", openai_provider)
    except Exception as e:
        print(f"[openai] provider registration failed: {e}")


# ==================================================
# App entry
# ==================================================
def main():
    """Main application entry point.
    
    Orchestrates the complete workflow:
    1. Bootstrap UI and register providers
    2. Render privacy dialog
    3. Collect document inputs
    4. Analyze documents with selected provider
    5. Display results and savings summary
    6. Render coverage matrix and debug info
    """
    # --------------------------------------------------
    # Bootstrap + providers
    # --------------------------------------------------
    bootstrap_ui()
    register_providers()

    # --------------------------------------------------
    # Defaults (can be overridden in debug)
    # --------------------------------------------------
    extractor_override = None
    analyzer_override = None

    # --------------------------------------------------
    # Privacy (session-scoped)
    # --------------------------------------------------
    if is_privacy_ui_enabled():
        render_privacy_dialog()

    # --------------------------------------------------
    # Documentation Assistant (sidebar)
    # --------------------------------------------------
    if is_assistant_enabled():
        render_doc_assistant()

    # --------------------------------------------------
    # Document input (UI ONCE)
    # --------------------------------------------------
    render_contextual_help('input')
    documents = render_document_inputs()

    # --------------------------------------------------
    # Analysis provider selector (user-facing)
    # --------------------------------------------------
    # Use config debug setting OR legacy runtime flag
    debug_mode = is_debug_enabled() or debug_enabled()
    
    if debug_mode:
        providers = ProviderRegistry.list()
        selected_provider = render_provider_selector(providers)  # keep in debug for now
    else:
        engine_label = st.selectbox(
            "Analysis Engine",
            options=list(ENGINE_OPTIONS.keys()),
            index=0,
        )
        selected_provider = ENGINE_OPTIONS[engine_label]

    if is_coverage_matrix_enabled():
        coverage_rows = build_coverage_matrix(documents)
        render_coverage_matrix(coverage_rows)

    # --------------------------------------------------
    # Debug controls (sidebar only)
    # --------------------------------------------------
    if debug_mode:
        with st.sidebar:
            st.markdown("## 🧪 Debug Mode")

            extractor_override = st.selectbox(
                "Fact Extraction Model",
                {
                    "Agent decides": None,
                    "gpt-4o-mini": "gpt-4o-mini",
                    "gemini-3-flash-preview": "gemini-3-flash-preview",
                    "Local heuristic": "heuristic",
                }.items(),
                format_func=lambda x: x[0],
            )[1]

            analyzer_override = st.selectbox(
                "Analysis Model",
                {
                    "Agent decides": None,
                    "gpt-4o-mini": "gpt-4o-mini",
                    "medgemma-4b-it": "medgemma-4b-it",
                }.items(),
                format_func=lambda x: x[0],
            )[1]

    # --------------------------------------------------
    # Resolve Smart (None) to a concrete analyzer
    # --------------------------------------------------
    if selected_provider is None:
        selected_provider = "gpt-4o-mini"

    # --------------------------------------------------
    # Orchestrator (NO UI inside)
    # --------------------------------------------------
    agent = OrchestratorAgent(
        extractor_override=extractor_override,
        analyzer_override=analyzer_override or selected_provider,
    )


    # --------------------------------------------------
    # Cross-document transaction collection (per run)
    # --------------------------------------------------
    all_normalized_transactions = []


    # --------------------------------------------------
    # Analyze action
    # --------------------------------------------------
    analyze_clicked = render_analyze_button()

    if analyze_clicked:
        if not documents:
            show_empty_warning()
            render_contextual_help('error')
            return
        if selected_provider == "heuristic":
            show_analysis_error("Local (Offline) analysis isn't wired yet. Use Smart/OpenAI for now.")
            render_contextual_help('error')
            return

        # Show analyzing context
        render_contextual_help('analyzing')

        # Aggregate savings across all documents for this run
        total_potential_savings = 0.0
        per_document_savings = {}
        

        install_billdozer_bridge()
        components.html(get_billdozer_widget_html(), height=220, scrolling=False)

        dispatch_widget_message("billie", "Bill Dozing Statements")

        if "billdozer_widget_initialized" not in st.session_state:
            dispatch_widget_message("billie", "Hi Billy, any more docs?")
            st.session_state.billdozer_widget_initialized = True





        for idx, doc in enumerate(documents, 1):
            speaker = "billie" if idx % 2 == 1 else "billy"


            result = agent.run(doc["raw_text"])

            dispatch_widget_message(
                speaker,
                f"Finished analyzing Document {idx}"
            )

            # Use index-based ID initially (will be replaced with friendly ID after facts extraction)
            initial_doc_id = f"Document {idx}"
            
            # Render document header first
            st.markdown(f"## 📄 {initial_doc_id}")
            
            # Create DAG container immediately (shows "In Progress" state) if enabled
            dag_placeholder = None
            if is_dag_enabled():
                dag_expander, dag_placeholder = create_pipeline_dag_container(document_id=str(idx))
            



            # --------------------------------------------------
            # Session persistence (in-memory, per run)
            # --------------------------------------------------
            st.session_state.setdefault("workflow_logs", {})
            st.session_state["workflow_logs"][doc["document_id"]] = result.get("_workflow_log")
            
            # Update DAG with completed workflow (AFTER spinner closes)
            if is_dag_enabled() and dag_placeholder:
                update_pipeline_dag(dag_placeholder, result.get("_workflow_log"))

            # Persist results
            doc["facts"] = result.get("facts")
            doc["analysis"] = result.get("analysis")
            doc["analysis_json"] = analysis_to_dict(result["analysis"])
            doc["_orchestration"] = result.get("_orchestration")
            doc["_workflow_log"] = result.get("_workflow_log")

            # Identity AFTER facts
            maybe_enhance_identity(doc)
            
            # Update DAG again with friendly document name now that we have it
            if is_dag_enabled() and dag_placeholder:
                friendly_doc_id = doc.get("document_id") if doc.get("document_id") != initial_doc_id else None
                if friendly_doc_id:
                    update_pipeline_dag(dag_placeholder, result.get("_workflow_log"), document_id=friendly_doc_id)

            # --------------------------------------------------
            # Transaction normalization (document-independent)
            # --------------------------------------------------
            line_items = (result.get("facts") or {}).get("line_items", [])

            if not line_items:
                st.warning(f"No line items extracted for document {doc['document_id']}")

            normalized_transactions = normalize_line_items(
                line_items=line_items,
                source_document_id=doc["document_id"],
            )

            all_normalized_transactions.extend(normalized_transactions)

            # --------------------------------------------------
            # Cross-document de-duplication (ONCE per run)
            # --------------------------------------------------
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

            # --------------------------------------------------
            # Savings aggregation
            # --------------------------------------------------
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

    # --------------------------------------------------
    # Debug output (read-only)
    # --------------------------------------------------
    if debug_mode:
        with st.sidebar:
            st.markdown("### Documents")
            st.json(documents)

            st.markdown("### Orchestration Decisions")
            st.json({
                d["document_id"]: d.get("_orchestration")
                for d in documents
            })

            st.markdown("### Aggregate Metrics")
            st.json(st.session_state.get("aggregate_metrics", {}))

            st.markdown("### Session State")
            st.json(dict(st.session_state))
            st.markdown("### Normalized Transactions")
            st.json(st.session_state.get("normalized_transactions", []))

            st.markdown("### Transaction Provenance")
            st.json(st.session_state.get("transaction_provenance", {}))

            st.markdown("### Coverage Matrix (Raw)")
            st.json([row.__dict__ for row in coverage_rows])
            

    # --------------------------------------------------
    # Footer (ONCE)
    # --------------------------------------------------
    render_footer()


if __name__ == "__main__":
    main()
