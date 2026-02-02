"""
Vercel serverless function entry point for FastAPI backend.

This file creates a modified FastAPI app without lifespan events for serverless.
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import sys
import logging

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the current directory to Python path to ensure imports work
sys.path.insert(0, os.path.dirname(__file__))

logger.info("Starting Vercel serverless function...")

from app.routers import auth, todos

# Create FastAPI application WITHOUT lifespan for serverless
app = FastAPI(
    title="Todo API",
    version="1.0.0",
    description="Secure REST API for todo management with JWT authentication",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
cors_origins_str = os.getenv("CORS_ORIGINS", "*")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

# Log CORS origins for debugging
logger.info(f"CORS Origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Environment check endpoint (for debugging)
@app.get("/debug/env", tags=["Debug"])
async def check_env():
    """Check if critical environment variables are set."""
    return {
        "database_url_set": bool(os.getenv("DATABASE_URL")),
        "cors_origins": os.getenv("CORS_ORIGINS", "NOT_SET"),
    }

# Include routers
logger.info("Including routers...")
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
logger.info("✓ Auth router included at /api/auth")
app.include_router(todos.router, prefix="/api/todos", tags=["Todos"])
logger.info("✓ Todos router included at /api/todos")

logger.info("All routers loaded successfully!")

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Todo API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
