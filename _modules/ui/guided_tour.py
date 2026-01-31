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
            "understand the problem this project is designed to solve."
        ),
        narration=(
            "Welcome to MedBillDozer. If you have ever tried to reconcile a medical bill, "
            "an insurance explanation, and a pharmacy receipt at the same time, you already "
            "understand the problem this project is designed to solve."
        ),
        target="logo",
        position="top"
    ),

    TourStep(
        id=2,
        title="Demo Documents",
        description=(
            "📋 These sample documents reflect the kinds of healthcare paperwork people deal "
            "with every day, including hospital bills, pharmacy receipts, dental statements, "
            "FSA summaries, and insurance claim histories."
        ),
        narration=(
            "These sample documents reflect the kinds of healthcare paperwork people deal "
            "with every day, including hospital bills, pharmacy receipts, dental statements, "
            "FSA summaries, and insurance claim histories."
        ),
        target="demo_section",
        position="top"
    ),

    TourStep(
        id=3,
        title="Document Input",
        description=(
            "✍️ Documents are ingested exactly as they appear in the real world, as raw text "
            "copied from portals, PDFs, or statements, without requiring predefined templates."
        ),
        narration=(
            "Documents are ingested exactly as they appear in the real world, as raw text "
            "copied from portals, PDFs, or statements, without requiring predefined templates."
        ),
        target="text_input",
        position="top"
    ),

    TourStep(
        id=4,
        title="Multi-Document Analysis",
        description=(
            "➕ Adding multiple documents allows the system to compare what was billed, what "
            "was covered, and what was paid across providers and dates of service."
        ),
        narration=(
            "Adding multiple documents allows the system to compare what was billed, what "
            "was covered, and what was paid across providers and dates of service."
        ),
        target="add_document",
        position="top"
    ),

    TourStep(
        id=5,
        title="Analysis Engine Selection",
        description=(
            "⚙️ Analysis is intentionally separated from ingestion, allowing deterministic "
            "fact extraction first and healthcare-aware reasoning only where it adds value."
        ),
        narration=(
            "Analysis is intentionally separated from ingestion, allowing deterministic "
            "fact extraction first and healthcare-aware reasoning only where it adds value."
        ),
        target="analysis_engine",
        position="top"
    ),

    TourStep(
        id=6,
        title="Deterministic Analysis Pipeline",
        description=(
            "🔍 When analysis begins, documents follow a predictable path: classification, "
            "fact extraction, normalization, and validation. Because the same inputs always "
            "produce the same outputs, data scientists and engineers refer to this property "
            "as idempotency."
        ),
        narration=(
            "When analysis begins, documents follow a predictable path: classification, "
            "fact extraction, normalization, and validation. Because the same inputs always "
            "produce the same outputs, data scientists and engineers refer to this property "
            "as idempotency."
        ),
        target="analyze_button",
        position="top"
    ),

    TourStep(
        id=7,
        title="Pipeline Observability",
        description=(
            "📊 You can expand the execution graph to inspect how each step ran. Data scientists "
            "and engineers call this a DAG, or Directed Acyclic Graph, which simply means the "
            "workflow flows forward with no hidden loops or ambiguity."
        ),
        narration=(
            "You can expand the execution graph to inspect how each step ran. Data scientists "
            "and engineers call this a DAG, or Directed Acyclic Graph, which simply means the "
            "workflow flows forward with no hidden loops or ambiguity."
        ),
        target="pipeline_dag",
        position="main"
    ),

    TourStep(
        id=8,
        title="Analysis Findings",
        description=(
            "📌 Findings highlight potential billing errors, duplicate charges, coverage "
            "mismatches, and anomalies that are difficult to catch through manual review."
        ),
        narration=(
            "Findings highlight potential billing errors, duplicate charges, coverage "
            "mismatches, and anomalies that are difficult to catch through manual review."
        ),
        target="results_section",
        position="main"
    ),

    TourStep(
        id=9,
        title="Sidebar Navigation",
        description=(
            "💬 The sidebar acts as a control center where users can ask questions, navigate "
            "the system, and understand why specific conclusions were reached."
        ),
        narration=(
            "The sidebar acts as a control center where users can ask questions, navigate "
            "the system, and understand why specific conclusions were reached."
        ),
        target="sidebar",
        position="main"
    ),

    TourStep(
        id=10,
        title="Health Profile",
        description=(
            "👤 The Health Profile stores insurance coverage and provider relationships so "
            "documents can be interpreted with the right context."
        ),
        narration=(
            "The Health Profile stores insurance coverage and provider relationships so "
            "documents can be interpreted with the right context."
        ),
        target="profile_button",
        position="sidebar"
    ),

    TourStep(
        id=11,
        title="Profile Management",
        description=(
            "👤 Over time, this persistent context allows the system to validate new documents "
            "against historical information instead of starting from scratch."
        ),
        narration=(
            "Over time, this persistent context allows the system to validate new documents "
            "against historical information instead of starting from scratch."
        ),
        target="profile_section",
        position="main"
    ),

    TourStep(
        id=12,
        title="Healthcare-Ready API",
        description=(
            "🔌 Everything demonstrated here is exposed through an API, making it possible to "
            "embed the same reconciliation and validation logic into healthcare and insurance systems."
        ),
        narration=(
            "Everything demonstrated here is exposed through an API, making it possible to "
            "embed the same reconciliation and validation logic into healthcare and insurance systems."
        ),
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
