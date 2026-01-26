"""MedBillDozer - Medical billing error detection application.

Main Streamlit application that orchestrates document analysis, provider registration,
and UI rendering for detecting billing, pharmacy, dental, and insurance claim issues.
"""
# app.py
import os
import streamlit as st


from _modules.ui.privacy_ui import render_privacy_dialog
from _modules.ui.ui_documents import render_document_inputs
from _modules.ui.doc_assistant import render_doc_assistant, render_contextual_help
from _modules.ui.guided_tour import (
    initialize_tour_state,
    maybe_launch_tour,
    check_tour_progression,
    render_tour_widget,
    render_tour_controls,
    advance_tour_step,
    open_sidebar_for_tour,
    install_paste_detector,
    install_copy_button_detector,
    check_pharmacy_copy_click,
    install_tour_highlight_styles,
    highlight_tour_elements,
)
from _modules.ui.health_profile import (
    render_profile_selector,
    render_profile_details,
    get_profile_context_for_analysis,
)
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
    render_clear_history_button,
    clear_analysis_history,
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
    is_guided_tour_enabled,
)

from _modules.ui.billdozer_widget import (
    get_billdozer_widget_html,
    install_billdozer_bridge,
    dispatch_widget_message,
    render_billdozer_sidebar_widget,
)

from _modules.ui.profile_editor import (
    render_profile_editor,
    is_profile_editor_enabled,
)


def check_access_password() -> bool:
    """Check if access password is required and validate user input.

    Returns:
        bool: True if access is granted, False if password gate should be shown
    """
    # Check if password is set via environment variable
    required_password = os.environ.get('APP_ACCESS_PASSWORD', '')

    # If no password is set, grant access
    if not required_password:
        return True

    # Initialize session state for password
    if 'access_granted' not in st.session_state:
        st.session_state.access_granted = False

    # If already granted, allow access
    if st.session_state.access_granted:
        return True

    # Show password gate
    st.markdown("""
    <div style="text-align: center; padding: 50px 20px;">
        <h1>medBillDozer</h1>
        <p style="font-size: 18px; color: #666; margin-bottom: 30px;">Enter password to access</p>
    </div>
    """, unsafe_allow_html=True)

    # Center the password input
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password_input = st.text_input(
            "Password",
            type="password",
            key="access_password_input",
            label_visibility="collapsed",
            placeholder="Enter access password"
        )

        if st.button("Access App", use_container_width=True, type="primary"):
            if password_input == required_password:
                st.session_state.access_granted = True
                st.rerun()
            else:
                st.error("❌ Incorrect password. Please try again.")

    return False


def should_enable_guided_tour() -> bool:
    """Check if guided tour should be enabled based on environment variable.

    Returns:
        bool: True if tour should be enabled
    """
    # Check environment variable first (overrides config)
    env_tour = os.environ.get('GUIDED_TOUR', '').upper()
    if env_tour in ('TRUE', '1', 'YES', 'ON'):
        return True
    elif env_tour in ('FALSE', '0', 'NO', 'OFF'):
        return False

    # Fall back to config file setting
    return is_guided_tour_enabled()


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


def bootstrap_ui_minimal():
    """Initialize minimal UI components for all pages.

    Sets up page configuration, CSS styles, and header.
    Should be called on all pages (home and profile).
    """
    setup_page()
    inject_css()
    render_header()


def bootstrap_home_page():
    """Initialize home page specific UI components.

    Renders demo documents and contextual help.
    Should only be called on the home page.
    """
    # Skip demo help message when guided tour is active
    if not should_enable_guided_tour():
        render_contextual_help('demo')

    render_demo_documents()

    # Install tour highlight styles for element emphasis
    install_tour_highlight_styles()

    # Install copy button detector for tour (detects pharmacy receipt copy click)
    install_copy_button_detector()

    # Check if pharmacy copy button was clicked
    check_pharmacy_copy_click()


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
    2. Initialize guided tour state
    3. Render privacy dialog
    4. Collect document inputs
    5. Analyze documents with selected provider
    6. Display results and savings summary
    7. Render coverage matrix and debug info
    """
    # --------------------------------------------------
    # Access Control Gate
    # --------------------------------------------------
    if not check_access_password():
        return  # Stop rendering if password not entered

    # --------------------------------------------------
    # Initialize Page Navigation
    # --------------------------------------------------
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'

    # --------------------------------------------------
    # Minimal Bootstrap (for all pages)
    # --------------------------------------------------
    bootstrap_ui_minimal()

    # --------------------------------------------------
    # Guided Tour Controls (sidebar - at top)
    # --------------------------------------------------
    if should_enable_guided_tour():
        render_tour_controls()

    # --------------------------------------------------
    # Guided Tour Widget (sidebar - instructions)
    # --------------------------------------------------
    if should_enable_guided_tour():
        render_tour_widget()
        open_sidebar_for_tour()
        highlight_tour_elements()


    # --------------------------------------------------
    # Page Navigation (sidebar - at top)
    # --------------------------------------------------
    with st.sidebar:
        st.markdown("## 📱 Navigation")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🏠 Home", use_container_width=True, type="primary" if st.session_state.current_page == 'home' else "secondary"):
                st.session_state.current_page = 'home'
                st.rerun()

        with col2:
            if is_profile_editor_enabled():
                if st.button("📋 Profile", use_container_width=True, type="primary" if st.session_state.current_page == 'profile' else "secondary"):
                    st.session_state.current_page = 'profile'
                    st.rerun()

        st.markdown("---")


    # --------------------------------------------------
    # Route to Profile Editor if selected
    # --------------------------------------------------
    if st.session_state.current_page == 'profile' and is_profile_editor_enabled():
        render_profile_editor()
        return  # Skip rest of home page rendering

    # --------------------------------------------------
    # Home Page Specific UI
    # --------------------------------------------------
    bootstrap_home_page()
    register_providers()

    # --------------------------------------------------
    # Guided Tour Initialization
    # --------------------------------------------------
    if should_enable_guided_tour():
        initialize_tour_state()
        maybe_launch_tour()
        # Check tour state at start of render to catch any pending step changes
        check_tour_progression()

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
    # Health Profile (Optional)
    # --------------------------------------------------
    st.markdown("---")
    selected_profile = render_profile_selector()

    if selected_profile:
        render_profile_details(selected_profile)
        st.info("💡 Profile loaded! The analysis will consider this patient's insurance and medical history.")

    st.markdown("---")

    # --------------------------------------------------
    # Document input (UI ONCE)
    # --------------------------------------------------
    render_contextual_help('input')
    documents = render_document_inputs()

    # Install paste detector for tour (triggers immediate detection on paste)
    install_paste_detector()

    # Check tour progression after document input
    check_tour_progression()

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
    # Get profile context if a profile is selected
    profile_context = None
    if selected_profile:
        profile_context = get_profile_context_for_analysis(selected_profile)

    agent = OrchestratorAgent(
        extractor_override=extractor_override,
        analyzer_override=analyzer_override or selected_provider,
        profile_context=profile_context,
    )


    # --------------------------------------------------
    # Cross-document transaction collection (per run)
    # --------------------------------------------------
    all_normalized_transactions = []


    # --------------------------------------------------
    # Analyze action
    # --------------------------------------------------
    col1, col2 = st.columns([3, 1])

    with col1:
        analyze_clicked = render_analyze_button()

    with col2:
        clear_clicked = render_clear_history_button()

    # Handle clear history action
    if clear_clicked:
        clear_analysis_history()
        st.success("✓ Analysis history cleared")
        st.rerun()

    # Check if we should proceed with analysis (either button clicked or pending from tour rerun)
    should_analyze = analyze_clicked or st.session_state.get('pending_analysis', False)

    if should_analyze:
        if not documents:
            show_empty_warning()
            render_contextual_help('error')
            st.session_state.pending_analysis = False
            return
        if selected_provider == "heuristic":
            show_analysis_error("Local (Offline) analysis isn't wired yet. Use Smart/OpenAI for now.")
            render_contextual_help('error')
            st.session_state.pending_analysis = False
            return

        # If tour is active and on second_document_loaded step, advance tour and rerun to show message
        if (analyze_clicked and
                st.session_state.get('tour_active', False) and
                st.session_state.get('tutorial_step') == 'second_document_loaded'):
            st.session_state.pending_analysis = True
            st.session_state.analyzing = True
            advance_tour_step('analysis_running')
            st.rerun()

        # Clear pending flag and proceed with analysis
        st.session_state.pending_analysis = False
        st.session_state.analyzing = True

        # Wrap entire analysis in a spinner
        with st.spinner("Analyzing your documents..."):

            # Show analyzing context
            render_contextual_help('analyzing')

            # Aggregate savings across all documents for this run
            total_potential_savings = 0.0
            per_document_savings = {}

            install_billdozer_bridge()
            st.session_state.setdefault("show_billdozer_widget", True)

            # --------------------------------------------------
            # Billdozer widget messaging
            # --------------------------------------------------
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


            for idx, doc in enumerate(documents, 1):
                speaker = "billie" if idx % 2 == 1 else "billy"

                # Use index-based ID initially (will be replaced with friendly ID after facts extraction)
                initial_doc_id = f"Document {idx}"

                # Render document header first
                st.markdown(f"## 📄 {initial_doc_id}")

                # Create DAG container immediately (shows initial plan) if enabled
                dag_placeholder = None
                if is_dag_enabled():
                    dag_expander, dag_placeholder = create_pipeline_dag_container(document_id=str(idx))

                # Progress callback for real-time DAG updates
                def progress_callback(workflow_log, step_status):
                    if dag_placeholder and is_dag_enabled():
                        update_pipeline_dag(dag_placeholder, workflow_log, document_id=str(idx), step_status=step_status)

                # Run analysis with progress callback
                result = agent.run(doc["raw_text"], progress_callback=progress_callback)

                dispatch_widget_message(
                    speaker,
                    f"Finished analyzing {initial_doc_id}"
                )


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

            # Clear analyzing flag and set results for tour progression
            st.session_state.analyzing = False
            st.session_state.doc_results = True

            # Advance tour step to review_issues
            if (st.session_state.get('tour_active', False) and
                    st.session_state.get('tutorial_step') == 'analysis_running'):
                advance_tour_step('review_issues')
                # Set flag to trigger widget update after rendering completes
                st.session_state.tour_needs_refresh = True

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

            # Save analysis state for potential rerun
            st.session_state.last_documents = documents
            st.session_state.last_total_savings = total_potential_savings
            st.session_state.last_per_doc_savings = per_document_savings

    # Trigger rerun to update tour widget if needed (results will redisplay)
    if st.session_state.get('tour_needs_refresh', False):
        st.session_state.tour_needs_refresh = False
        st.rerun()

    # Display previously analyzed results if they exist (e.g., after tour rerun)
    elif st.session_state.get('last_documents') and st.session_state.get('doc_results', False):
        documents = st.session_state.last_documents
        total_potential_savings = st.session_state.get('last_total_savings', 0.0)
        per_document_savings = st.session_state.get('last_per_doc_savings', {})

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

