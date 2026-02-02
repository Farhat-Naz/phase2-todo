# Authentication Skill

Reusable logic for JWT token handling, validation, and user extraction in FastAPI backend with Better Auth integration.

## Purpose

This skill provides consistent patterns for:
- **JWT Decoding**: Secure token parsing and validation
- **Token Validation**: Verify token signature, expiration, and claims
- **User Extraction**: Extract authenticated user information from tokens

## Usage Context

**Used by:**
- Backend Agent (FastAPI authentication middleware and dependencies)

**When to apply:**
- Implementing authentication middleware
- Creating protected API endpoints
- Extracting current user from JWT tokens
- Validating token expiration and signature
- Implementing authorization logic

## Core Patterns

### 1. JWT Decoding and Validation

```python
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import os

# Configuration
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Token payload model
class TokenPayload(BaseModel):
    sub: str  # User ID
    email: Optional[str] = None
    exp: Optional[int] = None  # Expiration timestamp
    iat: Optional[int] = None  # Issued at timestamp

class TokenData(BaseModel):
    user_id: str
    email: Optional[str] = None

def decode_jwt_token(token: str) -> TokenData:
    """
    Decode and validate JWT token

    Args:
        token: JWT token string

    Returns:
        TokenData with user information

    Raises:
        JWTError: If token is invalid, expired, or malformed
    """
    try:
        # Decode token with signature verification
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Extract user ID from 'sub' claim
        user_id: str = payload.get("sub")
        if user_id is None:
            raise JWTError("Token missing 'sub' claim")

        # Extract optional email
        email: Optional[str] = payload.get("email")

        return TokenData(user_id=user_id, email=email)

    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")

def verify_token_expiration(token: str) -> bool:
    """
    Check if token is expired without full validation

    Args:
        token: JWT token string

    Returns:
        True if token is valid and not expired, False otherwise
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": True}
        )
        return True
    except JWTError:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token

    Args:
        data: Dictionary with claims to encode
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

### 2. Token Validation and Extraction

```python
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

# HTTP Bearer token extractor
security = HTTPBearer()

def extract_token_from_header(authorization: str) -> Optional[str]:
    """
    Extract JWT token from Authorization header

    Args:
        authorization: Authorization header value (e.g., "Bearer <token>")

    Returns:
        Token string or None if invalid format
    """
    if not authorization:
        return None

    parts = authorization.split()

    # Validate format: "Bearer <token>"
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]

def extract_token_from_request(request: Request) -> Optional[str]:
    """
    Extract JWT token from request headers

    Args:
        request: FastAPI Request object

    Returns:
        Token string or None if not found
    """
    authorization = request.headers.get("Authorization")
    return extract_token_from_header(authorization)

def validate_token(token: str) -> TokenData:
    """
    Validate JWT token and return token data

    Args:
        token: JWT token string

    Returns:
        TokenData with user information

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_data = decode_jwt_token(token)
        return token_data
    except JWTError:
        raise credentials_exception
```

### 3. User Extraction (FastAPI Dependencies)

```python
from fastapi import Depends
from sqlmodel import Session, select
from uuid import UUID
from typing import Annotated

# Database models (example)
from models import User  # Assume User model exists

# Database dependency
from database import get_db

async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> UUID:
    """
    Extract current user ID from JWT token

    This is a lightweight dependency that only returns the user ID.
    Use this when you don't need the full user object from the database.

    Args:
        credentials: HTTP Bearer credentials from request

    Returns:
        User UUID

    Raises:
        HTTPException: 401 if token is invalid
    """
    token = credentials.credentials
    token_data = validate_token(token)

    try:
        user_id = UUID(token_data.user_id)
        return user_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db)
) -> User:
    """
    Extract current user from JWT token and fetch from database

    Use this dependency when you need the full user object.
    This makes an extra database query compared to get_current_user_id.

    Args:
        credentials: HTTP Bearer credentials from request
        db: Database session

    Returns:
        User object from database

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    token = credentials.credentials
    token_data = validate_token(token)

    try:
        user_id = UUID(token_data.user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )

    # Fetch user from database
    statement = select(User).where(User.id == user_id)
    user = db.exec(statement).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

# Optional: Dependency for user ID without Bearer scheme validation
async def get_current_user_id_optional(
    request: Request
) -> Optional[UUID]:
    """
    Extract user ID from token if present, otherwise return None

    Use this for endpoints that work for both authenticated and anonymous users.

    Args:
        request: FastAPI Request object

    Returns:
        User UUID if authenticated, None otherwise
    """
    token = extract_token_from_request(request)

    if not token:
        return None

    try:
        token_data = validate_token(token)
        return UUID(token_data.user_id)
    except (HTTPException, ValueError):
        return None
```

### 4. Better Auth Integration

```python
from typing import Optional
from pydantic import BaseModel, EmailStr

# Better Auth session model (matches Better Auth structure)
class BetterAuthSession(BaseModel):
    userId: str
    email: EmailStr
    emailVerified: bool
    name: Optional[str] = None
    image: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

# Login endpoint (integrates with Better Auth)
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login")
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token

    This endpoint should integrate with Better Auth's authentication logic.
    """
    # 1. Verify credentials (Better Auth handles this)
    # 2. Create session
    # 3. Generate JWT token

    # Example (simplified - actual implementation depends on Better Auth setup)
    user = await authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    }

@router.post("/register")
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register new user and return JWT token
    """
    # 1. Validate email not already registered
    # 2. Hash password (Better Auth handles this)
    # 3. Create user in database
    # 4. Generate JWT token

    # Check if user exists
    existing_user = db.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user (password hashing handled by Better Auth)
    new_user = create_user(db, user_data)

    # Create access token
    access_token = create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(new_user.id),
            "email": new_user.email,
            "name": new_user.name
        }
    }

@router.post("/refresh")
async def refresh_token(
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Refresh access token for authenticated user
    """
    # Generate new access token
    access_token = create_access_token(
        data={"sub": str(current_user_id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "created_at": current_user.created_at
    }
```

## Implementation Checklist

When implementing authentication, ensure:

- [ ] `BETTER_AUTH_SECRET` environment variable is set and secure
- [ ] JWT tokens include 'sub' claim with user ID
- [ ] Token expiration is configured appropriately (default: 30 minutes)
- [ ] Protected endpoints use `Depends(get_current_user_id)` or `Depends(get_current_user)`
- [ ] 401 Unauthorized errors include proper WWW-Authenticate header
- [ ] Tokens are validated on every protected request
- [ ] Token signature is verified using the secret key
- [ ] User IDs are validated as UUIDs before database queries
- [ ] Password hashing uses Better Auth's secure implementation
- [ ] HTTPS is enforced in production (tokens transmitted securely)

## Security Considerations

### Critical Security Rules:

1. **Secret Key Management**
   - ✅ Use strong, randomly generated secret key (minimum 32 characters)
   - ✅ Store secret in environment variables, NEVER in code
   - ✅ Use different secrets for development and production
   - ❌ NEVER commit secrets to version control

2. **Token Validation**
   - ✅ ALWAYS verify token signature
   - ✅ Check token expiration on every request
   - ✅ Validate 'sub' claim exists and is valid UUID
   - ❌ NEVER trust token payload without signature verification

3. **Password Security**
   - ✅ Use Better Auth's password hashing (bcrypt/argon2)
   - ✅ Enforce minimum password length (8+ characters)
   - ❌ NEVER store passwords in plain text
   - ❌ NEVER log passwords or tokens

4. **Token Transmission**
   - ✅ Use HTTPS in production
   - ✅ Send tokens in Authorization header (not query params)
   - ✅ Set secure httpOnly cookies when possible
   - ❌ NEVER expose tokens in URLs or logs

5. **Token Expiration**
   - ✅ Set reasonable expiration times (15-30 minutes for access tokens)
   - ✅ Implement refresh token mechanism for long sessions
   - ✅ Invalidate tokens on logout
   - ✅ Consider short-lived tokens for sensitive operations

## Environment Variables Required

```env
# Backend (.env)
BETTER_AUTH_SECRET=your-secure-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3000

# Optional
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Example Usage in Protected Endpoints

```python
from fastapi import APIRouter, Depends
from uuid import UUID

router = APIRouter(prefix="/api", tags=["api"])

# Lightweight: Only need user ID
@router.get("/todos")
async def list_todos(
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """List todos for authenticated user"""
    # Use current_user_id to filter database query
    todos = db.exec(
        select(Todo).where(Todo.user_id == current_user_id)
    ).all()
    return todos

# Full user object: Need user details
@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "created_at": current_user.created_at
    }

# Optional authentication: Public + authenticated features
@router.get("/todos/public")
async def list_public_todos(
    current_user_id: Optional[UUID] = Depends(get_current_user_id_optional),
    db: Session = Depends(get_db)
):
    """List public todos, with user-specific data if authenticated"""
    if current_user_id:
        # Show user's todos
        todos = db.exec(
            select(Todo).where(Todo.user_id == current_user_id)
        ).all()
    else:
        # Show public todos only
        todos = db.exec(
            select(Todo).where(Todo.is_public == True)
        ).all()
    return todos
```

## Error Handling

```python
from fastapi import status

# Standard authentication errors
AUTH_ERRORS = {
    "invalid_token": HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication token",
        headers={"WWW-Authenticate": "Bearer"}
    ),
    "expired_token": HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"}
    ),
    "missing_token": HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"}
    ),
    "user_not_found": HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found"
    ),
    "invalid_credentials": HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password"
    ),
    "email_already_exists": HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already registered"
    )
}
```

## Best Practices

1. **Dependency Injection**: Use FastAPI dependencies for authentication
2. **Token Refresh**: Implement refresh token mechanism for better UX
3. **Rate Limiting**: Add rate limiting to login/register endpoints
4. **Logging**: Log authentication events (login, failed attempts) without sensitive data
5. **Token Revocation**: Implement token blacklist for logout/security events
6. **Multi-Factor Auth**: Consider MFA for enhanced security (Better Auth supports this)
7. **Session Management**: Track active sessions for security monitoring
8. **Password Policies**: Enforce strong password requirements
9. **Account Lockout**: Implement lockout after repeated failed login attempts
10. **Audit Trail**: Log authentication events for compliance and security

## Testing Considerations

- Mock JWT token generation in tests
- Test token expiration scenarios
- Test invalid token formats
- Test missing Authorization header
- Test user not found scenarios
- Test concurrent requests with same token
- Verify 401 responses have correct headers
- Test token refresh flow

## Integration Points

- **Better Auth**: Authentication provider and session management
- **FastAPI**: Dependency injection and route protection
- **SQLModel**: User model and database queries
- **python-jose**: JWT encoding/decoding library
- **passlib**: Password hashing (via Better Auth)

## Required Dependencies

```txt
# requirements.txt
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

## Migration from Better Auth Client-Side to Backend JWT

If migrating from Better Auth client-side only to backend JWT validation:

1. Configure Better Auth to issue JWT tokens with appropriate claims
2. Extract and validate tokens on backend using this skill
3. Ensure 'sub' claim contains user ID
4. Sync secret key between frontend Better Auth config and backend
5. Test token validation with real Better Auth tokens
6. Implement token refresh flow
7. Handle token expiration gracefully on frontend
