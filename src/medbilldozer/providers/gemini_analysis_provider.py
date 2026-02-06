"""Gemini-powered healthcare document analysis provider.

Provides Google Gemini-based analysis of healthcare documents to identify billing issues,
discrepancies, and potential patient savings.
"""

import json
from typing import Optional, Dict

from medbilldozer.providers.llm_interface import Issue, AnalysisResult, LLMProvider
from medbilldozer.extractors.gemini_langextractor import run_prompt_gemini


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

        prompt = f"""You are a medical billing auditor. Analyze the following patient documents for billing errors.

CRITICAL: Return ONLY a valid JSON array. No markdown, no tables, no explanations. Just JSON.

Look for these billing issues:
1. Gender mismatches (e.g., male patient billed for obstetric/gynecology procedures)
2. Age-inappropriate procedures (e.g., pediatric vaccine for 70-year-old)
3. Procedures on removed/absent body parts (e.g., appendix removal after prior appendectomy)
4. Procedures without supporting medical conditions in patient history
5. Duplicate charges (same CPT code, same date, same amount)
6. Temporal violations (procedures before/after impossible timeframes)

For each issue found, return:
{{
  "type": "gender_mismatch" | "age_inappropriate_procedure" | "anatomical_contradiction" | "procedure_inconsistent_with_health_history" | "duplicate_charge" | "temporal_violation" | "other",
  "summary": "Brief description",
  "evidence": "Why this is problematic",
  "code": "CPT code (e.g., 76805, 99213)",
  "max_savings": null or dollar amount
}}

IMPORTANT: Extract CPT codes from the document. Look for patterns like "CPT 76805" or standalone procedure codes.

Return ONLY the JSON array. If no issues: []

PATIENT DOCUMENTS:
{raw_text}

JSON OUTPUT:"""

        response_text = run_prompt_gemini(prompt) or "[]"

        try:
            # Clean up response text - sometimes LLMs wrap JSON in markdown
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            raw_issues = json.loads(cleaned_text)
            if not isinstance(raw_issues, list):
                raw_issues = []
        except json.JSONDecodeError as e:
            # Debug: print first 500 chars of failed response
            print(f"⚠️  Gemini JSON parse error: {e}")
            print(f"   Response preview: {response_text[:500]}")
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

