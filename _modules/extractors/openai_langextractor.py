# _modules/openai_langextractor.py
"""OpenAI-based LLM fact extractor and generic prompt runner.

Provides OpenAI GPT-powered fact extraction from healthcare documents and
utility functions for running arbitrary prompts against OpenAI models.
Safe by design - never raises exceptions, always returns complete schema.
"""

import json
import re
from typing import Dict, Optional
from openai import OpenAI

from _modules.extractors.extraction_prompt import (
    FACT_KEYS,
    build_fact_extraction_prompt,
)


client = OpenAI()


def _safe_empty_result() -> Dict[str, Optional[str]]:
    """Return empty facts dictionary with all keys set to None.

    Returns:
        Dictionary with all FACT_KEYS mapped to None
    """
    return {k: None for k in FACT_KEYS}


def _clean_json(text: str) -> str:
    """
    Removes markdown fences and leading junk.
    """
    text = text.strip()

    # Remove ```json fences
    text = re.sub(r"^```(?:json)?", "", text)
    text = re.sub(r"```$", "", text)

    return text.strip()


def extract_facts_openai(raw_text: str) -> Dict[str, Optional[str]]:
    """
    Extract structured healthcare facts using OpenAI.
    SAFE: never raises, always returns all keys.
    """

    if not raw_text or not raw_text.strip():
        return _safe_empty_result()

    prompt = build_fact_extraction_prompt(raw_text)


    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": "You extract structured healthcare facts."},
                {"role": "user", "content": prompt},
            ],
        )

        content = response.choices[0].message.content or ""
        cleaned = _clean_json(content)

        data = json.loads(cleaned)

        # Guarantee shape
        return {k: data.get(k) for k in FACT_KEYS}

    except Exception as e:
        print(f"[langextract] failed: {e}")
        return _safe_empty_result()


def run_prompt_openai(prompt: str) -> str:
    """
    Runs a raw prompt using OpenAI and returns the text response.
    Intended for Phase-2 extraction (receipt items, line items, etc).
    SAFE: raises to caller (caller must catch).
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "You extract structured data and return valid JSON only."},
            {"role": "user", "content": prompt},
        ],
    )

    content = response.choices[0].message.content or ""
    return _clean_json(content)

