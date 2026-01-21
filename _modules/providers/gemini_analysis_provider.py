import json
from typing import Optional, Dict

from _modules.providers.llm_interface import Issue, AnalysisResult, LLMProvider
from _modules.extractors.gemini_langextractor import run_prompt_gemini


class GeminiAnalysisProvider(LLMProvider):
    """
    Gemini-powered analysis provider.
    """

    def __init__(self, model: str = "gemini-1.5-flash"):
        self.model = model

    def name(self) -> str:
        return self.model

    def analyze_document(
        self,
        raw_text: str,
        facts: Optional[Dict] = None
    ) -> AnalysisResult:

        prompt = f"""
You are a healthcare billing analysis assistant.

Analyze the document and return a JSON array of issues.

For each issue:
- type: one of duplicate_charge, billing_error, non_covered_service,
        overbilling, insurance_issue, fsa_issue, other
- summary: short description
- evidence: brief supporting explanation
- max_savings: numeric dollar amount representing the MAXIMUM
  patient responsibility that could be removed if the issue
  were resolved favorably, using ONLY amounts explicitly stated
  in the document. If no amount can be determined with certainty,
  set this to null.

Be conservative. Do not guess or infer missing numbers.

If no issues are found, return an empty JSON array.

DOCUMENT:
{raw_text}
"""

        response_text = run_prompt_gemini(prompt) or "[]"

        try:
            raw_issues = json.loads(response_text)
            if not isinstance(raw_issues, list):
                raw_issues = []
        except json.JSONDecodeError:
            raw_issues = []

        issues = []
        total = 0.0

        for item in raw_issues:
            max_savings = item.get("max_savings")
            if max_savings is not None:
                max_savings = float(max_savings)
                total += max_savings

            issues.append(Issue(
                type=item.get("type", "other"),
                summary=item.get("summary", "Potential issue identified"),
                evidence=item.get("evidence"),
                max_savings=max_savings,
            ))

        meta = {
            "provider": self.name(),
            "issue_count": len(issues),
            "total_max_savings": round(total, 2),
        }

        return AnalysisResult(issues=issues, meta=meta)
