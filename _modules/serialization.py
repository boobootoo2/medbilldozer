# _modules/serialization.py

from _modules.llm_interface import Issue, AnalysisResult

def issue_to_dict(issue):
    return {
        "type": getattr(issue, "type", None)
                or getattr(issue, "category", None)
                or issue.__class__.__name__,

        "summary": getattr(issue, "summary", None),
        "description": getattr(issue, "description", None),
        "confidence": getattr(issue, "confidence", None),
        "computed": getattr(issue, "computed", None),
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
