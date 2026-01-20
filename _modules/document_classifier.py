# _modules/document_classifier.py
import re
from collections import defaultdict

DOCUMENT_SIGNALS = {
    "medical_bill": [
        r"\bCPT\b",
        r"\bICD-10\b",
        r"Date of Service",
        r"Allowed Amount",
        r"Patient Responsibility",
    ],
    "insurance_eob": [
        r"Explanation of Benefits",
        r"\bEOB\b",
        r"Insurance Paid",
        r"Claim Number",
    ],
    "pharmacy_receipt": [
        r"\bRx\b",
        r"NDC",
        r"Pharmacy",
        r"Copay",
    ],
    "dental_bill": [
        r"\bD\d{4}\b",
        r"Dental",
        r"Crown",
        r"Lab Fee",
    ],
}

def classify_document(text: str) -> dict:
    scores = defaultdict(int)

    for doc_type, patterns in DOCUMENT_SIGNALS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                scores[doc_type] += 1

    if not scores:
        return {
            "document_type": "generic",
            "confidence": 0.0,
            "scores": {},
        }

    best_type = max(scores, key=scores.get)
    total = sum(scores.values())

    return {
        "document_type": best_type,
        "confidence": scores[best_type] / total,
        "scores": dict(scores),
    }
