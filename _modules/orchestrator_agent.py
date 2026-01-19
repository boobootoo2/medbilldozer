# _modules/orchestrator_agent.py

from typing import Dict, Optional

from _modules.openai_langextractor import extract_facts_openai
from _modules.local_heuristic_extractor import extract_facts_local
from _modules.fact_normalizer import normalize_facts
from _modules.llm_interface import ProviderRegistry


class OrchestratorAgent:
    def __init__(
        self,
        extractor_override: Optional[str] = None,
        analyzer_override: Optional[str] = None,
    ):
        self.extractor_override = extractor_override
        self.analyzer_override = analyzer_override

    def _choose_extractor(self, text: str) -> str:
        if self.extractor_override:
            return self.extractor_override

        # 🔹 simple heuristic for now
        if "Receipt" in text or "Store #" in text:
            return "heuristic"

        return "openai"

    def _choose_analyzer(self, text: str) -> str:
        if self.analyzer_override:
            return self.analyzer_override

        # 🔹 default
        return "openai"

    def run(self, raw_text: str) -> Dict:
        extractor = self._choose_extractor(raw_text)
        analyzer_key = self._choose_analyzer(raw_text)

        # ---- Extract facts ----
        if extractor == "heuristic":
            facts = extract_facts_local(raw_text)
        else:
            facts = extract_facts_openai(raw_text)

        facts = normalize_facts(facts)

        # ---- Analyze ----
        provider = ProviderRegistry.get(analyzer_key)
        if not provider:
            raise RuntimeError(f"No analysis provider: {analyzer_key}")

        analysis = provider.analyze_document(raw_text)

        return {
            "facts": facts,
            "analysis": analysis,
            "_orchestration": {
                "extractor": extractor,
                "analyzer": analyzer_key,
            },
        }
