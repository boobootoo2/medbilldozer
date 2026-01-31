"""Guided Tour - Interactive tutorial using Streamlit Session State (No JavaScript).

Provides step-by-step guidance for first-time users through the app's
main features using pure Streamlit session state and UI components.
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import os
from pathlib import Path
import logging
from _modules.ui.audio_controls import is_audio_muted

logger = logging.getLogger(__name__)


@dataclass
class TourStep:
    """Represents a single step in the guided tour."""
    id: int
    title: str
    description: str
    narration: str  # Spoken version for audio playback
    target: str  # Which UI element this step refers to
    position: str  # Where to display the tooltip
    
# Define the tour steps
TOUR_STEPS = [
    TourStep(
        id=1,
        title="Welcome to MedBillDozer",
        description=(
            "👋 Welcome to MedBillDozer. If you have ever tried to reconcile a medical bill, "
            "an insurance explanation, and a pharmacy receipt at the same time, you already "
            "understand the frustration this app is designed to solve. "
            "MedBillDozer turns that manual reconciliation process into a structured, transparent workflow."
        ),
        narration=(
            "Welcome to MedBillDozer. If you have ever tried to reconcile a medical bill, "
            "an insurance explanation, and a pharmacy receipt at the same time, you already "
            "understand the frustration this app is designed to solve. "
            "MedBillDozer turns that manual reconciliation process into a structured, transparent workflow."
        ),
        target="logo",
        position="top"
    ),

    TourStep(
        id=2,
        title="Demo POC Workflow – Copy & Paste",
        description=(
            "📋 This Demo POC workflow lets you lift the hood. Click Copy Document on any sample file "
            "and paste it into the input fields below. You can add additional documents anytime using "
            "the plus icon. This gives you a behind-the-scenes look at how documents move through the pipeline."
        ),
        narration=(
            "This Demo POC workflow lets you lift the hood. Click Copy Document on any sample file "
            "and paste it into the input fields below. You can add additional documents anytime using "
            "the plus icon. This gives you a behind-the-scenes look at how documents move through the pipeline."
        ),
        target="demo_section",
        position="top"
    ),

    TourStep(
        id=3,
        title="Multi-Document Observability",
        description=(
            "🔍 When you analyze multiple documents together, the system compares what was billed, "
            "what was covered, and what was paid across providers and dates of service. "
            "You can inspect the execution graph to see exactly how each step runs in a deterministic pipeline."
        ),
        narration=(
            "When you analyze multiple documents together, the system compares what was billed, "
            "what was covered, and what was paid across providers and dates of service. "
            "You can inspect the execution graph to see exactly how each step runs in a deterministic pipeline."
        ),
        target="pipeline_dag",
        position="main"
    ),

    TourStep(
        id=4,
        title="Demo Production Workflow",
        description=(
            "🚀 The Demo Production Workflow simulates a real-world deployment. "
            "Documents are preloaded and structured, minimizing user input. "
            "This reflects how providers or insurance companies could integrate the system at scale."
        ),
        narration=(
            "The Demo Production Workflow simulates a real-world deployment. "
            "Documents are preloaded and structured, minimizing user input. "
            "This reflects how providers or insurance companies could integrate the system at scale."
        ),
        target="production_workflow",
        position="top"
    ),

    TourStep(
        id=5,
        title="Sidebar Navigation & AI Agent",
        description=(
            "💬 The left sidebar acts as your control center. You can navigate the application, "
            "access different workflows, or ask the AI Agent questions about your documents "
            "and flagged findings."
        ),
        narration=(
            "The left sidebar acts as your control center. You can navigate the application, "
            "access different workflows, or ask the AI Agent questions about your documents "
            "and flagged findings."
        ),
        target="sidebar",
        position="main"
    ),

    TourStep(
        id=6,
        title="Profile & Data Import",
        description=(
            "👤 In the Profile section, you can import receipts or structured transaction data "
            "from insurance companies or providers. This allows the system to interpret new "
            "documents with the right coverage and provider context."
        ),
        narration=(
            "In the Profile section, you can import receipts or structured transaction data "
            "from insurance companies or providers. This allows the system to interpret new "
            "documents with the right coverage and provider context."
        ),
        target="profile_section",
        position="main"
    ),

    TourStep(
        id=7,
        title="Re-Analyze Newly Loaded Documents",
        description=(
            "🔄 After importing new data, return to Home and run the Demo Production Workflow again. "
            "The system will now analyze your newly loaded documents using the same structured pipeline."
        ),
        narration=(
            "After importing new data, return to Home and run the Demo Production Workflow again. "
            "The system will now analyze your newly loaded documents using the same structured pipeline."
        ),
        target="analyze_button",
        position="top"
    ),

    TourStep(
        id=8,
        title="Take Action on Findings",
        description=(
            "📌 Once results appear, click Actions on any flagged item to decide next steps. "
            "You can mark it for Follow-up, Ignore it, or mark it as Resolved. "
            "This turns billing review into an actionable workflow instead of a static report."
        ),
        narration=(
            "Once results appear, click Actions on any flagged item to decide next steps. "
            "You can mark it for Follow-up, Ignore it, or mark it as Resolved. "
            "This turns billing review into an actionable workflow instead of a static report."
        ),
        target="results_section",
        position="main"
    ),

    TourStep(
        id=9,
        title="Proof of Concept Vision",
        description=(
            "✨ This demonstration shows how billing error detection can be simplified. "
            "By combining structured ingestion, deterministic workflows, and intelligent validation, "
            "the process becomes transparent, auditable, and manageable."
        ),
        narration=(
            "This demonstration shows how billing error detection can be simplified. "
            "By combining structured ingestion, deterministic workflows, and intelligent validation, "
            "the process becomes transparent, auditable, and manageable."
        ),
        target="logo",
        position="top"
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


def generate_audio_narration(step_id: int, narration_text: str) -> Optional[Path]:
    """Generate audio narration using OpenAI Neural TTS with caching.
    
    Args:
        step_id: The tour step ID
        narration_text: Text to synthesize
        
    Returns:
        Path to audio file, or None if generation fails
    """
    audio_dir = Path("audio")
    audio_dir.mkdir(exist_ok=True)
    
    audio_file = audio_dir / f"tour_step_{step_id}.mp3"
    
    # Return cached file if exists
    if audio_file.exists():
        return audio_file
    
    # Try to generate using OpenAI TTS
    try:
        from openai import OpenAI
        
        # Initialize client (uses OPENAI_API_KEY from environment)
        client = OpenAI()
        
        logger.info(f"Generating audio narration for step {step_id}...")
        
        # Generate speech
        response = client.audio.speech.create(
            model="tts-1",  # Use tts-1 for faster, tts-1-hd for highest quality
            voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
            input=narration_text,
            speed=1.0  # 0.25 to 4.0
        )
        
        # Save to file
        audio_file.write_bytes(response.read())
        logger.info(f"✅ Generated audio: {audio_file}")
        
        return audio_file
        
    except ImportError:
        logger.debug("OpenAI library not available for audio generation")
        return None
    except Exception as e:
        logger.warning(f"Failed to generate audio for step {step_id}: {e}")
        return None


def run_guided_tour_runtime():
    """Runs guided tour using Streamlit session state.  Call ONCE per rerun, from within sidebar context."""
    tour_active = st.session_state.get("tour_active", False)
    if not tour_active:
        if st.button("🚀 Start Guided Tour", key="manual_tour_start", use_container_width=True):
            activate_tour()
            st.rerun()
        return
    current_step = get_current_step()
    if not current_step:
        return
    
    # Show tour (already in sidebar context from caller)
    st.markdown("---")
    
    # Audio narration (generate on-demand with caching, only if not muted)
    audio_file = None
    if not is_audio_muted():
        audio_file = generate_audio_narration(current_step.id, current_step.narration)
        if audio_file and audio_file.exists():
            try:
                st.audio(str(audio_file), format="audio/mp3", autoplay=True)
            except Exception as e:
                # Silently skip if audio playback fails - don't break the tour
                logger.debug(f"Audio playback failed: {e}")
                pass
    
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
    # SECURITY: unsafe_allow_html=True is safe here because:
    # - current_step.title and current_step.description are from TOUR_STEPS (predefined constants)
    # - Both values are HTML-escaped using html.escape() before insertion
    # - safe_title and safe_desc cannot contain executable code after escaping
    # - Used for styled tour step highlighting with custom CSS
    import html
    safe_title = html.escape(str(current_step.title))
    safe_desc = html.escape(str(current_step.description))
    st.markdown(f"""<div style="border: 3px solid #667eea; border-radius: 8px; padding: 10px; margin: 10px 0; background: rgba(102, 126, 234, 0.05); box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);"><strong style="color: #667eea;">📍 {safe_title}</strong><br/>{safe_desc}</div>""", unsafe_allow_html=True)


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
