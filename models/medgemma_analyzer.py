from analysis_engine import BaseAnalyzer, AnalysisResult


class MedGemmaAnalyzer(BaseAnalyzer):
    def __init__(self, model):
        self.model = model  # HF / local / containerized

    def analyze(self, text: str) -> AnalysisResult:
        """
        MedGemma is used for:
        - detecting duplicates
        - identifying eligibility signals
        - extracting cost components
        """

        prompt = f"""
        You are analyzing medical billing text.

        Extract potential billing issues as a JSON list.
        Focus on:
        - duplicate procedures
        - coverage eligibility
        - copays and patient responsibility
        - FSA-eligible signals

        Text:
        {text}
        """

        # Pseudocode — adapt to how you're running MedGemma
        # For example, if `model` is a local generator object expose a `generate(prompt)` method
        response = None
        try:
            response = self.model.generate(prompt)
        except Exception:
            # Fallback: store the prompt as the response so _parse_response can still run
            response = "[]"

        findings = self._parse_response(response)

        return AnalysisResult(
            findings=findings,
            model_used="medgemma"
        )

    def _parse_response(self, response: str):
        # Keep this simple for demo purposes. Real parsing should validate JSON.
        # If the model returns a JSON string, attempt a naive parse; otherwise
        # return a couple of placeholder findings.
        import json

        try:
            parsed = json.loads(response)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

        # Demo fallback
        return [
            {"type": "duplicate_procedure", "confidence": "high"},
            {"type": "fsa_eligible_copay", "confidence": "medium"}
        ]
