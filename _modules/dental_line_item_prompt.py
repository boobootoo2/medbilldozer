def build_dental_line_item_prompt(raw_text: str) -> str:
    return f"""
You are extracting DENTAL BILL LINE ITEMS.

Rules:
- Only extract from Itemized Charges tables
- CDT codes may include suffixes like "-L" (e.g., D2740-L)
- Do not infer coverage or benefits
- Do not combine rows

Return JSON:

{{
  "dental_line_items": [
    {{
      "date_of_service": "YYYY-MM-DD or null",
      "description": "string",
      "cdt_code": "string",
      "billed": number,
      "allowed": number or null,
      "patient_responsibility": number or null,
      "tooth_number": "string or null"
    }}
  ]
}}

RAW DOCUMENT:
\"\"\"
{raw_text}
\"\"\"
"""
