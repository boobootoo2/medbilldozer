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
    "duplicate cpt": "duplicate_charge",
    "duplicate billing": "duplicate_charge",
    "duplicate entry": "duplicate_charge",
    "same date": "duplicate_charge",
    "gender mismatch": "gender_mismatch",
    "gender_mismatch": "gender_mismatch",
    # phrases commonly observed in summaries that imply gender mismatch
    "male billed for": "gender_mismatch",
    "female billed for": "gender_mismatch",
    "billed for prostate": "gender_mismatch",
    "billed for pap": "gender_mismatch",
    "pap smear": "gender_mismatch",
    "hysterectomy": "gender_mismatch",
    "vasectomy": "gender_mismatch",
    "mammogram": "gender_mismatch",
    "age inappropriate": "age_inappropriate_service",
    "age_inappropriate": "age_inappropriate_service",
    "pediatric": "age_inappropriate_service",
    "child": "age_inappropriate_service",
    "neonate": "age_inappropriate_service",
    "screening colonoscopy": "age_inappropriate_service",
    "anatomical contradiction": "anatomical_contradiction",
    "anatomical_contradiction": "anatomical_contradiction",
    "procedure inconsistent with health history": "procedure_inconsistent_with_health_history",
    "procedure_inconsistent": "procedure_inconsistent_with_health_history",
    "procedure inconsistent": "procedure_inconsistent_with_health_history",
    "procedure inconsistency": "procedure_inconsistent_with_health_history",
    "inconsistent procedure": "procedure_inconsistent_with_health_history",
    "diagnosis procedure mismatch": "diagnosis_procedure_mismatch",
    "diagnosis_procedure_mismatch": "diagnosis_procedure_mismatch",
    "diagnosis mismatch": "diagnosis_procedure_mismatch",
    "no diagnosis": "diagnosis_procedure_mismatch",
    "drug disease contraindication": "drug_disease_contraindication",
    "drug_drug_interaction": "drug_drug_interaction",
    "drug interaction": "drug_drug_interaction",
    "drug-drug": "drug_drug_interaction",
    "drug drug": "drug_drug_interaction",
    "maoi": "drug_drug_interaction",
    "ssri": "drug_drug_interaction",
    "upcoding": "upcoding",
    "overbilling": "overbilling",
    "temporal violation": "temporal_violation",
    "repeated": "temporal_violation",
    "repeat": "temporal_violation",
    "billed twice": "temporal_violation",
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
                    continue  # nosec B112 - intentional skip of malformed mapping entries

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

        # --- Deterministic heuristics (post-processing) ---
        # These are low-risk, high-value rules to catch common misses.
        def _extract_cpt_entries(text: str):
            # Return list of {cpt, date, snippet}
            import re
            entries = []
            # find all CPT occurrences
            for m in re.finditer(r"CPT\s*[:\s]?([0-9]{3,5})", text, re.IGNORECASE):
                cpt = m.group(1)
                span_start = max(0, m.start() - 120)
                span_end = min(len(text), m.end() + 120)
                snippet = text[span_start:span_end].replace('\n', ' ')
                # try to find a nearby date (look backwards)
                date_match = re.search(r"Date of Service:?\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", text[:m.start()], re.IGNORECASE)
                date = date_match.group(1) if date_match else None
                # try to find a nearby monetary amount within the surrounding window
                amount = None
                amount_match = re.search(r"\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*USD", text[span_start:span_end], re.IGNORECASE)
                if amount_match:
                    amount = amount_match.group(0).strip()
                else:
                    # also accept simple patterns like 123.45 or 123
                    amount_match = re.search(r"\$?\d{1,6}(?:\.\d{2})?", text[span_start:span_end])
                    if amount_match:
                        amount = amount_match.group(0).strip()
                entries.append({"cpt": cpt, "date": date, "snippet": snippet, "pos": m.start(), "amount": amount})
            return entries

        def _heuristic_gender_mismatch(text: str, existing_codes: set):
            # Look for sex indicator
            import re
            sex_match = re.search(r"Sex: ?([MF]|Male|Female|male|female)", text)
            sex = None
            if sex_match:
                s = sex_match.group(1).lower()
                if s.startswith('m'):
                    sex = 'M'
                elif s.startswith('f'):
                    sex = 'F'

            if not sex:
                return []

            male_keywords = ["prostate", "vasectomy", "psa", "prostatectomy"]
            female_keywords = ["pap", "pap smear", "hysterectomy", "mammogram", "cervical", "ovary", "uterus", "oophorectomy", "cesarean", "obstetric", "pregnancy"]

            issues_out = []
            entries = _extract_cpt_entries(text)
            # Require corroborating evidence: keyword must be within a tight window (±40 chars) of the CPT occurrence
            window = 40
            for e in entries:
                snip = e.get("snippet", "")
                cpt = e.get("cpt")
                pos = e.get("pos")
                if not cpt or cpt in existing_codes:
                    continue
                # windowed text around the CPT occurrence (tighter than the snippet)
                start = max(0, pos - window)
                end = min(len(text), pos + window)
                nearby = text[start:end].lower()
                matched = False
                if sex == 'F':
                    for kw in male_keywords:
                        if kw in nearby:
                            matched = True
                            matched_kw = kw
                            break
                else:
                    for kw in female_keywords:
                        if kw in nearby:
                            matched = True
                            matched_kw = kw
                            break

                if matched:
                    # only raise when both CPT and nearby sex-specific keyword are present
                    issues_out.append(Issue(
                        type="gender_mismatch",
                        summary=f"Possible gender mismatch: found '{matched_kw}' near CPT {cpt}",
                        evidence=snip,
                        code=cpt,
                        source="deterministic",
                        confidence=0.85,
                        max_savings=None
                    ))
            return issues_out

        def _heuristic_duplicate_charge(text: str, existing_codes: set):
            import re
            # split by document markers if present
            docs = re.split(r"---+\s*DOCUMENT\s*\d+\s*---", text, flags=re.IGNORECASE)
            # For each doc, collect CPT entries (use _extract_cpt_entries to also capture amount/date)
            doc_entries = []
            for d in docs:
                entries = _extract_cpt_entries(d)
                # find date for this doc as fallback
                date_match = re.search(r"Date of Service:?\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", d, re.IGNORECASE)
                doc_date = date_match.group(1) if date_match else None
                doc_entries.append({"date": doc_date, "entries": entries, "snippet": d[:200].replace('\n', ' ')})

            issues_out = []
            seen = {}
            # Build seen map keyed by (cpt, date, amount)
            for idx, doc in enumerate(doc_entries):
                for e in doc["entries"]:
                    c = e.get("cpt")
                    date = e.get("date") or doc.get("date")
                    amount = e.get("amount")
                    # normalize amount to string or None
                    key = (c, date, amount)
                    seen.setdefault(key, []).append((idx, e.get("snippet")))

            # Only flag duplicates when we have corroborating date AND amount matches across occurrences
            for (cpt, date, amount), items in seen.items():
                if len(items) > 1 and (not cpt or cpt not in existing_codes):
                    if date and amount:
                        snippet = items[0][1]
                        issues_out.append(Issue(
                            type="duplicate_charge",
                            summary=f"Duplicate CPT {cpt} on {date} with identical amount {amount}",
                            evidence=f"Appears in {len(items)} documents with same date and amount. Example context: {snippet}",
                            code=cpt,
                            date=date,
                            source="deterministic",
                            confidence=0.9,
                            max_savings=None
                        ))
            return issues_out

        def _heuristic_drug_interactions(text: str, existing_codes: set):
            # Simple pair checks
            txt = text.lower()
            issues_out = []
            pairs = [
                (['phenelzine', 'maoi'], ['sertraline', 'ssri', 'fluoxetine']),
                (['warfarin', 'coumadin'], ['ibuprofen', 'naproxen', 'aspirin', 'nsaid']),
                (['digoxin'], ['furosemide', 'loop diuretic', 'bumetanide'])
            ]
            for a_list, b_list in pairs:
                a_found = next((a for a in a_list if a in txt), None)
                b_found = next((b for b in b_list if b in txt), None)
                if a_found and b_found:
                    issues_out.append(Issue(
                        type="drug_drug_interaction",
                        summary=f"Possible drug-drug interaction: {a_found} + {b_found}",
                        evidence=f"Both '{a_found}' and '{b_found}' found in documents.",
                        source="deterministic",
                        confidence=0.85,
                        max_savings=None
                    ))
            return issues_out

        # Build set of existing CPT codes to avoid duplicates
        existing_codes = {iss.code for iss in issues if iss.code}

        # Run heuristics and append any new detected deterministic issues
        try:
            heur_issues = []
            heur_issues.extend(_heuristic_gender_mismatch(raw_text, existing_codes))
            heur_issues.extend(_heuristic_duplicate_charge(raw_text, existing_codes))
            heur_issues.extend(_heuristic_drug_interactions(raw_text, existing_codes))

            # Avoid adding duplicates by (type, code, summary)
            seen_sig = {(i.type, i.code, i.summary) for i in issues}
            for hi in heur_issues:
                sig = (hi.type, getattr(hi, 'code', None), hi.summary)
                if sig not in seen_sig:
                    issues.append(hi)
                    seen_sig.add(sig)
        except Exception:
            # heuristics must not break pipeline
            pass  # nosec B110 - heuristics must not break pipeline

        meta = dict(result.meta or {})
        meta.update({"provider": self.name(), "canonicalized": True})

        return AnalysisResult(issues=issues, meta=meta)
