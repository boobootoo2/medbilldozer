"""Healthcare Data Ingestion Logic

This module handles the generation of fake healthcare data from simulated portals
and normalizes it into the proper data models for storage in session state.

DEMO ONLY - All data is fictional and clearly marked.
"""

import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, TypedDict

# Import data models from profile_editor
from medbilldozer.ui.profile_editor import (
    InsurancePlan,
    Provider,
    NormalizedLineItem,
    ImportJob,
    Document
)

# Import fictional entities
from medbilldozer.data.fictional_entities import (
    HealthcareEntity,
    InsuranceCompany,
    HealthcareProvider
)


# ==============================================================================
# Configuration
# ==============================================================================

# CPT codes with descriptions for realistic line items
CPT_CODES = {
    "99213": "Office Visit - Established Patient, Level 3",
    "99214": "Office Visit - Established Patient, Level 4",
    "99215": "Office Visit - Established Patient, Level 5",
    "99203": "Office Visit - New Patient, Level 3",
    "99204": "Office Visit - New Patient, Level 4",
    "80053": "Comprehensive Metabolic Panel",
    "85025": "Complete Blood Count with Differential",
    "36415": "Routine Venipuncture",
    "45378": "Colonoscopy with Biopsy",
    "93000": "Electrocardiogram (EKG)",
    "73610": "X-ray Ankle, 3 Views",
    "70450": "CT Head without Contrast",
    "71020": "Chest X-ray, 2 Views",
    "81001": "Urinalysis, Manual",
    "90471": "Immunization Administration, First Vaccine",
    "J3490": "Unclassified Drug Injection",
    "G0438": "Annual Wellness Visit - Initial",
    "G0439": "Annual Wellness Visit - Subsequent",
}

# Diagnosis codes (ICD-10)
ICD10_CODES = {
    "Z00.00": "Encounter for general adult medical examination",
    "E11.9": "Type 2 diabetes mellitus without complications",
    "I10": "Essential (primary) hypertension",
    "E78.5": "Hyperlipidemia, unspecified",
    "Z23": "Encounter for immunization",
    "R51.9": "Headache, unspecified",
    "J06.9": "Acute upper respiratory infection",
    "K21.9": "Gastro-esophageal reflux disease",
    "M79.3": "Panniculitis, unspecified",
}


# ==============================================================================
# Helper Functions
# ==============================================================================


def generate_fake_claim_number() -> str:
    """Generate a fake claim number."""
    return f"CLM-DEMO-{random.randint(100000, 999999)}"


def generate_fake_date(days_ago: int = 0) -> str:
    """Generate a fake date in ISO format (YYYY-MM-DD)."""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d")


def generate_fake_amount(min_amount: float = 50.0, max_amount: float = 2500.0) -> float:
    """Generate a fake dollar amount."""
    return round(random.uniform(min_amount, max_amount), 2)


def generate_realistic_claim_amounts() -> Dict[str, float]:
    """Generate realistic claim amounts with proper relationships.

    Returns:
        Dict with billed_amount, allowed_amount, paid_by_insurance, patient_responsibility
    """
    billed = generate_fake_amount(100.0, 3000.0)

    # Insurance typically negotiates 60-90% of billed
    allowed = round(billed * random.uniform(0.60, 0.90), 2)

    # Insurance pays 70-95% of allowed based on plan
    paid = round(allowed * random.uniform(0.70, 0.95), 2)

    # Patient pays the difference
    patient_resp = round(allowed - paid, 2)

    return {
        "billed_amount": billed,
        "allowed_amount": allowed,
        "paid_by_insurance": paid,
        "patient_responsibility": patient_resp
    }


def generate_npi() -> str:
    """Generate a fake but valid-looking NPI number (10 digits)."""
    return f"1{random.randint(100000000, 999999999)}"


def generate_tax_id() -> str:
    """Generate a fake EIN/Tax ID (XX-XXXXXXX format)."""
    return f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"


# ==============================================================================
# Document Generation
# ==============================================================================


def generate_fake_document(
    job_id: str,
    source_type: str,
    entity: HealthcareEntity
) -> Document:
    """Generate a fake ImportedDocument record.

    Args:
        job_id: Import job ID
        source_type: Type of source (insurance_portal, provider_portal, etc.)
        entity: The healthcare entity (insurance or provider)

    Returns:
        Document record
    """
    doc_id = str(uuid.uuid4())
    entity_name = entity.get('name', 'Unknown')

    # Generate fake filename based on source type
    if 'insurance' in source_type.lower():
        filename = f"eob_statement_{entity_name.replace(' ', '_')}_{generate_fake_date()}.pdf"
    else:
        filename = f"bill_{entity_name.replace(' ', '_')}_{generate_fake_date()}.pdf"

    return Document(
        document_id=doc_id,
        import_job_id=job_id,
        file_name=filename,
        file_path=f"/demo/documents/{doc_id}.pdf",
        file_type="pdf",
        raw_text=None,  # In demo mode, we don't store raw text
        status="extracted",
        created_at=datetime.utcnow().isoformat()
    )


# ==============================================================================
# Line Item Generation
# ==============================================================================


def generate_line_items_from_insurance(
    job_id: str,
    insurance_entity: InsuranceCompany,
    num_items: int = 5
) -> List[NormalizedLineItem]:
    """Generate fake line items from an insurance EOB/claim.

    Args:
        job_id: Import job ID
        insurance_entity: Insurance company entity
        num_items: Number of line items to generate (default 5)

    Returns:
        List of NormalizedLineItem records
    """
    line_items = []

    for i in range(num_items):
        # Pick random CPT code
        cpt_code = random.choice(list(CPT_CODES.keys()))
        description = CPT_CODES[cpt_code]

        # Generate realistic amounts
        amounts = generate_realistic_claim_amounts()

        # Generate service date (random in past 180 days)
        days_ago = random.randint(10, 180)
        service_date = generate_fake_date(days_ago)

        # Generate fake provider name
        provider_names = [
            "Dr. Sarah Johnson (DEMO)",
            "Dr. Michael Chen (DEMO)",
            "Dr. Emily Rodriguez (DEMO)",
            "Memorial Hospital (DEMO)",
            "City Medical Center (DEMO)",
            "Regional Healthcare (DEMO)"
        ]
        provider_name = random.choice(provider_names)

        line_item = NormalizedLineItem(
            line_item_id=str(uuid.uuid4()),
            import_job_id=job_id,
            service_date=service_date,
            procedure_code=cpt_code,
            procedure_description=description,
            provider_name=provider_name,
            provider_npi=generate_npi(),
            billed_amount=amounts["billed_amount"],
            allowed_amount=amounts["allowed_amount"],
            paid_by_insurance=amounts["paid_by_insurance"],
            patient_responsibility=amounts["patient_responsibility"],
            claim_number=generate_fake_claim_number(),
            created_at=datetime.utcnow().isoformat()
        )

        line_items.append(line_item)

    return line_items


def generate_line_items_from_provider(
    job_id: str,
    provider_entity: HealthcareProvider,
    num_items: int = 3
) -> List[NormalizedLineItem]:
    """Generate fake line items from a provider bill/statement.

    Args:
        job_id: Import job ID
        provider_entity: Healthcare provider entity
        num_items: Number of line items to generate (default 3)

    Returns:
        List of NormalizedLineItem records
    """
    line_items = []
    provider_name = provider_entity.get('name', 'Unknown Provider')
    provider_npi = provider_entity.get('npi', generate_npi())

    for i in range(num_items):
        # Pick random CPT code
        cpt_code = random.choice(list(CPT_CODES.keys()))
        description = CPT_CODES[cpt_code]

        # Generate realistic amounts
        amounts = generate_realistic_claim_amounts()

        # Generate service date (random in past 120 days)
        days_ago = random.randint(10, 120)
        service_date = generate_fake_date(days_ago)

        line_item = NormalizedLineItem(
            line_item_id=str(uuid.uuid4()),
            import_job_id=job_id,
            service_date=service_date,
            procedure_code=cpt_code,
            procedure_description=description,
            provider_name=provider_name,
            provider_npi=provider_npi,
            billed_amount=amounts["billed_amount"],
            allowed_amount=amounts["allowed_amount"],
            paid_by_insurance=amounts["paid_by_insurance"],
            patient_responsibility=amounts["patient_responsibility"],
            claim_number=None,  # Provider bills may not have claim numbers yet
            created_at=datetime.utcnow().isoformat()
        )

        line_items.append(line_item)

    return line_items


# ==============================================================================
# Main Ingestion Function
# ==============================================================================


def import_sample_data(
    selected_entity: HealthcareEntity,
    num_line_items: Optional[int] = None
) -> ImportJob:
    """Generate fake healthcare data and prepare for storage.

    This is the main ingestion function that:
    1. Generates fake ImportedDocument records
    2. Normalizes into NormalizedLineItem records
    3. Packages everything into an ImportJob

    The caller is responsible for storing the result in st.session_state.

    Args:
        selected_entity: The insurance or provider entity selected by user
        num_line_items: Number of line items to generate (optional, uses defaults)

    Returns:
        ImportJob with all generated documents and line items

    Notes:
        - All records have source = "demo_sample"
        - No UI rendering occurs in this function
        - No actual API calls or file I/O
    """
    job_id = str(uuid.uuid4())
    entity_type = selected_entity.get('entity_type', 'unknown')

    # Determine source type
    if entity_type == 'insurance':
        source_type = "insurance_portal"
        source_method = "demo_sample"
        default_items = 5
    elif entity_type == 'provider':
        source_type = "provider_portal"
        source_method = "demo_sample"
        default_items = 3
    else:
        raise ValueError(f"Unknown entity type: {entity_type}")

    num_items = num_line_items if num_line_items is not None else default_items

    # Generate fake document
    document = generate_fake_document(job_id, source_type, selected_entity)

    # Generate line items based on entity type
    if entity_type == 'insurance':
        line_items = generate_line_items_from_insurance(
            job_id,
            selected_entity,  # type: ignore - we know it's InsuranceCompany
            num_items
        )
    else:
        line_items = generate_line_items_from_provider(
            job_id,
            selected_entity,  # type: ignore - we know it's HealthcareProvider
            num_items
        )

    # Create ImportJob
    import_job = ImportJob(
        job_id=job_id,
        source_type=source_type,
        source_method=source_method,
        status="completed",
        documents=[document],
        line_items=line_items,
        created_at=datetime.utcnow().isoformat(),
        completed_at=datetime.utcnow().isoformat(),
        error_message=None
    )

    return import_job


# ==============================================================================
# Insurance Plan and Provider Extraction
# ==============================================================================


def extract_insurance_plan_from_entity(
    insurance_entity: InsuranceCompany
) -> InsurancePlan:
    """Extract an InsurancePlan record from an insurance entity.

    Args:
        insurance_entity: Insurance company entity

    Returns:
        InsurancePlan record
    """
    plan_id = str(uuid.uuid4())
    carrier_name = insurance_entity.get('name', 'Unknown Insurance')

    # Extract network type from entity (or default to PPO)
    network_type = insurance_entity.get('network_type', 'national')

    # Map network to plan type
    if network_type == 'national':
        plan_type = 'PPO'
    elif network_type == 'regional':
        plan_type = 'HMO'
    else:
        plan_type = 'EPO'

    # Generate realistic plan details
    deductible_individual = round(random.uniform(500, 3000), 0)
    deductible_family = deductible_individual * 2

    oop_individual = round(random.uniform(3000, 7000), 0)
    oop_family = oop_individual * 2

    return InsurancePlan(
        plan_id=plan_id,
        carrier_name=carrier_name,
        plan_name=f"{plan_type} - Demo Plan",
        member_id=f"MEM-{random.randint(100000, 999999)}",
        group_number=f"GRP-{random.randint(10000, 99999)}",
        policy_holder="DEMO PATIENT",
        effective_date=generate_fake_date(365),  # Started 1 year ago
        termination_date=None,
        plan_type=plan_type,
        deductible={
            "individual": deductible_individual,
            "family": deductible_family
        },
        out_of_pocket_max={
            "individual": oop_individual,
            "family": oop_family
        },
        copay={
            "primary_care": round(random.uniform(15, 40), 0),
            "specialist": round(random.uniform(40, 75), 0),
            "er": round(random.uniform(150, 350), 0),
            "urgent_care": round(random.uniform(50, 100), 0)
        },
        coinsurance=round(random.uniform(0.15, 0.30), 2),  # 15-30%
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )


def extract_provider_from_entity(
    provider_entity: HealthcareProvider
) -> Provider:
    """Extract a Provider record from a provider entity.

    Args:
        provider_entity: Healthcare provider entity

    Returns:
        Provider record
    """
    provider_id = str(uuid.uuid4())
    provider_name = provider_entity.get('name', 'Unknown Provider')
    specialty = provider_entity.get('specialty', 'General Practice')
    npi = provider_entity.get('npi', generate_npi())

    # Extract location info (fields are location_city and location_state in entity)
    city = provider_entity.get('location_city', 'Unknown City')
    state = provider_entity.get('location_state', 'XX')

    # Check if in network (random for demo)
    in_network = random.choice([True, True, True, False])  # 75% chance in-network

    return Provider(
        provider_id=provider_id,
        name=provider_name,
        specialty=specialty,
        npi=npi,
        tax_id=generate_tax_id(),
        address={
            "street": f"{random.randint(100, 9999)} Demo Street",
            "city": city,
            "state": state,
            "zip": f"{random.randint(10000, 99999)}"
        },
        phone=f"{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
        fax=f"{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
        in_network=in_network,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )


# ==============================================================================
# Batch Import Functions
# ==============================================================================


def import_multiple_entities(
    entities: List[HealthcareEntity],
    items_per_entity: int = 3
) -> List[ImportJob]:
    """Import data from multiple entities in batch.

    Args:
        entities: List of insurance or provider entities
        items_per_entity: Number of line items to generate per entity

    Returns:
        List of ImportJob records
    """
    import_jobs = []

    for entity in entities:
        job = import_sample_data(entity, num_line_items=items_per_entity)
        import_jobs.append(job)

    return import_jobs


# ==============================================================================
# Session State Storage Helper
# ==============================================================================


def store_import_job_in_session(
    import_job: ImportJob,
    session_state_key: str = "health_profile"
) -> None:
    """Store ImportJob data in Streamlit session state.

    This helper function handles the proper storage of import job data
    in the session state structure expected by the profile editor.

    Args:
        import_job: The import job to store
        session_state_key: Session state key (default: "health_profile")

    Notes:
        This function DOES interact with st.session_state.
        It's separated here for clarity but uses Streamlit internally.
    """
    import streamlit as st

    # Initialize session state if needed
    if session_state_key not in st.session_state:
        st.session_state[session_state_key] = {
            "import_jobs": [],
            "line_items": [],
            "insurance_plans": [],
            "providers": []
        }

    # Append import job
    st.session_state[session_state_key]["import_jobs"].append(import_job)

    # Append line items
    st.session_state[session_state_key]["line_items"].extend(import_job.get("line_items", []))


# ==============================================================================
# Export Functions
# ==============================================================================

__all__ = [
    # Main ingestion function
    'import_sample_data',

    # Extraction functions
    'extract_insurance_plan_from_entity',
    'extract_provider_from_entity',

    # Batch functions
    'import_multiple_entities',

    # Storage helper
    'store_import_job_in_session',

    # Document and line item generators (for advanced use)
    'generate_fake_document',
    'generate_line_items_from_insurance',
    'generate_line_items_from_provider',

    # Helper utilities
    'generate_fake_claim_number',
    'generate_fake_date',
    'generate_realistic_claim_amounts',
]

