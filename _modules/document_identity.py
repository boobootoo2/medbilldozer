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
    Never removes or overwrites existing document_id.
    Safe to call repeatedly.
    """
    print(f"Enhancing identity for doc: {doc.get('document_id')}")
    if doc.get("_identity"):
        print(f"  Already has identity, skipping.")
        return

    facts = doc.get("facts")
    if not facts:
        print(f"  No facts found, skipping.")
        return

    canonical = build_canonical_string(facts)
    print(f"Canonical string: {canonical}")
    digest = hash_canonical(canonical)
    print(f"Document hash: {digest}")

    doc["_identity"] = {
        "canonical": canonical,
        "hash": digest,
    }
