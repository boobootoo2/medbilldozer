import hashlib
import re
from typing import Dict, Optional
from datetime import datetime


# ==================================================
# Canonical identity (internal)
# ==================================================

def build_canonical_string(facts: Dict[str, Optional[str]]) -> str:
    keys = sorted(facts.keys())
    parts = [f"{k}={facts.get(k) or ''}" for k in keys]
    return "|".join(parts)


def hash_canonical(canonical: str) -> str:
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:10]


# ==================================================
# User-facing document label
# ==================================================

def _shorten(text: Optional[str], max_len=28) -> str:
    if not text:
        return "Unknown"
    return re.sub(r"\s+", " ", text).strip()[:max_len]


def _format_date(date_str: Optional[str]) -> str:
    if not date_str:
        return "Unknown Date"

    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return date_str


def _pretty_doc_type(doc_type: Optional[str]) -> Optional[str]:
    if not doc_type:
        return None
    return doc_type.replace("_", " ").title()



def make_user_friendly_document_id(
    facts: Dict[str, Optional[str]],
    fallback_index: Optional[int] = None,
) -> str:
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
