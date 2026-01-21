# _modules/fact_normalizer.py

from typing import Dict, Optional
from datetime import datetime
import re

DATE_INPUT_FORMATS = [
    "%B %d, %Y",     # January 18, 2026
    "%b %d, %Y",     # Jan 18, 2026
    "%m/%d/%Y",      # 01/18/2026
    "%Y-%m-%d",      # 2026-01-18
]

TIME_INPUT_FORMATS = [
    "%I:%M %p",      # 3:42 PM
    "%H:%M",         # 15:42
]


def _normalize_string(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value.lower()


def _normalize_date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    value = value.strip()

    for fmt in DATE_INPUT_FORMATS:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.date().isoformat()   # YYYY-MM-DD
        except ValueError:
            continue

    return None  # fail closed


def _normalize_time(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    value = value.strip()

    for fmt in TIME_INPUT_FORMATS:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%H:%M")    # 24-hour HH:MM
        except ValueError:
            continue

    return None


def normalize_facts(facts: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    """
    Provider-agnostic normalization pass.
    SAFE: never raises, preserves keys.
    """

    normalized = {}

    for key, value in facts.items():

        if key in {
            "patient_name",
            "provider_name",
            "facility_name",
            "address",
            "document_type",
        }:
            normalized[key] = _normalize_string(value)

        elif key in {
            "date_of_service",
            "date_of_birth",
            "date_range_start",
            "date_range_end",
        }:
            normalized[key] = _normalize_date(value)

        elif key in {
            "time_of_service",
        }:
            normalized[key] = _normalize_time(value)

        elif key in {
            "phone_number",
            "receipt_number",
            "store_id",
            "procedure_code",
        }:
            # Preserve formatting but trim
            normalized[key] = value.strip() if value else None

        else:
            # Pass-through for unknown future fields
            normalized[key] = value

    return normalized
