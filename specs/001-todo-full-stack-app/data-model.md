# Data Model: Agentic Todo Full-Stack Web Application

**Feature**: `001-todo-full-stack-app`
**Date**: 2026-01-07
**Status**: Complete

## Overview

This document defines the core data model for the multi-user todo application. The model consists of two primary entities: **User** (authentication and account management) and **Todo** (task items owned by users).

---

## Entity: User

### Purpose
Represents a registered user account with authentication credentials and personal information.

### Schema

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | `gen_random_uuid()` | Unique identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | - | Login email address |
| `hashed_password` | VARCHAR(255) | NOT NULL | - | Bcrypt-hashed password (never store plain text) |
| `name` | VARCHAR(255) | NULLABLE | NULL | User's display name |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Account creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Last update timestamp |

### Indexes
- `idx_user_email` ON `(email)` — Fast login queries

### Relationships
- **Todos**: One-to-many (User has many Todos)

### Validation Rules
- Email must be valid format (RFC 5322)
- Email must be unique (enforced at database level)
- Password minimum 8 characters, requires at least one uppercase, one lowercase, one number
- Password is hashed with bcrypt (salt rounds: 12) before storage

### SQL Definition
```sql
CREATE TABLE "user" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_email ON "user"(email);
```

---

## Entity: Todo

### Purpose
Represents a task/todo item owned by a user. Each todo is user-scoped and private.

### Schema

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| `id` | UUID | PRIMARY KEY, NOT NULL | `gen_random_uuid()` | Unique identifier |
| `user_id` | UUID | FOREIGN KEY → user(id), NOT NULL, INDEX | - | Owner of the todo |
| `title` | VARCHAR(500) | NOT NULL | - | Todo title/summary |
| `description` | TEXT | NULLABLE | NULL | Optional detailed description |
| `completed` | BOOLEAN | NOT NULL | FALSE | Completion status |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | NOW() | Last update timestamp |

### Indexes
- `idx_todo_user_id` ON `(user_id)` — Fast user-scoped queries (most common operation)
- `idx_todo_completed` ON `(completed)` — Fast filtering by completion status
- `idx_todo_created_at` ON `(created_at DESC)` — Fast sorting by creation date

### Relationships
- **User**: Many-to-one (Todo belongs to one User via `user_id`)

### Validation Rules
- Title: 1-500 characters, required
- Description: 0-2000 characters, optional
- User ID must reference an existing user
- Completed: Boolean, defaults to false

### SQL Definition
```sql
CREATE TABLE todo (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  title VARCHAR(500) NOT NULL,
  description TEXT,
  completed BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_todo_user_id ON todo(user_id);
CREATE INDEX idx_todo_completed ON todo(completed);
CREATE INDEX idx_todo_created_at ON todo(created_at DESC);
```

---

## Backend Types (Python/SQLModel)

### User Model
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(SQLModel, table=True):
    """User database model"""
    __tablename__ = "user"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    todos: List["Todo"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    def verify_password(self, plain_password: str) -> bool:
        """Verify a plain password against the hashed password"""
        return pwd_context.verify(plain_password, self.hashed_password)

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Hash a plain password"""
        return pwd_context.hash(plain_password)
```

### Todo Model
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class Todo(SQLModel, table=True):
    """Todo database model"""
    __tablename__ = "todo"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="todos")
```

### Pydantic Schemas

```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional
import re

# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: Optional[str] = Field(None, max_length=255)

    @field_validator('password')
    def validate_password(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Todo schemas
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    completed: bool = Field(default=False)

    @field_validator('title')
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    completed: Optional[bool] = None

    @field_validator('title')
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else None

class TodoResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TodoListResponse(BaseModel):
    items: list[TodoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
```

---

## Frontend Types (TypeScript)

```typescript
// User types
export interface User {
  id: string;
  email: string;
  name: string | null;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  name?: string | null;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  user: User;
}

// Todo types
export interface Todo {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TodoCreate {
  title: string;
  description?: string | null;
  completed?: boolean;
}

export interface TodoUpdate {
  title?: string;
  description?: string | null;
  completed?: boolean;
}

export interface TodoListResponse {
  items: Todo[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// Type guards
export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function isValidPassword(password: string): boolean {
  return (
    password.length >= 8 &&
    /[A-Z]/.test(password) &&
    /[a-z]/.test(password) &&
    /[0-9]/.test(password)
  );
}
```

---

## Migration Strategy

### Initial Migration (Alembic)

```python
"""Create user and todo tables

Revision ID: 0001_initial
Revises: None
Create Date: 2026-01-07 10:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_user_email', 'user', ['email'])

    # Create todo table
    op.create_table(
        'todo',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('completed', sa.Boolean, server_default='false', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_todo_user_id', 'todo', ['user_id'])
    op.create_index('idx_todo_completed', 'todo', ['completed'])
    op.create_index('idx_todo_created_at', 'todo', [sa.text('created_at DESC')])

def downgrade():
    op.drop_index('idx_todo_created_at', 'todo')
    op.drop_index('idx_todo_completed', 'todo')
    op.drop_index('idx_todo_user_id', 'todo')
    op.drop_table('todo')
    op.drop_index('idx_user_email', 'user')
    op.drop_table('user')
```

---

## Query Patterns

### User Operations
```python
# Create user
new_user = User(
    email="user@example.com",
    hashed_password=User.hash_password("Password123!"),
    name="John Doe"
)
db.add(new_user)
db.commit()

# Authenticate user
user = db.exec(select(User).where(User.email == email)).first()
if user and user.verify_password(password):
    # Generate JWT token
    ...
```

### Todo Operations
```python
# Create todo (user-scoped)
new_todo = Todo(
    user_id=current_user_id,
    title="Buy groceries",
    description="Milk, eggs, bread"
)
db.add(new_todo)
db.commit()

# List user's todos (CRITICAL: always filter by user_id)
todos = db.exec(
    select(Todo)
    .where(Todo.user_id == current_user_id)
    .order_by(Todo.created_at.desc())
).all()

# Update todo (with ownership verification)
todo = db.get(Todo, todo_id)
if todo and todo.user_id == current_user_id:
    todo.title = "Updated title"
    todo.updated_at = datetime.utcnow()
    db.commit()
else:
    raise HTTPException(status_code=404, detail="Todo not found")

# Delete todo (with ownership verification)
todo = db.get(Todo, todo_id)
if todo and todo.user_id == current_user_id:
    db.delete(todo)
    db.commit()
else:
    raise HTTPException(status_code=404, detail="Todo not found")
```

---

## Security Considerations

1. **Password Security**:
   - Passwords NEVER stored in plain text
   - Bcrypt hashing with 12 salt rounds
   - Minimum 8 characters, mixed case + numbers required

2. **User Isolation**:
   - ALL todo queries filtered by `user_id`
   - User ID extracted from JWT `sub` claim (NEVER from request body)
   - Ownership verified before UPDATE/DELETE operations
   - Return 404 (not 403) to prevent user enumeration

3. **Data Validation**:
   - Pydantic validates all inputs before database operations
   - SQL injection prevented by SQLModel parameterized queries
   - Max length enforced on all string fields

---

## References

- Spec: `specs/001-todo-full-stack-app/spec.md`
- Research: `specs/001-todo-full-stack-app/research.md` (Section 3: Database Schema Design)
- Constitution: `.specify/memory/constitution.md` (Section 5: Database Schema)
