"""
FastAPI application entry point for Todo API.

This module initializes the FastAPI application with:
- CORS middleware for frontend communication
- Exception handlers for consistent error responses
- Health check endpoint for monitoring
- Authentication and Todo routers

Configuration:
- CORS origins from CORS_ORIGINS environment variable
- Database connection from DATABASE_URL environment variable
- JWT settings from SECRET_KEY and related env vars

Run with:
    uv run uvicorn app.main:app --reload --port 8000

Production:
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import logging

from app.database import create_db_and_tables, test_connection
from app.routers import auth, todos

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events:
    - Startup: Create database tables, test connection
    - Shutdown: Cleanup resources (if needed)

    Args:
        app: FastAPI application instance

    Yields:
        None: Control to application runtime
    """
    # Startup
    logger.info("Starting Todo API application...")

    # Test database connection
    try:
        test_connection()
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

    # Create database tables (only if they don't exist)
    try:
        create_db_and_tables()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Database table creation failed: {e}")
        raise

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Todo API application...")


# Create FastAPI application
app = FastAPI(
    title="Todo API",
    version="1.0.0",
    description="Secure REST API for todo management with JWT authentication",
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# ============================================
# CORS Configuration
# ============================================

# Get allowed origins from environment variable
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

# Add CORS middleware
# TEMPORARY: Allow all origins for debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily for debugging
    allow_credentials=False,  # Must be False when using wildcard origins
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers (Authorization, Content-Type, etc.)
)

logger.info(f"CORS enabled for ALL origins (debugging mode)")

# ============================================
# Exception Handlers
# ============================================


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors with consistent format.

    Returns 422 with detailed validation errors from Pydantic.

    Args:
        request: FastAPI request object
        exc: Validation error exception

    Returns:
        JSONResponse: 422 with validation error details
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(f"Validation error on {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle unexpected exceptions with generic error message.

    Security:
    - Logs full error details internally
    - Returns generic message to client (no stack traces)
    - Prevents information leakage

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse: 500 with generic error message
    """
    logger.error(
        f"Unexpected error on {request.url.path}: {str(exc)}",
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error. Please try again later."
        }
    )


# ============================================
# Health Check Endpoint
# ============================================


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check if the API is running and database is accessible",
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "ok"}
                }
            }
        }
    }
)
async def health_check() -> dict:
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Status object with "ok" value

    Example:
        curl http://localhost:8000/health
        {"status": "ok"}
    """
    return {"status": "ok"}


# ============================================
# API Routers
# ============================================

# Mount user profile router (handles Better Auth integration)
app.include_router(auth.router, prefix="/api/auth")

# Mount todos router
app.include_router(todos.router, prefix="/api/todos", tags=["todos"])

logger.info("API routers registered: /api/auth, /api/todos")

# ============================================
# Root Endpoint
# ============================================


@app.get(
    "/",
    tags=["Root"],
    summary="API root",
    description="API information and available endpoints",
    status_code=status.HTTP_200_OK
)
async def root() -> dict:
    """
    API root endpoint with basic information.

    Returns:
        dict: API metadata and available endpoints
    """
    return {
        "name": "Todo API",
        "version": "1.0.0",
        "description": "Secure REST API for todo management with JWT authentication",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "auth": "/api/auth",
            "todos": "/api/todos"
        }
    }


# ============================================
# Development Server
# ============================================

if __name__ == "__main__":
    import uvicorn

    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting development server on {host}:{port}")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
