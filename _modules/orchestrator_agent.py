# _modules/orchestrator_agent.py

from typing import Dict, Optional
from datetime import datetime
import uuid
import re

from _modules.openai_langextractor import (
    extract_facts_openai,
    run_prompt_openai,
)
from _modules.gemini_langextractor import (
    extract_facts_gemini,
    run_prompt_gemini,
)

from _modules.local_heuristic_extractor import extract_facts_local
from _modules.fact_normalizer import normalize_facts
from _modules.llm_interface import ProviderRegistry
from _modules.llm_interface import Issue
from _modules.receipt_line_item_prompt import build_receipt_line_item_prompt
from _modules.medical_line_item_prompt import build_medical_line_item_prompt
from _modules.dental_line_item_prompt import build_dental_line_item_prompt
from _modules.insurance_claim_item_prompt import build_insurance_claim_item_prompt
from _modules.fsa_claim_item_prompt import build_fsa_claim_item_prompt

import json


def _clean_llm_json(text: str) -> str:
    """
    Cleans LLM output so it can be parsed as JSON.
    Safe for OpenAI and Gemini.
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

def _run_phase2_prompt(prompt: str, extractor: str) -> Optional[str]:
    if extractor == "gemini":
        return run_prompt_gemini(prompt)
    if extractor == "openai":
        return run_prompt_openai(prompt)
    return None


def normalize_issues(issues: list[Issue]) -> list[Issue]:
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
    "medical_bill": "openai",
    "insurance_eob": "openai",
    "pharmacy_receipt": "gemini",   # 👈 change
    "dental_bill": "openai",
    "generic": "openai",
}


def classify_document(text: str) -> Dict:
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
    """Lightweight heuristic facts (cheap, deterministic)."""
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
    ):
        self.extractor_override = extractor_override
        self.analyzer_override = analyzer_override

    def run(self, raw_text: str) -> Dict:
        # --------------------------------------------------
        # Workflow log (persistable artifact)
        # --------------------------------------------------
        workflow_log = {
            "workflow_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "pre_extraction": {},
            "extraction": {},
            "analysis": {},
        }

        # --------------------------------------------------
        # 1️⃣ Pre-extraction classification
        # --------------------------------------------------
        classification = classify_document(raw_text)
        pre_facts = extract_pre_facts(raw_text)

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
        
        if extractor == "heuristic":
            facts = extract_facts_local(raw_text)
            
        elif extractor == "gemini":
            facts = extract_facts_gemini(raw_text)

        else:  # openai default
            facts = extract_facts_openai(raw_text)

        facts = normalize_facts(facts)

        workflow_log["extraction"]["extractor"] = extractor
        workflow_log["extraction"]["facts"] = facts
        workflow_log["extraction"]["fact_count"] = len(facts or {})
        
        # --------------------------------------------------
        # 3️⃣b Phase-2 receipt line-item extraction (OPTIONAL)
        # --------------------------------------------------
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
        if document_type == "insurance_eob":
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
        analyzer_key = self.analyzer_override or "openai"
        provider = ProviderRegistry.get(analyzer_key)

        if not provider:
            raise RuntimeError(f"No analysis provider: {analyzer_key}")

        workflow_log["analysis"]["analyzer"] = analyzer_key

        # --------------------------------------------------
        # 5️⃣ Analyze (fact-aware if supported)
        # call provider (fact-aware if possible)
        try:
            analysis = provider.analyze_document(raw_text, facts=facts)
            workflow_log["analysis"]["mode"] = "facts+text"
        except TypeError:
            analysis = provider.analyze_document(raw_text)
            workflow_log["analysis"]["mode"] = "text_only"

        # normalize + enforce invariants
        analysis.issues = normalize_issues(analysis.issues)

        if not hasattr(analysis, "meta") or analysis.meta is None:
            analysis.meta = {}

        analysis.meta["total_max_savings"] = round(
            sum(i.max_savings or 0 for i in analysis.issues),
            2
        )



        workflow_log["analysis"]["result"] = analysis

        # --------------------------------------------------
        # Return full result
        # --------------------------------------------------
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
