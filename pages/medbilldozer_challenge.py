"""
MedBillDozer Challenge Page - Enhanced Version
Interactive medical billing dispute simulation with AI agents, clinical validation, and gamification
"""

import streamlit as st
import json
import base64
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import time

from medbilldozer.ui.doc_assistant import render_assistant_avatar
from medbilldozer.data.challenge_scenarios import ChallengeScenario
from medbilldozer.core.scenario_selector import ScenarioSelector
from medbilldozer.core.clinical_validator import ClinicalValidator
from medbilldozer.core.achievements import AchievementTracker, ScoringEngine

# Page configuration
st.set_page_config(
    page_title="MedBillDozer Challenge",
    page_icon="💰",
    layout="wide"
)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if "challenge_stage" not in st.session_state:
        st.session_state.challenge_stage = "start"
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "flagged_issues" not in st.session_state:
        st.session_state.flagged_issues = {}
    if "current_scenario" not in st.session_state:
        st.session_state.current_scenario = None
    if "clinical_validations" not in st.session_state:
        st.session_state.clinical_validations = []
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "completion_time" not in st.session_state:
        st.session_state.completion_time = 0
    if "score_breakdown" not in st.session_state:
        st.session_state.score_breakdown = None
    if "achievements_earned" not in st.session_state:
        st.session_state.achievements_earned = []

    # Session statistics
    if "session_stats" not in st.session_state:
        st.session_state.session_stats = {
            "scenarios_completed": 0,
            "total_score": 0,
            "images_validated": 0,
            "billing_errors_caught": 0,
            "perfect_streak": 0,
            "zero_fp_challenges": 0
        }

    # Initialize scenario selector
    if "scenario_selector" not in st.session_state:
        scenarios_dir = Path(__file__).parent.parent / "benchmarks" / "challenge_scenarios"
        st.session_state.scenario_selector = ScenarioSelector(
            data_source="json",
            scenarios_dir=scenarios_dir
        )

init_session_state()

# Avatar mapping
AVATARS = {
    "Provider": "🏥",
    "Insurance": "🏢",
    "Arbitrator": "⚖️",
    "AI": "🤖"
}

# Helper functions
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
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{item['service']}** ({item['code']})")
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
        st.markdown("---")

    st.markdown(f"**Insurance Paid: ${eob_data['total_paid']:.2f}**")
    st.markdown(f"**You Owe: ${eob_data['patient_owes']:.2f}**")

def encode_image_to_base64(image_path: Path) -> str:
    """Encode image to base64 for display"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def display_clinical_images(scenario: ChallengeScenario):
    """Display clinical images with AI validation"""
    if not scenario.clinical_images:
        return

    st.markdown("### 🔬 Clinical Image Analysis")
    st.info("AI is analyzing medical images to validate treatment appropriateness...")

    images_base = Path(__file__).parent.parent / "benchmarks" / "clinical_images" / "kaggle_datasets" / "selected"

    for idx, clinical_image in enumerate(scenario.clinical_images):
        image_path = images_base / clinical_image.file_path

        with st.container(border=True):
            col1, col2 = st.columns([1, 1])

            with col1:
                if image_path.exists():
                    # Display image
                    st.image(str(image_path), caption=f"{clinical_image.modality.upper()} Scan")
                else:
                    st.warning(f"Image not found: {clinical_image.file_path}")

            with col2:
                st.markdown(f"**Modality:** {clinical_image.modality.title()}")
                st.markdown(f"**Clinical Finding:** {clinical_image.finding}")

                # Get validation result if already performed
                if idx < len(st.session_state.clinical_validations):
                    validation = st.session_state.clinical_validations[idx]

                    if validation["determination"] == "CORRECT":
                        st.success("✅ Treatment matches imaging findings")
                    elif validation["determination"] == "ERROR":
                        st.error("❌ Treatment does not match imaging findings")
                    else:
                        st.warning("⚠️ Unable to validate")

                    st.markdown(f"**AI Confidence:** {validation['confidence']}")
                    with st.expander("View AI Analysis"):
                        st.write(validation['justification'])

def run_clinical_validation(scenario: ChallengeScenario):
    """Run AI validation on clinical images"""
    if not scenario.clinical_images or st.session_state.clinical_validations:
        return  # Already validated

    validator = ClinicalValidator(model="gpt-4o-mini")

    # Get prescribed treatment from provider bill
    prescribed_treatment = "Unknown treatment"
    if scenario.provider_bill and "items" in scenario.provider_bill:
        treatments = [item["service"] for item in scenario.provider_bill["items"] if "therapy" in item["service"].lower() or "treatment" in item["service"].lower()]
        if treatments:
            prescribed_treatment = ", ".join(treatments)

    # Validate each image
    validations = validator.validate_scenario_images(
        scenario.clinical_images,
        prescribed_treatment,
        scenario.patient_profile
    )

    st.session_state.clinical_validations = validations

    # Update session stats
    st.session_state.session_stats["images_validated"] += len(validations)

    # Add validation results to chat
    for validation in validations:
        if validation["determination"] == "ERROR":
            # Found a clinical error
            error_msg = f"🤖 **AI Clinical Validation Alert:**\n\n"
            error_msg += f"Modality: {validation['modality'].title()}\n"
            error_msg += f"Determination: Treatment mismatch detected\n"
            error_msg += f"Confidence: {validation['confidence']}\n\n"
            error_msg += f"Analysis: {validation['justification']}"
            add_message("AI", error_msg, "🤖")

def analyze_scenario():
    """Analyze current scenario for billing errors"""
    scenario = st.session_state.current_scenario

    if not scenario:
        return []

    # Return billing errors from scenario
    issues = []
    for error in scenario.billing_errors:
        issues.append({
            "id": error["id"],
            "severity": error["severity"],
            "category": error["category"],
            "description": error["description"],
            "potential_savings": error.get("potential_savings", 0)
        })

    # Add clinical errors if any
    for validation in st.session_state.clinical_validations:
        if validation["determination"] == "ERROR":
            issues.append({
                "id": f"C{len(issues)+1}",
                "severity": "Critical",
                "category": "Clinical Validation Error",
                "description": f"{validation['modality'].title()}: {validation['justification']}",
                "potential_savings": 0
            })

    return issues

def check_malpractice_trigger(scenario: ChallengeScenario) -> bool:
    """Check if malpractice decision stage should be triggered"""
    if not scenario.malpractice:
        return False

    # Check if clinical errors were found
    clinical_errors_found = any(
        v["determination"] == "ERROR"
        for v in st.session_state.clinical_validations
    )

    # Check severity
    harm_threshold_met = scenario.malpractice.harm_severity in ['moderate', 'severe', 'critical']

    return (
        scenario.malpractice.is_malpractice and
        clinical_errors_found and
        harm_threshold_met
    )

def calculate_final_score():
    """Calculate final score and achievements"""
    scenario = st.session_state.current_scenario

    if not scenario:
        return

    # Get flagged issues
    flagged_issues = [k for k, v in st.session_state.flagged_issues.items() if v == 'flag']

    # Expected issues
    expected_issue_ids = [e["id"] for e in scenario.billing_errors]

    # Add clinical error IDs if applicable
    for i, validation in enumerate(st.session_state.clinical_validations):
        if validation["determination"] == "ERROR":
            expected_issue_ids.append(f"C{i+1}")

    # Calculate false positives
    false_positives = len(set(flagged_issues) - set(expected_issue_ids))

    # Clinical validations
    clinical_correct = sum(1 for v in st.session_state.clinical_validations if v["determination"] == "CORRECT")
    clinical_total = len(st.session_state.clinical_validations)

    # Calculate score
    score_breakdown = ScoringEngine.calculate_score(
        issues_found=flagged_issues,
        issues_expected=expected_issue_ids,
        false_positives=false_positives,
        clinical_validations_correct=clinical_correct,
        clinical_validations_total=clinical_total,
        is_clean_case=(scenario.category == "clean_case"),
        difficulty=scenario.difficulty,
        completion_time=st.session_state.completion_time,
        time_bonus_threshold=scenario.time_bonus_threshold
    )

    st.session_state.score_breakdown = score_breakdown

    # Update session stats
    st.session_state.session_stats["scenarios_completed"] += 1
    st.session_state.session_stats["total_score"] += score_breakdown["final_score"]
    st.session_state.session_stats["billing_errors_caught"] += score_breakdown["correct_issues"]

    if score_breakdown["accuracy"] == 100:
        st.session_state.session_stats["perfect_streak"] += 1
    else:
        st.session_state.session_stats["perfect_streak"] = 0

    if false_positives == 0:
        st.session_state.session_stats["zero_fp_challenges"] += 1

    # Check achievements
    challenge_result = {
        "accuracy": score_breakdown["accuracy"],
        "scenario_category": scenario.category,
        "false_positives": false_positives,
        "completion_time": st.session_state.completion_time,
        "malpractice_identified": getattr(st.session_state, 'malpractice_escalated', False)
    }

    achievements = AchievementTracker.check_achievements(
        st.session_state.session_stats,
        challenge_result
    )

    st.session_state.achievements_earned = achievements

# Sidebar
with st.sidebar:
    render_assistant_avatar()

    # Toggle button for character switch
    current_character = st.session_state.get("avatar_character", "billy")
    other_character = "billie" if current_character == "billy" else "billy"
    button_label = f"Switch to {other_character.capitalize()}"

    if st.button(button_label, key="challenge_character_toggle"):
        st.session_state.avatar_character = other_character
        st.rerun()

    st.markdown("---")

    # Session statistics
    st.markdown("### 📊 Session Stats")
    stats = st.session_state.session_stats
    st.metric("Scenarios Completed", stats["scenarios_completed"])
    st.metric("Total Score", stats["total_score"])
    st.metric("Perfect Streak", f"🔥 {stats['perfect_streak']}")

    if st.session_state.current_scenario:
        st.markdown("---")
        st.markdown("### 📋 Current Scenario")
        scenario = st.session_state.current_scenario
        st.markdown(f"**Patient:** {scenario.patient_avatar} {scenario.patient_name}")
        st.markdown(f"**Category:** {scenario.category.replace('_', ' ').title()}")
        st.markdown(f"**Difficulty:** {scenario.difficulty.title()}")

        # Timer
        if st.session_state.start_time:
            elapsed = int((datetime.now() - st.session_state.start_time).total_seconds())
            st.markdown(f"**Time:** {elapsed // 60}:{elapsed % 60:02d}")

# Main UI
st.title("💰 MedBillDozer Challenge")
st.markdown("### Navigate the complex world of medical billing disputes")

# Control buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🎬 Start New Challenge", use_container_width=True, type="primary" if st.session_state.challenge_stage == "start" else "secondary"):
        # Select random scenario
        scenario = st.session_state.scenario_selector.select_scenario()

        if scenario:
            # Reset state
            st.session_state.current_scenario = scenario
            st.session_state.chat_messages = []
            st.session_state.challenge_stage = "story"
            st.session_state.flagged_issues = {}
            st.session_state.clinical_validations = []
            st.session_state.start_time = datetime.now()
            st.session_state.score_breakdown = None
            st.session_state.achievements_earned = []

            # Add patient story to chat
            add_message(scenario.patient_name, scenario.patient_story, scenario.patient_avatar)
            st.rerun()
        else:
            st.error("No scenarios available. Please generate scenarios first.")

with col2:
    if st.button("📄 Review Documents", disabled=(st.session_state.challenge_stage == "start"), use_container_width=True):
        if st.session_state.current_scenario:
            scenario = st.session_state.current_scenario

            # Add clinical validation stage if images present
            if scenario.clinical_images and st.session_state.challenge_stage == "story":
                st.session_state.challenge_stage = "clinical_validation"
            else:
                st.session_state.challenge_stage = "documents"
            st.rerun()

with col3:
    if st.button("🔍 Analyze", disabled=(st.session_state.challenge_stage not in ["documents", "clinical_validation"]), use_container_width=True):
        st.session_state.challenge_stage = "analysis"
        st.rerun()

with col4:
    if st.button("⚖️ Submit", disabled=(st.session_state.challenge_stage != "analysis"), use_container_width=True):
        # Calculate completion time
        if st.session_state.start_time:
            st.session_state.completion_time = int((datetime.now() - st.session_state.start_time).total_seconds())

        # Calculate score
        calculate_final_score()

        # Check for malpractice trigger
        if check_malpractice_trigger(st.session_state.current_scenario):
            st.session_state.challenge_stage = "malpractice_decision"
        else:
            st.session_state.challenge_stage = "scoring"
        st.rerun()

st.markdown("---")

# Main content area based on stage
if st.session_state.challenge_stage == "start":
    st.info("👆 Click 'Start New Challenge' to begin a random medical billing scenario!")

    # Show selector statistics
    if st.session_state.scenario_selector:
        stats = st.session_state.scenario_selector.get_statistics()
        st.markdown("### 📚 Available Scenarios")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Scenarios", stats["total"])
        with col2:
            st.metric("Completed", len(st.session_state.scenario_selector.played_scenarios))
        with col3:
            remaining = stats["total"] - len(st.session_state.scenario_selector.played_scenarios)
            st.metric("Remaining", remaining)

        # Category breakdown
        st.markdown("**By Category:**")
        for category, count in stats["by_category"].items():
            st.write(f"- {category.replace('_', ' ').title()}: {count}")

elif st.session_state.challenge_stage == "story":
    st.markdown("### 📖 Patient Story")
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"], avatar=msg["avatar"]):
            st.markdown(msg["content"])

elif st.session_state.challenge_stage == "clinical_validation":
    scenario = st.session_state.current_scenario

    if scenario and scenario.clinical_images:
        # Run clinical validation automatically
        with st.spinner("AI analyzing medical images..."):
            run_clinical_validation(scenario)
            time.sleep(1)  # Brief pause for effect

        display_clinical_images(scenario)

        if st.button("Continue to Documents →", type="primary"):
            st.session_state.challenge_stage = "documents"
            st.rerun()

elif st.session_state.challenge_stage == "documents":
    scenario = st.session_state.current_scenario

    if scenario:
        # Add Medical Images tab if clinical images exist
        tab_names = ["Provider Bill", "Insurance EOB", "Patient Story"]
        if scenario.clinical_images:
            tab_names.append("Medical Images")

        tabs = st.tabs(tab_names)

        with tabs[0]:
            if scenario.provider_bill:
                display_bill(scenario.provider_bill, "Provider Bill")

        with tabs[1]:
            if scenario.insurance_eob:
                display_eob(scenario.insurance_eob, "Insurance EOB")

        with tabs[2]:
            st.markdown(scenario.patient_story)

        # Medical Images tab (if exists)
        if scenario.clinical_images and len(tabs) > 3:
            with tabs[3]:
                st.markdown("### 🔬 Medical Imaging")
                images_base = Path(__file__).parent.parent / "benchmarks" / "clinical_images" / "kaggle_datasets" / "selected"

                for idx, clinical_image in enumerate(scenario.clinical_images):
                    image_path = images_base / clinical_image.file_path

                    with st.container(border=True):
                        col1, col2 = st.columns([1, 1])

                        with col1:
                            if image_path.exists():
                                st.image(str(image_path), caption=f"{clinical_image.modality.upper()} Scan")
                            else:
                                st.warning(f"Image not found: {clinical_image.file_path}")

                        with col2:
                            st.markdown(f"**Modality:** {clinical_image.modality.title()}")
                            st.markdown(f"**Finding:** {clinical_image.finding}")

                            # Show validation results if available
                            if idx < len(st.session_state.clinical_validations):
                                validation = st.session_state.clinical_validations[idx]
                                st.markdown("---")
                                st.markdown("**AI Analysis:**")

                                if validation["determination"] == "CORRECT":
                                    st.success("✅ Treatment appropriate")
                                elif validation["determination"] == "ERROR":
                                    st.error("❌ Treatment mismatch")
                                else:
                                    st.info("⚠️ Analysis pending")

                                if validation.get("confidence"):
                                    st.caption(f"Confidence: {validation['confidence']}")

                                with st.expander("View detailed analysis"):
                                    st.write(validation.get('justification', 'No details available'))

elif st.session_state.challenge_stage == "analysis":
    st.markdown("### 🔍 Analysis Results")

    with st.spinner("Analyzing medical documents..."):
        time.sleep(1)
        issues = analyze_scenario()

    if not issues:
        st.success("✅ No issues found! This appears to be a clean case.")
        st.session_state.flagged_issues = {}
    else:
        st.markdown(f"Found **{len(issues)}** potential issues:")

        for issue in issues:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**{issue['id']}: {issue['category']}** ({issue['severity']} Severity)")
                    st.write(issue['description'])
                    if issue['potential_savings'] > 0:
                        st.write(f"💰 Potential Savings: ${issue['potential_savings']:.2f}")

                with col2:
                    action = st.selectbox(
                        "Action",
                        ["flag", "ignore"],
                        key=f"action_{issue['id']}",
                        index=0 if st.session_state.flagged_issues.get(issue['id'], 'flag') == 'flag' else 1
                    )
                    st.session_state.flagged_issues[issue['id']] = action

elif st.session_state.challenge_stage == "malpractice_decision":
    scenario = st.session_state.current_scenario

    st.markdown("### ⚖️ Potential Malpractice Detected")

    st.warning(f"""
    Based on your analysis, this case involves:
    - Wrong treatment prescribed for the clinical findings
    - Patient harm documented
    - Severity: **{scenario.malpractice.harm_severity.title()}**

    You may escalate this to a malpractice review.
    """)

    with st.container(border=True):
        st.markdown("**Patient Outcome:**")
        st.write(scenario.malpractice.outcome_description)

        st.markdown("**Identified Issues:**")
        if scenario.malpractice.wrong_treatment:
            st.error("❌ Wrong treatment administered")
        if scenario.malpractice.wrong_diagnosis:
            st.error("❌ Misdiagnosis")
        if scenario.malpractice.unnecessary_procedure:
            st.error("❌ Unnecessary procedure performed")

        st.markdown(f"**Patient Harm:** {scenario.malpractice.patient_harm}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔺 Escalate to Malpractice Review", type="primary", use_container_width=True):
            st.session_state.malpractice_escalated = True
            st.session_state.challenge_stage = "scoring"
            st.rerun()

    with col2:
        if st.button("Continue with Billing Dispute Only", use_container_width=True):
            st.session_state.malpractice_escalated = False
            st.session_state.challenge_stage = "scoring"
            st.rerun()

elif st.session_state.challenge_stage == "scoring":
    st.markdown("## 🎯 Challenge Complete!")

    if st.session_state.score_breakdown:
        score = st.session_state.score_breakdown

        # Score metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Base Score", f"{score['base_score']} pts")
        with col2:
            st.metric("Accuracy Bonus", f"+{score['accuracy_bonus']} pts")
        with col3:
            st.metric("Speed Bonus", f"+{score['speed_bonus']} pts")
        with col4:
            st.metric("Accuracy", f"{score['accuracy']}%")

        st.markdown("---")

        # Final score with animation
        st.markdown(f"### 🏆 Final Score: **{score['final_score']}** points")
        st.progress(min(score['final_score'] / 3000, 1.0))

        # Detailed breakdown
        with st.expander("📊 Score Breakdown"):
            st.markdown(f"""
            - **Correct Issues Found:** {score['correct_issues']} × 100 pts = {score['base_score']} pts
            - **False Positives:** {score['false_positives']} × -50 pts = {score['fp_penalty']} pts
            - **Clinical Validation:** +{score['clinical_points']} pts
            - **Clean Case Bonus:** +{score['clean_bonus']} pts
            - **Accuracy Bonus:** +{score['accuracy_bonus']} pts
            - **Speed Bonus:** +{score['speed_bonus']} pts
            - **Difficulty Multiplier:** {score['difficulty_multiplier']}x
            """)

        # Achievements
        if st.session_state.achievements_earned:
            st.markdown("---")
            st.markdown("### 🎖️ Achievements Unlocked!")

            for achievement_id in st.session_state.achievements_earned:
                ach = AchievementTracker.get_achievement(achievement_id)
                if ach:
                    st.success(f"{ach.icon} **{ach.name}** - {ach.description} (+{ach.points} pts)")
                    st.balloons()

        # Completion summary
        st.markdown("---")
        completion_time = st.session_state.completion_time
        st.info(f"✨ Completed in {completion_time // 60}:{completion_time % 60:02d} | Accuracy: {score['accuracy']}% | Score: {score['final_score']} pts")

# Chat/Messages Container
if st.session_state.chat_messages and st.session_state.challenge_stage not in ["start", "scoring"]:
    st.markdown("---")
    st.markdown("### 💬 Messages")
    chat_container = st.container(height=300, border=True)

    with chat_container:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"], avatar=msg["avatar"]):
                st.markdown(msg["content"])
