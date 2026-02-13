"""
MedBillDozer Challenge Page
Interactive medical billing dispute simulation with AI agents
"""

import streamlit as st
import json
from datetime import datetime
from typing import Dict, List, Optional
import time
from medbilldozer.ui.doc_assistant import render_assistant_avatar

# Page configuration
st.set_page_config(
    page_title="MedBillDozer Challenge",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
if "challenge_patient" not in st.session_state:
    st.session_state.challenge_patient = "Sarah"
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "challenge_stage" not in st.session_state:
    st.session_state.challenge_stage = "start"
if "flagged_issues" not in st.session_state:
    st.session_state.flagged_issues = {}
if "dispute_sent" not in st.session_state:
    st.session_state.dispute_sent = False

# Avatar mapping
AVATARS = {
    "Sarah": "👩‍⚕️",
    "Marcus": "👨‍⚕️",
    "Provider": "🏥",
    "Insurance": "🏢",
    "Arbitrator": "⚖️"
}

# Sample medical documents with errors
MEDICAL_DOCUMENTS = {
    "patient_story": {
        "Sarah": """
        **Patient Story: Sarah's 2026 Medical Journey**
        
        In March 2026, I visited Dr. Jennifer Wu at Metro Medical Center for persistent headaches. 
        After a thorough examination, Dr. Wu ordered an MRI scan which was performed on March 15, 2026.
        The MRI cost was $1,200 and was deemed medically necessary.
        
        I have Blue Cross Gold Plan insurance with a $1,500 deductible (already met $800 from earlier visits)
        and 80/20 coinsurance after deductible. My out-of-pocket maximum is $5,000.
        
        The diagnosis was tension headaches, and I was prescribed physical therapy (10 sessions at $150 each).
        I completed 8 sessions between April and May 2026.
        """,
        "Marcus": """
        **Patient Story: Marcus's 2026 Medical Journey**
        
        In February 2026, I had an emergency room visit at City Hospital for severe abdominal pain.
        The ER physician, Dr. Michael Torres, ordered a CT scan and bloodwork on February 20, 2026.
        The total ER visit cost was $3,500, including a $200 CT scan and $150 lab work.
        
        I have Aetna Silver Plan with a $2,000 deductible (only $300 met previously) and 70/30 coinsurance.
        My out-of-pocket maximum is $6,500 annually.
        
        The diagnosis was gastritis, and I was prescribed medication (Omeprazole) for 3 months.
        I also had a follow-up visit with a gastroenterologist in March ($250 specialist visit).
        """
    },
    "provider_bill_1": {
        "Sarah": {
            "date": "2026-03-20",
            "provider": "Metro Medical Center",
            "items": [
                {"service": "Office Visit - Level 4", "code": "99214", "charge": 250.00, "error": None},
                {"service": "MRI Brain without contrast", "code": "70551", "charge": 1200.00, "error": None},
                {"service": "MRI Brain with contrast", "code": "70553", "charge": 800.00, "error": "Not performed - duplicate billing"},
                {"service": "Physical Therapy - 8 sessions", "code": "97110", "charge": 1200.00, "error": None},
                {"service": "Physical Therapy - 5 sessions", "code": "97110", "charge": 750.00, "error": "Only 8 sessions total, not 13"},
            ],
            "total": 4200.00
        },
        "Marcus": {
            "date": "2026-02-25",
            "provider": "City Hospital Emergency Department",
            "items": [
                {"service": "ER Visit - Level 5", "code": "99285", "charge": 2500.00, "error": None},
                {"service": "CT Abdomen without contrast", "code": "74150", "charge": 1200.00, "error": "Should be $200"},
                {"service": "CT Abdomen with contrast", "code": "74160", "charge": 950.00, "error": "Not performed"},
                {"service": "Blood Work - Comprehensive", "code": "80053", "charge": 150.00, "error": None},
                {"service": "IV Administration", "code": "96374", "charge": 300.00, "error": None},
                {"service": "Gastroenterology Consult", "code": "99253", "charge": 450.00, "error": "This was a separate follow-up, not ER"},
            ],
            "total": 5550.00
        }
    },
    "insurance_eob": {
        "Sarah": {
            "date": "2026-04-10",
            "plan": "Blue Cross Gold Plan",
            "items": [
                {"service": "Office Visit - Level 4", "billed": 250.00, "allowed": 200.00, "paid": 120.00, "patient_responsibility": 80.00},
                {"service": "MRI Brain without contrast", "billed": 1200.00, "allowed": 800.00, "paid": 100.00, "patient_responsibility": 700.00},
                {"service": "MRI Brain with contrast", "billed": 800.00, "allowed": 600.00, "paid": 480.00, "patient_responsibility": 120.00, "error": "Should be denied"},
                {"service": "Physical Therapy - 13 sessions", "billed": 1950.00, "allowed": 1200.00, "paid": 960.00, "patient_responsibility": 240.00, "error": "Should be 8 sessions only"},
            ],
            "total_paid": 1660.00,
            "patient_owes": 1140.00
        },
        "Marcus": {
            "date": "2026-03-15",
            "plan": "Aetna Silver Plan",
            "items": [
                {"service": "ER Visit - Level 5", "billed": 2500.00, "allowed": 2000.00, "paid": 200.00, "patient_responsibility": 1800.00},
                {"service": "CT Abdomen without contrast", "billed": 1200.00, "allowed": 200.00, "paid": 0.00, "patient_responsibility": 200.00},
                {"service": "CT Abdomen with contrast", "billed": 950.00, "allowed": 800.00, "paid": 130.00, "patient_responsibility": 670.00, "error": "Should be denied"},
                {"service": "Blood Work", "billed": 150.00, "allowed": 120.00, "paid": 0.00, "patient_responsibility": 120.00},
                {"service": "IV Administration", "billed": 300.00, "allowed": 250.00, "paid": 0.00, "patient_responsibility": 250.00},
                {"service": "Gastroenterology Consult", "billed": 450.00, "allowed": 250.00, "paid": 0.00, "patient_responsibility": 250.00, "error": "Not part of ER visit"},
            ],
            "total_paid": 330.00,
            "patient_owes": 3290.00
        }
    }
}

def add_message(role: str, content: str, avatar: str = None):
    """Add a message to the chat"""
    st.session_state.chat_messages.append({
        "role": role,
        "content": content,
        "avatar": avatar or AVATARS.get(role, "💬"),
        "timestamp": datetime.now()
    })

def display_bill(bill_data: Dict, title: str):
    """Display a medical bill in a formatted way"""
    st.markdown(f"### {title}")
    st.markdown(f"**Date:** {bill_data['date']}")
    st.markdown(f"**Provider:** {bill_data['provider']}")
    st.markdown("---")
    
    for item in bill_data['items']:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{item['service']}** ({item['code']})")
            if item.get('error'):
                st.error(f"⚠️ Error: {item['error']}")
        with col2:
            st.write(f"${item['charge']:.2f}")
    
    st.markdown("---")
    st.markdown(f"**Total: ${bill_data['total']:.2f}**")

def display_eob(eob_data: Dict, title: str):
    """Display an EOB in a formatted way"""
    st.markdown(f"### {title}")
    st.markdown(f"**Date:** {eob_data['date']}")
    st.markdown(f"**Plan:** {eob_data['plan']}")
    st.markdown("---")
    
    for item in eob_data['items']:
        st.write(f"**{item['service']}**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"Billed: ${item['billed']:.2f}")
        with col2:
            st.write(f"Allowed: ${item['allowed']:.2f}")
        with col3:
            st.write(f"Paid: ${item['paid']:.2f}")
        with col4:
            st.write(f"You owe: ${item['patient_responsibility']:.2f}")
        if item.get('error'):
            st.error(f"⚠️ Error: {item['error']}")
        st.markdown("---")
    
    st.markdown(f"**Insurance Paid: ${eob_data['total_paid']:.2f}**")
    st.markdown(f"**You Owe: ${eob_data['patient_owes']:.2f}**")

def analyze_bills_with_medgemma():
    """Simulate MedGemma ensemble analysis"""
    patient = st.session_state.challenge_patient
    
    # Simulated analysis results
    issues = {
        "Sarah": [
            {
                "id": "B1",
                "severity": "High",
                "category": "Duplicate Billing",
                "description": "MRI with contrast ($800) was not performed according to patient story, but was billed and partially paid by insurance.",
                "provider_charge": 800.00,
                "insurance_paid": 480.00,
                "potential_savings": 800.00
            },
            {
                "id": "B2",
                "severity": "High",
                "category": "Quantity Mismatch",
                "description": "Physical therapy billed for 13 sessions (5+8) but patient only received 8 sessions according to medical records.",
                "provider_charge": 750.00,
                "insurance_paid": 960.00,
                "potential_savings": 750.00
            },
            {
                "id": "B3",
                "severity": "Medium",
                "category": "Pricing Error",
                "description": "MRI without contrast: Insurance allowed $800 but standard rate should be $900-1000. Patient paid more than fair share.",
                "provider_charge": 0.00,
                "insurance_paid": 100.00,
                "potential_savings": 200.00
            }
        ],
        "Marcus": [
            {
                "id": "BY1",
                "severity": "High",
                "category": "Service Not Rendered",
                "description": "CT scan with contrast ($950) was not performed - only CT without contrast was done per medical records.",
                "provider_charge": 950.00,
                "insurance_paid": 130.00,
                "potential_savings": 950.00
            },
            {
                "id": "BY2",
                "severity": "High",
                "category": "Price Inflation",
                "description": "CT Abdomen without contrast billed at $1,200 but patient story indicates actual cost was $200. 600% markup.",
                "provider_charge": 1200.00,
                "insurance_paid": 0.00,
                "potential_savings": 1000.00
            },
            {
                "id": "BY3",
                "severity": "High",
                "category": "Unbundling/Separate Visit",
                "description": "Gastroenterology consult ($450) was a separate follow-up appointment in March, not part of February ER visit.",
                "provider_charge": 450.00,
                "insurance_paid": 0.00,
                "potential_savings": 250.00
            },
            {
                "id": "BY4",
                "severity": "Medium",
                "category": "Deductible Calculation",
                "description": "Insurance applied full deductible incorrectly. With $300 already met, patient should owe less.",
                "provider_charge": 0.00,
                "insurance_paid": 330.00,
                "potential_savings": 500.00
            }
        ]
    }
    
    return issues[patient]

# Sidebar - Patient Selection
with st.sidebar:
    # Render the assistant avatar at the top
    render_assistant_avatar()
    
    # Toggle button for character switch
    current_character = st.session_state.get("avatar_character", "billy")
    other_character = "billie" if current_character == "billy" else "billy"
    button_label = f"Switch to {other_character.capitalize()}"

    if st.button(button_label, key="challenge_character_toggle"):
        st.session_state.avatar_character = other_character
        st.rerun()
    
    st.markdown("---")
    st.markdown("## Select Patient")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👩‍⚕️ Sarah", use_container_width=True, type="primary" if st.session_state.challenge_patient == "Sarah" else "secondary"):
            if st.session_state.challenge_patient != "Sarah":
                st.session_state.challenge_patient = "Sarah"
                st.session_state.chat_messages = []
                st.session_state.challenge_stage = "start"
                st.session_state.flagged_issues = {}
                st.session_state.dispute_sent = False
                st.rerun()
    
    with col2:
        if st.button("👨‍⚕️ Marcus", use_container_width=True, type="primary" if st.session_state.challenge_patient == "Marcus" else "secondary"):
            if st.session_state.challenge_patient != "Marcus":
                st.session_state.challenge_patient = "Marcus"
                st.session_state.chat_messages = []
                st.session_state.challenge_stage = "start"
                st.session_state.flagged_issues = {}
                st.session_state.dispute_sent = False
                st.rerun()
    
    st.markdown("---")
    st.markdown(f"### Current Patient")
    st.markdown(f"# {AVATARS[st.session_state.challenge_patient]} {st.session_state.challenge_patient}")

# Main UI
st.title("💰 MedBillDozer Challenge")
st.markdown("### Navigate the complex world of medical billing disputes")

# Document accordion
st.markdown("---")
with st.expander("📋 Medical History & Documents", expanded=False):
    doc_tabs = st.tabs(["Patient Story", "Provider Bill", "Insurance EOB", "Updated Bill"])
    
    with doc_tabs[0]:
        st.markdown(MEDICAL_DOCUMENTS["patient_story"][st.session_state.challenge_patient])
    
    with doc_tabs[1]:
        if st.session_state.challenge_patient in MEDICAL_DOCUMENTS["provider_bill_1"]:
            bill_data = MEDICAL_DOCUMENTS["provider_bill_1"][st.session_state.challenge_patient]
            display_bill(bill_data, "Original Provider Bill")
    
    with doc_tabs[2]:
        if st.session_state.challenge_patient in MEDICAL_DOCUMENTS["insurance_eob"]:
            eob_data = MEDICAL_DOCUMENTS["insurance_eob"][st.session_state.challenge_patient]
            display_eob(eob_data, "Insurance Explanation of Benefits (EOB)")
    
    with doc_tabs[3]:
        st.info("Updated bill will appear after insurance processes the claim")

st.markdown("---")

# Control buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🎬 Start Challenge", use_container_width=True):
        st.session_state.chat_messages = []
        st.session_state.challenge_stage = "story"
        st.session_state.flagged_issues = {}
        st.session_state.dispute_sent = False
        
        # Add patient story to chat
        story = MEDICAL_DOCUMENTS["patient_story"][st.session_state.challenge_patient]
        add_message(st.session_state.challenge_patient, story, AVATARS[st.session_state.challenge_patient])
        st.rerun()

with col2:
    if st.button("📄 Send Provider Bill", disabled=(st.session_state.challenge_stage == "start"), use_container_width=True):
        if st.session_state.challenge_stage == "story":
            bill_data = MEDICAL_DOCUMENTS["provider_bill_1"][st.session_state.challenge_patient]
            
            bill_text = f"""
**Original Medical Bill from {bill_data['provider']}**
Date: {bill_data['date']}

"""
            for item in bill_data['items']:
                bill_text += f"• {item['service']} ({item['code']}): ${item['charge']:.2f}\n"
            
            bill_text += f"\n**Total Amount Due: ${bill_data['total']:.2f}**"
            
            add_message("Provider", bill_text, AVATARS["Provider"])
            st.session_state.challenge_stage = "bill_sent"
            st.rerun()

with col3:
    if st.button("🏢 Send Insurance EOB", disabled=(st.session_state.challenge_stage not in ["bill_sent", "eob_sent"]), use_container_width=True):
        if st.session_state.challenge_stage == "bill_sent":
            eob_data = MEDICAL_DOCUMENTS["insurance_eob"][st.session_state.challenge_patient]
            
            eob_text = f"""
**Explanation of Benefits (EOB)**
Plan: {eob_data['plan']}
Date: {eob_data['date']}

"""
            for item in eob_data['items']:
                eob_text += f"• {item['service']}\n"
                eob_text += f"  Billed: ${item['billed']:.2f} | Allowed: ${item['allowed']:.2f} | We Paid: ${item['paid']:.2f} | You Owe: ${item['patient_responsibility']:.2f}\n"
            
            eob_text += f"\n**Insurance Paid: ${eob_data['total_paid']:.2f}**"
            eob_text += f"\n**Your Responsibility: ${eob_data['patient_owes']:.2f}**"
            
            add_message("Insurance", eob_text, AVATARS["Insurance"])
            st.session_state.challenge_stage = "eob_sent"
            st.rerun()

with col4:
    if st.button("📋 Send Updated Bill", disabled=(st.session_state.challenge_stage != "eob_sent"), use_container_width=True):
        eob_data = MEDICAL_DOCUMENTS["insurance_eob"][st.session_state.challenge_patient]
        
        updated_bill_text = f"""
**Updated Bill After Insurance**
Date: {datetime.now().strftime('%Y-%m-%d')}

Based on the insurance EOB, your remaining balance is:

**Amount You Owe: ${eob_data['patient_owes']:.2f}**

Please remit payment within 30 days.
"""
        
        add_message("Provider", updated_bill_text, AVATARS["Provider"])
        st.session_state.challenge_stage = "updated_bill"
        st.rerun()

# Chat window
st.markdown("### 💬 Challenge Chat")
chat_container = st.container(height=400, border=True)

with chat_container:
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"], avatar=msg["avatar"]):
            st.markdown(msg["content"])

# Analysis section
if st.session_state.challenge_stage == "updated_bill":
    st.markdown("---")
    
    if st.button("🔍 Analyze Bills with MedGemma Ensemble", use_container_width=True, type="primary"):
        with st.spinner("MedGemma ensemble analyzing documents for billing errors..."):
            time.sleep(2)  # Simulate analysis
            issues = analyze_bills_with_medgemma()
            
            # Display analysis results in chat
            patient_name = st.session_state.challenge_patient
            avatar_character = st.session_state.get("avatar_character", "billy").capitalize()
            analysis_text = f"""
**{avatar_character}: I just analyzed the bills using MedGemma-Ensemble and here is what I found...**

Found {len(issues)} potential billing issues:

"""
            total_potential_savings = sum(issue['potential_savings'] for issue in issues)
            
            for issue in issues:
                analysis_text += f"\n**Issue {issue['id']}: {issue['category']}** (Severity: {issue['severity']})\n"
                analysis_text += f"{issue['description']}\n"
                analysis_text += f"💰 Potential Savings: ${issue['potential_savings']:.2f}\n"
            
            analysis_text += f"\n**Total Potential Savings: ${total_potential_savings:.2f}**"
            
            add_message(st.session_state.challenge_patient, analysis_text, AVATARS[st.session_state.challenge_patient])
            st.session_state.flagged_issues = {issue['id']: 'flag' for issue in issues}
            st.session_state.analysis_results = issues
            st.session_state.challenge_stage = "analyzed"
            st.rerun()

# Issue management
if st.session_state.challenge_stage == "analyzed" and hasattr(st.session_state, 'analysis_results'):
    st.markdown("---")
    st.markdown("### 🚩 Review Flagged Issues")
    
    issues = st.session_state.analysis_results
    
    for issue in issues:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{issue['id']}: {issue['category']}** ({issue['severity']} Severity)")
                st.write(issue['description'])
                st.write(f"💰 Potential Savings: ${issue['potential_savings']:.2f}")
            
            with col2:
                action = st.selectbox(
                    "Action",
                    ["flag", "ignore", "resolved"],
                    key=f"action_{issue['id']}",
                    index=["flag", "ignore", "resolved"].index(st.session_state.flagged_issues.get(issue['id'], 'flag'))
                )
                st.session_state.flagged_issues[issue['id']] = action
    
    # Dispute message section
    st.markdown("---")
    st.markdown("### ✍️ Submit Dispute")
    
    dispute_text = st.text_area(
        "Compose your dispute message to the provider and insurance company:",
        placeholder="Dear Provider and Insurance Company,\n\nI am writing to dispute the following charges on my medical bill...",
        height=150
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Send Dispute to Provider", use_container_width=True, disabled=not dispute_text):
            add_message(st.session_state.challenge_patient, f"**Dispute to Provider:**\n\n{dispute_text}", AVATARS[st.session_state.challenge_patient])
            st.session_state.dispute_sent_provider = True
            
            # Provider response (trying to minimize refund)
            time.sleep(1)
            provider_response = f"""
**Provider Response:**

Thank you for bringing these concerns to our attention. After reviewing your dispute:

• Regarding the duplicate/unperformed procedures: We have reviewed our records and found documentation that may support these charges. However, we can offer a 15% courtesy adjustment of ${sum(issue['potential_savings'] for issue in issues) * 0.15:.2f}.

• The quantity discrepancies appear to be administrative errors in our system. We're investigating.

We believe our billing is accurate, but we value you as a patient. Would this resolution be acceptable?
"""
            add_message("Provider", provider_response, AVATARS["Provider"])
            st.rerun()
    
    with col2:
        if st.button("📤 Send Dispute to Insurance", use_container_width=True, disabled=not dispute_text):
            add_message(st.session_state.challenge_patient, f"**Dispute to Insurance:**\n\n{dispute_text}", AVATARS[st.session_state.challenge_patient])
            st.session_state.dispute_sent_insurance = True
            
            # Insurance response (trying to minimize payout)
            time.sleep(1)
            insurance_response = f"""
**Insurance Company Response:**

We have received your appeal and conducted a secondary review of your claim.

• After review, we have identified one service that should not have been covered under your policy terms. We will be issuing a refund of ${sum(issue['potential_savings'] for issue in issues) * 0.10:.2f}.

• The remaining charges fall within your deductible and coinsurance obligations per your plan agreement.

• Our medical review team has determined the billed services align with the documentation provided.

If you disagree with this determination, you have the right to request external arbitration.
"""
            add_message("Insurance", insurance_response, AVATARS["Insurance"])
            st.rerun()
    
    # Arbitration button
    if hasattr(st.session_state, 'dispute_sent_provider') or hasattr(st.session_state, 'dispute_sent_insurance'):
        st.markdown("---")
        st.markdown("### ⚖️ Still Have Unresolved Issues?")
        
        if st.button("⚖️ Request Arbitration", use_container_width=True, type="primary"):
            arbitration_message = f"""
**Arbitration Requested**

An independent arbitrator has been assigned to review your case.

The arbitrator will examine:
• Original medical records and documentation
• Provider billing practices
• Insurance policy terms and coverage
• Industry standard pricing
• State and federal regulations

**Arbitrator Analysis:**

After thorough review of all documentation and applicable regulations:

1. **MRI with contrast charge** - UPHELD: Provider must refund $800. Service was not rendered.

2. **Physical therapy overbilling** - UPHELD: Provider must refund $750 for 5 unrendered sessions.

3. **CT scan pricing error** - UPHELD: Provider must adjust bill by $1,000. Charge was 600% above standard rate.

4. **CT scan with contrast** - UPHELD: Insurance and provider must refund $950. Service not rendered.

5. **Unbundled gastroenterology visit** - UPHELD: This was a separate appointment and must be billed separately.

6. **Insurance deductible calculation** - PARTIALLY UPHELD: Insurance recalculation required. Additional $350 credit to patient.

**FINAL RULING:**

Total Refund Due to Patient: ${sum(issue['potential_savings'] for issue in st.session_state.analysis_results):.2f}

Provider Penalties: $500 for billing violations
Insurance Penalties: $250 for incorrect claim processing

Case closed. All parties must comply within 30 days.
"""
            
            add_message("Arbitrator", arbitration_message, AVATARS["Arbitrator"])
            st.session_state.challenge_stage = "complete"
            st.balloons()
            st.rerun()

# Completion message
if st.session_state.challenge_stage == "complete":
    st.success("🎉 Challenge Complete! You successfully navigated the medical billing dispute process and recovered money owed to you!")
    
    if st.button("🔄 Start New Challenge", use_container_width=True):
        st.session_state.chat_messages = []
        st.session_state.challenge_stage = "start"
        st.session_state.flagged_issues = {}
        st.session_state.dispute_sent = False
        if hasattr(st.session_state, 'analysis_results'):
            delattr(st.session_state, 'analysis_results')
        if hasattr(st.session_state, 'dispute_sent_provider'):
            delattr(st.session_state, 'dispute_sent_provider')
        if hasattr(st.session_state, 'dispute_sent_insurance'):
            delattr(st.session_state, 'dispute_sent_insurance')
        st.rerun()
