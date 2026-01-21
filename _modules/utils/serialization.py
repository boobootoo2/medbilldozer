# _modules/serialization.py


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


# _modules/serialization.py

def analysis_to_dict(result) -> dict:
    """
    Convert an AnalysisResult-like object into a pure dict.
    Duck-typed to avoid importing domain models.
    """
    return {
        "issues": [
            {
                "type": getattr(issue, "type", None),
                "summary": getattr(issue, "summary", None),
                "evidence": getattr(issue, "evidence", None),
                "max_savings": getattr(issue, "max_savings", None),
            }
            for issue in getattr(result, "issues", [])
        ],
        "meta": getattr(result, "meta", {}),
    }

