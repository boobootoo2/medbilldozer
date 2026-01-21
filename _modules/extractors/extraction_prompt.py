"""Core fact extraction prompt builder.

Provides provider-agnostic prompts for extracting structured facts from
healthcare documents including bills, receipts, and claim histories.
"""
# _modules/extraction_prompt.py

from typing import List

FACT_KEYS: List[str] = [
    # --- Person / patient ---
    "patient_name",
    "date_of_birth",

    # --- Dates / times ---
    "date_of_service",
    "time_of_service",
    "date_range_start",
    "date_range_end",

    # --- Provider / facility ---
    "provider_name",
    "facility_name",

    # --- Location / contact ---
    "address",
    "phone_number",

    # --- Identifiers ---
    "procedure_code",
    "receipt_number",
    "store_id",

    # --- Classification ---
    "document_type",
]


def build_fact_extraction_prompt(document_text: str) -> str:
    """Build provider-agnostic prompt for structured healthcare fact extraction.
    
    Compatible with OpenAI, Gemini, MedGemma, or local LLMs.
    
    Args:
        document_text: Raw document text
    
    Returns:
        str: Formatted extraction prompt requesting JSON with FACT_KEYS
    """

    return f"""
You are extracting structured facts from healthcare-related documents.

The document may be:
- a medical bill
- a hospital or provider statement
- a pharmacy receipt
- an FSA or HSA receipt
- an FSA or HSA claim history
- an insurance document
- an insurance claim history

Return ONLY a valid JSON object with EXACTLY these keys:
{", ".join(FACT_KEYS)}

-----------------------------------
FIELD EXTRACTION RULES
-----------------------------------

patient_name:
- Only if explicitly labeled (e.g., "Patient Name")
- Do NOT infer from prescriptions or insurance

date_of_birth:
- Only if explicitly present

date_of_service:
- Medical bills: "Date of Service"
- Receipts: transaction or purchase date
- Prefer service/transaction date over statement date

time_of_service:
- Receipt time if explicitly present (e.g., "Time: 3:42 PM")
- Otherwise null

provider_name:
- Medical bills: rendering provider or physician
- Pharmacy receipts:
  - Pharmacy or merchant name
  - Usually the first prominent text block
  - Often repeated

facility_name:
- Hospitals, clinics, or store locations
- May include department or location name
- For pharmacy receipts, may match provider_name

address:
- Full street address if present
- May include city, state, ZIP
- Use a single string, not structured fields

phone_number:
- Phone number if explicitly present
- Any common format is acceptable

procedure_code:
- CPT / HCPCS codes only if explicitly present
- Do NOT invent codes
- Usually null for receipts

receipt_number:
- Receipt, transaction, or order number
- Often labeled "Receipt #", "Transaction #", or similar

store_id:
- Store number or location identifier
- Often labeled "Store #", "Location #", etc.

document_type:
Choose ONE of the following based on the document’s content:

- medical_bill:
  Hospital, clinic, physician, anesthesia, radiology, or outpatient medical services.
  Typically includes CPT or HCPCS codes.

- dental_bill:
  Dental provider statements or bills.
  Often includes:
  • CDT procedure codes (e.g., D2740, D2950)
  • Tooth numbers
  • Treating dentist (DDS/DMD)
  • Lab fees
  • Dental insurance plans

- pharmacy_receipt:
  Retail or pharmacy purchase receipts.
  May include prescription copays and OTC items.

- insurance_document:
  EOBs, claim summaries, adjudication notices.

- fsa_receipt:
  Receipts submitted for FSA/HSA reimbursement.

- unknown:
  If the document does not clearly fit the above categories.

-----------------------------------
FSA / HSA DOCUMENT GUIDANCE
-----------------------------------

If the document is an FSA or HSA account summary or claim history:

- provider_name:
  Use the plan administrator name
  (e.g., "HealthFlex Flexible Spending Account")

- patient_name:
  Use the participant name if labeled
  (e.g., "Participant: Jane Sample")

- date_of_service:
  Use the earliest relevant transaction date
  OR null if multiple dates are present

- receipt_number:
  Usually null (this is not a receipt)

- store_id:
  Null

- address:
  Null unless explicitly shown

- phone_number:
  Use plan administrator contact number if present

- procedure_code:
  Null

IMPORTANT:
- Do NOT treat individual claim rows as receipts
- Do NOT infer merchant addresses or store numbers

DATE HANDLING RULES:

- If the document contains multiple dates of service:
  • Set date_of_service to null
  • Set date_range_start to the earliest date
  • Set date_range_end to the latest date

- If only one relevant date exists:
  • Populate date_of_service
  • Leave date_range_start and date_range_end null


CLASSIFICATION RULES:
- If CDT codes (e.g., Dxxxx) are present → document_type = dental_bill
- If CPT/HCPCS codes are present → document_type = medical_bill
- If retail items + prices + receipt number → pharmacy_receipt
- If the document shows an FSA or HSA account summary, claim history,
  reimbursements, balances, or plan year → document_type = fsa_claim_history
- If the document shows:
• deductible or out-of-pocket maximums
• allowed vs insurance paid vs copay
• claim status (Paid / Denied)
• explanation of benefits language
→ document_type = insurance_claim_history

IMPORTANT CLASSIFICATION PRIORITY (highest wins):

1. If CDT dental codes (Dxxxx) are present → dental_bill
2. Else if CPT or HCPCS codes are present → medical_bill
3. Else if receipt number + prices + merchant → pharmacy_receipt
4. Else if plan year + balances + reimbursements → fsa_claim_history
5. Else if deductible / allowed / paid / copay table → insurance_claim_history
6. Else → unknown

You MUST choose exactly one document_type.



-----------------------------------
RECEIPT-SPECIFIC GUIDANCE
-----------------------------------

If the document appears to be a receipt:
- Identify the merchant or pharmacy name
- Extract receipt number, store ID, date, and time
- Address and phone number often appear near the top
- Line items are extracted in a separate step after document classification.

-----------------------------------
OUTPUT RULES
-----------------------------------

- Extract VALUES only (no labels)
- Do NOT infer missing information
- Use null for missing values
- Do NOT include extra keys
- Do NOT include explanations, markdown, or commentary

-----------------------------------
DOCUMENT:
-----------------------------------
{document_text}
"""
