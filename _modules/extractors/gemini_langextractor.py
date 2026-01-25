import json
from typing import Dict, Optional
from google import genai

from _modules.extractors.extraction_prompt import FACT_KEYS, build_fact_extraction_prompt

# Lazy client initialization to avoid requiring API key at import time
_client = None


def _get_client():
    """Get or create the Gemini client lazily."""
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


def _safe_empty_result() -> Dict[str, Optional[str]]:
    """Return empty facts dictionary with all keys set to None.

    Returns:
        Dictionary with all FACT_KEYS mapped to None
    """
    return {k: None for k in FACT_KEYS}


def extract_facts_gemini(raw_text: str) -> Dict[str, Optional[str]]:
    """
    Gemini-based fact extractor.
    SAFE: never raises, always returns full schema.
    """

    if not raw_text or not raw_text.strip():
        return _safe_empty_result()

    prompt = build_fact_extraction_prompt(raw_text)

    try:
        response = _get_client().models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )

        text = (response.text or "").strip()
        data = json.loads(text)

        # Enforce schema
        return {k: data.get(k) for k in FACT_KEYS}

    except Exception as e:
        print(f"[gemini extractor] failed: {e}")
        return _safe_empty_result()


def run_prompt_gemini(prompt: str) -> str:
    """
    Runs a raw prompt using Gemini and returns the text response.
    Intended for Phase-2 extraction.
    SAFE: raises to caller (caller must catch).
    """

    response = _get_client().models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    return (response.text or "").strip()

