"""Runtime flags and feature toggles.

Provides utility functions for checking runtime flags via query parameters.
"""
# _modules/runtime_flags.py
import streamlit as st


def debug_enabled() -> bool:
    """Check if debug mode is enabled via query parameter.

    Debug mode can be activated by adding ?debug=1 to the URL.

    Returns:
        bool: True if debug mode is enabled, False otherwise
    """
    return st.query_params.get("debug") == "1"

