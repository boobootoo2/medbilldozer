def build_receipt_line_item_prompt(document_text: str) -> str:
    """Build prompt for extracting line items from retail/pharmacy receipts.
    
    Args:
        document_text: Raw receipt text
    
    Returns:
        str: Formatted prompt for LLM extraction
    """
    return f"""
You are extracting line items from a retail or pharmacy receipt.

Extract EACH purchasable item listed on the receipt.

Return ONLY valid JSON in the following format:

{{
  "receipt_items": [
    {{
      "description": "string",
      "amount": number,
      "fsa_eligible": boolean | null,
      "eligibility_reason": string | null
    }}
  ]
}}

RULES:
- Use the item description exactly as written
- Parse dollar amounts as numbers (no $ symbol)
- If FSA eligibility is stated, capture it
- If eligibility is not stated, set fsa_eligible to null
- Do NOT invent CPT or medical codes
- Do NOT include totals as line items
- Ignore headers like "Item", "Amount", "Total"

Each receipt item must correspond to a purchasable product or copay.
Do not extract totals, headings, or explanatory text.


DOCUMENT:
{document_text}
"""
