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

    # 👇 NEW (does not break existing code)
    source: str = "llm"          # "llm" | "deterministic"
    confidence: Optional[float] = None


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
        # Extract date from document (look for "Date of Service:" pattern)
        dos_match = re.search(r"Date of Service:?\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", raw_text)
        dos = dos_match.group(1) if dos_match else "unknown"
        
        # Extract line items with CPT codes and amounts
        # Pattern: CPT XXXX - description $amount.00
        line_items_pattern = r"CPT\s+(\d{4,5})\s*[-–]\s*([^$]+?)\s*\$\s*(\d+\.\d{2})"
        line_items = re.findall(line_items_pattern, raw_text)

        # Track duplicates
        seen: Dict[tuple, list] = {}
        for cpt, desc, amount in line_items:
            key = (cpt.strip(), amount.strip())
            if key not in seen:
                seen[key] = []
            seen[key].append((cpt, desc, amount))

        # Report duplicates
        for (cpt, amount), items in seen.items():
            if len(items) > 1:
                amt = float(amount)
                issues.append(Issue(
                    type="duplicate_charge",
                    summary=f"Duplicate CPT {cpt} on {dos}",
                    evidence=(
                        f"CPT code {cpt} ({items[0][1].strip()}) appears {len(items)} times "
                        f"on {dos}, each at ${amount}. "
                        f"This suggests duplicate billing."
                    ),
                    code=cpt,
                    date=dos,
                    recommended_action=(
                        "Ask the provider to confirm whether one of the duplicate "
                        "charges should be removed."
                    ),
                    max_savings=amt
                ))

        # --- Overbilling heuristic: detect unusually high facility fees ---
        # Look for facility fee patterns (common pattern in medical bills)
        facility_fee_pattern = r"(?:facility|surgical suite|operating room|OR|anesthesia|room)\s*fee.*?\$\s*(\d+\.\d{2})"
        facility_fees = re.findall(facility_fee_pattern, raw_text, re.IGNORECASE)
        
        if facility_fees:
            for fee_str in facility_fees:
                fee_amt = float(fee_str)
                # Flag facility fees over $500 as potentially excessive
                if fee_amt > 500:
                    issues.append(Issue(
                        type="overbilling",
                        summary=f"Facility fee of ${fee_amt:.2f} appears excessive",
                        evidence=(
                            f"Facility or room fee of ${fee_amt:.2f} found. "
                            f"Typical facility fees range from $100-300. This may be worth negotiating."
                        ),
                        recommended_action="Review facility fee with the provider. Request itemization.",
                        max_savings=fee_amt * 0.5  # Estimate 50% potential savings
                    ))

        # --- Overbilling heuristic: detect repeated amounts suggesting duplicates ---
        # Extract all dollar amounts to check for patterns
        all_amounts = re.findall(r"\$\s*(\d+\.\d{2})", raw_text)
        amount_counts: Dict[str, int] = {}
        for amt in all_amounts:
            amount_counts[amt] = amount_counts.get(amt, 0) + 1
        
        # If same amount appears 3+ times in line items, might be overbilling
        for amt_str, count in amount_counts.items():
            if count >= 3:
                amt = float(amt_str)
                # Skip very small amounts (likely copays) and very large amounts
                if 50 < amt < 1000:
                    issues.append(Issue(
                        type="overbilling",
                        summary=f"Charge of ${amt:.2f} appears {count} times",
                        evidence=(
                            f"The charge of ${amt:.2f} appears {count} times in this bill. "
                            f"Verify that these are all necessary distinct charges."
                        ),
                        recommended_action="Request itemized explanation of each charge.",
                        max_savings=amt * (count - 1)  # Conservative: assume 1 is correct
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

