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
    "copy_first_document",
    "paste_first_document",
    "add_second_document",
    "second_document_loaded",
    "analysis_running",
    "review_issues",
    "coverage_matrix",
    "next_actions",
    "profile_view",
    "import_view",
    "import_now",
    "tour_complete",
]

# Steps that require manual "Continue" advancement
MANUAL_STEPS = [
    "welcome",
    "copy_first_document",
    "review_issues",
    "coverage_matrix",
    "next_actions",
    "profile_view",
    "import_view",
    "import_now",
]

# Tutorial messages for each step
TUTORIAL_MESSAGES = {
    "welcome": {
        "character": "billie",
        "message": "Hi! I'm Billie D., your guide to finding hidden errors in medical bills. Let me show you how this works!",
        "action_prompt": "Ready to begin",
    },
    "copy_first_document": {
        "character": "billie",
        "message": "First, scroll to the Hospital Bill – Colonoscopy section and click Copy.",
        "action_prompt": "Click Copy on Hospital Bill",
    },
    "paste_first_document": {
        "character": "billy",
        "message": "Great! Now scroll down to Analyze a Document and paste the text into Document 1.",
        "action_prompt": "Paste into Document 1",
    },
    "add_second_document": {
        "character": "billy",
        "message": "Perfect! Now let's add a second document. Click 'Add Another Document', then scroll to the Pharmacy Receipt – FSA Claim section, click Copy, and paste into Document 2.",
        "action_prompt": "Add document and paste pharmacy receipt",
    },
    "second_document_loaded": {
        "character": "billy",
        "message": "Excellent! You now have two documents ready. Scroll down and click the Analyze Document button to check both for billing errors.",
        "action_prompt": "Click Analyze Document",
    },
    "analysis_running": {
        "character": "billie",
        "message": "I'm examining your document right now. Click on '📊 Pipeline Workflow: Document Analysis' to expand it and watch the workflow diagram to see what I'm checking: document type, line items, and billing issues.",
        "action_prompt": "Click Pipeline Workflow to watch progress",
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
    "profile_view": {
        "character": "billie",
        "message": "You can see what the profile admissions look like, by clicking the profile button on the sidepanel.",
        "action_prompt": "Profile View",
    },
    "import_view": {
        "character": "billy",
        "message": "You can see how to import documents from health providers and insurance companies by clicking Import Data in the main panel.",
        "action_prompt": "Import View",
    },
    "import_now": {
        "character": "billy",
        "message": "Click the dropdown under Select Entity to choose an insurance company. Select any company and then click Import Now",
        "action_prompt": "Import Now",
    },
    "tour_complete": {
        "character": "billie",
        "message": "That's it! You're all set. If you need help anytime, just ask using the assistant in the sidebar. Good luck!",
        "action_prompt": "Exit tour",
    },
}


def run_guided_tour_runtime():
    """
    Runs guided tour lifecycle in the correct order.
    Call ONCE per rerun, AFTER main UI render.
    """
    if not st.session_state.get("tour_active", False):
        return

    # 1. Progress state machine
    check_tour_progression()

    # 2. UI overlays (sidebar)
    render_tour_widget()
    render_tour_controls()

    # 3. Visual emphasis
    highlight_tour_elements()

    # 4. Step-specific effects
    open_and_scroll_pipeline_workflow_step6()

    # 5. Sidebar control
    open_sidebar_for_tour()


def open_and_scroll_pipeline_workflow_step6():
    """Step 6: Expand Pipeline Workflow accordion and scroll it into view."""
    if not st.session_state.get("tour_active", False):
        return

    if st.session_state.get("tutorial_step") != "analysis_running":
        return

    components.html(
        """
        <script>
        (function () {
            // Prevent running more than once per session
            if (window.__pipelineWorkflowOpened) {
                return;
            }

            function tryOpenWorkflow() {
                const candidates = Array.from(
                    window.parent.document.querySelectorAll('details, div')
                );

                for (let el of candidates) {
                    const text = (el.innerText || '').trim();

                    if (text.startsWith('📊 Pipeline Workflow')) {
                        // 1️⃣ Expand accordion if it's a <details>
                        if (el.tagName === 'DETAILS' && !el.open) {
                            el.open = true;
                        }

                        // 2️⃣ Scroll so top is 10px from viewport
                        const rect = el.getBoundingClientRect();
                        const absoluteTop =
                            rect.top + window.parent.pageYOffset - 10;

                        window.parent.scrollTo({
                            top: absoluteTop,
                            behavior: 'smooth'
                        });

                        // 3️⃣ Optional highlight
                        if (window.parent.highlightElement) {
                            window.parent.highlightElement(el);
                        }

                        window.__pipelineWorkflowOpened = true;
                        console.log('✓ Pipeline Workflow expanded and scrolled');
                        return true;
                    }
                }
                return false;
            }

            // Initial attempt
            if (tryOpenWorkflow()) return;

            // Observe DOM mutations until it appears
            const observer = new MutationObserver(() => {
                if (tryOpenWorkflow()) {
                    observer.disconnect();
                }
            });

            observer.observe(window.parent.document.body, {
                childList: true,
                subtree: true
            });

            // Safety timeout (disconnect after 8s)
            setTimeout(() => observer.disconnect(), 8000);
        })();
        </script>
        """,
        height=0,
    )


def load_tour_config() -> Dict:
    """Load guided tour configuration from app_config.yaml."""
    config_path = Path(__file__).parent.parent.parent / "app_config.yaml"

    if config_path.exists():
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            return config.get("features", {}).get("guided_tour", {})

    return {
        "enabled": False,
        "auto_launch_for_new_users": True,
        "default_narrator": "billie",
        "widget_position": "top",
        "show_skip_button": True,
    }


def initialize_tour_state():
    """Initialize tour session state variables."""
    if "tour_active" not in st.session_state:
        st.session_state.tour_active = False

    if "tutorial_step" not in st.session_state:
        st.session_state.tutorial_step = "welcome"

    if "tour_completed" not in st.session_state:
        st.session_state.tour_completed = False

    if "is_first_visit" not in st.session_state:
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
    if not st.session_state.get("tour_active", False):
        return

    current_step = st.session_state.get("tutorial_step", "welcome")

    # Auto-advance based on state changes
    if current_step == "copy_first_document":
        # Auto-advance to paste step after a short delay (user has copied)
        # This step will be manually advanced or we can detect clipboard
        # For now, user will use Continue button
        pass

    elif current_step == "paste_first_document":
        # Check if first document has been loaded (text pasted into text area)
        doc_input_0 = st.session_state.get("doc_input_0", "")

        # Consider document loaded if there's substantial text (more than 50 chars)
        if doc_input_0 and len(doc_input_0.strip()) > 50:
            # Track that we detected the text to avoid re-triggering
            if not st.session_state.get("tour_first_doc_detected", False):
                st.session_state.tour_first_doc_detected = True
                advance_tour_step("add_second_document")
                st.rerun()

    elif current_step == "add_second_document":
        # Check if second document has been loaded
        doc_input_1 = st.session_state.get("doc_input_1", "")

        if doc_input_1 and len(doc_input_1.strip()) > 50:
            if not st.session_state.get("tour_second_doc_detected", False):
                st.session_state.tour_second_doc_detected = True
                advance_tour_step("second_document_loaded")
                st.rerun()

    elif current_step == "second_document_loaded":
        # Check if analysis has started (analyzing flag set)
        if st.session_state.get("analyzing", False):
            advance_tour_step("analysis_running")
            st.rerun()
        # Handle case where analysis completed without intermediate rerun
        elif st.session_state.get("doc_results", False) and not st.session_state.get(
            "analyzing", False
        ):
            advance_tour_step("review_issues")
            st.rerun()

    elif current_step == "analysis_running":
        # Check if analysis is complete
        if st.session_state.get("doc_results") and not st.session_state.get(
            "analyzing", False
        ):
            advance_tour_step("review_issues")
            st.rerun()

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
    if not st.session_state.get("tour_active", False):
        return None

    current_step = st.session_state.get("tutorial_step", "welcome")
    return TUTORIAL_MESSAGES.get(current_step)


def render_tour_widget():
    """Render the guided tour widget with narrator guidance in the sidebar."""
    tour_config = load_tour_config()

    if not tour_config.get("enabled", False):
        return

    if not st.session_state.get("tour_active", False):
        return

    tour_message = get_tour_message()
    if not tour_message:
        return

    current_step = st.session_state.get("tutorial_step", "welcome")
    show_skip = tour_config.get("show_skip_button", True)

    # Calculate step number
    step_index = (
        TUTORIAL_STEPS.index(current_step) if current_step in TUTORIAL_STEPS else 0
    )
    step_number = step_index + 1
    total_steps = len(TUTORIAL_STEPS)

    # Render tour guidance in sidebar
    with st.sidebar:
        # Tour message box with gradient background
        st.markdown(
            f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            padding: 16px;
            color: white;
            margin-bottom: 16px;
        ">
            <div style="font-size: 11px; opacity: 0.85; margin-bottom: 8px;">
                Step {step_number} of {total_steps}
            </div>
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
        """,
            unsafe_allow_html=True,
        )


def render_tour_controls():
    """Render tour control buttons in sidebar."""
    if not st.session_state.get("tour_active", False):
        return

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📚 Guided Tour")

        current_step = st.session_state.get("tutorial_step", "welcome")
        step_index = (
            TUTORIAL_STEPS.index(current_step) if current_step in TUTORIAL_STEPS else 0
        )

        # Show progress
        st.progress(step_index / (len(TUTORIAL_STEPS) - 1))
        st.caption(
            f"Step {step_index + 1} of {len(TUTORIAL_STEPS)}: {current_step.replace('_', ' ').title()}"
        )
        st.markdown("")

        col1, col2 = st.columns(2)

        with col1:
            # Next step button (for manual advancement on exploration steps)
            # Show Continue for welcome, copy step, and exploration steps
            if current_step in MANUAL_STEPS and step_index < len(TUTORIAL_STEPS) - 1:
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

    if not tour_config.get("enabled", False):
        return False

    if not tour_config.get("auto_launch_for_new_users", True):
        return False

    # Check if this is first visit and tour hasn't been completed
    is_first = st.session_state.get("is_first_visit", True)
    completed = st.session_state.get("tour_completed", False)

    return is_first and not completed


def maybe_launch_tour():
    """Auto-launch tour for new users if configured."""
    if should_auto_launch_tour():
        start_tour()
        st.session_state.is_first_visit = False


# Install message bridge for tour events
def highlight_continue_button_for_manual_steps():
    """Highlight the Continue button during manual tour steps.
    This function provides continuous highlighting for the Continue button
    on all manual steps to ensure visibility.
    """
    if not st.session_state.get("tour_active", False):
        return

    current_step = st.session_state.get("tutorial_step")

    if current_step not in MANUAL_STEPS:
        return

    components.html(
        f"""
        <script>
        (function () {{
            const stepName = '{current_step}';
            let intervalId;
            let foundCount = 0;

            function highlightContinueButton() {{
                const buttons = window.parent.document.querySelectorAll('button');
                let found = false;

                for (let btn of buttons) {{
                    const text = (btn.innerText || btn.textContent || '').trim();

                    if (text.includes('Continue') && text.includes('▶')) {{
                        found = true;
                        // Use the global highlightElement function for consistent styling
                        if (window.parent.highlightElement) {{
                            window.parent.highlightElement(btn);
                            foundCount++;
                            if (foundCount === 1) {{
                                console.log('✓ Highlighted Continue button (step: ' + stepName + ')');
                            }}
                        }}
                        break;
                    }}
                }}

                // If found a few times, we can stop checking
                if (foundCount > 3) {{
                    clearInterval(intervalId);
                }}

                return found;
            }}

            // Highlight immediately
            highlightContinueButton();

            // Then keep checking every 500ms to re-apply highlight
            intervalId = setInterval(highlightContinueButton, 500);

            // Stop after 15 seconds
            setTimeout(function() {{
                clearInterval(intervalId);
                if (foundCount === 0) {{
                    console.warn('Continue button never found for step: ' + stepName);
                }}
            }}, 15000);
        }})();
        </script>
        """,
        height=0,
    )


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


def check_pharmacy_copy_click():
    """Check if pharmacy receipt copy button was clicked and advance tour.

    Note: This function is deprecated as step 3 (first_document_loaded) has been removed.
    Kept for backwards compatibility but no longer active.
    """
    # Function no longer needed as we skip directly from upload_prompt to add_second_document
    return


def install_copy_button_detector():
    """Install JavaScript to detect clicks on pharmacy receipt copy button.

    Note: This function is deprecated as step 3 (first_document_loaded) has been removed.
    Kept for backwards compatibility but no longer active.
    """
    # Function no longer needed as we skip directly from upload_prompt to add_second_document
    return

    # Dead code below kept for reference
    if not st.session_state.get("tour_active", False):
        return

    current_step = st.session_state.get("tutorial_step", "welcome")

    # Only install during step where we're waiting for pharmacy receipt copy
    if current_step != "first_document_loaded":
        return

    components.html(
        """
        <script>
        (function() {
            let checkInterval;
            let clickDetected = false;

            function findAndMonitorPharmacyButton() {
                // Find all copy buttons in the document
                const iframes = window.parent.document.querySelectorAll('iframe');

                iframes.forEach(function(iframe) {
                    try {
                        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                        const buttons = iframeDoc.querySelectorAll('button[id^="copy_"]');

                        buttons.forEach(function(button) {
                            // Check if this is likely the pharmacy receipt button
                            // Look for nearby text containing "Pharmacy" or "💊"
                            let nearbyText = '';
                            let parent = button.parentElement;
                            for (let i = 0; i < 5 && parent; i++) {
                                nearbyText += parent.textContent || '';
                                parent = parent.parentElement;
                            }

                            if ((nearbyText.includes('Pharmacy') || nearbyText.includes('💊')) && !clickDetected) {
                                button.addEventListener('click', function() {
                                    if (!clickDetected) {
                                        clickDetected = true;
                                        // Store flag in localStorage to persist across rerun
                                        localStorage.setItem('pharmacy_copy_clicked', 'true');
                                        // Trigger page refresh after short delay
                                        setTimeout(function() {
                                            window.parent.location.reload();
                                        }, 200);
                                    }
                                });
                            }
                        });
                    } catch (e) {
                        // Cross-origin iframe, skip
                    }
                });
            }

            // Check periodically for the button
            checkInterval = setInterval(findAndMonitorPharmacyButton, 500);

            // Stop checking after 30 seconds
            setTimeout(function() {
                clearInterval(checkInterval);
            }, 30000);
        })();
        </script>
        """,
        height=0,
    )


def install_paste_detector():
    """Install JavaScript to detect paste events in text areas and trigger rerun."""
    if not st.session_state.get("tour_active", False):
        return

    current_step = st.session_state.get("tutorial_step", "welcome")

    # Only install during steps where we're waiting for paste
    if current_step not in ["paste_first_document", "add_second_document"]:
        return

    components.html(
        """
        <script>
        (function() {
            // Function to add paste listener to all text areas
            function addPasteListeners() {
                const textareas = window.parent.document.querySelectorAll('textarea');
                textareas.forEach(function(textarea) {
                    if (!textarea.hasAttribute('data-paste-listener')) {
                        textarea.setAttribute('data-paste-listener', 'true');
                        textarea.addEventListener('paste', function () {
                            setTimeout(function () {

                                // 🚫 Run only once
                                if (window.__tour_add_doc_highlighted) {
                                    return;
                                }

                                // ✅ Ensure this is the FIRST visible textarea (Document 1)
                                const visibleTextareas = Array.from(
                                    window.parent.document.querySelectorAll('textarea')
                                ).filter(t => t.offsetParent !== null);

                                if (!visibleTextareas.length || textarea !== visibleTextareas[0]) {
                                    return;
                                }

                                // Mark as handled
                                window.__tour_add_doc_highlighted = true;

                                // 1️⃣ Highlight the pasted textarea
                                if (window.parent.highlightElement) {
                                    window.parent.highlightElement(textarea);
                                }

                                // 2️⃣ Highlight ➕ Add another document button
                                function highlightAddAnotherDocumentButton() {
                                    const buttons = window.parent.document.querySelectorAll('button');

                                    for (let btn of buttons) {
                                        const text = (btn.innerText || '').toLowerCase();

                                        if (text.includes('add another document')) {
                                            if (window.parent.highlightElement) {
                                                window.parent.highlightElement(btn);
                                                console.log('✓ Highlighted Add another document button');
                                            }
                                            return true;
                                        }
                                    }
                                    return false;
                                }

                                // Try immediately + retry for Streamlit timing
                                highlightAddAnotherDocumentButton();
                                setTimeout(highlightAddAnotherDocumentButton, 300);
                                setTimeout(highlightAddAnotherDocumentButton, 600);
                                setTimeout(highlightAddAnotherDocumentButton, 1000);

                            }, 150);
                        });


                    }
                });
            }

            // Run immediately
            addPasteListeners();

            // Also watch for new textareas being added
            const observer = new MutationObserver(function(mutations) {
                addPasteListeners();
            });

            observer.observe(window.parent.document.body, {
                childList: true,
                subtree: true
            });
        })();
        </script>
        """,
        height=0,
    )


def install_tour_highlight_styles():
    """Install CSS styles and JavaScript function for tour element highlighting.

    Provides ADA-compliant drop shadows for both light and dark themes with
    proper contrast ratios. The highlight is temporary and auto-removes after 1.2s.
    """
    components.html(
        """
        <style>
        /* Tour highlight styles - ADA compliant for both light and dark themes */
        .demo-highlight {
            /* Light theme: dark shadow for contrast against light backgrounds */
            box-shadow: 0 0 0 3px rgba(255, 193, 7, 0.6),
                        0 0 20px 8px rgba(255, 193, 7, 0.4) !important;
            transition: box-shadow 0.3s ease-in-out !important;
            border-radius: 4px !important;
            position: relative !important;
            z-index: 1000 !important;
        }

        /* Dark theme: brighter shadow for contrast against dark backgrounds */
        @media (prefers-color-scheme: dark) {
            .demo-highlight {
                box-shadow: 0 0 0 3px rgba(255, 215, 64, 0.8),
                            0 0 25px 10px rgba(255, 215, 64, 0.5) !important;
            }
        }

        /* Streamlit dark theme detection (when user explicitly selects dark mode) */
        [data-theme="dark"] .demo-highlight {
            box-shadow: 0 0 0 3px rgba(255, 215, 64, 0.8),
                        0 0 25px 10px rgba(255, 215, 64, 0.5) !important;
        }
        </style>

        <script>
        // Install global highlight function for tour usage on parent window
        (function() {
            // CSS to inject into iframes
            const highlightCSS = `
                .demo-highlight {
                    box-shadow: 0 0 0 3px rgba(255, 193, 7, 0.6),
                                0 0 20px 8px rgba(255, 193, 7, 0.4) !important;
                    transition: box-shadow 0.3s ease-in-out !important;
                    border-radius: 4px !important;
                    position: relative !important;
                    z-index: 1000 !important;
                }
                @media (prefers-color-scheme: dark) {
                    .demo-highlight {
                        box-shadow: 0 0 0 3px rgba(255, 215, 64, 0.8),
                                    0 0 25px 10px rgba(255, 215, 64, 0.5) !important;
                    }
                }
                [data-theme="dark"] .demo-highlight {
                    box-shadow: 0 0 0 3px rgba(255, 215, 64, 0.8),
                                0 0 25px 10px rgba(255, 215, 64, 0.5) !important;
                }
            `;

            // Function to inject CSS into an iframe
            function injectCSSIntoIframe(iframeDoc) {
                if (iframeDoc.getElementById('tour-highlight-styles')) {
                    return; // Already injected
                }
                const style = iframeDoc.createElement('style');
                style.id = 'tour-highlight-styles';
                style.textContent = highlightCSS;
                (iframeDoc.head || iframeDoc.documentElement).appendChild(style);
            }

            // Main highlight function
            window.parent.highlightElement = function(el) {
                console.log('Highlighting element:', el);
                if (!el) {
                    console.warn('highlightElement called with null element');
                    return;
                }

                // Check if element is in an iframe
                const doc = el.ownerDocument;
                if (doc !== window.parent.document) {
                    // Element is in an iframe, inject CSS if needed
                    injectCSSIntoIframe(doc);
                }

                el.classList.add("demo-highlight");
                setTimeout(() => el.classList.remove("demo-highlight"), 6000);
            };

            console.log('Tour highlight function installed on window.parent');
        })();
        </script>
        """,
        height=0,
    )


def highlight_tour_elements():
    """Highlight interactive elements based on current tour step."""
    if not st.session_state.get("tour_active", False):
        return

    current_step = st.session_state.get("tutorial_step", "welcome")

    # Map steps to elements that should be highlighted
    highlight_script = ""

    # For all manual steps, highlight the Continue button
    if current_step in MANUAL_STEPS:
        # Highlight the Continue button in sidebar for manual steps
        highlight_script = f"""
        <script>
        (function() {{
            let checkCount = 0;
            
            function findAndHighlightContinue() {{
                checkCount++;
                const allButtons = window.parent.document.querySelectorAll('button');
                
                for (let btn of allButtons) {{
                    const btnText = btn.textContent || btn.innerText || '';
                    if (btnText.includes('Continue') && btnText.includes('▶')) {{
                        if (window.parent.highlightElement) {{
                            window.parent.highlightElement(btn);
                        }}
                        return true;
                    }}
                }}
                
                if (checkCount < 10) {{
                    setTimeout(findAndHighlightContinue, 500);
                }}
                return false;
            }}
            
            setTimeout(findAndHighlightContinue, 100);
            setTimeout(findAndHighlightContinue, 500);
            setTimeout(findAndHighlightContinue, 1000);
        }})();
        </script>
        """

    # Additional step-specific highlights
    if current_step == "copy_first_document":
        # Step 2: Highlight the first copy button (Hospital Bill - Colonoscopy)
        highlight_script += """
        <script>
        (function() {
            function highlightFirstCopyButton() {
                const iframes = window.parent.document.querySelectorAll('iframe');

                for (let iframe of iframes) {
                    try {
                        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                        const copyButtons = iframeDoc.querySelectorAll('button[id^="copy_"]');

                        if (copyButtons.length > 0 && window.parent.highlightElement) {
                            // Highlight the first copy button found
                            window.parent.highlightElement(copyButtons[0]);
                            return;
                        }
                    } catch (e) {
                        // Cross-origin iframe, skip
                    }
                }
            }

            // Try immediately and retry a few times in case content loads slowly
            highlightFirstCopyButton();
            setTimeout(highlightFirstCopyButton, 500);
            setTimeout(highlightFirstCopyButton, 1000);
        })();
        </script>
        """

    elif current_step == "paste_first_document":
        # Step 3: Highlight the first textarea (Document 1)
        highlight_script += """
        <script>
        (function() {
            function highlightFirstTextarea() {
                const textareas = window.parent.document.querySelectorAll('textarea');

                // Find the first visible textarea
                for (let textarea of textareas) {
                    if (textarea.offsetParent !== null) {
                        if (window.parent.highlightElement) {
                            window.parent.highlightElement(textarea);
                            console.log('Highlighted first textarea');
                        }
                        return;
                    }
                }
            }

            // Try immediately and retry in case content loads slowly
            highlightFirstTextarea();
            setTimeout(highlightFirstTextarea, 500);
            setTimeout(highlightFirstTextarea, 1000);
        })();
        </script>
        """

    elif current_step == "add_second_document":
        # Step 4: Highlight "Add Another Document" button
        highlight_script = """
        <script>
        (function() {
            function highlightAddDocButton() {
                const buttons = window.parent.document.querySelectorAll('button');

                for (let btn of buttons) {
                    const text = (btn.textContent || '').trim();

                    if (text.includes('Add Another Document')) {
                        btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        if (window.parent.highlightElement) {
                            window.parent.highlightElement(btn);
                            console.log('✓ Highlighted Add Another Document button');
                        }
                        return true;
                    }
                }
                return false;
            }

            // Try immediately + retry (Streamlit renders lazily)
            highlightAddDocButton();
            setTimeout(highlightAddDocButton, 300);
            setTimeout(highlightAddDocButton, 600);
            setTimeout(highlightAddDocButton, 1000);
            setTimeout(highlightAddDocButton, 1500);
        })();
        </script>
        """

    elif current_step == "profile_view":
        # Step 10: Highlight the profile button in sidebar
        highlight_script += """
        <script>
        (function() {
            function highlightProfileButton() {
                const buttons = window.parent.document.querySelectorAll('button');

                for (let btn of buttons) {
                    const text = (btn.textContent || '').trim().toLowerCase();

                    if (text.includes('profile') || text.includes('👤')) {
                        if (window.parent.highlightElement) {
                            window.parent.highlightElement(btn);
                            console.log('✓ Highlighted Profile button');
                        }
                        return true;
                    }
                }
                return false;
            }

            // Try immediately + retry (Streamlit renders lazily)
            highlightProfileButton();
            setTimeout(highlightProfileButton, 300);
            setTimeout(highlightProfileButton, 600);
            setTimeout(highlightProfileButton, 1000);
            setTimeout(highlightProfileButton, 1500);
        })();
        </script>
        """

    elif current_step == "import_view":
        # Step 11: Highlight the Import Data button
        highlight_script += """
        <script>
        (function() {
            let highlightAttempts = 0;
            const maxAttempts = 20;

            function highlightImportDataButton() {
                highlightAttempts++;

                // Search in main document
                const buttons = window.parent.document.querySelectorAll('button');

                for (let btn of buttons) {
                    const text = (btn.textContent || '').trim();

                    // Look for Import Data button (case insensitive)
                    if (text.toLowerCase().includes('import data')) {
                        // Scroll into view first
                        btn.scrollIntoView({ behavior: 'smooth', block: 'center' });

                        // Highlight after a brief delay to ensure scroll completes
                        setTimeout(() => {
                            if (window.parent.highlightElement) {
                                window.parent.highlightElement(btn);
                                console.log('✓ Highlighted Import Data button');
                            }
                        }, 200);
                        return true;
                    }
                }

                // If not found and haven't exceeded max attempts, try again
                if (highlightAttempts < maxAttempts) {
                    setTimeout(highlightImportDataButton, 500);
                } else {
                    console.warn('Import Data button not found after ' + maxAttempts + ' attempts');
                }
                return false;
            }
            // Start trying
            highlightImportDataButton();
        })();
        </script>
        """

    elif current_step == "import_now":
        # Step 12: Highlight Select Entity dropdown and Import Now button
        highlight_script += """
        <script>
        (function() {
            function highlightImportControls() {
                let foundCount = 0;

                // Find Select Entity dropdown
                const labels = window.parent.document.querySelectorAll('label, div');
                for (let label of labels) {
                    const text = (label.textContent || '').trim();
                    if (text.includes('Select Entity')) {
                        // Find the associated select/dropdown element
                        const selectBox = label.nextElementSibling || label.querySelector('select, div[data-baseweb="select"]');
                        if (selectBox) {
                            if (window.parent.highlightElement) {
                                window.parent.highlightElement(selectBox);
                                console.log('✓ Highlighted Select Entity dropdown');
                                foundCount++;
                            }
                        }
                        break;
                    }
                }

                // Find Import Now button
                const buttons = window.parent.document.querySelectorAll('button');
                for (let btn of buttons) {
                    const text = (btn.textContent || '').trim();
                    if (text.includes('Import Now')) {
                        if (window.parent.highlightElement) {
                            window.parent.highlightElement(btn);
                            console.log('✓ Highlighted Import Now button');
                            foundCount++;
                        }
                        break;
                    }
                }

                return foundCount > 0;
            }

            // Try immediately + retry (Streamlit renders lazily)
            highlightImportControls();
            setTimeout(highlightImportControls, 300);
            setTimeout(highlightImportControls, 600);
            setTimeout(highlightImportControls, 1000);
            setTimeout(highlightImportControls, 1500);
        })();
        </script>
        """

    # Inject the highlight script if we have one
    if highlight_script:
        components.html(highlight_script, height=0)


def open_sidebar_for_tour():
    """Open the sidebar automatically when tour is active."""
    if not st.session_state.get("tour_active", False):
        return

    if not st.session_state.get("tour_sidebar_opened", False):
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
