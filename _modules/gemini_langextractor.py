import json
from typing import Dict, Optional
from google import genai

from _modules.extraction_prompt import FACT_KEYS, build_fact_extraction_prompt

client = genai.Client()


def _safe_empty_result() -> Dict[str, Optional[str]]:
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
        response = client.models.generate_content(
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

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    return (response.text or "").strip()
