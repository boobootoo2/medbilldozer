# _modules/ui.py

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import os
import html
import uuid
import re
from bs4 import BeautifulSoup


def toggle_expander_state(key: str):
    st.session_state[key] = not st.session_state.get(key, False)


# ==================================================
# Notifications
# ==================================================
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

    st.markdown(
        "Paste a bill, receipt, or claim history below. "
        "**Likely administrative and cost reconciliation issues** will be flagged."
    )


# ==================================================
# Utilities
# ==================================================
def _read_html(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def html_to_plain_text(html_doc: str) -> str:
    soup = BeautifulSoup(html_doc, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def copy_to_clipboard_button(label: str, text: str):
    button_id = f"copy_{uuid.uuid4().hex}"
    escaped = html.escape(text)

    components.html(
        f"""
        <button id="{button_id}"
            style="
                padding: 0.4rem 0.75rem;
                border-radius: 8px;
                border: none;
                background: #0A66C2;
                color: white;
                font-weight: 600;
                cursor: pointer;
            ">
            {label}
        </button>

        <script>
        const btn = document.getElementById("{button_id}");
        btn.addEventListener("click", async () => {{
            try {{
                await navigator.clipboard.writeText(`{escaped}`);
                btn.innerText = "✅ Copied";
                setTimeout(() => btn.innerText = "{label}", 1500);
            }} catch (e) {{
                btn.innerText = "❌ Failed";
            }}
        }});
        </script>
        """,
        height=45,
    )


# ==================================================
# Demo Documents (FULLY REFACTORED)
# ==================================================
def render_demo_documents():
    st.markdown("### Demo Documents")

    docs = [
        ("🏥 Hospital Bill – Colonoscopy", "static/sample_colonoscopy_bill.html"),
        ("💊 Pharmacy Receipt – FSA Scenario", "static/sample_pharmacy_receipt_fsa.html"),
        ("🦷 Dental Crown Bill", "static/sample_dental_crown_bill.html"),
        ("📊 FSA Claim History", "static/sample_fsa_claim_history.html"),
        ("🧾 Insurance Claim History – $0 Out-of-Pocket", "static/sample_insurance_claim_history_zero_oop.html"),
    ]

    html_docs = []
    text_docs = []

    for _, path in docs:
        html_doc = _read_html(path)
        html_docs.append(html_doc)
        text_docs.append(html_to_plain_text(html_doc))

    # ---------- Global controls ----------
    col1, col2 = st.columns(2)

    with col1:
        copy_to_clipboard_button(
            "📋 Copy ALL demo documents",
            "\n\n---\n\n".join(text_docs)
        )

    with col2:
        if st.button("⬇️ Paste ALL into analyzer"):
            st.session_state["text_area_1"] = "\n\n---\n\n".join(text_docs)

    st.divider()

    # ---------- Document rows ----------
    for i, ((title, _), html_doc, text_doc) in enumerate(zip(docs, html_docs, text_docs)):
        expander_key = f"demo_open_{i}"

        c1, c2, c3 = st.columns([6, 1.5, 1.5])

        with c1:
            label = f"▾ {title}" if st.session_state.get(expander_key) else f"▸ {title}"
            if st.button(label, key=f"toggle_{i}", use_container_width=True):
                toggle_expander_state(expander_key)

        with c2:
            copy_to_clipboard_button("📋 Copy", text_doc)

        with c3:
            if st.button("⬇️ Paste", key=f"paste_{i}"):
                st.session_state["text_area_1"] = text_doc

        if st.session_state.get(expander_key):
            components.html(html_doc, height=420, scrolling=True)
            st.markdown("---")

# ==================================================
# Inputs
# ==================================================
def render_input_area():
    st.markdown("### Analyze a Document")
    return st.text_area(
        "Paste bill, receipt, or claim history text",
        height=240,
        placeholder="Paste text here...",
        key="text_area_1",
    )


def render_provider_selector(providers: list[str]) -> str:
    display_map = {}
    labels = []

    for key in providers:
        if key == "local":
            label = "Local — Heuristics (offline, fast, safe)"
        elif key == "medgemma-hosted":
            label = f"Hosted MedGemma — {os.getenv('HF_MODEL_ID', 'google/medgemma-4b-it')}"
        else:
            label = key

        labels.append(label)
        display_map[label] = key

    selected = st.selectbox("Analysis provider", labels, index=0)
    return display_map[selected]


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
    else:
        st.info("No obvious issues detected. Manual review may still be helpful.")

    st.info(
        "Billing and claim errors are common and often resolved once identified. "
        "This tool helps patients know what to question before paying."
    )


# ==================================================
# Footer
# ==================================================
def render_footer():
    st.caption(
        "medBillDozer is a prototype for educational purposes only. "
        "It does not provide medical, legal, or financial advice."
    )
