"""Analysis API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from datetime import datetime, timedelta
from uuid import uuid4

from app.models.requests import AnalyzeRequest, AnalyzeResponse, AnalysisResultResponse
from app.services.analysis_service import AnalysisService, get_analysis_service
from app.services.db_service import DBService, get_db_service
from app.dependencies import get_current_user
from app.utils import get_logger, log_with_context, get_correlation_id

router = APIRouter()
logger = get_logger(__name__)


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
    user_id = current_user['user_id']
    correlation_id = get_correlation_id()

    try:
        # Convert provider enum to string value (already validated by Pydantic)
        provider_str = request.provider.value if request.provider else "medgemma-ensemble"

        log_with_context(
            logger, 20,
            f"📊 Analysis requested for {len(request.document_ids)} document(s)",
            user_id=user_id,
            document_count=len(request.document_ids),
            provider=provider_str
        )

        # Generate analysis ID
        analysis_id = str(uuid4())
        log_with_context(
            logger, 20,
            f"📊 Generated analysis ID",
            user_id=user_id,
            analysis_id=analysis_id
        )

        # Validate documents belong to user
        logger.info(f"📊 Validating {len(request.document_ids)} document(s)...")
        for doc_id in request.document_ids:
            doc = await db.get_document(doc_id, user_id)
            if not doc:
                log_with_context(
                    logger, 30,
                    f"⚠️  Document not found or unauthorized",
                    user_id=user_id,
                    document_id=doc_id,
                    analysis_id=analysis_id
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "Document not found",
                        "message": f"Document {doc_id} not found or you don't have access to it",
                        "document_id": doc_id,
                        "correlation_id": correlation_id
                    }
                )

        # Create analysis record
        await db.create_analysis(
            analysis_id=analysis_id,
            user_id=user_id,
            document_ids=request.document_ids,
            provider=provider_str
        )
        log_with_context(
            logger, 20,
            f"✅ Created analysis record in database",
            user_id=user_id,
            analysis_id=analysis_id
        )

        # Queue background task for analysis
        background_tasks.add_task(
            analysis_service.run_analysis,
            analysis_id=analysis_id,
            document_ids=request.document_ids,
            user_id=user_id,
            provider=provider_str
        )
        log_with_context(
            logger, 20,
            f"🚀 Queued background analysis task",
            user_id=user_id,
            analysis_id=analysis_id
        )

        return AnalyzeResponse(
            analysis_id=analysis_id,
            status="queued",
            estimated_completion=datetime.utcnow() + timedelta(minutes=2)
        )

    except HTTPException:
        raise
    except Exception as e:
        log_with_context(
            logger, 40,
            f"❌ Failed to trigger analysis: {type(e).__name__}",
            user_id=user_id,
            error=str(e)
        )
        logger.exception("Analysis trigger failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Analysis trigger failed",
                "message": f"Failed to trigger analysis: {str(e)}",
                "correlation_id": correlation_id
            }
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
    user_id = current_user['user_id']
    correlation_id = get_correlation_id()

    try:
        log_with_context(
            logger, 20,
            f"📊 Fetching analysis status",
            user_id=user_id,
            analysis_id=analysis_id
        )

        # Get analysis from database
        analysis = await db.get_analysis(
            analysis_id=analysis_id,
            user_id=user_id
        )

        if not analysis:
            log_with_context(
                logger, 30,
                f"⚠️  Analysis not found",
                user_id=user_id,
                analysis_id=analysis_id
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Analysis not found",
                    "message": f"Analysis {analysis_id} not found. It may have been deleted or you don't have access to it.",
                    "analysis_id": analysis_id,
                    "correlation_id": correlation_id,
                    "help": "Make sure you're using the correct analysis ID and that it belongs to your account."
                }
            )

        log_with_context(
            logger, 20,
            f"✅ Analysis found: {analysis['status']}",
            user_id=user_id,
            analysis_id=analysis_id,
            status=analysis['status']
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
        log_with_context(
            logger, 40,
            f"❌ Failed to get analysis: {type(e).__name__}",
            user_id=user_id,
            analysis_id=analysis_id,
            error=str(e)
        )
        logger.exception("Get analysis failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to retrieve analysis",
                "message": f"An error occurred while retrieving the analysis: {str(e)}",
                "analysis_id": analysis_id,
                "correlation_id": correlation_id
            }
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
