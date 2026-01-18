from .interface import FactExtractor
from .schema import FACT_SCHEMA
from .heuristics import extract_dates, extract_procedure_code

class HeuristicExtractor(FactExtractor):
    def extract(self, text: str):
        facts = FACT_SCHEMA.copy()
        facts.update(extract_dates(text))
        facts["procedure_code"] = extract_procedure_code(text)
        return facts
