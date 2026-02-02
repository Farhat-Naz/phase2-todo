"""
Authentication endpoints for user registration and login.

This module provides endpoints for:
- User registration (POST /register)
- User login with JWT tokens (POST /login)
- Getting current authenticated user profile (GET /me)

Endpoints:
- POST /api/auth/register - Register new user
- POST /api/auth/login - Login and receive JWT token
- GET /api/auth/me - Get current authenticated user profile
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from typing import Annotated

from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserPublic, Token
from app.dependencies import CurrentUser
from app.auth import create_access_token, hash_password, verify_password

# Create router with tags for API documentation
router = APIRouter(
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized - Invalid or expired token"},
        422: {"description": "Validation Error - Invalid request data"},
    },
)


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email, password, and name.",
    responses={
        201: {
            "description": "User registered successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "john.doe@example.com",
                        "name": "John Doe",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Email already registered",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            }
        },
    }
)
async def register(
    user_data: UserRegister,
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """
    Register a new user.

    Args:
        user_data: User registration data (email, password, name)
        db: Database session dependency

    Returns:
        User: Created user object (password excluded)

    Raises:
        HTTPException 400: If email is already registered
        HTTPException 422: If validation fails
    """
    # Check if email already exists
    existing_user = db.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with hashed password
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        name=user_data.name
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and receive JWT access token.",
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect email or password"}
                }
            }
        },
    }
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
) -> Token:
    """
    Login user and return JWT access token.

    Args:
        form_data: OAuth2 form data with username (email) and password
        db: Database session dependency

    Returns:
        Token: JWT access token and token type

    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Find user by email (username field contains email)
    user = db.exec(select(User).where(User.email == form_data.username)).first()

    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user ID
    access_token = create_access_token(data={"sub": str(user.id)})

    # Return token with user data
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserPublic.model_validate(user)
    )


@router.get(
    "/me",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get the authenticated user's profile information.",
    responses={
        200: {
            "description": "Current user profile",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "name": "John Doe",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Not authenticated or token invalid",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid authentication credentials"}
                }
            }
        },
    }
)
async def get_me(current_user: CurrentUser) -> UserPublic:
    """
    Get the current authenticated user's profile.

    Args:
        current_user: Authenticated user from JWT token (injected by dependency)

    Returns:
        UserPublic: Current user's public profile data (excludes password)

    Raises:
        HTTPException 401: If token is invalid, expired, or user not found
    """
    return UserPublic.model_validate(current_user)
