"""Serialization utilities for converting analysis objects to dicts.

Provides duck-typed serialization functions that work with various analysis
result objects without requiring explicit imports.
"""
# _modules/serialization.py


def issue_to_dict(issue):
    """Convert an Issue object to a dictionary.
    
    Uses duck typing to extract attributes without importing domain models.
    
    Args:
        issue: Issue object with type, summary, description, confidence attributes
    
    Returns:
        dict: Dictionary representation of the issue
    """

    return {
        "type": getattr(issue, "type", None)
                or getattr(issue, "category", None)
                or issue.__class__.__name__,

        "summary": getattr(issue, "summary", None),
        "description": getattr(issue, "description", None),
        "confidence": getattr(issue, "confidence", None),
        "computed": getattr(issue, "computed", None),
    }


def analysis_to_dict(result) -> dict:
    """Convert an AnalysisResult object into a pure dict.
    
    Duck-typed to avoid importing domain models. Extracts issues and metadata.
    
    Args:
        result: AnalysisResult object with issues and meta attributes
    
    Returns:
        dict: Dictionary with 'issues' list and 'meta' dict
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

