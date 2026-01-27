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
    """Launch tour if conditions are met (after splash and privacy)."""
    # Tour should start after:
    # 1. Splash screen dismissed
    # 2. Privacy policy accepted
    # 3. Tour not already completed
    # 4. Tour not already active
    if st.session_state.get('splash_dismissed', False) and \
       st.session_state.get('privacy_acknowledged', False) and \
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
                    width: 60px;
                    font-size: 12px;
                }
                
                .introjs-prevbutton {
                    background: #e0e0e0;
                    color: #333;
                }
                
                .introjs-helperLayer {
                    background-color: rgba(0, 0, 0, 0.7) !important;
                }
                [data-step="1"] {
                    background: white !important;
                    border-radius: 50px !important;
                    padding: 10px !important;
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
                
                /* Force step 3 tooltip to bottom */
                .introjs-tooltip[data-step="3"] {
                    position: absolute !important;
                }
                .introjs-bottom[data-step="3"] {
                    top: auto !important;
                    bottom: auto !important;
                }
                
                /* Override step counter to always show '8' as total */
                .introjs-helperNumberLayer {
                    font-size: 0;
                }
                .introjs-helperNumberLayer::before {
                    font-size: 14px;
                }
                .introjs-tooltip[data-step="1"] ~ .introjs-helperNumberLayer::before { content: '1 of 8'; }
                .introjs-tooltip[data-step="2"] ~ .introjs-helperNumberLayer::before { content: '2 of 8'; }
                .introjs-tooltip[data-step="3"] ~ .introjs-helperNumberLayer::before { content: '3 of 8'; }
                .introjs-tooltip[data-step="4"] ~ .introjs-helperNumberLayer::before { content: '4 of 8'; }
                .introjs-tooltip[data-step="5"] ~ .introjs-helperNumberLayer::before { content: '5 of 8'; }
                .introjs-tooltip[data-step="6"] ~ .introjs-helperNumberLayer::before { content: '6 of 8'; }
                .introjs-tooltip[data-step="7"] ~ .introjs-helperNumberLayer::before { content: '7 of 8'; }
                body:has([data-step="1"].introjs-showElement) .introjs-helperNumberLayer::before { content: '1 of 8' !important; }
                body:has([data-step="2"].introjs-showElement) .introjs-helperNumberLayer::before { content: '2 of 8' !important; }
                body:has([data-step="3"].introjs-showElement) .introjs-helperNumberLayer::before { content: '3 of 8' !important; }
                body:has([data-step="4"].introjs-showElement) .introjs-helperNumberLayer::before { content: '4 of 8' !important; }
                body:has([data-step="5"].introjs-showElement) .introjs-helperNumberLayer::before { content: '5 of 8' !important; }
                body:has([data-step="6"].introjs-showElement) .introjs-helperNumberLayer::before { content: '6 of 8' !important; }
                body:has([data-step="7"].introjs-showElement) .introjs-helperNumberLayer::before { content: '7 of 8' !important; }
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
            
            // Get all buttons once for steps 4 and 5
            const buttons = doc.querySelectorAll('button');
            
            // Step 2: Demo Documents section (heading)
            // Note: Copy buttons are inside iframes, so we target the section heading instead
            const demoHeadings = doc.querySelectorAll('h3');
            let demoSection = null;
            for (let heading of demoHeadings) {
                if (heading.textContent.includes('Demo Documents') && !heading.hasAttribute('data-intro')) {
                    demoSection = heading;
                    break;
                }
            }
            if (demoSection) {
                demoSection.setAttribute('data-intro', '📋 Here are sample medical bills you can try. Expand any document and click the Copy button to copy it to your clipboard, then paste it below for analysis.');
                demoSection.setAttribute('data-step', '2');
                demoSection.setAttribute('data-position', 'bottom');
            }
            
            // Step 3: Document input area
            const textAreas = doc.querySelectorAll('textarea');
            if (textAreas.length > 0 && !textAreas[0].hasAttribute('data-intro')) {
                textAreas[0].parentElement.setAttribute('data-intro', '✍️ Paste your medical bill, pharmacy receipt, or insurance statement here. You can add multiple documents to compare.');
                textAreas[0].parentElement.setAttribute('data-step', '3');
                textAreas[0].parentElement.setAttribute('data-position', 'bottom');
            }
            
            // Step 4: Add document button
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
            console.log("sidebar", sidebar);
            if (sidebar && !sidebar.hasAttribute('data-intro')) {
                sidebar.setAttribute('data-intro', '💬 Use the sidebar to ask Billy or Billie questions about your bills, view your health profile, or import data from providers.');
                sidebar.setAttribute('data-step', '6');
                sidebar.setAttribute('data-position', 'right');
            }
            
            // Step 7: Profile section (in sidebar)
            const profileBtn = doc.querySelector('button[kind="secondary"]');
            console.log("profileBtn", profileBtn);
            if (profileBtn && profileBtn.textContent.includes('Profile') && !profileBtn.hasAttribute('data-intro')) {
                profileBtn.setAttribute('data-intro', '👤 View and manage your health profile, including insurance coverage and provider information.');
                profileBtn.setAttribute('data-step', '7');
                profileBtn.setAttribute('data-position', 'right');
            }
            
            // Step 8: Final step - create hidden marker element
            // Check if step 8 marker already exists
            let finalDiv = doc.getElementById('tour-step-8-marker');
            if (!finalDiv) {
                console.log("Creating step 8 marker div...");
                
                // Try to find a good container (fallback to body if needed)
                let container = doc.querySelector('.main') || 
                               doc.querySelector('[data-testid="stAppViewContainer"]') || 
                               doc.querySelector('.stApp') ||
                               doc.body;
                
                console.log("Step 8 container:", container?.tagName, container?.className);
                
                // Create the marker div
                finalDiv = doc.createElement('div');
                finalDiv.id = 'tour-step-8-marker';
                finalDiv.setAttribute('data-intro', '👤 In the Profile view, you can manage your health insurance details, track provider information, and save your medical history for faster analysis. This helps us give you more accurate insights!');
                finalDiv.setAttribute('data-step', '8');
                
                // Make it invisible but still counted by Intro.js
                finalDiv.style.position = 'absolute';
                finalDiv.style.visibility = 'hidden';
                finalDiv.style.width = '1px';
                finalDiv.style.height = '1px';
                finalDiv.style.top = '0';
                finalDiv.style.left = '0';
                
                container.appendChild(finalDiv);
                console.log("✓ Created step 8 marker div, appended to:", container.tagName);
            } else {
                console.log("Step 8 marker already exists");
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
            
            // Wait for UI elements to be rendered
            function waitForUIElements(callback, maxAttempts = 50) {
                let attempts = 0;
                const checkInterval = setInterval(() => {
                    attempts++;
                    const doc = window.parent.document;
                    const textAreas = doc.querySelectorAll('textarea');
                    const buttons = doc.querySelectorAll('button');
                    const analyzeBtn = Array.from(buttons).some(btn => btn.textContent.includes('Analyze'));
                    
                    console.log('[Intro.js] Check', attempts, '- TextAreas:', textAreas.length, 'Buttons:', buttons.length, 'Analyze:', analyzeBtn);
                    
                    if (textAreas.length > 0 && buttons.length > 5 && analyzeBtn) {
                        console.log('[Intro.js] UI elements ready after', attempts, 'attempts');
                        clearInterval(checkInterval);
                        callback();
                    } else if (attempts >= maxAttempts) {
                        console.warn('[Intro.js] UI elements not all found after', attempts, 'attempts, starting tour anyway');
                        console.log('[Intro.js] Final state - TextAreas:', textAreas.length, 'Buttons:', buttons.length);
                        clearInterval(checkInterval);
                        callback();
                    }
                }, 400);
            }
            
            waitForUIElements(() => {
                // Ensure steps are set up
                if (window.parent.setupTourSteps) {
                    console.log('[Intro.js] Setting up tour steps...');
                    window.parent.setupTourSteps();
                }
                
                // Wait a moment for attributes to be applied, then verify step count
                setTimeout(() => {
                    const doc = window.parent.document;
                    
                    // CRITICAL: Ensure sidebar is expanded so steps 6-8 can be counted
                    const sidebar = doc.querySelector('[data-testid="stSidebar"]');
                    const sidebarCollapse = doc.querySelector('[data-testid="collapsedControl"]');
                    if (sidebar && sidebarCollapse) {
                        const sidebarRect = sidebar.getBoundingClientRect();
                        // If sidebar is collapsed (very narrow), expand it
                        if (sidebarRect.width < 100) {
                            console.log('[Intro.js] Expanding sidebar before tour...');
                            sidebarCollapse.click();
                            // Wait for sidebar to expand
                            setTimeout(() => continueInit(), 500);
                            return;
                        }
                    }
                    
                    continueInit();
                    
                    function continueInit() {
                        console.log('[Intro.js] Verifying tour steps...');
                        // Re-run setup to catch any new elements (especially in sidebar)
                        if (window.parent.setupTourSteps) {
                            window.parent.setupTourSteps();
                        }
                        
                        const stepsFound = doc.querySelectorAll('[data-step]');
                        console.log('[Intro.js] Steps found before init:', stepsFound.length);
                        stepsFound.forEach((el, i) => {
                            console.log(`  Step ${el.getAttribute('data-step')}: ${el.tagName} - ${el.getAttribute('data-intro')?.substring(0, 50)}...`);
                        });
                        
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
                            tooltipPosition: 'auto',
                            positionPrecedence: ['bottom', 'right', 'top', 'left'],
                        });
                        
                        // Handle step changes
                        intro.onbeforechange(function(targetElement) {
                            const doc = window.parent.document;
                            const currentStep = this._currentStep;
                            const totalSteps = this._introItems.length;
                            
                            // Step 6: Open sidebar automatically
                            if (currentStep === 5) { // Step 6 is index 5 (0-based)
                                const sidebarCollapse = doc.querySelector('[data-testid="collapsedControl"]');
                                if (sidebarCollapse) {
                                    console.log('[Intro.js] Opening sidebar for step 6');
                                    sidebarCollapse.click();
                                }
                            }
                            
                            // Step 7: Click Profile button automatically
                            if (currentStep === 6) { // Step 7 is index 6 (0-based)
                                const buttons = doc.querySelectorAll('button[kind="secondary"]');
                                for (let btn of buttons) {
                                    if (btn.textContent.includes('Profile')) {
                                        console.log('[Intro.js] Clicking Profile button for step 7');
                                        setTimeout(() => btn.click(), 300);
                                        break;
                                    }
                                }
                            }
                            
                            // If we just moved to the last step (step 8), auto-complete after showing it
                            if (currentStep === 7) { // Step 8 is index 7 (0-based)
                                setTimeout(() => {
                                    intro.exit(true);
                                }, 5000); // Show last step for 5 seconds then close
                            }
                        });
                        
                        intro.oncomplete(() => {
                            console.log('[Intro.js] Tour completed!');
                        });
                        
                        intro.onexit(() => {
                            console.log('[Intro.js] Tour exited');
                        });
                        
                        console.log('[Intro.js] Starting tour now...');
                        intro.start();
                    } // End continueInit()
                }, 500);
            });
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
