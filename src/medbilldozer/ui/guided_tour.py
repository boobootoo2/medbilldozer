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
from medbilldozer.ui.audio_controls import is_audio_muted

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
        title="What MedBillDozer Does",
        description=(
            "👋 If you’ve ever tried to reconcile a medical bill and an insurance explanation "
            "at the same time, you understand the frustration. "
            "MedBillDozer turns that manual reconciliation into a structured, transparent workflow."
        ),
        narration=(
            "If you’ve ever tried to reconcile a medical bill and an insurance explanation "
            "at the same time, you understand the frustration. "
            "MedBillDozer turns that manual reconciliation into a structured, transparent workflow."
        ),
        target="logo",
        position="top"
    ),

    TourStep(
        id=2,
        title="Multi-Document Analysis",
        description=(
            "📄 You can load multiple documents at once. The system compares what was billed, "
            "what was covered, and what was paid across providers and dates of service. "
            "All processing runs through a deterministic pipeline — meaning the same input "
            "always produces the same result."
        ),
        narration=(
            "You can load multiple documents at once. The system compares what was billed, "
            "what was covered, and what was paid across providers and dates of service. "
            "All processing runs through a deterministic pipeline — meaning the same input "
            "always produces the same result."
        ),
        target="demo_section",
        position="top",
    ),

    TourStep(
        id=3,
        title="Intelligent Validation",
        description=(
            "🧠 During analysis, the system flags potential inconsistencies, duplicate charges, "
            "and reimbursement gaps. An AI model evaluates the medical and billing context "
            "to validate findings and surface issues that would be difficult to detect manually."
        ),
        narration=(
            "During analysis, the system flags potential inconsistencies, duplicate charges, "
            "and reimbursement gaps. An AI model evaluates the medical and billing context "
            "to validate findings and surface issues that would be difficult to detect manually."
        ),
        target="results_section",
        position="main"
    ),

    TourStep(
        id=4,
        title="Actionable Workflow",
        description=(
            "📌 Flagged issues are not just displayed — they become actionable. Users can mark "
            "findings as Follow-up, Ignore, or Resolved. This transforms billing review from "
            "a static report into an organized workflow. Documents persist state across "
            "sessions so users can track what still needs attention."
        ),
        narration=(
            "Flagged issues are not just displayed — they become actionable. Users can mark "
            "findings as Follow-up, Ignore, or Resolved. This transforms billing review from "
            "a static report into an organized workflow. Documents persist state across "
            "sessions so users can track what still needs attention."
        ),
        target="production_workflow",
        position="top"
    ),

    TourStep(
        id=5,
        title="Vision",
        description=(
            "✨ This proof of concept demonstrates how billing error detection can become "
            "transparent, auditable, and consumer-controlled. By combining structured ingestion, "
            "deterministic processing, and intelligent validation, billing review becomes "
            "manageable instead of overwhelming."
        ),
        narration=(
            "This proof of concept demonstrates how billing error detection can become "
            "transparent, auditable, and consumer-controlled. By combining structured ingestion, "
            "deterministic processing, and intelligent validation, billing review becomes "
            "manageable instead of overwhelming."
        ),
        target="logo",
        position="top"
    ),

    TourStep(
        id=6,
        title="MedBillDozer Challenge",
        description=(
            "🏆 Test your skills with the MedBillDozer Challenge! We've curated real-world "
            "medical billing scenarios with hidden errors, duplicate charges, and discrepancies. "
            "See if you can identify all the issues before the AI does. Challenge datasets are "
            "available in the demo section with increasing difficulty levels."
        ),
        narration=(
            "Test your skills with the MedBillDozer Challenge! We've curated real-world "
            "medical billing scenarios with hidden errors, duplicate charges, and discrepancies. "
            "See if you can identify all the issues before the AI does. Challenge datasets are "
            "available in the demo section with increasing difficulty levels."
        ),
        target="demo_section",
        position="top"
    ),

    TourStep(
        id=7,
        title="Production Stability Benchmarks",
        description=(
            "📊 MedBillDozer maintains production stability through continuous benchmarking. "
            "Every pipeline component is validated against test cases with known outcomes. "
            "Performance metrics track processing speed, accuracy rates, and error detection "
            "sensitivity. View real-time benchmarks to understand system reliability and data quality."
        ),
        narration=(
            "MedBillDozer maintains production stability through continuous benchmarking. "
            "Every pipeline component is validated against test cases with known outcomes. "
            "Performance metrics track processing speed, accuracy rates, and error detection "
            "sensitivity. View real-time benchmarks to understand system reliability and data quality."
        ),
        target="production_workflow",
        position="top"
    ),

    TourStep(
        id=8,
        title="Full Web Application",
        description=(
            "🖥️ The production web application at medbilldozer.vercel.app provides the complete MedBillDozer experience. "
            "Built with React and a FastAPI backend deployed on Cloud Run, the full application offers "
            "document upload, advanced analysis features, and comprehensive workflow management. "
            "It's designed for seamless interaction with complete functionality and production-grade reliability."
        ),
        narration=(
            "The production web application at medbilldozer.vercel.app provides the complete MedBillDozer experience. "
            "Built with React and a FastAPI backend deployed on Cloud Run, the full application offers "
            "document upload, advanced analysis features, and comprehensive workflow management. "
            "It's designed for seamless interaction with complete functionality and production-grade reliability."
        ),
        target="prototype_interface",
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
