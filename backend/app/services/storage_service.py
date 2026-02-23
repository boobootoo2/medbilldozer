"""Google Cloud Storage service for document uploads using signed URLs."""

from datetime import timedelta

from app.config import settings
from google.cloud import storage
from google.oauth2 import service_account


class StorageService:
    """Handles file uploads and downloads to/from Google Cloud Storage."""

    def __init__(self):
        """Initialize GCS client."""
        # Create credentials from Firebase service account
        try:
            credentials_dict = {
                "type": "service_account",
                "project_id": settings.firebase_project_id,
                "private_key": settings.firebase_private_key.replace("\\n", "\n"),
                "client_email": settings.firebase_client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            credentials = service_account.Credentials.from_service_account_info(credentials_dict)
            self.client = storage.Client(project=settings.gcs_project_id, credentials=credentials)
            print(f"✅ GCS initialized with bucket: {settings.gcs_bucket_documents}")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize GCS: {e}")
            # Fallback to default credentials
            self.client = storage.Client(project=settings.gcs_project_id)

        self.documents_bucket = settings.gcs_bucket_documents
        self.clinical_bucket = settings.gcs_bucket_clinical_images

    def generate_signed_upload_url(
        self, bucket_name: str, blob_path: str, content_type: str, expires_in_minutes: int = 15
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
        self, bucket_name: str, blob_path: str, expires_in_minutes: int = 10
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
        try:
            content = blob.download_as_text(encoding="utf-8")
        except (UnicodeDecodeError, Exception):
            # Fallback: download raw bytes and decode, replacing any bad chars
            raw = blob.download_as_bytes()
            content = raw.decode("utf-8", errors="replace")
        return content

    async def download_bytes(self, bucket_name: str, blob_path: str) -> bytes:
        """
        Download file content as bytes.

        Tries direct GCS download first. If that fails (e.g. service account
        lacks Storage Object Viewer), falls back to a short-lived signed URL
        fetched via httpx.

        Args:
            bucket_name: GCS bucket name
            blob_path: Path within bucket

        Returns:
            File content as bytes
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            return blob.download_as_bytes()
        except Exception as direct_err:
            # Fallback: use a signed download URL + httpx
            # This works even when the service account lacks objectViewer.
            try:
                signed_url = self.generate_signed_download_url(
                    bucket_name=bucket_name,
                    blob_path=blob_path,
                    expires_in_minutes=5,
                )
                import httpx

                async with httpx.AsyncClient(timeout=60.0) as http_client:
                    resp = await http_client.get(signed_url)
                    resp.raise_for_status()
                    print(
                        f"⚠️  direct download failed ({direct_err}); "
                        f"signed-URL fallback succeeded ({len(resp.content)} bytes)"
                    )
                    return resp.content
            except Exception as url_err:
                raise RuntimeError(
                    f"GCS download failed. "
                    f"Direct: {direct_err!r}. "
                    f"Signed-URL fallback: {url_err!r}"
                ) from url_err

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
