# 🧩 SPECIFICATION – ADD TASK

**Feature**: 001-todo-full-stack-app
**Component**: Create Todo API Endpoint
**Created**: 2026-01-06
**Status**: Draft

---

## 1. Purpose

Enable an authenticated user to create a new todo task using the web interface, REST API, voice commands, or chatbot input.

This endpoint implements User Story 2 (Create and View Personal Todos) from the feature specification, providing the core value proposition of task creation with secure user data isolation.

---

## 2. Functional Requirements

### Core Requirements

- **FR-ADD-001**: User MUST be authenticated (valid JWT token required)
- **FR-ADD-002**: User MUST provide a task title (minimum 1 character, maximum 500 characters)
- **FR-ADD-003**: User MAY provide a task description (maximum 2000 characters)
- **FR-ADD-004**: Task MUST be stored in Neon PostgreSQL database
- **FR-ADD-005**: Task MUST be linked to the authenticated user via user_id foreign key
- **FR-ADD-006**: Task MUST default to incomplete status (completed = false)
- **FR-ADD-007**: System MUST generate unique UUID for the task
- **FR-ADD-008**: System MUST record creation timestamp (created_at)
- **FR-ADD-009**: System MUST record update timestamp (updated_at, initially same as created_at)
- **FR-ADD-010**: System MUST return the created task with all fields populated

### Security Requirements

- **FR-ADD-011**: JWT token MUST be validated before processing request
- **FR-ADD-012**: User ID MUST be extracted from JWT 'sub' claim, NEVER from request body
- **FR-ADD-013**: Request MUST include Authorization header with Bearer token
- **FR-ADD-014**: Expired or invalid tokens MUST return 401 Unauthorized
- **FR-ADD-015**: All input data MUST be sanitized to prevent XSS and SQL injection

### Data Validation Requirements

- **FR-ADD-016**: Title field is mandatory; missing title returns 422 Unprocessable Entity
- **FR-ADD-017**: Title exceeding 500 characters returns 422 with validation error
- **FR-ADD-018**: Description exceeding 2000 characters returns 422 with validation error
- **FR-ADD-019**: Empty string title (whitespace only) returns 422 validation error
- **FR-ADD-020**: Unicode characters (including Urdu) MUST be supported in title and description

---

## 3. API Contract

### Endpoint

```
POST /api/todos
```

### Authentication

**Required**: Yes

**Header**:
```http
Authorization: Bearer <JWT_ACCESS_TOKEN>
```

### Request Body

**Content-Type**: `application/json`

**Schema**:
```json
{
  "title": "string (required, 1-500 chars)",
  "description": "string (optional, 0-2000 chars)"
}
```

**Example Request**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and vegetables"
}
```

**Example Request (Urdu)**:
```json
{
  "title": "سبزیاں خریدیں",
  "description": "دودھ، انڈے، روٹی اور سبزیاں"
}
```

**Example Request (Minimal)**:
```json
{
  "title": "Call dentist"
}
```

### Response

#### Success Response (201 Created)

**Status Code**: `201 Created`

**Content-Type**: `application/json`

**Schema**:
```json
{
  "id": "uuid (string)",
  "title": "string",
  "description": "string | null",
  "completed": "boolean",
  "user_id": "uuid (string)",
  "created_at": "ISO 8601 datetime string",
  "updated_at": "ISO 8601 datetime string"
}
```

**Example Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and vegetables",
  "completed": false,
  "user_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "created_at": "2026-01-06T12:30:45.123Z",
  "updated_at": "2026-01-06T12:30:45.123Z"
}
```

#### Error Responses

##### 401 Unauthorized (Missing or Invalid Token)

**Status Code**: `401 Unauthorized`

**Response Body**:
```json
{
  "detail": "Not authenticated"
}
```

**Scenarios**:
- Missing Authorization header
- Invalid JWT signature
- Expired access token
- Malformed Bearer token

##### 422 Unprocessable Entity (Validation Error)

**Status Code**: `422 Unprocessable Entity`

**Response Body**:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Common Validation Errors**:

```json
// Missing title
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}

// Title too long (>500 chars)
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at most 500 characters",
      "type": "value_error.any_str.max_length",
      "ctx": {"limit_value": 500}
    }
  ]
}

// Title is empty string or whitespace only
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "title cannot be empty or whitespace only",
      "type": "value_error"
    }
  ]
}

// Description too long (>2000 chars)
{
  "detail": [
    {
      "loc": ["body", "description"],
      "msg": "ensure this value has at most 2000 characters",
      "type": "value_error.any_str.max_length",
      "ctx": {"limit_value": 2000}
    }
  ]
}
```

##### 500 Internal Server Error

**Status Code**: `500 Internal Server Error`

**Response Body**:
```json
{
  "detail": "Internal server error"
}
```

**Scenarios**:
- Database connection failure
- Unexpected server exception
- Data persistence error

---

## 4. Data Model

### Database Table: `todos`

```sql
CREATE TABLE todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Index for efficient user-scoped queries
CREATE INDEX idx_todos_user_id ON todos(user_id);

-- Index for filtering by completion status
CREATE INDEX idx_todos_user_completed ON todos(user_id, completed);

-- Index for chronological ordering
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);
```

### SQLModel Schema

```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=500, nullable=False)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### Pydantic Schemas

```python
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional

class TodoCreate(BaseModel):
    """Request schema for creating a todo"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or v.strip() == '':
            raise ValueError('title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_stripped(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.strip() if v.strip() else None
        return None

class TodoResponse(BaseModel):
    """Response schema for todo operations"""
    id: UUID
    title: str
    description: Optional[str]
    completed: bool
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

## 5. Implementation Details

### Backend Implementation (FastAPI)

**File**: `backend/app/routers/todos.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models import Todo
from app.schemas import TodoCreate, TodoResponse
from app.auth import get_current_user_id

router = APIRouter(prefix="/api/todos", tags=["todos"])

@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    *,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    todo_in: TodoCreate
) -> TodoResponse:
    """
    Create a new todo task for the authenticated user.

    - **title**: Task title (required, 1-500 chars)
    - **description**: Task description (optional, max 2000 chars)

    Returns the created todo with generated ID and timestamps.
    """
    # Create todo instance with user_id from JWT
    now = datetime.utcnow()
    todo = Todo(
        user_id=user_id,  # SECURITY: From JWT, not request body
        title=todo_in.title,
        description=todo_in.description,
        completed=False,
        created_at=now,
        updated_at=now
    )

    # Persist to database
    db.add(todo)
    db.commit()
    db.refresh(todo)

    return TodoResponse.from_orm(todo)
```

### Frontend Implementation (Next.js)

**File**: `frontend/app/api/client.ts`

```typescript
import { makeApiRequest } from '@/lib/api';

export interface TodoCreateRequest {
  title: string;
  description?: string;
}

export interface TodoResponse {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export async function createTodo(data: TodoCreateRequest): Promise<TodoResponse> {
  return makeApiRequest<TodoResponse>({
    endpoint: '/api/todos',
    method: 'POST',
    body: data,
    requiresAuth: true,
  });
}
```

**File**: `frontend/components/AddTodoForm.tsx`

```typescript
'use client';

import { useState } from 'react';
import { createTodo } from '@/app/api/client';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Textarea } from '@/components/ui/Textarea';

export function AddTodoForm({ onSuccess }: { onSuccess: () => void }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await createTodo({
        title: title.trim(),
        description: description.trim() || undefined
      });

      // Reset form
      setTitle('');
      setDescription('');

      // Notify parent to refresh list
      onSuccess();
    } catch (err: any) {
      setError(err.message || 'Failed to create todo');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="What needs to be done?"
        required
        maxLength={500}
        disabled={isLoading}
      />

      <Textarea
        label="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Add details..."
        maxLength={2000}
        rows={3}
        disabled={isLoading}
      />

      {error && (
        <div className="text-red-600 text-sm">{error}</div>
      )}

      <Button
        type="submit"
        isLoading={isLoading}
        disabled={!title.trim() || isLoading}
      >
        Add Todo
      </Button>
    </form>
  );
}
```

---

## 6. Voice Command Integration

### English Voice Commands

**Patterns**:
- "Add todo: [title]"
- "Create task: [title]"
- "New todo: [title]"
- "Add: [title]"

**Example**:
```
User says: "Add todo: Buy groceries"
→ Classified as CREATE_TODO intent
→ Extracted title: "Buy groceries"
→ API call: POST /api/todos { "title": "Buy groceries" }
```

### Urdu Voice Commands

**Patterns (Urdu Script)**:
- "نیا کام: [title]"
- "اضافہ کریں: [title]"
- "ٹاسک بنائیں: [title]"

**Patterns (Roman Urdu)**:
- "naya kaam: [title]"
- "shamil karen: [title]"
- "task banayein: [title]"

**Example**:
```
User says: "نیا کام: دودھ خریدیں"
→ Classified as CREATE_TODO intent
→ Extracted title: "دودھ خریدیں"
→ API call: POST /api/todos { "title": "دودھ خریدیں" }
```

**Implementation Reference**: See `.claude/skills/voice.skill.md` for complete voice command mapping logic.

---

## 7. Test Cases

### Unit Tests (Backend)

```python
import pytest
from uuid import uuid4
from fastapi import status

def test_create_todo_success(client, auth_headers, db_session):
    """Test successful todo creation with valid data"""
    response = client.post(
        "/api/todos",
        json={"title": "Test Todo", "description": "Test Description"},
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "Test Description"
    assert data["completed"] is False
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_todo_minimal(client, auth_headers):
    """Test todo creation with only required fields"""
    response = client.post(
        "/api/todos",
        json={"title": "Minimal Todo"},
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Minimal Todo"
    assert data["description"] is None

def test_create_todo_urdu(client, auth_headers):
    """Test todo creation with Urdu text"""
    response = client.post(
        "/api/todos",
        json={"title": "خریداری کریں", "description": "دودھ اور روٹی"},
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "خریداری کریں"
    assert data["description"] == "دودھ اور روٹی"

def test_create_todo_missing_title(client, auth_headers):
    """Test validation error when title is missing"""
    response = client.post(
        "/api/todos",
        json={"description": "No title provided"},
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "title" in response.json()["detail"][0]["loc"]

def test_create_todo_empty_title(client, auth_headers):
    """Test validation error when title is empty or whitespace"""
    response = client.post(
        "/api/todos",
        json={"title": "   "},
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_todo_title_too_long(client, auth_headers):
    """Test validation error when title exceeds max length"""
    response = client.post(
        "/api/todos",
        json={"title": "x" * 501},
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_todo_description_too_long(client, auth_headers):
    """Test validation error when description exceeds max length"""
    response = client.post(
        "/api/todos",
        json={"title": "Valid", "description": "x" * 2001},
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_todo_unauthorized(client):
    """Test 401 error when no auth token provided"""
    response = client.post(
        "/api/todos",
        json={"title": "Unauthorized Todo"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_todo_invalid_token(client):
    """Test 401 error when invalid token provided"""
    response = client.post(
        "/api/todos",
        json={"title": "Invalid Token Todo"},
        headers={"Authorization": "Bearer invalid_token_here"}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_todo_user_isolation(client, auth_headers_user1, auth_headers_user2, db_session):
    """Test that todos are correctly associated with the authenticated user"""
    # User 1 creates a todo
    response1 = client.post(
        "/api/todos",
        json={"title": "User 1 Todo"},
        headers=auth_headers_user1
    )
    todo1 = response1.json()

    # User 2 creates a todo
    response2 = client.post(
        "/api/todos",
        json={"title": "User 2 Todo"},
        headers=auth_headers_user2
    )
    todo2 = response2.json()

    # Verify different user_ids
    assert todo1["user_id"] != todo2["user_id"]
```

### Integration Tests (Frontend)

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AddTodoForm } from '@/components/AddTodoForm';
import { createTodo } from '@/app/api/client';

jest.mock('@/app/api/client');

describe('AddTodoForm', () => {
  it('should create todo on form submission', async () => {
    const onSuccess = jest.fn();
    const mockCreateTodo = createTodo as jest.MockedFunction<typeof createTodo>;
    mockCreateTodo.mockResolvedValue({
      id: '123',
      title: 'Test Todo',
      description: null,
      completed: false,
      user_id: 'user-123',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });

    render(<AddTodoForm onSuccess={onSuccess} />);

    const titleInput = screen.getByLabelText(/title/i);
    fireEvent.change(titleInput, { target: { value: 'Test Todo' } });

    const submitButton = screen.getByRole('button', { name: /add todo/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockCreateTodo).toHaveBeenCalledWith({
        title: 'Test Todo',
        description: undefined,
      });
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it('should display validation error for empty title', () => {
    render(<AddTodoForm onSuccess={jest.fn()} />);

    const submitButton = screen.getByRole('button', { name: /add todo/i });
    expect(submitButton).toBeDisabled();
  });

  it('should handle API errors', async () => {
    const mockCreateTodo = createTodo as jest.MockedFunction<typeof createTodo>;
    mockCreateTodo.mockRejectedValue(new Error('API Error'));

    render(<AddTodoForm onSuccess={jest.fn()} />);

    const titleInput = screen.getByLabelText(/title/i);
    fireEvent.change(titleInput, { target: { value: 'Test' } });

    const submitButton = screen.getByRole('button', { name: /add todo/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/failed to create todo/i)).toBeInTheDocument();
    });
  });
});
```

### E2E Tests (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test.describe('Add Todo', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/auth/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('should create todo via form', async ({ page }) => {
    await page.fill('input[placeholder*="What needs"]', 'E2E Test Todo');
    await page.fill('textarea[placeholder*="Add details"]', 'This is a test description');
    await page.click('button:has-text("Add Todo")');

    // Verify todo appears in list
    await expect(page.locator('text=E2E Test Todo')).toBeVisible();
    await expect(page.locator('text=This is a test description')).toBeVisible();
  });

  test('should create todo via voice command', async ({ page, context }) => {
    // Grant microphone permissions
    await context.grantPermissions(['microphone']);

    await page.click('button[aria-label="Voice input"]');

    // Simulate voice input (requires mock)
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('voicecommand', {
        detail: { command: 'Add todo: Voice test task' }
      }));
    });

    await expect(page.locator('text=Voice test task')).toBeVisible();
  });

  test('should show validation error for empty title', async ({ page }) => {
    const submitButton = page.locator('button:has-text("Add Todo")');
    await expect(submitButton).toBeDisabled();
  });
});
```

---

## 8. Performance Requirements

- **Response Time**: p95 latency < 500ms for todo creation
- **Throughput**: Support 100 concurrent todo creations per second
- **Database**: Connection pooling with min 5, max 20 connections
- **Validation**: Client-side validation for immediate feedback, server-side for security

---

## 9. Security Considerations

### Authentication & Authorization

- JWT token validated on every request using python-jose
- User ID extracted from 'sub' claim, never trusted from request body
- Token expiration checked (30-minute access token lifespan)
- Failed authentication returns 401, not 404 or 403

### Input Sanitization

- All string inputs trimmed of leading/trailing whitespace
- SQL injection prevented by SQLModel parameterized queries
- XSS prevented by React's automatic escaping and Content-Security-Policy headers
- Unicode validation ensures proper UTF-8 encoding for Urdu text

### Data Isolation

- Every todo MUST have user_id foreign key constraint
- Database-level enforcement via foreign key ON DELETE CASCADE
- Application-level validation ensures user_id matches JWT claim
- No cross-user data leakage possible

---

## 10. Monitoring & Observability

### Metrics to Track

- `todo_create_requests_total` (counter) - Total creation requests
- `todo_create_requests_success` (counter) - Successful creations
- `todo_create_requests_failed` (counter) - Failed creations
- `todo_create_duration_seconds` (histogram) - Request latency
- `todo_create_validation_errors` (counter) - Validation failures

### Logging

```python
import logging

logger = logging.getLogger(__name__)

@router.post("")
async def create_todo(...):
    logger.info(f"Creating todo for user {user_id}")
    try:
        # ... creation logic
        logger.info(f"Successfully created todo {todo.id} for user {user_id}")
        return TodoResponse.from_orm(todo)
    except Exception as e:
        logger.error(f"Failed to create todo for user {user_id}: {str(e)}")
        raise
```

### Alerts

- Alert if error rate > 5% over 5 minutes
- Alert if p95 latency > 1 second over 5 minutes
- Alert if database connection pool exhausted

---

## 11. Dependencies

### Backend Dependencies

- **FastAPI**: Web framework and routing
- **SQLModel**: ORM and database models
- **Pydantic**: Request/response validation
- **python-jose**: JWT token validation
- **psycopg2-binary**: PostgreSQL driver
- **Neon PostgreSQL**: Database service

### Frontend Dependencies

- **Next.js 16+**: React framework
- **React**: UI library
- **TypeScript**: Type safety
- **Better Auth**: Authentication library
- **Web Speech API**: Voice command recognition

### Agent Skills

- **Database Skill** (`.claude/skills/database.skill.md`): User-scoped CRUD patterns
- **Auth Skill** (`.claude/skills/auth.skill.md`): JWT validation and user extraction
- **API Skill** (`.claude/skills/api.skill.md`): Request formatting and error handling
- **Voice Skill** (`.claude/skills/voice.skill.md`): Speech recognition and intent classification

---

## 12. Acceptance Criteria

- [ ] AC-001: Authenticated user can create todo with title only
- [ ] AC-002: Authenticated user can create todo with title and description
- [ ] AC-003: Created todo appears in user's todo list within 3 seconds
- [ ] AC-004: Todo is persisted across page refreshes
- [ ] AC-005: Unauthenticated request returns 401 error
- [ ] AC-006: Missing title returns 422 validation error
- [ ] AC-007: Title >500 chars returns 422 validation error
- [ ] AC-008: Description >2000 chars returns 422 validation error
- [ ] AC-009: Empty/whitespace title returns 422 validation error
- [ ] AC-010: Urdu text (Unicode) is correctly stored and retrieved
- [ ] AC-011: Voice command "Add todo: [title]" creates todo
- [ ] AC-012: User can only see their own todos (data isolation verified)
- [ ] AC-013: Todo ID is unique UUID
- [ ] AC-014: Todo defaults to incomplete status (completed = false)
- [ ] AC-015: Created_at and updated_at timestamps are populated

---

## 13. References

- **Feature Spec**: `specs/001-todo-full-stack-app/spec.md` (User Story 2)
- **Constitution**: `.specify/memory/constitution.md` (API Architecture, Security-First)
- **Database Skill**: `.claude/skills/database.skill.md` (CRUD patterns)
- **Auth Skill**: `.claude/skills/auth.skill.md` (JWT validation)
- **API Skill**: `.claude/skills/api.skill.md` (Request formatting)
- **Voice Skill**: `.claude/skills/voice.skill.md` (Intent classification)

---

## 14. Notes

- This specification covers CREATE operation only; see separate specs for READ, UPDATE, DELETE
- Voice command integration depends on browser support for Web Speech API
- Urdu support requires UTF-8 encoding throughout the stack
- All timestamps use UTC timezone for consistency
- Database indexes ensure efficient user-scoped queries

---

**Next Steps**:
- Review and approve this API specification
- Proceed to implementation following agent-driven development workflow
- Run `/sp.plan` to create detailed implementation plan if not already done
