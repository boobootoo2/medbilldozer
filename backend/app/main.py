"""FastAPI application entry point for MedBillDozer API."""
import sys
from pathlib import Path

# Add paths for medbilldozer modules
app_root = Path(__file__).parent.parent  # /app
src_dir = app_root / "src"  # /app/src
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
    print(f"✅ Added {src_dir} to Python path")
if str(app_root) not in sys.path:
    sys.path.insert(0, str(app_root))
    print(f"✅ Added {app_root} to Python path")
print(f"🐍 Python path: {sys.path[:5]}...")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.api import auth, documents, analyze, profile, issues
from app.utils import setup_logging, get_logger
from app.middleware.logging_middleware import LoggingMiddleware
# from app.middleware.auth_middleware import AuthMiddleware

# Setup structured logging
setup_logging(json_logs=False)  # Set to True for production JSON logs
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Initialize providers
    logger.info("🚀 Initializing MedBillDozer providers...")
    try:
        from medbilldozer.providers.provider_registry import register_providers, ProviderRegistry
        register_providers()
        providers = list(ProviderRegistry.list())
        logger.info(f"✅ Registered providers: {providers}")
    except Exception as e:
        logger.warning(f"⚠️  Warning: Could not initialize provider registry: {e}")

    yield

    # Shutdown
    logger.info("👋 Shutting down MedBillDozer API...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered medical billing analysis API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    redirect_slashes=False  # Prevent 307 redirects that lose Authorization headers
)

# Request/Response logging middleware
app.add_middleware(LoggingMiddleware)

# CORS middleware for React frontend
origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID"],  # Expose correlation ID to frontend
)

# Custom authentication middleware
# app.add_middleware(AuthMiddleware)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "api_version": settings.app_version,
        "environment": "production" if not settings.debug else "development"
    }


# Register API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["Analysis"])
app.include_router(issues.router, prefix="/api/issues", tags=["Issues"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    from app.utils import get_correlation_id

    correlation_id = get_correlation_id()
    logger.exception(f"Unhandled exception in request: {type(exc).__name__}")

    error_response = {
        "error": "Internal server error",
        "message": str(exc) if settings.debug else "An unexpected error occurred",
        "correlation_id": correlation_id,
        "path": str(request.url.path),
        "method": request.method
    }

    if settings.debug:
        error_response["exception_type"] = type(exc).__name__

    return JSONResponse(
        status_code=500,
        content=error_response
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug
    )
