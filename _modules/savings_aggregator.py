def extract_potential_savings(analysis: dict) -> float:
    """
    Best-effort extraction of potential savings from an analysis result.
    Returns 0.0 if nothing is found.
    """

    if not analysis or not isinstance(analysis, dict):
        return 0.0

    total = 0.0

    # Case 1: Explicit summary field
    summary = analysis.get("summary", {})
    if isinstance(summary, dict):
        total += float(summary.get("potential_savings", 0) or 0)

    # Case 2: Line-item issues with savings
    issues = analysis.get("issues") or analysis.get("findings") or []
    if isinstance(issues, list):
        for issue in issues:
            if isinstance(issue, dict):
                total += float(issue.get("potential_savings", 0) or 0)

    # Case 3: Flat field (fallback)
    total += float(analysis.get("potential_savings", 0) or 0)

    return round(total, 2)
