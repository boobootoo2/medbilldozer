import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import base64
import os
import json
import urllib.request
import ssl
try:
    import certifi
    _CA_BUNDLE = certifi.where()
except Exception:
    _CA_BUNDLE = None
from typing import List, Dict, Any

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


def call_openai_chat(api_key: str, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
    """Call the OpenAI Chat Completions API using the standard REST endpoint.
    Uses urllib to avoid extra dependencies. Returns parsed JSON response.
    """
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 800,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    # Build an SSL context that uses certifi's CA bundle when available. This avoids
    # macOS Python SSL verification issues where the system cert store isn't configured.
    ctx = None
    if _CA_BUNDLE:
        ctx = ssl.create_default_context(cafile=_CA_BUNDLE)
    else:
        ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            resp_bytes = resp.read()
            return json.loads(resp_bytes.decode("utf-8"))
    except ssl.SSLCertVerificationError as e:
        # Provide a clear actionable error for macOS users.
        raise RuntimeError(
            "SSL certificate verification failed when contacting OpenAI. "
            "On macOS, run the 'Install Certificates.command' that comes with your Python installation, "
            "or install the 'certifi' package (pip install certifi) and restart. "
            f"Original error: {e}"
        )

# ==================================================
# Header with left-aligned logo (uses medBillDozer-logo-transparent.png)
# ==================================================
logo_path = Path("medBillDozer-logo-transparent.png")
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

# ==================================================
# Input
# ==================================================
st.markdown("### Analyze a Document")

bill_text = st.text_area(
    "Paste bill, receipt, or claim history text",
    height=240,
    placeholder="Paste text here..."
    , key="text_area_1"
)

# expose a stable widget key so external integrations can reference it
bill_text = st.session_state.get("text_area_1", bill_text)

# Offer OpenAI-assisted analysis when the API key is present in the environment
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
use_openai = False
if OPENAI_KEY:
    use_openai = st.checkbox("Run OpenAI-assisted analysis (uses $OPENAI_API_KEY)", value=False)

analyze = st.button("Analyze with medBillDozer")

# ==================================================
# Analysis logic (demo-grade heuristics)
# ==================================================
def analyze_text(text: str):
    t = text.lower()
    flags = []

    # Duplicate procedures
    if t.count("45378") > 1 or t.count("d2740") > 1:
        flags.append((
            "Possible duplicate procedure",
            "The same procedure code appears more than once for the same date of service."
        ))

    # Dental lab fee bundling
    if "lab fee" in t and "crown" in t:
        flags.append((
            "Potential unbundled lab fee",
            "Lab fees are often included in crown allowances and may not be separately billable."
        ))

    # Preventive coverage mismatch
    if "screening" in t and ("patient responsibility" in t or "not covered" in t):
        flags.append((
            "Preventive coverage mismatch",
            "Preventive services are often covered at 100% with no patient cost."
        ))

    # FSA eligibility mix
    if "vitamin" in t and "fsa" in t:
        flags.append((
            "Mixed FSA eligibility",
            "Receipt includes both FSA-eligible and non-eligible items."
        ))

    # Missing FSA claim
    if "polyethylene glycol" in t and "claim history" in t:
        flags.append((
            "Missing FSA claim",
            "An FSA-eligible prescription appears on the receipt but not in the claim history."
        ))

    # Insurance shows $0 OOP but bill shows balance
    if "out-of-pocket" in t and "$0.00" in t and "patient responsibility" in t:
        flags.append((
            "Bill conflicts with insurance outcome",
            "Insurance claims show $0 out-of-pocket, but the bill indicates a balance due."
        ))

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

        # If the environment provides an OpenAI API key and the user opted in, run the LLM prompt
        if OPENAI_KEY and use_openai:
            st.markdown("### OpenAI-assisted analysis")
            with st.spinner("Running OpenAI analysis..."):
                system_msg = {
                    "role": "system",
                    "content": (
                        "You are an assistant specialized in analyzing medical bills, EOBs, receipts, "
                        "and insurance claim histories. Identify billing errors (duplicate procedure codes for the same "
                        "date of service, mismatched allowed/paid amounts, apparent balance-due vs insurer-paid conflicts), "
                        "and specifically detect instances where an FSA-eligible copay or patient responsibility amount "
                        "appears in a bill but is NOT listed in any provided FSA claim history."
                    )
                }

                user_msg = {
                    "role": "user",
                    "content": (
                        "Analyze the following document and return a strict JSON object with the key `issues` containing "
                        "an array of issues. Each issue should include: `type` (one of: duplicate_code, missing_fsa_copay, "
                        "inconsistent_insurance, other), `code` (if applicable), `date` (if applicable), `evidence` (short text "
                        "excerpt supporting the finding), and `recommended_action` (short guidance). Only return valid JSON.\n\n"
                        f"DOCUMENT:\n{bill_text}"
                    )
                }

                try:
                    resp = call_openai_chat(OPENAI_KEY, [system_msg, user_msg])
                    content = resp.get("choices", [])[0].get("message", {}).get("content", "")
                    # attempt to parse JSON from model output
                    parsed = None
                    try:
                        parsed = json.loads(content)
                    except Exception:
                        # sometimes the model wraps JSON in markdown; try to extract the first JSON block
                        import re
                        m = re.search(r"\{[\s\S]*\}", content)
                        if m:
                            try:
                                parsed = json.loads(m.group(0))
                            except Exception:
                                parsed = None

                    if parsed:
                        st.json(parsed)
                    else:
                        st.text_area("OpenAI raw response", content, height=240)
                except Exception as e:
                    st.error(f"OpenAI request failed: {e}")

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
