"""Production workflow with profile-based preloaded documents.

Provides a production-style interface where documents are preloaded based on
the selected health profile (policy holder or dependent), with status tracking
and parallel analysis capabilities.
"""
import streamlit as st
from typing import Dict, List, Optional, TypedDict
from datetime import datetime
import time
import copy
from medbilldozer.utils.sanitize import (
    sanitize_text,
    sanitize_html_content,
    sanitize_provider_name,
    sanitize_filename,
    sanitize_amount,
    sanitize_date
)


class ProfileDocument(TypedDict):
    """Document associated with a health profile."""
    doc_id: str
    profile_id: str
    profile_name: str
    doc_type: str  # medical_bill, insurance_eob, pharmacy_receipt, dental_bill
    provider: str
    service_date: str
    amount: float
    flagged: bool  # True if requires review
    status: str  # pending, analyzing, completed, error
    content: str  # Full document text
    action: Optional[str]  # None, ignored, followup, resolved
    action_notes: str  # Notes for the action
    action_date: Optional[str]  # When action was taken


# ==============================================================================
# SAMPLE DATA
# ==============================================================================

# Sample imported line items (for demo when no actual imports exist)
SAMPLE_IMPORTED_LINE_ITEMS = [
    {
        'line_item_id': 'item_demo_001',
        'import_job_id': 'job_demo_001',
        'service_date': '2026-01-15',
        'procedure_code': '99213',
        'procedure_description': 'Office Visit - Established Patient',
        'provider_name': 'Dr. Sarah Mitchell',
        'provider_npi': '1234567890',
        'billed_amount': 200.00,
        'allowed_amount': 150.00,
        'paid_by_insurance': 120.00,
        'patient_responsibility': 30.00,
        'claim_number': 'CLM-2026-001',
        'created_at': '2026-01-20T10:00:00Z'
    },
    {
        'line_item_id': 'item_demo_002',
        'import_job_id': 'job_demo_001',
        'service_date': '2026-01-18',
        'procedure_code': '80053',
        'procedure_description': 'Comprehensive Metabolic Panel',
        'provider_name': 'Quest Diagnostics',
        'provider_npi': '9876543210',
        'billed_amount': 180.00,
        'allowed_amount': 120.00,
        'paid_by_insurance': 96.00,
        'patient_responsibility': 24.00,
        'claim_number': 'CLM-2026-002',
        'created_at': '2026-01-20T10:00:00Z'
    },
    {
        'line_item_id': 'item_demo_003',
        'import_job_id': 'job_demo_002',
        'service_date': '2026-01-22',
        'procedure_code': 'D0120',
        'procedure_description': 'Periodic Oral Evaluation',
        'provider_name': 'Bright Smiles Dental',
        'provider_npi': '5555555555',
        'billed_amount': 85.00,
        'allowed_amount': 70.00,
        'paid_by_insurance': 56.00,
        'patient_responsibility': 14.00,
        'claim_number': 'CLM-2026-003',
        'created_at': '2026-01-23T14:30:00Z'
    }
]

# Sample insurance plan document (for demo)
SAMPLE_INSURANCE_PLAN_DOCUMENT = {
    'plan_id': 'PLAN-DEMO-001',
    'plan_name': 'Horizon PPO Plus',
    'carrier': 'Horizon Blue Cross Blue Shield',
    'member_id': 'HPP-8743920',
    'group_number': 'GRP-55512',
    'effective_date': '2026-01-01',
    'plan_year': '2026',
    'network_type': 'PPO',
    
    # Coverage details
    'deductible_individual': 1500.00,
    'deductible_family': 3000.00,
    'deductible_met_individual': 450.00,
    'deductible_met_family': 450.00,
    
    'out_of_pocket_max_individual': 5000.00,
    'out_of_pocket_max_family': 10000.00,
    'out_of_pocket_met_individual': 1250.00,
    'out_of_pocket_met_family': 1250.00,
    
    # Copays and coinsurance
    'copay_primary_care': 30.00,
    'copay_specialist': 60.00,
    'copay_urgent_care': 75.00,
    'copay_emergency_room': 250.00,
    'copay_generic_rx': 10.00,
    'copay_brand_rx': 35.00,
    
    'coinsurance_in_network': 0.20,  # 20% after deductible
    'coinsurance_out_of_network': 0.40,  # 40% after deductible
    
    # Eligible expenses with in/out-of-network prices
    'eligible_services': [
        {
            'procedure_code': '99213',
            'description': 'Office Visit - Established Patient (15-29 min)',
            'in_network_allowed': 150.00,
            'out_of_network_allowed': 120.00,
            'typical_billed': 200.00,
            'subject_to_deductible': True,
            'copay_applies': True
        },
        {
            'procedure_code': '99214',
            'description': 'Office Visit - Established Patient (30-39 min)',
            'in_network_allowed': 220.00,
            'out_of_network_allowed': 176.00,
            'typical_billed': 280.00,
            'subject_to_deductible': True,
            'copay_applies': True
        },
        {
            'procedure_code': '80053',
            'description': 'Comprehensive Metabolic Panel',
            'in_network_allowed': 120.00,
            'out_of_network_allowed': 96.00,
            'typical_billed': 180.00,
            'subject_to_deductible': True,
            'copay_applies': False
        },
        {
            'procedure_code': '45378',
            'description': 'Colonoscopy, Diagnostic',
            'in_network_allowed': 1400.00,
            'out_of_network_allowed': 1120.00,
            'typical_billed': 2500.00,
            'subject_to_deductible': True,
            'copay_applies': False
        },
        {
            'procedure_code': '70553',
            'description': 'MRI Brain without and with contrast',
            'in_network_allowed': 2200.00,
            'out_of_network_allowed': 1760.00,
            'typical_billed': 3500.00,
            'subject_to_deductible': True,
            'copay_applies': False
        },
        {
            'procedure_code': 'D0120',
            'description': 'Periodic Oral Evaluation',
            'in_network_allowed': 70.00,
            'out_of_network_allowed': 56.00,
            'typical_billed': 85.00,
            'subject_to_deductible': False,
            'copay_applies': True
        },
        {
            'procedure_code': 'D0220',
            'description': 'Intraoral Periapical X-ray - First Film',
            'in_network_allowed': 35.00,
            'out_of_network_allowed': 28.00,
            'typical_billed': 50.00,
            'subject_to_deductible': False,
            'copay_applies': True
        }
    ]
}

# Sample preloaded documents
PRELOADED_DOCUMENTS: List[ProfileDocument] = [
    # Policy Holder Documents
    {
        'doc_id': 'DOC-PH-001',
        'profile_id': 'PH-001',
        'profile_name': 'John Sample',
        'doc_type': 'medical_bill',
        'provider': 'Valley Medical Center',
        'service_date': '2026-01-12',
        'amount': 1200.00,
        'flagged': True,
        'status': 'pending',
        'action': None,
        'action_notes': '',
        'action_date': None,
        'content': '''VALLEY MEDICAL CENTER - STATEMENT

Patient: John Sample | Member ID: HPP-8743920
Date of Service: January 12, 2026

CPT 45378 - Colonoscopy, Diagnostic
Physician: Dr. Michael Reynolds

TOTAL BILLED:           $2,500.00
Insurance Adjustment:   -$1,100.00
Insurance Payment:        $200.00
PATIENT OWES:          $1,200.00

⚠️ ISSUE: Patient responsibility ($1,200) exceeds typical 
insurance allowed amount for in-network colonoscopy'''
    },
    {
        'doc_id': 'DOC-PH-002',
        'profile_id': 'PH-001',
        'profile_name': 'John Sample',
        'doc_type': 'pharmacy_receipt',
        'provider': 'GreenLeaf Pharmacy',
        'service_date': '2026-01-20',
        'amount': 125.00,
        'flagged': True,
        'status': 'pending',
        'action': None,
        'action_notes': '',
        'action_date': None,
        'content': '''GreenLeaf Pharmacy - RECEIPT

Patient: John Sample | Rx: RX-9876543
Date: January 20, 2026

Metformin 500mg - 90 tablets
Prescriber: Dr. Sarah Mitchell

TOTAL:     $125.00
PAID:      Cash

⚠️ ISSUE: Out-of-network pharmacy. Insurance copay 
would be $15 at in-network CVS. Extra cost: $110'''
    },
    {
        'doc_id': 'DOC-PH-003',
        'profile_id': 'PH-001',
        'profile_name': 'John Sample',
        'doc_type': 'insurance_eob',
        'provider': 'Horizon PPO Plus',
        'service_date': '2025-11-05',
        'amount': 0.00,
        'flagged': False,
        'status': 'pending',
        'action': None,
        'action_notes': '',
        'action_date': None,
        'content': '''HORIZON PPO PLUS - EOB

Member: John Sample | Member ID: HPP-8743920
Claim: CLM-2025-789456 | Date: Nov 5, 2025
Provider: Dr. Sarah Mitchell

CPT 99396 - Annual Physical Exam

Provider Charges:    $350.00
Plan Discount:      -$100.00
Allowed Amount:      $250.00
Insurance Paid:      $200.00
You Owe:              $50.00

✓ Preventive care - no deductible applied'''
    },
    
    # Dependent Documents
    {
        'doc_id': 'DOC-DEP-001',
        'profile_id': 'DEP-001',
        'profile_name': 'Emma Sample',
        'doc_type': 'dental_bill',
        'provider': 'BrightSmile Dental',
        'service_date': '2026-01-18',
        'amount': 850.00,
        'flagged': True,
        'status': 'pending',
        'action': None,
        'action_notes': '',
        'action_date': None,
        'content': '''BRIGHTSMILE DENTAL - STATEMENT

Patient: Emma Sample | Guardian: John Sample
Member ID: HPP-8743920-01 | Date: Jan 18, 2026

D2740 - Porcelain Crown (Tooth #14)
D0274 - X-Rays

Crown:           $1,250.00
Lab Fee:           $350.00
X-Rays:             $85.00
TOTAL:          $1,685.00

Insurance Est:    -$835.00
You Owe:           $850.00

⚠️ ISSUE: Lab fee ($350) not separately itemized 
in insurance estimate. May not be covered'''
    },
    {
        'doc_id': 'DOC-DEP-002',
        'profile_id': 'DEP-001',
        'profile_name': 'Emma Sample',
        'doc_type': 'pharmacy_receipt',
        'provider': 'CVS Pharmacy',
        'service_date': '2026-01-22',
        'amount': 15.00,
        'flagged': False,
        'status': 'pending',
        'action': None,
        'action_notes': '',
        'action_date': None,
        'content': '''CVS PHARMACY - RECEIPT

Patient: Emma Sample | Rx: 123456789
Date: January 22, 2026

Amoxicillin 500mg - 21 capsules (7 days)
Prescriber: Dr. Jennifer Park

Retail Price:    $62.00
Insurance:       -$47.00
Copay:            $15.00

✓ In-network. Properly processed'''
    },
    {
        'doc_id': 'DOC-DEP-003',
        'profile_id': 'DEP-001',
        'profile_name': 'Emma Sample',
        'doc_type': 'medical_bill',
        'provider': 'HealthFirst Medical Group',
        'service_date': '2026-01-15',
        'amount': 45.00,
        'flagged': False,
        'status': 'pending',
        'action': None,
        'action_notes': '',
        'action_date': None,
        'content': '''HEALTHFIRST MEDICAL GROUP - STATEMENT

Patient: Emma Sample | Acct: 987654321
Date: January 15, 2026
Provider: Dr. Jennifer Park, MD

CPT 99213 - Office Visit, Level 3
Diagnosis: Upper Respiratory Infection

Office Visit:        $145.00
Insurance Adj:        -$20.00
Insurance Paid:      -$100.00
Copay:                -$25.00
Balance Due:          $45.00

✓ Standard copay and coinsurance applied'''
    }
]


def get_documents_for_profile(profile_id: str) -> List[ProfileDocument]:
    """Get all documents for a specific profile from session state.
    
    Args:
        profile_id: Profile ID (e.g., 'PH-001', 'DEP-001')
        
    Returns:
        List of documents for the profile
    """
    docs = get_session_documents()
    return [doc for doc in docs if doc['profile_id'] == profile_id]


def get_flagged_documents(profile_id: Optional[str] = None) -> List[ProfileDocument]:
    """Get all flagged documents, optionally filtered by profile.
    
    Args:
        profile_id: Optional profile ID to filter by
        
    Returns:
        List of flagged documents
    """
    docs = get_session_documents() if profile_id is None else get_documents_for_profile(profile_id)
    return [doc for doc in docs if doc['flagged']]


def get_pending_documents(profile_id: Optional[str] = None) -> List[ProfileDocument]:
    """Get all pending documents (not yet analyzed).
    
    Args:
        profile_id: Optional profile ID to filter by
        
    Returns:
        List of pending documents
    """
    docs = get_session_documents() if profile_id is None else get_documents_for_profile(profile_id)
    return [doc for doc in docs if doc['status'] == 'pending']


def get_actioned_documents(profile_id: Optional[str] = None) -> List[ProfileDocument]:
    """Get all documents with actions (ignored, followup, resolved).
    
    Args:
        profile_id: Optional profile ID to filter by
        
    Returns:
        List of actioned documents
    """
    docs = get_session_documents() if profile_id is None else get_documents_for_profile(profile_id)
    return [doc for doc in docs if doc.get('action') is not None]


def export_actioned_items_csv(docs: List[ProfileDocument]) -> str:
    """Generate CSV content for actioned items.
    
    Args:
        docs: List of actioned documents
        
    Returns:
        CSV formatted string
    """
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Document ID',
        'Profile',
        'Provider',
        'Service Date',
        'Amount',
        'Action',
        'Action Date',
        'Notes',
        'Flagged'
    ])
    
    # Data rows
    for doc in docs:
        writer.writerow([
            doc['doc_id'],
            doc['profile_name'],
            doc['provider'],
            doc['service_date'],
            f"${doc['amount']:.2f}",
            doc.get('action', '').title(),
            doc.get('action_date', 'N/A'),
            doc.get('action_notes', ''),
            'Yes' if doc['flagged'] else 'No'
        ])
    
    return output.getvalue()


def load_receipts_as_documents() -> List[ProfileDocument]:
    """Load receipts from profile editor and convert to ProfileDocument format.
    
    Integrates receipts uploaded via the profile editor into the production workflow.
    Receipts are converted to ProfileDocument format and assigned to the active profile.
    """
    try:
        from medbilldozer.ui.profile_editor import load_receipts
        receipts = load_receipts()
        
        # Get the active profile ID from session state (default to PH-001)
        active_profile = st.session_state.get('selected_profile_id', 'PH-001')
        active_profile_name = st.session_state.get('selected_profile_name', 'John Sample')
        
        # Convert receipts to ProfileDocument format
        receipt_docs: List[ProfileDocument] = []
        for receipt in receipts:
            # Generate a unique document ID from receipt ID
            doc_id = f"DOC-RCPT-{receipt['receipt_id'].replace('rcpt_', '').upper()}"
            
            # Determine document type from file name or default to pharmacy receipt
            doc_type = 'pharmacy_receipt'
            if 'dental' in receipt.get('file_name', '').lower():
                doc_type = 'dental_bill'
            elif 'medical' in receipt.get('file_name', '').lower() or 'hospital' in receipt.get('file_name', '').lower():
                doc_type = 'medical_bill'
            
            # Build receipt document with safe value handling and sanitization
            # Handle None/missing values safely and sanitize all user input
            provider = sanitize_provider_name(receipt.get('provider') or 'Unknown Provider')
            file_name = sanitize_filename(receipt.get('file_name') or 'Unknown')
            source_method = sanitize_text(receipt.get('source_method') or 'unknown')
            date_value = sanitize_date(receipt.get('date') or datetime.now().strftime('%Y-%m-%d'))
            amount_value = sanitize_amount(receipt.get('amount') if receipt.get('amount') is not None else 0.0)
            notes_value = sanitize_text(receipt.get('notes') or 'No notes')
            raw_content = sanitize_html_content(receipt.get('raw_content') or '', max_length=500)
            
            receipt_doc: ProfileDocument = {
                'doc_id': doc_id,
                'profile_id': active_profile,
                'profile_name': active_profile_name,
                'doc_type': doc_type,
                'provider': provider,
                'service_date': date_value,
                'amount': float(amount_value),
                'flagged': receipt.get('status') == 'pending_review',  # Flag if needs review
                'status': 'completed' if receipt.get('status') == 'reconciled' else 'pending',
                'content': f"""RECEIPT - {file_name}

Source: {source_method}
Provider: {provider}
Amount: ${float(amount_value):.2f}
Date: {date_value}

Notes: {notes_value}

--- RAW CONTENT ---
{raw_content}...""",
                'action': None,
                'action_notes': '',
                'action_date': None,
            }
            receipt_docs.append(receipt_doc)
        
        return receipt_docs
    except ImportError:
        # Profile editor not available
        return []
    except Exception as e:
        # Error loading receipts, return empty list
        st.warning(f"Could not load receipts: {e}")
        return []


def load_imported_line_items_as_documents() -> List[ProfileDocument]:
    """Load imported line items from Profile Editor and convert to ProfileDocument format.
    
    Integrates imported data from insurance EOBs and provider bills into the production workflow.
    Each line item becomes a separate document for analysis.
    If no actual imports exist, uses sample data for demonstration.
    """
    try:
        from medbilldozer.ui.profile_editor import load_line_items
        line_items = load_line_items()
        
        # If no actual imports, use sample data for demo
        if not line_items:
            line_items = SAMPLE_IMPORTED_LINE_ITEMS
        
        # Get the active profile ID from session state (default to PH-001)
        active_profile = st.session_state.get('selected_profile_id', 'PH-001')
        active_profile_name = st.session_state.get('selected_profile_name', 'John Sample')
        
        # Convert line items to ProfileDocument format
        import_docs: List[ProfileDocument] = []
        for item in line_items:
            # Generate a unique document ID from line item ID
            doc_id = f"DOC-IMPORT-{item.get('line_item_id', 'UNKNOWN').replace('item_', '').upper()}"
            
            # Determine document type based on procedure code
            doc_type = 'medical_bill'
            procedure_code = item.get('procedure_code', '')
            if procedure_code.startswith('D'):  # Dental codes start with D
                doc_type = 'dental_bill'
            elif 'RX' in procedure_code or 'pharmacy' in item.get('procedure_description', '').lower():
                doc_type = 'pharmacy_receipt'
            
            # Handle None/missing values safely with sanitization
            provider_name = sanitize_provider_name(item.get('provider_name') or 'Unknown Provider')
            service_date = sanitize_date(item.get('service_date') or datetime.now().strftime('%Y-%m-%d'))
            procedure_code = sanitize_text(item.get('procedure_code') or 'N/A')
            procedure_desc = sanitize_text(item.get('procedure_description') or 'No description')
            billed_amount = sanitize_amount(item.get('billed_amount') if item.get('billed_amount') is not None else 0.0)
            allowed_amount = sanitize_amount(item.get('allowed_amount') if item.get('allowed_amount') is not None else 0.0)
            paid_by_insurance = sanitize_amount(item.get('paid_by_insurance') if item.get('paid_by_insurance') is not None else 0.0)
            patient_responsibility = sanitize_amount(item.get('patient_responsibility') if item.get('patient_responsibility') is not None else 0.0)
            claim_number = sanitize_text(item.get('claim_number') or 'N/A')
            provider_npi = sanitize_text(item.get('provider_npi') or 'N/A')
            
            # Flag if patient responsibility seems high or mismatched
            flagged = False
            if patient_responsibility > 0:
                # Flag if patient responsibility exceeds typical copay threshold
                if patient_responsibility > 500:
                    flagged = True
                # Flag if patient responsibility is higher than what insurance paid
                elif paid_by_insurance > 0 and patient_responsibility > paid_by_insurance:
                    flagged = True
            
            # Build imported line item document
            import_doc: ProfileDocument = {
                'doc_id': doc_id,
                'profile_id': active_profile,
                'profile_name': active_profile_name,
                'doc_type': doc_type,
                'provider': provider_name,
                'service_date': service_date,
                'amount': float(patient_responsibility),  # Patient owes amount
                'flagged': flagged,
                'status': 'pending',
                'content': f"""IMPORTED LINE ITEM - {procedure_code}

Service Date: {service_date}
Provider: {provider_name}
NPI: {provider_npi}
Claim #: {claim_number}

Procedure: {procedure_code}
Description: {procedure_desc}

AMOUNTS:
Billed Amount:           ${float(billed_amount):.2f}
Allowed Amount:          ${float(allowed_amount):.2f}
Paid by Insurance:       ${float(paid_by_insurance):.2f}
Patient Responsibility:  ${float(patient_responsibility):.2f}

{('⚠️ FLAGGED: High patient responsibility' if flagged else '✓ Standard charges')}

Import Job ID: {item.get('import_job_id', 'N/A')}
Line Item ID: {item.get('line_item_id', 'N/A')}""",
                'action': None,
                'action_notes': '',
                'action_date': None,
            }
            import_docs.append(import_doc)
        
        return import_docs
    except ImportError:
        # Profile editor not available
        return []
    except Exception as e:
        # Error loading imports, return empty list
        st.warning(f"Could not load imported items: {e}")
        return []


def load_insurance_plan_as_document() -> Optional[ProfileDocument]:
    """Load insurance plan document showing eligible expenses and network pricing.
    
    Creates a comprehensive plan document that displays coverage details,
    copays, deductibles, and in/out-of-network allowed amounts for procedures.
    """
    try:
        # Get the active profile ID from session state (default to PH-001)
        active_profile = st.session_state.get('selected_profile_id', 'PH-001')
        active_profile_name = st.session_state.get('selected_profile_name', 'John Sample')
        
        plan = SAMPLE_INSURANCE_PLAN_DOCUMENT
        
        # Build eligible services table
        services_table = []
        for svc in plan['eligible_services']:
            services_table.append(
                f"  {svc['procedure_code']:8} | {svc['description']:45} | "
                f"In: ${svc['in_network_allowed']:7.2f} | Out: ${svc['out_of_network_allowed']:7.2f} | "
                f"Typical: ${svc['typical_billed']:7.2f}"
            )
        
        plan_doc: ProfileDocument = {
            'doc_id': 'DOC-PLAN-001',
            'profile_id': active_profile,
            'profile_name': active_profile_name,
            'doc_type': 'insurance_eob',
            'provider': plan['carrier'],
            'service_date': plan['effective_date'],
            'amount': 0.0,  # Plan document, no amount owed
            'flagged': False,
            'status': 'completed',  # Reference document, already processed
            'content': f"""INSURANCE PLAN DOCUMENT - {plan['plan_name']}

Carrier: {plan['carrier']}
Plan Type: {plan['network_type']}
Member ID: {plan['member_id']}
Group Number: {plan['group_number']}
Plan Year: {plan['plan_year']}
Effective Date: {plan['effective_date']}

DEDUCTIBLE:
Individual: ${plan['deductible_individual']:.2f} (Met: ${plan['deductible_met_individual']:.2f})
Family:     ${plan['deductible_family']:.2f} (Met: ${plan['deductible_met_family']:.2f})

OUT-OF-POCKET MAXIMUM:
Individual: ${plan['out_of_pocket_max_individual']:.2f} (Met: ${plan['out_of_pocket_met_individual']:.2f})
Family:     ${plan['out_of_pocket_max_family']:.2f} (Met: ${plan['out_of_pocket_met_family']:.2f})

COPAYS:
Primary Care:   ${plan['copay_primary_care']:.2f}
Specialist:     ${plan['copay_specialist']:.2f}
Urgent Care:    ${plan['copay_urgent_care']:.2f}
Emergency Room: ${plan['copay_emergency_room']:.2f}
Generic Rx:     ${plan['copay_generic_rx']:.2f}
Brand Rx:       ${plan['copay_brand_rx']:.2f}

COINSURANCE:
In-Network:     {plan['coinsurance_in_network'] * 100:.0f}% (after deductible)
Out-of-Network: {plan['coinsurance_out_of_network'] * 100:.0f}% (after deductible)

ELIGIBLE EXPENSES - APPROVED PRICES:
(Shows in-network vs out-of-network allowed amounts)

  Code     | Description                                   | In-Network  | Out-Network | Typical Bill
  ---------|-----------------------------------------------|-------------|-------------|-------------
{chr(10).join(services_table)}

NOTE: Charges above allowed amounts are not eligible for reimbursement.
Out-of-network providers may balance bill the difference.""",
            'action': None,
            'action_notes': '',
            'action_date': None,
        }
        
        return plan_doc
        
    except Exception as e:
        # Error creating plan document
        st.warning(f"Could not load insurance plan: {e}")
        return None


def initialize_prod_workflow_state():
    """Initialize session state for production workflow documents.
    
    Combines preloaded sample documents, receipts, imported line items, 
    and insurance plan document from the profile editor.
    """
    if 'prod_workflow_documents' not in st.session_state:
        # Deep copy the preloaded documents to session state
        all_docs = copy.deepcopy(PRELOADED_DOCUMENTS)
        
        # Add insurance plan document (reference)
        plan_doc = load_insurance_plan_as_document()
        if plan_doc:
            all_docs.append(plan_doc)
        
        # Add receipts from profile editor
        receipt_docs = load_receipts_as_documents()
        all_docs.extend(receipt_docs)
        
        # Add imported line items from profile editor
        import_docs = load_imported_line_items_as_documents()
        all_docs.extend(import_docs)
        
        st.session_state.prod_workflow_documents = all_docs


def get_session_documents() -> List[ProfileDocument]:
    """Get documents from session state, initializing if needed."""
    initialize_prod_workflow_state()
    return st.session_state.prod_workflow_documents


def update_session_document(doc_id: str, updates: Dict):
    """Update a specific document in session state.
    
    Args:
        doc_id: Document ID to update
        updates: Dictionary of fields to update
    """
    docs = get_session_documents()
    for doc in docs:
        if doc['doc_id'] == doc_id:
            doc.update(updates)
            break


def reload_receipts_into_session():
    """Reload receipts and imported items from profile editor into session state.
    
    This function checks for new receipts and imported line items, adding them 
    to the session documents if they don't already exist (based on document ID).
    """
    receipt_docs = load_receipts_as_documents()
    import_docs = load_imported_line_items_as_documents()
    
    if 'prod_workflow_documents' not in st.session_state:
        initialize_prod_workflow_state()
    
    existing_docs = st.session_state.prod_workflow_documents
    existing_ids = {doc['doc_id'] for doc in existing_docs}
    
    # Combine receipts and imports
    all_new_docs = receipt_docs + import_docs
    
    # Add only new documents (receipts or imports)
    new_docs = [doc for doc in all_new_docs if doc['doc_id'] not in existing_ids]
    
    if new_docs:
        st.session_state.prod_workflow_documents.extend(new_docs)
        return len(new_docs)
    return 0


def render_prod_workflow():
    """Render production workflow interface with preloaded documents."""
    # Initialize session state on first load
    initialize_prod_workflow_state()
    
    st.header("📊 Production Workflow")
    
    st.info("""
    **Production Mode**: Documents are automatically loaded based on health profiles.
    Flagged documents require review. Click **Analyze** to process all pending documents in parallel.
    """)
    
    # Profile selector
    from medbilldozer.ui.health_profile import SAMPLE_PROFILES
    
    st.subheader("👤 Select Profile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        profile_options = {
            'PH-001': f"👨 {SAMPLE_PROFILES['policyholder']['name']} (Policy Holder)",
            'DEP-001': f"👧 {SAMPLE_PROFILES['dependent']['name']} (Dependent)"
        }
        
        selected_profile_id = st.radio(
            "Health Profile",
            options=list(profile_options.keys()),
            format_func=lambda x: profile_options[x],
            key='prod_profile_selector'
        )
        
        # Store selected profile in session state for receipt integration
        st.session_state.selected_profile_id = selected_profile_id
        if selected_profile_id == 'PH-001':
            st.session_state.selected_profile_name = SAMPLE_PROFILES['policyholder']['name']
        else:
            st.session_state.selected_profile_name = SAMPLE_PROFILES['dependent']['name']
    
    with col2:
        # Profile summary
        profile_data = SAMPLE_PROFILES['policyholder'] if selected_profile_id == 'PH-001' else SAMPLE_PROFILES['dependent']
        
        with st.container(border=True):
            st.write(f"**Name:** {profile_data['name']}")
            st.write(f"**DOB:** {profile_data['date_of_birth']}")
            st.write(f"**Insurance:** {profile_data['insurance']['provider']}")
            st.write(f"**Member ID:** {profile_data['insurance']['member_id']}")
    
    st.markdown("---")
    
    # Get documents for selected profile
    profile_docs = get_documents_for_profile(selected_profile_id)
    flagged_docs = [d for d in profile_docs if d['flagged']]
    pending_docs = [d for d in profile_docs if d['status'] == 'pending']
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Documents", len(profile_docs))
    
    with col2:
        st.metric("Flagged", len(flagged_docs), delta=f"🚩 {len(flagged_docs)}")
    
    with col3:
        st.metric("Pending Analysis", len(pending_docs))
    
    with col4:
        total_amount = sum(d['amount'] for d in flagged_docs)
        st.metric("Flagged Amount", f"${total_amount:,.2f}")
    
    st.markdown("---")
    
    # Document table
    st.subheader("📋 Documents")
    
    # Reset button for demo/testing
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Reload receipts and imported items from Profile Editor, or reset all documents")
        with col2:
            if st.button("📥 Reload Data", use_container_width=True):
                new_count = reload_receipts_into_session()
                if new_count > 0:
                    st.success(f"Added {new_count} new document(s)!")
                    st.rerun()
                else:
                    st.info("No new documents to add")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("")
        with col2:
            if st.button("🔄 Reset All", use_container_width=True):
                if 'prod_workflow_documents' in st.session_state:
                    del st.session_state.prod_workflow_documents
                st.success("Documents reset!")
                st.rerun()
    
    # Analyze button - works for pending, completed, and documents with no status
    # Get all unflagged docs (pending OR completed OR no status)
    analyzable_docs = [d for d in profile_docs if not d['flagged'] and d.get('status') in ['pending', 'completed', None, '']]
    pending_unflagged_docs = [d for d in profile_docs if not d['flagged'] and d.get('status') in ['pending', None, '']]
    completed_unflagged_docs = [d for d in profile_docs if not d['flagged'] and d.get('status') == 'completed']
    flagged_count = len([d for d in profile_docs if d['flagged']])
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if analyzable_docs:
            # Has documents to analyze - ENABLED button (pending or completed)
            button_text = "🔍 Analyze Documents"
            if pending_unflagged_docs and completed_unflagged_docs:
                button_text = f"🔍 Analyze {len(pending_unflagged_docs)} + Re-analyze {len(completed_unflagged_docs)} Document(s)"
            elif pending_unflagged_docs:
                button_text = f"🔍 Analyze {len(pending_unflagged_docs)} Document(s)"
            elif completed_unflagged_docs:
                button_text = f"🔍 Re-analyze {len(completed_unflagged_docs)} Document(s)"
            
            analyze_clicked = st.button(
                button_text,
                type="primary",
                use_container_width=True,
                disabled=False,
                help=f"Analyze {len(analyzable_docs)} unflagged documents" + (f" ({flagged_count} flagged docs excluded)" if flagged_count > 0 else "")
            )
        else:
            # Only flagged documents or no documents
            analyze_clicked = False
            if flagged_count > 0:
                st.button(
                    "🔍 Analyze Documents",
                    type="secondary",
                    use_container_width=True,
                    disabled=True,
                    help=f"{flagged_count} flagged document(s) require manual review before analysis"
                )
            else:
                st.button(
                    "🔍 Analyze Documents",
                    type="secondary",
                    use_container_width=True,
                    disabled=True,
                    help="No documents available to analyze"
                )
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Status message
    if analyzable_docs:
        if completed_unflagged_docs and not pending_unflagged_docs:
            st.info(f"ℹ️ {len(completed_unflagged_docs)} document(s) completed. Click Analyze to re-run.")
    elif flagged_count > 0:
        st.info(f"ℹ️ {flagged_count} flagged document(s) require manual review before analysis.")
    else:
        st.info("ℹ️ No documents available to analyze.")
    
    st.markdown("---")
    
    # Follow-up Tasks Table
    followup_docs = [d for d in profile_docs if d.get('action') == 'followup']
    actioned_docs = [d for d in profile_docs if d.get('action') is not None]
    
    if followup_docs:
        st.subheader("Follow-up Tasks ")
        
        # Action summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Follow-up Tasks", len(followup_docs))
        
        with col2:
            ignored_count = len([d for d in actioned_docs if d.get('action') == 'ignored'])
            st.metric("Ignored", ignored_count)
        
        with col3:
            total_actions = len(actioned_docs)
            st.metric("Total Actions", total_actions)
        
        with col4:
            resolved_count = len([d for d in actioned_docs if d.get('action') == 'resolved'])
            st.metric("Resolved", resolved_count)
        
        # Export/Share buttons
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Display follow-up tasks table only
            table_data = []
            for doc in followup_docs:
                table_data.append({
                    'Doc ID': doc['doc_id'],
                    'Provider': doc['provider'],
                    'Amount': f"${doc['amount']:,.2f}",
                    'Action Date': doc.get('action_date', 'N/A'),
                    'Notes': doc.get('action_notes', '')[:50] + ('...' if len(doc.get('action_notes', '')) > 50 else '')
                })
            
            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            # Download button - still exports all actioned items
            csv_data = export_actioned_items_csv(followup_docs)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"followup_tasks_{selected_profile_id}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Share button (copy to clipboard simulation)
            if st.button("📋 Copy Table", use_container_width=True):
                st.info("📋 Table data copied! (In production, this would copy to clipboard)")
        
        st.markdown("---")
    
    # Document list
    st.subheader("📄 All Documents")
    
    for doc in profile_docs:
        doc_icon = {
            'medical_bill': '🏥',
            'insurance_eob': '📋',
            'pharmacy_receipt': '💊',
            'dental_bill': '🦷'
        }.get(doc['doc_type'], '📄')
        
        status_icon = {
            'pending': '⏳',
            'analyzing': '🔄',
            'completed': '✅',
            'error': '❌'
        }.get(doc['status'], '⚪')
        
        flag_badge = " 🚩" if doc['flagged'] else ""
        
        with st.expander(
            f"{doc_icon} {status_icon} {doc['doc_id']} - {doc['provider']}{flag_badge}",
            expanded=False
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Document ID:** `{doc['doc_id']}`")
                st.write(f"**Type:** {doc['doc_type'].replace('_', ' ').title()}")
                st.write(f"**Provider:** {doc['provider']}")
                st.write(f"**Service Date:** {doc['service_date']}")
            
            with col2:
                st.write(f"**Status:** {doc['status'].title()}")
                st.write(f"**Flagged:** {'Yes 🚩' if doc['flagged'] else 'No'}")
                st.write(f"**Amount:** ${doc['amount']:,.2f}")
                
                # Show current action if set
                if doc.get('action'):
                    action_icon = {
                        'ignored': '⊘',
                        'followup': '🔔',
                        'resolved': '✅'
                    }.get(doc['action'], '•')
                    st.write(f"**Action:** {action_icon} {doc['action'].title()}")
            
            # Show spinner if analyzing
            if doc['status'] == 'analyzing':
                with st.spinner(f"Analyzing {doc['doc_id']}..."):
                    time.sleep(0.5)  # Simulated delay
            
            st.markdown("---")
            
            # Action Management Section
            st.markdown("**📋 Action Management**")
            
            col_action1, col_action2 = st.columns([2, 1])
            
            with col_action1:
                current_action = doc.get('action', 'none')
                action_options = {
                    'none': '— No Action',
                    'ignored': '⊘ Ignore',
                    'followup': '🔔 Follow-up Required',
                    'resolved': '✅ Resolved'
                }
                
                selected_action = st.selectbox(
                    "Action",
                    options=list(action_options.keys()),
                    index=list(action_options.keys()).index(current_action) if current_action in action_options else 0,
                    format_func=lambda x: action_options[x],
                    key=f"action_{doc['doc_id']}"
                )
            
            with col_action2:
                if selected_action != current_action:
                    if st.button("💾 Save Action", key=f"save_action_{doc['doc_id']}", type="primary"):
                        if selected_action == 'none':
                            doc['action'] = None
                            doc['action_date'] = None
                        else:
                            doc['action'] = selected_action
                            doc['action_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                        st.success(f"Action updated to: {action_options[selected_action]}")
                        st.rerun()
            
            # Action notes
            if doc.get('action') and doc['action'] != 'none':
                action_notes = st.text_area(
                    "Action Notes",
                    value=doc.get('action_notes', ''),
                    height=80,
                    key=f"notes_{doc['doc_id']}",
                    placeholder="Add notes about this action..."
                )
                
                col_notes1, col_notes2 = st.columns([1, 1])
                
                with col_notes1:
                    if action_notes != doc.get('action_notes', ''):
                        if st.button("💾 Save Notes", key=f"save_notes_{doc['doc_id']}"):
                            doc['action_notes'] = action_notes
                            st.success("Notes saved!")
                            st.rerun()
                
                with col_notes2:
                    if st.button("🗑️ Clear Action", key=f"clear_action_{doc['doc_id']}"):
                        doc['action'] = None
                        doc['action_notes'] = ''
                        doc['action_date'] = None
                        st.success("Action cleared!")
                        st.rerun()
            
            # Show document content
            with st.expander("📄 View Document"):
                st.text(doc['content'])
    
    # Handle analyze action - analyze all unflagged documents (pending or completed)
    if analyze_clicked and analyzable_docs:
        st.session_state.prod_analyzing = True
        
        # Reset completed docs to pending before analyzing
        for doc in completed_unflagged_docs:
            update_session_document(doc['doc_id'], {'status': 'pending'})
        
        # Now all analyzable docs are pending
        docs_to_analyze = analyzable_docs
        
        # Simulate parallel analysis with progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, doc in enumerate(docs_to_analyze):
            # Update document status to analyzing in session state
            update_session_document(doc['doc_id'], {'status': 'analyzing'})
            
            status_text.text(f"Analyzing {doc['doc_id']}... ({idx + 1}/{len(docs_to_analyze)})")
            
            # Simulate analysis time
            time.sleep(1.5)
            
            # Mark as completed in session state
            update_session_document(doc['doc_id'], {'status': 'completed'})
            
            # Update progress
            progress_bar.progress((idx + 1) / len(docs_to_analyze))
        
        status_text.text("✅ Analysis complete!")
        time.sleep(1)
        
        st.session_state.prod_analyzing = False
        
        # Show summary
        flagged_skipped = len([d for d in pending_docs if d['flagged']])
        if flagged_skipped > 0:
            st.success(f"✅ Successfully analyzed {len(pending_unflagged_docs)} document(s)! ({flagged_skipped} flagged documents skipped)")
        else:
            st.success(f"✅ Successfully analyzed {len(pending_unflagged_docs)} document(s)!")
        st.rerun()
