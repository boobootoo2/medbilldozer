"""Transaction normalization and deduplication.

Provides utilities to normalize billing transactions from various document formats
into a canonical structure, build unique fingerprints, and deduplicate across documents.
"""
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
    """Normalize string to lowercase with trimmed whitespace.
    
    Args:
        value: String to normalize
    
    Returns:
        str: Normalized lowercase string or empty string if None
    """
    return value.strip().lower() if value else ""


def _norm_money(value: Optional[Decimal]) -> str:
    """Format money value to standardized string.
    
    Args:
        value: Decimal amount
    
    Returns:
        str: Formatted amount with 2 decimal places or empty string if None
    """
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
    """Build canonical fingerprint for transaction deduplication.
    
    Creates a unique hash based on normalized transaction attributes.
    
    Args:
        patient_dob: Patient date of birth
        provider_name: Provider or facility name
        date_of_service: Service date
        cpt_code: CPT procedure code
        units: Number of units
        billed_amount: Billed amount
    
    Returns:
        str: SHA256 hash of canonical transaction representation
    """
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
    """Normalized representation of a billing transaction.
    
    Provides a standardized structure for transactions from different document types
    with a unique canonical_id for deduplication.
    """
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
    """Convert raw line items to normalized transaction objects.
    
    Args:
        line_items: List of raw line item dicts from document facts
        source_document_id: ID of source document for provenance tracking
    
    Returns:
        List[NormalizedTransaction]: Normalized transactions with canonical IDs
    """
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
    """Deduplicate transactions and track provenance.
    
    Args:
        transactions: List of normalized transactions (may contain duplicates)
    
    Returns:
        Tuple of:
            - Dict mapping canonical_id to unique transaction
            - Dict mapping canonical_id to list of source document IDs
    """
    unique: Dict[str, NormalizedTransaction] = {}
    provenance: Dict[str, List[str]] = defaultdict(list)

    for tx in transactions:
        provenance[tx.canonical_id].append(tx.source_document_id)

        if tx.canonical_id not in unique:
            unique[tx.canonical_id] = tx

    return unique, dict(provenance)
