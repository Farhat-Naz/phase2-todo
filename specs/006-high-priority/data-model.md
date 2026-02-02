# Data Model: High Priority Task Marking

**Feature**: 006-high-priority
**Date**: 2026-01-07
**Status**: Complete

## Entity Overview

This feature extends the existing `Todo` entity with a priority field. No new entities are introduced.

---

## Entity: Todo (UPDATED)

**Description**: Represents a user's task with priority level for urgent task identification.

### Schema Changes

**New Fields**:
- `priority`: VARCHAR(20) DEFAULT 'normal' NOT NULL
  - Values: "high" | "normal"
  - Indexed for efficient filtering and sorting
  - Default: "normal" for backwards compatibility with existing todos

**Existing Fields** (no changes):
- `id`: UUID PRIMARY KEY
- `user_id`: UUID FOREIGN KEY → user(id) ON DELETE CASCADE
- `title`: VARCHAR(500) NOT NULL
- `description`: TEXT NULL
- `completed`: BOOLEAN DEFAULT FALSE
- `created_at`: TIMESTAMP DEFAULT NOW()
- `updated_at`: TIMESTAMP DEFAULT NOW()

### Relationships

- **Belongs To**: User (many-to-one via user_id)
- **Ownership Rule**: User can only set priority on their own todos (JWT validation required)

### Validation Rules

**Priority Field**:
1. MUST be one of: "high" or "normal"
2. Cannot be null (default "normal" applied)
3. Maximum length: 20 characters
4. Validated at application layer (Pydantic Literal type)
5. Updated when priority changes via PATCH endpoint

**Updated At**:
- MUST update `updated_at` timestamp when priority changes
- MUST NOT update `created_at` timestamp

### State Transitions

Priority can change independently of completion status:

```
normal ←→ high   (toggleable)
   ↓       ↓
completed & normal ←→ completed & high
```

**Rules**:
- Priority can be set on incomplete or completed todos
- Completing a todo does NOT change its priority
- Uncompleting a todo preserves its priority
- Priority persists across all state changes

### Indexes

**New Index**:
```sql
CREATE INDEX idx_todo_priority ON todo(priority);
```

**Composite Index** (for optimized sorting):
```sql
CREATE INDEX idx_todo_priority_created ON todo(priority, created_at DESC);
```

**Existing Indexes** (unchanged):
- `idx_todo_user_id` ON todo(user_id)
- `idx_todo_completed` ON todo(completed)
- `idx_todo_created_at` ON todo(created_at DESC)

### Database Migration

**File**: `alembic/versions/xxx_add_priority_to_todos.py`

**Upgrade**:
```python
def upgrade():
    # Add priority column with default value
    op.add_column('todo',
        sa.Column('priority', sa.VARCHAR(20),
                  nullable=False,
                  server_default='normal')
    )

    # Create index for filtering/sorting
    op.create_index(
        op.f('idx_todo_priority'),
        'todo',
        ['priority'],
        unique=False
    )

    # Create composite index for optimized priority + date sorting
    op.create_index(
        op.f('idx_todo_priority_created'),
        'todo',
        ['priority', sa.text('created_at DESC')],
        unique=False
    )
```

**Downgrade**:
```python
def downgrade():
    op.drop_index(op.f('idx_todo_priority_created'), table_name='todo')
    op.drop_index(op.f('idx_todo_priority'), table_name='todo')
    op.drop_column('todo', 'priority')
```

---

## SQLModel Definition (Backend)

```python
from typing import Literal
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

PriorityLevel = Literal["high", "normal"]

class Todo(SQLModel, table=True):
    """Todo entity with priority support"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=500)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = Field(default=False, index=True)
    priority: PriorityLevel = Field(default="normal", max_length=20, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: "User" = Relationship(back_populates="todos")


class TodoCreate(SQLModel):
    """Schema for creating a new todo"""

    title: str = Field(min_length=1, max_length=500)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    priority: PriorityLevel = Field(default="normal")  # Optional during creation


class TodoUpdate(SQLModel):
    """Schema for updating an existing todo (all fields optional)"""

    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    completed: bool | None = None
    priority: PriorityLevel | None = None  # New field for priority updates


class TodoResponse(SQLModel):
    """Schema for todo API responses"""

    id: UUID
    user_id: UUID
    title: str
    description: str | None
    completed: bool
    priority: PriorityLevel  # Included in all responses
    created_at: datetime
    updated_at: datetime
```

---

## TypeScript Type Definitions (Frontend)

```typescript
// types/todo.ts

export type PriorityLevel = "high" | "normal";

export interface Todo {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: PriorityLevel;  // New field
  created_at: string;  // ISO 8601
  updated_at: string;  // ISO 8601
}

export interface TodoCreate {
  title: string;
  description?: string | null;
  completed?: boolean;
  priority?: PriorityLevel;  // Optional, defaults to "normal"
}

export interface TodoUpdate {
  title?: string;
  description?: string | null;
  completed?: boolean;
  priority?: PriorityLevel;  // Optional for PATCH updates
}

export interface TodoListResponse {
  data: Todo[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface TodoResponse {
  data: Todo;
}

export interface ErrorResponse {
  error: {
    message: string;
    code: string;
    details?: Record<string, any>;
  };
}
```

---

## Data Integrity Constraints

### Application-Level Constraints

1. **Priority Validation** (Pydantic):
   - MUST be "high" or "normal" (enforced by Literal type)
   - Returns 422 if invalid value provided

2. **Ownership Verification** (FastAPI):
   - MUST verify todo.user_id == current_user.id before allowing priority update
   - Returns 404 if verification fails (prevents enumeration)

3. **Timestamp Updates**:
   - MUST update updated_at when priority changes
   - MUST NOT modify created_at

### Database-Level Constraints

1. **NOT NULL**: priority column cannot be null (default 'normal')
2. **Foreign Key**: user_id references user(id) with CASCADE delete
3. **Default Value**: server_default='normal' for new rows

---

## Query Patterns

### List Todos with Priority Sorting

```python
from sqlmodel import select, desc

# Get all todos sorted by priority (high first), then creation date
stmt = (
    select(Todo)
    .where(Todo.user_id == current_user.id)
    .order_by(
        desc(Todo.priority == "high"),  # Boolean sort: True (1) before False (0)
        desc(Todo.created_at)
    )
)
todos = db.exec(stmt).all()
```

### Filter by High Priority

```python
# Get only high priority todos
stmt = (
    select(Todo)
    .where(Todo.user_id == current_user.id, Todo.priority == "high")
    .order_by(desc(Todo.created_at))
)
high_priority_todos = db.exec(stmt).all()
```

### Update Priority

```python
# Update todo priority with ownership check
todo = db.get(Todo, todo_id)
if not todo or todo.user_id != current_user.id:
    raise HTTPException(status_code=404, detail="Todo not found")

if update.priority is not None:
    todo.priority = update.priority
    todo.updated_at = datetime.utcnow()

db.add(todo)
db.commit()
db.refresh(todo)
```

---

## Backwards Compatibility

### Existing Todos

- All existing todos will have `priority = 'normal'` after migration (server_default)
- No data loss or corruption
- No breaking changes to existing API responses (new optional field)

### API Compatibility

- GET responses include new `priority` field (non-breaking: clients can ignore)
- POST requests accept optional `priority` field (defaults to "normal")
- PATCH requests accept optional `priority` field (no change to existing update behavior)

---

## Summary

**Entity Changes**:
- ✅ Todo entity updated with priority field
- ✅ No new entities introduced
- ✅ Backwards compatible with existing data
- ✅ Indexed for performance

**Validation**:
- ✅ Pydantic Literal type for enum validation
- ✅ Ownership verification before updates
- ✅ Timestamp management

**Performance**:
- ✅ Indexed priority column
- ✅ Composite index for priority + date sorting
- ✅ Efficient filtering queries
