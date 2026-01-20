# _modules/orchestrator_agent.py

from typing import Dict, Optional
from datetime import datetime
import uuid
import re

from _modules.openai_langextractor import extract_facts_openai
from _modules.gemini_langextractor import extract_facts_gemini
from _modules.local_heuristic_extractor import extract_facts_local
from _modules.fact_normalizer import normalize_facts
from _modules.llm_interface import ProviderRegistry


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
        # 4️⃣ Choose analyzer
        # --------------------------------------------------
        analyzer_key = self.analyzer_override or "openai"
        provider = ProviderRegistry.get(analyzer_key)

        if not provider:
            raise RuntimeError(f"No analysis provider: {analyzer_key}")

        workflow_log["analysis"]["analyzer"] = analyzer_key

        # --------------------------------------------------
        # 5️⃣ Analyze (fact-aware if supported)
        # --------------------------------------------------
        try:
            analysis = provider.analyze_document(raw_text, facts=facts)
            workflow_log["analysis"]["mode"] = "facts+text"
        except TypeError:
            analysis = provider.analyze_document(raw_text)
            workflow_log["analysis"]["mode"] = "text_only"

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
