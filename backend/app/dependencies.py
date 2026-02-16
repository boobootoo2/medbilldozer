"""FastAPI dependencies for dependency injection."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth_service import get_auth_service, AuthService
from app.services.storage_service import get_storage_service, StorageService
from app.services.db_service import get_db_service, DBService
from app.services.analysis_service import get_analysis_service, AnalysisService

# HTTP Bearer token security
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    db_service: DBService = Depends(get_db_service)
) -> dict:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Authorization credentials
        auth_service: Auth service dependency
        db_service: Database service dependency

    Returns:
        User dict with user_id, email, etc.

    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Verify JWT access token
        token = credentials.credentials
        payload = auth_service.verify_access_token(token)

        # Get user from database
        firebase_uid = payload.get("firebase_uid")
        if not firebase_uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        user = await db_service.get_user_by_firebase_uid(firebase_uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}"
        )


# Service dependencies (already singletons, but using Depends pattern)
def get_auth_service_dep() -> AuthService:
    """Get auth service dependency."""
    return get_auth_service()


def get_storage_service_dep() -> StorageService:
    """Get storage service dependency."""
    return get_storage_service()


def get_db_service_dep() -> DBService:
    """Get database service dependency."""
    return get_db_service()


def get_analysis_service_dep() -> AnalysisService:
    """Get analysis service dependency."""
    return get_analysis_service()
