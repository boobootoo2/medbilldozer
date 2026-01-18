from .heuristic_extractor import HeuristicExtractor
from .medgemma_extractor import MedGemmaExtractor
from .langextract_extractor import LangExtractExtractor

def get_extractor(
    *,
    provider_name: str,
    provider=None,
    langextract_instance=None,
):
    """
    Factory for provider-agnostic extractors.

    provider_name:
      - "heuristic"
      - "medgemma"
      - "langextract"
    """

    if provider_name == "heuristic":
        return HeuristicExtractor()

    if provider_name == "medgemma":
        if provider is None:
            raise ValueError("MedGemma provider required")
        return MedGemmaExtractor(provider)

    if provider_name == "langextract":
        if langextract_instance is None:
            raise ValueError("LangExtract instance required")
        return LangExtractExtractor(langextract_instance)

    raise ValueError(f"Unknown provider_name: {provider_name}")
