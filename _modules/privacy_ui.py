# _modules/privacy_ui.py

import streamlit as st

@st.dialog("🔒 Privacy & Cookie Preferences")
def _privacy_dialog():
    st.markdown(
        """
        **Welcome to medBillDozer**

        This is a demo application.  
        We do **not** collect, store, or transmit personal or medical data.
        """
    )

    # ==================================================
    # Privacy acceptance (checkbox + policy accordion)
    # ==================================================
    col1, col2 = st.columns([1, 3])

    with col1:
        accept_privacy = st.checkbox(
            "I agree",
            key="privacy_accept_checkbox",
        )

    with col2:
        with st.expander("View Privacy Policy"):
            st.markdown(
                """
                ### Privacy Policy

                - No personal or medical data is collected
                - No tracking or profiling
                - No third-party scripts
                - Cookies (if enabled) store preferences only

                This application is a hackathon demo and **not a medical device**.
                """
            )

    st.divider()

    # ==================================================
    # Cookie policy section (GDPR + CPRA compliant)
    # ==================================================
    st.markdown("### Cookie Preferences")

    st.checkbox(
        "Essential cookies (required)",
        value=True,
        disabled=True,
        help="Required for basic application functionality.",
    )

    preference_cookies = st.checkbox(
        "Preference cookies",
        help="Remember UI choices such as ignored issues.",
    )

    analytics_cookies = st.checkbox(
        "Analytics cookies",
        help="Allow anonymous usage analytics to improve the app.",
    )

    with st.expander("About Cookies"):
        st.markdown(
            """
            **Cookie Categories Explained**

            - **Essential**: Required for core functionality (always enabled)
            - **Preferences**: Store user-selected settings
            - **Analytics**: Anonymous usage data only (opt-in)

            We do **not** sell or share data, in compliance with
            GDPR and California CPRA/CCPA.
            """
        )

    st.divider()

    # ==================================================
    # Accept & continue
    # ==================================================
    if st.button(
        "Accept & Continue",
        type="primary",
        disabled=not accept_privacy,
    ):
        # For now, store only in session (cookies come next)
        st.session_state["privacy_accepted"] = True
        st.session_state["cookie_preferences"] = {
            "essential": True,
            "preferences": preference_cookies,
            "analytics": analytics_cookies,
        }
        st.rerun()


def render_privacy_dialog():
    """
    Open the privacy dialog once per session.
    """
    if not st.session_state.get("privacy_accepted"):
        _privacy_dialog()
