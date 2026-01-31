"""Splash Screen - Welcome screen with Billdozer introduction.

Shows a fullscreen welcome screen with Billy and Billie explaining the app
when GUIDED_TOUR=TRUE. Animation runs once and user can dismiss to proceed.
"""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import logging
import base64
from _modules.ui.billdozer_widget import (
    get_billdozer_widget_html,
    install_billdozer_bridge,
    dispatch_widget_message,
)
from _modules.ui.audio_controls import is_audio_muted

logger = logging.getLogger(__name__)


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


def generate_splash_audio(character: str, text: str, index: int):
    """Generate audio narration for splash screen using OpenAI TTS.
    
    Args:
        character: Either 'billy' (male voice) or 'billie' (female voice)
        text: Text to synthesize
        index: Message index for file naming
        
    Returns:
        Path to audio file, or None if generation fails
    """
    audio_dir = Path("audio")
    audio_dir.mkdir(exist_ok=True)
    
    audio_file = audio_dir / f"splash_{character}_{index}.mp3"
    
    # Return cached file if exists
    if audio_file.exists():
        return audio_file
    
    # Try to generate using OpenAI TTS
    try:
        from openai import OpenAI
        
        # Initialize client (uses OPENAI_API_KEY from environment)
        client = OpenAI()
        
        # Choose voice based on character
        # Billy (male): echo (authoritative, clear)
        # Billie (female): nova (warm, friendly)
        voice = "echo" if character == "billy" else "nova"
        
        logger.info(f"Generating splash audio for {character} (voice: {voice})...")
        
        # Generate speech
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            speed=1.0
        )
        
        # Save to file
        audio_file.write_bytes(response.read())
        logger.info(f"✅ Generated splash audio: {audio_file}")
        
        return audio_file
        
    except ImportError:
        logger.debug("OpenAI library not available for audio generation")
        return None
    except Exception as e:
        logger.warning(f"Failed to generate splash audio for {character}_{index}: {e}")
        return None


def prepare_splash_audio():
    """Pre-generate all splash screen audio files."""
    messages = [
        ("billie", "Hi! We're Billy and Billie—your guides to finding billing mistakes."),
        ("billy", "We scan medical bills, pharmacy receipts, dental claims, and insurance statements to uncover overcharges, duplicates, and missed reimbursements."),
        ("billie", "Ready to see how easy it is to double-check your bills?")
    ]
    
    for index, (character, text) in enumerate(messages):
        generate_splash_audio(character, text, index)


def render_splash_screen():
    """Render fullscreen splash screen with Billdozer widget.
    
    Shows Billy and Billie introducing the app with animation and audio narration.
    User can click dismiss button to proceed to main app.
    """
    # Pre-generate audio files (will use cache if already exist)
    prepare_splash_audio()
    
    # Check if audio is muted
    audio_muted = is_audio_muted()
    
    # Check which audio files are available and convert to base64 data URIs
    import json
    audio_dir = Path("audio")
    audio_files = []
    for i in range(3):
        character = ["billie", "billy", "billie"][i]
        audio_file = audio_dir / f"splash_{character}_{i}.mp3"
        if audio_file.exists():
            # Read audio file and convert to base64 data URI
            # This bypasses Streamlit's file serving issues
            try:
                with open(audio_file, "rb") as f:
                    audio_data = f.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    data_uri = f"data:audio/mpeg;base64,{audio_base64}"
                    audio_files.append(data_uri)
                    logger.info(f"✅ Converted {audio_file.name} to base64 ({len(audio_base64)} chars)")
            except Exception as e:
                logger.error(f"❌ Failed to read {audio_file}: {e}")
                audio_files.append(None)
        else:
            logger.warning(f"⚠️ Audio file not found: {audio_file}")
            audio_files.append(None)
    
    # Convert to JSON string for JavaScript
    audio_files_json = json.dumps(audio_files)
    logger.info(f"📦 Prepared {len([f for f in audio_files if f])} audio files as data URIs")
    
    # Fullscreen container
    st.html("""
    <style>
    /* ===============================
    SPLASH BASE (SAFE VERSION)
    =============================== */

    .splash-container {
    width: 100%;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    justify-content: flex-start;
    align-items: center;
    color: white;
    text-align: center;
    padding: 20px;
    }


    .splash-content {
        width: 90%;
        max-width: 800px;
        justify-content: flex-start;
        margin-top: 80px;
    }



    /* Responsive text */
    .splash-title {
        font-size: clamp(2rem, 6vw, 3.5rem);
        font-weight: 800;
        
        margin: 0px;
        font-style: italic;
        font-size: 2rem;
            scroll-margin-top: 3.75rem;
            font-weight: 700;
    padding: 1.25rem 0px 1rem;
        font-family: "Source Sans", sans-serif;
    line-height: 1.2;
    margin: 0px;
    color: inherit;
    }

    .splash-subtitle {
    font-size: clamp(1.1rem, 3vw, 1.5rem);
    margin-bottom: 20px;
    }

    .splash-description {
    font-size: clamp(0.95rem, 2.5vw, 1.2rem);
    line-height: 1.6;
    }

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
    
    /* Mobile portrait ONLY */
    @media (max-width: 480px) and (orientation: portrait) {
        .splash-enabled section > div {
            padding: 0;
            overflow: hidden !important;
            position: fixed;
            width: 100%;
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
        justify-content: flex-start;
        flex-direction: column;
        align-items: center;
        z-index: 9999;
        color: white;
        text-align: center;
        padding: 0 20px;
        overflow: hidden;
        left: -20px; /* Adjust for Streamlit padding */
    }
    
    .splash-content {
        width: 90%;
        animation: fadeInUp 0.8s ease-out;
        margin-top: 80px;
    }
    
    .splash-title {
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-style: italic;
        font-size: 2rem;
        scroll-margin-top: 3.75rem;
        font-weight: 700;
        padding: 1.25rem 0px 1rem;
        font-family: "Source Sans", sans-serif;
        line-height: 1.2;
        color: white;
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
    <button class="audio-enable-btn" id="audio-enable-btn">
        🔊 Enable Audio
    </button>
    <button class="get-started-btn" id="get-started-btn">
        Get Started 🚀
    </button>
    <div class="splash-content">
        <div class="splash-title">
        <img src="https://raw.githubusercontent.com/boobootoo2/medbilldozer/refs/heads/main/static/images/avatars/transparent/billy__eyes_open__billdozer_up.png" alt="Billy character with eyes open looking up" style="
            height: 87px;
            width: auto;" /> 
            medBill<span style="color: rgb(45, 164, 78);">Dozer</span>
        </div>
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
                    height: 140px;
                }
                
                .splash-widget-container .billdozer_animation:first-of-type {
                    width: 20%;
                }
                
                .splash-widget-container .billdozer_animation:nth-of-type(2) {
                    width: 60%;
                }
                
                .splash-widget-container .billdozer_animation:nth-of-type(2) img {
                    width: 100px;
                    height: auto;
                }
                
                .splash-widget-container .billdozer_animation:nth-of-type(3) {
                    width: 20%;
                }
                
                .splash-widget-container .billdozer_animation img {
                    position: absolute;
                    bottom: -18px;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 150%;
                    opacity: 0;
                    animation: frameCycle 3s steps(1, end) 2;
                    animation-fill-mode: forwards;
                }
                @media (max-width: 424px) and (orientation: portrait) {
                    .splash-widget-container .inner-container {
                        width: auto;
                        height: auto;
                        padding-bottom: 40px;
                    }
                    .splash-widget-container .billdozer_animation img {
                        width: 100%;
                        bottom: -60px;
                    }
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
                    font-size: 18px;
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
                .transcript-line {
                font-size: 0.95rem;
                line-height: 1.4;
                margin: 6px 0;
                opacity: 0.6;
                transition: all 0.2s ease;
                }

                .transcript-line.active {
                font-weight: 700;
                opacity: 1;
                }

                #splash-transcript {
                scrollbar-width: thin; /* Firefox */
                scrollbar-color: rgba(255, 255, 255, 0.5) rgba(255, 255, 255, 0.1); /* Firefox */
                }

                /* Webkit browsers (Chrome, Safari, Edge) */
                #splash-transcript::-webkit-scrollbar {
                width: 8px;
                }

                #splash-transcript::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                }

                #splash-transcript::-webkit-scrollbar-thumb {
                background: rgba(255, 255, 255, 0.5);
                border-radius: 4px;
                }

                #splash-transcript::-webkit-scrollbar-thumb:hover {
                background: rgba(255, 255, 255, 0.7);
                }
                
                /* Transcript Accordion */
                .transcript-accordion {
                    margin-top: 12px;
                    text-align: center;
                }
                
                .transcript-accordion summary {
                    cursor: pointer;
                    padding: 8px 16px;
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 8px;
                    color: white;
                    font-size: 14px;
                    font-weight: 600;
                    list-style: none;
                    display: inline-block;
                    transition: all 0.2s ease;
                    user-select: none;
                }
                
                .transcript-accordion summary::-webkit-details-marker {
                    display: none;
                }
                
                .transcript-accordion summary::before {
                    content: '▶ ';
                    display: inline-block;
                    transition: transform 0.2s ease;
                    margin-right: 8px;
                }
                
                .transcript-accordion[open] summary::before {
                    transform: rotate(90deg);
                }
                
                .transcript-accordion summary:hover {
                    background: rgba(255, 255, 255, 0.2);
                    border-color: rgba(255, 255, 255, 0.5);
                }
                
                .transcript-accordion .transcript-content {
                    margin-top: 12px;
                    max-height: 70px;
                    overflow-y: auto;
                    text-align: center;
                }
                
                /* Audio Enable Button */
                .audio-enable-btn {
                    position: absolute;
                    top: 20px;
                    right: 30px;
                    background: rgba(255, 255, 255, 0.2);
                    border: 3px solid white;
                    color: white;
                    border-radius: 50px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: 700;
                    backdrop-filter: blur(10px);
                    transition: all 0.3s ease;
                    z-index: 10000;
                    display: none;
                    height: 48px;
                    box-sizing: border-box;
                }
                
                .audio-enable-btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                    transform: translateY(-2px);
                }
                
                .audio-enable-btn.show {
                    display: block;
                    animation: pulse 2s infinite;
                }
                
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.7; }
                }
                
                /* Get Started Button */
                .get-started-btn {
                    position: absolute;
                    top: 20px;
                    left: 30px;
                    background: white;
                    border: 3px solid white;
                    color: #667eea;
                    border-radius: 50px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: 700;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                    backdrop-filter: blur(10px);
                    transition: all 0.3s ease;
                    z-index: 10000;
                    height: 48px;
                    box-sizing: border-box;
                }
                
                .get-started-btn:hover {
                    background: #f0f0f0;
                    transform: translateY(-2px);
                    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
                }
                
                @media (max-width: 932px) and (orientation: landscape) {
                    .get-started-btn {
                        font-size: 14px;
                        height: 40px;
                    }
                    .audio-enable-btn {
                        font-size: 14px;
                        height: 40px;
                    }
                }
                
                @media (max-width: 1024px) {
                    .get-started-btn {
                        top: 50px;
                    }
                    .audio-enable-btn {
                        top: 50px;
                    }
                }
                /* Transcript Accordion */
                .transcript-accordion {
                    margin-top: 12px;
                    text-align: center;
                }
                
                .transcript-accordion summary {
                    cursor: pointer;
                    padding: 8px 16px;
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 8px;
                    color: white;
                    font-size: 14px;
                    font-weight: 600;
                    list-style: none;
                    display: inline-block;
                    transition: all 0.2s ease;
                    user-select: none;
                }
                
                .transcript-accordion summary::-webkit-details-marker {
                    display: none;
                }
                
                .transcript-accordion summary::before {
                    content: '▶ ';
                    display: inline-block;
                    transition: transform 0.2s ease;
                    margin-right: 8px;
                }
                
                .transcript-accordion[open] summary::before {
                    transform: rotate(90deg);
                }
                
                .transcript-accordion summary:hover {
                    background: rgba(255, 255, 255, 0.2);
                    border-color: rgba(255, 255, 255, 0.5);
                }
                
                .transcript-accordion .transcript-content {
                    margin-top: 12px;
                    max-height: 70px;
                    overflow-y: auto;
                    text-align: center;
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

<details class="transcript-accordion">
  <summary>Transcript</summary>
  <div class="transcript-content">
    <div
      id="splash-transcript"
  role="region"
  aria-label="Billdozer spoken messages"
  style="
    margin-top: 12px;
    text-align: center;
    max-height: 70px;
    overflow-y: scroll;
  "
>
  <div
    id="splash-live"
    aria-live="polite"
    aria-atomic="true"
    style="
      position: absolute;
      left: -9999px;
      height: 1px;
      width: 1px;
      overflow: hidden;
    "
  ></div>

    <p class="transcript-line" data-index="0">
    Hi! We’re Billy and Billie—your guides to finding billing mistakes.
    </p>
    <p class="transcript-line" data-index="1">
    We scan medical bills, pharmacy receipts, dental claims, and insurance statements to uncover overcharges, duplicates, and missed reimbursements.
    </p>
    <p class="transcript-line" data-index="2">
    Ready to see how easy it is to double-check your bills?
    </p>
    </div>
  </div>
</details>

    </div>
    </div>
    
    <script>
    (function() {
    if (window.parent && window.parent.document) {
        const body = window.parent.document.body;

        body.classList.add('splash-enabled');
        body.classList.add('splash-scroll-locked');

        console.log('[Splash] Scroll locked');
    }
    })();
    (function() {
        console.log("[Splash Widget] Script starting...");
        
        // Audio file paths (injected from Python)
        const audioFiles = """ + audio_files_json + """;
        console.log("[Splash Widget] Audio files:", audioFiles);
        
        // Track if audio has been enabled or muted (from Python config)
        const audioMuted = """ + ("true" if audio_muted else "false") + """;
        console.log("[Splash Widget] Audio muted:", audioMuted);
        
        let audioEnabled = !audioMuted;
        let audioBlockedDetected = false;
        const audioEnableBtn = document.getElementById('audio-enable-btn');
        
        const liveRegion = document.getElementById("splash-live");
        const transcriptLines = document.querySelectorAll(".transcript-line");
        let currentMessageIndex = -1;

        
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
            {
                character: "billie",
                message: "Hi! We’re Billy and Billie—your guides to finding billing mistakes."
            },
            {
                character: "billy",
                message: "We scan medical bills, pharmacy receipts, dental claims, and insurance statements to uncover overcharges, duplicates, and missed reimbursements."
            },
            {
                character: "billie",
                message: "Ready to see how easy it is to double-check your bills?"
            }
        ];

        
        // Create audio elements for each message
        const audioElements = [];
        console.log("[Splash Widget] Creating audio elements from:", audioFiles);
        console.log("[Splash Widget] Audio files type:", typeof audioFiles);
        console.log("[Splash Widget] Is array?", Array.isArray(audioFiles));
        
        rawMessages.forEach((msg, idx) => {
            const audioPath = audioFiles[idx];
            console.log(`[Splash Widget] Processing message ${idx}, path:`, audioPath, "type:", typeof audioPath);
            
            if (audioPath && audioPath !== 'None' && audioPath !== null) {
                try {
                    const audio = new Audio(audioPath);
                    audio.preload = 'auto';
                    
                    // Add event listeners for debugging
                    audio.addEventListener('loadeddata', () => {
                        console.log(`[Splash Widget] ✅ Audio ${idx} loaded successfully:`, audioPath);
                    });
                    audio.addEventListener('error', (e) => {
                        console.error(`[Splash Widget] ❌ Audio ${idx} load error:`, e, audioPath);
                    });
                    audio.addEventListener('play', () => {
                        console.log(`[Splash Widget] ▶️ Audio ${idx} started playing`);
                    });
                    audio.addEventListener('ended', () => {
                        console.log(`[Splash Widget] ⏹️ Audio ${idx} finished playing`);
                    });
                    
                    audioElements.push(audio);
                    console.log(`[Splash Widget] ✅ Created audio element ${idx}:`, audioPath);
                } catch (err) {
                    console.error("[Splash Widget] ❌ Failed to create audio:", err);
                    audioElements.push(null);
                }
            } else {
                console.warn(`[Splash Widget] ⚠️ Skipping message ${idx} - invalid path:`, audioPath);
                audioElements.push(null);
            }
        });
        
        console.log("[Splash Widget] Total audio elements created:", audioElements.filter(a => a !== null).length);
        
        const queue = [];
        const maxChars = 70;
        
        rawMessages.forEach(({ character, message }, msgIndex) => {
            // Split message into words
            const words = message.split(' ');
            let chunk = '';
            let isFirstChunk = true;
            
            words.forEach((word, index) => {
                const testChunk = chunk ? chunk + ' ' + word : word;
                
                if (testChunk.length > maxChars && chunk) {
                    // Push current chunk and start new one
                    queue.push({ 
                        character, 
                        message: chunk, 
                        audioIndex: msgIndex, 
                        isFirstChunk: isFirstChunk 
                    });
                    isFirstChunk = false;
                    chunk = word;
                } else {
                    chunk = testChunk;
                }
                
                // Push final chunk
                if (index === words.length - 1 && chunk) {
                    queue.push({ 
                        character, 
                        message: chunk, 
                        audioIndex: msgIndex, 
                        isFirstChunk: isFirstChunk 
                    });
                }
            });
        });
        
        let active = false;
        let currentAudio = null;
        
        function playNext() {
            console.log("[Splash Widget] Playing next message, queue length:", queue.length);
            if (!queue.length) {
                active = false;
                speechLayer.style.display = "none";
                container.classList.remove("talking-left", "talking-right");
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }
                console.log("[Splash Widget] Queue empty, finished");
                return;
            }
            
            active = true;

            const { character, message, audioIndex, isFirstChunk } = queue.shift();
            
            // Update message index when we hit a new message
            if (isFirstChunk && audioIndex !== currentMessageIndex) {
                currentMessageIndex = audioIndex;
                
                // Visual transcript sync
                transcriptLines.forEach((el, idx) => {
                    el.classList.toggle("active", idx === currentMessageIndex);
                    // Auto-scroll to active line
                    if (idx === currentMessageIndex) {
                        el.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
                    }
                });
            }
            
            // Play audio only on first chunk of each message (and if not muted)
            if (isFirstChunk && !audioMuted) {
                console.log(`[Splash Widget] First chunk of message ${audioIndex}`);
                console.log(`[Splash Widget] Audio element exists?`, !!audioElements[audioIndex]);
                console.log(`[Splash Widget] Audio element:`, audioElements[audioIndex]);
                
                if (audioElements[audioIndex]) {
                    if (currentAudio) {
                        console.log("[Splash Widget] Pausing previous audio");
                        currentAudio.pause();
                    }
                    currentAudio = audioElements[audioIndex];
                    console.log(`[Splash Widget] 🎵 Attempting to play audio ${audioIndex}...`);
                    console.log(`[Splash Widget] Audio src:`, currentAudio.src);
                    console.log(`[Splash Widget] Audio ready state:`, currentAudio.readyState);
                    console.log(`[Splash Widget] Audio paused?`, currentAudio.paused);
                    
                    currentAudio.play()
                        .then(() => {
                            console.log(`[Splash Widget] ✅ Successfully started playing audio ${audioIndex}`);
                            audioEnabled = true;
                            // Hide the enable button if it's showing
                            if (audioEnableBtn) {
                                audioEnableBtn.classList.remove('show');
                            }
                        })
                        .catch(err => {
                            console.error(`[Splash Widget] ❌ Audio playback failed for message ${audioIndex}:`, err);
                            console.error(`[Splash Widget] Error name:`, err.name);
                            console.error(`[Splash Widget] Error message:`, err.message);
                            
                            // Try to provide helpful error messages
                            if (err.name === 'NotAllowedError') {
                                console.error('[Splash Widget] 🚫 Browser blocked autoplay. User interaction required.');
                                console.error('[Splash Widget] 💡 Tip: Click the "Enable Audio" button.');
                                
                                // Show the enable audio button
                                if (audioEnableBtn && !audioBlockedDetected) {
                                    audioBlockedDetected = true;
                                    audioEnableBtn.classList.add('show');
                                    audioEnableBtn.textContent = '🔊 Click to Enable Audio';
                                }
                            } else if (err.name === 'NotSupportedError') {
                                console.error('[Splash Widget] 🚫 Audio format not supported by browser.');
                            }
                        });
                } else {
                    console.warn(`[Splash Widget] ⚠️ No audio element for message ${audioIndex}`);
                }
            }

            // Screen reader announcement
            if (liveRegion) {
                liveRegion.textContent = message;
            }


            console.log("[Splash Widget] Showing message from", character, ":", message);
            
            container.classList.remove("talking-left", "talking-right");
            container.classList.add(character === "billie" ? "talking-left" : "talking-right");
            
            speechText.textContent = message;
            speechLayer.style.display = "block";
            
            setTimeout(() => {
                speechLayer.style.display = "none";
                container.classList.remove("talking-left", "talking-right");
                console.log("[Splash Widget] Message complete, waiting before next");
                setTimeout(playNext, 1200);
            }, 3000);
        }
        
        // Audio enable button click handler
        if (audioEnableBtn) {
            audioEnableBtn.addEventListener('click', function() {
                console.log('[Splash Widget] 🎵 User clicked Enable Audio button');
                audioEnabled = true;
                audioEnableBtn.classList.remove('show');
                audioEnableBtn.textContent = '✅ Audio Enabled';
                
                // Try to play the first audio if we have one
                if (audioElements.length > 0 && audioElements[0]) {
                    console.log('[Splash Widget] 🎵 Attempting to play first audio after enable...');
                    audioElements[0].play()
                        .then(() => {
                            console.log('[Splash Widget] ✅ Audio playback working!');
                            audioEnableBtn.style.display = 'none';
                        })
                        .catch(err => {
                            console.error('[Splash Widget] ❌ Still cannot play:', err);
                            audioEnableBtn.textContent = '❌ Audio Blocked';
                        });
                }
            });
        }
        
        // Get Started button click handler
        const getStartedBtn = document.getElementById('get-started-btn');
        if (getStartedBtn) {
            getStartedBtn.addEventListener('click', function() {
                console.log('[Splash Widget] 🚀 User clicked Get Started button');
                
                // Find and click the Streamlit button in parent document
                if (window.parent && window.parent.document) {
                    const parentDoc = window.parent.document;
                    
                    // Try multiple selectors to find the button
                    let hiddenButton = null;
                    
                    // Try 1: By aria-label
                    hiddenButton = parentDoc.querySelector('button[aria-label="Get Started"]');
                    if (hiddenButton) {
                        console.log('[Splash Widget] ✅ Found button by aria-label');
                    }
                    
                    // Try 2: By help text
                    if (!hiddenButton) {
                        hiddenButton = parentDoc.querySelector('button[title="Get Started"]');
                        if (hiddenButton) {
                            console.log('[Splash Widget] ✅ Found button by title');
                        }
                    }
                    
                    // Try 3: Find any button with the arrow icon text
                    if (!hiddenButton) {
                        const buttons = parentDoc.querySelectorAll('button[data-testid*="baseButton"]');
                        for (let btn of buttons) {
                            if (btn.textContent.trim() === '▶' || btn.textContent.includes('▶')) {
                                hiddenButton = btn;
                                console.log('[Splash Widget] ✅ Found button by icon text');
                                break;
                            }
                        }
                    }
                    
                    // Try 4: Find by class structure (column with button)
                    if (!hiddenButton) {
                        const buttons = parentDoc.querySelectorAll('button');
                        console.log('[Splash Widget] 🔍 Searching through', buttons.length, 'buttons...');
                        for (let btn of buttons) {
                            const text = btn.textContent.trim();
                            console.log('[Splash Widget] 🔍 Button text:', text);
                            if (text === '▶') {
                                hiddenButton = btn;
                                console.log('[Splash Widget] ✅ Found button by exact match');
                                break;
                            }
                        }
                    }
                    
                    if (hiddenButton) {
                        console.log('[Splash Widget] ✅ Clicking button...');
                        hiddenButton.click();
                        console.log('[Splash Widget] ✅ Button clicked successfully');
                    } else {
                        console.error('[Splash Widget] ❌ Could not find hidden button after all attempts');
                    }
                }
            });
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

    # Actual Streamlit button (positioned off-screen but functional)
    # Using custom CSS to hide it visually but keep it in DOM for JavaScript
    st.markdown("""
        <style>
        /* Hide the dismiss button container visually but keep in DOM */
        div[data-testid="column"]:has(button[aria-label="Get Started"]) {
            position: fixed !important;
            left: -9999px !important;
            top: -9999px !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }
        /* Make sure button itself is still clickable via JavaScript */
        button[aria-label="Get Started"] {
            pointer-events: auto !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create button with clear aria-label for JavaScript to find
    if st.button("▶", key="dismiss_splash_btn", type="secondary", help="Get Started", use_container_width=False):
        dismiss_splash_screen()
        st.rerun()
