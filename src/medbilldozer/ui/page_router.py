"""Page navigation and routing for the application."""

import streamlit as st
from medbilldozer.ui.profile_editor import render_profile_editor, is_profile_editor_enabled
from medbilldozer.ui.api_docs_page import render_api_docs_page
from medbilldozer.ui.audio_controls import render_mute_button
from medbilldozer.ui.guided_tour import run_guided_tour_runtime
from medbilldozer.ui.bootstrap import should_enable_guided_tour
from medbilldozer.ui.analytics import track_page_view


def render_page_navigation():
    """Render page navigation controls in the sidebar.

    Shows navigation buttons for Home, Profile (if enabled), and API pages.
    Also renders audio controls and guided tour if enabled.

    Returns:
        str: Current page name ('home', 'profile', or 'api')
    """
    # Initialize page navigation state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'

    with st.sidebar:
        # Audio mute button at very top
        render_mute_button()

        # Guided Tour at top of sidebar
        if should_enable_guided_tour():
            run_guided_tour_runtime()

        st.markdown("## 📱 Navigation")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🏠 Home", use_container_width=True, type="primary" if st.session_state.current_page == 'home' else "secondary"):
                st.session_state.current_page = 'home'
                track_page_view('/streamlit/home', 'Home')
                st.rerun()

        with col2:
            if is_profile_editor_enabled():
                if st.button("📋 Profile", use_container_width=True, type="primary" if st.session_state.current_page == 'profile' else "secondary"):
                    st.session_state.current_page = 'profile'
                    track_page_view('/streamlit/profile', 'Profile')
                    st.rerun()

        with col3:
            if st.button("🔌 API", use_container_width=True, type="primary" if st.session_state.current_page == 'api' else "secondary"):
                st.session_state.current_page = 'api'
                track_page_view('/streamlit/api', 'API')
                st.rerun()

        st.markdown("---")

    return st.session_state.current_page


def route_to_page(page: str) -> bool:
    """Route to the specified page and render its content.

    Args:
        page: Page name ('home', 'profile', or 'api')

    Returns:
        bool: True if page was rendered (app should stop), False if should continue to home page
    """
    if page == 'profile' and is_profile_editor_enabled():
        render_profile_editor()
        return True

    if page == 'api':
        render_api_docs_page()
        return True

    # Home page - continue with main app flow
    return False
