import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import os
from _modules.llm_interface import ProviderRegistry
try:
    from _modules.medgemma_hosted_provider import MedGemmaHostedProvider
except Exception:
    MedGemmaHostedProvider = None

# ==================================================
# Page config (MUST be first)
# ==================================================
st.set_page_config(
    page_title="medBillDozer",
    layout="centered"
)

# ==================================================
# CSS (brand + layout)
# ==================================================
st.markdown("""
<style>
:root {
    --brand-blue: #0A66C2;
    --brand-green: #2DA44E;
    --brand-warning: #F59E0B;
    --text-secondary: #6B7280;
    --ui-border: #E5E7EB;
}

/* Container */
.block-container {
    padding-top: 2rem;
    max-width: 900px;
}

/* Header (logo left of title on wide screens, stacked on small screens) */
.app-header {
    display: flex;
    align-items: center;
    gap: 18px;
    margin-bottom: 12px;
}
.med-bill-dozer-logo {
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    width: 140px;
    height: 88px;
    min-width: 100px;
    flex: 0 0 auto;
}
.title-block { flex: 1 1 auto; }
.app-title {
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--brand-blue);
    margin: 0;
    font-style: italic;
}
.app-title .dozer { color: var(--brand-green); }
.app-subtitle {
    font-size: 1.02rem;
    color: var(--text-secondary);
    margin-top: 6px;
}

@media (max-width: 640px) {
    .app-header { flex-direction: column; align-items: center; text-align: center; }
    .med-bill-dozer-logo { margin-right: 0; width: 120px; height: 70px; }
    .app-title { font-size: 1.6rem; }
}

/* Inputs */
.stTextArea textarea {
    border-radius: 10px;
    border: 1px solid var(--ui-border);
}

/* Button */
.stButton > button {
    background-color: var(--brand-blue);
    color: white;
    border-radius: 10px;
    font-weight: 600;
}

/* Flag cards */
.flag-warning {
    background-color: #FFFBEB;
    border-left: 6px solid var(--brand-warning);
    padding: 0.9rem;
    border-radius: 8px;
    margin-bottom: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# Helpers
# ==================================================
def load_static_html(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

def show_static_viewer(title: str, path: str, height: int = 520):
    with st.expander(title, expanded=False):
        components.html(
            load_static_html(path),
            height=height,
            scrolling=True
        )




# ==================================================
# Header with left-aligned logo (uses medBillDozer-logo-transparent.png)
# ==================================================
logo_path = Path("images/medBillDozer-logo-transparent.png")
if logo_path.exists():
    try:
        b64 = base64.b64encode(logo_path.read_bytes()).decode()
        st.markdown(
            f"""
            <style>
            /* inline logo image (data URL) so Streamlit routing won't block tiny assets */
            .med-bill-dozer-logo {{ background-image: url("data:image/png;base64,{b64}"); }}
            </style>
            <div class="app-header">
              <div class="med-bill-dozer-logo" aria-hidden="true"></div>
              <div class="title-block">
                <div class="app-title"><h1>medBill<span class="dozer">Dozer</span></h1></div>
                <div class="app-subtitle">Detecting billing, pharmacy, dental, and insurance claim issues</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        # fallback to simple title if reading fails
        st.markdown('<div class="app-title">medBillDozer</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="app-subtitle">Detecting billing, pharmacy, dental, and insurance claim issues</div>',
            unsafe_allow_html=True,
        )
else:
    # image missing: fall back to plain title/subtitle
    st.markdown('<div class="app-title">medBillDozer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Detecting billing, pharmacy, dental, and insurance claim issues</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    "Paste a bill, receipt, or claim history below. "
    "medBillDozer flags **likely administrative and cost reconciliation issues**."
)

# ==================================================
# Demo static documents
# ==================================================
st.markdown("### Demo Documents")

show_static_viewer(
    "🏥 Hospital Bill – Colonoscopy",
    "static/sample_colonoscopy_bill.html"
)

show_static_viewer(
    "💊 Pharmacy Receipt – FSA Scenario",
    "static/sample_pharmacy_receipt_fsa.html"
)

show_static_viewer(
    "🦷 Dental Crown Bill",
    "static/sample_dental_crown_bill.html"
)

show_static_viewer(
    "📊 FSA Claim History",
    "static/sample_fsa_claim_history.html"
)

show_static_viewer(
    "🧾 Insurance Claim History – $0 Out-of-Pocket",
    "static/sample_insurance_claim_history_zero_oop.html"
)

# If hosted MedGemma provider is available and HF_API_TOKEN is set, register it so it appears in the provider list
try:
    if MedGemmaHostedProvider is not None:
        hosted = MedGemmaHostedProvider()
        if hosted.health_check():
            ProviderRegistry.register("medgemma-hosted", hosted)
except Exception:
    pass

# ==================================================
# Input
# ==================================================
st.markdown("### Analyze a Document")

bill_text = st.text_area(
    "Paste bill, receipt, or claim history text",
    height=240,
    placeholder="Paste text here...",
    key="text_area_1",
)

# expose a stable widget key so external integrations can reference it
bill_text = st.session_state.get("text_area_1", bill_text)

# Provider selector: show all registered providers (local and any medgemma variants)
providers = ProviderRegistry.list()

# Map internal provider keys to human-friendly labels shown in the UI.
# Keep a reverse map so we can look up the selected provider key.
display_map = {}
display_labels = []
for key in providers:
    if key == "local":
        label = "Local — Heuristics (offline, fast, safe)"
    elif key == "medgemma":
        label = "Local MedGemma (requires local model)"
    elif key == "medgemma-hosted":
        model_id = os.getenv("HF_MODEL_ID", "google/medgemma-4b-it")
        label = f"Hosted MedGemma — {model_id}"
    else:
        label = key
    display_labels.append(label)
    display_map[label] = key

# Choose a sensible default (local heuristics preferred)
default_label = next((lab for lab, k in display_map.items() if k == "local"), display_labels[0])
selected_label = st.selectbox("Analysis provider", display_labels, index=display_labels.index(default_label))
# Map back to the provider key the rest of the app expects
selected_provider = display_map[selected_label]

analyze = st.button("Analyze with medBillDozer")

# ==================================================
# Analysis logic (delegated to a model-agnostic provider)
# ==================================================

# ==================================================
# Results
# ==================================================
if analyze:
    if not bill_text.strip():
        st.warning("Please paste a document to analyze.")
    else:
        st.success("Analysis complete")

        provider = ProviderRegistry.get(selected_provider)
        if provider is None:
            st.error("No analysis provider registered (expected 'local').")
            result = None
        else:
            try:
                result = provider.analyze_document(bill_text)
            except Exception as e:
                # Surface friendly error messages to the user (do not crash the app)
                st.error(f"Analysis failed: {e}")
                result = None

            if result and result.issues:
                st.markdown("### Flagged Issues")
                for issue in result.issues:
                    # Render each issue using the same visual treatment as before
                    st.markdown(
                        f"""
                        <div class="flag-warning">
                          <strong>{issue.summary}</strong><br/>
                          <em>Type:</em> {issue.type} <br/>
                          {issue.evidence or ''}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            elif result:
                st.info("No obvious issues detected. Manual review may still be helpful.")

        # Helpful reminder for users after results
        st.info(
            "Billing and claim errors are common and often resolved once identified. "
            "This tool helps patients know what to question before paying."
        )

        

        st.markdown("### Suggested Next Steps")
        st.markdown(
            "1. Compare the bill against insurance claim history and EOBs.\n"
            "2. Ask providers whether preventive or bundled services were applied correctly.\n"
            "3. Submit missing FSA claims with receipts if applicable.\n"
            "4. Request corrected statements when insurance indicates no patient cost."
        )

        st.markdown("#### Sample outreach script")
        st.code(
            "Hello, I’m reviewing my recent statement and insurance claims. "
            "My insurer indicates no out-of-pocket cost, but this bill shows a balance. "
            "Could you please review and provide a corrected statement?"
        )

# ==================================================
# Footer
# ==================================================
st.caption(
    "medBillDozer is a prototype for educational purposes only. "
    "It does not provide medical, legal, or financial advice."
)
