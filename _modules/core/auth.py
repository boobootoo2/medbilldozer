"""Authentication and access control for the application."""

import os
import streamlit as st


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
