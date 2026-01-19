from _modules.openai_langextractor import extract_facts_openai
from _modules.gemini_langextractor import extract_facts_gemini
from _modules.local_heuristic_extractor import extract_facts_local


def extract_facts(raw_text: str, provider: str):
    if provider == "openai":
        return extract_facts_openai(raw_text)

    if provider == "gemini":
        return extract_facts_gemini(raw_text)

    if provider == "heuristic":
        return extract_facts_local(raw_text)

    raise ValueError(f"Unknown extractor provider: {provider}")
