"""Logging middleware for request/response tracking."""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logger import get_logger, set_correlation_id, log_with_context

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses with correlation IDs."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        # Generate or extract correlation ID
        correlation_id = request.headers.get('X-Correlation-ID') or str(uuid.uuid4())
        set_correlation_id(correlation_id)

        # Start timer
        start_time = time.time()

        # Extract request details
        method = request.method
        path = request.url.path
        query_params = str(request.url.query) if request.url.query else None
        client_ip = request.client.host if request.client else None

        # Log incoming request
        log_with_context(
            logger,
            20,  # INFO level
            f"→ Incoming request: {method} {path}",
            method=method,
            path=path,
            query_params=query_params,
            client_ip=client_ip
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)

            # Log response
            log_with_context(
                logger,
                20,  # INFO level
                f"← Response: {method} {path} → {response.status_code}",
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=duration_ms
            )

            # Add correlation ID to response headers
            response.headers['X-Correlation-ID'] = correlation_id

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)

            # Log error
            log_with_context(
                logger,
                40,  # ERROR level
                f"✗ Request failed: {method} {path} → {type(e).__name__}: {str(e)}",
                method=method,
                path=path,
                duration_ms=duration_ms
            )
            logger.exception("Request processing failed")

            # Re-raise the exception
            raise
