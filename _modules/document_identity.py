import hashlib
from typing import Dict, Optional


def build_canonical_string(facts: Dict[str, Optional[str]]) -> str:
    """
    Stable, ordered representation of extracted facts.
    Missing values become empty strings.
    """
    keys = sorted(facts.keys())
    parts = [f"{k}={facts.get(k) or ''}" for k in keys]
    return "|".join(parts)


def hash_canonical(canonical: str) -> str:
    """
    Deterministic, one-way hash.
    Same input => same output.
    """
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:10]


def maybe_enhance_identity(doc: dict) -> None:
    """
    Adds a fact-based identity IF facts exist.
    Upgrades document_id to the fact-hash once available.
    Safe to call repeatedly.
    """

    if doc.get("_identity"):
        return

    facts = doc.get("facts")
    if not facts:
        return

    canonical = build_canonical_string(facts)
    digest = hash_canonical(canonical)

    doc["_identity"] = {
        "canonical": canonical,
        "hash": digest,
    }

    # 🔁 BACKWARD-COMPATIBLE UPGRADE
    doc["legacy_document_id"] = doc.get("document_id")
    doc["document_id"] = digest
