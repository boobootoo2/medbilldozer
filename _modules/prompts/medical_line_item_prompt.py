"""Prompt builder for medical bill line item extraction."""

def build_medical_line_item_prompt(raw_text: str) -> str:
    """Build prompt for extracting line items from medical bills.
    
    Args:
        raw_text: Raw medical bill text
    
    Returns:
        str: Formatted prompt for LLM extraction
    """
    return f"""
You are extracting MEDICAL BILL LINE ITEMS from a provider statement.

ONLY extract rows from sections labeled like:
- Itemized Charges
- Service Description
- CPT
- Billed / Allowed / Patient Responsibility

DO NOT:
- Extract insurance payments
- Extract claim history
- Extract totals or summaries

Each item must represent a single billed service.

Return JSON in this exact format:

{{
  "medical_line_items": [
    {{
      "date_of_service": "YYYY-MM-DD or null",
      "description": "string",
      "cpt_code": "string or null",
      "billed": number or null,
      "allowed": number or null,
      "patient_responsibility": number or null,
      "units": number or null
    }}
  ]
}}

If no medical line items exist, return:

{{
  "medical_line_items": []
}}

RAW DOCUMENT:
\"\"\"
{raw_text}
\"\"\"
"""
