from .interface import FactExtractor
from .schema import FACT_SCHEMA

class LangExtractExtractor(FactExtractor):
    def __init__(self, extractor):
        self.extractor = extractor

    def extract(self, text: str):
        result = self.extractor.extract(text)
        return {k: result.get(k) for k in FACT_SCHEMA}
