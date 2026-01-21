"""Cross-document coverage matrix builder.

Builds a coverage matrix that relates receipts, FSA claims, and insurance claims
across multiple documents to identify potential duplicate payments or coverage gaps.
"""
# _modules/coverage_matrix.py
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class CoverageRow:
    """Represents a single row in the coverage matrix.
    
    Tracks amounts and document references across receipt, FSA, and insurance sources
    for a specific service on a specific date.
    """
    description: str
    date: Optional[str]

    receipt_amount: Optional[float]
    fsa_amount: Optional[float]
    insurance_amount: Optional[float]

    receipt_doc: Optional[str]
    fsa_doc: Optional[str]
    insurance_doc: Optional[str]

    status: str

def build_coverage_matrix(documents: list[dict]) -> List[CoverageRow]:
    """Build a cross-document coverage matrix from analyzed documents.
    
    Args:
        documents: List of document dicts with 'facts' and 'document_id' keys
    
    Returns:
        List[CoverageRow]: Coverage rows showing related transactions across documents
    """
    rows: dict[str, CoverageRow] = {}

    def key(desc: str, date: Optional[str]):
        """Generate unique key for matching transactions across documents."""

        return f"{desc.lower()}|{date or ''}"

    for doc in documents:
        facts = doc.get("facts") or {}
        doc_id = doc.get("document_id")
        doc_type = facts.get("document_type")

        # --------------------
        # Receipts
        # --------------------
        for item in facts.get("receipt_items", []):
            k = key(item["description"], facts.get("date_of_service"))
            rows.setdefault(
                k,
                CoverageRow(
                    description=item["description"],
                    date=facts.get("date_of_service"),
                    receipt_amount=None,
                    fsa_amount=None,
                    insurance_amount=None,
                    receipt_doc=None,
                    fsa_doc=None,
                    insurance_doc=None,
                    status="",
                )
            )
            rows[k].receipt_amount = item["amount"]
            rows[k].receipt_doc = doc_id

        # --------------------
        # FSA claims
        # --------------------
        for item in facts.get("fsa_claim_items", []):
            k = key(item["description"], item.get("date_submitted"))
            rows.setdefault(
                k,
                CoverageRow(
                    description=item["description"],
                    date=item.get("date_submitted"),
                    receipt_amount=None,
                    fsa_amount=None,
                    insurance_amount=None,
                    receipt_doc=None,
                    fsa_doc=None,
                    insurance_doc=None,
                    status="",
                )
            )
            rows[k].fsa_amount = item["amount_reimbursed"]
            rows[k].fsa_doc = doc_id

        # --------------------
        # Insurance claims
        # --------------------
        if doc_type == "insurance_claim_history":
            for claim in facts.get("insurance_claim_items", []):
                k = key(claim["description"], claim["date_of_service"])
                rows.setdefault(
                    k,
                    CoverageRow(
                        description=claim["description"],
                        date=claim["date_of_service"],
                        receipt_amount=None,
                        fsa_amount=None,
                        insurance_amount=None,
                        receipt_doc=None,
                        fsa_doc=None,
                        insurance_doc=None,
                        status="",
                    )
                )
                rows[k].insurance_amount = claim["insurance_paid"]
                rows[k].insurance_doc = doc_id

    # --------------------
    # Final status labeling
    # --------------------
    for row in rows.values():
        if row.receipt_amount and not row.fsa_amount and row.insurance_amount:
            row.status = "⚠️ Missing FSA"
        elif row.receipt_amount and row.fsa_amount:
            row.status = "✅ Reimbursed"
        elif row.receipt_amount and not row.insurance_amount:
            row.status = "❌ Not Covered"
        else:
            row.status = "ℹ️ Informational"

    return list(rows.values())
