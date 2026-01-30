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
            "in_network_providers": [
                "Valley Medical Center",
                "Dr. Sarah Mitchell",
                "Dr. Michael Reynolds",
                "HealthFirst Medical Group",
                "BrightSmile Dental",
                "Dr. Laura Chen, DDS",
            ],
            "out_of_network_providers": [
                "GreenLeaf Pharmacy",
                "QuickCare Urgent Care",
            ],
            "in_network_codes": [
                {"code": "99213", "description": "Office Visit - Established Patient (15 min)", "accepted_fee": 125.00},
                {"code": "99214", "description": "Office Visit - Established Patient (25 min)", "accepted_fee": 185.00},
                {"code": "99215", "description": "Office Visit - Established Patient (40 min)", "accepted_fee": 245.00},
                {"code": "45378", "description": "Colonoscopy - Diagnostic", "accepted_fee": 1200.00},
                {"code": "80053", "description": "Comprehensive Metabolic Panel", "accepted_fee": 45.00},
                {"code": "85025", "description": "Complete Blood Count (CBC)", "accepted_fee": 35.00},
                {"code": "93000", "description": "Electrocardiogram (EKG)", "accepted_fee": 85.00},
                {"code": "71045", "description": "Chest X-Ray - Single View", "accepted_fee": 120.00},
            ],
            "out_of_network_codes": [
                {"code": "99213", "description": "Office Visit - Established Patient (15 min)", "accepted_fee": 100.00},
                {"code": "99214", "description": "Office Visit - Established Patient (25 min)", "accepted_fee": 148.00},
                {"code": "99215", "description": "Office Visit - Established Patient (40 min)", "accepted_fee": 196.00},
                {"code": "45378", "description": "Colonoscopy - Diagnostic", "accepted_fee": 960.00},
                {"code": "80053", "description": "Comprehensive Metabolic Panel", "accepted_fee": 36.00},
                {"code": "85025", "description": "Complete Blood Count (CBC)", "accepted_fee": 28.00},
                {"code": "93000", "description": "Electrocardiogram (EKG)", "accepted_fee": 68.00},
                {"code": "71045", "description": "Chest X-Ray - Single View", "accepted_fee": 96.00},
            ],
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
            "eligible_expenses": [
                "Medical copays and deductibles",
                "Prescription medications",
                "Dental treatments and cleanings",
                "Vision exams and eyeglasses",
                "Contact lenses and solution",
                "Over-the-counter medications (with prescription)",
                "Medical equipment (blood pressure monitors, diabetic supplies)",
                "Physical therapy copays",
                "Chiropractic services",
                "Mental health services",
                "Laboratory tests and diagnostic services",
                "Hearing aids and batteries",
                "Orthodontia (braces)",
                "Wheelchair and mobility aids",
                "First aid supplies",
                "Sunscreen (SPF 15+)",
                "Prenatal vitamins (with prescription)",
                "Smoking cessation programs",
                "Weight loss programs (for specific medical conditions)",
            ],
            "ineligible_expenses": [
                "Vitamins and supplements (without prescription)",
                "Cosmetic procedures",
                "Gym memberships (unless prescribed)",
                "Health club dues",
                "Cosmetic dentistry (teeth whitening)",
                "Hair transplants",
                "Nutritional supplements",
            ],
        },

        # Stored Receipts (for analysis context)
        "stored_receipts": [
            {
                "id": "RCP-001",
                "date": "01/12/2026",
                "provider": "Valley Medical Center",
                "service": "Screening Colonoscopy",
                "cpt_code": "45378",
                "billed_amount": 1450.00,
                "insurance_paid": 1100.00,
                "patient_paid": 100.00,
                "status": "Paid",
                "notes": "Billed $250 over in-network accepted fee of $1200",
            },
            {
                "id": "RCP-002",
                "date": "11/05/2025",
                "provider": "Dr. Sarah Mitchell",
                "service": "Annual Physical Exam",
                "cpt_code": "99396",
                "billed_amount": 350.00,
                "insurance_paid": 350.00,
                "patient_paid": 0.00,
                "status": "Paid",
                "notes": "Preventive care - 100% covered",
            },
            {
                "id": "RCP-003",
                "date": "12/15/2025",
                "provider": "GreenLeaf Pharmacy",
                "service": "Metformin 500mg (90-day supply)",
                "ndc_code": "00093-7214-01",
                "billed_amount": 85.00,
                "insurance_paid": 68.00,
                "patient_paid": 17.00,
                "status": "Paid",
                "notes": "Out-of-network pharmacy - 80% reimbursement",
            },
            {
                "id": "RCP-004",
                "date": "10/22/2025",
                "provider": "Valley Medical Center Lab",
                "service": "Comprehensive Metabolic Panel",
                "cpt_code": "80053",
                "billed_amount": 65.00,
                "insurance_paid": 45.00,
                "patient_paid": 0.00,
                "status": "Paid",
                "notes": "Billed $20 over accepted fee - deductible already met",
            },
            {
                "id": "RCP-005",
                "date": "09/18/2025",
                "provider": "Dr. Michael Reynolds",
                "service": "Follow-up Visit - Diabetes Management",
                "cpt_code": "99214",
                "billed_amount": 220.00,
                "insurance_paid": 185.00,
                "patient_paid": 35.00,
                "status": "Paid",
                "notes": "Overcharged $35 - accepted fee is $185",
            },
            {
                "id": "RCP-006",
                "date": "08/30/2025",
                "provider": "HealthFirst Medical Group",
                "service": "Chest X-Ray - Single View",
                "cpt_code": "71045",
                "billed_amount": 180.00,
                "insurance_paid": 120.00,
                "patient_paid": 60.00,
                "status": "Paid",
                "notes": "Overcharged $60 - in-network accepted fee is $120",
            },
            {
                "id": "RCP-007",
                "date": "07/14/2025",
                "provider": "QuickCare Urgent Care",
                "service": "Urgent Care Visit - Minor Injury",
                "cpt_code": "99213",
                "billed_amount": 175.00,
                "insurance_paid": 80.00,
                "patient_paid": 95.00,
                "status": "Paid",
                "notes": "Out-of-network - Patient balance billed $75 over accepted fee",
            },
            {
                "id": "RCP-008",
                "date": "06/05/2025",
                "provider": "Valley Medical Center Lab",
                "service": "Complete Blood Count (CBC)",
                "cpt_code": "85025",
                "billed_amount": 55.00,
                "insurance_paid": 35.00,
                "patient_paid": 0.00,
                "status": "Paid",
                "notes": "Billed $20 over in-network accepted fee of $35",
            },
            {
                "id": "RCP-009",
                "date": "05/20/2025",
                "provider": "Dr. Sarah Mitchell",
                "service": "Office Visit - Hypertension Check",
                "cpt_code": "99213",
                "billed_amount": 125.00,
                "insurance_paid": 125.00,
                "patient_paid": 0.00,
                "status": "Paid",
                "notes": "Correctly billed at in-network accepted fee",
            },
            {
                "id": "RCP-010",
                "date": "04/10/2025",
                "provider": "Valley Medical Center",
                "service": "Electrocardiogram (EKG)",
                "cpt_code": "93000",
                "billed_amount": 135.00,
                "insurance_paid": 85.00,
                "patient_paid": 50.00,
                "status": "Paid",
                "notes": "Overcharged $50 - in-network accepted fee is $85",
            },
        ],
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
            "in_network_providers": [
                "Valley Medical Center",
                "Dr. Sarah Mitchell",
                "Dr. Michael Reynolds",
                "HealthFirst Medical Group",
                "BrightSmile Dental",
                "Dr. Laura Chen, DDS",
                "Dr. Jennifer Adams",
            ],
            "out_of_network_providers": [
                "GreenLeaf Pharmacy",
                "QuickCare Urgent Care",
            ],
            "in_network_codes": [
                {"code": "99213", "description": "Office Visit - Established Patient (15 min)", "accepted_fee": 125.00},
                {"code": "99214", "description": "Office Visit - Established Patient (25 min)", "accepted_fee": 185.00},
                {"code": "99215", "description": "Office Visit - Established Patient (40 min)", "accepted_fee": 245.00},
                {"code": "45378", "description": "Colonoscopy - Diagnostic", "accepted_fee": 1200.00},
                {"code": "80053", "description": "Comprehensive Metabolic Panel", "accepted_fee": 45.00},
                {"code": "85025", "description": "Complete Blood Count (CBC)", "accepted_fee": 35.00},
                {"code": "93000", "description": "Electrocardiogram (EKG)", "accepted_fee": 85.00},
                {"code": "71045", "description": "Chest X-Ray - Single View", "accepted_fee": 120.00},
            ],
            "out_of_network_codes": [
                {"code": "99213", "description": "Office Visit - Established Patient (15 min)", "accepted_fee": 100.00},
                {"code": "99214", "description": "Office Visit - Established Patient (25 min)", "accepted_fee": 148.00},
                {"code": "99215", "description": "Office Visit - Established Patient (40 min)", "accepted_fee": 196.00},
                {"code": "45378", "description": "Colonoscopy - Diagnostic", "accepted_fee": 960.00},
                {"code": "80053", "description": "Comprehensive Metabolic Panel", "accepted_fee": 36.00},
                {"code": "85025", "description": "Complete Blood Count (CBC)", "accepted_fee": 28.00},
                {"code": "93000", "description": "Electrocardiogram (EKG)", "accepted_fee": 68.00},
                {"code": "71045", "description": "Chest X-Ray - Single View", "accepted_fee": 96.00},
            ],
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
            "eligible_expenses": [
                "Medical copays and deductibles",
                "Prescription medications",
                "Dental treatments and cleanings",
                "Vision exams and eyeglasses",
                "Contact lenses and solution",
                "Over-the-counter medications (with prescription)",
                "Medical equipment (blood pressure monitors, diabetic supplies)",
                "Physical therapy copays",
                "Chiropractic services",
                "Mental health services",
                "Laboratory tests and diagnostic services",
                "Hearing aids and batteries",
                "Orthodontia (braces)",
                "Wheelchair and mobility aids",
                "First aid supplies",
                "Sunscreen (SPF 15+)",
                "Prenatal vitamins (with prescription)",
                "Smoking cessation programs",
                "Weight loss programs (for specific medical conditions)",
            ],
            "ineligible_expenses": [
                "Vitamins and supplements (without prescription)",
                "Cosmetic procedures",
                "Gym memberships (unless prescribed)",
                "Health club dues",
                "Cosmetic dentistry (teeth whitening)",
                "Hair transplants",
                "Nutritional supplements",
            ],
        },

        # Stored Receipts (for analysis context)
        "stored_receipts": [
            {
                "id": "RCP-D001",
                "date": "01/20/2026",
                "provider": "BrightSmile Dental",
                "service": "Dental Crown (Tooth #14)",
                "cdt_code": "D2740",
                "billed_amount": 2500.00,
                "insurance_paid": 875.00,
                "patient_paid": 1625.00,
                "status": "Paid",
                "notes": "35% dental coverage - remaining balance paid out-of-pocket",
            },
            {
                "id": "RCP-D002",
                "date": "01/18/2026",
                "provider": "GreenLeaf Pharmacy",
                "service": "Albuterol Inhaler (90mcg)",
                "ndc_code": "59310-579-18",
                "billed_amount": 55.00,
                "insurance_paid": 40.00,
                "patient_paid": 15.00,
                "status": "Paid",
                "notes": "Out-of-network pharmacy - 80% reimbursement after copay",
            },
            {
                "id": "RCP-D003",
                "date": "12/28/2025",
                "provider": "Dr. Laura Chen, DDS",
                "service": "Dental Cleaning & Exam",
                "cdt_code": "D1110,D0150",
                "billed_amount": 225.00,
                "insurance_paid": 225.00,
                "patient_paid": 0.00,
                "status": "Paid",
                "notes": "Preventive dental - 100% covered",
            },
            {
                "id": "RCP-D004",
                "date": "11/15/2025",
                "provider": "Valley Medical Center Lab",
                "service": "Allergy Panel (Comprehensive)",
                "cpt_code": "86003",
                "billed_amount": 385.00,
                "insurance_paid": 308.00,
                "patient_paid": 77.00,
                "status": "Paid",
                "notes": "80% coverage after deductible",
            },
            {
                "id": "RCP-D005",
                "date": "10/12/2025",
                "provider": "Dr. Jennifer Adams",
                "service": "Annual Gynecological Exam",
                "cpt_code": "99385",
                "billed_amount": 285.00,
                "insurance_paid": 285.00,
                "patient_paid": 0.00,
                "status": "Paid",
                "notes": "Preventive care - 100% covered",
            },
            {
                "id": "RCP-D006",
                "date": "09/08/2025",
                "provider": "HealthFirst Medical Group",
                "service": "Asthma Management Visit",
                "cpt_code": "99214",
                "billed_amount": 210.00,
                "insurance_paid": 185.00,
                "patient_paid": 25.00,
                "status": "Paid",
                "notes": "Overcharged $25 - in-network accepted fee is $185",
            },
            {
                "id": "RCP-D007",
                "date": "08/14/2025",
                "provider": "QuickCare Urgent Care",
                "service": "Urgent Care Visit - Allergic Reaction",
                "cpt_code": "99213",
                "billed_amount": 195.00,
                "insurance_paid": 80.00,
                "patient_paid": 115.00,
                "status": "Paid",
                "notes": "Out-of-network - Balance billed $95 over accepted fee",
            },
            {
                "id": "RCP-D008",
                "date": "07/20/2025",
                "provider": "GreenLeaf Pharmacy",
                "service": "Cetirizine 10mg (90-day supply)",
                "ndc_code": "63868-0986-90",
                "billed_amount": 45.00,
                "insurance_paid": 36.00,
                "patient_paid": 9.00,
                "status": "Paid",
                "notes": "Out-of-network - 80% reimbursement",
            },
            {
                "id": "RCP-D009",
                "date": "06/10/2025",
                "provider": "Valley Medical Center",
                "service": "Pulmonary Function Test",
                "cpt_code": "94060",
                "billed_amount": 275.00,
                "insurance_paid": 220.00,
                "patient_paid": 55.00,
                "status": "Paid",
                "notes": "Overcharged - typical in-network fee is $220",
            },
            {
                "id": "RCP-D010",
                "date": "05/05/2025",
                "provider": "Dr. Sarah Mitchell",
                "service": "Office Visit - Follow-up",
                "cpt_code": "99213",
                "billed_amount": 125.00,
                "insurance_paid": 125.00,
                "patient_paid": 0.00,
                "status": "Paid",
                "notes": "Correctly billed at in-network accepted fee",
            },
        ],
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


def render_receipt_uploader():
    """Render receipt upload interface with session storage.
    
    Allows users to upload receipt images/PDFs and stores them in session state
    for use in analysis context.
    """
    st.markdown("### 🧾 Import Receipts")
    
    # Initialize session state for receipts if not exists
    if 'uploaded_receipts' not in st.session_state:
        st.session_state.uploaded_receipts = []
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload medical receipts (PDF, PNG, JPG)",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="Upload receipts to add context for analysis. Images will be stored in session.",
        key="receipt_uploader"
    )
    
    # Process uploaded files
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Check if file already exists in session
            file_exists = any(
                r['name'] == uploaded_file.name 
                for r in st.session_state.uploaded_receipts
            )
            
            if not file_exists:
                # Read file bytes
                file_bytes = uploaded_file.read()
                
                # Store in session state
                receipt_data = {
                    'name': uploaded_file.name,
                    'type': uploaded_file.type,
                    'size': len(file_bytes),
                    'bytes': file_bytes,
                    'uploaded_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.uploaded_receipts.append(receipt_data)
    
    # Display uploaded receipts
    if st.session_state.uploaded_receipts:
        st.markdown(f"**📎 {len(st.session_state.uploaded_receipts)} receipt(s) uploaded**")
        
        # Show receipts in expander
        with st.expander("View Uploaded Receipts", expanded=False):
            for idx, receipt in enumerate(st.session_state.uploaded_receipts):
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{receipt['name']}**")
                
                with col2:
                    size_kb = receipt['size'] / 1024
                    st.markdown(f"*{size_kb:.1f} KB*")
                
                with col3:
                    if st.button("🗑️", key=f"delete_receipt_{idx}", help="Delete receipt"):
                        st.session_state.uploaded_receipts.pop(idx)
                        st.rerun()
                
                st.markdown(f"Uploaded: {receipt['uploaded_at']}")
                st.markdown("---")
        
        # Clear all button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🗑️ Clear All", help="Remove all uploaded receipts"):
                st.session_state.uploaded_receipts = []
                st.rerun()
    else:
        st.info("💡 Upload receipts to enhance analysis with historical billing context")


def get_uploaded_receipts_context() -> str:
    """Generate context string for uploaded receipts.
    
    Returns:
        str: Formatted context string for LLM analysis
    """
    if 'uploaded_receipts' not in st.session_state or not st.session_state.uploaded_receipts:
        return ""
    
    context = "\n========================================\n"
    context += "UPLOADED RECEIPTS\n"
    context += "========================================\n"
    context += f"Total Uploaded Files: {len(st.session_state.uploaded_receipts)}\n\n"
    context += "The user has uploaded the following receipt files for reference:\n"
    
    for idx, receipt in enumerate(st.session_state.uploaded_receipts, 1):
        context += f"{idx}. {receipt['name']} ({receipt['size']/1024:.1f} KB)\n"
        context += f"   Type: {receipt['type']}\n"
        context += f"   Uploaded: {receipt['uploaded_at']}\n"
    
    context += "\nNote: These receipts are available in session storage and can be referenced "
    context += "when analyzing new bills for pattern detection and comparison.\n"
    
    return context


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

        st.markdown("---")

        # Network Providers
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🟢 In-Network Providers:**")
            for provider in ins.get('in_network_providers', []):
                st.markdown(f"✓ {provider}")
        with col2:
            st.markdown("**🟡 Out-of-Network Providers:**")
            for provider in ins.get('out_of_network_providers', []):
                st.markdown(f"• {provider}")

        st.markdown("---")

        # In-Network Accepted Fees
        st.markdown("### 🟢 In-Network Accepted Fees")
        if 'in_network_codes' in ins:
            for item in ins['in_network_codes']:
                st.markdown(f"**{item['code']}** - {item['description']}: ${item['accepted_fee']:,.2f}")

        st.markdown("---")

        # Out-of-Network Accepted Fees
        st.markdown("### 🟡 Out-of-Network Accepted Fees")
        st.markdown("*Reimbursement: 80% of accepted fee after deductible*")
        if 'out_of_network_codes' in ins:
            for item in ins['out_of_network_codes']:
                st.markdown(f"**{item['code']}** - {item['description']}: ${item['accepted_fee']:,.2f}")

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

        st.markdown("---")

        # Eligible Expenses
        st.markdown("### ✅ Eligible Expenses")
        st.markdown("*These expenses can be reimbursed through your FSA/HSA account:*")

        # Display in 2 columns for better readability
        eligible = fsa.get('eligible_expenses', [])
        if eligible:
            mid_point = len(eligible) // 2
            col1, col2 = st.columns(2)
            with col1:
                for expense in eligible[:mid_point]:
                    st.markdown(f"✅ {expense}")
            with col2:
                for expense in eligible[mid_point:]:
                    st.markdown(f"✅ {expense}")

        st.markdown("---")

        # Ineligible Expenses
        st.markdown("### ❌ Ineligible Expenses")
        st.markdown("*These expenses are NOT reimbursable:*")

        ineligible = fsa.get('ineligible_expenses', [])
        if ineligible:
            for expense in ineligible:
                st.markdown(f"❌ {expense}")

    # Stored Receipts
    with st.expander("🧾 Stored Receipts", expanded=False):
        receipts = profile.get('stored_receipts', [])
        
        if receipts:
            st.markdown(f"**{len(receipts)} receipts available for analysis context**")
            st.markdown("*These receipts can be referenced when analyzing new bills for pattern detection and overcharge comparison.*")
            st.markdown("---")
            
            # Summary metrics
            total_billed = sum(r['billed_amount'] for r in receipts)
            total_insurance = sum(r['insurance_paid'] for r in receipts)
            total_patient = sum(r['patient_paid'] for r in receipts)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Billed", f"${total_billed:,.2f}")
            with col2:
                st.metric("Insurance Paid", f"${total_insurance:,.2f}")
            with col3:
                st.metric("Patient Paid", f"${total_patient:,.2f}")
            
            st.markdown("---")
            
            # Display each receipt
            for idx, receipt in enumerate(receipts, 1):
                with st.container():
                    # Receipt header
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{receipt['id']}** - {receipt['service']}")
                    with col2:
                        status_emoji = "✅" if receipt['status'] == "Paid" else "⏳"
                        st.markdown(f"{status_emoji} {receipt['status']}")
                    
                    # Receipt details
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"📅 **Date:** {receipt['date']}")
                        st.markdown(f"🏥 **Provider:** {receipt['provider']}")
                    with col2:
                        if 'cpt_code' in receipt:
                            st.markdown(f"🔢 **CPT Code:** {receipt['cpt_code']}")
                        elif 'cdt_code' in receipt:
                            st.markdown(f"🔢 **CDT Code:** {receipt['cdt_code']}")
                        elif 'ndc_code' in receipt:
                            st.markdown(f"🔢 **NDC Code:** {receipt['ndc_code']}")
                    with col3:
                        st.markdown(f"💵 **Billed:** ${receipt['billed_amount']:,.2f}")
                        st.markdown(f"🏦 **Insurance:** ${receipt['insurance_paid']:,.2f}")
                        st.markdown(f"💳 **Patient:** ${receipt['patient_paid']:,.2f}")
                    
                    # Notes
                    if receipt.get('notes'):
                        # Color code based on content
                        if 'overcharge' in receipt['notes'].lower() or 'over' in receipt['notes'].lower():
                            st.warning(f"⚠️ {receipt['notes']}")
                        elif 'correctly billed' in receipt['notes'].lower() or '100% covered' in receipt['notes'].lower():
                            st.success(f"✓ {receipt['notes']}")
                        else:
                            st.info(f"ℹ️ {receipt['notes']}")
                    
                    if idx < len(receipts):
                        st.markdown("---")
        else:
            st.info("No receipts stored yet")


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

    # Build in-network codes reference
    in_network_fees = "\n".join([
        f"  - {code['code']}: {code['description']} = ${code['accepted_fee']:.2f}"
        for code in ins.get('in_network_codes', [])
    ])

    # Build out-of-network codes reference
    out_network_fees = "\n".join([
        f"  - {code['code']}: {code['description']} = ${code['accepted_fee']:.2f}"
        for code in ins.get('out_of_network_codes', [])
    ])

    # Build provider network lists
    in_network_providers = "\n  - ".join(ins.get('in_network_providers', []))
    out_network_providers = "\n  - ".join(ins.get('out_of_network_providers', []))

    # Build stored receipts history for pattern detection
    receipts = profile.get('stored_receipts', [])
    receipts_context = ""
    if receipts:
        receipts_context = "\n========================================\n"
        receipts_context += "BILLING HISTORY (STORED RECEIPTS)\n"
        receipts_context += "========================================\n"
        receipts_context += f"Total Receipts: {len(receipts)}\n\n"
        
        # Identify overcharge patterns
        overcharged_receipts = [r for r in receipts if 'overcharge' in r.get('notes', '').lower() or 'over' in r.get('notes', '').lower()]
        if overcharged_receipts:
            receipts_context += f"⚠️ OVERCHARGE PATTERNS DETECTED ({len(overcharged_receipts)} receipts):\n"
            for r in overcharged_receipts:
                code = r.get('cpt_code') or r.get('cdt_code') or r.get('ndc_code', 'N/A')
                receipts_context += f"  - {r['date']}: {r['provider']} | {r['service']} (Code: {code})\n"
                receipts_context += f"    Billed: ${r['billed_amount']:,.2f} | Insurance: ${r['insurance_paid']:,.2f} | Patient: ${r['patient_paid']:,.2f}\n"
                receipts_context += f"    Note: {r['notes']}\n"
            receipts_context += "\n"
        
        # Identify out-of-network patterns
        oon_receipts = [r for r in receipts if 'out-of-network' in r.get('notes', '').lower()]
        if oon_receipts:
            receipts_context += f"🟡 OUT-OF-NETWORK USAGE ({len(oon_receipts)} receipts):\n"
            for r in oon_receipts:
                code = r.get('cpt_code') or r.get('cdt_code') or r.get('ndc_code', 'N/A')
                receipts_context += f"  - {r['date']}: {r['provider']} | {r['service']} (Code: {code})\n"
                receipts_context += f"    Patient paid: ${r['patient_paid']:,.2f} | Note: {r['notes']}\n"
            receipts_context += "\n"
        
        # Summary statistics
        total_billed = sum(r['billed_amount'] for r in receipts)
        total_insurance = sum(r['insurance_paid'] for r in receipts)
        total_patient = sum(r['patient_paid'] for r in receipts)
        receipts_context += f"TOTALS ACROSS ALL STORED RECEIPTS:\n"
        receipts_context += f"  Total Billed: ${total_billed:,.2f}\n"
        receipts_context += f"  Insurance Paid: ${total_insurance:,.2f}\n"
        receipts_context += f"  Patient Paid: ${total_patient:,.2f}\n"
        receipts_context += f"  Potential Savings if overcharges corrected: ~${sum(r['patient_paid'] for r in overcharged_receipts):,.2f}\n"

    context = f"""
========================================
PATIENT PROFILE CONTEXT
========================================
Name: {profile['name']}
Age: {profile['age']} | Gender: {profile['gender']}
Relationship: {profile['relationship']}

INSURANCE COVERAGE:
Provider: {ins['provider']}
Plan Type: {ins['plan_type']}
Member ID: {ins['member_id']}
Annual Deductible: ${ins['deductible_annual']:,.2f} (${ins['deductible_met']:,.2f} met - {(ins['deductible_met']/ins['deductible_annual']*100):.0f}% complete)
Out-of-Pocket Maximum: ${ins['oop_max']:,.2f} (${ins['oop_met']:,.2f} met - {(ins['oop_met']/ins['oop_max']*100):.0f}% complete)

IN-NETWORK PROVIDERS (100% coverage after deductible):
  - {in_network_providers}

OUT-OF-NETWORK PROVIDERS (80% coverage after deductible):
  - {out_network_providers}

IN-NETWORK ACCEPTED FEES:
{in_network_fees}

OUT-OF-NETWORK ACCEPTED FEES (Patient responsible for balance billing):
{out_network_fees}

MEDICAL CONDITIONS: {', '.join(med['conditions'])}
CURRENT MEDICATIONS: {', '.join(med['medications'])}
ALLERGIES: {', '.join(med['allergies'])}
{receipts_context}
========================================
BILLING VALIDATION INSTRUCTIONS:
========================================
1. CHECK PROVIDER NETWORK STATUS: Verify if the provider is in-network or out-of-network
2. VALIDATE CPT/CDT CODES: Compare billed charges against accepted fees listed above
3. FLAG OVERCHARGES: If billed amount exceeds accepted fee for in-network providers
4. CHECK COVERAGE TIER: Out-of-network should be 80% reimbursement, not 100%
5. VERIFY DEDUCTIBLE APPLICATION: Check if deductible has been met before applying coverage
6. IDENTIFY BALANCE BILLING: Out-of-network providers may bill for difference between billed and accepted amounts
7. MEDICATION APPROPRIATENESS: Cross-reference prescriptions with patient's conditions and current medications
8. PATTERN DETECTION: Compare new bills against stored receipt history to identify recurring overcharges from same providers
9. PROVIDER REPUTATION: Flag providers with history of overcharging based on stored receipts

This profile context enables precise billing error detection and insurance coverage validation.
"""
    return context

