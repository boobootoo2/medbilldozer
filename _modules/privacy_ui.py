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

                #### Medical & Health Information Disclaimer

                **medBillDozer does not collect, store, transmit, or retain any
                personal health information (PHI).**

                Any medical or insurance text entered into the application is
                processed **only within the current user session** and is not
                saved, logged, or shared with third parties.

                medBillDozer is a **hackathon demonstration project** and is
                **not a covered entity or business associate under HIPAA**, and
                it is **not intended for clinical decision-making or medical advice**.

                #### General Privacy Practices

                - No analytics, tracking pixels, or third-party scripts  
                - No user accounts or identity tracking  
                - Cookies (if enabled) are used only for local preferences  
                """
            )

    st.divider()

    # ==================================================
    # Cookie policy section
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
