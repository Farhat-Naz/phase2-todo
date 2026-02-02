---
id: 5
title: Implement Todo Database Model and Migration
stage: green
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-todo-full-stack-app
branch: 006-high-priority
user: developer
command: none
labels: ["database", "sqlmodel", "migration", "todo-model", "implementation"]
links:
  spec: specs/001-todo-full-stack-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/models.py
  - backend/alembic/versions/20260108_0002_002_create_todos_table.py
tests:
  - Model import verification (passed)
  - Migration syntax validation (passed)
  - Relationship validation (passed)
---

## Prompt

I need you to implement the Todo database model and migration for a full-stack todo application. You are working on Phase 2 (US2-US4: Core Todo CRUD operations).

### Context
- Feature: 001-todo-full-stack-app
- Tech stack: Python 3.13+, FastAPI, SQLModel, Neon Serverless PostgreSQL
- Package manager: uv
- Project: Backend models already exist (User model in `backend/app/models.py`)
- Database connection already configured in `backend/app/database.py`

### Your Task

#### TASK-024: Create Todo Database Model
**File**: `backend/app/models.py` (append to existing file)
**Requirements**:
- Create SQLModel Todo entity with:
  - id: UUID (primary key)
  - user_id: UUID (foreign key to users.id, ON DELETE CASCADE)
  - title: str (VARCHAR 500, NOT NULL)
  - description: str | None (TEXT, nullable)
  - completed: bool (default False)
  - created_at: datetime
  - updated_at: datetime
- SQLModel with table=True
- Relationship to User model
- Foreign key constraint with CASCADE delete
- Indexes: user_id, completed, created_at
- Full type hints

#### TASK-025: Create Alembic Migration for Todos Table
**File**: `backend/alembic/versions/002_create_todos.py`
**Requirements**:
- Generate Alembic migration for todos table
- Include all fields: id (UUID PK), user_id (UUID FK), title (VARCHAR 500 NOT NULL), description (TEXT nullable), completed (BOOLEAN default false), timestamps
- Foreign key: user_id REFERENCES users(id) ON DELETE CASCADE
- Indexes: idx_todo_user_id, idx_todo_completed, idx_todo_created_at
- Both upgrade() and downgrade() functions

### Reference
- Existing User model in `backend/app/models.py`
- Data model specification: `specs/001-todo-full-stack-app/data-model.md`

### Acceptance Criteria
- Todo model properly configured with SQLModel table=True
- Relationship to User (one-to-many: User has many Todos)
- Foreign key constraint with CASCADE delete
- All indexes created for performance
- Migration can be run with: `uv run alembic upgrade head`
- Type safety: strict type hints throughout

### Important Notes
- APPEND Todo model to existing models.py (don't overwrite User model)
- Migration numbering: 002 (User migration is 001)
- Follow same patterns as User model for consistency
- Use UUID for all primary keys
- Add relationship field to User model: `todos: list["Todo"] = Relationship(back_populates="owner")`

Return a summary of what you created.

## Response snapshot

### Implementation Summary

Successfully implemented the Todo database model and migration for the full-stack todo application:

#### 1. Todo Database Model (backend/app/models.py)
Created the `Todo` SQLModel class with:
- **Primary Key**: UUID `id` (auto-generated via uuid4)
- **Foreign Key**: UUID `user_id` → `user.id` with CASCADE delete
- **Fields**:
  - `title`: VARCHAR(500), NOT NULL, indexed for search
  - `description`: TEXT, nullable
  - `completed`: BOOLEAN, default False, indexed for filtering
  - `created_at`: TIMESTAMP, indexed for sorting
  - `updated_at`: TIMESTAMP
- **Relationship**: Bidirectional relationship with User model
  - Todo.owner → User (many-to-one)
  - User.todos → List[Todo] (one-to-many) with cascade delete-orphan
- **Comprehensive Documentation**: Security notes, performance considerations, field descriptions

#### 2. Updated User Model
- Added `todos` relationship field to User model
- Configured SQLAlchemy cascade: "all, delete-orphan"
- Maintains bidirectional relationship with Todo

#### 3. Alembic Migration (backend/alembic/versions/20260108_0002_002_create_todos_table.py)
Created migration `002_create_todos` with:
- **Table Creation**: Full todo table schema matching SQLModel definition
- **Foreign Key Constraint**: user_id REFERENCES user(id) ON DELETE CASCADE
- **Performance Indexes**:
  1. `idx_todo_user_id`: User-scoped queries (CRITICAL for multi-tenant)
  2. `idx_todo_completed`: Filter by completion status
  3. `idx_todo_created_at`: Sort by creation date (DESC order)
  4. `idx_todo_title`: Search queries with text_pattern_ops
  5. `idx_todo_user_completed_created`: Composite index for common query pattern (user + status + date)
- **Complete upgrade()/downgrade()**: Both migration paths implemented
- **Detailed Documentation**: Security notes, performance rationale, column descriptions

#### 4. Verification Results
All validation checks passed:
- ✅ Model imports successfully without syntax errors
- ✅ Todo table name: `todo`
- ✅ User table name: `user`
- ✅ Bidirectional relationships established correctly
- ✅ Migration file syntax validated (Python compilation successful)
- ✅ All 7 fields present with correct types (id, user_id, title, description, completed, created_at, updated_at)

#### Key Design Decisions

1. **Security-First Design**:
   - user_id indexed for fast filtering (prevents cross-user data leaks)
   - CASCADE delete ensures automatic cleanup when users are deleted
   - Comprehensive documentation on user isolation requirements

2. **Performance Optimization**:
   - 5 strategic indexes covering common query patterns
   - Composite index for the most frequent query: user's active/completed todos sorted by date
   - text_pattern_ops for efficient LIKE queries on title field

3. **Type Safety**:
   - Full type hints throughout (UUID, str, Optional[str], bool, datetime)
   - SQLModel integration ensures Pydantic validation + SQLAlchemy power

4. **Maintainability**:
   - Comprehensive docstrings with security and performance notes
   - Consistent patterns with existing User model
   - Clear migration documentation for future developers

#### Files Modified/Created
1. **Modified**: `backend/app/models.py`
   - Added `import sqlalchemy as sa`
   - Updated User.todos relationship
   - Added complete Todo model class (90+ lines with documentation)

2. **Created**: `backend/alembic/versions/20260108_0002_002_create_todos_table.py`
   - Migration revision: 002_create_todos
   - Down revision: 001_create_users
   - Complete upgrade/downgrade functions with 5 indexes

#### Next Steps
1. Install Alembic if not already present: `uv add alembic`
2. Run migration: `uv run alembic upgrade head`
3. Verify table creation in Neon PostgreSQL
4. Proceed to implement Todo CRUD endpoints (TASK-026+)

## Outcome

- ✅ Impact: Todo database model and migration fully implemented, ready for CRUD endpoint development
- 🧪 Tests: Model import verified, migration syntax validated, relationships confirmed bidirectional
- 📁 Files: 1 modified (models.py), 1 created (migration 002)
- 🔁 Next prompts: "Implement Todo CRUD endpoints", "Create Todo Pydantic schemas", "Add user authentication middleware"
- 🧠 Reflection: Implementation follows Neon serverless best practices with comprehensive indexing strategy. The composite index (user_id, completed, created_at DESC) will significantly optimize the most common query pattern. Security documentation emphasizes mandatory user_id filtering for multi-tenant isolation.

## Evaluation notes (flywheel)

- Failure modes observed: Initial attempt used sa_column_kwargs with type_ parameter which caused SQLAlchemy conflict. Fixed by removing and using default SQLModel text handling.
- Graders run and results (PASS/FAIL): Model syntax validation (PASS), Migration compilation (PASS), Relationship validation (PASS)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding a GIN index on description field if full-text search is required in future iterations. Monitor query performance to determine if the composite index covers all common patterns or if additional specialized indexes are needed.
