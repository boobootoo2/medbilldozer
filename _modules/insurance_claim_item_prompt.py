def build_insurance_claim_item_prompt(raw_text: str) -> str:
    return f"""
You are extracting INSURANCE CLAIM HISTORY rows (EOB-style adjudication rows).

Only extract rows from a table section like:
- "Claim Activity"
- "Claim History"

Each extracted row MUST include at least:
- Date of Service
- Provider
- Description
AND at least TWO of these financial fields:
- Allowed
- Insurance Paid
- Copay
- Status

DO NOT extract "Itemized Charges" from provider bills or dental statements.
If you see a section titled "Itemized Charges", return an empty list.

Return ONLY valid JSON in this exact format:

{{
  "insurance_claim_items": [
    {{
      "date_of_service": "YYYY-MM-DD or null",
      "provider": "string",
      "description": "string",
      "allowed": number or null,
      "insurance_paid": number or null,
      "copay": number or null,
      "status": "Paid | Denied | Pending | null"
    }}
  ]
}}

If no insurance claim rows exist, return:
{{ "insurance_claim_items": [] }}

RAW DOCUMENT:
\"\"\"{raw_text}\"\"\"
"""
