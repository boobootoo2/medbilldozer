# _modules/ui_documents.py

import streamlit as st
import hashlib


def _make_document_id(text: str, index: int) -> str:
    """
    Human-readable, semi-stable document ID.
    Backward compatible.
    """
    date_hint = "unknown-date"
    vendor_hint = "unknown-vendor"

    for line in text.splitlines():
        if "202" in line:
            date_hint = line.strip()[:10]
            break

    raw = f"{vendor_hint}|{date_hint}|{index}"
    short_hash = hashlib.sha1(raw.encode()).hexdigest()[:6]

    return f"{vendor_hint}-{date_hint}-{short_hash}"


def render_document_inputs():
    """
    Renders editable document inputs.

    Returns:
        List[dict] — structured documents ready for analysis
    """

    # --------------------------------------------------
    # 1️⃣ Initialize session documents ONCE
    # --------------------------------------------------
    if "documents" not in st.session_state:
        st.session_state["documents"] = [
            {"id": 0, "raw_text": ""}
        ]

    docs = st.session_state["documents"]

    st.markdown("### Paste bill, receipt, or claim history text")

    # --------------------------------------------------
    # 2️⃣ Render editors
    # --------------------------------------------------
    for i, doc in enumerate(docs):
        with st.container(border=True, key=f"input_doc_container_{doc['id']}"):
            st.markdown(f"**Document {i + 1}**")

            doc["raw_text"] = st.text_area(
                "Document text",
                value=doc.get("raw_text", ""),
                height=220,
                key=f"input_doc_text_{doc['id']}",
                label_visibility="collapsed",
            )

            if len(docs) > 1:
                if st.button("Remove", key=f"remove_doc_{doc['id']}"):
                    docs.remove(doc)
                    st.rerun()

    # --------------------------------------------------
    # 3️⃣ Add document
    # --------------------------------------------------
    if st.button("➕ Add another document"):
        next_id = max(d["id"] for d in docs) + 1
        docs.append({"id": next_id, "raw_text": ""})
        st.rerun()

    # --------------------------------------------------
    # 4️⃣ Build structured docs (NO mutation)
    # --------------------------------------------------
    structured_docs = []

    for idx, doc in enumerate(docs):
        text = doc.get("raw_text", "").strip()
        if not text:
            continue

        structured_docs.append(
            {
                "index": idx,
                "raw_text": text,
                "document_id": _make_document_id(text, idx),
                "facts": None,
                "analysis": None,
            }
        )

    return structured_docs
