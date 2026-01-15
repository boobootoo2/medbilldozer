import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import os
import html
import uuid
import re
from bs4 import BeautifulSoup

# ==================================================
# State helpers
# ==================================================
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
# Page config (MUST be first in app.py)
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

    .flag-warning {
        background-color: #FFFBEB;
        border-left: 6px solid var(--brand-warning);
        padding: 0.9rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }
    /* ===============================
    Analyze button (PRIMARY)
    =============================== */

    .st-key-analyze_button button[data-testid="stBaseButton-secondary"] {
        padding: 0.4rem 0.75rem !important;
        border-radius: 8px !important;
        border: none !important;
        background: #0A66C2 !important;
        color: white !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition:
            background-color 120ms ease,
            box-shadow 120ms ease,
            transform 80ms ease;
    }

    /* Hover */
    .st-key-analyze_button button[data-testid="stBaseButton-secondary"]:hover {
        background: #084f9e !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }

    /* Focus (keyboard) */
    .st-key-analyze_button button[data-testid="stBaseButton-secondary"]:focus-visible {
        outline: 2px solid #FFFFFF !important;
        outline-offset: -2px;
    }

    /* Active */
    .st-key-analyze_button button[data-testid="stBaseButton-secondary"]:active {
        transform: scale(0.97);
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
                background-size: contain;
                background-repeat: no-repeat;
                width: 140px;
                height: 88px;
            }}
            </style>
            <div style="display:flex;gap:18px;align-items:center;">
              <div class="med-bill-dozer-logo"></div>
              <div>
                <h1 style="margin:0;font-style:italic;">
                    medBill<span style="color:#2DA44E;">Dozer</span>
                </h1>
                <div style="color:#6B7280;">
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
        document.getElementById("{button_id}").onclick = async () => {{
            await navigator.clipboard.writeText(`{escaped}`);
        }};
        </script>
        """,
        height=45,
    )


# ==================================================
# Document Rows (SINGLE SOURCE OF TRUTH)
# ==================================================
def render_document_rows(docs, html_docs, text_docs):
    from streamlit_extras.stylable_container import stylable_container

    for i, ((title, _), html_doc, text_doc) in enumerate(
        zip(docs, html_docs, text_docs)
    ):
        expander_key = f"demo_open_{i}"
        is_open = st.session_state.get(expander_key, False)

        with stylable_container(
            key=f"doc_section_{i}",
            css_styles="""
                button[data-testid="stButton"] {
                    border-radius: 8px;
                    font-weight: 600;
                }
                [data-testid="stHorizontalBlock"] > div:nth-child(1) button {
                    background: transparent;
                    border: none;
                    text-align: left;
                }
                [data-testid="stHorizontalBlock"] > div:nth-child(1) button > div {
                    justify-content: flex-start;
                }
                [data-testid="stHorizontalBlock"] > div:nth-child(2) button,
                [data-testid="stHorizontalBlock"] > div:nth-child(3) button {
                    background: #F3F4F6;
                    border: 1px solid #E5E7EB;
                }
            """
        ):
            c1, c2, c3 = st.columns([6, 1.5, 1.5])

            with c1:
                label = f"▾ {title}" if is_open else f"▸ {title}"
                if st.button(label, key=f"toggle_{i}", use_container_width=True):
                    toggle_expander_state(expander_key)

            with c2:
                copy_to_clipboard_button("📋 Copy", text_doc)

            with c3:
                if st.button("⬇️ Paste", key=f"paste_{i}"):
                    st.session_state["text_area_1"] = text_doc

            if is_open:
                components.html(html_doc, height=420, scrolling=True)
                st.markdown("---")


# ==================================================
# Demo Documents (CLEAN + FINAL)
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

    combined_text = "\n\n---\n\n".join(text_docs)

    col1, col2 = st.columns(2)
    with col1:
        copy_to_clipboard_button("📋 Copy ALL demo documents", combined_text)
    with col2:
        if st.button("⬇️ Paste ALL into analyzer", key="paste_all_demo"):
            st.session_state["text_area_1"] = combined_text

    st.divider()

    render_document_rows(docs, html_docs, text_docs)


# ==================================================
# Inputs
# ==================================================
def render_input_area():
    return st.text_area(
        "Paste bill, receipt, or claim history text",
        height=240,
        key="text_area_1",
    )


def render_provider_selector(providers: list[str]) -> str:
    display_map = {}

    for provider in providers:
        if provider == "local":
            label = (
                "Local Analysis — Rules & Heuristics "
                "(offline, fastest, no AI model)"
            )
        elif provider == "medgemma-hosted":
            label = (
                "AI Medical Model — Google MedGemma 4B "
                "(google/medgemma-4b-it)"
            )
        else:
            label = provider  # fallback

        display_map[label] = provider

    selected_label = st.selectbox(
        "Analysis method",
        list(display_map.keys()),
        index=0,
    )

    return display_map[selected_label]



def render_analyze_button() -> bool:
    return st.button(
        "🚜 Analyze with medBillDozer",
        key="analyze_button",
        use_container_width=True,
    )


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
                  {issue.evidence or ""}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No obvious issues detected.")


# ==================================================
# Footer
# ==================================================
def render_footer():
    st.caption(
        "medBillDozer is a prototype for educational purposes only."
    )
