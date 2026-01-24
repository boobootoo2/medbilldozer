"""Health profile management for policy holder and dependents.

Provides pre-loaded patient profiles with medical history, insurance details,
and demographic information for demo and testing purposes.
"""
import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime


# ==================================================
# Profile Data
# ==================================================

SAMPLE_PROFILES = {
    "policyholder": {
        "id": "PH-001",
        "name": "John Sample",
        "date_of_birth": "01/15/1975",
        "age": 51,
        "gender": "Male",
        "relationship": "Policy Holder",
        
        # Insurance Information
        "insurance": {
            "provider": "Horizon PPO Plus",
            "member_id": "HPP-8743920",
            "group_number": "G-1234567",
            "plan_type": "PPO",
            "effective_date": "01/01/2025",
            "deductible_annual": 1500.00,
            "deductible_met": 1500.00,
            "oop_max": 3000.00,
            "oop_met": 1500.00,
        },
        
        # Medical History
        "medical_history": {
            "conditions": [
                "Hypertension (controlled)",
                "Type 2 Diabetes",
                "Hyperlipidemia",
            ],
            "medications": [
                "Lisinopril 10mg daily",
                "Metformin 500mg twice daily",
                "Atorvastatin 20mg at bedtime",
            ],
            "allergies": [
                "Penicillin (rash)",
                "Sulfa drugs (hives)",
            ],
            "recent_procedures": [
                {
                    "date": "01/12/2026",
                    "procedure": "Screening Colonoscopy",
                    "provider": "Valley Medical Center",
                    "cpt_code": "45378",
                    "cost": 1200.00,
                    "out_of_pocket": 100.00,
                },
                {
                    "date": "11/05/2025",
                    "procedure": "Annual Physical Exam",
                    "provider": "Dr. Sarah Mitchell",
                    "cpt_code": "99396",
                    "cost": 350.00,
                    "out_of_pocket": 0.00,
                },
            ],
            "upcoming_appointments": [
                {
                    "date": "03/15/2026",
                    "type": "Follow-up",
                    "provider": "Dr. Michael Reynolds",
                    "reason": "Post-colonoscopy review",
                },
            ],
        },
        
        # FSA/HSA Information
        "fsa_hsa": {
            "account_type": "FSA",
            "plan_year": 2026,
            "annual_contribution": 2850.00,
            "balance_remaining": 2247.50,
            "claims_submitted": 5,
            "claims_approved": 4,
            "claims_pending": 0,
            "claims_denied": 1,
        },
    },
    
    "dependent": {
        "id": "DEP-001",
        "name": "Jane Sample",
        "date_of_birth": "08/22/1986",
        "age": 39,
        "gender": "Female",
        "relationship": "Spouse",
        
        # Insurance Information (covered under policy holder's plan)
        "insurance": {
            "provider": "Horizon PPO Plus",
            "member_id": "HPP-8743921",
            "group_number": "G-1234567",
            "plan_type": "PPO",
            "effective_date": "01/01/2025",
            "deductible_annual": 1500.00,
            "deductible_met": 450.00,
            "oop_max": 3000.00,
            "oop_met": 850.00,
        },
        
        # Medical History
        "medical_history": {
            "conditions": [
                "Seasonal Allergies",
                "Mild Asthma (controlled)",
            ],
            "medications": [
                "Cetirizine 10mg as needed",
                "Albuterol inhaler as needed",
                "Multivitamin daily",
            ],
            "allergies": [
                "Shellfish (anaphylaxis)",
                "Cat dander",
            ],
            "recent_procedures": [
                {
                    "date": "01/20/2026",
                    "procedure": "Dental Crown (Tooth #14)",
                    "provider": "BrightSmile Dental",
                    "cdt_code": "D2740",
                    "cost": 2500.00,
                    "out_of_pocket": 1625.00,
                },
                {
                    "date": "01/18/2026",
                    "procedure": "Prescription Refill",
                    "provider": "GreenLeaf Pharmacy",
                    "medication": "Albuterol Inhaler",
                    "cost": 45.00,
                    "out_of_pocket": 15.00,
                },
                {
                    "date": "10/12/2025",
                    "procedure": "Annual Gynecological Exam",
                    "provider": "Dr. Jennifer Adams",
                    "cpt_code": "99385",
                    "cost": 285.00,
                    "out_of_pocket": 0.00,
                },
            ],
            "upcoming_appointments": [
                {
                    "date": "02/28/2026",
                    "type": "Dental Follow-up",
                    "provider": "Dr. Laura Chen, DDS",
                    "reason": "Crown check-up",
                },
                {
                    "date": "04/10/2026",
                    "type": "Annual Physical",
                    "provider": "Dr. Sarah Mitchell",
                    "reason": "Preventive care",
                },
            ],
        },
        
        # FSA/HSA Information (shared family account)
        "fsa_hsa": {
            "account_type": "FSA",
            "plan_year": 2026,
            "annual_contribution": 2850.00,
            "balance_remaining": 2247.50,
            "claims_submitted": 5,
            "claims_approved": 4,
            "claims_pending": 0,
            "claims_denied": 1,
        },
    },
}


# ==================================================
# Profile Rendering Functions
# ==================================================

def render_profile_selector():
    """Render profile selection dropdown.
    
    Returns:
        str: Selected profile key ('policyholder', 'dependent', or None)
    """
    st.markdown("### 👤 Health Profile")
    
    profile_options = {
        "": "-- Select a Profile --",
        "policyholder": "🔷 John Sample (Policy Holder)",
        "dependent": "🔶 Jane Sample (Dependent - Spouse)",
    }
    
    selected = st.selectbox(
        "Load a pre-configured profile:",
        options=list(profile_options.keys()),
        format_func=lambda x: profile_options[x],
        key="profile_selector",
    )
    
    return selected if selected else None


def render_profile_details(profile_key: str):
    """Render detailed profile information in expandable sections.
    
    Args:
        profile_key: Profile key ('policyholder' or 'dependent')
    """
    if profile_key not in SAMPLE_PROFILES:
        st.warning("⚠️ Profile not found")
        return
    
    profile = SAMPLE_PROFILES[profile_key]
    
    # Basic Information
    with st.expander("📋 Basic Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Name:** {profile['name']}")
            st.markdown(f"**Date of Birth:** {profile['date_of_birth']}")
            st.markdown(f"**Age:** {profile['age']}")
        with col2:
            st.markdown(f"**Gender:** {profile['gender']}")
            st.markdown(f"**Relationship:** {profile['relationship']}")
            st.markdown(f"**ID:** {profile['id']}")
    
    # Insurance Information
    with st.expander("🏥 Insurance Information"):
        ins = profile['insurance']
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Provider:** {ins['provider']}")
            st.markdown(f"**Member ID:** {ins['member_id']}")
            st.markdown(f"**Group Number:** {ins['group_number']}")
            st.markdown(f"**Plan Type:** {ins['plan_type']}")
        with col2:
            st.markdown(f"**Effective Date:** {ins['effective_date']}")
            st.markdown(f"**Annual Deductible:** ${ins['deductible_annual']:,.2f}")
            st.markdown(f"**Deductible Met:** ${ins['deductible_met']:,.2f}")
            st.markdown(f"**Out-of-Pocket Max:** ${ins['oop_max']:,.2f}")
            st.markdown(f"**OOP Met:** ${ins['oop_met']:,.2f}")
    
    # Medical History
    with st.expander("🩺 Medical History"):
        med = profile['medical_history']
        
        st.markdown("**Conditions:**")
        for condition in med['conditions']:
            st.markdown(f"- {condition}")
        
        st.markdown("**Current Medications:**")
        for medication in med['medications']:
            st.markdown(f"- {medication}")
        
        st.markdown("**Allergies:**")
        for allergy in med['allergies']:
            st.markdown(f"- ⚠️ {allergy}")
    
    # Recent Procedures
    with st.expander("📅 Recent Procedures"):
        med = profile['medical_history']
        if med['recent_procedures']:
            for proc in med['recent_procedures']:
                st.markdown(f"**{proc['date']} - {proc['procedure']}**")
                st.markdown(f"Provider: {proc['provider']}")
                if 'cpt_code' in proc:
                    st.markdown(f"CPT Code: {proc['cpt_code']}")
                elif 'cdt_code' in proc:
                    st.markdown(f"CDT Code: {proc['cdt_code']}")
                elif 'medication' in proc:
                    st.markdown(f"Medication: {proc['medication']}")
                st.markdown(f"Cost: ${proc['cost']:,.2f} | Out-of-Pocket: ${proc['out_of_pocket']:,.2f}")
                st.markdown("---")
        else:
            st.info("No recent procedures recorded")
    
    # Upcoming Appointments
    with st.expander("📆 Upcoming Appointments"):
        med = profile['medical_history']
        if med['upcoming_appointments']:
            for apt in med['upcoming_appointments']:
                st.markdown(f"**{apt['date']} - {apt['type']}**")
                st.markdown(f"Provider: {apt['provider']}")
                st.markdown(f"Reason: {apt['reason']}")
                st.markdown("---")
        else:
            st.info("No upcoming appointments scheduled")
    
    # FSA/HSA Information
    with st.expander("💰 FSA/HSA Account"):
        fsa = profile['fsa_hsa']
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Account Type:** {fsa['account_type']}")
            st.markdown(f"**Plan Year:** {fsa['plan_year']}")
            st.markdown(f"**Annual Contribution:** ${fsa['annual_contribution']:,.2f}")
            st.markdown(f"**Balance Remaining:** ${fsa['balance_remaining']:,.2f}")
        with col2:
            st.markdown(f"**Claims Submitted:** {fsa['claims_submitted']}")
            st.markdown(f"**Claims Approved:** {fsa['claims_approved']}")
            st.markdown(f"**Claims Pending:** {fsa['claims_pending']}")
            st.markdown(f"**Claims Denied:** {fsa['claims_denied']}")


def get_profile_data(profile_key: str) -> Optional[Dict]:
    """Get profile data by key.
    
    Args:
        profile_key: Profile key ('policyholder' or 'dependent')
    
    Returns:
        Dict with profile data or None if not found
    """
    return SAMPLE_PROFILES.get(profile_key)


def get_profile_context_for_analysis(profile_key: str) -> str:
    """Generate context string for LLM analysis based on profile.
    
    Args:
        profile_key: Profile key ('policyholder' or 'dependent')
    
    Returns:
        str: Formatted context string
    """
    profile = get_profile_data(profile_key)
    if not profile:
        return ""
    
    ins = profile['insurance']
    med = profile['medical_history']
    
    context = f"""
PATIENT PROFILE CONTEXT:
Name: {profile['name']}
Age: {profile['age']} | Gender: {profile['gender']}
Relationship: {profile['relationship']}

INSURANCE:
Provider: {ins['provider']}
Plan: {ins['plan_type']}
Annual Deductible: ${ins['deductible_annual']:,.2f} (${ins['deductible_met']:,.2f} met)
Out-of-Pocket Maximum: ${ins['oop_max']:,.2f} (${ins['oop_met']:,.2f} met)

MEDICAL CONDITIONS: {', '.join(med['conditions'])}
CURRENT MEDICATIONS: {', '.join(med['medications'])}
ALLERGIES: {', '.join(med['allergies'])}

This context may help identify coverage issues, medication-related charges,
or procedure appropriateness based on the patient's medical history.
"""
    return context
