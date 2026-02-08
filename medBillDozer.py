"""MedBillDozer - Medical billing error detection application.

Main Streamlit application that orchestrates document analysis, provider registration,
and UI rendering for detecting billing, pharmacy, dental, and insurance claim issues.
"""
# app.py
import sys
from pathlib import Path

# Add src directory to Python path for package imports
src_path = Path(__file__).parent / "src"
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st

# Core modules
from medbilldozer.core.auth import check_access_password
from medbilldozer.core.orchestrator_agent import OrchestratorAgent
from medbilldozer.core.analysis_runner import (
    run_document_analysis,
    render_cached_results,
)

# UI modules
from medbilldozer.ui.bootstrap import (
    bootstrap_ui_minimal,
    bootstrap_home_page,
    should_enable_guided_tour,
)
from medbilldozer.ui.page_router import render_page_navigation, route_to_page
from medbilldozer.ui.privacy_ui import render_privacy_dialog
from medbilldozer.ui.ui_documents import render_document_inputs
from medbilldozer.ui.doc_assistant import render_doc_assistant, render_contextual_help
from medbilldozer.ui.guided_tour import (
    initialize_tour_state,
    maybe_launch_tour,
)
from medbilldozer.ui.health_profile import (
    render_profile_selector,
    render_profile_details,
    get_profile_context_for_analysis,
    render_receipt_uploader,
    get_uploaded_receipts_context,
)
from medbilldozer.ui.ui import (
    render_provider_selector,
    render_analyze_button,
    render_clear_history_button,
    clear_analysis_history,
    render_footer,
    show_analysis_error,
)
from medbilldozer.ui.audio_controls import initialize_audio_state
from medbilldozer.ui.splash_screen import (
    should_show_splash_screen,
    render_splash_screen,
)
from medbilldozer.core.coverage_matrix import build_coverage_matrix
from medbilldozer.ui.ui_coverage_matrix import render_coverage_matrix

# Provider modules
from medbilldozer.providers.provider_registry import (
    register_providers,
    ENGINE_OPTIONS,
)
from medbilldozer.providers.llm_interface import ProviderRegistry

# Utils
from medbilldozer.utils.runtime_flags import debug_enabled
from medbilldozer.utils.config import (
    is_assistant_enabled,
    is_debug_enabled,
    is_privacy_ui_enabled,
    is_coverage_matrix_enabled,
)


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
    # Splash Screen (before everything if tour enabled)
    # --------------------------------------------------
    if should_enable_guided_tour() and should_show_splash_screen():
        render_splash_screen()
        return  # Stop rendering until splash is dismissed

    # --------------------------------------------------
    # Minimal Bootstrap (for all pages)
    # --------------------------------------------------
    bootstrap_ui_minimal()
    
    # --------------------------------------------------
    # Audio Controls (initialize state)
    # --------------------------------------------------
    initialize_audio_state()

    # --------------------------------------------------
    # Page Navigation (sidebar - at top)
    # --------------------------------------------------
    current_page = render_page_navigation()

    # --------------------------------------------------
    # Route to other pages if selected
    # --------------------------------------------------
    if route_to_page(current_page):
        return  # Page was rendered, stop here

    # --------------------------------------------------
    # Register Providers (needed for both workflows)
    # --------------------------------------------------
    register_providers()

    # --------------------------------------------------
    # Guided Tour Initialization
    # --------------------------------------------------
    if should_enable_guided_tour():
        initialize_tour_state()
        maybe_launch_tour()

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

    # ==================================================
    # TAB NAVIGATION: POC vs Prod Workflow
    # ==================================================
    tab1, tab2 = st.tabs(["🧪 Demo POC", "🏭 Demo Prod Workflow"])
    
    # --------------------------------------------------
    # TAB 1: DEMO POC WORKFLOW (Original)
    # --------------------------------------------------
    with tab1:
        # Home Page Specific UI
        bootstrap_home_page()
        
        # --------------------------------------------------
        # Defaults (can be overridden in debug)
        # --------------------------------------------------
        extractor_override = None
        analyzer_override = None

        # --------------------------------------------------
        # Document input (UI ONCE)
        # --------------------------------------------------
        render_contextual_help('input')
        
        # Preserve documents during tour navigation to prevent clearing analysis state
        # This includes: completed analysis (doc_results), ongoing analysis (analyzing), 
        # and pending analysis (pending_analysis)
        if (st.session_state.get('tour_active', False) and 
            st.session_state.get('last_documents') and 
            (st.session_state.get('doc_results', False) or 
             st.session_state.get('analyzing', False) or 
             st.session_state.get('pending_analysis', False))):
            # During active tour with results/analysis, preserve the documents
            documents = st.session_state.last_documents
            # Still render the inputs for display, but don't use their output
            render_document_inputs()
        else:
            # Normal flow: get documents from input widgets
            documents = render_document_inputs()

        # Tour monitoring handled by Intro.js

        # --------------------------------------------------
        # Provider Overview (Engine + Health Profile)
        # --------------------------------------------------
        st.markdown("### 📊 Analysis Overview")
        
        # Use config debug setting OR legacy runtime flag
        debug_mode = is_debug_enabled() or debug_enabled()

        # Create columns for provider/engine and health profile
        col1, col2 = st.columns([1, 1])
        
        with col1:
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
        

        st.markdown("---")

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


        agent = OrchestratorAgent(
            extractor_override=extractor_override,
            analyzer_override=analyzer_override or selected_provider
        )


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

        # Check if we should proceed with analysis (either button clicked, pending, or interrupted)
        # If analyzing flag is still True, it means analysis was interrupted by a rerun (e.g., tour navigation)
        # and should be restarted
        should_analyze = (analyze_clicked or
                          st.session_state.get('pending_analysis', False) or
                          st.session_state.get('analyzing', False))

        if should_analyze:
            # Validate inputs
            if not documents:
                from medbilldozer.ui.ui import show_empty_warning
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
                # Save documents immediately so they persist during tour navigation
                st.session_state.last_documents = documents
                st.rerun()

            # Clear pending flag and proceed with analysis
            st.session_state.pending_analysis = False
            st.session_state.analyzing = True
            
            # Save documents at start of analysis so they persist during tour navigation
            st.session_state.last_documents = documents

            # Wrap entire analysis in a spinner
            with st.spinner("Analyzing your documents..."):
                # Show analyzing context
                render_contextual_help('analyzing')

                # Run document analysis
                analysis_result = run_document_analysis(documents, agent, analyze_clicked)

                if analysis_result:
                    total_potential_savings = analysis_result["total_savings"]
                    per_document_savings = analysis_result["per_document_savings"]
                    documents = analysis_result["documents"]

                    # Clear analyzing flag and set results for tour progression
                    st.session_state.analyzing = False
                    st.session_state.doc_results = True

                    # Advance tour step to review_issues
                    if (st.session_state.get('tour_active', False) and
                            st.session_state.get('tutorial_step') == 'analysis_running'):
                        st.session_state.tour_needs_refresh = True

                    # Save analysis state for potential rerun
                    st.session_state.last_documents = documents
                    st.session_state.last_total_savings = total_potential_savings
                    st.session_state.last_per_doc_savings = per_document_savings

        # Trigger rerun to update tour widget if needed (results will redisplay)
        if st.session_state.get('tour_needs_refresh', False):
            st.session_state.tour_needs_refresh = False
            st.rerun()

        # Display previously analyzed results if they exist (e.g., after tour rerun)
        # Only show cached results if we're NOT currently in an analysis run
        elif (st.session_state.get('last_documents') and 
              st.session_state.get('doc_results', False) and 
              not st.session_state.get('analyzing', False) and 
              not analyze_clicked):
            documents = st.session_state.last_documents
            total_potential_savings = st.session_state.get('last_total_savings', 0.0)
            per_document_savings = st.session_state.get('last_per_doc_savings', {})

            # Re-render cached results
            render_cached_results(documents, total_potential_savings, per_document_savings)

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
    
    # --------------------------------------------------
    # TAB 2: DEMO PROD WORKFLOW (Profile-based)
    # --------------------------------------------------
    with tab2:
        from medbilldozer.ui.prod_workflow import render_prod_workflow
        render_prod_workflow()


    # --------------------------------------------------
    # Footer (ONCE)
    # --------------------------------------------------
    render_footer()


if __name__ == "__main__":
    main()

