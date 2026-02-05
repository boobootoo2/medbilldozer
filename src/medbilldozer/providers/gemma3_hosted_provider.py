"""Gemma-3-27B-IT hosted model analysis provider.

Provides Gemma-3-27B-IT (large instruction-tuned LLM) hosted on Hugging Face
for medical billing analysis.
"""

import os
import json
import requests
from typing import Optional, Dict
from medbilldozer.providers.llm_interface import LLMProvider, AnalysisResult, Issue

# Gemma-3-27B-IT configuration
GEMMA3_MODEL_ID = os.getenv("GEMMA3_MODEL_ID", "google/gemma-3-27b-it")
GEMMA3_ENDPOINT = os.getenv(
    "GEMMA3_ENDPOINT",
    "https://q83u1j36gd1bymob.us-east-1.aws.endpoints.huggingface.cloud/v1/chat/completions"
)


SYSTEM_PROMPT = """
You are a medical billing analysis system.

You MUST return valid JSON only.
Do not include prose, explanations, or markdown outside JSON.

Be conservative and factual.
Only estimate savings when the document itself clearly supports it.
Never guess insurance outcomes.
Never exceed patient responsibility amounts shown on the document.
"""

TASK_PROMPT = """
Analyze the following medical billing documents.

Identify administrative or billing issues.

For each issue, determine whether a MAX POTENTIAL PATIENT SAVINGS
can be calculated directly from the document.

Rules for estimating max_savings:

1. Duplicate charges
   - Same CPT code
   - Same date of service
   - Identical billed/allowed/patient responsibility
   → max_savings = patient responsibility for ONE duplicate line item

2. Math or reconciliation errors
   → max_savings = difference implied by the document

3. Preventive vs diagnostic or coding issues
   → Do NOT estimate savings unless the patient responsibility amount
     could clearly be eliminated

4. If savings cannot be confidently estimated
   → max_savings = null

Return STRICT JSON using this schema:

{
  "issues": [
    {
      "type": string,
      "summary": string,
      "evidence": string,
      "max_savings": number | null
    }
  ]
}

Document:
"""


import re
import json


def _extract_json(text: str) -> dict:
    """
    Extract the first valid JSON object from model output.
    Handles leading whitespace, prose, or accidental formatting.
    """
    if not text:
        raise ValueError("Empty model output")

    # Trim obvious whitespace
    cleaned = text.strip()

    # Fast path: already valid JSON
    if cleaned.startswith("{"):
        return json.loads(cleaned)

    # Fallback: extract first {...} block
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        raise ValueError(f"No JSON object found in model output:\n{text}")

    return json.loads(match.group(0))


class Gemma3HostedProvider(LLMProvider):
    """Provider for Gemma-3-27B-IT hosted on Hugging Face Inference Endpoint."""
    
    def __init__(self):
        self.token = os.getenv("HF_API_TOKEN")
        self.endpoint = GEMMA3_ENDPOINT

    def name(self) -> str:
        return "gemma3-27b-hosted"

    def health_check(self) -> bool:
        return bool(self.token) and bool(self.endpoint)

    def analyze_document(
        self,
        raw_text: str,
        facts: Optional[Dict] = None
    ) -> AnalysisResult:
        if not self.token:
            raise RuntimeError("HF_API_TOKEN not set")
        
        if not self.endpoint:
            raise RuntimeError("GEMMA3_ENDPOINT not configured")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        # Use the raw_text as-is (may already contain patient context from orchestrator)
        prompt = f"{SYSTEM_PROMPT}\n{TASK_PROMPT}\n{raw_text}"

        # OpenAI-compatible chat completions format
        payload = {
            "model": GEMMA3_MODEL_ID,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 600,
        }

        response = requests.post(
            self.endpoint,
            headers=headers,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()

        data = response.json()

        try:
            content = data["choices"][0]["message"]["content"]
            parsed = _extract_json(content)
        except Exception as e:
            raise RuntimeError(
                f"Failed to parse model JSON output: {e}\nRaw output:\n{content if 'content' in locals() else data}"
            )

        issues = []
        for item in parsed.get("issues", []):
            issues.append(
                Issue(
                    type=item.get("type", "model_signal"),
                    summary=item.get("summary", ""),
                    evidence=item.get("evidence"),
                    max_savings=item.get("max_savings"),
                    recommended_action="Review this item against your bill or EOB.",
                )
            )

        total_max = sum(i.max_savings or 0 for i in issues)

        return AnalysisResult(
            issues=issues,
            meta={
                "provider": self.name(),
                "model": GEMMA3_MODEL_ID,
                "hosted": True,
                "endpoint": self.endpoint,
                "total_max_savings": round(total_max, 2),
            },
        )
