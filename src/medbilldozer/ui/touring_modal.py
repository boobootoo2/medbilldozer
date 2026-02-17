"""Touring Modal - Interactive overlay tour synced with sidebar guided tour.

Provides an engaging guided tour experience that:
- Syncs with the sidebar guided tour steps
- Displays modal overlay with avatar and speech bubble
- Plays audio narration using OpenAI TTS
- Auto-minimizes to sticky header when audio finishes
- Includes Cancel and Next navigation buttons
- Mobile responsive design with 0.3 opacity background
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Optional
from pathlib import Path
import logging
import base64
from medbilldozer.utils.image_paths import get_avatar_url
from medbilldozer.ui.audio_controls import is_audio_muted
from medbilldozer.ui.guided_tour import TOUR_STEPS, TourStep

logger = logging.getLogger(__name__)


def initialize_touring_modal_state():
    """Initialize touring modal session state variables.

    Note: Syncs with guided_tour state - uses tour_active and tour_current_step
    """
    if 'touring_modal_dismissed' not in st.session_state:
        st.session_state.touring_modal_dismissed = False
    if 'touring_modal_minimized' not in st.session_state:
        st.session_state.touring_modal_minimized = False


def should_show_touring_modal() -> bool:
    """Check if touring modal should be shown.

    Returns:
        bool: True if modal should display
    """
    # Don't show if dismissed
    if st.session_state.get('touring_modal_dismissed', False):
        return False

    # Don't show if tour is not active (syncs with sidebar tour)
    if not st.session_state.get('tour_active', False):
        return False

    # Show modal overlay when tour is active
    return True


def activate_touring_modal():
    """Activate the touring modal (synced with guided tour)."""
    st.session_state.tour_active = True
    st.session_state.touring_modal_dismissed = False
    st.session_state.touring_modal_minimized = False
    if 'tour_current_step' not in st.session_state:
        st.session_state.tour_current_step = 1


def get_current_touring_step() -> Optional[TourStep]:
    """Get the current touring step (synced with guided tour).

    Returns:
        Optional[TourStep]: Current step or None if not active
    """
    if not st.session_state.get('tour_active', False):
        return None

    step_num = st.session_state.get('tour_current_step', 1)
    for step in TOUR_STEPS:
        if step.id == step_num:
            return step
    return None


def advance_touring_step():
    """Move to the next touring step (synced with guided tour)."""
    current = st.session_state.get('tour_current_step', 1)
    if current < len(TOUR_STEPS):
        st.session_state.tour_current_step = current + 1
        # Reset minimized state when advancing
        st.session_state.touring_modal_minimized = False
    else:
        # Last step - complete the tour
        complete_touring_modal()


def minimize_touring_modal():
    """Minimize the touring modal to sticky header."""
    st.session_state.touring_modal_minimized = True


def expand_touring_modal():
    """Expand the minimized modal back to fullscreen."""
    st.session_state.touring_modal_minimized = False


def dismiss_touring_modal():
    """Dismiss the touring modal completely (synced with guided tour)."""
    st.session_state.touring_modal_dismissed = True
    st.session_state.tour_active = False
    st.session_state.touring_modal_minimized = False
    # Also mark tour as completed so it doesn't reappear
    st.session_state.tour_completed = True


def complete_touring_modal():
    """Complete the touring modal (reached end)."""
    dismiss_touring_modal()


def previous_tour_step():
    """Move to the previous step in the tour."""
    current = st.session_state.get('tour_current_step', 1)
    if current > 1:
        st.session_state.tour_current_step = current - 1


def get_character_for_step(step_id: int) -> str:
    """Get the character (billy or billie) for a given step.

    Args:
        step_id: The step ID (1-5)

    Returns:
        str: "billy" or "billie"
    """
    # Always use Billy for the touring modal
    return "billy"


def generate_touring_audio(step_id: int, narration: str) -> Optional[Path]:
    """Generate audio narration using OpenAI Neural TTS with caching.

    Args:
        step_id: The touring step ID
        narration: Text to synthesize

    Returns:
        Path to audio file, or None if generation fails
    """
    audio_dir = Path("audio")
    audio_dir.mkdir(exist_ok=True)

    audio_file = audio_dir / f"touring_step_{step_id}.mp3"

    # Return cached file if exists
    if audio_file.exists():
        logger.info(f"Using cached audio: {audio_file}")
        return audio_file

    # Try to generate using OpenAI TTS
    try:
        from openai import OpenAI

        # Initialize client (uses OPENAI_API_KEY from environment)
        client = OpenAI()

        # Choose voice based on character (alternating)
        character = get_character_for_step(step_id)
        voice = "nova" if character == "billie" else "echo"

        logger.info(f"Generating touring audio for step {step_id} (voice: {voice})...")

        # Generate speech
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=narration,
            speed=1.0
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


def get_audio_data_uri(step: TourStep) -> Optional[str]:
    """Get base64 data URI for audio file.

    Args:
        step: The touring step

    Returns:
        Optional[str]: Base64 data URI or None
    """
    # Check if audio is muted
    if is_audio_muted():
        return None

    # Generate audio file
    audio_file = generate_touring_audio(step.id, step.narration)

    if audio_file and audio_file.exists():
        try:
            with open(audio_file, "rb") as f:
                audio_data = f.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                data_uri = f"data:audio/mpeg;base64,{audio_base64}"
                logger.info(f"✅ Converted {audio_file.name} to base64 ({len(audio_base64)} chars)")
                return data_uri
        except Exception as e:
            logger.error(f"❌ Failed to read {audio_file}: {e}")
            return None
    else:
        logger.warning(f"⚠️ Audio file not found for step {step.id}")
        return None


@st.dialog("🚀 Guided Tour", width="large")
def touring_modal_dialog():
    """Render touring modal as a Streamlit dialog."""
    current_step = get_current_touring_step()

    if not current_step:
        return

    # Get character and avatar
    character = get_character_for_step(current_step.id)
    avatar_url = get_avatar_url(f"{character}__eyes_open__ready.png")

    # Display avatar and text side by side
    col_avatar, col_text = st.columns([1, 3])

    with col_avatar:
        st.image(avatar_url, width=100)

    with col_text:
        st.markdown(f"""
**Step {current_step.id} of {len(TOUR_STEPS)}: {current_step.title}**

{current_step.description}
        """)

    # Progress indicator
    progress = current_step.id / len(TOUR_STEPS)
    st.progress(progress, text=f"Step {current_step.id} of {len(TOUR_STEPS)}")

    st.divider()

    # Control buttons
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("✕ Cancel", key="touring_modal_cancel", use_container_width=True):
            dismiss_touring_modal()
            st.rerun()

    with col2:
        if st.button("▼ Minimize", key="touring_modal_minimize", use_container_width=True):
            minimize_touring_modal()
            st.rerun()

    with col3:
        if current_step.id > 1:
            if st.button("← Back", key="touring_modal_back", use_container_width=True):
                previous_tour_step()
                st.rerun()

    with col4:
        if current_step.id < len(TOUR_STEPS):
            if st.button("Next →", key="touring_modal_next", type="primary", use_container_width=True):
                advance_touring_step()
                st.rerun()
        else:
            if st.button("✓ Done", key="touring_modal_done", type="primary", use_container_width=True):
                complete_touring_modal()
                st.rerun()


def render_minimized_sticky_header():
    """Render a minimized sticky header with control buttons (non-blocking)."""
    current_step = get_current_touring_step()
    if not current_step:
        return

    # Get character and avatar
    character = get_character_for_step(current_step.id)
    avatar_url = get_avatar_url(f"{character}__eyes_open__ready.png")

    # Render sticky header with CSS
    st.markdown(f"""
        <style>
        .touring-minimized-header {{
            position: fixed;
            top: 80px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9998;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 12px 20px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            gap: 15px;
            color: white;
            pointer-events: none;
        }}

        .touring-minimized-header img {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: 2px solid white;
            object-fit: cover;
        }}

        .touring-minimized-header .message {{
            font-size: 14px;
            font-weight: 600;
        }}

        /* Style the button container */
        div[data-testid="stHorizontalBlock"]:has(button[key*="minimized_"]) {{
            position: fixed !important;
            top: 80px !important;
            right: 20px !important;
            z-index: 9999 !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border-radius: 12px !important;
            padding: 8px 12px !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
            gap: 8px !important;
            margin-top: 12px !important;
        }}

        /* Style individual buttons */
        button[key*="minimized_"] {{
            background: rgba(255, 255, 255, 0.25) !important;
            border: 1.5px solid rgba(255, 255, 255, 0.9) !important;
            color: white !important;
            padding: 8px 14px !important;
            border-radius: 8px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            margin-top: 12px;
        }}

        button[key*="minimized_"]:hover {{
            background: rgba(255, 255, 255, 0.35) !important;
        }}

        @media (max-width: 768px) {{
            .touring-minimized-header {{
                left: 10px;
                right: auto;
                transform: none;
                max-width: calc(50% - 20px);
            }}

            div[data-testid="stHorizontalBlock"]:has(button[key*="minimized_"]) {{
                right: 10px !important;
                top: 80px !important;
            }}
        }}
        </style>

        <div class="touring-minimized-header">
            <img src="{avatar_url}" alt="{character.capitalize()}" />
            <div class="message">Step {current_step.id} of {len(TOUR_STEPS)}</div>
        </div>
    """, unsafe_allow_html=True)

    # Render control buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✕", key="minimized_cancel", help="Cancel Tour"):
            dismiss_touring_modal()
            st.rerun()

    with col2:
        if st.button("↗️", key="minimized_expand", help="Expand Tour"):
            expand_touring_modal()
            st.rerun()

    with col3:
        if current_step.id < len(TOUR_STEPS):
            if st.button("→", key="minimized_next", help="Next Step", type="primary"):
                advance_touring_step()
                st.rerun()
        else:
            if st.button("✓", key="minimized_done", help="Finish Tour", type="primary"):
                complete_touring_modal()
                st.rerun()


def render_touring_modal():
    """Main render function - shows dialog or minimized header based on state."""
    if not st.session_state.get('tour_active', False) or st.session_state.get('touring_modal_dismissed', False):
        return

    is_minimized = st.session_state.get('touring_modal_minimized', False)

    if is_minimized:
        # Render minimized sticky header (non-blocking)
        render_minimized_sticky_header()
    else:
        # Render full dialog (blocking)
        touring_modal_dialog()


def render_fullscreen_modal(step: TourStep):
    """Render overlay touring modal with avatar, bubble, and controls.

    Args:
        step: The current touring step
    """
    # Get character for this step (alternating)
    character = get_character_for_step(step.id)

    # Get avatar URL
    avatar_url = get_avatar_url(f"{character}__eyes_open__ready.png")

    # Get audio data URI - DISABLED: don't play touring mp3s
    # audio_data_uri = get_audio_data_uri(step)
    audio_data_uri = None  # Disable audio playback

    # Estimate duration from narration length (rough: ~150 words per minute = ~2.5 words per second)
    # Average word length is 5 characters, so ~12.5 characters per second
    estimated_duration = len(step.narration) / 12.5
    fallback_duration = int(estimated_duration * 1000)  # Convert to milliseconds

    # Determine if we should use fallback timer (no audio or muted)
    use_fallback_timer = True  # Always use fallback since audio is disabled

    # Bubble pointer position based on character
    bubble_position = "left" if character == "billie" else "right"

    # Build the overlay modal HTML
    modal_html = f"""
    <style>
    body {{
        margin: 0;
        padding: 0;
    }}

    .touring-modal-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.3);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        left: -20px;
        pointer-events: none;
    }}

    .touring-modal-content {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 25px 20px 20px 20px;
        max-width: 550px;
        width: 85%;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        pointer-events: auto;
        color: white;
        text-align: center;
    }}

    .touring-avatar-container {{
        margin-bottom: 15px;
        animation: float 3s ease-in-out infinite;
    }}

    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-8px); }}
    }}

    .touring-avatar {{
        width: 70px;
        height: 70px;
        border-radius: 50%;
        object-fit: cover;
        background: white;
        border: 2px solid rgba(255, 255, 255, 0.9);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }}

    .touring-speech-bubble {{
        background: white;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        position: relative;
        margin-bottom: 20px;
    }}

    .bubble-text {{
        color: #333;
        font-size: 0.95rem;
        line-height: 1.5;
        font-weight: 500;
    }}

    .bubble-pointer {{
        position: absolute;
        top: -10px;
        width: 0;
        height: 0;
    }}

    .bubble-pointer.left {{
        left: 60px;
        border-left: 12px solid transparent;
        border-right: 12px solid transparent;
        border-bottom: 15px solid white;
    }}

    .bubble-pointer.right {{
        right: 60px;
        border-left: 12px solid transparent;
        border-right: 12px solid transparent;
        border-bottom: 15px solid white;
    }}

    .touring-controls {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 14px 20px;
        margin-top: 12px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4);
        max-width: 550px;
        width: 85%;
        pointer-events: auto;
    }}

    .touring-controls-buttons {{
        display: flex;
        gap: 10px;
        justify-content: center;
    }}

    .touring-controls button {{
        background: rgba(255, 255, 255, 0.25);
        border: 1.5px solid rgba(255, 255, 255, 0.9);
        color: white;
        padding: 10px 16px;
        border-radius: 50px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 600;
        backdrop-filter: blur(10px);
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 44px;
    }}

    .touring-controls button:hover {{
        background: rgba(255, 255, 255, 0.35);
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }}

    .touring-controls button.primary {{
        background: white;
        color: #667eea;
        border-color: white;
    }}

    .touring-controls button.primary:hover {{
        background: #f8f8f8;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.25);
    }}

    .touring-progress {{
        color: rgba(255, 255, 255, 0.9);
        font-size: 12px;
        font-weight: 600;
        margin-top: 15px;
        padding-top: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
    }}

    /* Mobile Responsive */
    @media (max-width: 768px) {{
        .touring-modal-content {{
            width: 90%;
            padding: 20px 15px 15px 15px;
        }}

        .touring-avatar {{
            width: 60px;
            height: 60px;
        }}

        .touring-speech-bubble {{
            padding: 15px 18px;
        }}

        .bubble-text {{
            font-size: 0.9rem;
        }}

        .touring-controls {{
            width: 90%;
            padding: 12px 16px;
        }}

        .touring-controls button {{
            padding: 9px 14px;
            font-size: 15px;
            min-width: 42px;
        }}
    }}

    @media (max-width: 480px) and (orientation: portrait) {{
        .touring-modal-content {{
            width: 95%;
            max-width: none;
        }}

        .touring-avatar {{
            width: 55px;
            height: 55px;
        }}

        .touring-speech-bubble {{
            padding: 14px 16px;
        }}

        .bubble-text {{
            font-size: 0.85rem;
        }}

        .touring-controls {{
            width: 95%;
            padding: 10px 12px;
        }}

        .touring-controls-buttons {{
            gap: 8px;
        }}

        .touring-controls button {{
            padding: 8px 12px;
            font-size: 14px;
            min-width: 40px;
        }}
    }}
    </style>

    <div class="touring-modal-overlay">
        <!-- Main Modal Content -->
        <div class="touring-modal-content">
            <!-- Avatar -->
            <div class="touring-avatar-container">
                <img src="{avatar_url}" class="touring-avatar" alt="{character.capitalize()} avatar" />
            </div>

            <!-- Speech Bubble -->
            <div class="touring-speech-bubble">
                <div class="bubble-pointer {bubble_position}"></div>
                <div class="bubble-text">{step.description}</div>
            </div>

            <!-- Progress -->
            <div class="touring-progress">Step {step.id} of {len(TOUR_STEPS)}</div>

            <!-- Audio (if available) -->
            {f'<audio id="touring-audio-step-{step.id}" preload="auto"><source src="{audio_data_uri}" type="audio/mpeg"></audio>' if audio_data_uri else ''}
        </div>
    </div>

    <script>
    (function() {{
        console.log('[Touring Modal] Overlay initialized - Step {step.id}');

        // Stop any previously playing audio in parent window and all iframes
        if (window.parent && window.parent.document) {{
            // Stop audio in parent window
            const allAudios = window.parent.document.querySelectorAll('audio');
            allAudios.forEach(function(prevAudio) {{
                if (!prevAudio.paused) {{
                    console.log('[Touring Modal] 🛑 Stopping audio in parent window');
                    prevAudio.pause();
                    prevAudio.currentTime = 0;
                }}
            }});

            // Stop audio in all iframes
            const allIframes = window.parent.document.querySelectorAll('iframe');
            allIframes.forEach(function(iframe) {{
                try {{
                    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                    const iframeAudios = iframeDoc.querySelectorAll('audio');
                    iframeAudios.forEach(function(audio) {{
                        if (!audio.paused) {{
                            console.log('[Touring Modal] 🛑 Stopping audio in iframe');
                            audio.pause();
                            audio.currentTime = 0;
                        }}
                    }});
                }} catch (e) {{
                    // Cross-origin iframe, skip
                    console.debug('[Touring Modal] Cannot access iframe (cross-origin)');
                }}
            }});
        }}

        // Button click handler
        window.clickStreamlitButton = function(ariaLabel) {{
            console.log('[Touring Modal] Button clicked:', ariaLabel);
            if (window.parent && window.parent.document) {{
                const btn = window.parent.document.querySelector(`button[aria-label="${{ariaLabel}}"]`);
                if (btn) {{
                    console.log('[Touring Modal] ✅ Clicking Streamlit button');
                    btn.click();
                }} else {{
                    console.error('[Touring Modal] ❌ Button not found:', ariaLabel);
                }}
            }}
        }};

        // Move Streamlit buttons into modal container
        setTimeout(function() {{
            if (window.parent && window.parent.document) {{
                // Find the touring modal content
                const modalContent = document.querySelector('.touring-modal-content');

                // Find the Streamlit buttons container in parent
                const parentDoc = window.parent.document;
                const buttonContainer = parentDoc.querySelector('.stIFrame + div[data-testid="stLayoutWrapper"]');

                if (modalContent && buttonContainer) {{
                    console.log('[Touring Modal] Moving buttons into modal container');

                    // Create a container div in the iframe for the buttons
                    const btnWrapper = document.createElement('div');
                    btnWrapper.id = 'touring-controls-moved';
                    btnWrapper.style.cssText = `
                        margin-top: 20px;
                        padding-top: 15px;
                        border-top: 1px solid rgba(255, 255, 255, 0.2);
                    `;

                    // Clone the button container and append to modal
                    const buttonClone = buttonContainer.cloneNode(true);
                    btnWrapper.appendChild(buttonClone);
                    modalContent.appendChild(btnWrapper);

                    // Add click handlers to cloned buttons
                    const clonedButtons = btnWrapper.querySelectorAll('button');
                    clonedButtons.forEach(function(btn, idx) {{
                        btn.addEventListener('click', function() {{
                            // Click the corresponding original button
                            const originalButtons = buttonContainer.querySelectorAll('button');
                            if (originalButtons[idx]) {{
                                originalButtons[idx].click();
                            }}
                        }});
                    }});

                    // Hide original buttons
                    buttonContainer.style.display = 'none';
                }}
            }}
        }}, 500);


        // Audio handling
        const audio = document.getElementById('touring-audio-step-{step.id}');

        if (audio) {{
            console.log('[Touring Modal] Audio element found for step {step.id}');

            // Wait for audio to load, then play after a small delay
            audio.addEventListener('loadeddata', function() {{
                console.log('[Touring Modal] Audio loaded for step {step.id}');

                // Stop any other audio elements in this iframe
                const otherAudios = document.querySelectorAll('audio');
                otherAudios.forEach(function(otherAudio) {{
                    if (otherAudio !== audio && !otherAudio.paused) {{
                        console.log('[Touring Modal] 🛑 Stopping other audio in this iframe');
                        otherAudio.pause();
                        otherAudio.currentTime = 0;
                    }}
                }});

                // Play this audio after a longer delay to ensure splash audio has stopped
                setTimeout(function() {{
                    // One final check - stop all audio again right before playing
                    if (window.parent && window.parent.document) {{
                        const allAudios = window.parent.document.querySelectorAll('audio');
                        allAudios.forEach(function(a) {{
                            if (!a.paused && a !== audio) {{
                                a.pause();
                                a.currentTime = 0;
                            }}
                        }});

                        const allIframes = window.parent.document.querySelectorAll('iframe');
                        allIframes.forEach(function(iframe) {{
                            try {{
                                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                                const iframeAudios = iframeDoc.querySelectorAll('audio');
                                iframeAudios.forEach(function(a) {{
                                    if (!a.paused && a !== audio) {{
                                        a.pause();
                                        a.currentTime = 0;
                                    }}
                                }});
                            }} catch (e) {{}}
                        }});
                    }}

                    // Now play the touring audio
                    audio.play().then(function() {{
                        console.log('[Touring Modal] ▶️ Audio playing - Step {step.id}');
                    }}).catch(function(e) {{
                        console.error('[Touring Modal] ❌ Audio play failed:', e);
                    }});
                }}, 1000);
            }}, {{ once: true }});

            // Auto-minimize when audio ends
            audio.addEventListener('ended', function() {{
                console.log('[Touring Modal] 🎵 Audio ended, minimizing in 1s');
                setTimeout(function() {{
                    clickStreamlitButton('Minimize Touring Modal');
                }}, 1000);
            }});

            // Error handling - fall back to timer
            audio.addEventListener('error', function(e) {{
                console.error('[Touring Modal] ❌ Audio error:', e);
                console.log('[Touring Modal] Using fallback timer: {fallback_duration}ms');
                setTimeout(function() {{
                    clickStreamlitButton('Minimize Touring Modal');
                }}, {fallback_duration});
            }});
        }} else {{
            console.log('[Touring Modal] No audio element (muted or failed)');
            {f'setTimeout(function() {{ clickStreamlitButton("Minimize Touring Modal"); }}, {fallback_duration});' if use_fallback_timer else ''}
        }}
    }})();
    </script>
    """

    # Render the modal (compact height)
    components.html(modal_html, height=450, scrolling=False)

    # Render hidden Streamlit buttons (off-screen)
    render_hidden_buttons()


def render_minimized_modal(step: TourStep):
    """Render minimized sticky header version of the modal.

    Args:
        step: The current touring step
    """
    # Get character for this step
    character = get_character_for_step(step.id)

    # Get avatar URL
    avatar_url = get_avatar_url(f"{character}__eyes_open__ready.png")

    # Truncate description for minimized view (remove emojis and truncate)
    clean_description = step.description.replace("👋", "").replace("📄", "").replace("🧠", "").replace("📌", "").replace("✨", "").strip()
    truncated_message = clean_description[:50] + "..." if len(clean_description) > 50 else clean_description

    # Build the minimized modal HTML
    minimized_html = f"""
    <style>
    .touring-modal-minimized {{
        position: fixed;
        top: 70px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9998;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 12px 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        gap: 15px;
        color: white;
        backdrop-filter: blur(10px);
    }}

    .mini-avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid white;
    }}

    .mini-message {{
        font-size: 14px;
        font-weight: 600;
        max-width: 300px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .mini-controls {{
        display: flex;
        gap: 10px;
    }}

    .mini-controls button {{
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid white;
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        cursor: pointer;
        font-size: 12px;
        font-weight: 700;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }}

    .mini-controls button:hover {{
        background: rgba(255, 255, 255, 0.3);
    }}

    /* Mobile Responsive */
    @media (max-width: 768px) {{
        .touring-modal-minimized {{
            left: 10px;
            right: 10px;
            transform: none;
            padding: 10px 15px;
        }}

        .mini-message {{
            max-width: 150px;
            font-size: 12px;
        }}

        .mini-avatar {{
            width: 32px;
            height: 32px;
        }}
    }}

    @media (max-width: 480px) and (orientation: portrait) {{
        .mini-message {{
            max-width: 100px;
        }}

        .mini-controls button {{
            padding: 5px 10px;
            font-size: 11px;
        }}
    }}
    </style>

    <div class="touring-modal-minimized">
        <img src="{avatar_url}" class="mini-avatar" alt="{character.capitalize()} avatar" />
        <div class="mini-message">{truncated_message}</div>
        <div class="mini-controls">
            <button onclick="clickStreamlitButton('Expand Touring Modal')">↗️ Expand</button>
            <button onclick="clickStreamlitButton('Dismiss Touring Modal')">✕</button>
        </div>
    </div>

    <script>
    (function() {{
        console.log('[Touring Modal] Minimized initialized');

        // Button click handler
        window.clickStreamlitButton = function(ariaLabel) {{
            console.log('[Touring Modal] Minimized button clicked:', ariaLabel);
            if (window.parent && window.parent.document) {{
                const btn = window.parent.document.querySelector(`button[aria-label="${{ariaLabel}}"]`);
                if (btn) {{
                    console.log('[Touring Modal] ✅ Clicking Streamlit button');
                    btn.click();
                }} else {{
                    console.error('[Touring Modal] ❌ Button not found:', ariaLabel);
                }}
            }}
        }};
    }})();
    </script>
    """

    # Render the minimized modal
    components.html(minimized_html, height=80, scrolling=False)

    # Render hidden Streamlit buttons
    render_hidden_buttons()


def render_hidden_buttons():
    """Render Streamlit control buttons styled as part of the modal."""
    # Style the buttons to match the modal design
    st.markdown("""
        <style>
        /* Gap for emotion cache */
        .st-emotion-cache-tn0cau {
            gap: 10px !important;
        }

        /* Container for touring modal controls */
        .stIFrame + div[data-testid="stLayoutWrapper"] {
            max-width: 550px !important;
            margin: 12px auto 0 auto !important;
            padding: 0 !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        /* Fixed container - target the horizontal block containing buttons */
        .stIFrame + div[data-testid="stLayoutWrapper"] .stHorizontalBlock {
            position: fixed !important;
            top: 20px !important;
            right: 20px !important;
            background: #e5e5e5 !important; /* Light mode - light gray */
            padding: 12px !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
            z-index: 10000 !important;
            width: auto !important;
            max-width: none !important;
        }

        /* Dark mode background */
        @media (prefers-color-scheme: dark) {
            .stIFrame + div[data-testid="stLayoutWrapper"] .stHorizontalBlock {
                background: #3a3a3a !important; /* Dark mode - dark gray */
            }
        }

        /* Style the column layout */
        .stIFrame + div[data-testid="stLayoutWrapper"] .stHorizontalBlock {
            gap: 10px !important;
            justify-content: center !important;
            display: flex !important;
            align-items: center !important;
        }

        /* Style individual buttons */
        .stIFrame + div[data-testid="stLayoutWrapper"] button {
            background: rgba(255, 255, 255, 0.25) !important;
            border: 1.5px solid rgba(255, 255, 255, 0.9) !important;
            color: white !important;
            padding: 10px 16px !important;
            border-radius: 50px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            min-width: 44px !important;
            margin-top: 12px !important;
        }

        /* Primary button (Next) */
        .st-key-touring_next_hidden button {
            background: white !important;
            color: #667eea !important;
            border-color: white !important;
        }

        /* Button hover effects */
        .stIFrame + div[data-testid="stLayoutWrapper"] button:hover {
            background: rgba(255, 255, 255, 0.35) !important;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
        }

        .st-key-touring_next_hidden button:hover {
            background: #f8f8f8 !important;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.25) !important;
        }

        /* Mobile responsive */
        @media (max-width: 768px) {
            .stIFrame + div[data-testid="stLayoutWrapper"] {
                max-width: 90% !important;
                padding: 12px 16px !important;
            }
            .stIFrame + div[data-testid="stLayoutWrapper"] .stHorizontalBlock {
                gap: 8px !important;
            }
            .stIFrame + div[data-testid="stLayoutWrapper"] button {
                padding: 9px 14px !important;
                font-size: 15px !important;
                min-width: 42px !important;
            }
        }

        @media (max-width: 480px) {
            .stIFrame + div[data-testid="stLayoutWrapper"] {
                max-width: 95% !important;
                padding: 10px 12px !important;
            }
            .stIFrame + div[data-testid="stLayoutWrapper"] .stHorizontalBlock {
                gap: 6px !important;
            }
            .stIFrame + div[data-testid="stLayoutWrapper"] button {
                padding: 8px 12px !important;
                font-size: 14px !important;
                min-width: 40px !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # Determine current state
    is_minimized = st.session_state.get('touring_modal_minimized', False)
    current_step = get_current_touring_step()

    # All 4 buttons: Cancel, Minimize, Maximize, Next
    col1, col2, col3, col4 = st.columns(4)

    # Cancel button
    with col1:
        if st.button("✕", key="touring_cancel_hidden",
                     help="Cancel Tour"):
            dismiss_touring_modal()
            st.rerun()

    # Minimize button (only active when not minimized)
    with col2:
        if st.button("▼", key="touring_minimize_hidden",
                     help="Minimize Tour",
                     disabled=is_minimized):
            minimize_touring_modal()
            st.rerun()

    # Maximize/Expand button (only active when minimized)
    with col3:
        if st.button("↗", key="touring_expand_hidden",
                     help="Expand Tour",
                     disabled=not is_minimized):
            expand_touring_modal()
            st.rerun()

    # Next button
    with col4:
        # Determine button text based on current step
        if current_step and current_step.id >= len(TOUR_STEPS):
            button_text = "✓"
            button_help = "Finish Tour"
        else:
            button_text = "→"
            button_help = "Next Step"

        if st.button(button_text, key="touring_next_hidden",
                     help=button_help):
            advance_touring_step()
            st.rerun()
