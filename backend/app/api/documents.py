"""Document management API endpoints."""

import csv
import io
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from app.dependencies import get_current_user
from app.models.requests import (
    AnalysisProvider,
    BulkAnalyzeRequest,
    BulkAnalyzeResponse,
    ConfirmUploadRequest,
    DocumentActionStatistics,
    DocumentActionUpdate,
    DocumentListResponse,
    DocumentMetadataUpdate,
    DocumentResponse,
    EnrichedDocumentResponse,
    UploadUrlRequest,
    UploadUrlResponse,
)
from app.services.db_service import DBService, get_db_service
from app.services.storage_service import StorageService, get_storage_service
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

router = APIRouter()


@router.post("/upload-url", response_model=UploadUrlResponse)
async def generate_upload_url(
    request: UploadUrlRequest,
    current_user: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service),
):
    """
    Generate signed URL for direct client upload to GCS.

    Flow:
    1. Client calls this endpoint with filename and content_type
    2. Backend generates signed URL (15min expiry)
    3. Client uploads file directly to GCS using signed URL
    4. Client confirms upload with /confirm endpoint
    """
    try:
        # Generate unique document ID
        document_id = str(uuid4())

        # Construct GCS path: {user_id}/{document_id}/{filename}
        user_id = current_user["user_id"]
        gcs_path = f"{user_id}/{document_id}/{request.filename}"

        # Generate signed upload URL
        signed_url = storage.generate_signed_upload_url(
            bucket_name=storage.documents_bucket,
            blob_path=gcs_path,
            content_type=request.content_type,
            expires_in_minutes=15,
        )

        return UploadUrlResponse(
            document_id=document_id,
            upload_url=signed_url,
            gcs_path=gcs_path,
            expires_at=datetime.utcnow() + timedelta(minutes=15),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload URL: {str(e)}",
        )


@router.post("/confirm")
async def confirm_upload(
    request: ConfirmUploadRequest,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service),
    storage: StorageService = Depends(get_storage_service),
):
    """
    Confirm document upload and save metadata to database.

    Called after client successfully uploads file to GCS.
    """
    try:
        # Verify file exists in GCS
        file_exists = storage.file_exists(
            bucket_name=storage.documents_bucket, blob_path=request.gcs_path
        )

        if not file_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File not found in storage"
            )

        # Save metadata to database (only include columns that exist in current schema)
        document_data = {
            "document_id": request.document_id,
            "user_id": current_user["user_id"],
            "filename": request.filename,
            "gcs_path": request.gcs_path,
            "status": "uploaded",
        }

        # Optional columns - only add if they exist in DB schema
        if hasattr(request, "content_type") and request.content_type:
            document_data["content_type"] = request.content_type

        # Note: size_bytes, original_filename, and document_type columns don't exist yet
        # They need to be added via database migration

        document = await db.insert_document(document_data)

        return {
            "status": "confirmed",
            "document_id": request.document_id,
            "message": "Document uploaded successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ CONFIRM UPLOAD ERROR: {type(e).__name__}: {str(e)}")
        import traceback

        print(f"❌ TRACEBACK:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm upload: {str(e)}",
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service),
    storage: StorageService = Depends(get_storage_service),
):
    """
    Get document metadata and signed download URL.
    """
    try:
        # Get document from database
        document = await db.get_document(document_id=document_id, user_id=current_user["user_id"])

        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        # Generate time-limited signed URL for download
        download_url = storage.generate_signed_download_url(
            bucket_name=storage.documents_bucket,
            blob_path=document["gcs_path"],
            expires_in_minutes=10,
        )

        return DocumentResponse(
            document_id=document["document_id"],
            filename=document["filename"],
            content_type=document["content_type"],
            size_bytes=document.get("size_bytes", 0),  # Default to 0 if column doesn't exist
            uploaded_at=document["uploaded_at"],
            status=document["status"],
            document_type=document.get("document_type"),
            download_url=download_url,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}",
        )


@router.get("/")
async def list_documents(
    profile_id: Optional[str] = None,
    action: Optional[str] = None,
    flagged_only: bool = False,
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service),
):
    """
    List documents with enhanced filtering by profile, action status, and flagged state.

    Query Parameters:
        - profile_id: Filter by profile (e.g., PH-001, DEP-001)
        - action: Filter by action status (ignored, followup, resolved)
        - flagged_only: Return only flagged documents
        - status_filter: Filter by document status
        - limit: Max results
        - offset: Pagination offset
    """
    try:
        # Try enhanced query first (requires migrations to be run)
        try:
            documents = await db.list_user_documents_enhanced(
                user_id=current_user["user_id"],
                profile_id=profile_id,
                action=action,
                status=status_filter,
                limit=limit,
                offset=offset,
            )
        except Exception as e:
            # Fall back to basic query if enhanced query fails (migrations not run yet)
            if action or profile_id:
                # Cannot filter by action/profile without migrations
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database migrations required. Please run migrations to use filters.",
                )
            # Use basic query without filters
            documents = await db.list_user_documents(
                user_id=current_user["user_id"], limit=limit, offset=offset
            )

        # Get issue counts for flagged status computation (may fail if issues table doesn't exist)
        document_ids = [d["document_id"] for d in documents]
        try:
            issue_counts = await db.get_document_issue_counts(document_ids) if document_ids else {}
        except Exception as e:
            # Issues table may not exist yet - return empty counts
            print(f"⚠️ Could not fetch issue counts (table may not exist): {e}")
            issue_counts = {}

        # Enrich responses
        enriched_docs = []
        for doc in documents:
            doc_id = str(doc["document_id"])
            metadata = doc.get("metadata", {})
            issues = issue_counts.get(doc_id, {})

            # Determine if flagged (has high-confidence open issues)
            flagged = issues.get("high_confidence_open", 0) > 0

            # Skip if flagged_only filter is set and doc is not flagged
            if flagged_only and not flagged:
                continue

            enriched_docs.append(
                EnrichedDocumentResponse(
                    document_id=doc_id,
                    filename=doc["filename"],
                    content_type=doc.get("content_type")
                    or "application/pdf",  # Default if None or missing
                    size_bytes=doc.get("size_bytes") or 0,
                    uploaded_at=doc["uploaded_at"],
                    status=doc["status"],
                    document_type=doc.get("document_type"),
                    # Profile data from metadata
                    profile_id=metadata.get("profile_id"),
                    profile_name=metadata.get("profile_name"),
                    profile_type=metadata.get("profile_type"),
                    provider_name=metadata.get("provider_name"),
                    service_date=metadata.get("service_date"),
                    patient_responsibility_amount=metadata.get("patient_responsibility_amount"),
                    # Action tracking
                    action=doc.get("action"),
                    action_notes=doc.get("action_notes"),
                    action_date=doc.get("action_date"),
                    action_updated_by=(
                        str(doc["action_updated_by"]) if doc.get("action_updated_by") else None
                    ),
                    # Computed fields
                    flagged=flagged,
                    high_confidence_issues_count=issues.get("high_confidence_open", 0),
                    total_issues_count=issues.get("total", 0),
                )
            )

        # Return in DocumentListResponse format for backward compatibility
        return {
            "documents": enriched_docs,
            "total": len(enriched_docs),
            "offset": offset,
            "limit": limit,
        }

    except Exception as e:
        print(f"❌ LIST DOCUMENTS ERROR: {type(e).__name__}: {str(e)}")
        import traceback

        print(f"❌ TRACEBACK:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}",
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service),
    storage: StorageService = Depends(get_storage_service),
):
    """
    Delete document from database and storage.
    """
    try:
        # Get document
        document = await db.get_document(document_id=document_id, user_id=current_user["user_id"])

        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        # Delete from GCS
        storage.delete_file(bucket_name=storage.documents_bucket, blob_path=document["gcs_path"])

        # Delete from database
        await db.delete_document(document_id=document_id, user_id=current_user["user_id"])

        return {"message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}",
        )


# ============================================================================
# DOCUMENT ACTION MANAGEMENT
# ============================================================================


@router.patch("/{document_id}/action", response_model=EnrichedDocumentResponse)
async def update_document_action(
    document_id: str,
    request: DocumentActionUpdate,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service),
):
    """
    Update action status for a document (ignored/followup/resolved).

    Setting action=null clears the action status.
    """
    try:
        # Verify document ownership
        document = await db.get_document(document_id, current_user["user_id"])
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        # Update action
        updated_doc = await db.update_document_action(
            document_id=document_id,
            action=request.action,
            action_notes=request.action_notes,
            action_updated_by=current_user["user_id"],
        )

        # Build enriched response
        metadata = updated_doc.get("metadata", {})
        issue_counts = await db.get_document_issue_counts([document_id])
        issues = issue_counts.get(document_id, {})
        flagged = issues.get("high_confidence_open", 0) > 0

        return EnrichedDocumentResponse(
            document_id=updated_doc["document_id"],
            filename=updated_doc["filename"],
            content_type=updated_doc["content_type"],
            size_bytes=updated_doc.get("size_bytes", 0),
            uploaded_at=updated_doc["uploaded_at"],
            status=updated_doc["status"],
            document_type=updated_doc.get("document_type"),
            profile_id=metadata.get("profile_id"),
            profile_name=metadata.get("profile_name"),
            profile_type=metadata.get("profile_type"),
            provider_name=metadata.get("provider_name"),
            service_date=metadata.get("service_date"),
            patient_responsibility_amount=metadata.get("patient_responsibility_amount"),
            action=updated_doc.get("action"),
            action_notes=updated_doc.get("action_notes"),
            action_date=updated_doc.get("action_date"),
            action_updated_by=(
                str(updated_doc["action_updated_by"])
                if updated_doc.get("action_updated_by")
                else None
            ),
            flagged=flagged,
            high_confidence_issues_count=issues.get("high_confidence_open", 0),
            total_issues_count=issues.get("total", 0),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document action: {str(e)}",
        )


@router.patch("/{document_id}/metadata", response_model=EnrichedDocumentResponse)
async def update_document_metadata(
    document_id: str,
    request: DocumentMetadataUpdate,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service),
):
    """
    Update document metadata (profile info, provider, amounts, etc).
    """
    try:
        # Verify ownership
        document = await db.get_document(document_id, current_user["user_id"])
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        # Merge with existing metadata
        existing_metadata = document.get("metadata", {})
        update_data = request.model_dump(exclude_none=True)
        merged_metadata = {**existing_metadata, **update_data}

        # Update in database
        updated_doc = await db.update_document_metadata(
            document_id=document_id, metadata=merged_metadata
        )

        # Build enriched response
        metadata = updated_doc.get("metadata", {})
        issue_counts = await db.get_document_issue_counts([document_id])
        issues = issue_counts.get(document_id, {})
        flagged = issues.get("high_confidence_open", 0) > 0

        return EnrichedDocumentResponse(
            document_id=updated_doc["document_id"],
            filename=updated_doc["filename"],
            content_type=updated_doc["content_type"],
            size_bytes=updated_doc.get("size_bytes", 0),
            uploaded_at=updated_doc["uploaded_at"],
            status=updated_doc["status"],
            document_type=updated_doc.get("document_type"),
            profile_id=metadata.get("profile_id"),
            profile_name=metadata.get("profile_name"),
            profile_type=metadata.get("profile_type"),
            provider_name=metadata.get("provider_name"),
            service_date=metadata.get("service_date"),
            patient_responsibility_amount=metadata.get("patient_responsibility_amount"),
            action=updated_doc.get("action"),
            action_notes=updated_doc.get("action_notes"),
            action_date=updated_doc.get("action_date"),
            action_updated_by=(
                str(updated_doc["action_updated_by"])
                if updated_doc.get("action_updated_by")
                else None
            ),
            flagged=flagged,
            high_confidence_issues_count=issues.get("high_confidence_open", 0),
            total_issues_count=issues.get("total", 0),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document metadata: {str(e)}",
        )


@router.post("/analyze-bulk", response_model=BulkAnalyzeResponse)
async def analyze_documents_bulk(
    request: BulkAnalyzeRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service),
):
    """
    Analyze multiple documents in parallel (background task).

    Optionally exclude flagged documents from analysis.
    """
    try:
        # Import here to avoid circular dependency
        from app.services.analysis_service import AnalysisService, get_analysis_service

        analysis_service = get_analysis_service()

        # Validate documents exist and belong to user
        valid_doc_ids = []
        excluded_doc_ids = []

        for doc_id in request.document_ids:
            doc = await db.get_document(doc_id, current_user["user_id"])
            if not doc:
                continue

            # Check if should be excluded
            if request.exclude_flagged:
                # Get issue counts
                issues = await db.get_document_issue_counts([doc_id])
                flagged = issues.get(doc_id, {}).get("high_confidence_open", 0) > 0

                if flagged:
                    excluded_doc_ids.append(doc_id)
                    continue

            valid_doc_ids.append(doc_id)

        if not valid_doc_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid documents to analyze (all excluded or not found)",
            )

        # Create analysis record
        analysis_id = str(uuid4())
        provider_str = request.provider.value if request.provider else "medgemma-ensemble"

        await db.create_analysis(
            analysis_id=analysis_id,
            user_id=current_user["user_id"],
            document_ids=valid_doc_ids,
            provider=provider_str,
        )

        # Trigger background analysis
        background_tasks.add_task(
            analysis_service.run_analysis,
            analysis_id=analysis_id,
            document_ids=valid_doc_ids,
            user_id=current_user["user_id"],
            provider=provider_str,
        )

        return BulkAnalyzeResponse(
            analysis_id=analysis_id,
            status="queued",
            documents_submitted=len(valid_doc_ids),
            documents_excluded=len(excluded_doc_ids),
            excluded_reason=(
                f"{len(excluded_doc_ids)} flagged documents excluded" if excluded_doc_ids else None
            ),
            estimated_completion=datetime.utcnow() + timedelta(minutes=len(valid_doc_ids) * 2),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start bulk analysis: {str(e)}",
        )


@router.get("/statistics", response_model=DocumentActionStatistics)
async def get_document_statistics(
    profile_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service),
):
    """
    Get statistics on document actions (followup, resolved, etc).

    Optionally filter by profile_id.
    """
    try:
        stats = await db.get_document_action_statistics(
            user_id=current_user["user_id"], profile_id=profile_id
        )

        return DocumentActionStatistics(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}",
        )


@router.get("/export/actioned")
async def export_actioned_documents(
    profile_id: Optional[str] = None,
    format: str = "csv",
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service),
):
    """
    Export documents with actions (ignored/followup/resolved) to CSV or JSON.

    Query Parameters:
        - profile_id: Filter by profile (optional)
        - format: csv or json (default: csv)
    """
    try:
        # Get actioned documents (documents with action != NULL)
        # Query for documents with any action
        all_docs = await db.list_user_documents_enhanced(
            user_id=current_user["user_id"], profile_id=profile_id, limit=1000
        )

        # Filter to only documents with actions
        actioned_docs = [doc for doc in all_docs if doc.get("action") is not None]

        if format == "csv":
            # Generate CSV
            output = io.StringIO()
            writer = csv.writer(output)

            writer.writerow(
                [
                    "Document ID",
                    "Profile",
                    "Provider",
                    "Service Date",
                    "Amount",
                    "Action",
                    "Action Date",
                    "Notes",
                    "Flagged",
                ]
            )

            # Get issue counts for flagged status
            doc_ids = [doc["document_id"] for doc in actioned_docs]
            issue_counts = await db.get_document_issue_counts(doc_ids) if doc_ids else {}

            for doc in actioned_docs:
                metadata = doc.get("metadata", {})
                doc_id = str(doc["document_id"])
                issues = issue_counts.get(doc_id, {})
                flagged = issues.get("high_confidence_open", 0) > 0

                writer.writerow(
                    [
                        doc_id,
                        metadata.get("profile_name", "N/A"),
                        metadata.get("provider_name", "N/A"),
                        metadata.get("service_date", "N/A"),
                        f"${metadata.get('patient_responsibility_amount', 0):.2f}",
                        doc.get("action", "").title(),
                        doc.get("action_date", "N/A"),
                        doc.get("action_notes", ""),
                        "Yes" if flagged else "No",
                    ]
                )

            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=actioned_documents_{profile_id or 'all'}_{datetime.now().strftime('%Y%m%d')}.csv"
                },
            )
        else:
            # Return JSON
            return {"documents": actioned_docs}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export documents: {str(e)}",
        )
