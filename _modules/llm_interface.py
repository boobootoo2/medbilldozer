# _modules/llm_interface.py

"""
Model-agnostic LLM interface for medBillDozer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import re

# ==================================================
# Domain models (canonical)
# ==================================================

@dataclass
class Issue:
    type: str
    summary: str
    evidence: Optional[str] = None
    code: Optional[str] = None
    date: Optional[str] = None
    recommended_action: Optional[str] = None
    max_savings: Optional[float] = None


@dataclass
class AnalysisResult:
    issues: List[Issue]
    meta: Dict[str, Any]


# ==================================================
# Provider interface
# ==================================================

class LLMProvider(ABC):
    """
    All analysis providers MUST implement the same interface.

    Contract:
        analyze_document(raw_text: str, facts: Optional[Dict]) -> AnalysisResult
    """

    @abstractmethod
    def name(self) -> str:
        """Return a short provider name."""

    @abstractmethod
    def analyze_document(
        self,
        raw_text: str,
        facts: Optional[Dict] = None
    ) -> AnalysisResult:
        """Analyze a document and return structured issues."""

    def health_check(self) -> bool:
        return True


# ==================================================
# Provider registry
# ==================================================

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


# ==================================================
# Local heuristic provider
# ==================================================

class LocalHeuristicProvider(LLMProvider):
    def name(self) -> str:
        return "local-heuristic"

    def analyze_document(
        self,
        raw_text: str,
        facts: Optional[Dict] = None
    ) -> AnalysisResult:
        t = raw_text.lower()
        issues: List[Issue] = []

        # --- Duplicate CPT heuristic ---
        line_items = re.findall(
            r"(?P<date>\d{2}/\d{2}/\d{4}).*?(?P<cpt>\b\d{4,5}\b).*?\$(?P<patient>\d+\.\d{2})",
            raw_text
        )

        seen: Dict[tuple, int] = {}
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
                    max_savings=amt
                ))

        meta = {
            "provider": self.name(),
            "issue_count": len(issues),
            "total_max_savings": round(
                sum(i.max_savings or 0 for i in issues),
                2
            ),
        }

        return AnalysisResult(issues=issues, meta=meta)


# ==================================================
# Default registrations
# ==================================================

ProviderRegistry.register("local", LocalHeuristicProvider())

__all__ = [
    "LLMProvider",
    "ProviderRegistry",
    "LocalHeuristicProvider",
    "Issue",
    "AnalysisResult",
]
