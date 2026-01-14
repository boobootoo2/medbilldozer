import streamlit as st

st.set_page_config(
    page_title="medBillDozer",
    layout="centered"
)

# Try to embed a vector icon (prefer traced white SVG), fall back to emoji title
def _render_title_with_svg():
    import os
    svg_candidates = ["icon-traced-white.svg", "icon.svg", "bulldozer-white.svg"]
    for name in svg_candidates:
        if os.path.exists(name):
            try:
                with open(name, "r", encoding="utf-8") as f:
                    svg_icon = f.read()
                st.markdown(
                    f"<div style='display:flex; align-items:center; gap:10px'>"
                    f"<div style='width:38px; height:38px'>{svg_icon}</div>"
                    f"<h1 style='margin:0; font-size:28px'>medBillDozer</h1>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                return
            except Exception:
                continue
    # fallback
    st.title("🧾 medBillDozer")


_render_title_with_svg()
st.subheader("Detecting medical billing errors")

st.markdown(
    "Paste a medical bill or Explanation of Benefits (EOB) below. "
    "medBillDozer will flag **likely billing issues** and suggest next steps."
)

bill_text = st.text_area(
    "Paste your medical bill or EOB text",
    height=260,
    placeholder="Paste medical bill or EOB text here..."
)

with st.expander("Optional insurance details"):
    in_network = st.selectbox("In-network provider?", ["Yes", "No"])
    deductible_status = st.selectbox("Deductible status", ["Met", "Not met"])
    coinsurance = st.slider("Coinsurance (%)", 0, 50, 20)

analyze = st.button("🔍 Analyze with medBillDozer")

if analyze:
    if not bill_text.strip():
        st.warning("Please paste a medical bill or EOB.")
    else:
        st.success("Analysis complete")

        st.markdown("## 🚩 Flagged Issues")

        st.markdown(
            "**1. Possible duplicate charge**  \n"
            "- *Reason:* The same service appears more than once on the same date.  \n"
            "- *Confidence:* **High**"
        )

        st.markdown(
            "**2. Math inconsistency in patient responsibility**  \n"
            "- *Reason:* Copay + coinsurance exceeds the allowed amount.  \n"
            "- *Confidence:* **Medium**"
        )

        st.markdown(
            "**3. Coverage mismatch signal**  \n"
            "- *Reason:* Charge marked as not covered, but policy notes suggest coverage.  \n"
            "- *Confidence:* **Low**"
        )

        st.markdown("## 💬 What this means")

        st.markdown(
            "These issues do **not** guarantee an error, but they are worth reviewing. "
            "Billing mistakes are common and often resolved after clarification."
        )

        st.markdown("## 📋 Suggested Next Steps")

        st.markdown(
            "1. Contact the billing office listed on your statement.  \n"
            "2. Ask whether duplicate charges were applied in error.  \n"
            "3. Request an itemized bill if you do not already have one.  \n"
            "4. Confirm coverage details with your insurer."
        )

        st.markdown("### 📝 Sample dispute script")

        st.code(
            "Hello, I’m reviewing my recent medical bill and noticed a few charges "
            "that may be duplicated or calculated incorrectly. "
            "Could you please review these items and provide clarification?"
        )

st.caption(
    "medBillDozer is a prototype for educational purposes only. "
    "It does not provide medical, legal, or financial advice."
)
