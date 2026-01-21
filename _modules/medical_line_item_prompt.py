def build_medical_line_item_prompt(document_text: str) -> str:
    return f"""
You are extracting line items from a medical provider bill or patient statement.

Extract EACH row in the "Itemized Charges" (or similar) section.

Return ONLY valid JSON in the following format:

{{
  "medical_line_items": [
    {{
      "date_of_service": "YYYY-MM-DD | null",
      "description": "string",
      "cpt_code": "string | null",
      "billed": number | null,
      "allowed": number | null,
      "patient_responsibility": number | null,
      "units": number | null
    }}
  ]
}}

RULES:
- Only include actual charge rows (NOT totals / summaries).
- Keep duplicates as separate entries (do NOT merge them).
- CPT/HCPCS codes are 5 digits (e.g., 45378, 00812). If missing, use null.
- Parse money values as numbers (no $).
- Units: if not present, use null (do NOT guess).
- If the document has columns for billed/allowed/patient responsibility, extract them.
- Return JSON only. No markdown, no commentary.

DOCUMENT:
{document_text}
"""
