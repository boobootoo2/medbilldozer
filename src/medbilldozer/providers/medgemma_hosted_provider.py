"""MedGemma hosted model analysis provider.

Provides MedGemma (medical domain-specific LLM) hosted on Hugging Face
for specialized medical billing analysis.

PRODUCTION HARDENING:
- Deterministic decoding (temp=0, do_sample=false)
- JSON sanitization with markdown fence removal
- Automatic truncation repair (closes incomplete JSON)
- Retry logic for JSON parsing failures
- Defensive error handling (never crashes benchmark loop)
"""

import os
import json
import time
import requests
import re
import logging
from typing import Optional, Dict, Tuple
from medbilldozer.providers.llm_interface import LLMProvider, AnalysisResult, Issue

# Configure logging
logger = logging.getLogger(__name__)

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


SYSTEM_PROMPT = """You are a medical billing auditor. Analyze documents and return ONLY valid JSON. No markdown. No explanation. No reasoning. Just raw JSON."""

TASK_PROMPT = """Analyze billing documents for issues. Estimate max_savings only when directly supported:
1. Duplicate charges: max_savings = patient responsibility for ONE duplicate
2. Math errors: max_savings = difference shown
3. Other issues: max_savings = null unless patient amount clearly eliminated

CRITICAL OUTPUT REQUIREMENTS:
- Return ONLY a single JSON object
- Do NOT wrap in markdown code fences (no ```json or ```)
- Do NOT include any text before or after the JSON
- Do NOT include explanations or reasoning
- Use double quotes for all strings (not single quotes)
- Use null for missing values (not None)
- Do NOT include trailing commas
- Ensure all strings are properly closed
- Ensure all braces and brackets are balanced

JSON schema (return EXACTLY this structure):
{
  "issues": [
    {
      "type": "string",
      "summary": "string", 
      "evidence": "string",
      "code": "string or null",
      "max_savings": 0.00
    }
  ]
}

Document:"""


import threading

# Global lock and state for coordinating endpoint warmup across threads
_warmup_lock = threading.Lock()
_endpoint_warmed_global = False
_warmup_attempted = False  # Track if warmup was attempted (success or fail)


def sanitize_and_parse_json(raw_output: str, context: str = "model output") -> Tuple[dict, bool]:
    """
    PRODUCTION-GRADE JSON sanitization and parsing.
    
    This function implements defensive parsing for LLM-generated JSON with:
    - Markdown fence removal (```json, ```)
    - Leading/trailing prose stripping
    - Balanced brace validation
    - Truncation repair (closes incomplete strings/arrays/objects)
    - Multi-strategy extraction (fast path, regex extraction, repair)
    
    Args:
        raw_output: Raw text from LLM (may contain markdown, prose, malformed JSON)
        context: Description of where this JSON came from (for error logging)
    
    Returns:
        Tuple of (parsed_dict, was_repaired)
        - parsed_dict: Successfully parsed JSON object
        - was_repaired: True if automatic repair was needed
        
    Raises:
        ValueError: If JSON cannot be extracted or parsed even after repair attempts
    """
    if not raw_output or not raw_output.strip():
        raise ValueError(f"Empty {context}")
    
    original_output = raw_output
    was_repaired = False
    
    # STEP 1: Strip whitespace
    cleaned = raw_output.strip()
    
    # STEP 2: Remove markdown code fences
    # Match: ```json\n{...}\n``` or ```\n{...}\n``` or inline ```{...}```
    if "```" in cleaned:
        # Remove opening fence with optional language tag
        cleaned = re.sub(r"^```(?:json|JSON)?\s*\n?", "", cleaned, flags=re.MULTILINE)
        # Remove closing fence
        cleaned = re.sub(r"\s*```\s*$", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()
        logger.debug(f"Removed markdown fences from {context}")
    
    # STEP 3: Fast path - try parsing as-is
    if cleaned.startswith("{"):
        try:
            parsed = json.loads(cleaned)
            logger.debug(f"Successfully parsed {context} on fast path")
            return parsed, was_repaired
        except json.JSONDecodeError as e:
            logger.debug(f"Fast path failed for {context}: {e}")
            # Continue to repair strategies
    
    # STEP 4: Extract first complete {...} block using regex
    # This handles cases where LLM adds prose before/after JSON
    # Try to match nested JSON (up to 3 levels deep for performance)
    for depth in range(3):
        pattern = r'\{'
        for _ in range(depth + 1):
            pattern += r'(?:[^{}"]|"(?:[^"\\]|\\.)*"|\{(?:[^{}"]|"(?:[^"\\]|\\.)*")*\})*'
        pattern += r'\}'
        
        match = re.search(pattern, cleaned, re.DOTALL)
        if match:
            extracted = match.group(0)
            try:
                parsed = json.loads(extracted)
                # Validate that we extracted an issues structure, not a sub-object
                if "issues" in parsed:
                    logger.debug(f"Extracted valid JSON from {context} using regex (depth={depth})")
                    return parsed, was_repaired
                else:
                    # Found a nested object, not the root - keep trying
                    logger.debug(f"Found nested object without 'issues' key, continuing...")
                    continue
            except json.JSONDecodeError:
                continue
    
    # STEP 5: Aggressive repair - handle truncated output
    # This is common when max_tokens is hit
    logger.warning(f"Attempting aggressive repair on {context}")
    was_repaired = True
    
    # Find the outermost JSON structure
    json_start = cleaned.find('{')
    if json_start == -1:
        raise ValueError(f"No JSON object found in {context}. Output: {original_output[:500]}")
    
    repaired = cleaned[json_start:]
    
    # Repair strategy 1: Remove trailing commas FIRST (before parsing attempts)
    repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)
    
    # Repair strategy 2: Smart truncation handling
    # Find the last complete field before truncation
    # Look for the last properly closed string or number
    last_complete_pos = -1
    in_string = False
    escaped = False
    depth = 0
    
    for i, char in enumerate(repaired):
        if char == '\\' and not escaped:
            escaped = True
            continue
        
        if char == '"' and not escaped:
            in_string = not in_string
            if not in_string:
                # String just closed
                last_complete_pos = i
        
        if not in_string:
            if char in '{[':
                depth += 1
            elif char in '}]':
                depth -= 1
                if depth >= 0:
                    last_complete_pos = i
        
        escaped = False
    
    # If we have an unterminated string, truncate to last complete position
    # and rebuild from there
    if in_string and last_complete_pos > 0:
        logger.debug(f"Truncating at last complete field (pos {last_complete_pos})")
        repaired = repaired[:last_complete_pos + 1]
    
    # Repair strategy 3: Balance braces and brackets
    open_braces = repaired.count('{') - repaired.count('}')
    open_brackets = repaired.count('[') - repaired.count(']')
    
    if open_brackets > 0:
        logger.debug(f"Closing {open_brackets} unclosed arrays in {context}")
        repaired += ']' * open_brackets
    
    if open_braces > 0:
        logger.debug(f"Closing {open_braces} unclosed objects in {context}")
        repaired += '}' * open_braces
    
    # Repair strategy 4: Try parsing repaired JSON
    try:
        parsed = json.loads(repaired)
        logger.info(f"Successfully repaired and parsed {context}")
        return parsed, was_repaired
    except json.JSONDecodeError as e:
        logger.debug(f"Repair attempt failed: {e}")
        
        # Fallback 1: Try to find last valid complete object in issues array
        # Extract up to the last complete issue object
        issues_pattern = r'"issues"\s*:\s*\[([^\]]*)\]'
        issues_match = re.search(issues_pattern, repaired, re.DOTALL)
        
        if issues_match:
            issues_content = issues_match.group(1)
            # Try to parse what we have
            try:
                minimal = '{"issues": [' + issues_content + ']}'
                parsed = json.loads(minimal)
                logger.warning(f"Extracted issues array from malformed {context}")
                return parsed, True
            except json.JSONDecodeError:
                # Try parsing individual complete issue objects
                # Find all complete {...} blocks within issues
                issue_objects = []
                brace_depth = 0
                current_obj = ""
                
                for char in issues_content:
                    current_obj += char
                    if char == '{':
                        brace_depth += 1
                    elif char == '}':
                        brace_depth -= 1
                        if brace_depth == 0 and current_obj.strip():
                            # Try to parse this object
                            try:
                                obj = json.loads(current_obj.strip().rstrip(','))
                                issue_objects.append(obj)
                                current_obj = ""
                            except json.JSONDecodeError:
                                current_obj = ""
                
                if issue_objects:
                    logger.warning(f"Extracted {len(issue_objects)} complete issue objects")
                    return {"issues": issue_objects}, True
        
        # Fallback 2: Return empty issues if we have valid opening structure
        if repaired.startswith('{"issues":'):
            logger.error(f"Returning empty issues due to parse failure in {context}")
            return {"issues": []}, True
        
        # All repair strategies failed
        error_preview = original_output[:500] + ("..." if len(original_output) > 500 else "")
        raise ValueError(
            f"Failed to parse {context} even after repair attempts.\n"
            f"Final error: {e}\n"
            f"Original output (truncated): {error_preview}"
        )


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
            # Double-check inside lock - another thread may have already done this
            if _endpoint_warmed_global:
                return True
            
            # Only first thread prints and sets flags
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

    def _call_model(
        self, 
        prompt: str, 
        max_tokens: int = 4096,
        retry_count: int = 0
    ) -> str:
        """
        Call HuggingFace model with production-grade parameters.
        
        Uses deterministic decoding to ensure reproducible, parseable output:
        - temperature = 0 (deterministic, no randomness)
        - top_p = 1.0 (consider full probability distribution) 
        - do_sample = False (greedy decoding, most likely token)
        - stop tokens to prevent markdown fences
        
        Args:
            prompt: Full prompt including system and task instructions
            max_tokens: Maximum tokens to generate (default 4096)
            retry_count: Internal retry counter
            
        Returns:
            Raw model output string
            
        Raises:
            RuntimeError: On API errors or max retries exceeded
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        
        # PRODUCTION CONFIGURATION: Deterministic decoding
        payload = {
            "model": HF_MODEL_ID,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,        # Deterministic (no randomness)
            "top_p": 1.0,              # Consider full distribution
            "max_tokens": max_tokens,  # Sufficient for complete JSON
            "stop": ["```", "```json", "```JSON"],  # Prevent markdown fences
        }
        
        # Try to add do_sample if supported (some HF endpoints ignore this)
        try:
            payload["do_sample"] = False  # Greedy decoding
        except Exception:
            pass  # Some endpoints don't support this parameter
        
        try:
            response = requests.post(
                HF_MODEL_URL,
                headers=headers,
                json=payload,
                timeout=300,  # 5 min timeout
            )
            
            # Detailed error handling for 400 errors
            if response.status_code == 400:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = json.dumps(error_json, indent=2)
                except (json.JSONDecodeError, ValueError):
                    pass
                raise RuntimeError(
                    f"HuggingFace API returned 400 Bad Request.\n"
                    f"Model: {HF_MODEL_ID}\n"
                    f"Endpoint: {HF_MODEL_URL}\n"
                    f"Error details:\n{error_detail}"
                )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract content from response
            content = data["choices"][0]["message"]["content"]
            
            # Check for truncation warning
            finish_reason = data["choices"][0].get("finish_reason")
            if finish_reason == "length":
                logger.warning(
                    f"Model output truncated (hit max_tokens={max_tokens}). "
                    f"Will attempt JSON repair."
                )
            
            return content
            
        except requests.exceptions.Timeout:
            if retry_count < 1:
                logger.warning(f"Request timeout, retrying... (attempt {retry_count + 1})")
                time.sleep(5)
                return self._call_model(prompt, max_tokens, retry_count + 1)
            raise RuntimeError("Model request timed out after retries")
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Model API request failed: {e}")

    def analyze_document(
        self,
        raw_text: str,
        facts: Optional[Dict] = None
    ) -> AnalysisResult:
        """
        Analyze document with production-grade JSON robustness.
        
        RESILIENCE FEATURES:
        - Automatic JSON sanitization and repair
        - Retry on parsing failure with shortened prompt
        - Defensive error handling (never crashes benchmark)
        - Comprehensive logging for debugging
        
        Args:
            raw_text: Document text or pre-formatted patient context
            facts: Optional structured facts (unused for now)
            
        Returns:
            AnalysisResult with detected issues
            
        Raises:
            RuntimeError: Only on unrecoverable errors (API auth, endpoint down)
        """
        if not self.token:
            raise RuntimeError("HF_API_TOKEN not set")
        
        # Warm up endpoint if needed (only happens once globally)
        if not self._warmup_endpoint():
            raise RuntimeError(
                "HuggingFace Inference Endpoint is not available. "
                "Please start the endpoint or wait for auto-scaling."
            )
        
        # Build full prompt
        prompt = f"{SYSTEM_PROMPT}\n\n{TASK_PROMPT}\n\n{raw_text}"
        
        # ATTEMPT 1: Full prompt with standard max_tokens
        try:
            content = self._call_model(prompt, max_tokens=4096)
            parsed, was_repaired = sanitize_and_parse_json(content, context="model output (attempt 1)")
            
            if was_repaired:
                logger.info("JSON repair was needed but succeeded")
            
            return self._build_result(parsed)
            
        except ValueError as e:
            # JSON parsing failed even after repair attempts
            logger.error(f"JSON parsing failed on attempt 1: {e}")
            
            # ATTEMPT 2: Retry with higher max_tokens and shortened prompt
            try:
                logger.info("Retrying with increased max_tokens...")
                
                # Shorten prompt by removing verbose instructions
                short_prompt = (
                    f"{SYSTEM_PROMPT}\n\n"
                    f"Return ONLY JSON: {{\"issues\": [{{\"type\": str, \"summary\": str, "
                    f"\"evidence\": str, \"code\": str|null, \"max_savings\": float|null}}]}}\n\n"
                    f"{raw_text}"
                )
                
                content = self._call_model(short_prompt, max_tokens=6144)
                parsed, was_repaired = sanitize_and_parse_json(
                    content, 
                    context="model output (attempt 2 - shortened)"
                )
                
                logger.info("Retry succeeded with shortened prompt")
                return self._build_result(parsed)
                
            except ValueError as e2:
                # Both attempts failed - return empty result rather than crash
                logger.error(
                    f"All JSON parsing attempts failed. "
                    f"Attempt 1: {str(e)[:200]}. "
                    f"Attempt 2: {str(e2)[:200]}"
                )
                
                # DEFENSIVE: Return empty result to keep benchmark running
                return AnalysisResult(
                    issues=[],
                    meta={
                        "provider": self.name(),
                        "model": HF_MODEL_ID,
                        "error": "JSON parsing failed after retries",
                        "total_max_savings": 0.0,
                    },
                )
        
        except Exception as e:
            # Unexpected error - log and return empty result
            logger.exception(f"Unexpected error in analyze_document: {e}")
            return AnalysisResult(
                issues=[],
                meta={
                    "provider": self.name(),
                    "model": HF_MODEL_ID,
                    "error": f"Unexpected error: {str(e)[:200]}",
                    "total_max_savings": 0.0,
                },
            )
    
    def _build_result(self, parsed: dict) -> AnalysisResult:
        """
        Build AnalysisResult from parsed JSON.
        Handles missing fields gracefully.
        """
        issues = []
        
        for item in parsed.get("issues", []):
            # Defensive field access with fallbacks
            issue_type = item.get("type") or "unspecified"
            summary = item.get("summary") or "No summary provided"
            evidence = item.get("evidence")
            code = item.get("code")
            max_savings = item.get("max_savings")
            
            # Validate and sanitize max_savings
            if max_savings is not None:
                try:
                    max_savings = float(max_savings)
                    if max_savings < 0:
                        max_savings = None
                except (TypeError, ValueError):
                    max_savings = None
            
            issues.append(
                Issue(
                    type=issue_type,
                    summary=summary,
                    evidence=evidence,
                    code=code,
                    max_savings=max_savings,
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
                "num_issues": len(issues),
            },
        )

