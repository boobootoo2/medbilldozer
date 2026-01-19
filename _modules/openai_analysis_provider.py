# _modules/openai_analysis_provider.py

from openai import OpenAI


class Issue:
    def __init__(self, summary, evidence=None, max_savings=None):
        self.summary = summary
        self.evidence = evidence
        self.max_savings = max_savings


class AnalysisResult:
    def __init__(self, issues):
        self.issues = issues


class OpenAIAnalysisProvider:
    """
    OpenAI-powered analysis provider.
    Duck-typed to match existing providers.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = OpenAI()
        self.model = model

    def health_check(self) -> bool:
        return True

    def analyze_document(self, text: str):
        prompt = f"""
You are a healthcare billing analysis assistant.

Identify:
- duplicate charges
- billing errors
- non-covered services
- overbilling
- insurance or FSA issues

Be conservative.
If no issues are found, say so clearly.

DOCUMENT:
{text}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You analyze healthcare billing documents.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        analysis_text = response.choices[0].message.content or ""

        issue = Issue(
            summary="AI Analysis (OpenAI)",
            evidence=analysis_text,
            max_savings=None,
        )

        return AnalysisResult(issues=[issue])
