# _modules/ui_documents.py

import streamlit as st
import hashlib


def _make_document_id(text: str, index: int) -> str:
    """
    Human-readable, semi-stable document ID for hackathon use.
    Later we can replace this with fact-based fingerprinting.
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
    Renders multiple document text inputs.
    Returns a list of structured document objects.
    """

    st.session_state.setdefault(
        "documents",
        [{"id": 0, "raw_text": ""}],
    )


    st.markdown("### Paste bill, receipt, or claim history text")

    docs = st.session_state["documents"]

    for i, doc in enumerate(docs):
        with st.container(border=True):
            st.markdown(f"**Document {i + 1}**")

            key = f"doc_text_{i}"
            doc["raw_text"] = st.text_area(
                "Document text",
                value=doc.get("raw_text", ""),
                height=200,
                key=key,
                label_visibility="collapsed",
            )

            doc["raw_text"] = st.session_state[key]




            if len(docs) > 1:
                if st.button("Remove", key=f"remove_{doc['id']}"):
                    docs.remove(doc)
                    st.rerun()

    if st.button("➕ Add another document"):
        next_id = max(d["id"] for d in docs) + 1
        docs.append({"id": next_id, "raw_text": ""})
        st.rerun()

    structured_docs = []
    for idx, doc in enumerate(docs):
        if doc["raw_text"].strip():
            structured_docs.append(
                {
                    "index": idx,
                    "raw_text": doc["raw_text"],
                    "document_id": _make_document_id(doc["raw_text"], idx),
                    "facts": None,
                }
            )




    return structured_docs
