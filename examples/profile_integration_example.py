"""
Minimal integration example for Profile Editor in app.py

This file shows the minimal code needed to add Profile Editor to your existing Streamlit app.
Copy/adapt these snippets into your app.py file.
"""

import streamlit as st

# ==============================================================================
# STEP 1: Add imports at the top of app.py
# ==============================================================================

from _modules.ui.profile_editor import (
    render_profile_editor,
    is_profile_editor_enabled
)


# Placeholder functions for example purposes


def render_home_page():
    """Placeholder for your existing home page."""
    pass


def render_analysis_page():
    """Placeholder for your existing analysis page."""
    pass


# ==============================================================================
# STEP 2: Initialize session state (add to your existing initialization)
# ==============================================================================


def initialize_app_state():
    """Initialize application session state."""
    # Your existing state initialization...

    # Add profile navigation state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'


# ==============================================================================
# STEP 3: Add navigation option (sidebar approach)
# ==============================================================================


def render_sidebar_navigation():
    """Render sidebar navigation with profile option."""
    with st.sidebar:
        st.markdown("## 📱 Navigation")

        # Home button
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = 'home'
            st.rerun()

        # Analyze button
        if st.button("� Analyze", use_container_width=True):
            st.session_state.current_page = 'analyze'
            st.rerun()

        # Profile button (only if enabled)
        if is_profile_editor_enabled():
            if st.button("📋 Profile", use_container_width=True):
                st.session_state.current_page = 'profile'
                st.rerun()

        st.markdown("---")


# ==============================================================================
# STEP 4: Route to profile page in main()
# ==============================================================================


def main():
    """Main application entry point."""

    # Initialize
    initialize_app_state()

    # Render navigation
    render_sidebar_navigation()

    # Route to appropriate page
    current_page = st.session_state.get('current_page', 'home')

    if current_page == 'profile' and is_profile_editor_enabled():
        # Render profile editor
        render_profile_editor()

    elif current_page == 'analyze':
        # Your existing analysis page
        render_analysis_page()

    else:
        # Your existing home page
        render_home_page()


# ==============================================================================
# ALTERNATIVE: Tab-based navigation
# ==============================================================================


def main_with_tabs():
    """Alternative main function using tabs instead of sidebar."""

    # Build tab list
    tab_labels = ["🏠 Home", "� Analyze"]
    if is_profile_editor_enabled():
        tab_labels.append("📋 Profile")

    # Create tabs
    tabs = st.tabs(tab_labels)

    # Render each tab
    with tabs[0]:
        render_home_page()

    with tabs[1]:
        render_analysis_page()

    if is_profile_editor_enabled() and len(tabs) > 2:
        with tabs[2]:
            render_profile_editor()


# ==============================================================================
# USAGE EXAMPLE: Accessing profile data in your analysis
# ==============================================================================


def analyze_document_with_profile_context(document_text: str):
    """Example: Use profile data to enhance document analysis."""
    from _modules.ui.profile_editor import (
        load_profile,
        load_insurance_plans,
        load_providers
    )

    # Load user context
    profile = load_profile()
    plans = load_insurance_plans()
    providers = load_providers()

    # Build context string for analysis
    context_parts = []

    if profile:
        context_parts.append(f"Patient: {profile.get('full_name', 'Unknown')}")
        context_parts.append(f"DOB: {profile.get('date_of_birth', 'Unknown')}")

    if plans:
        primary_plan = plans[0]
        context_parts.append(f"Insurance: {primary_plan.get('carrier_name')} - {primary_plan.get('plan_name')}")
        context_parts.append(f"Member ID: {primary_plan.get('member_id')}")

        deductible = primary_plan.get('deductible', {}).get('individual', 0)
        oop_max = primary_plan.get('out_of_pocket_max', {}).get('individual', 0)
        context_parts.append(f"Deductible: ${deductible:,.2f}")
        context_parts.append(f"OOP Max: ${oop_max:,.2f}")

    if providers:
        in_network = [p for p in providers if p.get('in_network')]
        context_parts.append(f"In-Network Providers: {len(in_network)}")

    context = "\n".join(context_parts)

    # Pass to your analysis agent
    # result = your_orchestrator.analyze(document_text, user_context=context)

    return context


# ==============================================================================
# USAGE EXAMPLE: Check if user has completed profile setup
# ==============================================================================


def check_profile_completeness():
    """Check if user has completed their profile setup."""
    from _modules.ui.profile_editor import (
        load_profile,
        load_insurance_plans
    )

    profile = load_profile()
    plans = load_insurance_plans()

    is_complete = (
        profile is not None
        and profile.get('full_name')
        and profile.get('date_of_birth')
        and len(plans) > 0
    )

    return is_complete


def show_profile_completion_banner():
    """Show a banner encouraging users to complete their profile."""
    if not check_profile_completeness():
        st.info("""
        📋 **Complete your profile** for better analysis results!

        Add your insurance information and provider details to get more accurate billing error detection.
        """)

        if st.button("Complete Profile Now"):
            st.session_state.current_page = 'profile'
            st.rerun()


# ==============================================================================
# EXAMPLE: Full minimal integration into existing app.py
# ==============================================================================

"""
# In your existing app.py, add these sections:

# 1. Add import at top:
from _modules.ui.profile_editor import render_profile_editor, is_profile_editor_enabled

# 2. In your main() function, add navigation:


def main():
    # ... your existing setup code ...

    # Add sidebar navigation
    with st.sidebar:
        st.markdown("## Navigation")

        if st.button("🏠 Home"):
            st.session_state.page = 'home'
            st.rerun()

        if st.button("� Analyze"):
            st.session_state.page = 'analyze'
            st.rerun()

        if is_profile_editor_enabled():
            if st.button("📋 Profile"):
                st.session_state.page = 'profile'
                st.rerun()

    # 3. Add routing logic:

    page = st.session_state.get('page', 'home')

    if page == 'profile' and is_profile_editor_enabled():
        render_profile_editor()
    elif page == 'analyze':
        # Your existing analyze page
        pass
    else:
        # Your existing home page
        pass

# 4. Set environment variable before running:
# export PROFILE_EDITOR_ENABLED=true
# export IMPORTER_ENABLED=true
# streamlit run app.py
"""

