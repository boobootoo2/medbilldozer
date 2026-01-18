# _modules/openai_langextractor.py

import json
import re
from typing import Dict, Optional
from openai import OpenAI


FACT_KEYS = [
    "patient_name",
    "date_of_birth",
    "date_of_service",
    "provider_name",
    "facility_name",
    "procedure_code",
    "document_type",
]

client = OpenAI()


def _safe_empty_result() -> Dict[str, Optional[str]]:
    return {k: None for k in FACT_KEYS}


def _clean_json(text: str) -> str:
    """
    Removes markdown fences and leading junk.
    """
    text = text.strip()

    # Remove ```json fences
    text = re.sub(r"^```(?:json)?", "", text)
    text = re.sub(r"```$", "", text)

    return text.strip()


def extract_facts_openai(raw_text: str) -> Dict[str, Optional[str]]:
    """
    Extract structured healthcare facts using OpenAI.
    SAFE: never raises, always returns all keys.
    """

    if not raw_text or not raw_text.strip():
        return _safe_empty_result()

    prompt = f"""
You extract structured facts from healthcare-related documents.

Return ONLY valid JSON with EXACTLY these keys:
patient_name, date_of_birth, date_of_service, provider_name, facility_name, procedure_code, document_type

INTERPRETATION RULES:

- patient_name:
  Only extract if explicitly labeled
  Examples: "Patient Name", "Member Name"
  Otherwise use null

- date_of_birth:
  Only if explicitly labeled
  Examples: "DOB", "Date of Birth"
  Otherwise use null

- date_of_service:
  • Medical bills: labeled "Date of Service"
  • Pharmacy receipts: transaction date (e.g., "Date:", "Transaction Date")
  Preserve the original text format exactly

- provider_name:
  • Medical bills:
      – Rendering or billing provider
      – Must be explicitly labeled
  • Pharmacy receipts:
      – Pharmacy or store name
      – Often appears at the top of the receipt
      – Example: "GreenLeaf Pharmacy"
  Otherwise use null

- facility_name:
  • Hospital names, clinics, or store locations
  • Extract only if clearly stated

- procedure_code:
  • CPT or HCPCS codes only
  • Must be explicitly present
  • Never infer or guess

- document_type:
  Choose exactly ONE:
  • medical_bill → hospital or physician billing statements
  • pharmacy_receipt → retail or mail-order pharmacy receipts
  • insurance_document → EOBs, claims summaries, insurer letters
  • fsa_receipt → FSA/HSA transaction or reimbursement records
  • unknown → none of the above clearly apply

GLOBAL RULES:
- Extract values only
- Do not infer missing information
- Use null if not explicitly present
- No extra keys
- No explanations or comments
- Output JSON only (no markdown)

DOCUMENT:
\"\"\"
{raw_text}
\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": "You extract structured healthcare facts."},
                {"role": "user", "content": prompt},
            ],
        )

        content = response.choices[0].message.content or ""
        cleaned = _clean_json(content)

        data = json.loads(cleaned)

        # Guarantee shape
        return {k: data.get(k) for k in FACT_KEYS}

    except Exception as e:
        print(f"[langextract] failed: {e}")
        return _safe_empty_result()
