# app.py

import streamlit as st

from _modules.privacy_ui import render_privacy_dialog
from _modules.ui_documents import render_document_inputs
from _modules.document_identity import maybe_enhance_identity
from _modules.openai_analysis_provider import OpenAIAnalysisProvider
from _modules.orchestrator_agent import OrchestratorAgent
from _modules.serialization import analysis_to_dict

from _modules.llm_interface import ProviderRegistry
from _modules.ui import (
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

try:
    from _modules.medgemma_hosted_provider import MedGemmaHostedProvider
except Exception:
    MedGemmaHostedProvider = None

from _modules.runtime_flags import debug_enabled


ENGINE_OPTIONS = {
    "Smart (Recommended)": None,
    "gpt-4o-mini": "gpt-4o-mini",
    "gemini-3-flash-preview": "gemini-3-flash-preview",
    "Local (Offline)": "heuristic",
}


# ==================================================
# Savings aggregation helpers
# ==================================================


def render_total_savings_summary(total_potential_savings: float, per_document_savings: dict):
    """
    Render a single aggregate summary once per run.
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
    setup_page()
    inject_css()
    render_header()
    render_demo_documents()


# ==================================================
# Provider registration
# ==================================================
def register_providers():
    # --- MedGemma ---
    if MedGemmaHostedProvider is not None:
        try:
            provider = MedGemmaHostedProvider()
            if provider.health_check():
                ProviderRegistry.register("medgemma-4b-it", provider)
        except Exception:
            pass

    # --- OpenAI ---
    try:
        openai_provider = OpenAIAnalysisProvider()
        if openai_provider.health_check():
            # Primary key
            ProviderRegistry.register("gpt-4o-mini", openai_provider)

            # 👇 ADD THIS ALIAS
            ProviderRegistry.register("openai", openai_provider)

    except Exception as e:
        print(f"[openai] provider registration failed: {e}")



# ==================================================
# Main analysis flow (single document)
# ==================================================
def handle_analysis(bill_text: str, provider_key: str, document_id: str):
    if not bill_text.strip():
        return

    provider = ProviderRegistry.get(provider_key)
    if not provider:
        show_analysis_error("No analysis provider registered.")
        return

    with st.spinner(f"🚜 Analyzing document {document_id}…"):
        try:
            result = provider.analyze_document(bill_text)
        except Exception as e:
            show_analysis_error(f"Analysis failed: {e}")
            return

    st.markdown(f"## 📄 Document `{document_id}`")
    show_analysis_success()
    render_results(result)


# ==================================================
# App entry
# ==================================================
def main():
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
    render_privacy_dialog()

    # --------------------------------------------------
    # Document input (UI ONCE)
    # --------------------------------------------------
    documents = render_document_inputs()

    # --------------------------------------------------
    # Analysis provider selector (user-facing)
    # --------------------------------------------------
    if debug_enabled():
        providers = ProviderRegistry.list()
        selected_provider = render_provider_selector(providers)  # keep in debug for now
    else:
        engine_label = st.selectbox(
            "Analysis Engine",
            options=list(ENGINE_OPTIONS.keys()),
            index=0,
        )
        selected_provider = ENGINE_OPTIONS[engine_label]

    # --------------------------------------------------
    # Debug controls (sidebar only)
    # --------------------------------------------------
    if debug_enabled():
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
    # Orchestrator (NO UI inside)
    # --------------------------------------------------
    agent = OrchestratorAgent(
        extractor_override=extractor_override,
        analyzer_override=analyzer_override or selected_provider,
    )

    # --------------------------------------------------
    # Analyze action
    # --------------------------------------------------
    analyze_clicked = render_analyze_button()

    if analyze_clicked:
        if not documents:
            show_empty_warning()
            return
        if selected_provider == "heuristic":
            show_analysis_error("Local (Offline) analysis isn't wired yet. Use Smart/OpenAI for now.")
            return

        if not documents:
            show_empty_warning()
            return

        # Aggregate savings across all documents for this run
        total_potential_savings = 0.0
        per_document_savings = {}

        for doc in documents:
            with st.spinner(f"🚜 Processing document {doc['document_id']}…"):
                result = agent.run(doc["raw_text"])

                # --------------------------------------------------
                # Session persistence (in-memory, per run)
                # --------------------------------------------------
                st.session_state.setdefault("workflow_logs", {})
                st.session_state["workflow_logs"][doc["document_id"]] = result.get("_workflow_log")

            # Persist results
            doc["facts"] = result.get("facts")
            doc["analysis"] = result.get("analysis")
            doc["analysis_json"] = analysis_to_dict(result["analysis"])
            doc["_orchestration"] = result.get("_orchestration")

            # Identity AFTER facts
            maybe_enhance_identity(doc)

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


            # Render results (unique per doc)
            st.markdown(f"## 📄 Document `{doc['document_id']}`")
            show_analysis_success()
            render_results(doc["analysis"])

        total_potential_savings = round(total_potential_savings, 2)

        # Persist aggregate metrics (optional, but useful for debug / export later)
        st.session_state.setdefault("aggregate_metrics", {})
        st.session_state["aggregate_metrics"]["total_potential_savings"] = total_potential_savings
        st.session_state["aggregate_metrics"]["per_document_savings"] = per_document_savings

        # Render the aggregate summary ONCE (after all documents)
        render_total_savings_summary(total_potential_savings, per_document_savings)

    # --------------------------------------------------
    # Debug output (read-only)
    # --------------------------------------------------
    if debug_enabled():
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

    # --------------------------------------------------
    # Footer (ONCE)
    # --------------------------------------------------
    render_footer()


if __name__ == "__main__":
    main()
