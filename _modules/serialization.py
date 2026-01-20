# _modules/serialization.py

from _modules.llm_interface import Issue, AnalysisResult

def issue_to_dict(issue: Issue) -> dict:
    return {
        "type": issue.type,
        "summary": issue.summary,
        "evidence": issue.evidence,
        "code": issue.code,
        "date": issue.date,
        "recommended_action": issue.recommended_action,
        "max_savings": issue.max_savings,
    }

def analysis_to_dict(analysis: AnalysisResult) -> dict:
    return {
        "issues": [issue_to_dict(i) for i in analysis.issues],
        "meta": analysis.meta or {},
    }

def dict_to_issue(data: dict) -> Issue:
    return Issue(**data)

def dict_to_analysis(data: dict) -> AnalysisResult:
    return AnalysisResult(
        issues=[dict_to_issue(i) for i in data.get("issues", [])],
        meta=data.get("meta", {}),
    )
