"""Documentation Assistant - AI-powered help sidebar.

Provides contextual help and answers to user questions by reading
the comprehensive documentation as a source of truth.
"""

import streamlit as st
from pathlib import Path
from typing import Optional, Dict, List
import re
import time
import random
import streamlit.components.v1 as components
import base64


# Module-level cache for avatar images (loaded once per server, not per session)
_BILLY_IMAGES_CACHE = None

def dispatch_billy_event(event_type: str):
    components.html(
        f"""
        <script>
            window.parent.document.dispatchEvent(
                new CustomEvent("billy-event", {{
                    detail: {{ type: "{event_type}" }}
                }})
            );
        </script>
        """,
        height=0,
    )



def _get_billy_images():
    """Load and cache Billy avatar images as base64 data URIs."""
    global _BILLY_IMAGES_CACHE
    
    if _BILLY_IMAGES_CACHE is None:
        avatar_dir = Path(__file__).parent.parent.parent / "static" / "images" / "avatars"
        avatar_images = [
            "billy__eyes_open__ready.png",           # 0
            "billy__eyes_closed__ready.png",         # 1
            "billy__eyes_open__talking.png",         # 2
            "billy__eyes_closed__talking.png",       # 3
            "billy__eyes_open__happy.png",           # 4
            "billy__eyes_open__billdozer_up.png",    # 5
            "billy__eyes_open__billdozer_down.png",  # 6
            "billy__eyes_open__smiling.png",         # 7
        ]
        
        # Convert to base64 data URIs
        b64_images = []
        for img_name in avatar_images:
            img_path = avatar_dir / img_name
            if img_path.exists():
                with open(img_path, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode()
                    b64_images.append(f"data:image/png;base64,{b64}")
            else:
                b64_images.append("")
        
        _BILLY_IMAGES_CACHE = b64_images
    
    return _BILLY_IMAGES_CACHE


class DocumentationAssistant:
    """AI-powered documentation assistant that provides contextual help."""
    
    def __init__(self):
        """Initialize the documentation assistant with documentation content."""
        self.docs_path = Path(__file__).parent.parent.parent / "docs"
        self.docs_cache = {}
        self._load_documentation()
    
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


def render_doc_assistant():
    if "assistant_talking" not in st.session_state:
        st.session_state.assistant_talking = False
    
    # Initialize avatar character selection
    if "avatar_character" not in st.session_state:
        st.session_state.avatar_character = "billy"

    """Render the documentation assistant in the sidebar."""
    
    def render_assistant_avatar():
        talking = st.session_state.assistant_talking
        character = st.session_state.avatar_character
        character_name = character.capitalize()
        
        # Embedded HTML/CSS/JS from avatar_prototype.html
        avatar_html = f"""
        <div style="display: flex; justify-content: center; padding: 12px 0;">
            <div style="display: flex; flex-direction: column; align-items: center;">
                <div class="child-div nameplate {character}" id="billyAvatar">
                    <img class="avatar-img" src="app/static/images/avatars/{character}__eyes_open__ready.png" style="display: block;">
                    <img class="avatar-img" src="app/static/images/avatars/{character}__eyes_closed__ready.png" style="display: none;">
                    <img class="avatar-img" src="app/static/images/avatars/{character}__eyes_open__talking.png" style="display: none;">
                    <img class="avatar-img" src="app/static/images/avatars/{character}__eyes_closed__talking.png" style="display: none;">
                    <img class="avatar-img" src="app/static/images/avatars/{character}__eyes_open__smiling.png" style="display: none;">
                </div>
            </div>
        </div>
        
        <style>
            .child-div {{
                width: 80px;
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                align-items: center;
                position: relative;
            }}
            
            .avatar-img {{
                width: 80px;
                height: 80px;
                border-radius: 50%;
                object-fit: cover;
                background: white;
                border: 2px solid rgba(255, 255, 255, 0.8);
            }}
            
            .child-div.nameplate::after {{
                content: "";
                position: absolute;
                top: 100%;
                margin-top: 8px;
                left: 50%;
                transform: translateX(-50%);
                width: 92px;
                height: 26px;
                border-radius: 6px;
                background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0.15) 18%, rgba(20,20,20,0.95) 55%, rgba(255,255,255,0.18) 100%);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.45), inset 0 -1px 0 rgba(0,0,0,0.85), 0 3px 6px rgba(0,0,0,0.35);
                z-index: 1;
            }}
            
            .child-div.nameplate.billy::before {{
                content: "Billy";
                position: absolute;
                top: calc(100% + 16px);
                left: 50%;
                transform: translateX(-50%);
                width: 92px;
                text-align: center;
                font-size: 12px;
                font-weight: 900;
                letter-spacing: 1px;
                text-transform: uppercase;
                color: #ffffff;
                text-shadow: 0 1px 0 rgba(0,0,0,0.95), 0 -1px 0 rgba(255,255,255,0.35), 0 0 8px rgba(255,255,255,0.35);
                z-index: 2;
            }}
            
            .child-div.nameplate.billie::before {{
                content: "Billie";
                position: absolute;
                top: calc(100% + 16px);
                left: 50%;
                transform: translateX(-50%);
                width: 92px;
                text-align: center;
                font-size: 12px;
                font-weight: 900;
                letter-spacing: 1px;
                text-transform: uppercase;
                color: #ffffff;
                text-shadow: 0 1px 0 rgba(0,0,0,0.95), 0 -1px 0 rgba(255,255,255,0.35), 0 0 8px rgba(255,255,255,0.35);
                z-index: 2;
            }}
        </style>
        
        <script>
    let idleTimers = [];
    let talkingTimers = [];
    const div = document.getElementById('billyAvatar');

    function showOnly(index) {{
        const imgs = div.querySelectorAll('img');
        imgs.forEach((img, i) => {{
            img.style.display = i === index ? 'block' : 'none';
        }});
    }}

    function scheduleBlink() {{
        const delay = Math.random() * 4000 + 4000;
        const timer = setTimeout(() => {{
            if (div.classList.contains('talking')) return;
            showOnly(1);
            setTimeout(() => {{
                showOnly(0);
                scheduleBlink();
            }}, 150);
        }}, delay);
        idleTimers.push(timer);
    }}

    function startTalking() {{
        idleTimers.forEach(t => clearTimeout(t));
        idleTimers = [];

        div.classList.add('talking');

        function cycleTalking() {{
            if (!div.classList.contains('talking')) return;
            const index = Math.floor(Math.random() * 2) + 2;
            showOnly(index);
            const timer = setTimeout(cycleTalking, Math.random() * 800 + 400);
            talkingTimers.push(timer);
        }}

        cycleTalking();
    }}

    function stopTalking() {{
        div.classList.remove('talking');
        talkingTimers.forEach(t => clearTimeout(t));
        talkingTimers = [];
        showOnly(4); // smiling
        setTimeout(() => {{
            showOnly(0);
            scheduleBlink();
        }}, 5000);
    }}

    // 🔑 LISTEN FOR EVENTS FROM STREAMLIT
    window.parent.document.addEventListener("billy-event", (event) => {{
        if (!event.detail || !event.detail.type) return;

        switch (event.detail.type) {{
            case "BILLY_TALK_START":
                startTalking();
                break;
            case "BILLY_TALK_STOP":
                stopTalking();
                break;
        }}
    }});


    scheduleBlink();
</script>

        """
        
        with st.sidebar:
            components.html(avatar_html, height=140)
    
    # Render avatar at the top
    render_assistant_avatar()
    
    # Toggle button for character switch
    current_character = st.session_state.avatar_character
    other_character = "billie" if current_character == "billy" else "billy"
    button_label = f"Switch to {other_character.capitalize()}"
    
    if st.sidebar.button(button_label, key="character_toggle"):
        st.session_state.avatar_character = other_character
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Documentation Assistant")
    
    # Initialize assistant
    if 'doc_assistant' not in st.session_state:
        st.session_state.doc_assistant = DocumentationAssistant()
    
    # Initialize conversation history
    if 'assistant_history' not in st.session_state:
        st.session_state.assistant_history = []
    
    # AI provider selection
    ai_provider = st.sidebar.selectbox(
        "Assistant AI Provider:",
        ["openai", "gemini"],
        help="Choose which AI service to use for the assistant"
    )
    
    # Quick help buttons
    st.sidebar.markdown("**Quick Help:**")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🚀 Getting Started", width="stretch"):
            st.session_state.assistant_question = "How do I get started with medBillDozer?"
    
    with col2:
        if st.button("🔒 Privacy Info", width="stretch"):
            st.session_state.assistant_question = "Is my medical data private and secure?"
    
    col3, col4 = st.sidebar.columns(2)
    
    with col3:
        if st.button("💰 Savings", width="stretch"):
            st.session_state.assistant_question = "How do I interpret the savings estimates?"
    
    with col4:
        if st.button("❓ Troubleshoot", width="stretch"):
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
    ask_button = st.sidebar.button("Ask Assistant", type="primary", width="stretch")
    
    # Process question
    if ask_button and user_question.strip():
        # 🗣️ Billy starts talking
        dispatch_billy_event("BILLY_TALK_START")

        status_placeholder = st.sidebar.empty()
        status_placeholder.info("🤔 Consulting documentation...")

        answer = st.session_state.doc_assistant.get_answer(
            user_question, ai_provider
        )

        status_placeholder.empty()

        # 🛑 Billy stops talking
        dispatch_billy_event("BILLY_TALK_STOP")

        st.session_state.assistant_history.append({
            "question": user_question,
            "answer": answer,
        })

        st.rerun()

        # Show status in sidebar
        status_placeholder = st.sidebar.empty()
        status_placeholder.info("🤔 Consulting documentation...")
        
        answer = st.session_state.doc_assistant.get_answer(user_question, ai_provider)
        
        # Clear status
        status_placeholder.empty()
        

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
        if st.sidebar.button("Clear History", width="stretch"):
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
    # Initialize dismissed alerts in session state
    if 'dismissed_alerts' not in st.session_state:
        st.session_state.dismissed_alerts = set()
    
    # Check if this alert has been dismissed
    alert_key = f"help_{context}"
    if alert_key in st.session_state.dismissed_alerts:
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
        
        # Create dismissible alert with custom HTML
        # Use a Streamlit button container for dismissing
        col1, col2 = st.sidebar.columns([9, 1])
        
        with col1:
            st.sidebar.info(
                f"{help_info['icon']} **{help_info['title']}**\n\n{help_info['message']}"
            )
        
        with col2:
            if st.button("✕", key=f"dismiss_{alert_key}", help="Dismiss"):
                st.session_state.dismissed_alerts.add(alert_key)
                st.rerun()
