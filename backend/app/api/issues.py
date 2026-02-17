"""Issue management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel

from app.services.db_service import DBService, get_db_service
from app.dependencies import get_current_user

router = APIRouter()


# Request/Response Models
class UpdateIssueStatusRequest(BaseModel):
    status: str  # 'open', 'follow_up', 'resolved', 'ignored'
    notes: Optional[str] = None


class IssueResponse(BaseModel):
    issue_id: str
    analysis_id: str
    document_id: Optional[str]
    issue_type: str
    summary: str
    evidence: Optional[str]
    code: Optional[str]
    recommended_action: Optional[str]
    max_savings: float
    confidence: Optional[str]
    source: Optional[str]
    status: str
    status_updated_at: Optional[str]
    status_updated_by: Optional[str]
    notes: Optional[str]
    created_at: str
    metadata: dict


class IssueStatisticsResponse(BaseModel):
    analysis_id: str
    open_count: int
    follow_up_count: int
    resolved_count: int
    ignored_count: int
    open_potential_savings: float
    follow_up_potential_savings: float
    resolved_savings: float


@router.get("/analysis/{analysis_id}", response_model=List[IssueResponse])
async def get_analysis_issues(
    analysis_id: str,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service)
):
    """
    Get all issues for a specific analysis.

    Args:
        analysis_id: Analysis ID
        status_filter: Filter by status (open, follow_up, resolved, ignored)
    """
    try:
        # Verify user owns this analysis
        analysis = await db.get_analysis(analysis_id, current_user['user_id'])
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )

        # Get issues
        issues = await db.get_issues_by_analysis(
            analysis_id,
            status_filter=status_filter
        )

        return [
            IssueResponse(
                issue_id=str(issue['issue_id']),
                analysis_id=str(issue['analysis_id']),
                document_id=str(issue['document_id']) if issue.get('document_id') else None,
                issue_type=issue['issue_type'],
                summary=issue['summary'],
                evidence=issue.get('evidence'),
                code=issue.get('code'),
                recommended_action=issue.get('recommended_action'),
                max_savings=float(issue.get('max_savings', 0)),
                confidence=issue.get('confidence'),
                source=issue.get('source'),
                status=issue.get('status', 'open'),
                status_updated_at=issue.get('status_updated_at'),
                status_updated_by=str(issue['status_updated_by']) if issue.get('status_updated_by') else None,
                notes=issue.get('notes'),
                created_at=str(issue['created_at']),
                metadata=issue.get('metadata', {})
            )
            for issue in issues
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get issues: {str(e)}"
        )


@router.patch("/{issue_id}/status")
async def update_issue_status(
    issue_id: str,
    request: UpdateIssueStatusRequest,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service)
):
    """
    Update the status of an issue (open, follow_up, resolved, ignored).
    """
    try:
        # Validate status
        valid_statuses = ['open', 'follow_up', 'resolved', 'ignored']
        if request.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        # Verify user owns this issue (via analysis)
        issue = await db.get_issue(issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found"
            )

        analysis = await db.get_analysis(
            str(issue['analysis_id']),
            current_user['user_id']
        )
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this issue"
            )

        # Update issue status
        updated_issue = await db.update_issue_status(
            issue_id=issue_id,
            status=request.status,
            notes=request.notes,
            updated_by=current_user['user_id']
        )

        return {
            "message": "Issue status updated successfully",
            "issue_id": issue_id,
            "status": request.status,
            "updated_at": updated_issue.get('status_updated_at')
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update issue status: {str(e)}"
        )


@router.get("/analysis/{analysis_id}/statistics", response_model=IssueStatisticsResponse)
async def get_issue_statistics(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service)
):
    """
    Get statistics on issue statuses for an analysis.
    """
    try:
        # Verify user owns this analysis
        analysis = await db.get_analysis(analysis_id, current_user['user_id'])
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )

        # Get statistics
        stats = await db.get_issue_statistics(analysis_id)

        return IssueStatisticsResponse(
            analysis_id=analysis_id,
            open_count=stats.get('open_count', 0),
            follow_up_count=stats.get('follow_up_count', 0),
            resolved_count=stats.get('resolved_count', 0),
            ignored_count=stats.get('ignored_count', 0),
            open_potential_savings=float(stats.get('open_potential_savings', 0) or 0),
            follow_up_potential_savings=float(stats.get('follow_up_potential_savings', 0) or 0),
            resolved_savings=float(stats.get('resolved_savings', 0) or 0)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get issue statistics: {str(e)}"
        )


@router.post("/{issue_id}/notes")
async def add_issue_note(
    issue_id: str,
    note: str,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service)
):
    """
    Add or update notes for an issue.
    """
    try:
        # Verify user owns this issue
        issue = await db.get_issue(issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue not found"
            )

        analysis = await db.get_analysis(
            str(issue['analysis_id']),
            current_user['user_id']
        )
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this issue"
            )

        # Update notes
        await db.update_issue_notes(issue_id, note)

        return {
            "message": "Notes updated successfully",
            "issue_id": issue_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notes: {str(e)}"
        )
