import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

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
  max-width: 760px;
}

/* Header */
.app-title {
  font-size: 2.3rem;
  font-weight: 700;
  color: var(--brand-blue);
  text-align: center;
}
.app-subtitle {
  font-size: 1.05rem;
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
  text-align: center;
}

/* Logo */
.logo-viewport {
  width: 100%;
  height: 104px;
  overflow: hidden;
}
.logo-transform {
  transform: translate(0%, -33%);
}
.logo-viewport .logo-transform svg {
  width: 95%;
  display: block;
  margin: 0 auto;
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
# Logo (optional)
# ==================================================
try:
    svg_logo = load_static_html("medBillDozer-logo.svg")
    st.markdown(
        f"""
        <div class="logo-viewport">
          <div class="logo-transform">
            {svg_logo}
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
except Exception:
    pass

# ==================================================
# Header
# ==================================================
st.markdown('<div class="app-title">medBillDozer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Detecting medical billing, pharmacy, dental, and FSA errors</div>',
    unsafe_allow_html=True
)

st.markdown(
    "Paste a bill, receipt, or claim history below. "
    "medBillDozer flags **likely administrative errors** and suggests next steps."
)

# ==================================================
# Demo static documents
# ==================================================
st.markdown("### Demo Documents")

show_static_viewer(
    "🏥 Example Hospital Bill – Colonoscopy",
    "static/sample_colonoscopy_bill.html"
)

show_static_viewer(
    "💊 Example Pharmacy Receipt – FSA Scenario",
    "static/sample_pharmacy_receipt_fsa.html"
)

show_static_viewer(
    "🦷 Example Dental Crown Bill",
    "static/sample_dental_crown_bill.html"
)

show_static_viewer(
    "📊 Example FSA Claim History",
    "static/sample_fsa_claim_history.html"
)

# ==================================================
# Input
# ==================================================
st.markdown("### Analyze a Document")

bill_text = st.text_area(
    "Paste bill, receipt, or claim history text",
    height=240,
    placeholder="Paste text here..."
)

analyze = st.button("Analyze with medBillDozer")

# ==================================================
# Analysis logic (demo-grade heuristics)
# ==================================================
def analyze_text(text: str):
    flags = []

    # Duplicate procedure
    if text.lower().count("45378") > 1 or text.lower().count("d2740") > 1:
        flags.append(("Possible duplicate procedure", "Same procedure code appears more than once."))

    # Lab fee bundling
    if "lab fee" in text.lower() and "crown" in text.lower():
        flags.append(("Potential unbundled lab fee", "Lab fees are often included in crown allowances."))

    # Preventive coverage mismatch
    if "screening" in text.lower() and "not covered" in text.lower():
        flags.append(("Coverage mismatch", "Preventive services may be covered at 100%."))

    # FSA eligibility mix
    if "vitamin" in text.lower() and "fsa" in text.lower():
        flags.append(("Mixed FSA eligibility", "Receipt includes both eligible and non-eligible items."))

    # Missing FSA claim
    if "polyethylene glycol" in text.lower() and "claim history" in text.lower():
        flags.append(("Missing FSA claim", "An FSA-eligible item does not appear in claim history."))

    return flags

# ==================================================
# Results
# ==================================================
if analyze:
    if not bill_text.strip():
        st.warning("Please paste a document to analyze.")
    else:
        st.success("Analysis complete")

        flags = analyze_text(bill_text)

        if flags:
            st.markdown("### Flagged Issues")
            for title, reason in flags:
                st.markdown(
                    f"""
                    <div class="flag-warning">
                      <strong>{title}</strong><br/>
                      {reason}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No obvious issues detected. Manual review may still be helpful.")

        st.markdown("### Suggested Next Steps")
        st.markdown(
            "1. Request an itemized statement or explanation of benefits.\n"
            "2. Ask whether duplicate or bundled services were applied correctly.\n"
            "3. Confirm preventive or frequency-based coverage rules.\n"
            "4. Submit missing FSA claims with supporting receipts."
        )

        st.markdown("#### Sample outreach script")
        st.code(
            "Hello, I’m reviewing my recent statement and noticed a few items that may "
            "have been billed incorrectly or not processed. Could you please review "
            "these charges and provide clarification?"
        )

# ==================================================
# Footer
# ==================================================
st.caption(
    "medBillDozer is a prototype for educational purposes only. "
    "It does not provide medical, legal, or financial advice."
)
