"""
Database configuration optimized for Vercel serverless functions.

This module provides serverless-optimized database connections without connection pooling.
"""
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy import text
from typing import Generator
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Global engine instance (created lazily)
_engine = None


def get_engine():
    """
    Get or create the database engine optimized for serverless.

    Uses NullPool to avoid connection pooling issues in serverless environments.
    """
    global _engine

    if _engine is not None:
        return _engine

    # Database URL from environment variable
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL environment variable is not set"
        )

    # Strip whitespace
    DATABASE_URL = "".join(DATABASE_URL.split())
    DATABASE_URL = DATABASE_URL.strip("'\"")

    # Ensure SSL mode for Neon
    if "sslmode" not in DATABASE_URL:
        separator = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL = f"{DATABASE_URL}{separator}sslmode=require"

    # Create engine with NullPool for serverless (no connection pooling)
    from sqlalchemy.pool import NullPool

    _engine = create_engine(
        DATABASE_URL,
        echo=False,
        poolclass=NullPool,  # No connection pooling for serverless
        connect_args={
            "connect_timeout": 10,
            "options": "-c timezone=utc",
        },
    )
    logger.info("Serverless database engine created (NullPool)")

    return _engine


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI in serverless environment.
    """
    engine = get_engine()
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def test_connection() -> bool:
    """Test database connection."""
    try:
        engine = get_engine()
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise
