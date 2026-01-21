import streamlit as st


def _init_privacy_state():
    st.session_state.setdefault("privacy_accepted", False)
    st.session_state.setdefault(
        "cookie_preferences",
        {
            "essential": True,
            "preferences": False,
            "analytics": False,
        },
    )


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

    col1, col2 = st.columns([1, 3])

    with col1:
        accept_privacy = st.checkbox(
            "I agree",
            value=st.session_state["privacy_accepted"],
        )

    with col2:
        with st.expander("View Privacy Policy"):
            st.markdown(
                """
                **Medical & Health Information Disclaimer**

                medBillDozer does not collect or retain PHI.
                Processing occurs only within the current session.

                This is a hackathon demo and not a HIPAA-covered service.
                """
            )

    st.divider()

    st.markdown("### Cookie Preferences")

    st.checkbox(
        "Essential cookies (required)",
        value=True,
        disabled=True,
    )

    preferences = st.checkbox(
        "Preference cookies",
        value=st.session_state["cookie_preferences"]["preferences"],
    )

    analytics = st.checkbox(
        "Analytics cookies",
        value=st.session_state["cookie_preferences"]["analytics"],
    )

    st.divider()

    if st.button(
        "Accept & Continue",
        type="primary",
        disabled=not accept_privacy,
    ):
        st.session_state.privacy_acknowledged = True
        st.rerun()



def render_privacy_dialog():
    if st.session_state.get("privacy_acknowledged"):
        return

    _privacy_dialog()

