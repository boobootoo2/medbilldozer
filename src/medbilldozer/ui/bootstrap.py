"""UI bootstrap and initialization functions."""

import os
import streamlit as st
from medbilldozer.ui.ui import setup_page, inject_css, render_header, render_demo_documents
from medbilldozer.ui.doc_assistant import render_contextual_help
from medbilldozer.utils.config import is_guided_tour_enabled
from medbilldozer.ui.analytics import initialize_ga4_for_streamlit


def should_enable_guided_tour() -> bool:
    """Check if guided tour should be enabled based on environment variable.

    Returns:
        bool: True if tour should be enabled
    """
    # Check environment variable first (overrides config)
    env_tour = os.environ.get('GUIDED_TOUR', '').upper()
    if env_tour in ('TRUE', '1', 'YES', 'ON'):
        return True
    elif env_tour in ('FALSE', '0', 'NO', 'OFF'):
        return False

    # Fall back to config file setting
    return is_guided_tour_enabled()


def bootstrap_ui_minimal():
    """Initialize minimal UI components for all pages.

    Sets up page configuration, CSS styles, header, and analytics.
    Should be called on all pages (home and profile).
    """
    setup_page()
    inject_css()
    render_header()

    # Initialize Google Analytics 4 (privacy-focused)
    initialize_ga4_for_streamlit()


def bootstrap_home_page():
    """Initialize home page specific UI components.

    Renders demo documents and contextual help for POC workflow.
    Should only be called on the home page.
    """
    # Skip demo help message when guided tour is active
    if not should_enable_guided_tour():
        render_contextual_help('demo')

    render_demo_documents()

    # Tour handled by Intro.js runtime
