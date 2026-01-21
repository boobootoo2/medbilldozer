"""Privacy dialog and cookie preferences UI.

Provides privacy acknowledgment dialog with cookie preference management.
"""
import streamlit as st


def _init_privacy_state():
    """Initialize privacy and cookie preference state in session.
    
    Sets default values for privacy acceptance and cookie preferences.
    """
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
    """Display privacy policy and cookie preferences dialog.
    
    Shows HIPAA disclaimer, privacy policy, and cookie preference toggles.
    """
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
    
    with st.expander("ℹ️ What are cookies and what do they do?"):
        st.markdown(
            """
            **Cookie Types & Purposes**
            
            **Essential Cookies** (Required)  
            - Enable core functionality like session management
            - Remember your privacy preferences during your visit
            - Required for the application to work properly
            - Cannot be disabled
            
            **Preference Cookies** (Optional)  
            - Remember your UI preferences (theme, language, layout)
            - Save your analysis method selection
            - Store document viewing preferences
            - Make your experience more personalized
            
            **Analytics Cookies** (Optional)  
            - Help us understand how the app is used
            - Identify which features are most helpful
            - Improve performance and user experience
            - All data is anonymized and aggregated
            
            **What You're Agreeing To:**
            - Essential cookies are automatically enabled
            - Optional cookies are only set if you enable them
            - You can change preferences at any time
            - No personal or medical data is ever stored in cookies
            - All processing happens locally in your browser session
            """
        )

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
    """Render privacy dialog if not already acknowledged.
    
    Shows the privacy dialog on first visit. Subsequent visits skip the dialog
    based on session state.
    """
    if st.session_state.get("privacy_acknowledged"):
        return

    _privacy_dialog()

