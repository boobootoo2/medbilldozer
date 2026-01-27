"""Guided Tour - Interactive tutorial using Intro.js.

Provides step-by-step guidance for first-time users through the app's
main features using the Intro.js library.
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, List, Optional


def initialize_tour_state():
    """Initialize tour-related session state variables."""
    if 'tour_active' not in st.session_state:
        st.session_state.tour_active = False
    if 'tour_completed' not in st.session_state:
        st.session_state.tour_completed = False


def maybe_launch_tour():
    """Launch tour if conditions are met (called after splash screen)."""
    # If splash was just dismissed and tour hasn't been completed, activate it
    if st.session_state.get('splash_dismissed', False) and \
       not st.session_state.get('tour_completed', False) and \
       not st.session_state.get('tour_active', False):
        activate_tour()


def install_introjs_library():
    """Install Intro.js CSS and JS files into parent document."""
    components.html("""
    <script>
    (function() {
        if (!window.parent || !window.parent.document) {
            console.error('[Intro.js] No parent document access');
            return;
        }
        
        const doc = window.parent.document;
        const head = doc.head;
        
        // Check if already loaded
        if (window.parent.introJs) {
            console.log('[Intro.js] Library already loaded');
            return;
        }
        
        console.log('[Intro.js] Loading library...');
        
        // Add CSS
        if (!doc.getElementById('introjs-css')) {
            const css = doc.createElement('link');
            css.id = 'introjs-css';
            css.rel = 'stylesheet';
            css.href = 'https://cdnjs.cloudflare.com/ajax/libs/intro.js/7.2.0/introjs.min.css';
            head.appendChild(css);
        }
        
        // Add custom styles
        if (!doc.getElementById('introjs-custom-css')) {
            const style = doc.createElement('style');
            style.id = 'introjs-custom-css';
            style.textContent = `
                /* Custom Intro.js styling to match MedBillDozer theme */
                .introjs-tooltip {
                    background-color: white;
                    border-radius: 12px;
                    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                    padding: 20px;
                    max-width: 400px;
                }
                
                .introjs-tooltiptext {
                    font-size: 16px;
                    line-height: 1.6;
                    color: #333;
                }
                
                .introjs-button {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                
                .introjs-button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
                }
                
                .introjs-skipbutton {
                    color: #667eea;
                    font-weight: 600;
                }
                
                .introjs-prevbutton {
                    background: #e0e0e0;
                    color: #333;
                }
                
                .introjs-helperLayer {
                    background-color: rgba(0, 0, 0, 0.7);
                }
                
                .introjs-tooltipReferenceLayer {
                    background-color: transparent;
                    border: 3px solid #667eea;
                    border-radius: 8px;
                    box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
                }
                
                /* Avatar in tooltip */
                .intro-avatar {
                    width: 60px;
                    height: 60px;
                    margin-bottom: 10px;
                    display: block;
                }
                
                .intro-character-name {
                    font-weight: 700;
                    color: #667eea;
                    margin-bottom: 8px;
                }
            `;
            head.appendChild(style);
        }
        
        // Add JS
        if (!doc.getElementById('introjs-js')) {
            const script = doc.createElement('script');
            script.id = 'introjs-js';
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/intro.js/7.2.0/intro.min.js';
            script.onload = function() {
                console.log('[Intro.js] Library loaded successfully');
            };
            script.onerror = function() {
                console.error('[Intro.js] Failed to load library');
            };
            head.appendChild(script);
        }
    })();
    </script>
    """, height=0)


def render_tour_steps():
    """Add data-intro attributes to elements for the guided tour."""
    components.html("""
    <script>
    (function() {
        if (!window.parent || !window.parent.document) return;
        
        const doc = window.parent.document;
        
        // Wait for elements to be ready
        function setupTourSteps() {
            // Step 1: Welcome - Title/Logo area
            const logo = doc.querySelector('img[alt*="Billy"]');
            if (logo && !logo.hasAttribute('data-intro')) {
                logo.setAttribute('data-intro', '👋 Hi! I\\'m Billy, and with my partner Billie, we\\'ll help you find hidden errors in medical bills. Let\\'s get started!');
                logo.setAttribute('data-step', '1');
                logo.setAttribute('data-position', 'bottom');
            }
            
            // Step 2: Sample documents section
            const sampleDocs = doc.querySelector('[data-testid="stExpander"]');
            if (sampleDocs && !sampleDocs.hasAttribute('data-intro')) {
                sampleDocs.setAttribute('data-intro', '📋 First, let\\'s try analyzing a sample document. Click here to see example bills you can copy and paste.');
                sampleDocs.setAttribute('data-step', '2');
                sampleDocs.setAttribute('data-position', 'bottom');
            }
            
            // Step 3: Document input area
            const textAreas = doc.querySelectorAll('textarea');
            if (textAreas.length > 0 && !textAreas[0].hasAttribute('data-intro')) {
                textAreas[0].parentElement.setAttribute('data-intro', '✍️ Paste your medical bill, pharmacy receipt, or insurance statement here. You can add multiple documents to compare.');
                textAreas[0].parentElement.setAttribute('data-step', '3');
                textAreas[0].parentElement.setAttribute('data-position', 'top');
            }
            
            // Step 4: Add document button
            const buttons = doc.querySelectorAll('button');
            buttons.forEach(btn => {
                if (btn.textContent.includes('Add Another Document') && !btn.hasAttribute('data-intro')) {
                    btn.setAttribute('data-intro', '➕ Click here to add multiple documents for comparison analysis.');
                    btn.setAttribute('data-step', '4');
                    btn.setAttribute('data-position', 'top');
                }
            });
            
            // Step 5: Analyze button
            buttons.forEach(btn => {
                if (btn.textContent.includes('Analyze') && !btn.hasAttribute('data-intro')) {
                    btn.setAttribute('data-intro', '🔍 Once you\\'ve pasted your document, click here to start the analysis. I\\'ll check for billing errors, overcharges, and coding mistakes.');
                    btn.setAttribute('data-step', '5');
                    btn.setAttribute('data-position', 'top');
                }
            });
            
            // Step 6: Sidebar
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (sidebar && !sidebar.hasAttribute('data-intro')) {
                sidebar.setAttribute('data-intro', '💬 Use the sidebar to ask Billy or Billie questions about your bills, view your health profile, or import data from providers.');
                sidebar.setAttribute('data-step', '6');
                sidebar.setAttribute('data-position', 'right');
            }
            
            // Step 7: Profile section (in sidebar)
            const profileBtn = doc.querySelector('button[kind="secondary"]');
            if (profileBtn && profileBtn.textContent.includes('Profile') && !profileBtn.hasAttribute('data-intro')) {
                profileBtn.setAttribute('data-intro', '👤 View and manage your health profile, including insurance coverage and provider information.');
                profileBtn.setAttribute('data-step', '7');
                profileBtn.setAttribute('data-position', 'right');
            }
            
            // Step 8: Final step
            const mainContent = doc.querySelector('.main');
            if (mainContent && !mainContent.hasAttribute('data-intro-final')) {
                mainContent.setAttribute('data-intro-final', 'true');
                const finalDiv = doc.createElement('div');
                finalDiv.setAttribute('data-intro', '✅ That\\'s it! You\\'re ready to start finding billing errors. If you need help, just ask using the assistant in the sidebar. Good luck!');
                finalDiv.setAttribute('data-step', '8');
                finalDiv.style.display = 'none';
                mainContent.appendChild(finalDiv);
            }
        }
        
        // Initial setup
        setupTourSteps();
        
        // Re-setup when DOM changes
        const observer = new MutationObserver(setupTourSteps);
        observer.observe(doc.body, { childList: true, subtree: true });
        
        // Store setup function globally
        window.parent.setupTourSteps = setupTourSteps;
    })();
    </script>
    """, height=0)


def start_introjs_tour():
    """Start the Intro.js tour."""
    components.html("""
    <script>
    (function() {
        console.log('[Intro.js] Starting tour initialization...');
        
        if (!window.parent || !window.parent.document) {
            console.error('[Intro.js] No parent window access');
            return;
        }
        
        // Wait for Intro.js library to load
        function waitForIntroJs(callback, maxAttempts = 20) {
            let attempts = 0;
            const checkInterval = setInterval(() => {
                attempts++;
                if (window.parent.introJs) {
                    console.log('[Intro.js] Library found after', attempts, 'attempts');
                    clearInterval(checkInterval);
                    callback();
                } else if (attempts >= maxAttempts) {
                    console.error('[Intro.js] Library failed to load after', attempts, 'attempts');
                    clearInterval(checkInterval);
                }
            }, 200);
        }
        
        waitForIntroJs(() => {
            console.log('[Intro.js] Intro.js library ready');
            
            // Ensure steps are set up
            if (window.parent.setupTourSteps) {
                console.log('[Intro.js] Setting up tour steps...');
                window.parent.setupTourSteps();
            }
            
            // Wait a moment for attributes to be applied
            setTimeout(() => {
                console.log('[Intro.js] Initializing tour...');
                const intro = window.parent.introJs();
                
                intro.setOptions({
                    showProgress: true,
                    showBullets: true,
                    exitOnOverlayClick: false,
                    exitOnEsc: true,
                    nextLabel: 'Next →',
                    prevLabel: '← Back',
                    doneLabel: 'Done! 🎉',
                    skipLabel: 'Skip Tour',
                    scrollToElement: true,
                    scrollPadding: 30,
                    overlayOpacity: 0.7,
                    showStepNumbers: true,
                });
                
                intro.oncomplete(() => {
                    console.log('[Intro.js] Tour completed!');
                });
                
                intro.onexit(() => {
                    console.log('[Intro.js] Tour exited');
                });
                
                console.log('[Intro.js] Starting tour now...');
                intro.start();
            }, 500);
        });
    })();
    </script>
    """, height=0)


def run_guided_tour_runtime():
    """
    Runs guided tour using Intro.js.
    Call ONCE per rerun, AFTER main UI render.
    """
    # Debug info (remove in production)
    tour_active = st.session_state.get("tour_active", False)
    start_now = st.session_state.get("start_tour_now", False)
    
    if not tour_active:
        # Show debug button to manually start tour
        if st.sidebar.button("🚀 Start Guided Tour", key="manual_tour_start"):
            activate_tour()
            st.rerun()
        return
    
    # Install Intro.js library
    install_introjs_library()
    
    # Set up tour step attributes
    render_tour_steps()
    
    # Start the tour if just activated
    if start_now:
        start_introjs_tour()
        st.session_state.start_tour_now = False


def activate_tour():
    """Activate the guided tour (called after splash screen dismissal)."""
    st.session_state.tour_active = True
    st.session_state.start_tour_now = True


# Compatibility functions for existing code
def check_tour_progression():
    """Compatibility - no longer needed with Intro.js."""
    pass


def render_tour_widget():
    """Compatibility - Intro.js handles tour UI."""
    pass


def render_tour_controls():
    """Compatibility - Intro.js handles controls."""
    pass


def advance_tour_step():
    """Compatibility - Intro.js handles step advancement."""
    pass


def open_sidebar_for_tour():
    """Compatibility - manual sidebar control if needed."""
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
    """Compatibility - Intro.js handles highlighting."""
    pass


def highlight_tour_elements():
    """Compatibility - Intro.js handles highlighting."""
    pass


def open_and_scroll_pipeline_workflow_step6():
    """Compatibility - Intro.js handles scrolling."""
    pass
