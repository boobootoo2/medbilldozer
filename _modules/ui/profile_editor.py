"""Profile Editor - User identity, insurance, and provider management with importer.

Provides a Plaid-like experience for importing health insurance and provider data,
with structured field extraction and normalization into a consistent schema.
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, TypedDict, Literal
from datetime import datetime
import tempfile


# ==============================================================================
# TYPE DEFINITIONS
# ==============================================================================

class UserProfile(TypedDict, total=False):
    """User identity information."""
    user_id: str
    full_name: str
    date_of_birth: str  # ISO format YYYY-MM-DD
    email: str
    phone: str
    address: Dict[str, str]  # street, city, state, zip
    created_at: str
    updated_at: str


class InsurancePlan(TypedDict, total=False):
    """Health insurance plan details."""
    plan_id: str
    carrier_name: str
    plan_name: str
    member_id: str
    group_number: str
    policy_holder: str
    effective_date: str
    termination_date: Optional[str]
    plan_type: str  # PPO, HMO, EPO, POS
    deductible: Dict[str, float]  # individual, family
    out_of_pocket_max: Dict[str, float]  # individual, family
    copay: Dict[str, float]  # primary_care, specialist, er, urgent_care
    coinsurance: float  # percentage
    created_at: str
    updated_at: str


class Provider(TypedDict, total=False):
    """Healthcare provider information."""
    provider_id: str
    name: str
    specialty: str
    npi: str  # National Provider Identifier
    tax_id: str
    address: Dict[str, str]
    phone: str
    fax: str
    in_network: bool
    created_at: str
    updated_at: str


class NormalizedLineItem(TypedDict, total=False):
    """Normalized billing line item from imported documents."""
    line_item_id: str
    import_job_id: str
    service_date: str
    procedure_code: str  # CPT, CDT, HCPCS
    procedure_description: str
    provider_name: str
    provider_npi: Optional[str]
    billed_amount: float
    allowed_amount: float
    paid_by_insurance: float
    patient_responsibility: float
    claim_number: Optional[str]
    created_at: str


class Document(TypedDict, total=False):
    """Uploaded or imported document metadata."""
    document_id: str
    import_job_id: str
    file_name: str
    file_path: str
    file_type: str  # pdf, csv, text
    raw_text: Optional[str]
    status: str  # pending, extracted, failed
    created_at: str


class ImportJob(TypedDict, total=False):
    """Import job tracking."""
    job_id: str
    source_type: str  # insurance_eob, insurance_csv, provider_bill, provider_csv, text_paste
    source_method: str  # upload, paste, fhir_connect
    status: str  # pending, processing, completed, failed
    documents: List[Document]
    line_items: List[NormalizedLineItem]
    created_at: str
    completed_at: Optional[str]
    error_message: Optional[str]


# ==============================================================================
# CONFIGURATION & FEATURE FLAGS
# ==============================================================================

def is_profile_editor_enabled() -> bool:
    """Check if profile editor is enabled via environment variable."""
    env_value = os.environ.get('PROFILE_EDITOR_ENABLED', '').upper()
    return env_value in ('TRUE', '1', 'YES', 'ON')


def is_importer_enabled() -> bool:
    """Check if importer feature is enabled via environment variable."""
    env_value = os.environ.get('IMPORTER_ENABLED', '').upper()
    return env_value in ('TRUE', '1', 'YES', 'ON')


# ==============================================================================
# DATA PERSISTENCE
# ==============================================================================

def get_data_dir() -> Path:
    """Get or create data directory for profile storage."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def atomic_write_json(file_path: Path, data: Dict) -> None:
    """Atomically write JSON data to file using temp file + rename."""
    temp_fd, temp_path = tempfile.mkstemp(
        dir=file_path.parent,
        prefix=f".{file_path.name}.",
        suffix=".tmp"
    )
    
    try:
        # Write to temp file
        with os.fdopen(temp_fd, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        # Atomic rename
        os.replace(temp_path, file_path)
    except Exception:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except Exception:
            pass
        raise


def load_profile() -> Optional[UserProfile]:
    """Load user profile from disk."""
    profile_path = get_data_dir() / "user_profile.json"
    if profile_path.exists():
        with open(profile_path, 'r') as f:
            return json.load(f)
    return None


def save_profile(profile: UserProfile) -> None:
    """Save user profile to disk with atomic write."""
    profile['updated_at'] = datetime.utcnow().isoformat()
    if 'created_at' not in profile:
        profile['created_at'] = profile['updated_at']
    
    profile_path = get_data_dir() / "user_profile.json"
    atomic_write_json(profile_path, profile)


def load_insurance_plans() -> List[InsurancePlan]:
    """Load insurance plans from disk."""
    plans_path = get_data_dir() / "insurance_plans.json"
    if plans_path.exists():
        with open(plans_path, 'r') as f:
            return json.load(f)
    return []


def save_insurance_plans(plans: List[InsurancePlan]) -> None:
    """Save insurance plans to disk with atomic write."""
    plans_path = get_data_dir() / "insurance_plans.json"
    atomic_write_json(plans_path, plans)


def load_providers() -> List[Provider]:
    """Load providers from disk."""
    providers_path = get_data_dir() / "providers.json"
    if providers_path.exists():
        with open(providers_path, 'r') as f:
            return json.load(f)
    return []


def save_providers(providers: List[Provider]) -> None:
    """Save providers to disk with atomic write."""
    providers_path = get_data_dir() / "providers.json"
    atomic_write_json(providers_path, providers)


def load_import_jobs() -> List[ImportJob]:
    """Load import jobs from disk."""
    jobs_path = get_data_dir() / "import_jobs.json"
    if jobs_path.exists():
        with open(jobs_path, 'r') as f:
            return json.load(f)
    return []


def save_import_jobs(jobs: List[ImportJob]) -> None:
    """Save import jobs to disk with atomic write."""
    jobs_path = get_data_dir() / "import_jobs.json"
    atomic_write_json(jobs_path, jobs)


def load_line_items() -> List[NormalizedLineItem]:
    """Load normalized line items from disk."""
    items_path = get_data_dir() / "normalized_line_items.json"
    if items_path.exists():
        with open(items_path, 'r') as f:
            return json.load(f)
    return []


def save_line_items(items: List[NormalizedLineItem]) -> None:
    """Save normalized line items to disk with atomic write."""
    items_path = get_data_dir() / "normalized_line_items.json"
    atomic_write_json(items_path, items)


# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================

def initialize_profile_state():
    """Initialize profile editor session state variables."""
    if 'profile_page' not in st.session_state:
        st.session_state.profile_page = 'overview'  # overview, identity, insurance, providers, importer
    
    if 'import_wizard_step' not in st.session_state:
        st.session_state.import_wizard_step = 1
    
    if 'import_source_type' not in st.session_state:
        st.session_state.import_source_type = None
    
    if 'import_data' not in st.session_state:
        st.session_state.import_data = None
    
    if 'pending_line_items' not in st.session_state:
        st.session_state.pending_line_items = []


# ==============================================================================
# PROFILE OVERVIEW PAGE
# ==============================================================================

def render_profile_overview():
    """Render profile overview page with quick stats and actions."""
    st.header("👤 Profile Overview")
    
    profile = load_profile()
    plans = load_insurance_plans()
    providers = load_providers()
    jobs = load_import_jobs()
    line_items = load_line_items()
    
    # Quick stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Identity",
            value="✓ Complete" if profile and profile.get('full_name') else "⚠ Incomplete",
            help="Your personal information"
        )
    
    with col2:
        st.metric(
            label="Insurance Plans",
            value=len(plans),
            help="Number of insurance plans on file"
        )
    
    with col3:
        st.metric(
            label="Providers",
            value=len(providers),
            help="Number of healthcare providers on file"
        )
    
    with col4:
        st.metric(
            label="Imported Items",
            value=len(line_items),
            help="Number of normalized line items from imports"
        )
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Edit Identity", use_container_width=True, type="primary"):
            st.session_state.profile_page = 'identity'
            st.rerun()
        
        if st.button("🏥 Manage Insurance", use_container_width=True):
            st.session_state.profile_page = 'insurance'
            st.rerun()
    
    with col2:
        if st.button("👨‍⚕️ Manage Providers", use_container_width=True):
            st.session_state.profile_page = 'providers'
            st.rerun()
        
        if is_importer_enabled():
            if st.button("📥 Import Data", use_container_width=True):
                st.session_state.profile_page = 'importer'
                st.session_state.import_wizard_step = 1
                st.rerun()
    
    # Recent import activity
    if jobs:
        st.markdown("---")
        st.subheader("Recent Imports")
        
        for job in sorted(jobs, key=lambda x: x.get('created_at', ''), reverse=True)[:5]:
            with st.expander(f"📄 {job.get('source_type', 'Unknown')} - {job.get('created_at', '')[:10]}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Status:** {job.get('status', 'Unknown')}")
                    st.write(f"**Method:** {job.get('source_method', 'Unknown')}")
                    st.write(f"**Line Items:** {len(job.get('line_items', []))}")
                with col2:
                    st.write(f"**Documents:** {len(job.get('documents', []))}")


# ==============================================================================
# IDENTITY EDITOR
# ==============================================================================

def render_identity_editor():
    """Render user identity editor form."""
    st.header("👤 Personal Identity")
    
    profile = load_profile() or {}
    
    with st.form("identity_form", clear_on_submit=False):
        st.subheader("Basic Information")
        
        full_name = st.text_input(
            "Full Name *",
            value=profile.get('full_name', ''),
            placeholder="John Doe",
            help="Your legal full name as it appears on insurance documents"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            dob = st.date_input(
                "Date of Birth *",
                value=datetime.fromisoformat(profile['date_of_birth']) if profile.get('date_of_birth') else None,
                help="Required for insurance verification"
            )
        
        with col2:
            email = st.text_input(
                "Email",
                value=profile.get('email', ''),
                placeholder="john@example.com"
            )
        
        phone = st.text_input(
            "Phone Number",
            value=profile.get('phone', ''),
            placeholder="(555) 123-4567"
        )
        
        st.subheader("Address")
        
        address = profile.get('address', {})
        
        street = st.text_input(
            "Street Address",
            value=address.get('street', ''),
            placeholder="123 Main St, Apt 4B"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            city = st.text_input(
                "City",
                value=address.get('city', ''),
                placeholder="San Francisco"
            )
        
        with col2:
            state = st.text_input(
                "State",
                value=address.get('state', ''),
                placeholder="CA",
                max_chars=2
            )
        
        with col3:
            zip_code = st.text_input(
                "ZIP Code",
                value=address.get('zip', ''),
                placeholder="94102",
                max_chars=10
            )
        
        submitted = st.form_submit_button("💾 Save Identity", use_container_width=True, type="primary")
        
        if submitted:
            if not full_name or not dob:
                st.error("⚠️ Full Name and Date of Birth are required fields.")
            else:
                # Build updated profile
                updated_profile: UserProfile = {
                    'user_id': profile.get('user_id', f"user_{datetime.utcnow().timestamp()}"),
                    'full_name': full_name,
                    'date_of_birth': dob.isoformat(),
                    'email': email,
                    'phone': phone,
                    'address': {
                        'street': street,
                        'city': city,
                        'state': state.upper() if state else '',
                        'zip': zip_code
                    },
                    'created_at': profile.get('created_at', ''),
                    'updated_at': ''
                }
                
                save_profile(updated_profile)
                st.success("✅ Identity saved successfully!")
                st.balloons()


# ==============================================================================
# INSURANCE PLAN EDITOR
# ==============================================================================

def render_insurance_editor():
    """Render insurance plan management interface."""
    st.header("🏥 Insurance Plans")
    
    plans = load_insurance_plans()
    
    # Add new plan button
    if st.button("➕ Add New Insurance Plan", type="primary"):
        st.session_state.editing_plan_id = 'new'
    
    if st.session_state.get('editing_plan_id'):
        render_insurance_plan_form(plans)
    else:
        # List existing plans
        if not plans:
            st.info("📋 No insurance plans on file. Add one to get started!")
        else:
            for plan in plans:
                with st.expander(f"🏥 {plan.get('carrier_name', 'Unknown')} - {plan.get('plan_name', 'Unknown')}"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**Member ID:** {plan.get('member_id', 'N/A')}")
                        st.write(f"**Plan Type:** {plan.get('plan_type', 'N/A')}")
                        st.write(f"**Effective Date:** {plan.get('effective_date', 'N/A')}")
                    
                    with col2:
                        deductible = plan.get('deductible', {})
                        st.write(f"**Deductible (Ind/Fam):** ${deductible.get('individual', 0):,.2f} / ${deductible.get('family', 0):,.2f}")
                        st.write(f"**OOP Max (Ind/Fam):** ${plan.get('out_of_pocket_max', {}).get('individual', 0):,.2f} / ${plan.get('out_of_pocket_max', {}).get('family', 0):,.2f}")
                    
                    with col3:
                        if st.button("✏️ Edit", key=f"edit_plan_{plan['plan_id']}"):
                            st.session_state.editing_plan_id = plan['plan_id']
                            st.rerun()
                        
                        if st.button("🗑️ Delete", key=f"delete_plan_{plan['plan_id']}"):
                            plans = [p for p in plans if p['plan_id'] != plan['plan_id']]
                            save_insurance_plans(plans)
                            st.success("Plan deleted!")
                            st.rerun()


def render_insurance_plan_form(plans: List[InsurancePlan]):
    """Render insurance plan edit/create form."""
    editing_id = st.session_state.get('editing_plan_id')
    
    if editing_id == 'new':
        st.subheader("➕ Add New Insurance Plan")
        plan = {}
    else:
        st.subheader("✏️ Edit Insurance Plan")
        plan = next((p for p in plans if p['plan_id'] == editing_id), {})
    
    with st.form("insurance_form", clear_on_submit=False):
        st.markdown("### Basic Plan Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            carrier_name = st.text_input(
                "Insurance Carrier *",
                value=plan.get('carrier_name', ''),
                placeholder="Blue Cross Blue Shield"
            )
            
            member_id = st.text_input(
                "Member ID *",
                value=plan.get('member_id', ''),
                placeholder="ABC123456789"
            )
        
        with col2:
            plan_name = st.text_input(
                "Plan Name *",
                value=plan.get('plan_name', ''),
                placeholder="Gold PPO Plan"
            )
            
            group_number = st.text_input(
                "Group Number",
                value=plan.get('group_number', ''),
                placeholder="GRP987654"
            )
        
        policy_holder = st.text_input(
            "Policy Holder Name",
            value=plan.get('policy_holder', ''),
            placeholder="John Doe"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            plan_type = st.selectbox(
                "Plan Type *",
                options=['PPO', 'HMO', 'EPO', 'POS', 'HDHP', 'Other'],
                index=['PPO', 'HMO', 'EPO', 'POS', 'HDHP', 'Other'].index(plan.get('plan_type', 'PPO')) if plan.get('plan_type') in ['PPO', 'HMO', 'EPO', 'POS', 'HDHP', 'Other'] else 0
            )
        
        with col2:
            effective_date = st.date_input(
                "Effective Date *",
                value=datetime.fromisoformat(plan['effective_date']) if plan.get('effective_date') else None
            )
        
        with col3:
            termination_date = st.date_input(
                "Termination Date",
                value=datetime.fromisoformat(plan['termination_date']) if plan.get('termination_date') else None,
                help="Leave blank if plan is still active"
            )
        
        st.markdown("### Cost Sharing")
        
        deductible = plan.get('deductible', {})
        oop_max = plan.get('out_of_pocket_max', {})
        copay = plan.get('copay', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Deductible**")
            ded_ind = st.number_input(
                "Individual Deductible ($)",
                value=float(deductible.get('individual', 0)),
                min_value=0.0,
                step=100.0
            )
            ded_fam = st.number_input(
                "Family Deductible ($)",
                value=float(deductible.get('family', 0)),
                min_value=0.0,
                step=100.0
            )
        
        with col2:
            st.write("**Out-of-Pocket Maximum**")
            oop_ind = st.number_input(
                "Individual OOP Max ($)",
                value=float(oop_max.get('individual', 0)),
                min_value=0.0,
                step=100.0
            )
            oop_fam = st.number_input(
                "Family OOP Max ($)",
                value=float(oop_max.get('family', 0)),
                min_value=0.0,
                step=100.0
            )
        
        coinsurance = st.slider(
            "Coinsurance (%)",
            min_value=0,
            max_value=100,
            value=int(plan.get('coinsurance', 20)),
            help="Percentage you pay after deductible (e.g., 20% = you pay 20%, insurance pays 80%)"
        )
        
        st.write("**Copays**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            copay_pc = st.number_input("Primary Care ($)", value=float(copay.get('primary_care', 0)), min_value=0.0)
        with col2:
            copay_spec = st.number_input("Specialist ($)", value=float(copay.get('specialist', 0)), min_value=0.0)
        with col3:
            copay_er = st.number_input("ER ($)", value=float(copay.get('er', 0)), min_value=0.0)
        with col4:
            copay_uc = st.number_input("Urgent Care ($)", value=float(copay.get('urgent_care', 0)), min_value=0.0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 Save Plan", use_container_width=True, type="primary"):
                if not carrier_name or not plan_name or not member_id or not effective_date:
                    st.error("⚠️ Please fill in all required fields (marked with *)")
                else:
                    new_plan: InsurancePlan = {
                        'plan_id': plan.get('plan_id', f"plan_{datetime.utcnow().timestamp()}"),
                        'carrier_name': carrier_name,
                        'plan_name': plan_name,
                        'member_id': member_id,
                        'group_number': group_number,
                        'policy_holder': policy_holder,
                        'effective_date': effective_date.isoformat(),
                        'termination_date': termination_date.isoformat() if termination_date else None,
                        'plan_type': plan_type,
                        'deductible': {'individual': ded_ind, 'family': ded_fam},
                        'out_of_pocket_max': {'individual': oop_ind, 'family': oop_fam},
                        'copay': {
                            'primary_care': copay_pc,
                            'specialist': copay_spec,
                            'er': copay_er,
                            'urgent_care': copay_uc
                        },
                        'coinsurance': float(coinsurance),
                        'created_at': plan.get('created_at', datetime.utcnow().isoformat()),
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    
                    if editing_id == 'new':
                        plans.append(new_plan)
                    else:
                        plans = [new_plan if p['plan_id'] == editing_id else p for p in plans]
                    
                    save_insurance_plans(plans)
                    st.session_state.editing_plan_id = None
                    st.success("✅ Insurance plan saved successfully!")
                    st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.editing_plan_id = None
                st.rerun()


# ==============================================================================
# PROVIDER EDITOR
# ==============================================================================

def render_provider_editor():
    """Render healthcare provider management interface."""
    st.header("👨‍⚕️ Healthcare Providers")
    
    providers = load_providers()
    
    # Add new provider button
    if st.button("➕ Add New Provider", type="primary"):
        st.session_state.editing_provider_id = 'new'
    
    if st.session_state.get('editing_provider_id'):
        render_provider_form(providers)
    else:
        # List existing providers
        if not providers:
            st.info("📋 No providers on file. Add one to get started!")
        else:
            for provider in providers:
                with st.expander(f"👨‍⚕️ {provider.get('name', 'Unknown')} - {provider.get('specialty', 'N/A')}"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**Specialty:** {provider.get('specialty', 'N/A')}")
                        st.write(f"**NPI:** {provider.get('npi', 'N/A')}")
                        st.write(f"**Phone:** {provider.get('phone', 'N/A')}")
                    
                    with col2:
                        address = provider.get('address', {})
                        st.write(f"**Address:** {address.get('street', 'N/A')}")
                        st.write(f"{address.get('city', '')}, {address.get('state', '')} {address.get('zip', '')}")
                        st.write(f"**In Network:** {'✅ Yes' if provider.get('in_network') else '❌ No'}")
                    
                    with col3:
                        if st.button("✏️ Edit", key=f"edit_prov_{provider['provider_id']}"):
                            st.session_state.editing_provider_id = provider['provider_id']
                            st.rerun()
                        
                        if st.button("🗑️ Delete", key=f"delete_prov_{provider['provider_id']}"):
                            providers = [p for p in providers if p['provider_id'] != provider['provider_id']]
                            save_providers(providers)
                            st.success("Provider deleted!")
                            st.rerun()


def render_provider_form(providers: List[Provider]):
    """Render provider edit/create form."""
    editing_id = st.session_state.get('editing_provider_id')
    
    if editing_id == 'new':
        st.subheader("➕ Add New Provider")
        provider = {}
    else:
        st.subheader("✏️ Edit Provider")
        provider = next((p for p in providers if p['provider_id'] == editing_id), {})
    
    with st.form("provider_form", clear_on_submit=False):
        name = st.text_input(
            "Provider/Practice Name *",
            value=provider.get('name', ''),
            placeholder="Dr. Jane Smith / ABC Medical Group"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            specialty = st.text_input(
                "Specialty",
                value=provider.get('specialty', ''),
                placeholder="Cardiology, Primary Care, etc."
            )
            
            npi = st.text_input(
                "NPI Number",
                value=provider.get('npi', ''),
                placeholder="1234567890",
                max_chars=10,
                help="National Provider Identifier (10 digits)"
            )
        
        with col2:
            tax_id = st.text_input(
                "Tax ID / EIN",
                value=provider.get('tax_id', ''),
                placeholder="12-3456789"
            )
            
            in_network = st.checkbox(
                "In Network",
                value=provider.get('in_network', False),
                help="Check if this provider is in your insurance network"
            )
        
        st.markdown("### Contact Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            phone = st.text_input(
                "Phone Number",
                value=provider.get('phone', ''),
                placeholder="(555) 123-4567"
            )
        
        with col2:
            fax = st.text_input(
                "Fax Number",
                value=provider.get('fax', ''),
                placeholder="(555) 123-4568"
            )
        
        st.markdown("### Address")
        
        address = provider.get('address', {})
        
        street = st.text_input(
            "Street Address",
            value=address.get('street', ''),
            placeholder="456 Medical Plaza, Suite 200"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            city = st.text_input(
                "City",
                value=address.get('city', ''),
                placeholder="San Francisco"
            )
        
        with col2:
            state = st.text_input(
                "State",
                value=address.get('state', ''),
                placeholder="CA",
                max_chars=2
            )
        
        with col3:
            zip_code = st.text_input(
                "ZIP Code",
                value=address.get('zip', ''),
                placeholder="94102",
                max_chars=10
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 Save Provider", use_container_width=True, type="primary"):
                if not name:
                    st.error("⚠️ Provider name is required")
                else:
                    new_provider: Provider = {
                        'provider_id': provider.get('provider_id', f"prov_{datetime.utcnow().timestamp()}"),
                        'name': name,
                        'specialty': specialty,
                        'npi': npi,
                        'tax_id': tax_id,
                        'address': {
                            'street': street,
                            'city': city,
                            'state': state.upper() if state else '',
                            'zip': zip_code
                        },
                        'phone': phone,
                        'fax': fax,
                        'in_network': in_network,
                        'created_at': provider.get('created_at', datetime.utcnow().isoformat()),
                        'updated_at': datetime.utcnow().isoformat()
                    }
                    
                    if editing_id == 'new':
                        providers.append(new_provider)
                    else:
                        providers = [new_provider if p['provider_id'] == editing_id else p for p in providers]
                    
                    save_providers(providers)
                    st.session_state.editing_provider_id = None
                    st.success("✅ Provider saved successfully!")
                    st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.editing_provider_id = None
                st.rerun()


# ==============================================================================
# IMPORTER - WIZARD STEP 1: SOURCE SELECTION
# ==============================================================================

def render_importer_step1():
    """Render Step 1: Choose import source type."""
    st.subheader("Step 1: Choose Data Source")
    
    st.markdown("""
    Select the type of data you want to import. We'll guide you through the process 
    and extract structured information from your documents.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏥 Insurance Data")
        
        if st.button(
            "📄 EOB (Explanation of Benefits)",
            use_container_width=True,
            help="Import from insurance EOB documents (PDF or text)"
        ):
            st.session_state.import_source_type = 'insurance_eob'
            st.session_state.import_wizard_step = 2
            st.rerun()
        
        if st.button(
            "📊 Insurance CSV Export",
            use_container_width=True,
            help="Import from insurance portal CSV download"
        ):
            st.session_state.import_source_type = 'insurance_csv'
            st.session_state.import_wizard_step = 2
            st.rerun()
        
        if st.button(
            "📝 Paste Insurance Text",
            use_container_width=True,
            help="Copy/paste text from insurance documents"
        ):
            st.session_state.import_source_type = 'insurance_text'
            st.session_state.import_wizard_step = 2
            st.rerun()
        
        if st.button(
            "🔗 FHIR Connect (Preview)",
            use_container_width=True,
            help="Connect to insurance FHIR API (UI placeholder)",
            disabled=True
        ):
            st.info("🚧 FHIR Connect coming soon! This will allow direct API connections to insurance portals.")
    
    with col2:
        st.markdown("### 👨‍⚕️ Provider Data")
        
        if st.button(
            "🧾 Itemized Medical Bill",
            use_container_width=True,
            help="Import from provider itemized bill (PDF or text)"
        ):
            st.session_state.import_source_type = 'provider_bill'
            st.session_state.import_wizard_step = 2
            st.rerun()
        
        if st.button(
            "📊 Provider CSV Export",
            use_container_width=True,
            help="Import from provider portal CSV download"
        ):
            st.session_state.import_source_type = 'provider_csv'
            st.session_state.import_wizard_step = 2
            st.rerun()
        
        if st.button(
            "📝 Paste Bill Text",
            use_container_width=True,
            help="Copy/paste text from medical bills"
        ):
            st.session_state.import_source_type = 'provider_text'
            st.session_state.import_wizard_step = 2
            st.rerun()
    
    if st.button("← Back to Profile"):
        st.session_state.profile_page = 'overview'
        st.rerun()


# ==============================================================================
# IMPORTER - WIZARD STEP 2: DATA INPUT
# ==============================================================================

def render_importer_step2():
    """Render Step 2: Provide input data."""
    source_type = st.session_state.import_source_type
    
    st.subheader(f"Step 2: Provide {source_type.replace('_', ' ').title()}")
    
    if 'csv' in source_type:
        render_csv_upload()
    elif 'text' in source_type:
        render_text_paste()
    else:
        render_pdf_upload()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back to Source Selection"):
            st.session_state.import_wizard_step = 1
            st.rerun()
    
    with col2:
        if st.session_state.get('import_data'):
            if st.button("Continue to Preview →", type="primary"):
                # Extract and normalize data
                extract_and_normalize_data()
                st.session_state.import_wizard_step = 3
                st.rerun()


def render_pdf_upload():
    """Render PDF upload interface."""
    st.markdown("""
    Upload a PDF document. We'll extract the text and structure it for you.
    
    **Note:** PDF text extraction is handled by the upstream pipeline. If you upload a PDF now,
    it will be stored as "pending extraction" until the extraction process populates the raw text.
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload your EOB or itemized bill as a PDF",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        # Save uploaded file
        data_dir = get_data_dir() / "uploads"
        data_dir.mkdir(exist_ok=True)
        
        file_path = data_dir / f"{datetime.utcnow().timestamp()}_{uploaded_file.name}"
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state.import_data = {
            'method': 'pdf_upload',
            'file_name': uploaded_file.name,
            'file_path': str(file_path),
            'file_type': 'pdf',
            'raw_text': None,  # Will be populated by extraction pipeline
            'status': 'pending'
        }
        
        st.success(f"✅ Uploaded: {uploaded_file.name}")
        st.info("📋 PDF stored. Text extraction will happen in the next step.")


def render_csv_upload():
    """Render CSV upload interface."""
    st.markdown("""
    Upload a CSV file exported from your insurance or provider portal.
    
    Expected columns:
    - Date of Service
    - Procedure Code (CPT/CDT/HCPCS)
    - Description
    - Billed Amount
    - Allowed Amount
    - Paid by Insurance
    - Patient Responsibility
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload CSV export from insurance/provider portal",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        import csv
        import io
        
        # Read CSV
        content = uploaded_file.getvalue().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        rows = list(csv_reader)
        
        st.session_state.import_data = {
            'method': 'csv_upload',
            'file_name': uploaded_file.name,
            'file_type': 'csv',
            'rows': rows,
            'raw_text': content,
            'status': 'ready'
        }
        
        st.success(f"✅ Uploaded: {uploaded_file.name} ({len(rows)} rows)")
        
        # Preview first few rows
        if rows:
            st.write("**Preview (first 3 rows):**")
            st.json(rows[:3])


def render_text_paste():
    """Render text paste interface."""
    st.markdown("""
    Copy and paste the text from your document. We'll extract the structured data from it.
    """)
    
    pasted_text = st.text_area(
        "Paste your document text here",
        height=300,
        placeholder="Paste the full text of your EOB or itemized bill...",
        help="Include all details: dates, codes, amounts, provider names",
        label_visibility="collapsed"
    )
    
    if pasted_text and len(pasted_text.strip()) > 50:
        st.session_state.import_data = {
            'method': 'text_paste',
            'file_type': 'text',
            'raw_text': pasted_text,
            'status': 'ready'
        }
        
        st.success(f"✅ Text captured ({len(pasted_text)} characters)")


def extract_and_normalize_data():
    """Extract structured data from import input and normalize to line items.
    
    This is a placeholder that demonstrates the extraction flow.
    In production, this would integrate with your existing extraction pipeline.
    """
    import_data = st.session_state.import_data
    
    # Mock extraction - in production, integrate with your extraction agents
    line_items: List[NormalizedLineItem] = []
    
    if import_data.get('file_type') == 'csv' and import_data.get('rows'):
        # Parse CSV rows
        for row in import_data['rows']:
            line_item: NormalizedLineItem = {
                'line_item_id': f"item_{datetime.utcnow().timestamp()}_{len(line_items)}",
                'import_job_id': '',  # Will be set when job is created
                'service_date': row.get('Date of Service', row.get('date', '')),
                'procedure_code': row.get('Procedure Code', row.get('code', '')),
                'procedure_description': row.get('Description', row.get('description', '')),
                'provider_name': row.get('Provider', row.get('provider_name', '')),
                'provider_npi': row.get('NPI', None),
                'billed_amount': float(row.get('Billed Amount', row.get('billed', 0))),
                'allowed_amount': float(row.get('Allowed Amount', row.get('allowed', 0))),
                'paid_by_insurance': float(row.get('Paid by Insurance', row.get('insurance_paid', 0))),
                'patient_responsibility': float(row.get('Patient Responsibility', row.get('patient_resp', 0))),
                'claim_number': row.get('Claim Number', None),
                'created_at': datetime.utcnow().isoformat()
            }
            line_items.append(line_item)
    
    elif import_data.get('raw_text'):
        # Mock text extraction - in production, use your extraction agent
        # For demo, create a sample line item
        line_item: NormalizedLineItem = {
            'line_item_id': f"item_{datetime.utcnow().timestamp()}",
            'import_job_id': '',
            'service_date': datetime.now().date().isoformat(),
            'procedure_code': '99213',
            'procedure_description': 'Office visit (extracted from text)',
            'provider_name': 'Sample Provider',
            'provider_npi': None,
            'billed_amount': 150.0,
            'allowed_amount': 120.0,
            'paid_by_insurance': 96.0,
            'patient_responsibility': 24.0,
            'claim_number': None,
            'created_at': datetime.utcnow().isoformat()
        }
        line_items.append(line_item)
    
    st.session_state.pending_line_items = line_items


# ==============================================================================
# IMPORTER - WIZARD STEP 3: PREVIEW & EDIT
# ==============================================================================

def render_importer_step3():
    """Render Step 3: Preview extracted data and allow inline edits."""
    st.subheader("Step 3: Review & Edit Extracted Data")
    
    line_items = st.session_state.pending_line_items
    
    if not line_items:
        st.warning("⚠️ No data extracted. Please go back and try again.")
        if st.button("← Back to Input"):
            st.session_state.import_wizard_step = 2
            st.rerun()
        return
    
    st.success(f"✅ Extracted {len(line_items)} line item(s)")
    
    st.markdown("""
    Review the extracted data below. You can edit any field inline before saving.
    Click on cells to make corrections.
    """)
    
    # Editable table
    for idx, item in enumerate(line_items):
        with st.expander(f"Line Item {idx + 1}: {item.get('procedure_description', 'Unknown')}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                service_date = st.date_input(
                    "Service Date",
                    value=datetime.fromisoformat(item['service_date']) if item.get('service_date') else datetime.now(),
                    key=f"date_{idx}"
                )
                item['service_date'] = service_date.isoformat()
                
                procedure_code = st.text_input(
                    "Procedure Code",
                    value=item.get('procedure_code', ''),
                    key=f"code_{idx}"
                )
                item['procedure_code'] = procedure_code
                
                procedure_desc = st.text_input(
                    "Description",
                    value=item.get('procedure_description', ''),
                    key=f"desc_{idx}"
                )
                item['procedure_description'] = procedure_desc
                
                provider_name = st.text_input(
                    "Provider Name",
                    value=item.get('provider_name', ''),
                    key=f"prov_{idx}"
                )
                item['provider_name'] = provider_name
            
            with col2:
                billed = st.number_input(
                    "Billed Amount ($)",
                    value=float(item.get('billed_amount', 0)),
                    min_value=0.0,
                    step=0.01,
                    key=f"billed_{idx}"
                )
                item['billed_amount'] = billed
                
                allowed = st.number_input(
                    "Allowed Amount ($)",
                    value=float(item.get('allowed_amount', 0)),
                    min_value=0.0,
                    step=0.01,
                    key=f"allowed_{idx}"
                )
                item['allowed_amount'] = allowed
                
                ins_paid = st.number_input(
                    "Paid by Insurance ($)",
                    value=float(item.get('paid_by_insurance', 0)),
                    min_value=0.0,
                    step=0.01,
                    key=f"inspaid_{idx}"
                )
                item['paid_by_insurance'] = ins_paid
                
                patient_resp = st.number_input(
                    "Patient Responsibility ($)",
                    value=float(item.get('patient_responsibility', 0)),
                    min_value=0.0,
                    step=0.01,
                    key=f"patresp_{idx}"
                )
                item['patient_responsibility'] = patient_resp
    
    # Update session state with edited items
    st.session_state.pending_line_items = line_items
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back to Input"):
            st.session_state.import_wizard_step = 2
            st.rerun()
    
    with col2:
        if st.button("💾 Save & Complete Import", type="primary"):
            save_import_job()
            st.session_state.import_wizard_step = 4
            st.rerun()


def save_import_job():
    """Save the import job and normalized line items to disk."""
    import_data = st.session_state.import_data
    line_items = st.session_state.pending_line_items
    
    # Create import job
    job_id = f"job_{datetime.utcnow().timestamp()}"
    
    # Update line items with job ID
    for item in line_items:
        item['import_job_id'] = job_id
    
    # Create document record
    document: Document = {
        'document_id': f"doc_{datetime.utcnow().timestamp()}",
        'import_job_id': job_id,
        'file_name': import_data.get('file_name', 'pasted_text'),
        'file_path': import_data.get('file_path', ''),
        'file_type': import_data.get('file_type', 'text'),
        'raw_text': import_data.get('raw_text'),
        'status': import_data.get('status', 'completed'),
        'created_at': datetime.utcnow().isoformat()
    }
    
    # Create job record
    job: ImportJob = {
        'job_id': job_id,
        'source_type': st.session_state.import_source_type,
        'source_method': import_data.get('method', 'unknown'),
        'status': 'completed',
        'documents': [document],
        'line_items': line_items,
        'created_at': datetime.utcnow().isoformat(),
        'completed_at': datetime.utcnow().isoformat(),
        'error_message': None
    }
    
    # Load existing data
    jobs = load_import_jobs()
    all_line_items = load_line_items()
    
    # Append new data
    jobs.append(job)
    all_line_items.extend(line_items)
    
    # Save to disk
    save_import_jobs(jobs)
    save_line_items(all_line_items)


# ==============================================================================
# IMPORTER - WIZARD STEP 4: SUCCESS
# ==============================================================================

def render_importer_step4():
    """Render Step 4: Success confirmation."""
    st.subheader("✅ Import Complete!")
    
    line_items = st.session_state.pending_line_items
    
    st.success(f"""
    Successfully imported {len(line_items)} line item(s)!
    
    Your data has been normalized and saved. You can now:
    - View imported items in your profile overview
    - Use this data for analysis in medBillDozer
    - Import additional documents
    """)
    
    st.balloons()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Import More Data", use_container_width=True, type="primary"):
            # Reset wizard
            st.session_state.import_wizard_step = 1
            st.session_state.import_source_type = None
            st.session_state.import_data = None
            st.session_state.pending_line_items = []
            st.rerun()
    
    with col2:
        if st.button("← Back to Profile", use_container_width=True):
            # Reset wizard
            st.session_state.import_wizard_step = 1
            st.session_state.import_source_type = None
            st.session_state.import_data = None
            st.session_state.pending_line_items = []
            st.session_state.profile_page = 'overview'
            st.rerun()


# ==============================================================================
# IMPORTER ORCHESTRATOR
# ==============================================================================

def render_importer():
    """Render importer wizard based on current step."""
    st.header("📥 Data Importer")
    
    # Progress indicator
    step = st.session_state.import_wizard_step
    
    progress_cols = st.columns(4)
    steps = [
        ("1️⃣", "Choose Source"),
        ("2️⃣", "Provide Data"),
        ("3️⃣", "Review & Edit"),
        ("4️⃣", "Complete")
    ]
    
    for idx, (emoji, label) in enumerate(steps, 1):
        with progress_cols[idx - 1]:
            if idx < step:
                st.markdown(f"### ✅ {label}")
            elif idx == step:
                st.markdown(f"### {emoji} **{label}**")
            else:
                st.markdown(f"### ⚪ {label}")
    
    st.markdown("---")
    
    # Render appropriate step
    if step == 1:
        render_importer_step1()
    elif step == 2:
        render_importer_step2()
    elif step == 3:
        render_importer_step3()
    elif step == 4:
        render_importer_step4()


# ==============================================================================
# MAIN PROFILE EDITOR RENDERER
# ==============================================================================

def render_profile_editor():
    """Main entry point for profile editor interface.
    
    Provides navigation between different profile sections and
    the data importer wizard.
    """
    # Check if feature is enabled
    if not is_profile_editor_enabled():
        st.info("📋 Profile Editor is not enabled. Set PROFILE_EDITOR_ENABLED=true to use this feature.")
        return
    
    # Initialize session state
    initialize_profile_state()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 📋 Profile Sections")
        
        pages = {
            'overview': '🏠 Overview',
            'identity': '👤 Identity',
            'insurance': '🏥 Insurance',
            'providers': '👨‍⚕️ Providers'
        }
        
        if is_importer_enabled():
            pages['importer'] = '📥 Import Data'
        
        for page_key, page_label in pages.items():
            if st.button(
                page_label,
                use_container_width=True,
                type="primary" if st.session_state.profile_page == page_key else "secondary"
            ):
                st.session_state.profile_page = page_key
                if page_key == 'importer':
                    st.session_state.import_wizard_step = 1
                st.rerun()
    
    # Render selected page
    page = st.session_state.profile_page
    
    if page == 'overview':
        render_profile_overview()
    elif page == 'identity':
        render_identity_editor()
    elif page == 'insurance':
        render_insurance_editor()
    elif page == 'providers':
        render_provider_editor()
    elif page == 'importer':
        render_importer()
