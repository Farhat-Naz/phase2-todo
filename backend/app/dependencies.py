"""
FastAPI dependency injection functions for authentication and database sessions.

This module provides reusable dependencies for:
- Current user extraction from JWT tokens (cookies or Authorization header)
- Database session management
- Rate limiting for API endpoints

Security Pattern:
- JWT tokens are validated on every request
- User existence is verified in database
- Invalid/expired tokens return 401 Unauthorized
- Rate limiting protects against abuse
"""
from fastapi import Depends, HTTPException, status, Request
from sqlmodel import Session, select
from typing import Annotated, Optional
from uuid import UUID

from app.database import get_db
from app.models import User
from app.auth import decode_access_token, get_token_from_cookie, oauth2_scheme
from app.services.rate_limiter import InMemoryRateLimiter, get_rate_limiter


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token_from_header: str | None = Depends(oauth2_scheme)
) -> User:
    """
    Extract and validate current user from JWT token (US1, US5).

    Token extraction priority:
    1. Cookie (access_token) - preferred for web browsers
    2. Authorization header (Bearer token) - fallback for API clients

    Args:
        request: FastAPI Request object (for cookie access)
        db: Database session (injected)
        token_from_header: Token from Authorization header (optional)

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException 401: If token is missing, invalid, or user not found

    Security:
        - Validates JWT signature and expiration
        - Verifies user exists in database
        - Extracts user_id from token 'sub' claim (NEVER from request body)

    Example:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"message": f"Hello {current_user.name}"}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try to get token from cookie first (US5)
    token = get_token_from_cookie(request, "access_token")

    # Fallback to Authorization header if no cookie
    if not token:
        token = token_from_header

    # No token provided
    if not token:
        raise credentials_exception

    # Decode and validate token
    try:
        payload = decode_access_token(token)
        user_id_str: str | None = payload.get("sub")

        if user_id_str is None:
            raise credentials_exception

        # Convert string UUID to UUID object
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise credentials_exception

    except HTTPException:
        raise credentials_exception

    # Fetch user from database
    user = db.exec(select(User).where(User.id == user_id)).first()

    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
    token_from_header: str | None = Depends(oauth2_scheme)
) -> User | None:
    """
    Optional authentication dependency for endpoints that support both
    authenticated and unauthenticated access.

    Returns None if no token is provided or if token is invalid.
    Use this for public endpoints that show additional data for logged-in users.

    Args:
        request: FastAPI Request object (for cookie access)
        db: Database session (injected)
        token_from_header: Token from Authorization header (optional)

    Returns:
        User | None: User if authenticated, None otherwise

    Example:
        @app.get("/public")
        def public_route(current_user: User | None = Depends(get_current_user_optional)):
            if current_user:
                return {"message": f"Hello {current_user.name}"}
            return {"message": "Hello guest"}
    """
    try:
        return await get_current_user(request, db, token_from_header)
    except HTTPException:
        return None


async def get_current_user_id(
    request: Request,
    token_from_header: str | None = Depends(oauth2_scheme)
) -> UUID:
    """
    Lightweight dependency that returns only user ID from JWT token.

    Use this when you only need user_id and don't need to query the database.
    More efficient than get_current_user() which fetches full user object.

    Args:
        request: FastAPI Request object (for cookie access)
        token_from_header: Token from Authorization header (optional)

    Returns:
        UUID: User ID from token 'sub' claim

    Raises:
        HTTPException 401: If token is missing or invalid

    Example:
        @app.get("/todos")
        def get_todos(
            current_user_id: UUID = Depends(get_current_user_id),
            db: Session = Depends(get_db)
        ):
            todos = db.exec(select(Todo).where(Todo.user_id == current_user_id)).all()
            return todos
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try to get token from cookie first
    token = get_token_from_cookie(request, "access_token")

    # Fallback to Authorization header
    if not token:
        token = token_from_header

    if not token:
        raise credentials_exception

    # Decode token
    try:
        payload = decode_access_token(token)
        user_id_str: str | None = payload.get("sub")

        if user_id_str is None:
            raise credentials_exception

        return UUID(user_id_str)

    except (HTTPException, ValueError):
        raise credentials_exception


def get_rate_limiter_dependency() -> InMemoryRateLimiter:
    """
    Dependency injection for rate limiter (US6).

    Returns:
        InMemoryRateLimiter: Global rate limiter instance

    Example:
        @app.post("/login")
        def login(
            credentials: LoginRequest,
            request: Request,
            limiter: InMemoryRateLimiter = Depends(get_rate_limiter_dependency)
        ):
            # Check rate limit
            ip = request.client.host
            if not limiter.check_rate_limit(f"login:{ip}", max_attempts=5, window_seconds=900):
                raise HTTPException(status_code=429, detail="Too many login attempts")

            # Process login...
    """
    return get_rate_limiter()


async def check_rate_limit(
    request: Request,
    key_prefix: str,
    max_attempts: int,
    window_seconds: int,
    limiter: InMemoryRateLimiter = Depends(get_rate_limiter_dependency)
) -> None:
    """
    Reusable rate limiting dependency (US6).

    Args:
        request: FastAPI Request object (for IP address)
        key_prefix: Rate limit key prefix (e.g., "login", "register")
        max_attempts: Maximum attempts allowed in window
        window_seconds: Time window in seconds
        limiter: Rate limiter instance (injected)

    Raises:
        HTTPException 429: If rate limit exceeded

    Example:
        # Create a rate limit dependency for login (5 attempts per 15 minutes)
        login_rate_limit = lambda request, limiter=Depends(get_rate_limiter_dependency): (
            check_rate_limit(request, "login", 5, 900, limiter)
        )

        @app.post("/login")
        def login(
            credentials: LoginRequest,
            _: None = Depends(login_rate_limit)
        ):
            # Rate limit checked, process login...
    """
    # Get client IP address
    ip_address = request.client.host if request.client else "unknown"

    # Build rate limit key
    key = f"{key_prefix}:{ip_address}"

    # Check rate limit
    if not limiter.check_rate_limit(key, max_attempts, window_seconds):
        retry_after = limiter.get_retry_after(key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Retry after {retry_after} seconds",
            headers={"Retry-After": str(retry_after)}
        )


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalCurrentUser = Annotated[User | None, Depends(get_current_user_optional)]
CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]
RateLimiter = Annotated[InMemoryRateLimiter, Depends(get_rate_limiter_dependency)]


# Pre-configured rate limit dependencies (US6)
async def login_rate_limit(
    request: Request,
    limiter: RateLimiter
) -> None:
    """Rate limit for login endpoint: 5 attempts per 15 minutes per IP"""
    await check_rate_limit(request, "login", 5, 900, limiter)


async def register_rate_limit(
    request: Request,
    limiter: RateLimiter
) -> None:
    """Rate limit for registration endpoint: 3 attempts per hour per IP"""
    await check_rate_limit(request, "register", 3, 3600, limiter)


async def password_reset_rate_limit(
    request: Request,
    limiter: RateLimiter
) -> None:
    """Rate limit for password reset endpoint: 3 attempts per hour per IP"""
    await check_rate_limit(request, "password_reset", 3, 3600, limiter)


async def email_verification_rate_limit(
    request: Request,
    limiter: RateLimiter
) -> None:
    """Rate limit for email verification resend: 3 attempts per hour per IP"""
    await check_rate_limit(request, "email_verification", 3, 3600, limiter)
