# _modules/transaction_normalization.py

from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from collections import defaultdict
import hashlib
import json


# ==================================================
# Helpers
# ==================================================

def _norm_str(value: Optional[str]) -> str:
    return value.strip().lower() if value else ""


def _norm_money(value: Optional[Decimal]) -> str:
    if value is None:
        return ""
    return f"{Decimal(value):.2f}"


# ==================================================
# Canonical Transaction Fingerprint
# ==================================================

def build_transaction_fingerprint(
    *,
    patient_dob: Optional[str],
    provider_name: Optional[str],
    date_of_service: Optional[str],
    cpt_code: Optional[str],
    units: int,
    billed_amount: Optional[Decimal],
) -> str:
    parts = {
        "patient_dob": _norm_str(patient_dob),
        "provider": _norm_str(provider_name),
        "date": _norm_str(date_of_service),
        "cpt": _norm_str(cpt_code),
        "units": str(units or 1),
        "billed": _norm_money(billed_amount),
    }

    serialized = json.dumps(parts, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


# ==================================================
# Normalized Transaction Model
# ==================================================

@dataclass
class NormalizedTransaction:
    canonical_id: str
    source_document_id: str

    patient_dob: Optional[str]
    provider_name: Optional[str]

    date_of_service: Optional[str]
    cpt_code: Optional[str]
    units: int

    billed_amount: Optional[Decimal]
    allowed_amount: Optional[Decimal]

    description: Optional[str]


# ==================================================
# Line-item → Normalized Transactions
# ==================================================

def normalize_line_items(
    line_items: List[dict],
    source_document_id: str,
) -> List[NormalizedTransaction]:
    normalized: List[NormalizedTransaction] = []

    for item in line_items:
        billed = item.get("billed")
        allowed = item.get("allowed")

        billed_amount = Decimal(str(billed)) if billed is not None else None
        allowed_amount = Decimal(str(allowed)) if allowed is not None else None

        canonical_id = build_transaction_fingerprint(
            patient_dob=item.get("patient_dob"),
            provider_name=item.get("provider"),
            date_of_service=item.get("date_of_service"),
            cpt_code=item.get("cpt"),
            units=item.get("units", 1),
            billed_amount=billed_amount,
        )

        normalized.append(
            NormalizedTransaction(
                canonical_id=canonical_id,
                source_document_id=source_document_id,

                patient_dob=item.get("patient_dob"),
                provider_name=item.get("provider"),

                date_of_service=item.get("date_of_service"),
                cpt_code=item.get("cpt"),
                units=item.get("units", 1),

                billed_amount=billed_amount,
                allowed_amount=allowed_amount,

                description=item.get("description"),
            )
        )

    return normalized


# ==================================================
# De-duplication + Provenance
# ==================================================

def deduplicate_transactions(
    transactions: List[NormalizedTransaction],
) -> Tuple[
    Dict[str, NormalizedTransaction],
    Dict[str, List[str]],
]:
    unique: Dict[str, NormalizedTransaction] = {}
    provenance: Dict[str, List[str]] = defaultdict(list)

    for tx in transactions:
        provenance[tx.canonical_id].append(tx.source_document_id)

        if tx.canonical_id not in unique:
            unique[tx.canonical_id] = tx

    return unique, dict(provenance)
