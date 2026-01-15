"""Model-agnostic LLM interface for medBillDozer.

This module defines a small, dependency-free interface for integrating
different LLM providers (OpenAI, Anthropic, local LLMs, or a simple
local heuristic fallback). The goal is to keep the app code independent
of a concrete model implementation.

Components:
- AnalysisResult / Issue dataclasses: structured output from analysis.
- LLMProvider (abstract base): defines the provider contract.
- ProviderRegistry: small registry to register and retrieve providers.
- LocalHeuristicProvider: a built-in provider that runs simple text
  heuristics (no network calls) and can be used as a safe default.

Usage example:

    from _modules.llm_interface import ProviderRegistry, LocalHeuristicProvider

    ProviderRegistry.register('local', LocalHeuristicProvider())
    provider = ProviderRegistry.get('local')
    result = provider.analyze_document("paste bill text here")
    print(result.issues)

The interface is intentionally small and sync-first. Implementations
for remote providers should implement the same methods and handle their
own networking, retries, and auth.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
import re


@dataclass
class Issue:
    type: str
    summary: str
    evidence: Optional[str] = None
    code: Optional[str] = None
    date: Optional[str] = None
    recommended_action: Optional[str] = None

    # NEW: maximum patient-facing savings if resolved favorably
    max_savings: Optional[float] = None


@dataclass
class AnalysisResult:
    issues: List[Issue]

    # meta now explicitly supports savings aggregation
    meta: Dict[str, Any]


class LLMProvider(ABC):
    """
    Providers should:
    - Identify billing/claim issues
    - Populate Issue.max_savings ONLY when the document itself
      clearly supports a maximum patient-facing savings amount
    - Leave max_savings as None when uncertain
    """

    @abstractmethod
    def name(self) -> str:
        """Return a short provider name."""

    @abstractmethod
    def analyze_document(self, text: str) -> AnalysisResult:
        """Analyze a pasted document and return structured issues.

        The contract is intentionally broad: providers may return any set
        of issues. The app will render them in a friendly UI.
        """

    def health_check(self) -> bool:
        """Optional: return True if provider is ready (e.g., API key present).

        Defaults to True for local/no-op providers.
        """
        return True


class ProviderRegistry:
    _providers: Dict[str, LLMProvider] = {}

    @classmethod
    def register(cls, key: str, provider: LLMProvider) -> None:
        cls._providers[key] = provider

    @classmethod
    def get(cls, key: str) -> Optional[LLMProvider]:
        return cls._providers.get(key)

    @classmethod
    def list(cls) -> List[str]:
        return list(cls._providers.keys())


class LocalHeuristicProvider(LLMProvider):
    def name(self) -> str:
        return "local-heuristic"

    def analyze_document(self, text: str) -> AnalysisResult:
        t = text.lower()
        issues: List[Issue] = []

        # --- Duplicate CPT heuristic ---
        # Capture CPT + dollar amounts in same line
        line_items = re.findall(
            r"(?P<date>\d{2}/\d{2}/\d{4}).*?(?P<cpt>\b\d{4,5}\b).*?\$(?P<patient>\d+\.\d{2})",
            text
        )

        seen = {}
        for date, cpt, patient_amt in line_items:
            key = (date, cpt, patient_amt)
            seen[key] = seen.get(key, 0) + 1

        for (date, cpt, patient_amt), count in seen.items():
            if count > 1:
                amt = float(patient_amt)
                issues.append(Issue(
                    type="duplicate_charge",
                    summary=f"Duplicate billing for CPT {cpt} on {date}",
                    evidence=(
                        f"The same CPT {cpt} appears {count} times on {date}, "
                        f"each with a patient responsibility of ${amt:.2f}."
                    ),
                    code=cpt,
                    date=date,
                    recommended_action=(
                        "Ask the provider to confirm whether one of the duplicate "
                        "charges can be removed."
                    ),
                    max_savings=amt  # ← THIS is the key addition
                ))

        meta = {
            "provider": self.name(),
            "issue_count": len(issues),
            "total_max_savings": round(
                sum(i.max_savings or 0 for i in issues),
                2
            )
        }

        return AnalysisResult(issues=issues, meta=meta)


# Register the local provider by default
ProviderRegistry.register("local", LocalHeuristicProvider())


__all__ = ["LLMProvider", "ProviderRegistry", "LocalHeuristicProvider", "Issue", "AnalysisResult"]
