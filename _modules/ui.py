# _modules/ui.py
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import os


def show_empty_warning():
    st.warning("Please paste a document to analyze.")

def show_analysis_success():
    st.success("Analysis complete")

def show_analysis_error(msg: str):
    st.error(msg)


# ==================================================
# Page config (MUST be first)
# ==================================================
def setup_page():
    st.set_page_config(
        page_title="medBillDozer",
        layout="centered"
    )


# ==================================================
# CSS (brand + layout)
# ==================================================
def inject_css():
    st.markdown("""
    <style>
    :root {
        --brand-blue: #0A66C2;
        --brand-green: #2DA44E;
        --brand-warning: #F59E0B;
        --text-secondary: #6B7280;
        --ui-border: #E5E7EB;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 900px;
    }

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
        .app-header {
            flex-direction: column;
            align-items: center;
            text-align: center;
        }
        .med-bill-dozer-logo {
            width: 120px;
            height: 70px;
        }
        .app-title { font-size: 1.6rem; }
    }

    .stTextArea textarea {
        border-radius: 10px;
        border: 1px solid var(--ui-border);
    }

    .stButton > button {
        background-color: var(--brand-blue);
        color: white;
        border-radius: 10px;
        font-weight: 600;
    }

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
# Header
# ==================================================
def render_header():
    logo_path = Path("images/medBillDozer-logo-transparent.png")

    if logo_path.exists():
        try:
            b64 = base64.b64encode(logo_path.read_bytes()).decode()
            st.markdown(
                f"""
                <style>
                .med-bill-dozer-logo {{
                    background-image: url("data:image/png;base64,{b64}");
                }}
                </style>
                <div class="app-header">
                  <div class="med-bill-dozer-logo"></div>
                  <div class="title-block">
                    <h1 class="app-title">
                        medBill<span class="dozer">Dozer</span>
                    </h1>
                    <div class="app-subtitle">
                        Detecting billing, pharmacy, dental, and insurance claim issues
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        except Exception:
            _fallback_title()
    else:
        _fallback_title()

    st.markdown(
        "Paste a bill, receipt, or claim history below. "
        "**Likely administrative and cost reconciliation issues** will be flagged."
    )


def _fallback_title():
    st.markdown('<h1 class="app-title">medBillDozer</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Detecting billing, pharmacy, dental, and insurance claim issues</div>',
        unsafe_allow_html=True
    )


# ==================================================
# Static viewers
# ==================================================
def _load_static_html(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def static_viewer(title: str, path: str, height: int = 520):
    with st.expander(title, expanded=False):
        components.html(
            _load_static_html(path),
            height=height,
            scrolling=True
        )


def render_demo_documents():
    st.markdown("### Demo Documents")

    static_viewer("🏥 Hospital Bill – Colonoscopy", "static/sample_colonoscopy_bill.html")
    static_viewer("💊 Pharmacy Receipt – FSA Scenario", "static/sample_pharmacy_receipt_fsa.html")
    static_viewer("🦷 Dental Crown Bill", "static/sample_dental_crown_bill.html")
    static_viewer("📊 FSA Claim History", "static/sample_fsa_claim_history.html")
    static_viewer(
        "🧾 Insurance Claim History – $0 Out-of-Pocket",
        "static/sample_insurance_claim_history_zero_oop.html"
    )


# ==================================================
# Inputs
# ==================================================
def render_input_area():
    st.markdown("### Analyze a Document")

    bill_text = st.text_area(
        "Paste bill, receipt, or claim history text",
        height=240,
        placeholder="Paste text here...",
        key="text_area_1",
    )

    return st.session_state.get("text_area_1", bill_text)


def render_provider_selector(providers: list[str]) -> str:
    display_map = {}
    labels = []

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

        labels.append(label)
        display_map[label] = key

    default_label = next(l for l in labels if "Local — Heuristics" in l)
    selected_label = st.selectbox("Analysis provider", labels, index=labels.index(default_label))

    return display_map[selected_label]


def render_analyze_button() -> bool:
    return st.button("Analyze with medBillDozer")


# ==================================================
# Results
# ==================================================
def render_results(result):
    if result and result.issues:
        st.markdown("### Flagged Issues")
        for issue in result.issues:
            st.markdown(
                f"""
                <div class="flag-warning">
                  <strong>{issue.summary}</strong><br/>
                  <em>Type:</em> {issue.type}<br/>
                  {issue.evidence or ""}
                </div>
                """,
                unsafe_allow_html=True
            )
    elif result:
        st.info("No obvious issues detected. Manual review may still be helpful.")

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
def render_footer():
    st.caption(
        "medBillDozer is a prototype for educational purposes only. "
        "It does not provide medical, legal, or financial advice."
    )
