"""
Vercel serverless function entry point for FastAPI backend.
Creates a separate FastAPI instance without lifespan for serverless compatibility.
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application WITHOUT lifespan for Vercel
app = FastAPI(
    title="Todo API",
    version="1.0.0",
    description="Secure REST API for todo management with JWT authentication",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================
# CORS Configuration
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS enabled for ALL origins")

# ============================================
# Exception Handlers
# ============================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
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
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error on {request.url.path}: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if os.getenv("DEBUG", "False") == "True" else "An unexpected error occurred"
        }
    )

# ============================================
# Health Check
# ============================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check."""
    return {
        "status": "ok",
        "message": "Todo API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "todo-api",
        "version": "1.0.0"
    }

@app.get("/api/test", tags=["Health"])
async def test_endpoint():
    """Simple test endpoint to verify API is working without authentication."""
    import os

    # Check environment variables (without exposing sensitive values)
    has_database_url = bool(os.getenv("DATABASE_URL"))
    has_secret_key = bool(os.getenv("SECRET_KEY"))

    return {
        "status": "success",
        "message": "API is working correctly",
        "timestamp": "2026-01-15",
        "environment": {
            "database_url_configured": has_database_url,
            "secret_key_configured": has_secret_key,
            "python_version": os.sys.version.split()[0]
        }
    }

@app.get("/api/db-test", tags=["Health"])
async def database_test():
    """Test database connection without authentication."""
    try:
        from app.database import test_connection
        test_connection()
        return {
            "status": "success",
            "message": "Database connection successful",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Database connection failed",
                "error": str(e)
            }
        )

# ============================================
# API Routers - Import after app creation
# ============================================

try:
    from app.routers import auth, todos
    app.include_router(auth.router, tags=["Authentication"])
    app.include_router(todos.router, tags=["Todos"])
    logger.info("Routers loaded successfully")
except Exception as e:
    logger.error(f"Failed to load routers: {str(e)}", exc_info=True)

    # Create fallback error endpoint
    @app.get("/api/{path:path}")
    async def router_error(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Router initialization failed",
                "message": str(e),
                "path": path
            }
        )

# Vercel requires a handler function
handler = app

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
