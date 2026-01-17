# _modules/privacy_ui.py

import streamlit as st


def _init_privacy_state():
    """Initialize session-scoped privacy state exactly once."""
    st.session_state.setdefault("privacy_accepted", False)
    st.session_state.setdefault(
        "cookie_preferences",
        {
            "essential": True,
            "preferences": False,
            "analytics": False,
        },
    )


def get_privacy_debug_state():
    """Return a snapshot of privacy-related session state (safe for debugging)."""
    return {
        "privacy_accepted": st.session_state.get("privacy_accepted"),
        "cookie_preferences": st.session_state.get("cookie_preferences"),
    }


@st.dialog("🔒 Privacy & Cookie Preferences")
def _privacy_dialog():
    _init_privacy_state()

    st.markdown(
        """
        **Welcome to medBillDozer**

        This is a demo application.  
        We do **not** collect, store, or transmit personal or medical data.
        """
    )

    # ==================================================
    # Privacy acceptance
    # ==================================================
    col1, col2 = st.columns([1, 3])

    with col1:
        accept_privacy = st.checkbox(
            "I agree",
            value=st.session_state["privacy_accepted"],
            key="privacy_accept_checkbox",
        )

    with col2:
        with st.expander("View Privacy Policy"):
            st.markdown(
                """
                ### Privacy Policy

                #### Medical & Health Information Disclaimer

                **medBillDozer does not collect, store, transmit, or retain PHI.**

                Any medical or insurance text is processed **only in the current session**.

                This is a **hackathon demo**, not a HIPAA-covered service and not
                intended for medical advice.
                """
            )

    st.divider()

    # ==================================================
    # Cookie preferences (session-scoped)
    # ==================================================
    st.markdown("### Cookie Preferences")

    st.checkbox(
        "Essential cookies (required)",
        value=True,
        disabled=True,
    )

    preference_cookies = st.checkbox(
        "Preference cookies",
        value=st.session_state["cookie_preferences"]["preferences"],
    )

    analytics_cookies = st.checkbox(
        "Analytics cookies",
        value=st.session_state["cookie_preferences"]["analytics"],
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
    """Open the privacy dialog once per session."""
    _init_privacy_state()

    if not st.session_state["privacy_accepted"]:
        _privacy_dialog()
