import os
import requests
from _modules.llm_interface import LLMProvider, AnalysisResult, Issue

# Allow overriding the hosted inference URL via env var for flexibility.
# Default to the standard inference API endpoint (router endpoints may vary by account).
# Determine the correct hosted URL:
# 1. Use HF_MODEL_URL if explicitly provided.
# 2. If HF_ENDPOINT_BASE is provided (e.g. your deployed endpoint base),
#    construct a model path against it.
# 3. Fall back to the public HF Inference API model path.
HF_MODEL_URL = os.getenv("HF_MODEL_URL")
# Allow overriding which model id to request (useful for router chat)
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "google/medgemma-4b-it")
if not HF_MODEL_URL:
    hf_endpoint_base = os.getenv("HF_ENDPOINT_BASE")
    if hf_endpoint_base:
        HF_MODEL_URL = f"{hf_endpoint_base.rstrip('/')}/v1/models/{HF_MODEL_ID.split('/')[-1]}"
    else:
        HF_MODEL_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}"


class MedGemmaHostedProvider(LLMProvider):
    def __init__(self):
        self.token = os.getenv("HF_API_TOKEN")

    def name(self) -> str:
        return "medgemma-hosted"

    def health_check(self) -> bool:
        return bool(self.token)

    def analyze_document(self, text: str) -> AnalysisResult:
        if not self.token:
            raise RuntimeError("HF_API_TOKEN not set")

        # Prepare possible auth header variants. Some HF deployments expect
        # an Authorization: Bearer <token>, others use an endpoint-specific
        # x-api-key header. Try both if available.
        auth_token = self.token
        api_key = os.getenv("HF_API_KEY")
        header_variants = []
        if auth_token:
            header_variants.append({"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"})
        if api_key:
            header_variants.append({"x-api-key": api_key, "Content-Type": "application/json"})
        # As a last resort try no-auth headers (some internal endpoints handle auth differently)
        header_variants.append({"Content-Type": "application/json"})

        prompt = (
            "You analyze healthcare billing, pharmacy, dental, and insurance documents.\n"
            "Identify possible administrative or billing issues.\n\n"
            f"Document:\n{text}\n\n"
            "Return a concise bullet list of potential issues."
        )

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 180,
                "temperature": 0.2,
                "do_sample": False
            }
        }

        # Try a list of candidate endpoints (in order). This helps handle
        # different deployment URL shapes (user-provided endpoint base, HF router,
        # etc.) and fall back gracefully.
        candidates = []
        # explicit HF_MODEL_URL first
        if os.getenv("HF_MODEL_URL"):
            candidates.append(os.getenv("HF_MODEL_URL"))
        # endpoint base variants
        if os.getenv("HF_ENDPOINT_BASE"):
            base = os.getenv("HF_ENDPOINT_BASE").rstrip("/")
            model_name = HF_MODEL_ID.split("/")[-1]
            candidates.append(f"{base}/v1/models/{model_name}")
            candidates.append(f"{base}/v1/models/{model_name}:predict")
        # router model path (may 404 for chat-only models)
        candidates.append(f"https://router.huggingface.co/models/{HF_MODEL_ID}")
        # router chat completions (works for chat-capable models)
        candidates.append("https://router.huggingface.co/v1/chat/completions")

        last_errs = []
        response = None
        for url in candidates:
            for hdr in header_variants:
                try:
                    # choose payload shape: chat completions vs single-input text generation
                    if url.endswith("/v1/chat/completions"):
                        chat_payload = {
                            "model": HF_MODEL_ID,
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 180,
                            "temperature": 0.2,
                        }
                        response = requests.post(url, headers=hdr, json=chat_payload, timeout=90)
                    else:
                        response = requests.post(url, headers=hdr, json=payload, timeout=90)

                    response.raise_for_status()
                    # success
                    break
                except requests.exceptions.HTTPError as err:
                    text = ""
                    try:
                        text = response.text
                    except Exception:
                        pass
                    last_errs.append((url, hdr, f"HTTPError: {err} - {text[:1000]}"))
                    # try next header variant
                except requests.exceptions.RequestException as err:
                    last_errs.append((url, hdr, f"RequestException: {err}"))
                    # try next header variant

            if response is not None and response.status_code < 400:
                break

        if response is None or response.status_code >= 400:
            # Aggregate errors for troubleshooting
            msgs = "\n".join([f"{u} -> {m}" for u, m in last_errs])
            raise RuntimeError(f"All hosted model endpoints failed. Attempts:\n{msgs}")

        try:
            data = response.json()
        except ValueError:
            # non-json response
            raise RuntimeError(f"Hosted model returned a non-JSON response from {response.url}: {response.text[:1000]}")

        # Normalize generated text from different response shapes
        generated_text = ""
        # Chat completions: {choices: [{message: {content: "..."}}]}
        if isinstance(data, dict) and "choices" in data and data.get("choices"):
            try:
                first = data["choices"][0]
                if isinstance(first.get("message"), dict):
                    generated_text = first["message"].get("content", "")
                elif "text" in first:
                    generated_text = first.get("text", "")
                else:
                    if isinstance(first.get("delta"), dict):
                        generated_text = first["delta"].get("content", "")
            except Exception:
                generated_text = ""
        # Some model endpoints return list with generated_text
        if not generated_text and isinstance(data, list) and data:
            generated_text = data[0].get("generated_text", "")
        if not generated_text and isinstance(data, dict):
            generated_text = data.get("generated_text", "") or data.get("output", "")

        issues = []
        for line in generated_text.splitlines():
            line = line.strip("-• ").strip()
            if line:
                issues.append(
                    Issue(
                        type="model_signal",
                        summary=line,
                        recommended_action="Review this item against your bill, EOB, or claim history."
                    )
                )

        return AnalysisResult(
            issues=issues,
            meta={
                "provider": self.name(),
                "model": HF_MODEL_ID,
                "hosted": True,
            }
        )
