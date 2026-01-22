"""Documentation Assistant - AI-powered help sidebar.

Provides contextual help and answers to user questions by reading
the comprehensive documentation as a source of truth.
"""

import streamlit as st
from pathlib import Path
from typing import Optional, Dict, List
import re
import base64
import time
import numpy as np


class DocumentationAssistant:
    """AI-powered documentation assistant that provides contextual help."""
    
    def __init__(self):
        """Initialize the documentation assistant with documentation content."""
        self.docs_path = Path(__file__).parent.parent.parent / "docs"
        self.images_path = Path(__file__).parent.parent.parent / "images"
        self.docs_cache = {}
        self._load_documentation()
    
    def get_avatar_image(self, state: str = "ready_open") -> str:
        """Get base64 encoded avatar image.
        
        This follows the randomized algorithms for blinking used by an android on the Enterprise.
        Data's blink patterns were designed to appear human-like while maintaining precise
        mathematical intervals derived from Fourier transform harmonics.
        
        Args:
            state: Avatar state - "ready_open", "ready_closed", "talking_open", "talking_closed"
            
        Returns:
            Base64 encoded image data URL
        """
        state_map = {
            "ready_open": "billy__eyes_open__ready.png",
            "ready_closed": "billy__eyes_closed__ready.png",
            "talking_open": "billy__eyes_open__talking.png",
            "talking_closed": "billy__eyes_closed__talking.png"
        }
        
        img_name = state_map.get(state, "billy__eyes_open__ready.png")
        avatar_file = self.images_path / "avatars" / img_name
        
        if avatar_file.exists():
            with open(avatar_file, 'rb') as f:
                img_bytes = f.read()
                img_base64 = base64.b64encode(img_bytes).decode()
                return f"data:image/png;base64,{img_base64}"
        return ""
    
    def _load_documentation(self):
        """Load all documentation files into memory."""
        doc_files = [
            "QUICKSTART.md",
            "USER_GUIDE.md",
            "INDEX.md",
            "README.md",
        ]
        
        for doc_file in doc_files:
            file_path = self.docs_path / doc_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.docs_cache[doc_file] = f.read()
    
    def _build_context_prompt(self, user_question: str) -> str:
        """Build a comprehensive context prompt from documentation.
        
        Args:
            user_question: The user's question
            
        Returns:
            Formatted prompt with documentation context
        """
        # Combine all documentation
        full_docs = "\n\n---\n\n".join([
            f"# {filename}\n\n{content}"
            for filename, content in self.docs_cache.items()
        ])
        
        prompt = f"""You are a helpful assistant for medBillDozer, an AI-powered medical bill auditing application.

Your role is to help users by answering questions based ONLY on the official documentation provided below.

IMPORTANT GUIDELINES:
1. Answer questions using ONLY information from the documentation below
2. Be concise and helpful - users want quick answers
3. If the documentation doesn't cover the topic, say so clearly
4. Provide specific section references when helpful (e.g., "See Quick Start Guide")
5. Use a friendly, supportive tone
6. For technical issues, suggest checking the Troubleshooting section
7. Always remind users of important disclaimers when relevant

DOCUMENTATION:
{full_docs}

USER QUESTION:
{user_question}

Please provide a helpful, accurate answer based on the documentation above. If the question isn't covered in the docs, politely say so and suggest what the user might do instead.
"""
        return prompt
    
    def get_answer_openai(self, user_question: str) -> str:
        """Get answer using OpenAI API.
        
        Args:
            user_question: The user's question
            
        Returns:
            AI-generated answer based on documentation
        """
        try:
            from openai import OpenAI
            
            client = OpenAI()
            prompt = self._build_context_prompt(user_question)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful documentation assistant for medBillDozer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3,  # Lower temperature for more factual responses
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"❌ OpenAI API Error: {str(e)}\n\nPlease check your OPENAI_API_KEY environment variable."
    
    def get_answer_gemini(self, user_question: str) -> str:
        """Get answer using Google Gemini API.
        
        Args:
            user_question: The user's question
            
        Returns:
            AI-generated answer based on documentation
        """
        try:
            from google import genai
            
            client = genai.Client()
            prompt = self._build_context_prompt(user_question)
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
            )
            
            return response.text.strip()
            
        except Exception as e:
            return f"❌ Gemini API Error: {str(e)}\n\nPlease check your GOOGLE_API_KEY environment variable."
    
    def get_answer(self, user_question: str, provider: str = "openai") -> str:
        """Get answer using specified AI provider.
        
        Args:
            user_question: The user's question
            provider: AI provider to use ('openai' or 'gemini')
            
        Returns:
            AI-generated answer based on documentation
        """
        if provider == "gemini":
            return self.get_answer_gemini(user_question)
        else:
            return self.get_answer_openai(user_question)
    
    def search_docs(self, query: str) -> List[Dict[str, str]]:
        """Search documentation for relevant sections.
        
        Args:
            query: Search query
            
        Returns:
            List of matching sections with file and content
        """
        results = []
        query_lower = query.lower()
        
        for filename, content in self.docs_cache.items():
            # Split into sections by headers
            sections = re.split(r'\n##+ ', content)
            
            for section in sections:
                if query_lower in section.lower():
                    # Extract section title
                    lines = section.split('\n')
                    title = lines[0] if lines else "Untitled"
                    
                    # Get first few lines as preview
                    preview = '\n'.join(lines[1:6])
                    
                    results.append({
                        'file': filename,
                        'title': title,
                        'preview': preview[:200] + "..." if len(preview) > 200 else preview
                    })
        
        return results[:5]  # Return top 5 matches


def calculate_blink_probability() -> bool:
    """Calculate if avatar should blink using Fourier transform harmonics.
    
    This follows the randomized algorithms for blinking used by an android on the Enterprise.
    Uses harmonic analysis to create natural-seeming but mathematically precise blink timing,
    similar to how Data's positronic neural net regulated involuntary humanoid behaviors.
    
    Returns:
        True if avatar should blink, False otherwise
    """
    # Use current time as seed for Fourier series
    t = time.time()
    
    # Generate harmonic components (simulating neural oscillations)
    # Base frequency at 8 seconds with natural variation (blinks every 5-12 seconds)
    harmonics = np.array([
        np.sin(2 * np.pi * t / 8.0),       # Base frequency ~8s
        np.sin(2 * np.pi * t / 4.0) * 0.5,  # First harmonic
        np.sin(2 * np.pi * t / 2.67) * 0.3, # Second harmonic
        np.sin(2 * np.pi * t / 2.0) * 0.2   # Third harmonic
    ])
    
    # Sum harmonics and normalize
    fourier_value = np.sum(harmonics)
    
    # Blink threshold: creates ~5-10% blink probability per check
    # Results in human-like blink frequency (minimum 5+ seconds between blinks)
    blink_threshold = 1.6
    
    return fourier_value > blink_threshold


def render_doc_assistant():
    """Render the documentation assistant in the sidebar."""
    st.sidebar.markdown("---")
    
    # Initialize assistant
    if 'doc_assistant' not in st.session_state:
        st.session_state.doc_assistant = DocumentationAssistant()
    
    # Initialize conversation history
    if 'assistant_history' not in st.session_state:
        st.session_state.assistant_history = []
    
    # Initialize avatar state
    if 'assistant_is_speaking' not in st.session_state:
        st.session_state.assistant_is_speaking = False
    if 'avatar_frame' not in st.session_state:
        st.session_state.avatar_frame = 1
    
    # Get avatar images with new system
    assistant = st.session_state.doc_assistant
    
    # Determine avatar state
    is_speaking = st.session_state.assistant_is_speaking
    should_blink = calculate_blink_probability()
    
    # Get appropriate images based on state
    if is_speaking:
        avatar_open = assistant.get_avatar_image("talking_open")
        avatar_closed = assistant.get_avatar_image("talking_closed")
    else:
        avatar_open = assistant.get_avatar_image("ready_open")
        avatar_closed = assistant.get_avatar_image("ready_closed")
    
    # Display avatar with title and animation
    if avatar_open and avatar_closed:
        animation_style = """
        <style>
        [data-testid="stSidebar"] .stElementContainer:first-of-type {
            display: none !important;
        }
        .avatar-container {
            position: relative;
            width: 80px;
            height: 80px;
            margin: 0 auto;
        }
        .avatar-frame {
            position: absolute;
            top: 0;
            left: 0;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: 2px solid #4CAF50;
            object-fit: cover;
        }
        .avatar-frame-base {
            opacity: 1;
            z-index: 1;
        }
        .avatar-frame-overlay {
            opacity: 0;
            z-index: 2;
        }
        @keyframes blink {
            0%, 97% { opacity: 0; }
            97.5%, 99.5% { opacity: 1; }
            100% { opacity: 0; }
        }
        @keyframes talk {
            0%, 49% { opacity: 1; }
            50%, 100% { opacity: 0; }
        }
        .avatar-ready .avatar-frame-overlay {
            animation: blink 6.5s infinite;
        }
        .avatar-speaking .avatar-frame-overlay {
            animation: talk 0.6s infinite, blink 6.5s infinite;
        }
        </style>
        """
        
        # Determine container class and which images to show
        if is_speaking:
            # Speaking animation (alternates between open and closed mouth, with periodic blinks)
            container_class = "avatar-speaking"
            st.sidebar.markdown(f"""{animation_style}
<div style="text-align: center; margin-bottom: 1rem;">
    <div class="avatar-container {container_class}">
        <img src="{avatar_open}" class="avatar-frame avatar-frame-base">
        <img src="{avatar_closed}" class="avatar-frame avatar-frame-overlay">
    </div>
    <h3 style="margin-top: 0.5rem; font-size: 1.2rem;">Documentation Assistant</h3>
</div>""", unsafe_allow_html=True)
        else:
            # Ready state - show open eyes with periodic blinks
            container_class = "avatar-ready"
            st.sidebar.markdown(f"""{animation_style}
<div style="text-align: center; margin-bottom: 1rem;">
    <div class="avatar-container {container_class}">
        <img src="{avatar_open}" class="avatar-frame avatar-frame-base">
        <img src="{avatar_closed}" class="avatar-frame avatar-frame-overlay">
    </div>
    <h3 style="margin-top: 0.5rem; font-size: 1.2rem;">Documentation Assistant</h3>
</div>""", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("### 🤖 Documentation Assistant")
    
    # AI provider selection
    ai_provider = st.sidebar.radio(
        "Assistant AI Provider:",
        ["openai", "gemini"],
        help="Choose which AI service to use for the assistant"
    )
    
    # Quick help buttons
    st.sidebar.markdown("**Quick Help:**")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🚀 Getting Started", use_container_width=True):
            st.session_state.assistant_question = "How do I get started with medBillDozer?"
    
    with col2:
        if st.button("🔒 Privacy Info", use_container_width=True):
            st.session_state.assistant_question = "Is my medical data private and secure?"
    
    col3, col4 = st.sidebar.columns(2)
    
    with col3:
        if st.button("💰 Savings", use_container_width=True):
            st.session_state.assistant_question = "How do I interpret the savings estimates?"
    
    with col4:
        if st.button("❓ Troubleshoot", use_container_width=True):
            st.session_state.assistant_question = "My analysis failed. What should I do?"
    
    # Question input
    user_question = st.sidebar.text_input(
        "Ask a question:",
        value=st.session_state.get('assistant_question', ''),
        placeholder="e.g., How do I analyze a bill?",
        key="doc_assistant_input"
    )
    
    # Clear the temporary question after it's been used
    if 'assistant_question' in st.session_state:
        del st.session_state.assistant_question
    
    # Ask button
    ask_button = st.sidebar.button("Ask Assistant", type="primary", use_container_width=True)
    
    # Check if we're in the middle of processing
    if 'processing_question' in st.session_state and st.session_state.processing_question:
        # Get the queued question
        question = st.session_state.queued_question
        provider = st.session_state.queued_provider
        
        # Set speaking state for animation
        st.session_state.assistant_is_speaking = True
        
        with st.spinner("🤔 Consulting documentation..."):
            answer = st.session_state.doc_assistant.get_answer(question, provider)
            
            # Reset states
            st.session_state.assistant_is_speaking = False
            st.session_state.processing_question = False
            
            # Add to history
            st.session_state.assistant_history.append({
                'question': question,
                'answer': answer
            })
        
        st.rerun()
    
    # Process question button click
    if ask_button and user_question.strip():
        # Start speaking animation immediately
        st.session_state.assistant_is_speaking = True
        # Queue the question for processing
        st.session_state.processing_question = True
        st.session_state.queued_question = user_question
        st.session_state.queued_provider = ai_provider
        st.rerun()
    
    # Display conversation history (most recent first)
    if st.session_state.assistant_history:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Recent Questions:**")
        
        # Show last 3 questions
        for i, qa in enumerate(reversed(st.session_state.assistant_history[-3:])):
            with st.sidebar.expander(f"❓ {qa['question'][:50]}...", expanded=(i == 0)):
                st.markdown(qa['answer'])
    
    # Clear history button
    if st.session_state.assistant_history:
        if st.sidebar.button("Clear History", use_container_width=True):
            st.session_state.assistant_history = []
            st.rerun()
    
    # Help footer
    st.sidebar.markdown("---")
    st.sidebar.caption(
        "💡 **Tip**: The assistant answers questions based on the official documentation. "
        "For technical support, see the troubleshooting guide."
    )
    
    # Documentation links
    with st.sidebar.expander("📚 View Documentation"):
        st.markdown("""
        - [Quick Start Guide](docs/QUICKSTART.md)
        - [User Guide](docs/USER_GUIDE.md)
        - [Documentation Index](docs/INDEX.md)
        """)


def render_contextual_help(context: str):
    """Render contextual help based on current page/action.
    
    Args:
        context: Current context (e.g., 'input', 'results', 'error')
    """
    # Initialize dismissed help state
    if 'dismissed_help' not in st.session_state:
        st.session_state.dismissed_help = set()
    
    # Check if this context has been dismissed
    if context in st.session_state.dismissed_help:
        return
    
    help_messages = {
        'input': {
            'icon': '📝',
            'title': 'Document Input Help',
            'message': 'Paste your complete medical bill, EOB, or receipt text here. Include all details: headers, line items, dates, and amounts.'
        },
        'demo': {
            'icon': '🎯',
            'title': 'Try Demo Documents',
            'message': 'Select a demo document to see how medBillDozer works. These realistic examples show common billing issues.'
        },
        'analyzing': {
            'icon': '⏳',
            'title': 'Analysis in Progress',
            'message': 'medBillDozer is examining your document for billing errors. This typically takes 5-30 seconds.'
        },
        'results': {
            'icon': '✅',
            'title': 'Understanding Results',
            'message': 'Review the issues found and potential savings. Click "Ask Assistant" in the sidebar for help interpreting any result.'
        },
        'error': {
            'icon': '❌',
            'title': 'Need Help?',
            'message': 'Something went wrong. Try the troubleshooting quick help button in the assistant sidebar.'
        }
    }
    
    if context in help_messages:
        help_info = help_messages[context]
        
        # Create dismissible bubble with custom HTML
        st.sidebar.markdown(f"""
        <style>
        .help-bubble {{
            position: relative;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .help-bubble-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.5rem;
        }}
        .help-bubble-title {{
            font-weight: 600;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .help-bubble-message {{
            font-size: 0.9rem;
            line-height: 1.5;
            opacity: 0.95;
        }}
        </style>
        <div class="help-bubble">
            <div class="help-bubble-header">
                <div class="help-bubble-title">{help_info['icon']} {help_info['title']}</div>
            </div>
            <div class="help-bubble-message">{help_info['message']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add dismiss button below the bubble
        if st.sidebar.button(f"✕ Dismiss", key=f"dismiss_{context}", use_container_width=True):
            st.session_state.dismissed_help.add(context)
            st.rerun()
