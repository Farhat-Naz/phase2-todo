"""
Database configuration and session management for Neon Serverless PostgreSQL.

This module provides:
- SQLModel engine configuration with connection pooling
- Database session dependency for FastAPI
- Connection testing utilities

Environment Variables Required:
    DATABASE_URL: PostgreSQL connection string (e.g., postgresql://user:password@host/db)

Connection Pooling Configuration:
    - pool_size=5: Number of persistent connections
    - max_overflow=10: Max additional connections when pool exhausted
    - pool_pre_ping=True: Verify connections before use (critical for serverless)
    - pool_recycle=3600: Recycle connections after 1 hour

SSL Mode:
    Neon requires SSL connections. If DATABASE_URL doesn't include sslmode,
    it will be automatically appended.
"""
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy import text
from contextlib import contextmanager
from typing import Generator, Optional
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Global engine instance (created lazily)
_engine: Optional[object] = None


def get_engine():
    """
    Get or create the database engine (lazy initialization for serverless).

    This function creates the engine only when first called, preventing
    database connection attempts during module import in serverless environments.
    """
    global _engine

    if _engine is not None:
        return _engine

    # Database URL from environment variable
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL environment variable is not set. "
            "Please set it to your Neon PostgreSQL connection string."
        )

    # Strip all whitespace and newlines (common copy-paste issue from Render/Neon dashboards)
    # Database URLs should never contain spaces, newlines, or tabs
    DATABASE_URL = "".join(DATABASE_URL.split())

    # Strip surrounding quotes (single or double) that may be accidentally included
    # This handles cases where users paste URLs like: 'postgresql://...' or "postgresql://..."
    DATABASE_URL = DATABASE_URL.strip("'\"")

    # Fix common typos in dialect prefix
    # Handle cases like 'psql'postgresql:// or psql'postgresql:// or just psql
    if "'psql'" in DATABASE_URL[:10] or DATABASE_URL.startswith("psql"):
        logger.warning("Detected malformed DATABASE_URL with 'psql' prefix, fixing...")
        # Remove the malformed prefix and any quotes around it
        DATABASE_URL = DATABASE_URL.replace("'psql'", "", 1)
        DATABASE_URL = DATABASE_URL.replace("psql'", "", 1)
        DATABASE_URL = DATABASE_URL.replace("psql", "", 1)
        DATABASE_URL = DATABASE_URL.strip("'\"")

    # Ensure PostgreSQL URLs use the psycopg dialect
    if DATABASE_URL.startswith("postgresql://"):
        logger.info("Converting postgresql:// to postgresql+psycopg:// for psycopg3 compatibility")
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

    # Detect database type (SQLite vs PostgreSQL)
    is_sqlite = DATABASE_URL.startswith("sqlite")

    # Configure engine based on database type
    if is_sqlite:
        # SQLite configuration (for local development/testing)
        _engine = create_engine(
            DATABASE_URL,
            echo=False,  # Set to True for SQL query logging
            connect_args={"check_same_thread": False},  # Allow multi-threading
        )
        logger.info("Database engine created for SQLite (local development)")
    else:
        # PostgreSQL configuration (for production with Neon)
        # Ensure SSL mode is configured for Neon
        if "sslmode" not in DATABASE_URL:
            separator = "&" if "?" in DATABASE_URL else "?"
            DATABASE_URL = f"{DATABASE_URL}{separator}sslmode=require"
            logger.info("Added sslmode=require to DATABASE_URL for Neon compatibility")

        # Create SQLModel engine with Neon Serverless PostgreSQL optimizations
        _engine = create_engine(
            DATABASE_URL,
            echo=False,  # Set to True for SQL query logging in development
            pool_pre_ping=True,  # Verify connections before using (critical for serverless)
            pool_size=5,  # Number of persistent connections to maintain
            max_overflow=10,  # Max additional connections when pool is exhausted
            pool_recycle=3600,  # Recycle connections after 1 hour (3600 seconds)
            connect_args={
                "connect_timeout": 10,  # Connection timeout in seconds
                "options": "-c timezone=utc",  # Use UTC timezone
            },
        )
        logger.info(
            "Database engine created with connection pooling: "
            f"pool_size=5, max_overflow=10, pool_recycle=3600s"
        )

    return _engine


def create_db_and_tables() -> None:
    """
    Create all database tables defined in SQLModel models.

    This should only be called once during initial setup or in tests.
    For production migrations, use Alembic instead.

    Warning:
        This creates tables if they don't exist but does NOT handle migrations.
        Always use Alembic for schema changes in production.
    """
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI.

    Yields a database session that is automatically closed after use.
    Use this in FastAPI endpoints via Depends(get_db).

    Yields:
        Session: SQLModel database session

    Example:
        @app.get("/users")
        def list_users(db: Session = Depends(get_db)):
            users = db.exec(select(User)).all()
            return users
    """
    engine = get_engine()
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for manual database session handling.

    Use this for operations outside FastAPI endpoints or when you need
    explicit transaction control.

    Yields:
        Session: SQLModel database session

    Example:
        with get_session() as db:
            user = User(email="test@example.com", ...)
            db.add(user)
            db.commit()
    """
    engine = get_engine()
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise


def test_connection() -> bool:
    """
    Test database connection.

    Returns:
        bool: True if connection successful, False otherwise

    Raises:
        Exception: If connection fails (for diagnostic purposes)
    """
    try:
        engine = get_engine()
        with Session(engine) as session:
            # Execute a simple query to verify connection
            session.exec(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise


# Connection pool monitoring (optional, for debugging)
def get_pool_status() -> dict:
    """
    Get current connection pool status.

    Returns:
        dict: Pool statistics including size, checked out connections, etc.

    Example:
        {
            "pool_size": 5,
            "checked_out": 2,
            "overflow": 0,
            "total_connections": 7
        }
    """
    engine = get_engine()
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total_connections": pool.size() + pool.overflow(),
    }
