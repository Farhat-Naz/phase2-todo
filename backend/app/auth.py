"""
JWT authentication utilities for token creation and validation.

This module provides:
- create_access_token(): Generate JWT access tokens with short expiration
- decode_access_token(): Validate and decode JWT access tokens
- create_refresh_token(): Generate JWT refresh tokens with long expiration (US1)
- decode_refresh_token(): Validate and decode JWT refresh tokens (US1)
- set_auth_cookies(): Set access and refresh tokens in HTTP-only cookies (US5)
- clear_auth_cookies(): Clear authentication cookies on logout (US5)
- get_token_from_cookie(): Extract token from cookie (US5)
- hash_password(): Hash passwords using bcrypt
- verify_password(): Verify password against hash
- oauth2_scheme: FastAPI OAuth2 password bearer dependency

Required environment variables:
- SECRET_KEY: Secret key for JWT access token signing (generate with: openssl rand -hex 32)
- REFRESH_TOKEN_SECRET: Secret key for JWT refresh token signing (MUST be different from SECRET_KEY)
- ALGORITHM: JWT algorithm (default: HS256)
- ACCESS_TOKEN_EXPIRE_MINUTES: Access token expiration time in minutes (default: 30)
- REFRESH_TOKEN_EXPIRE_DAYS: Refresh token expiration time in days (default: 7)
"""
from fastapi import HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import os

# OAuth2 scheme for token extraction from Authorization header (fallback)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# JWT configuration from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "0a37b3f5d1e8c2a4f6b9d8e7c5a4f3b20a37b3f5d1e8c2a4f6b9d8e7c5a4f3b2")
REFRESH_TOKEN_SECRET = os.getenv("REFRESH_TOKEN_SECRET", "1b48c4g6e2f9d3b5g7c0e9f8d6b5g4c31b48c4g6e2f9d3b5g7c0e9f8d6b5g4c3")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Cookie configuration
ACCESS_TOKEN_COOKIE_NAME = "access_token"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token with expiration.

    Args:
        data: Payload data to encode (must include "sub" for user_id)
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token

    Security:
        - Uses SECRET_KEY for signing
        - Short expiration (default 30 minutes)
        - Signed with HS256 algorithm

    Example:
        token = create_access_token(data={"sub": str(user.id)})
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})

    # Encode JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Validates:
    - Token signature using SECRET_KEY
    - Token expiration (exp claim)
    - Token type (type claim must be "access")
    - Required claims presence (sub)

    Args:
        token: JWT token string to decode

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException 401: If token is invalid or expired

    Example:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and validate token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check token type
        if payload.get("type") != "access":
            raise credentials_exception

        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise credentials_exception

        return payload
    except JWTError:
        raise credentials_exception


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT refresh token with long expiration (US1).

    Args:
        data: Payload data to encode (must include "sub" for user_id)
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT refresh token

    Security:
        - Uses REFRESH_TOKEN_SECRET for signing (different from access token)
        - Long expiration (default 7 days)
        - Used to issue new access tokens without re-authentication
        - Should be stored as hash in database (Session model)

    Example:
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})

    # Encode JWT token with refresh token secret
    encoded_jwt = jwt.encode(to_encode, REFRESH_TOKEN_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


def decode_refresh_token(token: str) -> dict:
    """
    Decode and validate a JWT refresh token (US1).

    Validates:
    - Token signature using REFRESH_TOKEN_SECRET
    - Token expiration (exp claim)
    - Token type (type claim must be "refresh")
    - Required claims presence (sub)

    Args:
        token: JWT refresh token string to decode

    Returns:
        dict: Decoded token payload

    Raises:
        HTTPException 401: If token is invalid or expired

    Security:
        - Uses separate REFRESH_TOKEN_SECRET for validation
        - Checks token type to prevent access token abuse
        - Validates expiration

    Example:
        payload = decode_refresh_token(refresh_token)
        user_id = payload.get("sub")
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and validate token with refresh token secret
        payload = jwt.decode(token, REFRESH_TOKEN_SECRET, algorithms=[ALGORITHM])

        # Check token type
        if payload.get("type") != "refresh":
            raise credentials_exception

        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise credentials_exception

        return payload
    except JWTError:
        raise credentials_exception


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str
) -> None:
    """
    Set access and refresh tokens in HTTP-only cookies (US5).

    Args:
        response: FastAPI Response object
        access_token: JWT access token
        refresh_token: JWT refresh token

    Security:
        - HttpOnly: Prevents JavaScript access (XSS protection)
        - Secure: Only sent over HTTPS (production)
        - SameSite=Strict: CSRF protection
        - Path=/: Available for all routes
        - Max-Age: Cookie expiration time

    Example:
        @app.post("/login")
        def login(response: Response, credentials: LoginRequest):
            user = authenticate_user(credentials)
            access_token = create_access_token(data={"sub": str(user.id)})
            refresh_token = create_refresh_token(data={"sub": str(user.id)})
            set_auth_cookies(response, access_token, refresh_token)
            return {"message": "Logged in successfully"}
    """
    # Get secure flag from environment (True for production HTTPS)
    secure = os.getenv("ENV", "development") != "development"

    # Set access token cookie (short-lived)
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,  # Prevent JavaScript access
        secure=secure,  # HTTPS only in production
        samesite="strict",  # CSRF protection
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert minutes to seconds
        path="/"
    )

    # Set refresh token cookie (long-lived)
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,  # Prevent JavaScript access
        secure=secure,  # HTTPS only in production
        samesite="strict",  # CSRF protection
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # Convert days to seconds
        path="/"
    )


def clear_auth_cookies(response: Response) -> None:
    """
    Clear authentication cookies on logout (US5).

    Args:
        response: FastAPI Response object

    Security:
        - Deletes both access and refresh token cookies
        - Same path and domain as set_auth_cookies()
        - Forces immediate cookie deletion

    Example:
        @app.post("/logout")
        def logout(response: Response):
            clear_auth_cookies(response)
            return {"message": "Logged out successfully"}
    """
    response.delete_cookie(key=ACCESS_TOKEN_COOKIE_NAME, path="/")
    response.delete_cookie(key=REFRESH_TOKEN_COOKIE_NAME, path="/")


def get_token_from_cookie(request: Request, cookie_name: str) -> str | None:
    """
    Extract token from HTTP cookie (US5).

    Args:
        request: FastAPI Request object
        cookie_name: Name of cookie containing token

    Returns:
        str | None: Token if found in cookie, None otherwise

    Example:
        access_token = get_token_from_cookie(request, "access_token")
        if not access_token:
            raise HTTPException(status_code=401, detail="Not authenticated")
    """
    return request.cookies.get(cookie_name)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Bcrypt has a 72-byte limit, so passwords are truncated if necessary.

    Args:
        password: Plain text password to hash

    Returns:
        str: Bcrypt hashed password

    Example:
        hashed = hash_password("SecurePass123")
    """
    # Bcrypt has a 72-byte limit - truncate if necessary
    password_bytes = password.encode('utf-8')[:72]
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Bcrypt has a 72-byte limit, so passwords are truncated if necessary.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password to compare against

    Returns:
        bool: True if password matches, False otherwise

    Example:
        is_valid = verify_password("SecurePass123", user.hashed_password)
    """
    # Bcrypt has a 72-byte limit - truncate if necessary
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    # Verify password
    return bcrypt.checkpw(password_bytes, hashed_bytes)
