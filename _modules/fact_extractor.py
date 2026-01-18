import re
from typing import Dict, Optional

def extract_facts(raw_text: str) -> Dict[str, Optional[str]]:
    """
    Minimal heuristic extractor.
    Safe, deterministic, no AI.
    """

    facts = {
        "patient_name": None,
        "date_of_service": None,
        "provider_name": None,
        "document_type": None,
    }

    # Date heuristic
    match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}", raw_text)
    if match:
        facts["date_of_service"] = match.group(0)

    # Very light document-type heuristic
    lowered = raw_text.lower()
    if "receipt" in lowered:
        facts["document_type"] = "receipt"
    elif "statement" in lowered:
        facts["document_type"] = "statement"

    return facts
