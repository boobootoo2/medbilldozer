"""Application configuration using Pydantic settings."""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # API Configuration
    app_name: str = "MedBillDozer API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server Configuration
    server_host: str = "127.0.0.1"  # Default to localhost for security; use 0.0.0.0 for containers
    server_port: int = 8080

    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # Firebase Auth
    firebase_project_id: str
    firebase_private_key: Optional[str] = None
    firebase_client_email: Optional[str] = None

    # Google Cloud Storage
    gcs_project_id: str
    gcs_bucket_documents: str = "medbilldozer-documents"
    gcs_bucket_clinical_images: str = "medbilldozer-clinical"

    # Supabase - supports both beta and production env vars
    supabase_url: str = Field(
        default_factory=lambda: os.getenv("SUPABASE_BETA_URL") or os.getenv("SUPABASE_URL", "")
    )
    supabase_service_role_key: str = Field(
        default_factory=lambda: os.getenv("SUPABASE_BETA_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    )

    # AI Providers
    openai_api_key: str
    gemini_api_key: Optional[str] = None
    hf_api_token: Optional[str] = None

    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
