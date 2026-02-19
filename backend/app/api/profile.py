"""User profile API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.requests import ProfileResponse, ProfileUpdateRequest
from app.services.db_service import DBService, get_db_service
from app.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user profile.
    """
    return ProfileResponse(
        user_id=str(current_user['user_id']),
        email=current_user['email'],
        display_name=current_user.get('display_name'),
        avatar_url=current_user.get('avatar_url'),
        created_at=current_user['created_at'],
        last_login_at=current_user.get('last_login_at')
    )


@router.put("/")
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: DBService = Depends(get_db_service)
):
    """
    Update user profile.
    """
    try:
        # Update user profile
        await db.create_or_update_user(
            firebase_uid=current_user['firebase_uid'],
            email=current_user['email'],
            display_name=request.display_name or current_user.get('display_name'),
            avatar_url=request.avatar_url or current_user.get('avatar_url')
        )

        return {"message": "Profile updated successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
