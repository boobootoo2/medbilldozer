"""Audio Preference Dialog - Ask users about audio before showing splash screen.

Shows a simple dialog asking if visitors want audio narration during the tour,
then stores their preference before proceeding to the splash screen.
"""

import streamlit as st


def should_show_audio_preference_dialog() -> bool:
    """Check if audio preference dialog should be shown.
    
    Returns:
        bool: True if user hasn't set audio preference yet
    """
    if 'audio_preference_set' not in st.session_state:
        st.session_state.audio_preference_set = False
    
    return not st.session_state.audio_preference_set


def render_audio_preference_dialog():
    """Render audio preference dialog before splash screen.
    
    Asks user if they want audio narration during the tour and splash screen.
    Stores preference in session state for use by audio_controls module.
    """
    # Fullscreen centered dialog
    st.html("""
    <style>
    /* Hide Streamlit default elements for clean dialog */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Fullscreen container */
    .audio-pref-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .audio-pref-dialog {
        background: white;
        border-radius: 20px;
        padding: 50px;
        max-width: 600px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        text-align: center;
        animation: slideUp 0.6s ease-out;
    }
    
    @keyframes slideUp {
        from {
            transform: translateY(30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .audio-pref-icon {
        font-size: 72px;
        margin-bottom: 20px;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .audio-pref-title {
        font-size: 32px;
        font-weight: bold;
        color: #333;
        margin-bottom: 15px;
    }
    
    .audio-pref-subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 40px;
        line-height: 1.6;
    }
    
    .audio-pref-buttons {
        display: flex;
        gap: 20px;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .audio-pref-note {
        margin-top: 30px;
        font-size: 14px;
        color: #999;
        font-style: italic;
    }
    
    .audio-button {
        display: inline-block;
        padding: 15px 40px;
        margin: 10px;
        font-size: 18px;
        font-weight: 600;
        border: none;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        color: white;
    }
    
    .audio-button-yes {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .audio-button-yes:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
    
    .audio-button-no {
        background: linear-gradient(135deg, #868f96 0%, #596164 100%);
    }
    
    .audio-button-no:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(89, 97, 100, 0.4);
    }
    </style>
    """)
    
    # Use CSS to absolutely position the dialog content instead of manual spacing
    # Create centered columns for buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Add wrapper div with absolute positioning for true vertical centering
        st.markdown("""
        <div style="
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 10000;
            width: 600px;
            max-width: 90vw;
        ">
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; background: white; border-radius: 20px; padding: 50px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
            <div style="font-size: 72px; margin-bottom: 20px;">🔊</div>
            <div style="font-size: 32px; font-weight: bold; color: #333; margin-bottom: 15px;">Welcome to medBillDozer!</div>
            <div style="font-size: 18px; color: #666; margin-bottom: 40px; line-height: 1.6;">
                Would you like audio narration during your tour?<br>
                Billy and Billie can guide you with their voices.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Buttons inside the white dialog
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button(
                "🔊 Yes, Play Audio",
                key="audio_pref_yes",
                type="primary",
                use_container_width=True
            ):
                # Enable audio
                st.session_state.audio_muted = False
                st.session_state.audio_preference_set = True
                st.rerun()
        
        with col_b:
            if st.button(
                "🔇 No, Silent Mode",
                key="audio_pref_no",
                use_container_width=True
            ):
                # Mute audio
                st.session_state.audio_muted = True
                st.session_state.audio_preference_set = True
                st.rerun()
        
        # Note at bottom
        st.markdown(
            """
            <div style="text-align: center; margin-top: 20px; color: #666; font-size: 14px;">
            💡 <i>You can change this preference later in the app settings</i>
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )
