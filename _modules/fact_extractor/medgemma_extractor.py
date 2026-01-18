from .interface import FactExtractor
from .schema import FACT_SCHEMA
from .heuristics import extract_dates, extract_procedure_code
from .llm_medgemma import extract_with_medgemma

class MedGemmaExtractor(FactExtractor):
    def __init__(self, provider):
        self.provider = provider

    def extract(self, text: str):
        facts = FACT_SCHEMA.copy()

        # Rules-first extraction
        facts.update(extract_dates(text))
        facts["procedure_code"] = extract_procedure_code(text)

        llm_facts = extract_with_medgemma(text, self.provider)

        for key, value in llm_facts.items():
            if facts[key] is None and value is not None:
                facts[key] = value

        return facts
