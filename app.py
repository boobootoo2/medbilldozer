# app.py

import streamlit as st
from _modules.privacy_ui import render_privacy_dialog

from _modules.llm_interface import ProviderRegistry
from _modules.ui import (
    setup_page,
    inject_css,
    render_header,
    render_demo_documents,
    render_input_area,
    render_provider_selector,
    render_analyze_button,
    render_results,
    render_footer,
    show_empty_warning,
    show_analysis_success,
    show_analysis_error,
)

try:
    from _modules.medgemma_hosted_provider import MedGemmaHostedProvider
except Exception:
    MedGemmaHostedProvider = None


# ==================================================
# Debug mode (URL-based)
# ==================================================
def debug_enabled() -> bool:
    return st.query_params.get("debug") == "1"


def render_debug_sidebar():
    with st.sidebar:
        st.markdown("## 🧪 Debug Mode")
        st.caption("Session-scoped server state")
        st.json(dict(st.session_state))


# ==================================================
# Bootstrap UI
# ==================================================
def bootstrap_ui():
    setup_page()
    inject_css()
    render_header()
    render_demo_documents()


# ==================================================
# Provider registration
# ==================================================
def register_providers():
    if MedGemmaHostedProvider is None:
        return
    try:
        provider = MedGemmaHostedProvider()
        if provider.health_check():
            ProviderRegistry.register("medgemma-hosted", provider)
    except Exception:
        pass


# ==================================================
# Main analysis flow
# ==================================================
def handle_analysis(bill_text: str, provider_key: str):
    if not bill_text.strip():
        show_empty_warning()
        return

    provider = ProviderRegistry.get(provider_key)
    if not provider:
        show_analysis_error("No analysis provider registered.")
        return

    with st.spinner("🚜 medBillDozer is analyzing your document…"):
        try:
            result = provider.analyze_document(bill_text)
        except Exception as e:
            show_analysis_error(f"Analysis failed: {e}")
            return

    show_analysis_success()
    render_results(result)


# ==================================================
# App entry
# ==================================================
def main():
    bootstrap_ui()
    register_providers()

    # 🔒 Session-scoped privacy dialog
    render_privacy_dialog()

    # 🧪 Debug sidebar (enabled via ?debug=1)
    if debug_enabled():
        render_debug_sidebar()

    bill_text = render_input_area()
    providers = ProviderRegistry.list()
    selected_provider = render_provider_selector(providers)

    analyze_clicked = render_analyze_button()

    if analyze_clicked:
        handle_analysis(bill_text, selected_provider)

    render_footer()


if __name__ == "__main__":
    main()
