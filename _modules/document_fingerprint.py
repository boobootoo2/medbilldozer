# _modules/document_fingerprint.py

import hashlib
from typing import Dict, Optional

FACT_ORDER = [
    "document_type",
    "facility_name",
    "provider_name",
    "patient_name",
    "date_of_birth",
    "date_of_service",
    "procedure_code",
]


def build_canonical_string(facts: Dict[str, Optional[str]]) -> str:
    """
    Builds a deterministic canonical string from extracted facts.
    Missing values are normalized to '_'.
    """

    parts = []
    for key in FACT_ORDER:
        value = facts.get(key)
        if value is None:
            value = "_"
        else:
            value = str(value).strip().lower()
        parts.append(f"{key}={value}")

    return "|".join(parts)


def hash_canonical(canonical: str) -> str:
    """
    One-way deterministic hash of the canonical string.
    """
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
