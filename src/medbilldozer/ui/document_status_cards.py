"""Real-time document processing status cards with progress tracking."""

import time
import streamlit as st
from typing import Optional, Dict, Any

# Phase mapping with icons, labels, and order
PHASE_MAP = {
    "pre_extraction_active": {"icon": "🔍", "label": "Pre-Extraction", "desc": "Classifying document", "order": 1},
    "extraction_active": {"icon": "📋", "label": "Fact Extraction", "desc": "Extracting information", "order": 2},
    "line_items_active": {"icon": "📊", "label": "Line Items", "desc": "Parsing line items", "order": 3},
    "analysis_active": {"icon": "🔬", "label": "Issue Analysis", "desc": "Analyzing issues", "order": 4},
    "complete": {"icon": "✅", "label": "Complete", "desc": "Analysis finished", "order": 5},
    "failed": {"icon": "❌", "label": "Failed", "desc": "Error occurred", "order": -1}
}

# All phases in order
ALL_PHASES = ["pre_extraction_active", "extraction_active", "line_items_active", "analysis_active", "complete"]


def initialize_document_status(doc_id: str, friendly_name: Optional[str] = None):
    """Initialize session state tracking for a document.

    Args:
        doc_id: Unique document identifier (e.g., "doc_1")
        friendly_name: Optional human-readable document name
    """
    if 'doc_status_tracking' not in st.session_state:
        st.session_state.doc_status_tracking = {}

    st.session_state.doc_status_tracking[doc_id] = {
        "document_id": doc_id,
        "friendly_name": friendly_name or doc_id,
        "status": "analyzing",  # analyzing, complete, failed
        "start_time": time.time(),
        "current_phase": "pre_extraction_active",
        "completed_phases": [],
        "error_message": None,
        "last_update": time.time(),
        "phase_times": {}  # Track time spent in each phase
    }


def create_status_card_placeholder(doc_id: str):
    """Create st.empty() placeholder for live updates.

    Args:
        doc_id: Document identifier

    Returns:
        Streamlit placeholder object for updating
    """
    placeholder = st.empty()

    # Render initial status
    with placeholder.container():
        doc_data = st.session_state.doc_status_tracking.get(doc_id, {})
        render_status_card_content(doc_data, 0.0)

    return placeholder


def update_status_card(placeholder, doc_id: str, phase: str, workflow_log: Optional[Dict[str, Any]] = None):
    """Update the status card placeholder with current phase.

    Args:
        placeholder: Streamlit placeholder to update
        doc_id: Document identifier
        phase: Current phase (e.g., "extraction_active", "complete", "failed")
        workflow_log: Optional workflow log for detailed info
    """
    if doc_id not in st.session_state.doc_status_tracking:
        return

    doc_data = st.session_state.doc_status_tracking[doc_id]
    current_time = time.time()

    # Track time for previous phase
    prev_phase = doc_data.get("current_phase")
    if prev_phase and prev_phase != phase:
        phase_elapsed = current_time - doc_data.get("last_update", current_time)
        doc_data["phase_times"][prev_phase] = phase_elapsed

        # Add to completed phases
        if prev_phase not in doc_data["completed_phases"] and phase != "failed":
            doc_data["completed_phases"].append(prev_phase)

    # Update current phase
    doc_data["current_phase"] = phase
    doc_data["last_update"] = current_time

    # Update status based on phase
    if phase == "complete":
        doc_data["status"] = "complete"
        if phase not in doc_data["completed_phases"]:
            doc_data["completed_phases"].append(phase)
    elif phase == "failed":
        doc_data["status"] = "failed"

    # Calculate elapsed time
    elapsed = current_time - doc_data["start_time"]

    # Render updated card
    with placeholder.container():
        render_status_card_content(doc_data, elapsed)


def render_status_card_content(doc_data: Dict[str, Any], elapsed_seconds: float):
    """Build and render the visual status card.

    Args:
        doc_data: Document status data from session state
        elapsed_seconds: Total elapsed time in seconds
    """
    doc_name = doc_data.get("friendly_name", doc_data.get("document_id", "Document"))
    status = doc_data.get("status", "analyzing")
    current_phase = doc_data.get("current_phase", "pre_extraction_active")
    completed_phases = doc_data.get("completed_phases", [])
    error_message = doc_data.get("error_message")
    phase_times = doc_data.get("phase_times", {})

    # Container with border and padding
    with st.container():
        # Header row with document name and timer
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            if status == "complete":
                st.markdown(f"### ✅ {doc_name}")
            elif status == "failed":
                st.markdown(f"### ❌ {doc_name}")
            else:
                st.markdown(f"### 📄 {doc_name}")

        with col2:
            st.markdown(f"**⏱️ {format_elapsed_time(elapsed_seconds)}**")

        with col3:
            # Calculate progress percentage
            progress = calculate_progress(current_phase, completed_phases, status)
            st.progress(progress)

        st.divider()

        # Error banner if failed
        if status == "failed" and error_message:
            st.error(f"**Error:** {error_message}")

        # Phase checklist
        st.markdown("**Pipeline Progress:**")

        for phase_key in ALL_PHASES:
            phase_info = PHASE_MAP.get(phase_key, {})
            icon = phase_info.get("icon", "⏳")
            label = phase_info.get("label", phase_key)
            desc = phase_info.get("desc", "")

            # Determine phase display
            if phase_key in completed_phases:
                # Completed phase - show checkmark and time
                phase_time = phase_times.get(phase_key, 0.0)
                time_str = f" ({format_elapsed_time(phase_time)})" if phase_time > 0 else ""
                st.markdown(f"✅ **{label}**{time_str}")
            elif phase_key == current_phase:
                # Current active phase
                if status == "failed":
                    st.markdown(f"❌ **{label}** — {error_message or 'Failed'}")
                else:
                    st.markdown(f"🔄 **{label}** — {desc}...")
            else:
                # Pending phase
                st.markdown(f"⏳ {label}")

        # Final status message
        if status == "complete":
            st.success(f"✨ Analysis complete in {format_elapsed_time(elapsed_seconds)}")
        elif status == "analyzing" and current_phase != "failed":
            phase_info = PHASE_MAP.get(current_phase, {})
            st.info(f"🔄 {phase_info.get('desc', 'Processing')}...")


def format_elapsed_time(seconds: float) -> str:
    """Format elapsed seconds as human-readable string.

    Args:
        seconds: Elapsed time in seconds

    Returns:
        Formatted time string (e.g., "12.3s", "2m 15s", "1h 5m")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def calculate_progress(current_phase: str, completed_phases: list, status: str) -> float:
    """Calculate progress percentage based on completed phases.

    Args:
        current_phase: Current active phase
        completed_phases: List of completed phase keys
        status: Current status (analyzing, complete, failed)

    Returns:
        Progress value between 0.0 and 1.0
    """
    if status == "complete":
        return 1.0

    if status == "failed":
        # Show progress up to failed phase
        phase_order = PHASE_MAP.get(current_phase, {}).get("order", 0)
        if phase_order > 0:
            return phase_order / len(ALL_PHASES)
        return 0.0

    # Count completed phases
    total_phases = len(ALL_PHASES)
    completed_count = len([p for p in completed_phases if p in ALL_PHASES])

    # Add partial progress for current phase
    current_order = PHASE_MAP.get(current_phase, {}).get("order", 0)
    if current_order > 0 and current_phase not in completed_phases:
        completed_count = current_order - 1  # Phases before current

    return min(completed_count / total_phases, 0.99)  # Never show 100% until complete
