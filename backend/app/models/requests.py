"""Request/Response Pydantic models."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ============================================================================
# AUTH
# ============================================================================

class LoginRequest(BaseModel):
    """Firebase login request."""
    firebase_id_token: str = Field(..., description="Firebase ID token from client")


class LoginResponse(BaseModel):
    """Login response with JWT tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


# ============================================================================
# DOCUMENTS
# ============================================================================

class UploadUrlRequest(BaseModel):
    """Request for signed upload URL."""
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    document_type: Optional[str] = Field(
        None,
        description="Document type (medical_bill, dental_bill, insurance_eob, etc.)"
    )


class UploadUrlResponse(BaseModel):
    """Response with signed upload URL."""
    document_id: str
    upload_url: str
    gcs_path: str
    expires_at: datetime


class ConfirmUploadRequest(BaseModel):
    """Confirm document upload."""
    document_id: str
    filename: str
    gcs_path: str
    size_bytes: int
    document_type: Optional[str] = None


class DocumentResponse(BaseModel):
    """Document metadata response."""
    document_id: str
    filename: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime
    status: str
    document_type: Optional[str] = None
    download_url: Optional[str] = None


class DocumentListResponse(BaseModel):
    """List of documents."""
    documents: List[DocumentResponse]
    total: int
    offset: int
    limit: int


# ============================================================================
# ANALYSIS
# ============================================================================

class AnalyzeRequest(BaseModel):
    """Request to analyze documents."""
    document_ids: List[str] = Field(..., description="List of document IDs to analyze")
    provider: Optional[str] = Field(
        "medgemma-ensemble",
        description="AI provider (medgemma-ensemble, openai, gemini, smart)"
    )


class AnalyzeResponse(BaseModel):
    """Analysis submission response."""
    analysis_id: str
    status: str
    estimated_completion: datetime


class AnalysisResultResponse(BaseModel):
    """Full analysis results."""
    analysis_id: str
    status: str
    provider: str
    results: Optional[dict] = None
    coverage_matrix: Optional[dict] = None
    total_savings_detected: Optional[float] = None
    issues_count: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None


# ============================================================================
# PROFILE
# ============================================================================

class ProfileResponse(BaseModel):
    """User profile response."""
    user_id: str
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None


class ProfileUpdateRequest(BaseModel):
    """Update user profile."""
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
