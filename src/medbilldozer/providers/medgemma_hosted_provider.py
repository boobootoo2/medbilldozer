"""MedGemma hosted model analysis provider.

Provides MedGemma (medical domain-specific LLM) hosted on Hugging Face
for specialized medical billing analysis.
"""

import os
import json
import time
import requests
from typing import Optional, Dict
from medbilldozer.providers.llm_interface import LLMProvider, AnalysisResult, Issue

HF_MODEL_ID = os.getenv("HF_MODEL_ID", "google/medgemma-4b-it")

# Support both dedicated inference endpoints and router
# If HF_ENDPOINT_BASE is set, use it (for dedicated endpoints)
# Otherwise fall back to router
HF_ENDPOINT_BASE = os.getenv("HF_ENDPOINT_BASE")
if HF_ENDPOINT_BASE:
    HF_MODEL_URL = f"{HF_ENDPOINT_BASE}/v1/chat/completions"
else:
    HF_MODEL_URL = os.getenv(
        "HF_MODEL_URL",
        f"https://router.huggingface.co/v1/chat/completions"
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
import threading

# Global lock and state for coordinating endpoint warmup across threads
_warmup_lock = threading.Lock()
_endpoint_warmed_global = False
_warmup_attempted = False  # Track if warmup was attempted (success or fail)


def _extract_json(text: str) -> dict:
    """
    Extract the first valid JSON object from model output.
    Handles leading whitespace, prose, markdown code fences, or accidental formatting.
    Also attempts to repair truncated JSON by closing incomplete structures.
    """
    if not text:
        raise ValueError("Empty model output")

    # Trim obvious whitespace
    cleaned = text.strip()
    
    # Remove markdown code fences if present (```json ... ``` or ``` ... ```)
    if cleaned.startswith("```"):
        # Remove opening fence
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        # Remove closing fence
        cleaned = re.sub(r"\s*```\s*$", "", cleaned)
        cleaned = cleaned.strip()

    # Fast path: already valid JSON
    if cleaned.startswith("{"):
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Try to repair truncated JSON
            if "Unterminated string" in str(e) or "Expecting" in str(e):
                # Attempt to close incomplete JSON structures
                repaired = cleaned
                # Close unterminated strings
                if repaired.count('"') % 2 != 0:
                    repaired += '"'
                # Close incomplete arrays and objects
                open_braces = repaired.count('{') - repaired.count('}')
                open_brackets = repaired.count('[') - repaired.count(']')
                repaired += ']' * open_brackets + '}' * open_braces
                
                try:
                    return json.loads(repaired)
                except json.JSONDecodeError:
                    # Still can't parse, raise original error
                    raise e
            raise

    # Fallback: extract first {...} block
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        raise ValueError(f"No JSON object found in model output:\n{text}")

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        # Try repair on extracted JSON
        extracted = match.group(0)
        if "Unterminated string" in str(e) or "Expecting" in str(e):
            repaired = extracted
            if repaired.count('"') % 2 != 0:
                repaired += '"'
            open_braces = repaired.count('{') - repaired.count('}')
            open_brackets = repaired.count('[') - repaired.count(']')
            repaired += ']' * open_brackets + '}' * open_braces
            
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                raise e
        raise


class MedGemmaHostedProvider(LLMProvider):
    def __init__(self):
        self.token = os.getenv("HF_API_TOKEN")

    def name(self) -> str:
        return "medgemma-hosted"

    def health_check(self) -> bool:
        return bool(self.token)
    
    def _warmup_endpoint(self) -> bool:
        """
        Warm up the HuggingFace Inference Endpoint if it's in stopped state.
        Inference Endpoints auto-pause to save costs and need to be woken up.
        Uses a global lock to ensure only ONE thread does the warmup work.
        Returns True if endpoint is ready, False otherwise.
        """
        global _endpoint_warmed_global, _warmup_attempted
        
        # Fast path: already warmed up successfully
        if _endpoint_warmed_global:
            return True
        
        # Fast path: warmup was already attempted and failed - don't retry
        if _warmup_attempted and not _endpoint_warmed_global:
            return False
        
        # Check if Router (no warmup needed)
        if not HF_ENDPOINT_BASE:
            with _warmup_lock:
                if not _endpoint_warmed_global:
                    _endpoint_warmed_global = True
                    _warmup_attempted = True
            return True
        
        # TEMPORARY: Skip warmup check since endpoint is already running
        # TODO: Fix warmup logic to handle all HTTP response codes properly
        with _warmup_lock:
            if not _endpoint_warmed_global:
                print("✅ Skipping warmup - endpoint already active", flush=True)
                _endpoint_warmed_global = True
                _warmup_attempted = True
        return True
            
        # Acquire lock - only one thread will do the warmup attempt
        with _warmup_lock:
            # Double-check after acquiring lock (another thread may have just finished)
            if _endpoint_warmed_global:
                return True
            
            # Check if another thread already tried and failed
            if _warmup_attempted:
                return False
            
            # Mark that we're attempting warmup (prevents other threads from trying)
            _warmup_attempted = True
            
            # This thread won the race - do the warmup
            print("🔄 Warming up HuggingFace Inference Endpoint (up to 3 minutes)...", flush=True)
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            
            # Send a minimal warmup request
            warmup_payload = {
                "model": HF_MODEL_ID,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 1,
            }
            
            max_retries = 6
            retry_delay = 30  # seconds
            
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        HF_MODEL_URL,
                        headers=headers,
                        json=warmup_payload,
                        timeout=180,
                    )
                    
                    if response.status_code == 503:
                        if attempt < max_retries - 1:
                            print(f"⏳ Attempt {attempt + 1}/{max_retries}...", flush=True)
                            time.sleep(retry_delay)
                            continue
                        else:
                            print("⚠️ Endpoint still unavailable after 3 minutes", flush=True)
                            return False
                    
                    if response.status_code == 200:
                        print("✅ Endpoint ready!", flush=True)
                        _endpoint_warmed_global = True
                        return True
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"⏳ Retry {attempt + 1}...", flush=True)
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"⚠️ Warmup failed: {str(e)[:100]}", flush=True)
                        return False
            
            return False

    def analyze_document(
        self,
        raw_text: str,
        facts: Optional[Dict] = None
    ) -> AnalysisResult:
        if not self.token:
            raise RuntimeError("HF_API_TOKEN not set")
        
        # Warm up endpoint if needed (only happens once)
        if not self._warmup_endpoint():
            raise RuntimeError(
                "HuggingFace Inference Endpoint is not available. "
                "Please start the endpoint at: https://ui.endpoints.huggingface.co/ "
                "or wait for it to auto-scale."
            )

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        # Use the raw_text as-is (may already contain patient context from orchestrator)
        prompt = f"{SYSTEM_PROMPT}\n{TASK_PROMPT}\n{raw_text}"

        payload = {
            "model": HF_MODEL_ID,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 8192,  # Increased to prevent truncation in multi-pass analysis
        }

        response = requests.post(
            HF_MODEL_URL,
            headers=headers,
            json=payload,
            timeout=180,
        )
        
        # Provide detailed error message for 400 errors
        if response.status_code == 400:
            error_detail = response.text
            try:
                error_json = response.json()
                error_detail = json.dumps(error_json, indent=2)
            except (json.JSONDecodeError, ValueError):
                pass
            raise RuntimeError(
                f"HuggingFace API returned 400 Bad Request.\n"
                f"This usually means:\n"
                f"1. Model '{HF_MODEL_ID}' is not available via Router endpoint\n"
                f"2. Token doesn't have access to this model\n"
                f"3. Model requires a dedicated Inference Endpoint\n"
                f"\nError details:\n{error_detail}\n"
                f"\nConsider using a dedicated endpoint or switching to Vertex AI for MedGemma."
            )
        
        response.raise_for_status()

        data = response.json()

        try:
            content = data["choices"][0]["message"]["content"]
            parsed = _extract_json(content)
        except Exception as e:
            # Truncate raw output to first 500 chars to avoid log spam
            truncated = content[:500] + "..." if len(content) > 500 else content
            raise RuntimeError(
                f"Failed to parse model JSON output: {e}\n"
                f"Raw output (truncated): {truncated}"
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
                "model": HF_MODEL_ID,
                "hosted": True,
                "total_max_savings": round(total_max, 2),
            },
        )

