import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import html
import uuid
import re
from bs4 import BeautifulSoup
from _modules.utils.runtime_flags import debug_enabled
from _modules.ui.ui_pipeline_dag import render_pipeline_dag
from _modules.utils.image_paths import get_image_url


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
    Opens sidebar by default if guided tour is active.
    """
    # Check if tour is active to open sidebar by default
    initial_sidebar_state = "auto"
    if hasattr(st, 'session_state') and st.session_state.get('tour_active', False):
        initial_sidebar_state = "expanded"

    st.set_page_config(
        page_title="medBillDozer",
        layout="centered",
        initial_sidebar_state=initial_sidebar_state
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

    #billdozer-sticky {
        position: sticky;
        top: 70px;
        z-index: 100;
    }

    .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 900px;
    }

    /* Give input fields breathing room */
    .stTextArea textarea, .stTextInput input {
        max-width: 100%;
    }

    .flag-warning {
        background-color: #FFFBEB;
        border-left: 6px solid var(--brand-warning);
        padding: 0.9rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        color: #1F2937;
    }

    /* Dark mode override for flag-warning */
    @media (prefers-color-scheme: dark) {
        .flag-warning {
            background-color: #422006;
            border-left: 6px solid #F59E0B;
            color: #FEF3C7;
        }
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


   /* ===============================
   Checkbox – SAFE styling
   =============================== */

/* Let BaseWeb render the checkbox normally */
.stCheckbox [data-baseweb="checkbox"] > div {
    background: transparent !important;
    border-color: #374151 !important;
}

/* Checked state */
.stCheckbox input:checked + div {
    border-color: #0A66C2 !important;
}

/* Focus ring (accessible, visible) */
.stCheckbox:focus-within {
    outline: 3px dashed #000000;
    outline-offset: 4px;
    border-radius: 6px;
}

/* Remove Streamlit red error glow */
.stCheckbox [data-baseweb="checkbox"] div[aria-invalid="true"] {
    box-shadow: none !important;
    border-color: #374151 !important;
}

/* Hover affordance */
.stCheckbox:hover [data-baseweb="checkbox"] > div {
    border-color: #0A66C2;
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
    /* Target the expand button by its data-testid */
    button[data-testid="stExpandSidebarButton"]::after {
        content: " Menu"; /* The text you want to display */
        font-size: 14px;
        margin-left: 5px;
        color: rgba(49, 51, 63, 0.6); /* Matches default Streamlit icon color */
    }

    /* Ensure the button is wide enough to show the label */
    button[data-testid="stExpandSidebarButton"] {
        width: auto !important;
        padding-right: 10px !important;
    }
    div[data-testid="stSidebarCollapseButton"] button {
    position: relative;
    }

    div[data-testid="stSidebarCollapseButton"] button::after {
    content: "Close menu";
    margin-left: 8px;
    font-size: 12px;
    color: rgba(49, 51, 63, 0.7);
    white-space: nowrap;
    }

    /* Prevent hidden sidebar elements from receiving focus */
    section[data-testid="stSidebar"][aria-expanded="false"] * {
        visibility: hidden !important;
    }

    section[data-testid="stSidebar"][aria-expanded="false"] {
        visibility: visible !important;
    }

    /* Remove from tab order when collapsed */
    section[data-testid="stSidebar"][aria-expanded="false"] button,
    section[data-testid="stSidebar"][aria-expanded="false"] input,
    section[data-testid="stSidebar"][aria-expanded="false"] select,
    section[data-testid="stSidebar"][aria-expanded="false"] textarea,
    section[data-testid="stSidebar"][aria-expanded="false"] a {
        pointer-events: none !important;
        tabindex: -1 !important;
    }

    /* Make widget containers responsive to sidebar */
    div[data-key="billdozer_widget"],
    div[data-key="guided_tour_widget"] {
        transition: margin-left 0.3s ease;
    }

    @media (max-width: 768px) {
        #med-bill-dozer {
            font-size: 2rem;
        }
    }

    /* Streamlit adds data-testid and data-key attributes */
    /* Widget container injected by Streamlit - full width responsive */
    div.st-key-billdozer_widget {
        position: fixed;
        top: 60px;
        left: 0;
        right: 0;
        z-index: 100;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 0 1rem;
        background-color: white;
    }

    /* OUR wrapper — the anchor, centered child */
    .billdozer-wrapper {
        position: relative;
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        overflow: hidden;
        width: 320px;
    }

    /* Dismiss button */
    .billdozer-dismiss {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        border: none;
        background: rgba(0,0,0,0.55);
        color: white;
        font-size: 14px;
        cursor: pointer;
        z-index: 10;
    }

    .billdozer-dismiss:hover {
        background: rgba(0,0,0,0.75);
    }
       /* ===============================
        Copy button focus – theme aware
        =============================== */

        button:focus-visible {
            outline-style: dashed;
            outline-width: 3px;
            outline-offset: 4px;
        }
        /* Light theme */

        @media (prefers-color-scheme: light) {
            button:focus-visible {
                outline-color: #000000;
            }
        }
        /* Dark theme */

        @media (prefers-color-scheme: dark) {
            button:focus-visible {
                outline-color: #F9FAFB;
                /* near-white, not pure */
            }
        }
        /* ===============================
        Header anchor icon visibility
        =============================== */

        /* Base (light theme default) */
        [data-testid="stHeaderActionElements"] a {
            color: #374151; /* slate-700 */
        }

        /* Dark theme override */
        @media (prefers-color-scheme: dark) {
            [data-testid="stHeaderActionElements"] a {
                color: #F9FAFB; /* near-white */
            }
        }

        /* Hover affordance */
        [data-testid="stHeaderActionElements"] a:hover {
            opacity: 0.85;
        }

        /* Keyboard focus (accessible) */
        [data-testid="stHeaderActionElements"] a:focus-visible {
            outline: 3px dashed currentColor;
            outline-offset: 4px;
            border-radius: 6px;
        }
        .st-key-guided_tour_widget {
            position: fixed;
            z-index: 1000;
            bottom: 20px;
        }
        .demo-highlight {
            /* Light theme: dark shadow for contrast against light backgrounds */
            box-shadow: 0 0 0 3px rgba(255, 193, 7, 0.6),
                        0 0 20px 8px rgba(255, 193, 7, 0.4) !important;
            transition: box-shadow 0.3s ease-in-out !important;
            border-radius: 4px !important;
            position: relative !important;
            z-index: 1000 !important;
        }
        /* Textarea highlight: solid outline that survives overflow clipping */
        textarea.demo-highlight {
        outline: 4px solid rgba(255, 193, 7, 0.95) !important;
        outline-offset: 4px !important;

        /* Optional: add an inner ring (not clipped, because it's inset) */
        box-shadow: inset 0 0 0 2px rgba(255, 193, 7, 0.55) !important;

        border-radius: 6px !important;
        }

        /* Dark mode tweak (optional) */
        @media (prefers-color-scheme: dark) {
        textarea.demo-highlight {
            outline: 4px solid rgba(255, 215, 64, 0.95) !important;
            box-shadow: inset 0 0 0 2px rgba(255, 215, 64, 0.6) !important;
        }
        }

        /* Streamlit theme attribute (covers explicit dark theme) */
        [data-theme="dark"] textarea.demo-highlight {
        outline: 4px solid rgba(255, 215, 64, 0.95) !important;
        box-shadow: inset 0 0 0 2px rgba(255, 215, 64, 0.6) !important;
        }


    """, unsafe_allow_html=True)


# ==================================================
# Header
# ==================================================


def render_header():
    """Render the application header with logo and tagline.

    Displays the medBillDozer logo and descriptive text about the application's purpose.
    """
    logo_path = Path("static/images/medBillDozer-logo-transparent.png")

    # Get logo URL (local file or CDN)
    logo_url = None
    if logo_path.exists():
        # Try to use base64 encoding for local files
        try:
            b64 = base64.b64encode(logo_path.read_bytes()).decode()
            logo_url = f"data:image/png;base64,{b64}"
        except Exception:
            # Fallback to URL-based approach
            logo_url = get_image_url("images/medBillDozer-logo-transparent.png")
    else:
        # Use CDN for production
        logo_url = get_image_url("images/medBillDozer-logo-transparent.png")

    if logo_url:
        st.markdown(
            f"""
            <style>
            .med-bill-dozer-logo {{
                background-image: url("{logo_url}");
                background-size: contain;
                background-repeat: no-repeat;
                width: 140px;
                height: 88px;
            }}
            </style>
            <div style="display:flex;gap:18px;align-items:center;">
              <img src="https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static/images/avatars/transparent/billy__eyes_open__billdozer_up.png" alt="Billy character with eyes open looking up" style="
            height: 87px;
            width: auto;" /> 
              <div>
                <h1 style="margin:0;font-style:italic;">
                    medBill<span style="color:#2DA44E;">Dozer</span>
                </h1>
                <div style="opacity:0.7;">
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
    Shows a brief success message after copying.

    Args:
        label: Button label text
        text: Text content to copy when clicked
    """
    button_id = f"copy_{uuid.uuid4().hex}"
    message_id = f"msg_{uuid.uuid4().hex}"
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
        .copy-message {{
            display: inline-block;
            margin-left: 10px;
            padding: 0.3rem 0.6rem;
            background: #10B981;
            color: white;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 500;
            opacity: 0;
            transition: opacity 0.3s ease-in-out;
        }}
        .copy-message.show {{
            opacity: 1;
        }}
        </style>
        <div style="display: flex; align-items: center;">
            <button id="{button_id}"
                aria-label="{label} - Copy to clipboard"
                style="
                    padding: 0.4rem 0.75rem;
                    border-radius: 8px;
                    border: none;
                    font-weight: 600;
                    cursor: pointer;
                ">
                {label}
            </button>
            <span id="{message_id}" class="copy-message" role="status" aria-live="polite">✓ Copied!</span>
        </div>

        <script>
        document.getElementById("{button_id}").onclick = async () => {{
            await navigator.clipboard.writeText(`{escaped}`);

            // Show success message
            const message = document.getElementById("{message_id}");
            message.classList.add('show');

            // Hide message after 2 seconds
            setTimeout(() => {{
                message.classList.remove('show');
            }}, 2000);
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
                    st.rerun()

            with c2:
                copy_to_clipboard_button(
                    label="Copy",
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
        "Analyze with medBillDozer",
        key="analyze_button",
        use_container_width=True,
    )


def render_clear_history_button() -> bool:
    """Render a button to clear analysis history.

    Returns:
        bool: True if button was clicked, False otherwise
    """
    return st.button(
        "🗑️ Clear Analysis History",
        key="clear_history_button",
        use_container_width=True,
        type="secondary",
    )


def clear_analysis_history():
    """Clear all analysis-related data from session state.

    Removes:
    - Analysis results and workflow logs
    - Extracted facts and normalized transactions
    - Aggregate metrics and savings data
    - Billdozer widget state
    """
    keys_to_clear = [
        "workflow_logs",
        "extracted_facts",
        "normalized_transactions",
        "transaction_provenance",
        "aggregate_metrics",
        "billdozer_analysis_started",
        "billdozer_widget_initialized",
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


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

