import re
from typing import Dict, Optional

DATE_REGEX = r"\b\d{2}/\d{2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b"
CPT_REGEX = r"\b\d{5}\b"

def extract_dates(text: str) -> Dict[str, Optional[str]]:
    dos = None
    dob = None

    for line in text.splitlines():
        lower = line.lower()

        if "date of service" in lower:
            m = re.search(DATE_REGEX, line)
            if m:
                dos = m.group(0)

        if "date of birth" in lower or "dob" in lower:
            m = re.search(DATE_REGEX, line)
            if m:
                dob = m.group(0)

    return {
        "date_of_service": dos,
        "date_of_birth": dob,
    }

def extract_procedure_code(text: str) -> Optional[str]:
    matches = re.findall(CPT_REGEX, text)
    return matches[0] if matches else None
