"""Demo-Only Healthcare Data Ingestion API

This module provides API-style functions for ingesting healthcare data
from fictional entities and retrieving normalized results.

IMPORTANT: This is a DEMO-ONLY interface with no real networking,
authentication, or HIPAA compliance. It's designed to demonstrate
how a Plaid-like healthcare data connector API might work.

Future Deployment: These functions could be exposed via FastAPI:
    - POST /api/v1/ingest/document -> ingest_document()
    - GET /api/v1/imports?user_id=xxx -> list_imports()
    - GET /api/v1/data?user_id=xxx -> get_normalized_data()
    - GET /api/v1/imports/{job_id} -> get_import_status()

Authentication (Future): Would use OAuth 2.0 or API keys
Storage (Current): In-memory dictionary (replace with database in production)
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime
import uuid

# Import our existing ingestion logic
from _modules.data.health_data_ingestion import (
    import_sample_data,
    generate_fake_document,
    generate_line_items_from_insurance,
    generate_line_items_from_provider,
)
from _modules.data.fictional_entities import (
    get_all_fictional_entities,
    get_entity_by_id,
)

# Type definitions for entity types
EntityType = Literal["insurance", "provider"]
ImportStatus = Literal["pending", "processing", "completed", "failed"]


# ==============================================================================
# REQUEST & RESPONSE SCHEMAS
# ==============================================================================
# Note: Using dataclasses for simplicity. In FastAPI, these would be
# Pydantic models for automatic validation and OpenAPI documentation.


@dataclass


class IngestRequest:
    """Request payload for document ingestion.

    This represents the data a client application would send to ingest
    healthcare data from a connected entity.

    Future FastAPI equivalent:
        class IngestRequest(BaseModel):
            user_id: str
            entity_type: Literal["insurance", "provider"]
            entity_id: str
            raw_text: Optional[str] = None
            metadata: Dict[str, Any] = Field(default_factory=dict)
    """
    user_id: str
    entity_type: EntityType
    entity_id: str
    raw_text: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Optional parameters
    num_line_items: Optional[int] = None

    def validate(self) -> List[str]:
        """Validate request payload.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        if not self.user_id:
            errors.append("user_id is required")

        if self.entity_type not in ["insurance", "provider"]:
            errors.append(f"entity_type must be 'insurance' or 'provider', got '{self.entity_type}'")

        if not self.entity_id:
            errors.append("entity_id is required")

        if self.num_line_items is not None and self.num_line_items <= 0:
            errors.append("num_line_items must be positive")

        return errors


@dataclass


class IngestResponse:
    """Response from document ingestion.

    Future FastAPI equivalent:
        class IngestResponse(BaseModel):
            success: bool
            job_id: str
            message: str
            documents_created: int
            line_items_created: int
            timestamp: str
    """
    success: bool
    job_id: str
    message: str
    documents_created: int
    line_items_created: int
    timestamp: str
    errors: List[str] = field(default_factory=list)


@dataclass


class ImportSummary:
    """Summary of an import job.

    Used in list_imports() response.
    """
    job_id: str
    user_id: str
    entity_type: str
    entity_id: str
    entity_name: str
    status: ImportStatus
    documents_count: int
    line_items_count: int
    created_at: str
    completed_at: Optional[str] = None


@dataclass


class ImportListResponse:
    """Response from list_imports().

    Future FastAPI equivalent:
        class ImportListResponse(BaseModel):
            success: bool
            user_id: str
            total_imports: int
            imports: List[ImportSummary]
    """
    success: bool
    user_id: str
    total_imports: int
    imports: List[ImportSummary]


@dataclass


class NormalizedDataResponse:
    """Response from get_normalized_data().

    Returns all normalized line items for a user.

    Future FastAPI equivalent:
        class NormalizedDataResponse(BaseModel):
            success: bool
            user_id: str
            total_line_items: int
            line_items: List[Dict[str, Any]]
            metadata: Dict[str, Any]
    """
    success: bool
    user_id: str
    total_line_items: int
    line_items: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass


class ImportStatusResponse:
    """Response from get_import_status().

    Returns detailed status of a specific import job.

    Future FastAPI equivalent:
        class ImportStatusResponse(BaseModel):
            success: bool
            job_id: str
            status: ImportStatus
            import_job: Dict[str, Any]
    """
    success: bool
    job_id: str
    status: ImportStatus
    import_job: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


# ==============================================================================
# IN-MEMORY STORAGE
# ==============================================================================
# NOTE: In production, this would be replaced with a database (PostgreSQL,
# MongoDB, etc.) or a persistent cache (Redis). This is demo-only storage.


class InMemoryStorage:
    """In-memory storage for import jobs.

    Thread-safe operations would be needed in production.
    In a real deployment, this would be:
    - SQLAlchemy models + PostgreSQL
    - MongoDB collections
    - Redis cache for session data
    """

    def __init__(self):
        # user_id -> list of import jobs
        self._imports_by_user: Dict[str, List[Dict[str, Any]]] = {}

        # job_id -> import job
        self._imports_by_job_id: Dict[str, Dict[str, Any]] = {}

    def store_import(self, user_id: str, import_job: Dict[str, Any]) -> None:
        """Store an import job."""
        job_id = import_job['job_id']

        # Store by job ID
        self._imports_by_job_id[job_id] = import_job

        # Store by user ID
        if user_id not in self._imports_by_user:
            self._imports_by_user[user_id] = []
        self._imports_by_user[user_id].append(import_job)

    def get_imports_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all imports for a user."""
        return self._imports_by_user.get(user_id, [])

    def get_import_by_job_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific import job by ID."""
        return self._imports_by_job_id.get(job_id)

    def get_all_line_items_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all line items across all imports for a user."""
        imports = self.get_imports_by_user(user_id)
        all_items = []
        for import_job in imports:
            all_items.extend(import_job.get('line_items', []))
        return all_items

    def clear(self) -> None:
        """Clear all storage (for testing)."""
        self._imports_by_user.clear()
        self._imports_by_job_id.clear()


# Global storage instance (would be dependency-injected in FastAPI)
_storage = InMemoryStorage()


# ==============================================================================
# API FUNCTIONS
# ==============================================================================


def ingest_document(payload: Dict[str, Any]) -> IngestResponse:
    """Ingest a healthcare document and normalize the data.

    This is the main ingestion endpoint. It accepts a payload with entity
    information and generates normalized line items using the existing
    ingestion logic.

    Args:
        payload: Dictionary matching IngestRequest schema

    Returns:
        IngestResponse with job_id and results

    Example:
        >>> payload = {
        ...     "user_id": "demo_user_123",
        ...     "entity_type": "insurance",
        ...     "entity_id": "demo_ins_001",
        ...     "metadata": {"source": "web_app"}
        ... }
        >>> response = ingest_document(payload)
        >>> response.success
        True
        >>> response.job_id
        'uuid-...'

    Future FastAPI deployment:
        @app.post("/api/v1/ingest/document", response_model=IngestResponse)
        async def api_ingest_document(request: IngestRequest):
            return ingest_document(request.dict())
    """
    # Parse request
    try:
        request = IngestRequest(**payload)
    except TypeError as e:
        return IngestResponse(
            success=False,
            job_id="",
            message="Invalid request payload",
            documents_created=0,
            line_items_created=0,
            timestamp=datetime.utcnow().isoformat(),
            errors=[str(e)]
        )

    # Validate request
    errors = request.validate()
    if errors:
        return IngestResponse(
            success=False,
            job_id="",
            message="Validation failed",
            documents_created=0,
            line_items_created=0,
            timestamp=datetime.utcnow().isoformat(),
            errors=errors
        )

    # Get fictional entities (in production, this would query a provider catalog)
    entities = get_all_fictional_entities()

    # Find the entity
    entity_list = entities['insurance'] if request.entity_type == 'insurance' else entities['providers']
    entity = get_entity_by_id(request.entity_id, entity_list)

    if not entity:
        return IngestResponse(
            success=False,
            job_id="",
            message=f"Entity not found: {request.entity_id}",
            documents_created=0,
            line_items_created=0,
            timestamp=datetime.utcnow().isoformat(),
            errors=[f"Entity {request.entity_id} of type {request.entity_type} not found"]
        )

    # Perform ingestion (reuse existing logic from Stage 4)
    try:
        import_job = import_sample_data(
            entity,
            num_line_items=request.num_line_items
        )

        # Add user_id and metadata to import job
        import_job['user_id'] = request.user_id
        import_job['entity_id'] = request.entity_id
        import_job['entity_name'] = entity.get('name', 'Unknown')
        import_job['metadata'] = request.metadata

        # Store in memory (in production, save to database)
        _storage.store_import(request.user_id, import_job)

        return IngestResponse(
            success=True,
            job_id=import_job['job_id'],
            message=f"Successfully ingested data from {entity.get('name', 'Unknown')}",
            documents_created=len(import_job.get('documents', [])),
            line_items_created=len(import_job.get('line_items', [])),
            timestamp=import_job['created_at']
        )

    except Exception as e:
        return IngestResponse(
            success=False,
            job_id="",
            message="Ingestion failed",
            documents_created=0,
            line_items_created=0,
            timestamp=datetime.utcnow().isoformat(),
            errors=[str(e)]
        )


def list_imports(user_id: str) -> ImportListResponse:
    """List all import jobs for a user.

    Args:
        user_id: User identifier

    Returns:
        ImportListResponse with list of import summaries

    Example:
        >>> response = list_imports("demo_user_123")
        >>> response.total_imports
        3
        >>> response.imports[0].entity_name
        'Beacon Life (DEMO)'

    Future FastAPI deployment:
        @app.get("/api/v1/imports", response_model=ImportListResponse)
        async def api_list_imports(user_id: str):
            return list_imports(user_id)
    """
    imports = _storage.get_imports_by_user(user_id)

    # Build summaries
    summaries = []
    for import_job in imports:
        summary = ImportSummary(
            job_id=import_job['job_id'],
            user_id=user_id,
            entity_type=import_job['source_type'],
            entity_id=import_job.get('entity_id', 'unknown'),
            entity_name=import_job.get('entity_name', 'Unknown'),
            status=import_job['status'],
            documents_count=len(import_job.get('documents', [])),
            line_items_count=len(import_job.get('line_items', [])),
            created_at=import_job['created_at'],
            completed_at=import_job.get('completed_at')
        )
        summaries.append(summary)

    return ImportListResponse(
        success=True,
        user_id=user_id,
        total_imports=len(summaries),
        imports=summaries
    )


def get_normalized_data(user_id: str, job_id: Optional[str] = None) -> NormalizedDataResponse:
    """Get normalized line items for a user.

    If job_id is provided, returns line items for that specific job.
    Otherwise, returns all line items across all jobs.

    Args:
        user_id: User identifier
        job_id: Optional import job ID to filter by

    Returns:
        NormalizedDataResponse with line items

    Example:
        >>> response = get_normalized_data("demo_user_123")
        >>> response.total_line_items
        15
        >>> response.line_items[0]['procedure_code']
        '99213'

    Future FastAPI deployment:
        @app.get("/api/v1/data", response_model=NormalizedDataResponse)
        async def api_get_normalized_data(
            user_id: str,
            job_id: Optional[str] = None
        ):
            return get_normalized_data(user_id, job_id)
    """
    if job_id:
        # Get line items for specific job
        import_job = _storage.get_import_by_job_id(job_id)
        if not import_job:
            return NormalizedDataResponse(
                success=False,
                user_id=user_id,
                total_line_items=0,
                line_items=[],
                metadata={"error": f"Import job {job_id} not found"}
            )

        if import_job.get('user_id') != user_id:
            return NormalizedDataResponse(
                success=False,
                user_id=user_id,
                total_line_items=0,
                line_items=[],
                metadata={"error": "Access denied"}
            )

        line_items = import_job.get('line_items', [])
    else:
        # Get all line items for user
        line_items = _storage.get_all_line_items_by_user(user_id)

    # Calculate metadata
    total_billed = sum(item.get('billed_amount', 0) for item in line_items)
    total_patient_resp = sum(item.get('patient_responsibility', 0) for item in line_items)

    unique_providers = set(item.get('provider_name', 'Unknown') for item in line_items)
    unique_procedures = set(item.get('procedure_code', 'Unknown') for item in line_items)

    metadata = {
        "total_billed_amount": round(total_billed, 2),
        "total_patient_responsibility": round(total_patient_resp, 2),
        "unique_providers": len(unique_providers),
        "unique_procedure_codes": len(unique_procedures),
        "date_range": {
            "earliest": min((item.get('service_date', '') for item in line_items), default=''),
            "latest": max((item.get('service_date', '') for item in line_items), default='')
        }
    }

    return NormalizedDataResponse(
        success=True,
        user_id=user_id,
        total_line_items=len(line_items),
        line_items=line_items,
        metadata=metadata
    )


def get_import_status(job_id: str) -> ImportStatusResponse:
    """Get status of a specific import job.

    Args:
        job_id: Import job identifier

    Returns:
        ImportStatusResponse with job details

    Example:
        >>> response = get_import_status("uuid-...")
        >>> response.status
        'completed'
        >>> response.import_job['line_items_count']
        5

    Future FastAPI deployment:
        @app.get("/api/v1/imports/{job_id}", response_model=ImportStatusResponse)
        async def api_get_import_status(job_id: str):
            return get_import_status(job_id)
    """
    import_job = _storage.get_import_by_job_id(job_id)

    if not import_job:
        return ImportStatusResponse(
            success=False,
            job_id=job_id,
            status="failed",
            error_message=f"Import job {job_id} not found"
        )

    # Build response with sanitized job data
    job_data = {
        "job_id": import_job['job_id'],
        "user_id": import_job.get('user_id', 'unknown'),
        "entity_id": import_job.get('entity_id', 'unknown'),
        "entity_name": import_job.get('entity_name', 'Unknown'),
        "source_type": import_job['source_type'],
        "source_method": import_job['source_method'],
        "status": import_job['status'],
        "documents_count": len(import_job.get('documents', [])),
        "line_items_count": len(import_job.get('line_items', [])),
        "created_at": import_job['created_at'],
        "completed_at": import_job.get('completed_at'),
        "error_message": import_job.get('error_message')
    }

    return ImportStatusResponse(
        success=True,
        job_id=job_id,
        status=import_job['status'],
        import_job=job_data
    )


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================


def clear_storage() -> None:
    """Clear all stored data (for testing).

    In production, this would not be exposed as an API endpoint.
    """
    _storage.clear()


def get_storage_stats() -> Dict[str, Any]:
    """Get statistics about stored data (for debugging).

    Example:
        >>> stats = get_storage_stats()
        >>> stats['total_users']
        5
    """
    return {
        "total_users": len(_storage._imports_by_user),
        "total_import_jobs": len(_storage._imports_by_job_id),
        "users": list(_storage._imports_by_user.keys())
    }


# ==============================================================================
# EXAMPLE FASTAPI APPLICATION (NOT DEPLOYED)
# ==============================================================================

"""
Example FastAPI application structure (DO NOT RUN - reference only):

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Healthcare Data Ingestion API",
    description="Demo-only API for ingesting fictional healthcare data",
    version="1.0.0"
)

# Convert dataclasses to Pydantic models for FastAPI


class IngestRequestModel(BaseModel):
    user_id: str
    entity_type: Literal["insurance", "provider"]
    entity_id: str
    raw_text: Optional[str] = None
    metadata: Dict[str, Any] = {}
    num_line_items: Optional[int] = None


class IngestResponseModel(BaseModel):
    success: bool
    job_id: str
    message: str
    documents_created: int
    line_items_created: int
    timestamp: str
    errors: List[str] = []

@app.post("/api/v1/ingest/document", response_model=IngestResponseModel)
async def api_ingest_document(request: IngestRequestModel):
    '''Ingest a healthcare document.'''
    response = ingest_document(request.dict())
    if not response.success:
        raise HTTPException(status_code=400, detail=response.errors)
    return response

@app.get("/api/v1/imports", response_model=ImportListResponse)
async def api_list_imports(user_id: str):
    '''List all imports for a user.'''
    return list_imports(user_id)

@app.get("/api/v1/data", response_model=NormalizedDataResponse)
async def api_get_normalized_data(
    user_id: str,
    job_id: Optional[str] = None
):
    '''Get normalized line items.'''
    return get_normalized_data(user_id, job_id)

@app.get("/api/v1/imports/{job_id}", response_model=ImportStatusResponse)
async def api_get_import_status(job_id: str):
    '''Get status of a specific import job.'''
    response = get_import_status(job_id)
    if not response.success:
        raise HTTPException(status_code=404, detail=response.error_message)
    return response

# Run with: uvicorn api:app --reload
# API docs at: http://localhost:8000/docs
```

DEPLOYMENT NOTES:
- Would add OAuth 2.0 or API key authentication
- Would use PostgreSQL/MongoDB instead of in-memory storage
- Would add rate limiting (e.g., 100 requests/minute per user)
- Would add logging and monitoring (Sentry, DataDog)
- Would add input sanitization and validation
- Would add CORS middleware for web clients
- Would containerize with Docker
- Would deploy to AWS/GCP/Azure with load balancing
"""

