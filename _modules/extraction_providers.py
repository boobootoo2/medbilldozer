# _modules/extraction_providers.py

# ✅ MUST be top-level
EXTRACTOR_OPTIONS = {
    "OpenAI": "openai",
    "Local heuristic": "heuristic",
}

# ✅ ALSO top-level
DOCUMENT_EXTRACTOR_MAP = {
    "medical_bill": "medgemma",
    "insurance_eob": "medgemma",
    "pharmacy_receipt": "heuristic",
    "dental_bill": "openai",
    "generic": "openai",
}
