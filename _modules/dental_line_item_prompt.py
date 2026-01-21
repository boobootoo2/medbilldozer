def build_dental_line_item_prompt(document_text: str) -> str:
    return f"""
You are extracting line items from a dental patient statement.

Extract EACH row in the "Itemized Charges" section.

Return ONLY valid JSON in the following format:

{{
  "dental_line_items": [
    {{
      "date_of_service": "YYYY-MM-DD | null",
      "description": "string",
      "cdt_code": "string | null",
      "billed": number | null,
      "allowed": number | null,
      "patient_responsibility": number | null,
      "tooth_number": "string | null"
    }}
  ]
}}

RULES:
- Only include actual charge rows (NOT totals / summaries).
- Keep duplicates as separate entries (do NOT merge them).
- CDT codes look like D#### (e.g., D2740, D2950). If missing, use null.
- Parse money values as numbers (no $).
- Tooth number: extract if present anywhere (e.g., "#14") else null.
- Return JSON only. No markdown, no commentary.

DOCUMENT:
{document_text}
"""
