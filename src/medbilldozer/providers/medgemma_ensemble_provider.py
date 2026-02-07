"""Non-destructive MedGemma + optional OpenAI canonicalizer ensemble provider.

This wrapper keeps the original `MedGemmaHostedProvider` untouched and post-processes
its outputs to map free-form labels to canonical issue types. It can optionally
use an OpenAI-based canonicalizer in the future, but currently applies a
deterministic mapping to improve interoperability with the benchmark runner.
"""

import os
import json
from typing import Optional, Dict, List

from openai import OpenAI

from medbilldozer.providers.llm_interface import LLMProvider, AnalysisResult, Issue
from medbilldozer.providers.medgemma_hosted_provider import MedGemmaHostedProvider


SIMPLE_LABEL_MAP: Dict[str, str] = {
    # common observed free-form -> canonical
    "duplicate charge": "duplicate_charge",
    "duplicate_charge": "duplicate_charge",
    "duplicate": "duplicate_charge",
    "duplicate line": "duplicate_charge",
    "gender mismatch": "gender_mismatch",
    "gender_mismatch": "gender_mismatch",
    "age inappropriate": "age_inappropriate_service",
    "age_inappropriate": "age_inappropriate_service",
    "anatomical contradiction": "anatomical_contradiction",
    "anatomical_contradiction": "anatomical_contradiction",
    "procedure inconsistent with health history": "procedure_inconsistent_with_health_history",
    "procedure_inconsistent": "procedure_inconsistent_with_health_history",
    "diagnosis procedure mismatch": "diagnosis_procedure_mismatch",
    "diagnosis_procedure_mismatch": "diagnosis_procedure_mismatch",
    "drug disease contraindication": "drug_disease_contraindication",
    "drug_drug_interaction": "drug_drug_interaction",
    "drug interaction": "drug_drug_interaction",
    "upcoding": "upcoding",
    "overbilling": "overbilling",
    "temporal violation": "temporal_violation",
}


class MedGemmaEnsembleProvider(LLMProvider):
    """Wrapper provider that calls MedGemma then canonicalizes labels."""

    def __init__(self):
        self.medgemma = MedGemmaHostedProvider()
        # Optional OpenAI canonicalizer toggle (reserved for future use)
        self.enable_openai = os.getenv("ENABLE_ENSEMBLE_OPENAI", "false").lower() in ("1", "true", "yes")

    def name(self) -> str:
        return "medgemma-ensemble"

    def health_check(self) -> bool:
        return self.medgemma.health_check()

    def _canonicalize_type(self, raw_type: Optional[str], summary: Optional[str]) -> str:
        """Try to map free-form type/summary into a canonical issue type."""
        if not raw_type and not summary:
            return "other"

        candidates: List[str] = []
        if raw_type:
            candidates.append(raw_type.lower())
        if summary:
            candidates.append(summary.lower())

        for c in candidates:
            # direct exact mapping
            if c in SIMPLE_LABEL_MAP:
                return SIMPLE_LABEL_MAP[c]

            # substring matching
            for key, val in SIMPLE_LABEL_MAP.items():
                if key in c:
                    return val

        # fallback heuristic: normalize underscores/spaces
        t = (raw_type or summary or "other").lower().strip()
        t = t.replace(" ", "_").replace("-", "_")
        return t

    def _call_openai_canonicalizer(self, items: List[Dict[str, str]]) -> List[Dict[str, object]]:
        """Call OpenAI to canonicalize a list of {raw_type, summary} items.

        Returns a list of {original_type, mapped_type, confidence} objects in the same order.
        """
        # Prepare client and model
        client = OpenAI()
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        # Build canonical key list for prompt
        canonical_keys = sorted(set(SIMPLE_LABEL_MAP.values()))

        # Few-shot examples (small, representative)
        examples = [
            ("Duplicate Charge", "Duplicate charge for CPT 99213 on same date", "duplicate_charge"),
            ("Gender mismatch", "Male patient billed for Pap smear (CPT 88150)", "gender_mismatch"),
            ("Age inappropriate", "8-year-old billed for screening colonoscopy", "age_inappropriate_service"),
            ("Procedure inconsistent", "Procedure without supporting diagnosis in history", "procedure_inconsistent_with_health_history"),
            ("Drug interaction", "ACE inhibitor + potassium supplement", "drug_drug_interaction"),
        ]

        prompt_lines = []
        prompt_lines.append("You are a label canonicalizer. Map free-form issue labels or short summaries to canonical issue keys.")
        prompt_lines.append("Return a JSON array where each element is: {\"original_type\":..., \"mapped_type\":..., \"confidence\":0.0-1.0 } in the same order as the input.")
        prompt_lines.append("Canonical keys available: " + ", ".join(canonical_keys))
        prompt_lines.append("Examples:")
        for orig, summ, mapped in examples:
            prompt_lines.append(json.dumps({"original_type": orig, "summary": summ, "mapped_type": mapped}))

        prompt_lines.append("INPUT:")
        prompt_lines.append(json.dumps(items))

        system = "You must return valid JSON only. No explanation."
        user = "\n".join(prompt_lines)

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.0,
            )

            text = response.choices[0].message.content or "[]"
            # Extract JSON (robust)
            parsed = json.loads(text)
            if not isinstance(parsed, list):
                return []
            return parsed
        except Exception:
            # On any failure, return empty so caller falls back to deterministic map
            return []

    def analyze_document(self, raw_text: str, facts: Optional[Dict] = None) -> AnalysisResult:
        # Run MedGemma first
        result = self.medgemma.analyze_document(raw_text, facts)

        issues = []
        # First pass: deterministic mapping
        canonical_values = set(SIMPLE_LABEL_MAP.values())
        intermediate = []
        ambiguous = []
        for idx, item in enumerate(result.issues):
            canonical = self._canonicalize_type(item.type, item.summary)
            intermediate.append({
                "idx": idx,
                "item": item,
                "canonical": canonical,
            })
            # Mark ambiguous if canonical isn't a known canonical value OR original type not clearly mapped
            if canonical not in canonical_values:
                ambiguous.append({"original_type": item.type or "", "summary": item.summary or "", "idx": idx})

        # Optionally call OpenAI canonicalizer for ambiguous items
        if self.enable_openai and ambiguous:
            mapped = self._call_openai_canonicalizer(ambiguous)
            # Build mapping by idx
            for m in mapped:
                try:
                    idx = m.get("idx")
                    mapped_type = m.get("mapped_type") or m.get("mappedType") or m.get("mapped")
                    confidence = float(m.get("confidence", 0))
                except Exception:
                    continue

                # Apply mapping only if confidence above threshold
                threshold = float(os.getenv("ENABLE_ENSEMBLE_CONFIDENCE", "0.7"))
                if confidence >= threshold and idx is not None and 0 <= idx < len(intermediate):
                    intermediate[idx]["canonical"] = mapped_type

        # Build final Issue objects
        for entry in intermediate:
            item = entry["item"]
            canonical = entry["canonical"]
            issues.append(Issue(
                type=canonical,
                summary=item.summary,
                evidence=item.evidence,
                code=getattr(item, 'code', None) if hasattr(item, 'code') else None,
                max_savings=getattr(item, 'max_savings', None),
                recommended_action=getattr(item, 'recommended_action', None)
            ))

        meta = dict(result.meta or {})
        meta.update({"provider": self.name(), "canonicalized": True})

        return AnalysisResult(issues=issues, meta=meta)
