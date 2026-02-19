#!/usr/bin/env python3
"""Test local upload endpoint to diagnose 500 error."""
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Load .env file from backend directory
from dotenv import load_dotenv
env_path = backend_dir / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded .env from {env_path}")
else:
    print(f"⚠️  No .env file found at {env_path}")

def test_storage_service():
    """Test StorageService initialization and signed URL generation."""
    print("="*60)
    print("Testing StorageService initialization...")
    print("="*60)

    try:
        from app.services.storage_service import StorageService
        from app.config import settings

        # Print configuration
        print(f"\n📋 Configuration:")
        print(f"  - GCS Project ID: {settings.gcs_project_id}")
        print(f"  - Documents Bucket: {settings.gcs_bucket_documents}")
        print(f"  - Firebase Project: {settings.firebase_project_id}")
        print(f"  - Firebase Client Email: {settings.firebase_client_email}")
        print(f"  - Private Key Configured: {'Yes' if settings.firebase_private_key else 'No'}")

        # Initialize storage service
        print(f"\n🔧 Initializing StorageService...")
        storage = StorageService()
        print(f"✅ StorageService initialized successfully")

        # Try to generate a test signed URL
        print(f"\n🔑 Testing signed URL generation...")
        test_path = "test-user/test-doc-123/test.pdf"
        try:
            signed_url = storage.generate_signed_upload_url(
                bucket_name=settings.gcs_bucket_documents,
                blob_path=test_path,
                content_type="application/pdf",
                expires_in_minutes=15
            )
            print(f"✅ Signed URL generated successfully")
            print(f"   URL length: {len(signed_url)} characters")
            print(f"   URL starts with: {signed_url[:50]}...")
            return True
        except Exception as e:
            print(f"❌ Failed to generate signed URL")
            print(f"   Error: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"\n📜 Full traceback:")
            traceback.print_exc()
            return False

    except Exception as e:
        print(f"❌ Failed to initialize StorageService")
        print(f"   Error: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"\n📜 Full traceback:")
        traceback.print_exc()
        return False


def test_upload_endpoint():
    """Test the upload-url endpoint directly."""
    print("\n" + "="*60)
    print("Testing /api/documents/upload-url endpoint...")
    print("="*60)

    try:
        from app.api.documents import generate_upload_url
        from app.models.requests import UploadUrlRequest
        from app.services.storage_service import get_storage_service

        # Create test request
        request = UploadUrlRequest(
            filename="test-file.pdf",
            content_type="application/pdf"
        )

        # Mock user
        mock_user = {
            'user_id': 'test-user-123',
            'email': 'test@example.com'
        }

        # Call endpoint logic directly
        print(f"\n📤 Calling generate_upload_url...")
        print(f"   Filename: {request.filename}")
        print(f"   Content-Type: {request.content_type}")
        print(f"   User: {mock_user['email']}")

        import asyncio
        response = asyncio.run(generate_upload_url(
            request=request,
            current_user=mock_user,
            storage=get_storage_service()
        ))

        print(f"\n✅ Endpoint call successful!")
        print(f"   Document ID: {response.document_id}")
        print(f"   GCS Path: {response.gcs_path}")
        print(f"   Upload URL length: {len(response.upload_url)}")
        print(f"   Expires at: {response.expires_at}")
        return True

    except Exception as e:
        print(f"\n❌ Endpoint call failed")
        print(f"   Error: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"\n📜 Full traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 MedBillDozer Local Upload Diagnostics")
    print("=" * 60)

    # Test 1: StorageService initialization
    storage_ok = test_storage_service()

    # Test 2: Upload endpoint
    if storage_ok:
        endpoint_ok = test_upload_endpoint()
    else:
        print("\n⚠️  Skipping endpoint test due to StorageService failure")
        endpoint_ok = False

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"  StorageService: {'✅ PASS' if storage_ok else '❌ FAIL'}")
    print(f"  Upload Endpoint: {'✅ PASS' if endpoint_ok else '❌ FAIL'}")

    if not storage_ok or not endpoint_ok:
        print("\n💡 Next Steps:")
        if not storage_ok:
            print("  1. Check that FIREBASE_PRIVATE_KEY is correctly formatted in backend/.env")
            print("  2. Verify GCS_PROJECT_ID matches your Firebase project")
            print("  3. Ensure service account has 'Storage Object Admin' role")
            print("  4. Check if you have local gcloud credentials: gcloud auth application-default login")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed! The upload system is working correctly.")
        sys.exit(0)
