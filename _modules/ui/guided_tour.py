"""Guided Tour - Interactive tutorial with Billy/Billie narration.

Provides step-by-step guidance for first-time users through the app's
main features using state-based progression and avatar narration.
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, List, Optional
import yaml
from pathlib import Path


# Tutorial step definitions
TUTORIAL_STEPS = [
    "welcome",
    "upload_prompt",
    "document_loaded",
    "analysis_running",
    "review_issues",
    "coverage_matrix",
    "next_actions",
    "tour_complete",
]

# Tutorial messages for each step
TUTORIAL_MESSAGES = {
    "welcome": {
        "character": "billie",
        "message": "Hi! I'm Billie D., your guide to finding hidden errors in medical bills. Let me show you how this works!",
        "action_prompt": "Ready to begin",
    },
    "upload_prompt": {
        "character": "billie",
        "message": "First, scroll to the Hospital Bill – Colonoscopy section and click Copy. Next, scroll down to Analyze a Document, paste the text, and click Analyze Document to start checking for billing errors.",
        "action_prompt": "Copy demo, paste into Document 1",
    },
    "document_loaded": {
        "character": "billy",
        "message": "Great — I can see the document text now. Scroll down and click the Analyze Document button to start checking for billing errors.",
        "action_prompt": "Click Analyze Document",
    },
    "analysis_running": {
        "character": "billie",
        "message": "I'm examining your document right now. Watch the workflow diagram to see what I'm checking: document type, line items, and billing issues.",
        "action_prompt": "Analysis in progress...",
    },
    "review_issues": {
        "character": "billy",
        "message": "Here are the results! Each issue shows what might be wrong and how much you could save. Expand any section to see more details.",
        "action_prompt": "Review the findings",
    },
    "coverage_matrix": {
        "character": "billie",
        "message": "Want to track multiple bills? The coverage matrix helps you see all your medical expenses across different providers and dates.",
        "action_prompt": "Explore the coverage matrix",
    },
    "next_actions": {
        "character": "billy",
        "message": "You can analyze more documents, ask Billy or Billie questions using the assistant sidebar, or copy results to share with your provider.",
        "action_prompt": "Analyze another document",
    },
    "tour_complete": {
        "character": "billie",
        "message": "That's it! You're all set. If you need help anytime, just ask using the assistant in the sidebar. Good luck!",
        "action_prompt": "Exit tour",
    },
}


def load_tour_config() -> Dict:
    """Load guided tour configuration from app_config.yaml."""
    config_path = Path(__file__).parent.parent.parent / "app_config.yaml"

    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('features', {}).get('guided_tour', {})

    return {
        'enabled': False,
        'auto_launch_for_new_users': True,
        'default_narrator': 'billie',
        'widget_position': 'top',
        'show_skip_button': True,
    }


def initialize_tour_state():
    """Initialize tour session state variables."""
    if 'tour_active' not in st.session_state:
        st.session_state.tour_active = False

    if 'tutorial_step' not in st.session_state:
        st.session_state.tutorial_step = "welcome"

    if 'tour_completed' not in st.session_state:
        st.session_state.tour_completed = False

    if 'is_first_visit' not in st.session_state:
        st.session_state.is_first_visit = True


def start_tour():
    """Start the guided tour."""
    st.session_state.tour_active = True
    st.session_state.tutorial_step = "welcome"
    st.session_state.show_billdozer_widget = True
    st.session_state.avatar_character = TUTORIAL_MESSAGES["welcome"]["character"]
    st.session_state.tour_sidebar_should_open = True


def end_tour():
    """End the guided tour."""
    st.session_state.tour_active = False
    st.session_state.tour_completed = True
    st.session_state.show_billdozer_widget = False


def advance_tour_step(next_step: str):
    """Advance to the next tutorial step.

    Args:
        next_step: The next tutorial step to advance to
    """
    if next_step in TUTORIAL_STEPS:
        st.session_state.tutorial_step = next_step

        # Switch narrator if needed
        if next_step in TUTORIAL_MESSAGES:
            character = TUTORIAL_MESSAGES[next_step]["character"]
            st.session_state.avatar_character = character


def check_tour_progression():
    """Check app state and automatically advance tour steps when appropriate."""
    if not st.session_state.get('tour_active', False):
        return

    current_step = st.session_state.get('tutorial_step', 'welcome')

    # Auto-advance based on state changes
    if current_step == "upload_prompt":
        # Check if document has been loaded (text pasted into text area)
        # Check the actual document input field
        doc_input_0 = st.session_state.get('doc_input_0', '')

        # Consider document loaded if there's substantial text (more than 50 chars)
        if doc_input_0 and len(doc_input_0.strip()) > 50:
            # Track that we detected the text to avoid re-triggering
            if not st.session_state.get('tour_text_detected', False):
                st.session_state.tour_text_detected = True
                advance_tour_step("document_loaded")
                st.rerun()

    elif current_step == "document_loaded":
        # Check if analysis has started (analyzing flag set)
        if st.session_state.get('analyzing', False):
            advance_tour_step("analysis_running")
        # Handle case where analysis completed without intermediate rerun
        elif st.session_state.get('doc_results', False) and not st.session_state.get('analyzing', False):
            advance_tour_step("review_issues")

    elif current_step == "analysis_running":
        # Check if analysis is complete
        if st.session_state.get('doc_results') and not st.session_state.get('analyzing', False):
            advance_tour_step("review_issues")

    elif current_step == "review_issues":
        # User can manually advance or we wait for them to explore results
        pass

    elif current_step == "tour_complete":
        # Auto-end tour after showing final message
        end_tour()


def get_tour_message() -> Optional[Dict]:
    """Get the current tour message based on tutorial step.

    Returns:
        Dict with character, message, and action_prompt, or None if tour not active
    """
    if not st.session_state.get('tour_active', False):
        return None

    current_step = st.session_state.get('tutorial_step', 'welcome')
    return TUTORIAL_MESSAGES.get(current_step)


def render_tour_widget():
    """Render the guided tour widget with narrator guidance in the sidebar."""
    tour_config = load_tour_config()

    if not tour_config.get('enabled', False):
        return

    if not st.session_state.get('tour_active', False):
        return

    tour_message = get_tour_message()
    if not tour_message:
        return

    current_step = st.session_state.get('tutorial_step', 'welcome')
    show_skip = tour_config.get('show_skip_button', True)

    # Render tour guidance in sidebar
    with st.sidebar:
        # Tour message box with gradient background
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            padding: 16px;
            color: white;
            margin-bottom: 16px;
        ">
            <div style="font-weight: 700; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
                {tour_message['character'].capitalize()} says:
            </div>
            <div style="font-size: 14px; line-height: 1.5; margin-bottom: 12px;">
                {tour_message['message']}
            </div>
            <div style="font-size: 12px; opacity: 0.9;">
                <strong>Next:</strong> {tour_message['action_prompt']}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_tour_controls():
    """Render tour control buttons in sidebar."""
    if not st.session_state.get('tour_active', False):
        return

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📚 Guided Tour")

        current_step = st.session_state.get('tutorial_step', 'welcome')
        step_index = TUTORIAL_STEPS.index(current_step) if current_step in TUTORIAL_STEPS else 0

        # Show progress
        st.progress(step_index / (len(TUTORIAL_STEPS) - 1))
        st.caption(f"Step {step_index + 1} of {len(TUTORIAL_STEPS)}: {current_step.replace('_', ' ').title()}")
        st.markdown("")

        col1, col2 = st.columns(2)

        with col1:
            # Next step button (for manual advancement on exploration steps)
            # Show Continue for welcome and exploration steps
            manual_steps = ["welcome", "review_issues", "coverage_matrix", "next_actions"]
            if current_step in manual_steps and step_index < len(TUTORIAL_STEPS) - 1:
                if st.button("Continue ▶", key="tour_next", use_container_width=True):
                    next_step = TUTORIAL_STEPS[step_index + 1]
                    advance_tour_step(next_step)
                    st.rerun()

        with col2:
            # End tour button
            if st.button("Exit Tour", key="tour_end", use_container_width=True):
                end_tour()
                st.rerun()

        # Add a "Restart Tour" option
        st.markdown("")
        if st.button("🔄 Restart Tour", key="tour_restart", use_container_width=True):
            start_tour()
            st.rerun()


def should_auto_launch_tour() -> bool:
    """Determine if tour should auto-launch for new users.

    Returns:
        True if tour should launch, False otherwise
    """
    tour_config = load_tour_config()

    if not tour_config.get('enabled', False):
        return False

    if not tour_config.get('auto_launch_for_new_users', True):
        return False

    # Check if this is first visit and tour hasn't been completed
    is_first = st.session_state.get('is_first_visit', True)
    completed = st.session_state.get('tour_completed', False)

    return is_first and not completed


def maybe_launch_tour():
    """Auto-launch tour for new users if configured."""
    if should_auto_launch_tour():
        start_tour()
        st.session_state.is_first_visit = False


# Install message bridge for tour events


def install_tour_bridge():
    """Install JavaScript bridge to handle tour events from widget."""
    components.html(
        """
        <script>
        (function() {
            window.addEventListener('message', function(event) {
                if (event.data && event.data.type === 'TOUR_END') {
                    // Signal Streamlit to end tour
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {action: 'end_tour'}
                    }, '*');
                }
            });
        })();
        </script>
        """,
        height=0,
    )


def open_sidebar_for_tour():
    """Open the sidebar automatically when tour is active."""
    if not st.session_state.get('tour_active', False):
        return

    if not st.session_state.get('tour_sidebar_opened', False):
        components.html(
            """
            <script>
            (function() {
                // Find and click the sidebar expand button if sidebar is collapsed
                const expandButton = window.parent.document.querySelector('button[data-testid="stExpandSidebarButton"]');
                if (expandButton && expandButton.offsetParent !== null) {
                    // Button is visible, meaning sidebar is collapsed
                    setTimeout(function() {
                        expandButton.click();
                    }, 100);
                }
            })();
            </script>
            """,
            height=0,
        )
        st.session_state.tour_sidebar_opened = True

