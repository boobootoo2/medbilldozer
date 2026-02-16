"""Firebase Authentication service."""
import firebase_admin
from firebase_admin import credentials, auth
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config import settings


class AuthService:
    """Handles Firebase authentication and JWT token management."""

    def __init__(self):
        """Initialize Firebase Admin SDK."""
        # Initialize Firebase Admin (only once)
        if not firebase_admin._apps:
            # Use default credentials or service account
            try:
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize Firebase Admin: {e}")

    async def verify_firebase_token(self, id_token: str) -> dict:
        """
        Verify Firebase ID token.

        Args:
            id_token: Firebase ID token from client

        Returns:
            Decoded token with user info

        Raises:
            Exception if token is invalid
        """
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            raise Exception(f"Invalid Firebase token: {e}")

    def create_access_token(self, user_data: dict) -> str:
        """
        Create JWT access token.

        Args:
            user_data: User information to encode

        Returns:
            JWT access token
        """
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
        to_encode = {
            **user_data,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt

    def create_refresh_token(self, user_data: dict) -> str:
        """
        Create JWT refresh token (longer expiry).

        Args:
            user_data: User information to encode

        Returns:
            JWT refresh token
        """
        expire = datetime.utcnow() + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )
        to_encode = {
            "sub": user_data.get("user_id"),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt

    def verify_access_token(self, token: str) -> dict:
        """
        Verify JWT access token.

        Args:
            token: JWT token to verify

        Returns:
            Decoded token payload

        Raises:
            JWTError if token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError as e:
            raise Exception(f"Invalid access token: {e}")

    def verify_refresh_token(self, token: str) -> dict:
        """
        Verify JWT refresh token.

        Args:
            token: JWT refresh token to verify

        Returns:
            Decoded token payload

        Raises:
            JWTError if token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            if payload.get("type") != "refresh":
                raise Exception("Not a refresh token")
            return payload
        except JWTError as e:
            raise Exception(f"Invalid refresh token: {e}")


# Singleton instance
_auth_service: AuthService | None = None


def get_auth_service() -> AuthService:
    """Get or create AuthService singleton."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
