"""Analysis API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from datetime import datetime, timedelta
from uuid import uuid4

from app.models.requests import AnalyzeRequest, AnalyzeResponse, AnalysisResultResponse
from app.services.analysis_service import AnalysisService, get_analysis_service
from app.services.db_service import DBService, get_db_service
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=AnalyzeResponse)
async def trigger_analysis(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service),
    db: DBService = Depends(get_db_service)
):
    """
    Trigger document analysis (async background task).

    Flow:
    1. Client calls this endpoint with document IDs
    2. Backend creates analysis record in database
    3. Backend queues background task to run MedGemma analysis
    4. Backend immediately returns analysis_id
    5. Client polls GET /analyze/{analysis_id} for results
    """
    try:
        # Generate analysis ID
        analysis_id = str(uuid4())

        # Validate documents belong to user
        for doc_id in request.document_ids:
            doc = await db.get_document(doc_id, current_user['user_id'])
            if not doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Document {doc_id} not found"
                )

        # Create analysis record
        await db.create_analysis(
            analysis_id=analysis_id,
            user_id=current_user['user_id'],
            document_ids=request.document_ids,
            provider=request.provider or "medgemma-ensemble"
        )

        # Queue background task for analysis
        background_tasks.add_task(
            analysis_service.run_analysis,
            analysis_id=analysis_id,
            document_ids=request.document_ids,
            user_id=current_user['user_id'],
            provider=request.provider or "medgemma-ensemble"
        )

        return AnalyzeResponse(
            analysis_id=analysis_id,
            status="queued",
            estimated_completion=datetime.utcnow() + timedelta(minutes=2)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger analysis: {str(e)}"
        )


@router.get("/{analysis_id}", response_model=AnalysisResultResponse)
async def get_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service)
):
    """
    Get analysis results (polling endpoint).

    Client should poll this endpoint every 2-3 seconds until status is 'completed' or 'failed'.
    """
    try:
        # Get analysis from database
        analysis = await db.get_analysis(
            analysis_id=analysis_id,
            user_id=current_user['user_id']
        )

        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )

        return AnalysisResultResponse(
            analysis_id=analysis['analysis_id'],
            status=analysis['status'],
            provider=analysis['provider'],
            results=analysis.get('results'),
            coverage_matrix=analysis.get('coverage_matrix'),
            total_savings_detected=analysis.get('total_savings_detected'),
            issues_count=analysis.get('issues_count', 0),
            created_at=analysis['created_at'],
            completed_at=analysis.get('completed_at')
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis: {str(e)}"
        )


@router.get("/")
async def list_analyses(
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service)
):
    """
    List all analyses for current user.
    """
    try:
        analyses = await db.list_user_analyses(
            user_id=current_user['user_id'],
            limit=limit,
            offset=offset
        )

        return {
            "analyses": analyses,
            "total": len(analyses),
            "offset": offset,
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list analyses: {str(e)}"
        )
