"""Google Cloud Storage service for document uploads using signed URLs."""
from datetime import timedelta
from google.cloud import storage
from google.oauth2 import service_account
from app.config import settings


class StorageService:
    """Handles file uploads and downloads to/from Google Cloud Storage."""

    def __init__(self):
        """Initialize GCS client."""
        # Initialize with default credentials or service account
        self.client = storage.Client(project=settings.gcs_project_id)
        self.documents_bucket = settings.gcs_bucket_documents
        self.clinical_bucket = settings.gcs_bucket_clinical_images

    def generate_signed_upload_url(
        self,
        bucket_name: str,
        blob_path: str,
        content_type: str,
        expires_in_minutes: int = 15
    ) -> str:
        """
        Generate a signed URL for client to upload file directly to GCS.

        Args:
            bucket_name: GCS bucket name
            blob_path: Path within bucket (e.g., "user123/doc456/file.pdf")
            content_type: MIME type of file
            expires_in_minutes: URL expiration time

        Returns:
            Signed URL string valid for PUT requests
        """
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_path)

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expires_in_minutes),
            method="PUT",
            content_type=content_type,
        )

        return url

    def generate_signed_download_url(
        self,
        bucket_name: str,
        blob_path: str,
        expires_in_minutes: int = 10
    ) -> str:
        """
        Generate a signed URL for client to download file from GCS.

        Args:
            bucket_name: GCS bucket name
            blob_path: Path within bucket
            expires_in_minutes: URL expiration time

        Returns:
            Signed URL string valid for GET requests
        """
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_path)

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expires_in_minutes),
            method="GET",
        )

        return url

    async def download_text(self, bucket_name: str, blob_path: str) -> str:
        """
        Download file content as text.

        Args:
            bucket_name: GCS bucket name
            blob_path: Path within bucket

        Returns:
            File content as string
        """
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        content = blob.download_as_text()
        return content

    async def download_bytes(self, bucket_name: str, blob_path: str) -> bytes:
        """
        Download file content as bytes.

        Args:
            bucket_name: GCS bucket name
            blob_path: Path within bucket

        Returns:
            File content as bytes
        """
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        content = blob.download_as_bytes()
        return content

    def delete_file(self, bucket_name: str, blob_path: str) -> bool:
        """
        Delete a file from GCS.

        Args:
            bucket_name: GCS bucket name
            blob_path: Path within bucket

        Returns:
            True if successful
        """
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.delete()
        return True

    def file_exists(self, bucket_name: str, blob_path: str) -> bool:
        """
        Check if a file exists in GCS.

        Args:
            bucket_name: GCS bucket name
            blob_path: Path within bucket

        Returns:
            True if file exists
        """
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        return blob.exists()


# Singleton instance
_storage_service: StorageService | None = None


def get_storage_service() -> StorageService:
    """Get or create StorageService singleton."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
