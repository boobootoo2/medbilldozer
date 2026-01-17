import streamlit as st


def render_document_inputs(label="Paste bill, receipt, or claim history text"):
    """
    Renders a dynamic list of text areas for document input.
    Returns a list of document texts (non-empty).
    """

    # Initialize document list once
    st.session_state.setdefault(
        "documents",
        [{"id": 0, "text": ""}],
    )

    st.markdown(f"### {label}")

    documents = st.session_state["documents"]

    # Render each document input
    for idx, doc in enumerate(documents):
        with st.container(border=True):
            st.markdown(f"**Document {idx + 1}**")

            doc["text"] = st.text_area(
                label=f"Document {idx + 1} text",
                value=doc["text"],
                height=200,
                key=f"doc_text_{doc['id']}",
                label_visibility="collapsed",
            )

            # Allow removal if more than one document
            if len(documents) > 1:
                if st.button(
                    "Remove document",
                    key=f"remove_doc_{doc['id']}",
                ):
                    documents.remove(doc)
                    st.rerun()

    # Add new document button
    if st.button("➕ Add another document"):
        next_id = max(doc["id"] for doc in documents) + 1
        documents.append({"id": next_id, "text": ""})
        st.rerun()

    # Return only non-empty documents
    return [doc["text"] for doc in documents if doc["text"].strip()]
