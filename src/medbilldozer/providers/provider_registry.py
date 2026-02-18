"""Provider registration and management for LLM analysis providers."""

from medbilldozer.providers.llm_interface import ProviderRegistry
from medbilldozer.providers.openai_analysis_provider import OpenAIAnalysisProvider
from medbilldozer.providers.gemini_analysis_provider import GeminiAnalysisProvider

try:
    from medbilldozer.providers.medgemma_hosted_provider import MedGemmaHostedProvider
except Exception:
    MedGemmaHostedProvider = None

try:
    from medbilldozer.providers.gemma3_hosted_provider import Gemma3HostedProvider
except Exception:
    Gemma3HostedProvider = None

try:
    from medbilldozer.providers.medgemma_ensemble_provider import MedGemmaEnsembleProvider
except Exception:
    MedGemmaEnsembleProvider = None


# Engine options for user-facing selection
ENGINE_OPTIONS = {
    "Smart (Recommended)": None,
    "gpt-4o-mini": "gpt-4o-mini",
    "gemini-3-flash-preview": "gemini-3-flash-preview",
    "Local (Offline)": "heuristic",
}


def register_providers():
    """Register available LLM analysis providers.

    Attempts to register MedGemma, Gemma-3, Gemini, OpenAI, and ensemble providers.
    Only registers providers that pass health checks.
    """
    # --- MedGemma Ensemble (PRIORITY) ---
    # This is the primary provider used by the React frontend
    try:
        if MedGemmaEnsembleProvider:
            ensemble_provider = MedGemmaEnsembleProvider()
            if ensemble_provider.health_check():
                ProviderRegistry.register("medgemma-ensemble", ensemble_provider)
                print("[medgemma-ensemble] provider registered successfully")
    except Exception as e:
        print(f"[medgemma-ensemble] provider registration failed: {e}")

    # --- MedGemma 4B ---
    try:
        if MedGemmaHostedProvider:
            provider = MedGemmaHostedProvider()
            if provider.health_check():
                ProviderRegistry.register("medgemma-4b-it", provider)
    except Exception as e:
        print(f"[medgemma] provider registration failed: {e}")

    # --- Gemma-3 27B ---
    try:
        if Gemma3HostedProvider:
            gemma3_provider = Gemma3HostedProvider()
            if gemma3_provider.health_check():
                ProviderRegistry.register("gemma3-27b-it", gemma3_provider)
    except Exception as e:
        print(f"[gemma3] provider registration failed: {e}")

    # --- Gemini ---
    try:
        gemini_provider = GeminiAnalysisProvider("gemini-1.5-flash")
        if gemini_provider.health_check():
            ProviderRegistry.register("gemini-1.5-flash", gemini_provider)
    except Exception as e:
        print(f"[gemini] provider registration failed: {e}")

    # --- OpenAI ---
    try:
        openai_provider = OpenAIAnalysisProvider("gpt-4o-mini")
        if openai_provider.health_check():
            ProviderRegistry.register("gpt-4o-mini", openai_provider)
    except Exception as e:
        print(f"[openai] provider registration failed: {e}")
