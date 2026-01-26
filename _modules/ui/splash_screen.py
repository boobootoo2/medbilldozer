"""Splash Screen - Welcome screen with Billdozer introduction.

Shows a fullscreen welcome screen with Billy and Billie explaining the app
when GUIDED_TOUR=TRUE. Animation runs once and user can dismiss to proceed.
"""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from _modules.ui.billdozer_widget import (
    get_billdozer_widget_html,
    install_billdozer_bridge,
    dispatch_widget_message,
)


def should_show_splash_screen() -> bool:
    """Check if splash screen should be shown.
    
    Returns:
        bool: True if splash screen has not been dismissed yet
    """
    if 'splash_dismissed' not in st.session_state:
        st.session_state.splash_dismissed = False
    
    return not st.session_state.splash_dismissed


def dismiss_splash_screen():
    """Mark splash screen as dismissed."""
    st.session_state.splash_dismissed = True


def render_splash_screen():
    """Render fullscreen splash screen with Billdozer widget.
    
    Shows Billy and Billie introducing the app with animation.
    User can click dismiss button to proceed to main app.
    """
    # Fullscreen container
    st.html("""
    <style>
    /* Hide Streamlit default elements for splash screen */
    .splash-active header[data-testid="stHeader"] {
        display: none !important;
    }
    .splash-active [data-testid="stSidebar"] {
        display: none !important;
    }
    .splash-active .main .block-container {
        padding-top: 0 !important;
        max-width: 100% !important;
    }
    
    /* Remove padding and max-width from parent containers */
    .splash-enabled section > div {
        padding: 0;
        max-width: none;
    }
    
    /* Splash screen styles */
    .splash-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        color: white;
        text-align: center;
        padding: 0 20px;
        overflow: hidden;
    }
    
    .splash-content {
        max-width: 800px;
        width: 100%;
        animation: fadeInUp 0.8s ease-out;
    }
    
    .splash-title {
        font-size: 3.5em;
        font-weight: 800;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .splash-subtitle {
        font-size: 1.5em;
        margin-bottom: 40px;
        opacity: 0.95;
        font-weight: 400;
    }
    
    .splash-widget-container {
        margin: 40px auto;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    .splash-description {
        font-size: 1.2em;
        line-height: 1.8;
        margin: 30px auto;
        max-width: 700px;
        opacity: 0.9;
    }
    
    .splash-dismiss-btn {
        margin-top: 40px;
        padding: 15px 50px;
        font-size: 1.2em;
        background: white;
        color: #667eea;
        border: none;
        border-radius: 50px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .splash-dismiss-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        background: #f8f9fa;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
    """)
    
    
    # Add splash-enabled class to body
    components.html("""
    <script>
    (function() {
        // Add class to parent document body
        if (window.parent && window.parent.document && window.parent.document.body) {
            window.parent.document.body.classList.add('splash-enabled');
            console.log('[Splash] Added splash-enabled class to parent body');
        }
    })();
    </script>
    """, height=0)
    
    # Render splash screen content with embedded widget
    components.html("""
    <style>
    body {
        margin: 0;
        padding: 0;
        overflow: hidden;
    }
    .splash-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        color: white;
        text-align: center;
        padding: 0 20px;
        overflow: hidden;
    }
    
    .splash-content {
        max-width: 800px;
        width: 100%;
        animation: fadeInUp 0.8s ease-out;
    }
    
    .splash-title {
        font-size: 3.5em;
        font-weight: 800;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .splash-subtitle {
        font-size: 1.5em;
        margin-bottom: 40px;
        opacity: 0.95;
        font-weight: 400;
    }
    
    .splash-widget-container {
        margin: 40px auto;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    .splash-description {
        font-size: 1.2em;
        line-height: 1.8;
        margin: 30px auto;
        max-width: 700px;
        opacity: 0.9;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
    <div class="splash-container">
    <div class="splash-content">
        <div class="splash-title"><img src="https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static/images/avatars/transparent/billy__eyes_open__billdozer_up.png" alt="Billy character with eyes open looking up" style="
    height: 87px;
    width: auto;
"> medBillDozer</div>

        <div class="splash-subtitle">
        Find Hidden Errors in Medical Bills
        </div>

        <div class="splash-widget-container" id="splash-widget-container">
            <style>
                .splash-widget-container .inner-container {
                    width: 320px;
                    height: 120px;
                    display: flex;
                    align-items: flex-end;
                    background-color: transparent;
                    position: relative;
                    margin: 0 auto;
                }
                
                .splash-widget-container .billdozer_animation {
                    position: relative;
                    width: 33.3333%;
                    height: 140px;
                }
                
                .splash-widget-container .billdozer_animation img {
                    position: absolute;
                    bottom: 0;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 90%;
                    opacity: 0;
                    animation: frameCycle 3s steps(1, end) 2;
                    animation-fill-mode: forwards;
                }
                
                /* First child starts visible and ends visible */
                .splash-widget-container .billdozer_animation img:nth-child(1) {
                    opacity: 1;
                    animation: frame1Cycle 6s steps(1) 1;
                    animation-fill-mode: forwards;
                }
                
                .splash-widget-container .billdozer_animation img:nth-child(2) {
                    animation: frame2Cycle 6s steps(1) 1;
                    animation-fill-mode: forwards;
                }
                
                .splash-widget-container .billdozer_animation img:nth-child(3) {
                    animation: frame3Cycle 6s steps(1) 1;
                    animation-fill-mode: forwards;
                }
                
                @keyframes frame1Cycle {
                    0%, 16.66% { opacity: 1; }
                    16.67%, 49.99% { opacity: 0; }
                    50%, 66.66% { opacity: 1; }
                    66.67%, 100% { opacity: 1; }
                }
                
                @keyframes frame2Cycle {
                    0%, 16.66% { opacity: 0; }
                    16.67%, 33.33% { opacity: 1; }
                    33.34%, 66.66% { opacity: 0; }
                    66.67%, 83.33% { opacity: 1; }
                    83.34%, 100% { opacity: 0; }
                }
                
                @keyframes frame3Cycle {
                    0%, 33.33% { opacity: 0; }
                    33.34%, 49.99% { opacity: 1; }
                    50%, 83.33% { opacity: 0; }
                    83.34%, 99.99% { opacity: 1; }
                    100% { opacity: 0; }
                }
                
                .splash-widget-container .speech-layer {
                    position: absolute;
                    top: -10px;
                    left: 50%;
                    transform: translateX(-50%);
                    display: none;
                    pointer-events: none;
                }
                
                .splash-widget-container .speech-bubble {
                    background: white;
                    border-radius: 10px;
                    padding: 8px 12px;
                    font-size: 12px;
                    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
                    margin-bottom: 60px;
                    position: relative;
                }
                .splash-widget-container .speech-bubble .speech-text {
                    color: #333;
                }
                .splash-widget-container .speech-pointer {
                    
                    position: absolute;
                    bottom: -10px;
                    width: 0;
                    height: 0;
                }
                
                .splash-widget-container .talking-left .speech-pointer {
                    left: -12px;
                    border-top: 10px solid transparent;
                    border-bottom: 12px solid transparent;
                    border-right: 22px solid white;
                    transform: rotate(-45deg);
                }
                
                .splash-widget-container .talking-right .speech-pointer {
                    right: -12px;
                    border-top: 12px solid transparent;
                    border-bottom: 10px solid transparent;
                    border-left: 22px solid white;
                    transform: rotate(45deg);
                }
            </style>
            
            <div class="inner-container" role="region" aria-label="Billdozer animation widget">
                <!-- Left (Billie) -->
                <div class="billdozer_animation">
                    <img src="https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static/images/avatars/transparent/billie__eyes_closed__billdozer_down.png" alt="Billie character with eyes closed">
                    <img src="https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static/images/avatars/transparent/billie__eyes_open__billdozer_up.png" alt="Billie character with eyes open looking up">
                    <img src="https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static/images/avatars/transparent/billie__eyes_open__billdozer_down.png" alt="Billie character with eyes open looking down">
                </div>

                <!-- Middle -->
                <div class="billdozer_animation">
                    <img src="https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static/images/avatars/transparent/envelop_rest.png" alt="Envelope at rest">
                    <img src="https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static/images/avatars/transparent/envelop_falling_1.png" alt="Envelope falling animation frame 1">
                    <img src="https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static/images/avatars/transparent/envelop_falling_2.png" alt="Envelope falling animation frame 2">
                </div>

                <!-- Right (Billy) -->
                <div class="billdozer_animation">
                    <img src="https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static/images/avatars/transparent/billy__eyes_closed__billdozer_down.png" alt="Billy character with eyes closed">
                    <img src="https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static/images/avatars/transparent/billy__eyes_open__billdozer_down.png" alt="Billy character with eyes open looking down">
                    <img src="https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static/images/avatars/transparent/billy__eyes_open__billdozer_up.png" alt="Billy character with eyes open looking up">
                </div>

                <div class="speech-layer">
                    <div class="speech-bubble">
                        <div class="speech-text"></div>
                        <div class="speech-pointer"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="splash-description">
        <p><strong>Hi! We're Billy and Billie,</strong> your guides to uncovering billing errors.</p>
        <p>
            We analyze medical bills, pharmacy receipts, dental claims,
            and insurance statements to find overcharges, duplicate charges,
            and coding errors that could save you money.
        </p>
        <p>
            Let us show you how easy it is to check your bills for accuracy!
        </p>
        </div>
    </div>
    </div>
    
    <script>
    (function() {
        console.log("[Splash Widget] Script starting...");
        
        const container = document.querySelector(".splash-widget-container .inner-container");
        const speechLayer = document.querySelector(".splash-widget-container .speech-layer");
        const speechText = document.querySelector(".splash-widget-container .speech-text");
        
        console.log("[Splash Widget] Elements found:", {
            container: !!container,
            speechLayer: !!speechLayer,
            speechText: !!speechText
        });
        
        if (!container || !speechLayer || !speechText) {
            console.error("[Splash Widget] Required elements not found!");
            return;
        }
        
        // Pre-populate queue with welcome messages - split long messages into chunks
        const rawMessages = [
            { character: "billie", message: "Hi! We're Billy and Billie, your guides to uncovering billing errors." },
            { character: "billy", message: "We analyze medical bills, pharmacy receipts, dental claims, and insurance statements to find overcharges, duplicate charges, and coding errors that could save you money." },
            { character: "billie", message: "Let us show you how easy it is to check your bills for accuracy!" }
        ];
        
        const queue = [];
        const maxChars = 40;
        
        rawMessages.forEach(({ character, message }) => {
            // Split message into words
            const words = message.split(' ');
            let chunk = '';
            
            words.forEach((word, index) => {
                const testChunk = chunk ? chunk + ' ' + word : word;
                
                if (testChunk.length > maxChars && chunk) {
                    // Push current chunk and start new one
                    queue.push({ character, message: chunk });
                    chunk = word;
                } else {
                    chunk = testChunk;
                }
                
                // Push final chunk
                if (index === words.length - 1 && chunk) {
                    queue.push({ character, message: chunk });
                }
            });
        });
        
        let active = false;
        
        function playNext() {
            console.log("[Splash Widget] Playing next message, queue length:", queue.length);
            if (!queue.length) {
                active = false;
                speechLayer.style.display = "none";
                container.classList.remove("talking-left", "talking-right");
                console.log("[Splash Widget] Queue empty, finished");
                return;
            }
            
            active = true;
            const { character, message } = queue.shift();
            console.log("[Splash Widget] Showing message from", character, ":", message);
            
            container.classList.remove("talking-left", "talking-right");
            container.classList.add(character === "billie" ? "talking-left" : "talking-right");
            
            speechText.textContent = message;
            speechLayer.style.display = "block";
            
            setTimeout(() => {
                speechLayer.style.display = "none";
                container.classList.remove("talking-left", "talking-right");
                console.log("[Splash Widget] Message complete, waiting before next");
                setTimeout(playNext, 300);
            }, 3000);
        }
        
        // Start showing messages after a brief delay
        setTimeout(() => {
            console.log("[Splash Widget] Starting welcome message sequence");
            playNext();
        }, 1500);
        
        console.log("[Splash Widget] Initialized with", queue.length, "messages");
    })();
    </script>
    """, height=1000, scrolling=False)

    # Style and render dismiss button positioned over splash screen
    st.markdown("""
        <style>
        div[data-testid="stButton"] > button[kind="primary"] {
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10000;
            background: white !important;
            color: #667eea !important;
            font-size: 18px;
            font-weight: 700;
            padding: 16px 48px;
            border-radius: 50px;
            border: 3px solid white !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover {
            transform: translateX(-50%) translateY(-2px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
            background: #f0f0f0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if st.button("Get Started 🚀", key="dismiss_splash_btn", type="primary"):
        dismiss_splash_screen()
