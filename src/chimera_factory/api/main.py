"""
FastAPI application for Project Chimera API.

Reference: specs/technical.md, specs/api/orchestrator.yaml
"""

import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from dotenv import load_dotenv

from chimera_factory.api.routers import trends, content, engagement, agents, campaigns
from chimera_factory.api.models import APIResponse, ErrorResponse
from chimera_factory.exceptions import ChimeraError
from chimera_factory.utils.logging import setup_logger

# Load environment variables
load_dotenv()

logger = setup_logger(__name__)

# Get CORS origins from environment
cors_origins = os.getenv("CORS_ORIGINS", "*")
if cors_origins == "*":
    allow_origins = ["*"]
else:
    # Split comma-separated origins
    allow_origins = [origin.strip() for origin in cors_origins.split(",")]

# Create FastAPI app
app = FastAPI(
    title="Chimera Orchestrator API",
    version="0.1.0",
    description="API for managing the Chimera Agent fleet",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trends.router, prefix="/api/v1/trends", tags=["trends"])
app.include_router(content.router, prefix="/api/v1/content", tags=["content"])
app.include_router(engagement.router, prefix="/api/v1/engagement", tags=["engagement"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["campaigns"])


@app.exception_handler(ChimeraError)
async def chimera_error_handler(request: Request, exc: ChimeraError):
    """Handle Chimera-specific errors."""
    logger.error(f"Chimera error: {exc.message}", extra={"code": exc.code, "retryable": exc.retryable})
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if exc.code == "VALIDATION_ERROR":
        status_code = status.HTTP_400_BAD_REQUEST
    elif exc.code == "RATE_LIMIT_EXCEEDED":
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
    elif exc.code == "NOT_FOUND":
        status_code = status.HTTP_404_NOT_FOUND
    
    return JSONResponse(
        status_code=status_code,
        content=APIResponse(
            success=False,
            data=None,
            error=ErrorResponse(
                code=exc.code or "INTERNAL_ERROR",
                message=exc.message,
                details={"retryable": exc.retryable}
            ).model_dump(),
            timestamp=datetime.now()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.exception(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse(
            success=False,
            data=None,
            error=ErrorResponse(
                code="INTERNAL_ERROR",
                message="An internal server error occurred",
                details={"type": type(exc).__name__}
            ).model_dump(),
            timestamp=datetime.now()
        ).model_dump()
    )


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return APIResponse(
        success=True,
        data={"status": "healthy", "version": "0.1.0"},
        error=None,
        timestamp=datetime.now()
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Chimera Orchestrator API",
        "version": "0.1.0",
        "docs": "/api/v1/docs"
    }
