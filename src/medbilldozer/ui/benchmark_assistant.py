"""Benchmark Documentation Assistant - AI-powered help for benchmark analysis.

Provides contextual help and answers to questions about benchmark metrics,
performance monitoring, and regression detection.
"""

import streamlit as st
from pathlib import Path
from typing import Dict, List
import time
from medbilldozer.ui.doc_assistant import render_assistant_avatar, dispatch_billy_event


class BenchmarkAssistant:
    """AI-powered benchmark documentation assistant."""

    def __init__(self):
        """Initialize the benchmark assistant with documentation content."""
        self.docs_path = Path(__file__).parent.parent.parent.parent / "benchmarks"
        self.archive_path = Path(__file__).parent.parent.parent / "docs_archive_20260207" / "architecture"
        self.docs_cache = {}
        self._load_documentation()

    def _load_documentation(self):
        """Load all benchmark documentation files into memory."""
        # Benchmark-specific docs
        doc_files = {
            "README.md": self.docs_path,
            "ANNOTATION_GUIDE.md": self.docs_path,
            "GROUND_TRUTH_SCHEMA.md": self.docs_path,
            "MODEL_COMPARISON.md": self.docs_path,
            "benchmark_engine.md": self.archive_path,
        }

        for doc_file, base_path in doc_files.items():
            file_path = base_path / doc_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.docs_cache[doc_file] = f.read()

    def _build_context_prompt(self, user_question: str) -> str:
        """Build a comprehensive context prompt from benchmark documentation.

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

        prompt = f"""You are Billy, a helpful benchmark analysis assistant for medBillDozer's Production Stability Dashboard.

Your role is to help engineers and data scientists understand benchmark metrics, performance trends, and regression detection based ONLY on the official documentation provided below.

IMPORTANT GUIDELINES:
1. Answer questions using ONLY information from the benchmark documentation below - never make up metrics or features
2. Be technical and precise - your audience consists of engineers and data scientists
3. Structure answers clearly with numbered steps, bullet points, or code examples when appropriate
4. Include specific, actionable advice for interpreting metrics and debugging regressions
5. When discussing metrics (F1, precision, recall, RMSE), explain what they mean in the context of medical bill analysis
6. When discussing regressions, provide clear steps for investigation and root cause analysis
7. For data quality issues, suggest specific queries or filters to use in the dashboard
8. Use technical terminology appropriately (true positives, false negatives, confidence intervals, etc.)
9. End complex answers with a clear next step or recommended action
10. If the question requires information not in the docs, acknowledge this and suggest where they might find help

RESPONSE STRUCTURE:
- Start with a direct, technical answer
- Follow with relevant metrics or examples
- Include practical steps for using the dashboard
- Reference specific documentation sections when helpful
- Keep total length under 500 words unless question specifically asks for detail

TONE EXAMPLES:
✅ Good: "F1 score is calculated as the harmonic mean of precision and recall..."
✅ Good: "To investigate this regression, first check the per-category metrics..."
❌ Avoid: "I'm not sure about that..." (too uncertain)
❌ Avoid: "That's a great question!" (too casual)

DOCUMENTATION:
{full_docs}

USER QUESTION:
{user_question}

Please provide a technical, well-structured answer based on the documentation above. Focus on helping the user interpret metrics and take action based on benchmark results.
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
                    {"role": "system", "content": "You are a technical assistant for benchmark analysis and performance monitoring."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
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


def render_benchmark_assistant():
    """Render the benchmark documentation assistant in the sidebar."""

    # Initialize avatar character if not set
    if 'avatar_character' not in st.session_state:
        st.session_state.avatar_character = "billy"

    # Render avatar at the top (in sidebar)
    with st.sidebar:
        render_assistant_avatar()

    # Toggle button for character switch
    current_character = st.session_state.avatar_character
    other_character = "billie" if current_character == "billy" else "billy"
    button_label = f"Switch to {other_character.capitalize()}"

    if st.sidebar.button(button_label, key="benchmark_character_toggle"):
        st.session_state.avatar_character = other_character
        st.rerun()

    st.sidebar.markdown("---")

    # Initialize assistant
    if 'benchmark_assistant' not in st.session_state:
        st.session_state.benchmark_assistant = BenchmarkAssistant()

    # Initialize conversation history
    if 'benchmark_assistant_history' not in st.session_state:
        st.session_state.benchmark_assistant_history = []

    # AI provider selection
    ai_provider = st.sidebar.selectbox(
        "Assistant AI Provider:",
        ["gpt-4o-mini", "gemini-2.0-flash-exp"],
        help="Choose which AI service to use for the assistant",
        key="benchmark_ai_provider"
    )

    # Quick help buttons
    st.sidebar.markdown("**Quick Help:**")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("📊 Metrics", key="quick_help_metrics"):
            question = """I need to understand the benchmark metrics shown in the dashboard. Please explain:
1. What is F1 score and why is it the primary metric?
2. What do precision and recall mean in the context of medical bill error detection?
3. How is RMSE (savings estimation error) calculated?
4. What are "true positives", "false positives", and "false negatives" for billing errors?
5. What metric values indicate good vs poor performance?

Provide specific examples using medical billing scenarios (e.g., detecting upcoding or duplicate charges)."""
            dispatch_billy_event("BILLY_TALK_START")
            answer = st.session_state.benchmark_assistant.get_answer(question, ai_provider)
            dispatch_billy_event("BILLY_TALK_STOP")
            st.session_state.benchmark_assistant_history.append({
                "question": "📊 Metrics - Understanding benchmark metrics",
                "answer": answer,
            })
            st.rerun()

    with col2:
        if st.button("🚨 Regressions", key="quick_help_regressions"):
            question = """I see a regression alert in the dashboard. Please explain:
1. How are regressions detected? What thresholds trigger alerts?
2. What should I check first when investigating a regression?
3. How do I use the time-range filters to pinpoint when the regression started?
4. What are common causes of regressions (model changes, data drift, infrastructure)?
5. What's the process for confirming a true regression vs normal variance?

Give me a step-by-step debugging workflow for regression investigation."""
            dispatch_billy_event("BILLY_TALK_START")
            answer = st.session_state.benchmark_assistant.get_answer(question, ai_provider)
            dispatch_billy_event("BILLY_TALK_STOP")
            st.session_state.benchmark_assistant_history.append({
                "question": "🚨 Regressions - Investigating performance regressions",
                "answer": answer,
            })
            st.rerun()

    col3, col4 = st.sidebar.columns(2)

    with col3:
        if st.button("🔬 Models", key="quick_help_models"):
            question = """I want to understand model comparison in the benchmark system. Please explain:
1. What models are being compared (GPT-4o-mini, Gemini, MedGemma, etc.)?
2. How do I interpret the model comparison charts?
3. What are the tradeoffs between different models (accuracy, cost, latency)?
4. Which metrics should I prioritize when choosing a model for production?
5. How do I compare performance across different error categories (upcoding, duplicates, etc.)?

Include specific guidance on reading the dashboard visualizations."""
            dispatch_billy_event("BILLY_TALK_START")
            answer = st.session_state.benchmark_assistant.get_answer(question, ai_provider)
            dispatch_billy_event("BILLY_TALK_STOP")
            st.session_state.benchmark_assistant_history.append({
                "question": "🔬 Models - Comparing model performance",
                "answer": answer,
            })
            st.rerun()

    with col4:
        if st.button("📈 Trends", key="quick_help_trends"):
            question = """I need help interpreting the historical trend charts. Please explain:
1. What time ranges are available and when should I use each?
2. How do I identify patterns vs noise in the trend data?
3. What do the confidence bands/intervals represent?
4. How can I correlate performance changes with deployments or data updates?
5. What trends should trigger investigation vs just monitoring?

Focus on actionable insights from trend analysis."""
            dispatch_billy_event("BILLY_TALK_START")
            answer = st.session_state.benchmark_assistant.get_answer(question, ai_provider)
            dispatch_billy_event("BILLY_TALK_STOP")
            st.session_state.benchmark_assistant_history.append({
                "question": "📈 Trends - Analyzing performance trends",
                "answer": answer,
            })
            st.rerun()

    # Question input
    user_question = st.sidebar.text_input(
        "Ask about benchmarks:",
        value=st.session_state.get('benchmark_assistant_question', ''),
        placeholder="e.g., How is F1 score calculated?",
        key="benchmark_assistant_input"
    )

    # Clear the temporary question after it's been used
    if 'benchmark_assistant_question' in st.session_state:
        del st.session_state.benchmark_assistant_question

    # Ask button
    ask_button = st.sidebar.button("Ask Assistant", type="primary", use_container_width=True, key="benchmark_ask_button")

    # Process question
    if ask_button and user_question.strip():
        with st.spinner("🤔 Consulting benchmark documentation..."):
            dispatch_billy_event("BILLY_TALK_START")
            answer = st.session_state.benchmark_assistant.get_answer(user_question, ai_provider)
            dispatch_billy_event("BILLY_TALK_STOP")

            # Add to history
            st.session_state.benchmark_assistant_history.append({
                'question': user_question,
                'answer': answer
            })
            st.rerun()

    # Display conversation history (most recent first)
    if st.session_state.benchmark_assistant_history:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Recent Questions:**")

        # Show last 3 questions
        for i, qa in enumerate(reversed(st.session_state.benchmark_assistant_history[-3:])):
            with st.sidebar.expander(f"❓ {qa['question'][:50]}...", expanded=(i == 0)):
                st.markdown(qa['answer'])

    # Clear history button
    if st.session_state.benchmark_assistant_history:
        if st.sidebar.button("Clear History", use_container_width=True, key="benchmark_clear_history"):
            st.session_state.benchmark_assistant_history = []
            st.rerun()

    # Help footer
    st.sidebar.markdown("---")
    st.sidebar.caption(
        "💡 **Tip**: The assistant answers questions based on the benchmark documentation. "
        "For technical support, contact the MLOps team."
    )

    # Documentation quick access
    with st.sidebar.expander("📚 Benchmark Documentation"):
        doc_choice = st.selectbox(
            "Choose a guide:",
            [
                "📖 Benchmark Overview",
                "📊 Ground Truth Schema",
                "✏️ Annotation Guide",
                "🔬 Model Comparison",
                "⚙️ Benchmark Engine"
            ],
            label_visibility="collapsed",
            key="benchmark_doc_selector"
        )

        # Map choices to file paths
        doc_files = {
            "📖 Benchmark Overview": "benchmarks/README.md",
            "📊 Ground Truth Schema": "benchmarks/GROUND_TRUTH_SCHEMA.md",
            "✏️ Annotation Guide": "benchmarks/ANNOTATION_GUIDE.md",
            "🔬 Model Comparison": "benchmarks/MODEL_COMPARISON.md",
            "⚙️ Benchmark Engine": "docs_archive_20260207/architecture/benchmark_engine.md"
        }

        if st.button("📖 View Guide", key="open_benchmark_doc_sidebar", use_container_width=True):
            # Store the selected doc in session state to display it
            st.session_state['benchmark_sidebar_doc_view'] = doc_files[doc_choice]
            st.session_state['benchmark_sidebar_doc_title'] = doc_choice
            st.rerun()

    # Display selected documentation in main area (not sidebar - too long)
    # Note: This will be rendered in the main page, not in the sidebar
    # The calling page should check for this session state variable
