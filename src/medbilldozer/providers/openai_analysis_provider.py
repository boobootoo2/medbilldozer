"""OpenAI-powered healthcare document analysis provider.

Provides GPT-based analysis of healthcare documents to identify billing issues,
discrepancies, and potential patient savings.
"""

from openai import OpenAI
import json
from typing import Optional, Dict

from medbilldozer.providers.llm_interface import Issue, AnalysisResult, LLMProvider


class OpenAIAnalysisProvider(LLMProvider):
    """
    OpenAI-powered analysis provider.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = OpenAI()
        self.model = model

    def name(self) -> str:
        return self.model

    def analyze_document(
        self,
        raw_text: str,
        facts: Optional[Dict] = None
    ) -> AnalysisResult:
        prompt = f"""You are a healthcare billing expert. Analyze this medical bill for billing errors.

ISSUE TYPES TO DETECT:
1. duplicate_charge: Same CPT code on same date with identical amounts (clear sign of duplicate billing)
2. overbilling: Charges that are unusually high, facility fees that exceed norms, or math errors
3. coding_error: Procedure coded as higher complexity/cost than appropriate
4. unbundling: Related services billed separately instead of as one bundled code
5. cross_bill_discrepancy: Same service appears on multiple bills with different amounts
6. excessive_charge: Single charge much higher than reasonable for that service
7. facility_fee_error: Facility/room fees that appear incorrect or excessive
8. gender_mismatch: Procedures for anatomy the patient doesn't have (e.g., male with obstetric procedures)
9. age_inappropriate_procedure: Procedures outside recommended age ranges (e.g., 8yo with colonoscopy)
10. anatomical_contradiction: Procedures on organs/body parts the patient doesn't have
11. procedure_inconsistent_with_health_history: Procedures without supporting medical conditions
12. diagnosis_procedure_mismatch: Procedure doesn't match the diagnosis
13. temporal_violation: Procedures that violate medical timelines

IMPORTANT RULES:
- If you see the SAME CPT code listed multiple times on the SAME date with the SAME patient responsibility amount, THIS IS A DUPLICATE
- If a facility fee exceeds $500, flag as potentially excessive
- If charges are clearly repeated, flag as potential overbilling
- Use only dollar amounts explicitly shown in the document for max_savings
- Be thorough - this is for patient advocacy, not insurance approval
- ALWAYS include the CPT code in the "code" field when available

RESPONSE FORMAT - Return ONLY a valid JSON array, no other text:
[
  {{
    "type": "issue_type",
    "summary": "Brief description",
    "evidence": "Specific facts and amounts",
    "code": "CPT code or procedure code (e.g., 76805, 99213)",
    "max_savings": 150.00
  }}
]

DOCUMENT:
{raw_text}"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You analyze healthcare billing documents and return "
                        "ONLY valid JSON. No prose."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        analysis_text = response.choices[0].message.content or "[]"

        try:
            raw_issues = json.loads(analysis_text)
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
                code=item.get("code"),  # Include CPT code for matching
                max_savings=max_savings,
            ))

        meta = {
            "provider": self.name(),
            "issue_count": len(issues),
            "total_max_savings": round(total, 2),
        }

        return AnalysisResult(issues=issues, meta=meta)

