# _modules/orchestrator_agent.py
"""Main workflow orchestration for healthcare document analysis.

Coordinates document classification, fact extraction, line item parsing,
and issue analysis through a multi-phase pipeline. Provides deterministic
issue detection and LLM-based analysis integration.
"""

from typing import Dict, Optional
from datetime import datetime, timezone
import uuid
import re

from _modules.extractors.openai_langextractor import (
    extract_facts_openai,
    run_prompt_openai,
)
from _modules.extractors.gemini_langextractor import (
    extract_facts_gemini,
    run_prompt_gemini,
)
from _modules.ui.billdozer_widget import (
    install_billdozer_bridge,
    dispatch_widget_message,
)

from _modules.providers.llm_interface import ProviderRegistry, Issue
from _modules.extractors.local_heuristic_extractor import extract_facts_local
from _modules.extractors.fact_normalizer import normalize_facts
from _modules.providers.llm_interface import ProviderRegistry
from _modules.prompts.receipt_line_item_prompt import build_receipt_line_item_prompt
from _modules.prompts.medical_line_item_prompt import build_medical_line_item_prompt
from _modules.prompts.dental_line_item_prompt import build_dental_line_item_prompt
from _modules.prompts.insurance_claim_item_prompt import build_insurance_claim_item_prompt
from _modules.prompts.fsa_claim_item_prompt import build_fsa_claim_item_prompt
import json


def _clean_llm_json(text: str) -> str:
    """Clean LLM output for JSON parsing.

    Removes markdown fences, leading commentary, and other artifacts
    that prevent JSON parsing.

    Args:
        text: Raw LLM output string

    Returns:
        Cleaned string ready for JSON parsing
    """
    if not text:
        return text

    text = text.strip()

    # Remove ```json fences
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```$", "", text)

    # Strip leading commentary before JSON
    first_brace = text.find("{")
    if first_brace != -1:
        text = text[first_brace:]

    return text.strip()


def model_backend(model: str) -> Optional[str]:
    """Determine backend provider from model name.

    Args:
        model: Model identifier string (e.g., 'gpt-4', 'gemini-1.5-flash')

    Returns:
        Backend name ('openai', 'gemini') or None if unknown
    """
    if model.startswith("gpt-"):
        return "openai"
    if model.startswith("gemini-"):
        return "gemini"
    return None


def _run_phase2_prompt(prompt: str, model: str) -> Optional[str]:
    """Execute phase 2 line item parsing prompt using appropriate backend.

    Args:
        prompt: Formatted prompt string for line item extraction
        model: Model identifier to use for execution

    Returns:
        LLM response text or None if backend not supported
    """
    backend = model_backend(model)

    if backend == "openai":
        return run_prompt_openai(prompt)

    if backend == "gemini":
        return run_prompt_gemini(prompt)

    return None


def deterministic_issues_from_facts(facts: dict) -> list[Issue]:
    issues = []

    # --- Duplicate medical CPTs ---
    seen = set()
    for item in facts.get("medical_line_items", []):
        key = (item.get("date_of_service"), item.get("cpt_code"))
        if key in seen:
            issues.append(Issue(
                type="duplicate_charge",
                summary="Duplicate medical procedure billed",
                evidence=(
                    f"CPT {item.get('cpt_code')} appears more than once on "
                    f"{item.get('date_of_service')} with patient responsibility "
                    f"${item.get('patient_responsibility')}"
                ),
                max_savings=item.get("patient_responsibility"),
                confidence=1.0,
                source="deterministic",
            ))
        else:
            seen.add(key)

    # --- Duplicate dental CDT codes ---
    seen = set()
    for item in facts.get("dental_line_items", []):
        key = (item.get("date_of_service"), item.get("cdt_code"))
        if key in seen:
            issues.append(Issue(
                type="duplicate_charge",
                summary="Duplicate dental procedure billed",
                evidence=(
                    f"CDT {item.get('cdt_code')} billed multiple times on "
                    f"{item.get('date_of_service')}"
                ),
                max_savings=item.get("patient_responsibility"),
                confidence=1.0,
                source="deterministic",
            ))
        else:
            seen.add(key)

    return issues


def deterministic_issues_from_facts(facts: dict) -> list[Issue]:
    issues = []

    # --- Duplicate medical CPTs ---
    seen = set()
    for item in facts.get("medical_line_items", []):
        key = (item.get("date_of_service"), item.get("cpt_code"))
        if key in seen:
            issues.append(Issue(
                type="duplicate_charge",
                summary="Duplicate medical procedure billed",
                evidence=(
                    f"CPT {item.get('cpt_code')} appears more than once on "
                    f"{item.get('date_of_service')}"
                ),
                code=item.get("cpt_code"),
                date=item.get("date_of_service"),
                max_savings=item.get("patient_responsibility"),
                recommended_action="Contact the provider or insurer to verify duplicate billing.",
                source="deterministic",
                confidence=1.0,
            ))
        else:
            seen.add(key)

    # --- Duplicate dental CDT codes ---
    seen = set()
    for item in facts.get("dental_line_items", []):
        key = (item.get("date_of_service"), item.get("cdt_code"))
        if key in seen:
            issues.append(Issue(
                type="duplicate_charge",
                summary="Duplicate dental procedure billed",
                evidence=(
                    f"CDT {item.get('cdt_code')} billed multiple times on "
                    f"{item.get('date_of_service')}"
                ),
                code=item.get("cdt_code"),
                date=item.get("date_of_service"),
                max_savings=item.get("patient_responsibility"),
                recommended_action="Ask the dental office whether this procedure was billed twice.",
                source="deterministic",
                confidence=1.0,
            ))
        else:
            seen.add(key)

    return issues


def compute_deterministic_savings(facts: dict) -> float:
    """Calculate total savings from deterministic issues.

    Sums max_savings from all deterministic issues identified in facts.

    Args:
        facts: Facts dictionary containing line items and extracted data

    Returns:
        Total potential savings amount in dollars
    """
    savings = 0.0

    # --- Duplicate medical CPTs ---
    items = facts.get("medical_line_items", [])
    seen = set()
    for item in items:
        key = (item.get("date_of_service"), item.get("cpt_code"))
        if key in seen:
            savings += item.get("patient_responsibility", 0) or 0
        else:
            seen.add(key)

    # --- Duplicate dental procedures ---
    items = facts.get("dental_line_items", [])
    seen = set()
    for item in items:
        key = (item.get("date_of_service"), item.get("cdt_code"))
        if key in seen:
            savings += item.get("patient_responsibility", 0) or 0
        else:
            seen.add(key)

    # --- Non-covered / denied FSA items ---
    for item in facts.get("fsa_claim_items", []):
        if item.get("amount_reimbursed", 0) == 0:
            savings += item.get("amount_submitted", 0) or 0

    return round(savings, 2)


def normalize_issues(issues: list) -> list:
    for issue in issues:
        # Ensure attribute exists
        if not hasattr(issue, "max_savings"):
            issue.max_savings = None

        # Normalize numeric values
        if issue.max_savings is not None:
            try:
                issue.max_savings = round(float(issue.max_savings), 2)
            except Exception:
                issue.max_savings = None

    return issues

# --------------------------------------------------
# Regex-based document classification
# --------------------------------------------------
DOCUMENT_SIGNALS = {
    "medical_bill": [
        r"\bCPT\b",
        r"\bICD-10\b",
        r"Date of Service",
        r"Patient Responsibility",
        r"Allowed Amount",
    ],
    "insurance_eob": [
        r"Explanation of Benefits",
        r"\bEOB\b",
        r"Insurance Paid",
        r"Claim Number",
    ],
    "pharmacy_receipt": [
        r"\bRx\b",
        r"NDC",
        r"Pharmacy",
        r"Copay",
    ],
    "dental_bill": [
        r"\bD\d{4}\b",
        r"Dental",
        r"Crown",
        r"Lab Fee",
    ],
}


DOCUMENT_EXTRACTOR_MAP = {
    "medical_bill": "gpt-4o-mini",
    "insurance_eob": "gpt-4o-mini",
    "pharmacy_receipt": "gemini-1.5-flash",
    "dental_bill": "gpt-4o-mini",
    "generic": "gpt-4o-mini",
}


def classify_document(text: str) -> Dict:
    """Classify document type using regex pattern matching.

    Scores document against known patterns for medical bills, dental bills,
    pharmacy receipts, insurance claims, and FSA claims.

    Args:
        text: Raw document text

    Returns:
        Dict with document_type, confidence score, and pattern match scores
    """
    scores = {}

    for doc_type, patterns in DOCUMENT_SIGNALS.items():
        matches = sum(
            1 for p in patterns if re.search(p, text, re.IGNORECASE)
        )
        if matches:
            scores[doc_type] = matches

    if not scores:
        return {
            "document_type": "generic",
            "confidence": 0.0,
            "scores": {},
        }

    best = max(scores, key=scores.get)
    confidence = scores[best] / sum(scores.values())

    return {
        "document_type": best,
        "confidence": round(confidence, 2),
        "scores": scores,
    }


def extract_pre_facts(text: str) -> Dict:
    """Extract lightweight heuristic facts before full extraction.

    Provides fast, cheap feature detection (CPT codes, dental codes, Rx markers)
    for downstream routing and optimization.

    Args:
        text: Raw document text

    Returns:
        Dict with boolean flags and document statistics
    """
    return {
        "contains_cpt": bool(re.search(r"\bCPT\b", text)),
        "contains_dental_code": bool(re.search(r"\bD\d{4}\b", text)),
        "contains_rx": bool(re.search(r"\bRx\b", text)),
        "line_count": len(text.splitlines()),
        "char_count": len(text),
    }


# --------------------------------------------------
# Orchestrator Agent
# --------------------------------------------------


class OrchestratorAgent:
    def __init__(
        self,
        extractor_override: Optional[str] = None,
        analyzer_override: Optional[str] = None,
        profile_context: Optional[str] = None,
    ):
        self.extractor_override = extractor_override
        self.analyzer_override = analyzer_override
        self.profile_context = profile_context

    def run(self, raw_text: str, progress_callback=None) -> Dict:
        """Run document analysis pipeline with optional progress callbacks.

        Args:
            raw_text: Raw document text to analyze
            progress_callback: Optional callable(workflow_log, step_status) for progress updates
                step_status values: 'pre_extraction_active', 'extraction_active', 'line_items_active', 'analysis_active', 'complete'

        Returns:
            Dict with facts, analysis, and _workflow_log
        """
        # --------------------------------------------------
        # Workflow log (persistable artifact)
        # --------------------------------------------------
        workflow_log = {
            "workflow_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pre_extraction": {},
            "extraction": {},
            "analysis": {},
        }

        # --------------------------------------------------
        # 1️⃣ Pre-extraction classification
        # --------------------------------------------------
        if progress_callback:
            progress_callback(workflow_log, "pre_extraction_active")

        classification = classify_document(raw_text)
        pre_facts = extract_pre_facts(raw_text)

        document_type = (
            classification.get("document_type")
            if isinstance(classification, dict)
            else getattr(classification, "document_type", None)
        )

        if document_type:
            readable = document_type.replace("_", " ")
            dispatch_widget_message(
                "billy",
                f"We are processing {readable}"
            )


        workflow_log["pre_extraction"]["classification"] = classification
        workflow_log["pre_extraction"]["facts"] = pre_facts

        # --------------------------------------------------
        # 2️⃣ Choose extractor
        # --------------------------------------------------
        if self.extractor_override:
            extractor = self.extractor_override
            extractor_reason = "debug override"
        else:
            extractor = DOCUMENT_EXTRACTOR_MAP.get(
                classification["document_type"],
                "openai",
            )
            extractor_reason = "regex classification"

        workflow_log["pre_extraction"]["extractor_selected"] = extractor
        workflow_log["pre_extraction"]["extractor_reason"] = extractor_reason

        # --------------------------------------------------
        # 3️⃣ Extract facts
        # --------------------------------------------------
        if progress_callback:
            progress_callback(workflow_log, "extraction_active")

        # Prepend profile context to raw text if available
        text_with_context = raw_text
        if self.profile_context:
            text_with_context = f"{self.profile_context}\n\n{'='*50}\nDOCUMENT TO ANALYZE:\n{'='*50}\n\n{raw_text}"

        if extractor == "heuristic":
            facts = extract_facts_local(text_with_context)

        elif extractor == "gemini":
            facts = extract_facts_gemini(text_with_context)

        else:  # openai default
            facts = extract_facts_openai(text_with_context)

        facts = normalize_facts(facts)

        workflow_log["extraction"]["extractor"] = extractor
        workflow_log["extraction"]["facts"] = facts
        workflow_log["extraction"]["fact_count"] = len(facts or {})

        # --------------------------------------------------
        # 3️⃣b Phase-2 receipt line-item extraction (OPTIONAL)
        # --------------------------------------------------
        if progress_callback:
            progress_callback(workflow_log, "line_items_active")

        document_type = facts.get("document_type")

        if document_type == "pharmacy_receipt":
            try:
                prompt = build_receipt_line_item_prompt(raw_text)

                raw_response = _run_phase2_prompt(prompt, extractor)

                if raw_response:
                    cleaned = _clean_llm_json(raw_response)
                    parsed = json.loads(cleaned)
                    receipt_items = parsed.get("receipt_items", [])

                    if isinstance(receipt_items, list) and receipt_items:
                        facts["receipt_items"] = receipt_items
                        workflow_log["extraction"]["receipt_item_count"] = len(receipt_items)
                    else:
                        workflow_log["extraction"]["receipt_item_count"] = 0

            except Exception as e:
                workflow_log["extraction"]["receipt_extraction_error"] = str(e)
                print("[receipt extraction error]", e)

        # --------------------------------------------------
        # 3️⃣c Phase-2 medical line-item extraction (OPTIONAL)
        # --------------------------------------------------
        if document_type == "medical_bill":
            try:
                prompt = build_medical_line_item_prompt(raw_text)

                raw_response = _run_phase2_prompt(prompt, extractor)


                if raw_response:
                    cleaned = _clean_llm_json(raw_response)
                    parsed = json.loads(cleaned)
                    items = parsed.get("medical_line_items", [])

                    if isinstance(items, list) and items:
                        facts["medical_line_items"] = items
                        workflow_log["extraction"]["medical_item_count"] = len(items)
                    else:
                        workflow_log["extraction"]["medical_item_count"] = 0

            except Exception as e:
                workflow_log["extraction"]["medical_extraction_error"] = str(e)
                print("[medical extraction error]", e)

        # --------------------------------------------------
        # 3️⃣d Phase-2 dental line-item extraction (OPTIONAL)
        # --------------------------------------------------
        if document_type == "dental_bill":
            try:
                prompt = build_dental_line_item_prompt(raw_text)

                raw_response = _run_phase2_prompt(prompt, extractor)


                if raw_response:
                    cleaned = _clean_llm_json(raw_response)
                    parsed = json.loads(cleaned)
                    items = parsed.get("dental_line_items", [])

                    if isinstance(items, list) and items:
                        facts["dental_line_items"] = items
                        workflow_log["extraction"]["dental_item_count"] = len(items)
                    else:
                        workflow_log["extraction"]["dental_item_count"] = 0

            except Exception as e:
                workflow_log["extraction"]["dental_extraction_error"] = str(e)
                print("[dental extraction error]", e)

        # --------------------------------------------------
        # 3️⃣e Phase-2 insurance claim row extraction (OPTIONAL)
        # --------------------------------------------------
        if document_type in ("insurance_eob", "insurance_claim_history", "insurance_document"):
            try:
                prompt = build_insurance_claim_item_prompt(raw_text)

                raw_response = _run_phase2_prompt(prompt, extractor)


                if raw_response:
                    cleaned = _clean_llm_json(raw_response)
                    parsed = json.loads(cleaned)
                    items = parsed.get("insurance_claim_items", [])

                    if isinstance(items, list) and items:
                        facts["insurance_claim_items"] = items
                        workflow_log["extraction"]["insurance_item_count"] = len(items)
                    else:
                        workflow_log["extraction"]["insurance_item_count"] = 0

            except Exception as e:
                workflow_log["extraction"]["insurance_extraction_error"] = str(e)
                print("[insurance extraction error]", e)

        # --------------------------------------------------
        # 3️⃣f Phase-2 FSA claim row extraction (OPTIONAL)
        # --------------------------------------------------
        if document_type == "fsa_claim_history":
            try:
                prompt = build_fsa_claim_item_prompt(raw_text)

                raw_response = _run_phase2_prompt(prompt, extractor)


                if raw_response:
                    cleaned = _clean_llm_json(raw_response)
                    parsed = json.loads(cleaned)
                    items = parsed.get("fsa_claim_items", [])

                    if isinstance(items, list) and items:
                        facts["fsa_claim_items"] = items
                        workflow_log["extraction"]["fsa_item_count"] = len(items)
                    else:
                        workflow_log["extraction"]["fsa_item_count"] = 0

            except Exception as e:
                workflow_log["extraction"]["fsa_extraction_error"] = str(e)
                print("[fsa extraction error]", e)


        # --------------------------------------------------
        # 4️⃣ Choose analyzer
        # --------------------------------------------------
        analyzer_key = self.analyzer_override
        if not analyzer_key:
            raise RuntimeError("Analyzer model must be specified (e.g. gpt-4o-mini)")

        provider = ProviderRegistry.get(analyzer_key)

        if not provider:
            fallback = "gpt-4o-mini"
            provider = ProviderRegistry.get(fallback)

            if not provider:
                raise RuntimeError(
                    f"No analysis provider: {analyzer_key} (and fallback missing)"
                )

            workflow_log["analysis"]["fallback_used"] = {
                "requested": analyzer_key,
                "used": fallback,
            }

            analyzer_key = fallback


        workflow_log["analysis"]["analyzer"] = analyzer_key

        # --------------------------------------------------
        # 5️⃣ Analyze (fact-aware if supported)
        # call provider (fact-aware if possible)
        if progress_callback:
            progress_callback(workflow_log, "analysis_active")

        try:
            analysis = provider.analyze_document(raw_text, facts=facts)
            # --- Add deterministic issues as first-class issues ---
            deterministic_issues = deterministic_issues_from_facts(facts)

            analysis.issues = (analysis.issues or []) + deterministic_issues

            workflow_log["analysis"]["mode"] = "facts+text"
        except TypeError:
            analysis = provider.analyze_document(raw_text)
            workflow_log["analysis"]["mode"] = "text_only"

        # normalize + enforce invariants
        analysis.issues = normalize_issues(analysis.issues)

        deterministic = compute_deterministic_savings(facts)

        analysis.meta["deterministic_savings"] = deterministic
        analysis.meta["llm_max_savings"] = round(
            sum(i.max_savings or 0 for i in analysis.issues if getattr(i, "source", None) != "deterministic"),
            2
        )

        analysis.meta["total_max_savings"] = round(
            sum(i.max_savings or 0 for i in analysis.issues),
            2
        )


        if not hasattr(analysis, "meta") or analysis.meta is None:
            analysis.meta = {}

        llm_total = round(
            sum(i.max_savings or 0 for i in analysis.issues),
            2
        )

        deterministic = analysis.meta.get("deterministic_savings", 0.0)

        analysis.meta["total_max_savings"] = max(llm_total, deterministic)
        analysis.meta["llm_max_savings"] = llm_total


        workflow_log["analysis"]["result"] = analysis

        # --------------------------------------------------
        # Return full result
        # --------------------------------------------------
        if progress_callback:
            progress_callback(workflow_log, "complete")

        return {
            "facts": facts,
            "analysis": analysis,
            "_orchestration": {
                "classification": classification,
                "extractor": extractor,
                "analyzer": analyzer_key,
            },
            "_workflow_log": workflow_log,
        }

