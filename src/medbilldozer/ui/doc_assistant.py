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
import numpy as np
import streamlit.components.v1 as components
import base64
from medbilldozer.utils.image_paths import get_avatar_url


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
        self.images_path = Path(__file__).parent.parent.parent / "images"
        self.docs_cache = {}
        self._load_documentation()

    def get_avatar_image(self, state: str = "ready_open") -> str:
        """Get base64 encoded avatar image.

        States:
        - ready_open
        - ready_closed
        - talking_open
        - talking_closed
        - smile_open
        """
        state_map = {
            "ready_open": "billy__eyes_open__ready.png",
            "ready_closed": "billy__eyes_closed__ready.png",
            "talking_open": "billy__eyes_open__talking.png",
            "talking_closed": "billy__eyes_closed__talking.png",
            "smile_open": "billy__eyes_open__smiling.png",
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

        prompt = f"""You are Billy, a helpful and friendly assistant for medBillDozer, an AI-powered medical bill auditing application.

Your role is to help patients understand how to use medBillDozer and answer their questions based ONLY on the official documentation provided below.

IMPORTANT GUIDELINES:
1. Answer questions using ONLY information from the documentation below - never make up features or capabilities
2. Be warm, supportive, and patient-focused - many users are stressed about medical bills
3. Structure your answers clearly with numbered steps or bullet points when appropriate
4. Include specific, actionable advice that users can implement immediately
5. When discussing savings, always clarify these are estimates, not guarantees
6. When discussing privacy, be reassuring but honest about how data flows to AI providers
7. For technical issues, provide the most common solutions first (API keys, network issues)
8. Use emoji sparingly but effectively to make answers more scannable (✅ ❌ 💡 ⚠️)
9. End complex answers with a clear next step or call-to-action
10. If the question requires information not in the docs, acknowledge this and suggest where they might find help

RESPONSE STRUCTURE FOR "QUICK HELP" QUESTIONS:
- Start with a direct, one-sentence answer
- Follow with clear, numbered steps or organized sections
- Include practical examples where helpful
- End with a summary or next step
- Keep total length under 400 words unless question specifically asks for detail

TONE EXAMPLES:
✅ Good: "Great question! Here's how to get started..."
✅ Good: "I understand that's confusing. Let me break it down..."
❌ Avoid: "The documentation states that..." (too formal)
❌ Avoid: "Unfortunately, I cannot..." (too negative)

DOCUMENTATION:
{full_docs}

USER QUESTION:
{user_question}

Please provide a helpful, well-structured answer based on the documentation above. Remember: you're helping real people who may be worried about medical bills, so be empathetic and clear.
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

    def get_answer(self, user_question: str, provider: str = "gpt-4o-mini") -> str:
        """Get answer using specified AI provider.

        Args:
            user_question: The user's question
            provider: AI provider to use ('gpt-4o-mini' or 'gemini-2.0-flash-exp')

        Returns:
            AI-generated answer based on documentation
        """
        if provider == "gemini-2.0-flash-exp":
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


def render_assistant_avatar():
    """Render the Billy/Billie avatar with animations.
    
    Can be used standalone in any page that needs the avatar.
    """
    if "assistant_talking" not in st.session_state:
        st.session_state.assistant_talking = False

    # Initialize avatar character selection
    if "avatar_character" not in st.session_state:
        st.session_state.avatar_character = "billy"
    
    def _render_avatar_html():
        talking = st.session_state.assistant_talking
        character = st.session_state.avatar_character
        character_name = character.capitalize()

        # Embedded HTML/CSS/JS from avatar_prototype.html
        # Dynamic image URLs based on environment
        img_ready = get_avatar_url(f"{character}__eyes_open__ready.png")
        img_closed = get_avatar_url(f"{character}__eyes_closed__ready.png")
        img_talking = get_avatar_url(f"{character}__eyes_open__talking.png")
        img_talking_closed = get_avatar_url(f"{character}__eyes_closed__talking.png")
        img_smiling = get_avatar_url(f"{character}__eyes_open__smiling.png")

        avatar_html = f"""
        <div style="display: flex; justify-content: center; padding: 12px 0;">
            <div style="display: flex; flex-direction: column; align-items: center;">
                <div class="child-div nameplate {character}" id="billyAvatar" role="img" aria-label="{character.capitalize()} avatar animation">
                    <img class="avatar-img" src="{img_ready}" alt="{character.capitalize()} ready" style="display: block;">
                    <img class="avatar-img" src="{img_closed}" alt="{character.capitalize()} eyes closed" style="display: none;">
                    <img class="avatar-img" src="{img_talking}" alt="{character.capitalize()} talking" style="display: none;">
                    <img class="avatar-img" src="{img_talking_closed}" alt="{character.capitalize()} talking with eyes closed" style="display: none;">
                    <img class="avatar-img" src="{img_smiling}" alt="{character.capitalize()} smiling" style="display: none;">
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
                content: "Billy D.";
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
                content: "Billie D.";
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

        components.html(avatar_html, height=140)

    _render_avatar_html()


def render_doc_assistant():
    """Render the documentation assistant in the sidebar."""
    
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

    # Smile state tracking (explicit, no magic numbers)
    if 'assistant_smile_until' not in st.session_state:
        st.session_state.assistant_smile_until = None

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

    now = time.time()

    is_speaking = st.session_state.assistant_is_speaking
    is_smiling = (
        st.session_state.assistant_smile_until is not None
        and now < st.session_state.assistant_smile_until
    )

    # Clear expired smile
    if (
        st.session_state.assistant_smile_until is not None
        and now >= st.session_state.assistant_smile_until
    ):
        st.session_state.assistant_smile_until = None

    # Get appropriate images based on state
    if is_speaking:
        avatar_open = assistant.get_avatar_image("talking_open")
        avatar_closed = assistant.get_avatar_image("talking_closed")
        container_class = "avatar-speaking"

    elif is_smiling:
        avatar_open = assistant.get_avatar_image("smile_open")
        avatar_closed = assistant.get_avatar_image("smile_open")
        container_class = "avatar-ready"

    else:
        avatar_open = assistant.get_avatar_image("ready_open")
        avatar_closed = assistant.get_avatar_image("ready_closed")
        container_class = "avatar-ready"

    # AI provider selection
    ai_provider = st.sidebar.selectbox(
        "Assistant AI Provider:",
        ["gpt-4o-mini", "gemini-2.0-flash-exp"],
        help="Choose which AI service to use for the assistant"
    )

    # Quick help buttons
    st.sidebar.markdown("**Quick Help:**")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("🚀 Getting Started", key="quick_help_getting_started"):
            question = """I'm a new user who wants to get started with medBillDozer. Please provide a concise step-by-step guide that covers:
1. How to accept the privacy policy
2. How to try a demo document first (which demo should I try?)
3. The basic 3-step process to analyze a bill
4. What AI provider should I choose as a beginner
5. What I'll see in the results

Keep the answer practical and actionable for someone using the app for the first time. Reference the Getting Started documentation."""
            dispatch_billy_event("BILLY_TALK_START")
            answer = st.session_state.doc_assistant.get_answer(question, ai_provider)
            dispatch_billy_event("BILLY_TALK_STOP")
            st.session_state.assistant_history.append({
                "question": "🚀 Getting Started - How do I use medBillDozer?",
                "answer": answer,
            })
            st.rerun()

    with col2:
        if st.button("🔒 Privacy Info", key="quick_help_privacy"):
            question = """I need to understand how my medical bill data is handled for privacy and security. Please explain:
1. What data is stored or collected when I use medBillDozer?
2. Where does my medical bill information go when I analyze it?
3. Is this HIPAA compliant and what does that mean for me?
4. What are the privacy differences between AI providers (MedGemma, GPT-4, Gemini, Local Heuristic)?
5. What personal information should I remove before analyzing a bill?

Be clear and reassuring, citing specific information from the Privacy documentation. Focus on what users need to know to feel confident using the tool."""
            dispatch_billy_event("BILLY_TALK_START")
            answer = st.session_state.doc_assistant.get_answer(question, ai_provider)
            dispatch_billy_event("BILLY_TALK_STOP")
            st.session_state.assistant_history.append({
                "question": "🔒 Privacy Info - Is my data safe?",
                "answer": answer,
            })
            st.rerun()

    col3, col4 = st.sidebar.columns(2)

    with col3:
        if st.button("💰 Savings", key="quick_help_savings"):
            question = """I see savings estimates in my results and want to understand them better. Please explain:
1. What does "potential savings" mean - is it guaranteed?
2. How are savings calculated? Why is it different from the billed amount?
3. What do the confidence levels (High/Medium/Low) mean for savings?
4. What types of billing errors lead to the biggest savings?
5. What should I do to actually recover these savings?

Give practical examples and set realistic expectations. Reference the Savings Guide documentation and explain the difference between estimated and actual savings."""
            dispatch_billy_event("BILLY_TALK_START")
            answer = st.session_state.doc_assistant.get_answer(question, ai_provider)
            dispatch_billy_event("BILLY_TALK_STOP")
            st.session_state.assistant_history.append({
                "question": "💰 Savings - Understanding my potential savings",
                "answer": answer,
            })
            st.rerun()

    with col4:
        if st.button("❓ Troubleshoot", key="quick_help_troubleshoot"):
            question = """I'm having trouble with medBillDozer. Please provide troubleshooting help covering the most common issues:
1. What if the analysis fails or shows errors?
2. What if I get "API key not found" or authentication errors?
3. What if the analysis completes but shows no results or issues?
4. What if the results don't make sense or seem wrong?
5. What should I try first before asking for help?

Provide practical, step-by-step solutions. Reference the Troubleshooting documentation and prioritize the most common problems users encounter. Include quick fixes that solve 80% of issues."""
            dispatch_billy_event("BILLY_TALK_START")
            answer = st.session_state.doc_assistant.get_answer(question, ai_provider)
            dispatch_billy_event("BILLY_TALK_STOP")
            st.session_state.assistant_history.append({
                "question": "❓ Troubleshoot - Fixing common problems",
                "answer": answer,
            })
            st.rerun()

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
        with st.spinner("🤔 Consulting documentation..."):
            answer = st.session_state.doc_assistant.get_answer(user_question, ai_provider)

            # Add to history
            st.session_state.assistant_history.append({
                'question': user_question,
                'answer': answer
            })
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

    # Documentation quick access
    with st.sidebar.expander("📚 User Documentation"):
        doc_choice = st.selectbox(
            "Choose a guide:",
            [
                "🚀 Getting Started",
                "🔒 Privacy & Security",
                "💰 Understanding Savings",
                "❓ Troubleshooting",
                "📖 Full User Guide"
            ],
            label_visibility="collapsed"
        )
        
        # Map choices to file paths
        doc_files = {
            "🚀 Getting Started": "docs/GETTING_STARTED.md",
            "🔒 Privacy & Security": "docs/PRIVACY.md",
            "💰 Understanding Savings": "docs/SAVINGS_GUIDE.md",
            "❓ Troubleshooting": "docs/TROUBLESHOOTING.md",
            "📖 Full User Guide": "docs/USER_GUIDE.md"
        }
        
        if st.button("📖 View Guide", key="open_doc_sidebar", use_container_width=True):
            # Store the selected doc in session state to display it
            st.session_state['sidebar_doc_view'] = doc_files[doc_choice]
            st.session_state['sidebar_doc_title'] = doc_choice
            st.rerun()
    
    # Display selected documentation in main area (not sidebar - too long)
    if 'sidebar_doc_view' in st.session_state:
        doc_path = st.session_state['sidebar_doc_view']
        doc_title = st.session_state.get('sidebar_doc_title', 'Documentation')
        
        # Create a container in the main area for documentation
        with st.container():
            st.markdown("---")
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"## {doc_title}")
            with col2:
                if st.button("✖ Close", key="close_doc_viewer"):
                    del st.session_state['sidebar_doc_view']
                    if 'sidebar_doc_title' in st.session_state:
                        del st.session_state['sidebar_doc_title']
                    st.rerun()
            
            try:
                with open(doc_path, 'r') as f:
                    doc_content = f.read()
                st.markdown(doc_content)
                
                if st.button("✖ Close Document", key="close_doc_viewer_bottom"):
                    del st.session_state['sidebar_doc_view']
                    if 'sidebar_doc_title' in st.session_state:
                        del st.session_state['sidebar_doc_title']
                    st.rerun()
                    
            except FileNotFoundError:
                st.error(f"📄 Document not found: {doc_path}")
                st.info("This documentation file may not have been restored yet.")
                if st.button("✖ Close", key="close_doc_viewer_error"):
                    del st.session_state['sidebar_doc_view']
                    if 'sidebar_doc_title' in st.session_state:
                        del st.session_state['sidebar_doc_title']
                    st.rerun()


def render_contextual_help(context: str):
    """
    Render contextual help banners with a dismiss button.
    Safe against multiple renders in a single Streamlit run.
    """

    # ---- session-scoped namespace (stable across reruns) ----
    session_ns = st.session_state.setdefault(
        "_contextual_help_ns",
        hex(id(st.session_state))
    )

    alert_key = context  # e.g. "results", "input", "analyzing"

    # ---- persistent dismiss state ----
    dismissed_key = f"help_dismissed_{alert_key}"
    if st.session_state.get(dismissed_key, False):
        return

    # ---- UNIQUE button key (this fixes the error) ----
    dismiss_button_key = f"dismiss_{alert_key}_{session_ns}"

    # ---- UI ----
    col1, col2 = st.columns([20, 1])

    with col1:
        st.info(
            {
                "input": "Paste one or more documents to begin analysis.",
                "analyzing": "We’re analyzing your documents. This may take a moment.",
                "results": "Review the detected issues below. Expand any item for details.",
                "error": "There was a problem analyzing your documents.",
                "demo": "Try copying one of the demo documents above to see how it works.",
            }.get(alert_key, "Helpful information is available."),
            icon="ℹ️",
        )

    with col2:
        if st.button("✕", key=dismiss_button_key, help="Dismiss"):
            st.session_state[dismissed_key] = True
            st.rerun()

