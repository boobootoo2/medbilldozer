"""Document input and management UI.

Provides UI components for document input, validation, and user-friendly labeling.
"""
import streamlit as st
import re
from datetime import datetime


def _shorten_provider(name: str, max_len=28) -> str:
    """Shorten provider name to maximum length.

    Args:
        name: Provider name
        max_len: Maximum length (default 28)

    Returns:
        str: Shortened name or "Unknown Provider" if None
    """
    if not name:
        return "Unknown Provider"
    name = re.sub(r"\s+", " ", name).strip()
    return name[:max_len]


def _format_date(date_str: str) -> str:
    """
    Accepts many formats, returns YYYY-MM-DD or YYYY-MM
    """
    if not date_str:
        return "Unknown Date"

    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Month-only fallback
    try:
        return datetime.strptime(date_str, "%B %Y").strftime("%Y-%m")
    except Exception:
        return date_str


def make_user_friendly_document_id(
    facts: dict,
    fallback_index: int | None = None,
) -> str:
    """Generate user-friendly document ID from facts.

    Creates readable label like "Provider · Date · Type".

    Args:
        facts: Document facts dictionary
        fallback_index: Optional index for disambiguation

    Returns:
        str: User-friendly document label
    """
    provider = _shorten_provider(
        facts.get("facility")
        or facts.get("provider")
        or facts.get("merchant")
    )

    date = _format_date(
        facts.get("date_of_service")
        or facts.get("statement_date")
    )

    doc_type = (
        facts.get("document_type")
        or facts.get("claim_type")
        or facts.get("visit_type")
    )

    account = facts.get("account_number") or facts.get("claim_number")

    tail = doc_type or (f"Acct {account}" if account else None)

    label = f"{provider} · {date}"
    if tail:
        label += f" · {tail}"

    if fallback_index is not None:
        label += f" ({fallback_index})"

    return label


# ==================================================
# Document Inputs (dynamic, single by default)
# ==================================================


def render_document_inputs():
    """Render dynamic document input fields with validation.

    Allows users to paste multiple documents. Validates for duplicates and
    returns list of document dicts ready for analysis.

    Returns:
        list[dict]: List of document dicts with 'raw_text', 'facts', 'analysis', 'document_id' keys.
                   Returns empty list if validation fails.
    """
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

