"""
Better Auth integration utilities for FastAPI backend.

This module provides functions to validate Better Auth JWTs
received from the frontend.
"""

from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import os
from jose import jwt, JWTError
from sqlmodel import Session, select
from .models import User
from .database import get_db
from typing import Annotated

# Configuration
BETTER_AUTH_JWT_SECRET = os.getenv("BETTER_AUTH_JWT_SECRET",
                                  os.getenv("BETTER_AUTH_SECRET",
                                          "jwt-secret-change-in-production"))

# Security scheme for extracting JWT from Authorization header
security = HTTPBearer()

def validate_better_auth_jwt(token: str) -> Optional[Dict[Any, Any]]:
    """
    Validate Better Auth JWT token.

    Args:
        token: JWT token string to validate

    Returns:
        dict: Decoded token payload if valid, None if invalid
    """
    try:
        # Decode and validate JWT token
        payload = jwt.decode(
            token,
            BETTER_AUTH_JWT_SECRET,
            algorithms=["HS512"]  # Using HS512 as configured in auth-server.ts
        )

        # Check if token is expired (Better Auth includes exp claim)
        exp = payload.get("exp")
        if exp and isinstance(exp, int):
            import datetime
            if datetime.datetime.fromtimestamp(exp) < datetime.datetime.utcnow():
                return None

        return payload
    except JWTError:
        return None


async def get_current_user_from_better_auth(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """
    Get current user from Better Auth JWT.

    Args:
        credentials: HTTP authorization credentials from request header
        db: Database session dependency

    Returns:
        User object if authenticated, raises HTTPException otherwise
    """
    token = credentials.credentials

    # Validate the Better Auth JWT
    payload = validate_better_auth_jwt(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from the payload
    # Better Auth typically stores user info in the token
    user_id = payload.get("userId") or payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Query database for user
    statement = select(User).where(User.id == user_id)
    user = db.exec(statement).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# Type alias for cleaner dependency injection
BetterAuthUser = Annotated[User, Depends(get_current_user_from_better_auth)]