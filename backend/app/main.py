"""FastAPI application entry point for MedBillDozer API."""
import sys
from pathlib import Path

# Add parent directory to Python path to import medbilldozer modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.api import auth, documents, analyze, profile
# from app.middleware.auth_middleware import AuthMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Initialize providers
    print("🚀 Initializing MedBillDozer providers...")
    try:
        from src.medbilldozer.providers.provider_registry import get_provider_registry
        registry = get_provider_registry()
        print(f"✅ Registered providers: {list(registry.list_providers())}")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize provider registry: {e}")

    yield

    # Shutdown
    print("👋 Shutting down MedBillDozer API...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered medical billing analysis API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware for React frontend
origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.debug
    )
