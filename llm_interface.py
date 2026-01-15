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

    from llm_interface import ProviderRegistry, LocalHeuristicProvider

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


@dataclass
class AnalysisResult:
    issues: List[Issue]
    meta: Dict[str, Any]


class LLMProvider(ABC):
    """Abstract provider contract.

    Implementations should be synchronous for simplicity. Networked
    providers may provide async wrappers if desired.
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
    """A simple provider that applies local heuristics to find common issues.

    This is safe to run offline and is the recommended default for a
    consumer-facing app that shouldn't call external LLMs by default.
    """

    def name(self) -> str:
        return "local-heuristic"

    def analyze_document(self, text: str) -> AnalysisResult:
        t = text.lower()
        issues: List[Issue] = []

        # Duplicate CPT/code heuristics
        codes = re.findall(r"\b[0-9]{3,5}\b|\b[a-zA-Z]\d{3,4}\b", text)
        # simple frequency map
        freq: Dict[str, int] = {}
        for c in codes:
            freq[c] = freq.get(c, 0) + 1
        for c, count in freq.items():
            if count > 1:
                issues.append(Issue(
                    type="duplicate_code",
                    summary=f"Procedure code {c} appears {count} times",
                    evidence=f"Found {count} occurrences of code {c}",
                    code=c,
                    recommended_action="Confirm whether multiple entries are separate services or duplicate billing; request corrected statement if duplicate."
                ))

        # FSA-related heuristics: look for polyethylene glycol or 'copay' and check claim history mentions
        if "polyethylene glycol" in t or "polyethylene-glycol" in t:
            if "claim history" in t and "polyethylene glycol" not in t.split("claim history", 1)[1].lower():
                issues.append(Issue(
                    type="missing_fsa_copay",
                    summary="FSA-eligible prescription appears on receipt but not in claim history",
                    evidence="Polyethylene Glycol appears in receipt text while claim history section lacks it",
                    recommended_action="Submit the missing claim to your FSA administrator with receipt attached."
                ))

        # General mixed FSA eligibility
        if "vitamin" in t and "fsa" in t:
            issues.append(Issue(
                type="mixed_fsa_eligibility",
                summary="Receipt contains both FSA-eligible and non-eligible items",
                evidence="Found 'vitamin' together with FSA references",
                recommended_action="Separate eligible items when submitting; keep receipts."
            ))

        # Insurance conflict heuristic
        if "out-of-pocket" in t and "$0.00" in t and "patient responsibility" in t:
            issues.append(Issue(
                type="inconsistent_insurance",
                summary="Insurer shows $0 out-of-pocket but bill shows patient responsibility",
                evidence="Found both 'out-of-pocket: $0.00' and a patient balance in the document",
                recommended_action="Compare EOBs to the bill and request corrected statement from provider/insurer."
            ))

        meta = {"provider": self.name(), "found_codes": list(freq.keys())}
        return AnalysisResult(issues=issues, meta=meta)


# Register the local provider by default
ProviderRegistry.register("local", LocalHeuristicProvider())


__all__ = ["LLMProvider", "ProviderRegistry", "LocalHeuristicProvider", "Issue", "AnalysisResult"]
