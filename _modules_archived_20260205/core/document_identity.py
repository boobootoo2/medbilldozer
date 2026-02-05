"""Document identity and labeling utilities.

Provides functions to generate canonical identities, user-friendly labels,
and unique fingerprints for medical billing documents.
"""
import hashlib
import re
from typing import Dict, Optional
from datetime import datetime


# ==================================================
# Canonical identity (internal)
# ==================================================


def build_canonical_string(facts: Dict[str, Optional[str]]) -> str:
    """Build canonical string representation of document facts.

    Args:
        facts: Dictionary of document facts

    Returns:
        str: Canonical string with sorted key-value pairs
    """
    keys = sorted(facts.keys())
    parts = [f"{k}={facts.get(k) or ''}" for k in keys]
    return "|".join(parts)


def hash_canonical(canonical: str) -> str:
    """Generate short hash from canonical string.

    Args:
        canonical: Canonical string representation

    Returns:
        str: First 10 characters of SHA256 hash
    """
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:10]


# ==================================================
# User-facing document label
# ==================================================


def _shorten(text: Optional[str], max_len=28) -> str:
    """Shorten text to maximum length, normalizing whitespace.

    Args:
        text: Text to shorten
        max_len: Maximum length (default 28)

    Returns:
        str: Shortened text or "Unknown" if text is None
    """
    if not text:
        return "Unknown"
    return re.sub(r"\s+", " ", text).strip()[:max_len]


def _format_date(date_str: Optional[str]) -> str:
    """Parse and format date string to YYYY-MM-DD format.

    Tries multiple common date formats. Returns original string if parsing fails.

    Args:
        date_str: Date string in various formats

    Returns:
        str: Date in YYYY-MM-DD format or original string
    """
    if not date_str:
        return "Unknown Date"

    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return date_str


def _pretty_doc_type(doc_type: Optional[str]) -> Optional[str]:
    """Convert document type to user-friendly title case.

    Args:
        doc_type: Document type string (e.g., 'insurance_claim')

    Returns:
        Optional[str]: Title case string (e.g., 'Insurance Claim') or None
    """
    if not doc_type:
        return None
    return doc_type.replace("_", " ").title()


def make_user_friendly_document_id(
    facts: Dict[str, Optional[str]],
    fallback_index: Optional[int] = None,
) -> str:
    """Generate user-friendly document label from facts.

    Creates a readable label like "Provider Name · 2024-01-15 · Document Type"

    Args:
        facts: Dictionary of document facts
        fallback_index: Optional index to append for disambiguation

    Returns:
        str: User-friendly document label
    """
    provider = _shorten(
        facts.get("facility_name")
        or facts.get("provider_name")
        or facts.get("merchant")
    )


    date = _format_date(
        facts.get("date_of_service")
        or facts.get("statement_date")
    )

    descriptor = _pretty_doc_type(
        facts.get("document_type")
        or facts.get("visit_type")
        or facts.get("claim_type")
    )

    label = f"{provider} · {date}"
    if descriptor:
        label += f" · {descriptor}"

    if fallback_index is not None:
        label += f" ({fallback_index})"

    return label


# ==================================================
# Identity enhancement
# ==================================================


def maybe_enhance_identity(doc: dict) -> None:
    """Enhance document with canonical identity and hash.

    Modifies the document dict in-place to add '_identity' field if not present.

    Args:
        doc: Document dict with 'facts' key
    """
    facts = doc.get("facts")
    if not facts:
        return

    # Internal identity
    if not doc.get("_identity"):
        canonical = build_canonical_string(facts)
        digest = hash_canonical(canonical)

        doc["_identity"] = {
            "canonical": canonical,
            "hash": digest,
        }
        doc["internal_id"] = digest

    # User-facing ID
    if not doc.get("document_id") or doc.get("document_id") == doc.get("legacy_document_id"):
        doc["legacy_document_id"] = doc.get("document_id")
        doc["document_id"] = make_user_friendly_document_id(
            facts=facts,
            fallback_index=doc.get("_index"),
        )

