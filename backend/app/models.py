"""
SQLModel database models for the todo application.

This module defines the core database entities:
- User: Authentication and account management
- Todo: Task items owned by users
- Session: Refresh token and session management
- PasswordResetToken: Password reset flow
- EmailVerificationToken: Email verification flow

All models use UUID primary keys and include created_at/updated_at timestamps.
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, Literal
from passlib.context import CryptContext
import sqlalchemy as sa

# Priority level type for todos
PriorityLevel = Literal["high", "normal"]

# Password hashing context (bcrypt with 12 salt rounds)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(SQLModel, table=True):
    """
    User database model for authentication and account management.

    Attributes:
        id: Unique identifier (UUID, auto-generated)
        email: Login email address (unique, indexed)
        hashed_password: Bcrypt-hashed password (never store plain text)
        name: User's display name (optional)
        email_verified: Email verification status (default: False)
        language_preference: User's preferred language ('en' or 'ur', default 'en')
        last_login: Last successful login timestamp (indexed)
        created_at: Account creation timestamp
        updated_at: Last update timestamp

    Relationships:
        todos: One-to-many relationship with Todo items
        sessions: One-to-many relationship with Session records
        password_reset_tokens: One-to-many relationship with PasswordResetToken
        email_verification_tokens: One-to-many relationship with EmailVerificationToken

    Security:
        - Passwords are hashed with bcrypt (12 salt rounds)
        - Email is unique and indexed for fast login queries
        - UUID primary key for security and distributed systems
        - Email verification prevents unauthorized access
    """
    __tablename__ = "user"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique user identifier"
    )

    # Authentication
    email: str = Field(
        max_length=255,
        unique=True,
        index=True,
        nullable=False,
        description="Login email address (unique, indexed)"
    )
    hashed_password: str = Field(
        max_length=255,
        nullable=False,
        description="Bcrypt-hashed password (never plain text)"
    )

    # Profile
    name: Optional[str] = Field(
        default=None,
        max_length=255,
        nullable=True,
        description="User's display name"
    )

    # Email Verification (US5)
    email_verified: bool = Field(
        default=False,
        nullable=False,
        description="Email verification status (default: False)"
    )

    # Language Preference (MCP Feature - US3)
    language_preference: str = Field(
        default="en",
        max_length=2,
        nullable=False,
        description="User's preferred language: 'en' or 'ur' (default: 'en')"
    )

    # Session Tracking (US4)
    last_login: Optional[datetime] = Field(
        default=None,
        nullable=True,
        index=True,
        description="Last successful login timestamp (indexed for queries)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Account creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp"
    )

    # Relationships
    todos: List["Todo"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    sessions: List["Session"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    password_reset_tokens: List["PasswordResetToken"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    email_verification_tokens: List["EmailVerificationToken"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    def verify_password(self, plain_password: str) -> bool:
        """
        Verify a plain password against the hashed password.

        Args:
            plain_password: The plain text password to verify

        Returns:
            True if password matches, False otherwise

        Note:
            Truncates password to 72 bytes to match the hashing behavior.
        """
        # Truncate password to 72 bytes for bcrypt compatibility
        password_bytes = plain_password.encode('utf-8')[:72]
        truncated_password = password_bytes.decode('utf-8', errors='ignore')
        return pwd_context.verify(truncated_password, self.hashed_password)

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """
        Hash a plain password using bcrypt.

        Args:
            plain_password: The plain text password to hash

        Returns:
            Bcrypt-hashed password string

        Note:
            Bcrypt has a 72-byte limit on passwords. Passwords are truncated
            to 72 bytes before hashing to avoid compatibility issues.
        """
        # Truncate password to 72 bytes for bcrypt compatibility
        password_bytes = plain_password.encode('utf-8')[:72]
        return pwd_context.hash(password_bytes.decode('utf-8', errors='ignore'))

    class Config:
        """SQLModel configuration"""
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "email_verified": False,
            }
        }


class Session(SQLModel, table=True):
    """
    Session database model for refresh token management (US1).

    Attributes:
        id: Unique identifier (UUID, auto-generated)
        user_id: Owner of the session (foreign key to users.id)
        refresh_token_hash: Bcrypt-hashed refresh token for security
        expires_at: Token expiration timestamp (indexed)
        created_at: Session creation timestamp
        last_activity: Last activity timestamp for session tracking
        ip_address: Client IP address (max 45 chars for IPv6)
        user_agent: Client user agent string for device identification

    Relationships:
        user: Many-to-one relationship with User

    Security:
        - Refresh tokens are hashed with bcrypt (never store plain text)
        - Expired sessions are automatically invalid
        - All queries MUST filter by user_id
        - CASCADE delete when user is deleted

    Performance:
        - user_id indexed for fast user-scoped queries
        - expires_at indexed for cleanup of expired sessions
    """
    __tablename__ = "session"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique session identifier"
    )

    # Foreign Key to User
    user_id: UUID = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,
        description="Owner of the session (foreign key to users.id, CASCADE on delete)"
    )

    # Token Management
    refresh_token_hash: str = Field(
        max_length=255,
        nullable=False,
        description="Bcrypt-hashed refresh token (never plain text)"
    )

    # Session Metadata
    expires_at: datetime = Field(
        nullable=False,
        index=True,
        description="Token expiration timestamp (indexed for cleanup)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Session creation timestamp"
    )
    last_activity: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last activity timestamp for session tracking"
    )

    # Device Tracking
    ip_address: str = Field(
        max_length=45,  # IPv6 max length
        nullable=False,
        description="Client IP address (max 45 chars for IPv6)"
    )
    user_agent: str = Field(
        sa_column=sa.Column(sa.Text, nullable=False),
        description="Client user agent string for device identification"
    )

    # Relationships
    user: Optional[User] = Relationship(back_populates="sessions")

    class Config:
        """SQLModel configuration"""
        json_schema_extra = {
            "example": {
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
        }


class PasswordResetToken(SQLModel, table=True):
    """
    PasswordResetToken database model for password reset flow (US2).

    Attributes:
        id: Unique identifier (UUID, auto-generated)
        user_id: Owner of the token (foreign key to users.id)
        token_hash: Bcrypt-hashed token for security
        expires_at: Token expiration timestamp (indexed, typically 24 hours)
        created_at: Token creation timestamp
        used: Token usage status (default: False)

    Relationships:
        user: Many-to-one relationship with User

    Security:
        - Tokens are hashed with bcrypt (never store plain text)
        - Tokens expire after 24 hours
        - Tokens can only be used once (used=True after use)
        - All tokens invalidated when password changes
        - CASCADE delete when user is deleted

    Performance:
        - user_id indexed for fast user-scoped queries
        - expires_at indexed for cleanup of expired tokens
    """
    __tablename__ = "password_reset_token"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique token identifier"
    )

    # Foreign Key to User
    user_id: UUID = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,
        description="Owner of the token (foreign key to users.id, CASCADE on delete)"
    )

    # Token Management
    token_hash: str = Field(
        max_length=255,
        nullable=False,
        description="Bcrypt-hashed token (never plain text)"
    )

    # Token Metadata
    expires_at: datetime = Field(
        nullable=False,
        index=True,
        description="Token expiration timestamp (indexed for cleanup, typically 24 hours)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Token creation timestamp"
    )
    used: bool = Field(
        default=False,
        nullable=False,
        description="Token usage status (default: False, set to True after use)"
    )

    # Relationships
    user: Optional[User] = Relationship(back_populates="password_reset_tokens")

    class Config:
        """SQLModel configuration"""
        json_schema_extra = {
            "example": {
                "used": False,
            }
        }


class EmailVerificationToken(SQLModel, table=True):
    """
    EmailVerificationToken database model for email verification flow (US3).

    Attributes:
        id: Unique identifier (UUID, auto-generated)
        user_id: Owner of the token (foreign key to users.id)
        token_hash: Bcrypt-hashed token for security
        expires_at: Token expiration timestamp (indexed, typically 24 hours)
        created_at: Token creation timestamp

    Relationships:
        user: Many-to-one relationship with User

    Security:
        - Tokens are hashed with bcrypt (never store plain text)
        - Tokens expire after 24 hours
        - Token deleted after successful verification
        - CASCADE delete when user is deleted

    Performance:
        - user_id indexed for fast user-scoped queries
        - expires_at indexed for cleanup of expired tokens
    """
    __tablename__ = "email_verification_token"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique token identifier"
    )

    # Foreign Key to User
    user_id: UUID = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,
        description="Owner of the token (foreign key to users.id, CASCADE on delete)"
    )

    # Token Management
    token_hash: str = Field(
        max_length=255,
        nullable=False,
        description="Bcrypt-hashed token (never plain text)"
    )

    # Token Metadata
    expires_at: datetime = Field(
        nullable=False,
        index=True,
        description="Token expiration timestamp (indexed for cleanup, typically 24 hours)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Token creation timestamp"
    )

    # Relationships
    user: Optional[User] = Relationship(back_populates="email_verification_tokens")

    class Config:
        """SQLModel configuration"""
        json_schema_extra = {
            "example": {
                "expires_at": "2026-01-14T00:00:00Z",
            }
        }


class Todo(SQLModel, table=True):
    """
    Todo database model for task management.

    Attributes:
        id: Unique identifier (UUID, auto-generated)
        user_id: Owner of the todo (foreign key to users.id)
        title: Todo title/summary (max 500 characters)
        description: Optional detailed description (unlimited text)
        completed: Completion status (default: False)
        priority: Priority level - "high" or "normal" (default: "normal")
        created_at: Creation timestamp
        updated_at: Last update timestamp

    Relationships:
        owner: Many-to-one relationship with User

    Security:
        - All queries MUST filter by user_id to prevent cross-user data access
        - User ID extracted from JWT token (NEVER from request body)
        - Ownership verification required before UPDATE/DELETE operations
        - Foreign key with CASCADE delete ensures cleanup when user is deleted

    Performance:
        - user_id indexed for fast user-scoped queries
        - completed indexed for filtering by status
        - created_at indexed for sorting by creation date
    """
    __tablename__ = "todo"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique todo identifier"
    )

    # Foreign Key to User
    user_id: UUID = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,
        description="Owner of the todo (foreign key to users.id, CASCADE on delete)"
    )

    # Todo Fields
    title: str = Field(
        max_length=500,
        nullable=False,
        index=True,  # Index for search queries
        description="Todo title/summary (1-500 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        nullable=True,
        description="Optional detailed description (0-2000 characters)"
    )
    completed: bool = Field(
        default=False,
        nullable=False,
        index=True,  # Index for filtering by completion status
        description="Completion status (default: False)"
    )
    priority: str = Field(
        default="normal",
        description="Priority level: 'high' or 'normal' (default: normal)",
        sa_column=sa.Column(sa.String(20), nullable=False, index=True, default="normal")
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,  # Index for sorting by creation date
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp"
    )

    # Relationships
    owner: Optional[User] = Relationship(back_populates="todos")

    class Config:
        """SQLModel configuration"""
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, and coffee",
                "completed": False,
            }
        }
