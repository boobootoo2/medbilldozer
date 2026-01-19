# _modules/local_heuristic_extractor.py

import re
from typing import Dict, Optional

from _modules.extraction_prompt import FACT_KEYS


# -----------------------------
# helpers
# -----------------------------

def _safe_empty() -> Dict[str, Optional[str]]:
    return {k: None for k in FACT_KEYS}


def _find_first(pattern: str, text: str) -> Optional[str]:
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else None


def _find_date(patterns: list[str], text: str) -> Optional[str]:
    for p in patterns:
        value = _find_first(p, text)
        if value:
            return value
    return None


# -----------------------------
# main extractor
# -----------------------------

def extract_facts_local(raw_text: str) -> Dict[str, Optional[str]]:
    """
    Deterministic local heuristic fact extractor.
    Conservative by design.
    """

    if not raw_text or not raw_text.strip():
        return _safe_empty()

    text = raw_text.strip()
    facts = _safe_empty()

    # -----------------------------
    # Patient / participant
    # -----------------------------
    facts["patient_name"] = _find_first(
        r"(?:Patient Name|Participant|Member):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        text,
    )

    facts["date_of_birth"] = _find_first(
        r"(?:Date of Birth|DOB):\s*([0-9]{2}/[0-9]{2}/[0-9]{4})",
        text,
    )

    # -----------------------------
    # Dates / times
    # -----------------------------
    facts["date_of_service"] = _find_date(
        [
            r"Date of Service:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})",
            r"Date:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})",
            r"(\d{2}/\d{2}/\d{4})",
        ],
        text,
    )

    facts["time_of_service"] = _find_first(
        r"Time:\s*([0-9]{1,2}:[0-9]{2}\s*(?:AM|PM))",
        text,
    )

    # -----------------------------
    # Provider / facility
    # -----------------------------
    facts["provider_name"] = _find_first(
        r"(?:Rendering Provider|Treating Dentist|Provider):\s*([A-Za-z.,\s]+)",
        text,
    )

    # Pharmacy / merchant name (often first prominent line)
    if not facts["provider_name"]:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if lines:
            facts["provider_name"] = lines[0]

    facts["facility_name"] = _find_first(
        r"(?:Facility|Location):\s*(.+)",
        text,
    ) or facts["provider_name"]

    # -----------------------------
    # Address / contact
    # -----------------------------
    facts["address"] = _find_first(
        r"(\d{2,5}\s+.+?,\s*[A-Za-z\s]+,\s*[A-Z]{2})",
        text,
    )

    facts["phone_number"] = _find_first(
        r"(\(\d{3}\)\s*\d{3}-\d{4})",
        text,
    )

    # -----------------------------
    # Identifiers
    # -----------------------------
    facts["receipt_number"] = _find_first(
        r"(?:Receipt|Transaction)\s*#?:?\s*([A-Za-z0-9\-]+)",
        text,
    )

    facts["store_id"] = _find_first(
        r"(?:Store|Location)\s*#\s*(\d+)",
        text,
    )

    facts["procedure_code"] = _find_first(
        r"\b([A-Z]\d{4}|\d{5})\b",
        text,
    )

    # -----------------------------
    # Document type classification
    # -----------------------------
    if re.search(r"\bD\d{4}\b", text):
        facts["document_type"] = "dental_bill"

    elif re.search(r"\b\d{5}\b", text):
        facts["document_type"] = "medical_bill"

    elif re.search(r"Receipt|Store\s*#", text, re.IGNORECASE):
        facts["document_type"] = "pharmacy_receipt"

    elif re.search(r"Flexible Spending Account|FSA|Reimbursed", text, re.IGNORECASE):
        facts["document_type"] = "fsa_claim_history"

    elif re.search(r"Insurance Claim History|Deductible|Out-of-Pocket", text, re.IGNORECASE):
        facts["document_type"] = "insurance_claim_history"

    else:
        facts["document_type"] = "unknown"

    return facts
