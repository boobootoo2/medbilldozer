def build_insurance_claim_item_prompt(document_text: str) -> str:
    return f"""
You are extracting claim line items from an insurance claim history or EOB-style table.

Extract EACH row in the "Claim Activity" (or similar) table.

Return ONLY valid JSON in the following format:

{{
  "insurance_claim_items": [
    {{
      "date_of_service": "YYYY-MM-DD | null",
      "provider": "string | null",
      "description": "string",
      "allowed": number | null,
      "insurance_paid": number | null,
      "copay": number | null,
      "status": "string | null"
    }}
  ]
}}

RULES:
- Only include actual claim rows (NOT plan summary).
- Keep duplicates as separate entries (do NOT merge them).
- Parse money values as numbers (no $).
- Status examples: Paid, Denied, Pending. If missing, null.
- Return JSON only. No markdown, no commentary.

DOCUMENT:
{document_text}
"""
