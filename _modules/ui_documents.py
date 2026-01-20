import streamlit as st

# ==================================================
# Document Inputs (dynamic, single by default)
# ==================================================
def render_document_inputs():
    st.markdown("### Analyze a Document")

    # ------------------------------
    # Initialize state ONCE
    # ------------------------------
    if "doc_inputs" not in st.session_state:
        st.session_state.doc_inputs = [""]  # ✅ ONE input by default

    # ------------------------------
    # Render inputs
    # ------------------------------
    raw_fields = []

    for i, value in enumerate(st.session_state.doc_inputs):
        text = st.text_area(
            f"Document {i + 1}",
            value=value,
            height=220,
            key=f"doc_input_{i}",
        )
        raw_fields.append(text)

    # ------------------------------
    # Add another document
    # ------------------------------
    if st.button("➕ Add another document"):
        st.session_state.doc_inputs.append("")
        st.rerun()

    # ------------------------------
    # Validation (duplicates only)
    # ------------------------------
    errors = []
    seen = {}

    for idx, text in enumerate(raw_fields, start=1):
        normalized = " ".join((text or "").split())
        if not normalized:
            continue  # empty is allowed

        h = hash(normalized)
        if h in seen:
            errors.append(
                f"Document {idx} is a duplicate of document {seen[h]}."
            )
        else:
            seen[h] = idx

    if errors:
        st.error("⚠️ Please fix the following input issues:")
        for err in errors:
            st.markdown(f"- {err}")
        return []  # 🚫 BLOCK analysis

    # ------------------------------
    # Build documents (non-empty only)
    # ------------------------------
    documents = []

    for raw in raw_fields:
        if not raw.strip():
            continue

        documents.append({
            "raw_text": raw,
            "facts": None,
            "analysis": None,
            "document_id": None,
        })

    return documents
