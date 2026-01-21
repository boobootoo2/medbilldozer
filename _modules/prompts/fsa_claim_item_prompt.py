"""Prompt builder for FSA/HSA claim history extraction."""

def build_fsa_claim_item_prompt(document_text: str) -> str:
    """Build prompt for extracting claim rows from FSA/HSA claim history.
    
    Args:
        document_text: Raw FSA/HSA claim history text
    
    Returns:
        str: Formatted prompt for LLM extraction
    """
    return f"""
You are extracting claim rows from an FSA/HSA claim history.

Extract EACH row in the "Recent Claims" (or similar) table.

Return ONLY valid JSON in the following format:

{{
  "fsa_claim_items": [
    {{
      "date_submitted": "YYYY-MM-DD | null",
      "merchant": "string | null",
      "description": "string",
      "amount_submitted": number | null,
      "amount_reimbursed": number | null,
      "status": "string | null"
    }}
  ]
}}

RULES:
- Only include actual claim rows (NOT account summary).
- Keep duplicates as separate entries (do NOT merge them).
- Parse money values as numbers (no $).
- Status examples: Approved, Denied, Pending. If missing, null.
- Return JSON only. No markdown, no commentary.

Each row must represent a reimbursement decision, not a purchase.


DOCUMENT:
{document_text}
"""
