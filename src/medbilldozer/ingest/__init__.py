"""Ingestion API module.

Provides programmatic API-style interface for healthcare data ingestion.
DEMO ONLY - Not deployed, no real networking or authentication.
"""

from .api import (
    # Main API functions
    ingest_document,
    list_imports,
    get_normalized_data,
    get_import_status,

    # Schemas
    IngestRequest,
    IngestResponse,
    ImportListResponse,
    NormalizedDataResponse,
    ImportStatusResponse,

    # Storage interface
    InMemoryStorage,
)

__all__ = [
    # API functions
    'ingest_document',
    'list_imports',
    'get_normalized_data',
    'get_import_status',

    # Schemas
    'IngestRequest',
    'IngestResponse',
    'ImportListResponse',
    'NormalizedDataResponse',
    'ImportStatusResponse',

    # Storage
    'InMemoryStorage',
]

