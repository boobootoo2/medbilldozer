"""Document management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from uuid import uuid4

from app.models.requests import (
    UploadUrlRequest, UploadUrlResponse,
    ConfirmUploadRequest, DocumentResponse,
    DocumentListResponse
)
from app.services.storage_service import StorageService, get_storage_service
from app.services.db_service import DBService, get_db_service
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/upload-url", response_model=UploadUrlResponse)
async def generate_upload_url(
    request: UploadUrlRequest,
    current_user: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service)
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
        user_id = current_user['user_id']
        gcs_path = f"{user_id}/{document_id}/{request.filename}"

        # Generate signed upload URL
        signed_url = storage.generate_signed_upload_url(
            bucket_name=storage.documents_bucket,
            blob_path=gcs_path,
            content_type=request.content_type,
            expires_in_minutes=15
        )

        return UploadUrlResponse(
            document_id=document_id,
            upload_url=signed_url,
            gcs_path=gcs_path,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload URL: {str(e)}"
        )


@router.post("/confirm")
async def confirm_upload(
    request: ConfirmUploadRequest,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service),
    storage: StorageService = Depends(get_storage_service)
):
    """
    Confirm document upload and save metadata to database.

    Called after client successfully uploads file to GCS.
    """
    try:
        # Verify file exists in GCS
        file_exists = storage.file_exists(
            bucket_name=storage.documents_bucket,
            blob_path=request.gcs_path
        )

        if not file_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File not found in storage"
            )

        # Save metadata to database
        document_data = {
            "document_id": request.document_id,
            "user_id": current_user['user_id'],
            "filename": request.filename,
            "original_filename": request.filename,
            "gcs_path": request.gcs_path,
            "content_type": "application/pdf",  # TODO: get from request
            "size_bytes": request.size_bytes,
            "status": "uploaded",
            "document_type": request.document_type
        }

        document = await db.insert_document(document_data)

        return {
            "status": "confirmed",
            "document_id": request.document_id,
            "message": "Document uploaded successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm upload: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service),
    storage: StorageService = Depends(get_storage_service)
):
    """
    Get document metadata and signed download URL.
    """
    try:
        # Get document from database
        document = await db.get_document(
            document_id=document_id,
            user_id=current_user['user_id']
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Generate time-limited signed URL for download
        download_url = storage.generate_signed_download_url(
            bucket_name=storage.documents_bucket,
            blob_path=document['gcs_path'],
            expires_in_minutes=10
        )

        return DocumentResponse(
            document_id=document['document_id'],
            filename=document['filename'],
            content_type=document['content_type'],
            size_bytes=document['size_bytes'],
            uploaded_at=document['uploaded_at'],
            status=document['status'],
            document_type=document.get('document_type'),
            download_url=download_url
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}"
        )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service)
):
    """
    List all documents for current user.
    """
    try:
        documents = await db.list_user_documents(
            user_id=current_user['user_id'],
            limit=limit,
            offset=offset
        )

        document_responses = [
            DocumentResponse(
                document_id=doc['document_id'],
                filename=doc['filename'],
                content_type=doc['content_type'],
                size_bytes=doc['size_bytes'],
                uploaded_at=doc['uploaded_at'],
                status=doc['status'],
                document_type=doc.get('document_type')
            )
            for doc in documents
        ]

        return DocumentListResponse(
            documents=document_responses,
            total=len(documents),
            offset=offset,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service),
    storage: StorageService = Depends(get_storage_service)
):
    """
    Delete document from database and storage.
    """
    try:
        # Get document
        document = await db.get_document(
            document_id=document_id,
            user_id=current_user['user_id']
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Delete from GCS
        storage.delete_file(
            bucket_name=storage.documents_bucket,
            blob_path=document['gcs_path']
        )

        # Delete from database
        await db.delete_document(
            document_id=document_id,
            user_id=current_user['user_id']
        )

        return {"message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )
