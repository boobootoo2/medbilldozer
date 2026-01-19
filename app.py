# app.py

from annotated_types import doc
import streamlit as st

from _modules.privacy_ui import render_privacy_dialog
from _modules.ui_documents import render_document_inputs
from _modules.document_identity import maybe_enhance_identity
from _modules.openai_langextractor import extract_facts_openai
from _modules.fact_normalizer import normalize_facts



from _modules.llm_interface import ProviderRegistry
from _modules.ui import (
    setup_page,
    inject_css,
    render_header,
    render_demo_documents,
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
# Main analysis flow (single document)
# ==================================================
def handle_analysis(bill_text: str, provider_key: str, document_id: str):
    if not bill_text.strip():
        return

    provider = ProviderRegistry.get(provider_key)
    if not provider:
        show_analysis_error("No analysis provider registered.")
        return

    with st.spinner(f"🚜 Analyzing document {document_id}…"):
        try:
            result = provider.analyze_document(bill_text)
        except Exception as e:
            show_analysis_error(f"Analysis failed: {e}")
            return

    st.markdown(f"## 📄 Document `{document_id}`")
    show_analysis_success()
    render_results(result)


# ==================================================
# App entry
# ==================================================
def main():
    bootstrap_ui()
    register_providers()

    # 🔒 Privacy dialog (session-scoped)
    render_privacy_dialog()

    # 📄 Multi-document input
    documents = render_document_inputs()

    providers = ProviderRegistry.list()
    selected_provider = render_provider_selector(providers)

    analyze_clicked = render_analyze_button()

    if analyze_clicked:
        if not documents:
            show_empty_warning()
        else:
            for doc in documents:
                
                if doc.get("facts") is None:
                    raw_facts = extract_facts_openai(doc["raw_text"])
                    doc["facts"] = normalize_facts(raw_facts)
                    
                st.session_state.setdefault("extracted_facts", {})
                st.session_state["extracted_facts"][doc["document_id"]] = doc["facts"]
                    
                handle_analysis(
                    bill_text=doc["raw_text"],
                    provider_key=selected_provider,
                    document_id=doc["document_id"],
                )
                maybe_enhance_identity(doc)


    # 🧪 Debug sidebar (URL-based)
    if debug_enabled():
        with st.sidebar:
            st.markdown("## 🧪 Debug Mode")

            st.markdown("### 📄 Documents")
            st.json(documents)

            st.markdown("### 🧠 Extracted Facts")
            st.json(st.session_state.get("extracted_facts", {}))

            st.markdown("### 🧾 Session State (raw)")
            st.json(dict(st.session_state))

    render_footer()


if __name__ == "__main__":
    main()