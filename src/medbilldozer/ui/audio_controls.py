"""Audio Controls - Mute/unmute button for audio narration.

Provides a persistent mute button that controls all audio playback
across splash screen and guided tour.
"""

import streamlit as st
from medbilldozer.utils.config import should_show_mute_button, is_audio_enabled


def initialize_audio_state():
    """Initialize audio state in session state."""
    if 'audio_muted' not in st.session_state:
        # Start unmuted by default (respects config)
        st.session_state.audio_muted = False


def is_audio_muted() -> bool:
    """Check if audio is currently muted.
    
    Returns:
        bool: True if audio is muted or disabled in config
    """
    initialize_audio_state()
    
    # If audio is disabled in config, treat as muted
    if not is_audio_enabled():
        return True
    
    return st.session_state.audio_muted


def toggle_mute():
    """Toggle audio mute state."""
    initialize_audio_state()
    st.session_state.audio_muted = not st.session_state.audio_muted


def render_mute_button():
    """Render a floating mute/unmute button in the top-right corner.
    
    The button appears as a small icon button that persists across pages
    and controls all audio playback.
    """
    initialize_audio_state()
    
    # Don't show if disabled in config or audio feature disabled
    if not should_show_mute_button() or not is_audio_enabled():
        return
    
    muted = st.session_state.audio_muted
    icon = "🔇" if muted else "🔊"
    tooltip = "Unmute audio" if muted else "Mute audio"
    
    # Inject CSS for floating button
    # SECURITY: unsafe_allow_html=True is safe here because:
    # - Contains only static CSS for styling - no executable code
    # - No user input or dynamic content
    # - Pure styling for floating mute button positioning
    st.markdown("""
        <style>
        .audio-mute-button {
            position: fixed;
            top: 70px;
            right: 20px;
            z-index: 9999;
            background: rgba(255, 255, 255, 0.95);
            border: 2px solid #e0e0e0;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            transition: all 0.2s ease;
            font-size: 24px;
        }
        
        .audio-mute-button:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
            border-color: #1f77b4;
        }
        
        .audio-mute-button.muted {
            background: rgba(200, 200, 200, 0.95);
            border-color: #999;
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .audio-mute-button {
                background: rgba(40, 40, 40, 0.95);
                border-color: #555;
            }
            .audio-mute-button:hover {
                border-color: #4a9eff;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create button container in sidebar or main area
    with st.sidebar:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(
                icon,
                key="audio_mute_button",
                help=tooltip,
                type="secondary",
                use_container_width=True
            ):
                toggle_mute()
                st.rerun()


def render_inline_mute_button():
    """Render an inline mute button (for use within other components).
    
    This is a smaller, more compact version suitable for embedding
    in other UI elements.
    """
    initialize_audio_state()
    
    if not should_show_mute_button() or not is_audio_enabled():
        return
    
    muted = st.session_state.audio_muted
    icon = "🔇" if muted else "🔊"
    label = "Unmute" if muted else "Mute"
    
    if st.button(
        f"{icon} {label}",
        key="inline_audio_mute_button",
        type="secondary"
    ):
        toggle_mute()
        st.rerun()


def get_audio_enabled_for_javascript() -> str:
    """Get audio enabled state as JavaScript boolean.
    
    Returns:
        str: JavaScript boolean ('true' or 'false')
    """
    return 'false' if is_audio_muted() else 'true'


def inject_audio_state_into_html(html: str) -> str:
    """Inject audio mute state into HTML/JavaScript.
    
    Replaces placeholder {{AUDIO_ENABLED}} with actual state.
    
    Args:
        html: HTML string with {{AUDIO_ENABLED}} placeholder
        
    Returns:
        str: HTML with audio state injected
    """
    audio_enabled = get_audio_enabled_for_javascript()
    return html.replace('{{AUDIO_ENABLED}}', audio_enabled)
