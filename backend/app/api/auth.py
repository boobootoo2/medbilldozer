"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from datetime import datetime, timedelta

from app.models.requests import LoginRequest, LoginResponse, RefreshTokenRequest
from app.services.auth_service import AuthService, get_auth_service
from app.services.db_service import DBService, get_db_service

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    db_service: DBService = Depends(get_db_service)
):
    """
    Login with Firebase ID token.

    1. Client logs in with Firebase (Google/GitHub OAuth)
    2. Client sends Firebase ID token to this endpoint
    3. Backend verifies token with Firebase Admin SDK
    4. Backend creates/updates user in database
    5. Backend returns JWT access token + sets refresh token cookie
    """
    try:
        # Verify Firebase token
        firebase_user = await auth_service.verify_firebase_token(
            request.firebase_id_token
        )

        # Extract user info
        firebase_uid = firebase_user['uid']
        email = firebase_user.get('email')
        display_name = firebase_user.get('name')
        avatar_url = firebase_user.get('picture')

        # Create or update user in database
        user = await db_service.create_or_update_user(
            firebase_uid=firebase_uid,
            email=email,
            display_name=display_name,
            avatar_url=avatar_url
        )

        # Create JWT access token
        user_data = {
            "user_id": str(user['user_id']),
            "firebase_uid": firebase_uid,
            "email": email
        }
        access_token = auth_service.create_access_token(user_data)
        refresh_token = auth_service.create_refresh_token(user_data)

        # Set refresh token in httpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,  # HTTPS only
            samesite="strict",
            max_age=7 * 24 * 60 * 60  # 7 days
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "user_id": str(user['user_id']),
                "email": email,
                "display_name": display_name,
                "avatar_url": avatar_url
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
    db_service: DBService = Depends(get_db_service)
):
    """
    Refresh access token using refresh token.

    Used when access token expires (after 1 hour).
    """
    try:
        # Verify refresh token
        payload = auth_service.verify_refresh_token(request.refresh_token)
        user_id = payload.get("sub")

        # Get user from database
        user = await db_service.get_user_by_firebase_uid(payload.get("firebase_uid"))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Create new access token
        user_data = {
            "user_id": str(user['user_id']),
            "firebase_uid": user['firebase_uid'],
            "email": user['email']
        }
        new_access_token = auth_service.create_access_token(user_data)

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout")
async def logout(response: Response):
    """
    Logout user by clearing refresh token cookie.
    """
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}
