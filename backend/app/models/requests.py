"""Request/Response Pydantic models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

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
        None, description="Document type (medical_bill, dental_bill, insurance_eob, etc.)"
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


class DocumentActionUpdate(BaseModel):
    """Update document action status."""

    action: Optional[str] = Field(
        None, description="Action status: ignored, followup, resolved, or null to clear"
    )
    action_notes: Optional[str] = Field(None, description="Notes for this action")

    @field_validator("action")
    @classmethod
    def validate_action(cls, v):
        if v is not None and v not in ["ignored", "followup", "resolved"]:
            raise ValueError("Action must be one of: ignored, followup, resolved")
        return v


class DocumentMetadataUpdate(BaseModel):
    """Update document metadata (profile info, amounts, etc)."""

    profile_id: Optional[str] = Field(None, description="Profile ID (PH-001, DEP-001, etc.)")
    profile_name: Optional[str] = Field(None, description="Profile name (e.g., John Sample)")
    profile_type: Optional[str] = Field(None, description="policyholder or dependent")
    provider_name: Optional[str] = Field(None, description="Provider name")
    service_date: Optional[str] = Field(None, description="Service date (YYYY-MM-DD)")
    patient_responsibility_amount: Optional[float] = Field(None, description="Amount patient owes")


class EnrichedDocumentResponse(DocumentResponse):
    """Document response with profile and action data."""

    # Profile fields from metadata
    profile_id: Optional[str] = None
    profile_name: Optional[str] = None
    profile_type: Optional[str] = None
    provider_name: Optional[str] = None
    service_date: Optional[str] = None
    patient_responsibility_amount: Optional[float] = None

    # Action tracking fields
    action: Optional[str] = None
    action_notes: Optional[str] = None
    action_date: Optional[datetime] = None
    action_updated_by: Optional[str] = None

    # Computed fields
    flagged: bool = False
    high_confidence_issues_count: int = 0
    total_issues_count: int = 0


class DocumentActionStatistics(BaseModel):
    """Statistics on document actions for a profile."""

    user_id: str
    profile_id: Optional[str] = None
    profile_name: Optional[str] = None
    total_documents: int
    followup_count: int
    ignored_count: int
    resolved_count: int
    pending_count: int
    completed_count: int
    followup_amount: Optional[float] = 0.0
    resolved_amount: Optional[float] = 0.0
    total_amount: Optional[float] = 0.0
    last_action_date: Optional[datetime] = None
    last_upload_date: Optional[datetime] = None


# ============================================================================
# ANALYSIS
# ============================================================================


class AnalysisProvider(str, Enum):
    """Allowed analysis providers."""

    MEDGEMMA_ENSEMBLE = "medgemma-ensemble"
    OPENAI = "openai"
    GEMINI = "gemini"
    SMART = "smart"


class AnalyzeRequest(BaseModel):
    """Request to analyze documents."""

    document_ids: List[str] = Field(..., description="List of document IDs to analyze")
    provider: Optional[AnalysisProvider] = Field(
        default=AnalysisProvider.MEDGEMMA_ENSEMBLE,
        description="AI provider (medgemma-ensemble, openai, gemini, smart)",
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
    results: Optional[list] = None  # List of document results with progress
    coverage_matrix: Optional[dict] = None
    total_savings_detected: Optional[float] = None
    issues_count: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None


class BulkAnalyzeRequest(BaseModel):
    """Request to analyze multiple documents in bulk."""

    document_ids: List[str] = Field(..., description="List of document IDs to analyze")
    profile_id: Optional[str] = Field(None, description="Filter by profile ID (optional)")
    exclude_flagged: bool = Field(True, description="Exclude flagged documents from analysis")
    provider: Optional[AnalysisProvider] = Field(
        default=AnalysisProvider.MEDGEMMA_ENSEMBLE, description="AI provider to use for analysis"
    )


class BulkAnalyzeResponse(BaseModel):
    """Response from bulk analysis request."""

    analysis_id: str
    status: str
    documents_submitted: int
    documents_excluded: int = 0
    excluded_reason: Optional[str] = None
    estimated_completion: datetime


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
