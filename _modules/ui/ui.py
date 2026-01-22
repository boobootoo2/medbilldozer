import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import os
import html
import uuid
import re
from bs4 import BeautifulSoup
from _modules.utils.runtime_flags import debug_enabled
from _modules.ui.ui_pipeline_dag import render_pipeline_dag, render_pipeline_comparison


# ==================================================
# Savings estimation helpers (UI-only)
# ==================================================
def calculate_max_savings(issues):
    """
    Calculate the maximum potential savings from a list of billing issues.
    
    Args:
        issues: List of Issue objects with optional max_savings attribute
    
    Returns:
        tuple: (total_max (float), breakdown (list of dicts))
            - total_max: Sum of all max_savings values
            - breakdown: List of dicts with summary and max_savings per issue
    """
    total = 0.0
    breakdown = []

    for issue in issues:
        max_savings = getattr(issue, "max_savings", None)

        if max_savings is None:
            continue

        total += max_savings
        breakdown.append({
            "summary": issue.summary,
            "max_savings": round(max_savings, 2),
        })

    return round(total, 2), breakdown


def render_savings_breakdown(title: str, total: float, breakdown: list[dict]):
    """Render a formatted savings breakdown UI component.
    
    Args:
        title: Section title for the savings display
        total: Total maximum potential savings amount
        breakdown: List of dicts with 'summary' and 'max_savings' keys
    """
    st.markdown(f"#### 💰 Max Potential Savings — {title}")

    if not breakdown:
        st.caption("No directly quantifiable savings identified.")
        return

    for item in breakdown:
        st.markdown(
            f"- **{item['summary']}**: up to **${item['max_savings']:,.2f}**"
        )

    st.markdown(
        f"""
        <div style="
            margin-top: 0.6rem;
            padding: 0.6rem 0.8rem;
            border: 1px solid var(--ui-border);
            border-radius: 8px;
            font-weight: 600;
        ">
            Max potential savings for this document:
            <span style="float:right;">
                ${total:,.2f}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==================================================
# State helpers
# ==================================================
def toggle_expander_state(key: str):
    """Toggle the boolean state of an expander in session state.
    
    Args:
        key: Session state key to toggle
    """
    st.session_state[key] = not st.session_state.get(key, False)


# ==================================================
# Notifications
# ==================================================
def show_empty_warning():
    """Display warning message when no document is provided."""
    st.warning("Please paste a document to analyze.")

def show_analysis_success():
    """Display success message after analysis completion."""
    st.success("Analysis complete")

def show_analysis_error(msg: str):
    """Display error message during analysis.
    
    Args:
        msg: Error message to display
    """
    st.error(msg)


# ==================================================
# Page config (MUST be first in app.py)
# ==================================================
def setup_page():
    """Configure Streamlit page settings. Must be called first in app.py.
    
    Sets page title and centered layout.
    """
    st.set_page_config(
        page_title="medBillDozer",
        layout="centered"
    )


# ==================================================
# CSS (brand + layout)
# ==================================================
def inject_css():
    """Inject custom CSS styles for branding and UI consistency.
    
    Includes styles for:
    - Brand colors and variables
    - Button styling (analyze button, copy buttons)
    - Checkbox focus states with dashed outlines
    - Accessibility improvements
    - Layout and spacing
    """
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
        background: #0A66C2;
        color: white;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition:
            background-color 120ms ease,
            box-shadow 120ms ease,
            transform 80ms ease;
    }

    /* Hover */
    .st-key-analyze_button button[data-testid="stBaseButton-secondary"]:hover {
            background: #E5E7EB;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
            color: rgb(49, 51, 63);
    }


    /* Active */
    .st-key-analyze_button button[data-testid="stBaseButton-secondary"]:active {
        transform: scale(0.97);
    }
    /* ===============================
    Override Streamlit error borders
    =============================== */

    /* Remove red borders */
    .st-dr,
    .st-dq,
    .st-dp {
        border-color: transparent !important;
    }
    
    /* Checkbox styling - default and focus states */
    .stCheckbox > [data-baseweb="checkbox"] > span {
        background-color: #000000 !important;
    }
    
    [type="checkbox"]:focus {
        outline-offset: 4px !important;
        outline: 3px dashed #000000 !important;
    }
    
    /* Override Streamlit's red checkbox focus styles */
    .st-g7 {
        background-color: #000000 !important;
    }
    .st-g6 {
        background-image: url(data:image/svg+xml,%0A%20%20%20%20%3Csvg%20width%3D%2217%22%20height%3D%2213%22%20viewBox%3D%220%200%2017%2013%22%20fill%3D%22none%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%0A%20%20%20%20%20%20%3Cpath%20d%3D%22M6.50002%2012.6L0.400024%206.60002L2.60002%204.40002L6.50002%208.40002L13.9%200.900024L16.1%203.10002L6.50002%2012.6Z%22%20fill%3D%22%23f0f2f6%22%2F%3E%0A%20%20%20%20%3C%2Fsvg%3E%0A%20%20) !important;
    }
    .st-g5,
    .st-g4,
    .st-g3,
    .st-g2 {
        border-color: transparent !important;
    }
    
    /* Apply dashed outline to checkbox wrapper on focus */
    .stCheckbox:focus-within > [data-baseweb="checkbox"] {
        outline: 3px dashed #000000 !important;
        outline-offset: 4px !important;
    }
    
    /* Apply unified dashed outline */
    .st-dr,
    .st-dq,
    .st-dp {
        outline-offset: 4px !important;
    }
    div[data-baseweb="select"] .st-dr,
    div[data-baseweb="select"] .st-dq,
    div[data-baseweb="select"] .st-dp {
        outline: transparent !important;
    }
    div[tabindex="0" ]:focus-visible .st-dr,
    div[tabindex="0" ]:focus-visible .st-dq,
    div[tabindex="0" ]:focus-visible .st-dp {
        outline: 3px dashed #000000 !important;
    }
    [class*="st-key-demo_toggle_"] button div {
        justify-content: flex-start;
    }
    [type="textarea"],
    [data-baseweb="select"] > div > div {
        background-color: rgba(0, 0, 0, 0) !important;
    }

    </style>
    """, unsafe_allow_html=True)


# ==================================================
# Header
# ==================================================
def render_header():
    """Render the application header with logo and tagline.
    
    Displays the medBillDozer logo and descriptive text about the application's purpose.
    """
    logo_path = Path("static/images/medBillDozer-logo-transparent.png")

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
    """Read HTML file contents from disk.
    
    Args:
        path: Path to HTML file
    
    Returns:
        str: HTML file contents
    """
    return Path(path).read_text(encoding="utf-8")


def html_to_plain_text(html_doc: str) -> str:
    """Convert HTML document to plain text.
    
    Removes script and style tags, extracts text content, and normalizes whitespace.
    
    Args:
        html_doc: HTML content as string
    
    Returns:
        str: Cleaned plain text content
    """
    soup = BeautifulSoup(html_doc, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def copy_to_clipboard_button(label: str, text: str):
    """Render a custom button that copies text to clipboard.
    
    Uses HTML/JavaScript component to enable clipboard functionality.
    
    Args:
        label: Button label text
        text: Text content to copy when clicked
    """
    button_id = f"copy_{uuid.uuid4().hex}"
    escaped = html.escape(text)

    components.html(
        f"""
        <style>
        button#{button_id} {{
            background: #0A66C2;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
            color: white;
        }}
        button#{button_id}:hover {{
            background: #E5E7EB;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
            color: rgb(49, 51, 63);
        }}
        button#{button_id}:focus-visible {{
            box-shadow: rgba(255, 75, 75, 0) 0px 0px 0px 0.2rem !important;
            outline: 3px dashed #000000 !important;
            outline-offset: 4px !important;
        }}
        button#{button_id}:active {{
            transform: scale(0.97);
        }}
        </style>
        <button id="{button_id}"
            style="
                padding: 0.4rem 0.75rem;
                border-radius: 8px;
                border: none;
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
def render_document_rows(docs, html_docs, text_docs, key_prefix=""):
    """Render expandable document rows with toggle and copy functionality.
    
    Args:
        docs: List of (title, path) tuples
        html_docs: List of HTML content strings
        text_docs: List of plain text content strings
        key_prefix: Prefix for Streamlit widget keys to avoid collisions
    """
    from streamlit_extras.stylable_container import stylable_container

    for i, ((title, _), html_doc, text_doc) in enumerate(
    zip(docs, html_docs, text_docs)
):
        expander_key = f"{key_prefix}demo_open_{i}"
        is_open = st.session_state.get(expander_key, False)

        with stylable_container(
            key=f"{key_prefix}doc_section_{i}",
            css_styles=""" ... """
        ):
            c1, c2 = st.columns([7, 2])

            with c1:
                label = f"▾ {title}" if is_open else f"▸ {title}"
                if st.button(label, key=f"{key_prefix}toggle_{i}", use_container_width=True):
                    toggle_expander_state(expander_key)

            with c2:
                copy_to_clipboard_button(
                    label="📋 Copy",
                    text=text_doc,
                )

            if is_open:
                components.html(
                    html_doc,
                    height=420,
                    scrolling=True,
                )
                st.markdown("---")



# ==================================================
# Demo Documents (CLEAN + FINAL)
# ==================================================
def render_demo_documents():
    """Render the demo documents section with sample medical bills.
    
    Displays 5 demo documents:
    - Hospital bill (colonoscopy)
    - Pharmacy receipt (FSA)
    - Dental crown bill
    - FSA claim history
    - Insurance claim history
    """
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

    st.divider()

    render_document_rows(docs, html_docs, text_docs, key_prefix="demo_")


# ==================================================
# Inputs
# ==================================================
def render_input_area():
    """Render the main text input area for document analysis.
    
    Returns:
        str: User input text from the text area
    """
    return st.text_area(
        "Paste bill, receipt, or claim history text",
        height=240,
        key="text_area_1",
    )


def render_provider_selector(providers: list[str]) -> str:
    """Render analysis provider selection dropdown.
    
    Maps provider IDs to user-friendly display names.
    
    Args:
        providers: List of available provider IDs
    
    Returns:
        str: Selected provider ID
    """
    display_map = {}

    for provider in providers:
        if provider == "local":
            label = "Local Analysis — Rules & Heuristics (offline)"
        elif provider == "medgemma-hosted":
            label = "AI Medical Model — Google MedGemma 4B"
        elif provider == "openai":
            label = "AI Analysis — OpenAI GPT-4o Mini"
        else:
            label = provider

        display_map[label] = provider

    selected_label = st.selectbox(
        "Analysis method",
        list(display_map.keys()),
        index=0,
        disabled=debug_enabled(),
    )

    return display_map[selected_label]


def render_analyze_button() -> bool:
    """Render the primary 'Analyze with medBillDozer' button.
    
    Returns:
        bool: True if button was clicked, False otherwise
    """
    return st.button(
        "🚜 Analyze with medBillDozer",
        key="analyze_button",
        use_container_width=True,
    )


# ==================================================
# Results
# ==================================================
def render_results(result):
    """Render analysis results including flagged issues and savings breakdown.
    
    Args:
        result: AnalysisResult object or dict containing issues and metadata
    """
    if not result:
        st.info("No analysis results available.")
        return

    if isinstance(result, dict):
        issues = result.get("issues", [])
        workflow_log = result.get("_workflow_log")
    else:
        issues = result.issues or []
        workflow_log = getattr(result, "_workflow_log", None)

    # ---------- Pipeline DAG Visualization ----------
    if workflow_log:
        render_pipeline_dag(workflow_log)
        st.divider()

    # ---------- Issues ----------
    if issues:
        st.markdown("### Flagged Issues")
        for issue in issues:
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

    # ---------- Savings ----------
    total_max, breakdown = calculate_max_savings(issues)

    st.divider()

    render_savings_breakdown(
        title="This Document",
        total=total_max,
        breakdown=breakdown,
    )

    st.caption(
        "“Max potential savings” represents the maximum amount that could be "
        "removed from patient responsibility if all identified issues were "
        "resolved favorably. Final amounts depend on insurer adjudication."
    )


# ==================================================
# Footer
# ==================================================
def render_footer():
    """Render application footer with disclaimer."""
    st.caption(
        "medBillDozer is a prototype for educational purposes only."
    )
