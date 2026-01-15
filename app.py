import os
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
)

try:
    from _modules.medgemma_hosted_provider import MedGemmaHostedProvider
except Exception:
    MedGemmaHostedProvider = None


# ==================================================
# UI bootstrap
# ==================================================
setup_page()
inject_css()
render_header()
render_demo_documents()


# ==================================================
# Provider registration
# ==================================================
try:
    if MedGemmaHostedProvider is not None:
        hosted = MedGemmaHostedProvider()
        if hosted.health_check():
            ProviderRegistry.register("medgemma-hosted", hosted)
except Exception:
    pass


# ==================================================
# Inputs
# ==================================================
bill_text = render_input_area()
providers = ProviderRegistry.list()
selected_provider = render_provider_selector(providers)
analyze = render_analyze_button()


# ==================================================
# Analysis
# ==================================================
if analyze:
    if not bill_text.strip():
        from _modules.ui import show_empty_warning
        show_empty_warning()
    else:
        from _modules.ui import show_analysis_success
        show_analysis_success()

        provider = ProviderRegistry.get(selected_provider)
        if not provider:
            st.error("No analysis provider registered.")
        else:
            try:
                result = provider.analyze_document(bill_text)
                render_results(result)
            except Exception as e:
                st.error(f"Analysis failed: {e}")


render_footer()
