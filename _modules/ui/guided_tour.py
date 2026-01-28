"""Guided Tour - Interactive tutorial using Streamlit Session State (No JavaScript).

Provides step-by-step guidance for first-time users through the app's
main features using pure Streamlit session state and UI components.
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TourStep:
    """Represents a single step in the guided tour."""
    id: int
    title: str
    description: str
    target: str  # Which UI element this step refers to
    position: str  # Where to display the tooltip
    
    
# Define the tour steps
TOUR_STEPS = [
    TourStep(
        id=1,
        title="Welcome to MedBillDozer!",
        description="👋 Hi! I'm Billy, and with my partner Billie, we'll help you find hidden errors in medical bills. Let's get started!",
        target="logo",
        position="top"
    ),
    TourStep(
        id=2,
        title="Demo Documents",
        description="📋 Here are sample medical bills you can try. Expand any document and click the Copy button to copy it to your clipboard, then paste it below for analysis.",
        target="demo_section",
        position="top"
    ),
    TourStep(
        id=3,
        title="Document Input",
        description="✍️ Paste your medical bill, pharmacy receipt, or insurance statement here. You can add multiple documents to compare.",
        target="text_input",
        position="top"
    ),
    TourStep(
        id=4,
        title="Add Multiple Documents",
        description="➕ Click here to add multiple documents for comparison analysis.",
        target="add_document",
        position="top"
    ),
    TourStep(
        id=5,
        title="Start Analysis",
        description="🔍 Once you've pasted your document, click here to start the analysis. I'll check for billing errors, overcharges, and coding mistakes.",
        target="analyze_button",
        position="top"
    ),
    TourStep(
        id=6,
        title="Sidebar Navigation",
        description="💬 Use the sidebar to ask Billy or Billie questions about your bills, view your health profile, or import data from providers.",
        target="sidebar",
        position="main"
    ),
    TourStep(
        id=7,
        title="Your Profile",
        description="👤 View and manage your health profile, including insurance coverage and provider information.",
        target="profile_button",
        position="sidebar"
    ),
    TourStep(
        id=8,
        title="Profile Management",
        description="👤 In the Profile view, you can manage your health insurance details, track provider information, and save your medical history for faster analysis. This helps us give you more accurate insights!",
        target="profile_section",
        position="main"
    ),
    TourStep(
        id=9,
        title="API Integration",
        description="🔌 Built for healthcare and insurance workflows. MedBillDozer's API enables programmatic data ingestion and quality validation of medical records, powered by MedGemma's healthcare-aligned LLM and designed for claims and audit pipelines.",
        target="api_button",
        position="sidebar"
    ),
]


def initialize_tour_state():
    """Initialize tour-related session state variables."""
    if 'tour_active' not in st.session_state:
        st.session_state.tour_active = False
    if 'tour_completed' not in st.session_state:
        st.session_state.tour_completed = False
    if 'tour_current_step' not in st.session_state:
        st.session_state.tour_current_step = 1
    if 'tour_paused' not in st.session_state:
        st.session_state.tour_paused = False
    if 'start_tour_now' not in st.session_state:
        st.session_state.start_tour_now = False


def maybe_launch_tour():
    """Launch tour if conditions are met (after splash and privacy)."""
    if st.session_state.get('splash_dismissed', False) and st.session_state.get('privacy_acknowledged', False) and not st.session_state.get('tour_completed', False) and not st.session_state.get('tour_active', False):
        activate_tour()


def activate_tour():
    """Activate the guided tour (called after splash screen dismissal)."""
    st.session_state.tour_active = True
    st.session_state.start_tour_now = True
    st.session_state.tour_current_step = 1
    st.session_state.tour_paused = False


def get_current_step() -> Optional[TourStep]:
    """Get the current tour step."""
    if not st.session_state.get('tour_active', False):
        return None
    step_num = st.session_state.get('tour_current_step', 1)
    for step in TOUR_STEPS:
        if step.id == step_num:
            return step
    return None


def advance_tour_step():
    """Move to the next step in the tour."""
    current = st.session_state.get('tour_current_step', 1)
    if current < len(TOUR_STEPS):
        st.session_state.tour_current_step = current + 1
    else:
        complete_tour()


def previous_tour_step():
    """Move to the previous step in the tour."""
    current = st.session_state.get('tour_current_step', 1)
    if current > 1:
        st.session_state.tour_current_step = current - 1


def complete_tour():
    """Mark the tour as completed."""
    st.session_state.tour_completed = True
    st.session_state.tour_active = False
    st.session_state.tour_current_step = 1


def skip_tour():
    """Skip the tour."""
    complete_tour()


def run_guided_tour_runtime():
    """Runs guided tour using Streamlit session state.  Call ONCE per rerun, AFTER main UI render."""
    tour_active = st.session_state.get("tour_active", False)
    if not tour_active:
        if st.sidebar.button("🚀 Start Guided Tour", key="manual_tour_start"):
            activate_tour()
            st.rerun()
        return
    current_step = get_current_step()
    if not current_step:
        return
    
    # Show tour in sidebar for natural sticky behavior
    with st.sidebar:
        st.markdown("---")
        st.info(f"""
**Step {current_step.id} of {len(TOUR_STEPS)}: {current_step.title}**

{current_step.description}
""")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if current_step.id > 1:
                if st.button("← Back", key="tour_back", use_container_width=True):
                    previous_tour_step()
                    st.rerun()
        with col2:
            if current_step.id < len(TOUR_STEPS):
                if st.button("Next →", key="tour_next", use_container_width=True):
                    advance_tour_step()
                    st.rerun()
            else:
                if st.button("✓ Done", key="tour_done", use_container_width=True):
                    complete_tour()
                    st.rerun()
        with col3:
            if st.button("Skip", key="tour_skip", use_container_width=True):
                skip_tour()
                st.rerun()
        
        st.markdown("---")


def show_tour_step_hint(step_target: str):
    """Show a visual hint for a specific tour step target."""
    if not st.session_state.get('tour_active', False):
        return
    current_step = get_current_step()
    if not current_step or current_step.target != step_target:
        return
    st.info(f"**{current_step.title}**: {current_step.description}")


def tour_step_marker(step_target: str):
    """Mark a UI element as a tour target and show hint if it's the current step."""
    if not st.session_state.get('tour_active', False):
        return
    current_step = get_current_step()
    if not current_step or current_step.target != step_target:
        return
    st.markdown(f"""<div style="border: 3px solid #667eea; border-radius: 8px; padding: 10px; margin: 10px 0; background: rgba(102, 126, 234, 0.05); box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);"><strong style="color: #667eea;">📍 {current_step.title}</strong><br/>{current_step.description}</div>""", unsafe_allow_html=True)


# Compatibility functions for existing code
def check_tour_progression():
    """Compatibility - handled by session state."""
    pass

def render_tour_widget():
    """Compatibility - handled by run_guided_tour_runtime."""
    pass

def render_tour_controls():
    """Compatibility - handled by run_guided_tour_runtime."""
    pass

def open_sidebar_for_tour():
    """Compatibility - Streamlit handles sidebar state."""
    pass

def install_paste_detector():
    """Compatibility - no longer needed."""
    pass

def install_copy_button_detector():
    """Compatibility - no longer needed."""
    pass

def check_pharmacy_copy_click():
    """Compatibility - no longer needed."""
    pass

def install_tour_highlight_styles():
    """Compatibility - no longer needed."""
    pass

def highlight_tour_elements():
    """Compatibility - no longer needed."""
    pass

def open_and_scroll_pipeline_workflow_step6():
    """Compatibility - no longer needed."""
    pass


# Enhanced API for better integration
def is_tour_on_step(step_id: int) -> bool:
    """Check if the tour is currently on a specific step."""
    return (st.session_state.get('tour_active', False) and st.session_state.get('tour_current_step', 1) == step_id)


def is_tour_on_target(target: str) -> bool:
    """Check if the tour is currently focused on a specific target."""
    if not st.session_state.get('tour_active', False):
        return False
    current_step = get_current_step()
    return current_step is not None and current_step.target == target


def get_tour_progress() -> Tuple[int, int]:
    """Get the current tour progress."""
    if not st.session_state.get('tour_active', False):
        return (0, len(TOUR_STEPS))
    return (st.session_state.get('tour_current_step', 1), len(TOUR_STEPS))


def pause_tour():
    """Pause the tour temporarily."""
    st.session_state.tour_paused = True


def resume_tour():
    """Resume a paused tour."""
    st.session_state.tour_paused = False


def is_tour_paused() -> bool:
    """Check if the tour is currently paused."""
    return st.session_state.get('tour_paused', False)
