# Database Operations Skill

Reusable logic for standardized database operations using SQLModel with Neon Serverless PostgreSQL, including CRUD patterns, user-scoped filtering, and pagination.

## Purpose

This skill provides consistent patterns for:
- **SQLModel CRUD**: Standard create, read, update, delete operations
- **Query Filtering by User**: Secure multi-tenant data isolation
- **Pagination**: Efficient data retrieval with limit/offset patterns

## Usage Context

**Used by:**
- Backend Agent (FastAPI API endpoints)

**When to apply:**
- Implementing new database models and CRUD endpoints
- Adding user-scoped data access controls
- Implementing paginated list endpoints
- Ensuring data isolation between users

## Core Patterns

### 1. SQLModel CRUD Operations

```python
from sqlmodel import Session, select
from typing import Optional, List
from uuid import UUID

# Base CRUD pattern for SQLModel
class CRUDBase:
    """Base class for CRUD operations on SQLModel tables"""

    def __init__(self, model):
        self.model = model

    def create(self, db: Session, *, obj_in: dict) -> model:
        """Create a new record"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: UUID) -> Optional[model]:
        """Get a single record by ID"""
        statement = select(self.model).where(self.model.id == id)
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[model]:
        """Get multiple records with pagination"""
        statement = select(self.model).offset(skip).limit(limit)
        return db.exec(statement).all()

    def update(
        self,
        db: Session,
        *,
        db_obj: model,
        obj_in: dict
    ) -> model:
        """Update an existing record"""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: UUID) -> model:
        """Delete a record by ID"""
        obj = db.get(self.model, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
```

### 2. User-Scoped Filtering

```python
from sqlmodel import Session, select, Field, SQLModel
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

# Example model with user ownership
class TodoBase(SQLModel):
    title: str = Field(index=True)
    description: Optional[str] = None
    completed: bool = Field(default=False)

class Todo(TodoBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)  # CRITICAL: Index for performance
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# User-scoped CRUD operations
class CRUDTodo:
    """CRUD operations for Todo with user-scoped filtering"""

    def create(self, db: Session, *, obj_in: dict, user_id: UUID) -> Todo:
        """Create a new todo for the authenticated user"""
        # SECURITY: Always set user_id from authenticated session, not from request body
        db_obj = Todo(**obj_in, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, id: UUID, user_id: UUID) -> Optional[Todo]:
        """Get a single todo, ensuring it belongs to the user"""
        # SECURITY: Always filter by user_id
        statement = select(Todo).where(
            Todo.id == id,
            Todo.user_id == user_id
        )
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        completed: Optional[bool] = None
    ) -> List[Todo]:
        """Get all todos for the authenticated user with optional filtering"""
        # SECURITY: Always filter by user_id
        statement = select(Todo).where(Todo.user_id == user_id)

        # Optional filters
        if completed is not None:
            statement = statement.where(Todo.completed == completed)

        # Pagination
        statement = statement.offset(skip).limit(limit).order_by(Todo.created_at.desc())

        return db.exec(statement).all()

    def update(
        self,
        db: Session,
        *,
        id: UUID,
        user_id: UUID,
        obj_in: dict
    ) -> Optional[Todo]:
        """Update a todo, ensuring it belongs to the user"""
        # SECURITY: Verify ownership before updating
        db_obj = self.get(db, id=id, user_id=user_id)
        if not db_obj:
            return None

        # Update fields
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and field != 'user_id':  # Prevent user_id changes
                setattr(db_obj, field, value)

        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: UUID, user_id: UUID) -> Optional[Todo]:
        """Delete a todo, ensuring it belongs to the user"""
        # SECURITY: Verify ownership before deleting
        db_obj = self.get(db, id=id, user_id=user_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

    def get_count(self, db: Session, *, user_id: UUID) -> int:
        """Get total count of todos for the user"""
        from sqlmodel import func
        statement = select(func.count(Todo.id)).where(Todo.user_id == user_id)
        return db.exec(statement).one()

# Instantiate CRUD object
crud_todo = CRUDTodo()
```

### 3. Pagination Patterns

```python
from sqlmodel import Session, select, func
from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')

# Pagination response model
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

# Pagination helper function
def paginate(
    db: Session,
    statement: select,
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100
) -> PaginatedResponse:
    """
    Generic pagination helper

    Args:
        db: Database session
        statement: SQLModel select statement (without offset/limit)
        page: Page number (1-indexed)
        page_size: Number of items per page
        max_page_size: Maximum allowed page size

    Returns:
        PaginatedResponse with items and pagination metadata
    """
    # Validate and cap page_size
    page_size = min(page_size, max_page_size)
    page = max(1, page)  # Ensure page is at least 1

    # Get total count
    count_statement = select(func.count()).select_from(statement.subquery())
    total = db.exec(count_statement).one()

    # Calculate pagination metadata
    total_pages = (total + page_size - 1) // page_size  # Ceiling division
    has_next = page < total_pages
    has_prev = page > 1

    # Apply pagination to statement
    skip = (page - 1) * page_size
    paginated_statement = statement.offset(skip).limit(page_size)
    items = db.exec(paginated_statement).all()

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )

# Example usage in endpoint
from fastapi import APIRouter, Depends, Query

router = APIRouter()

@router.get("/todos", response_model=PaginatedResponse[Todo])
def list_todos(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """List todos with pagination and filtering"""
    # Build query with user filtering
    statement = select(Todo).where(Todo.user_id == current_user_id)

    # Apply optional filters
    if completed is not None:
        statement = statement.where(Todo.completed == completed)

    # Order by created date
    statement = statement.order_by(Todo.created_at.desc())

    # Paginate
    return paginate(db, statement, page=page, page_size=page_size)
```

### 4. Database Session Management

```python
from sqlmodel import Session, create_engine
from contextlib import contextmanager
import os

# Database engine setup
DATABASE_URL = os.getenv("DATABASE_URL")

# Neon Serverless PostgreSQL requires connection pooling configuration
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Dependency for FastAPI endpoints
def get_db():
    """Database session dependency for FastAPI"""
    with Session(engine) as session:
        yield session

# Context manager for manual session handling
@contextmanager
def get_session():
    """Context manager for database sessions"""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
```

## Implementation Checklist

When implementing database operations, ensure:

- [ ] All models include `user_id` field with foreign key and index
- [ ] All CRUD operations filter by authenticated user's ID
- [ ] User ID is retrieved from JWT token, NEVER from request body
- [ ] Database indexes exist on frequently queried fields (user_id, created_at)
- [ ] Pagination is implemented with reasonable default and maximum page sizes
- [ ] Database sessions are properly closed (use FastAPI dependencies)
- [ ] SQLModel models have proper type hints and validation
- [ ] Timestamps (created_at, updated_at) are automatically managed
- [ ] Foreign key relationships are properly defined
- [ ] Database migrations are created for schema changes (Alembic)

## Security Considerations

### Critical Security Rules:

1. **User Isolation (MANDATORY)**
   - ✅ ALWAYS filter queries by `user_id` from JWT token
   - ❌ NEVER trust `user_id` from request body
   - ✅ Verify ownership before update/delete operations
   - ❌ NEVER allow users to access other users' data

2. **SQL Injection Prevention**
   - ✅ Use SQLModel parameterized queries (automatic)
   - ❌ NEVER concatenate SQL strings manually
   - ✅ Validate and sanitize all user inputs

3. **Database Indexes**
   - ✅ Index `user_id` on all user-owned tables
   - ✅ Index frequently queried fields (created_at, completed)
   - ✅ Use composite indexes for multi-column filters

4. **Connection Management**
   - ✅ Use connection pooling for Neon Serverless PostgreSQL
   - ✅ Set appropriate pool size and timeouts
   - ✅ Use `pool_pre_ping` to verify connections

## Environment Variables Required

```env
# Backend (.env)
DATABASE_URL=postgresql://user:password@host/database
```

## Example Usage

### Complete CRUD Endpoint Implementation

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import Optional, List
from uuid import UUID

router = APIRouter(prefix="/api/todos", tags=["todos"])

# Pydantic schemas for request/response
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TodoResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    completed: bool
    user_id: UUID
    created_at: datetime
    updated_at: datetime

# CREATE
@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo_in: TodoCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """Create a new todo for the authenticated user"""
    return crud_todo.create(
        db,
        obj_in=todo_in.dict(),
        user_id=current_user_id
    )

# READ (single)
@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(
    todo_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """Get a specific todo"""
    todo = crud_todo.get(db, id=todo_id, user_id=current_user_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return todo

# READ (list with pagination)
@router.get("/", response_model=PaginatedResponse[TodoResponse])
def list_todos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    completed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """List todos with pagination and filtering"""
    statement = select(Todo).where(Todo.user_id == current_user_id)

    if completed is not None:
        statement = statement.where(Todo.completed == completed)

    statement = statement.order_by(Todo.created_at.desc())

    return paginate(db, statement, page=page, page_size=page_size)

# UPDATE
@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: UUID,
    todo_in: TodoUpdate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """Update a todo"""
    # Filter out None values (partial updates)
    update_data = {k: v for k, v in todo_in.dict().items() if v is not None}

    todo = crud_todo.update(
        db,
        id=todo_id,
        user_id=current_user_id,
        obj_in=update_data
    )
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return todo

# DELETE
@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """Delete a todo"""
    todo = crud_todo.delete(db, id=todo_id, user_id=current_user_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return None
```

## Best Practices

1. **Type Safety**: Use SQLModel type hints and Pydantic validation
2. **Transactions**: Use database sessions properly with automatic commit/rollback
3. **Indexes**: Create indexes on foreign keys and frequently queried fields
4. **Soft Deletes**: Consider adding `is_deleted` flag instead of hard deletes (optional)
5. **Timestamps**: Always include `created_at` and `updated_at` fields
6. **UUID Primary Keys**: Use UUIDs instead of auto-incrementing integers for security
7. **Connection Pooling**: Configure appropriate pool sizes for Neon Serverless
8. **Query Optimization**: Use `select_related` equivalent or joins for related data
9. **Pagination Limits**: Enforce maximum page size to prevent performance issues
10. **Error Handling**: Return appropriate HTTP status codes (404, 403, 500)

## Migration Management (Alembic)

```bash
# Initialize Alembic (one-time setup)
alembic init alembic

# Create a new migration
alembic revision --autogenerate -m "Create todo table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Testing Considerations

- Test CRUD operations with user isolation (ensure users can't access others' data)
- Test pagination edge cases (empty results, page out of bounds)
- Test database connection failures and retries
- Mock database sessions in unit tests
- Use test database for integration tests
- Verify indexes exist in test migrations
- Test concurrent access and race conditions

## Performance Optimization

1. **Eager Loading**: Use `selectinload()` for related objects to avoid N+1 queries
2. **Batch Operations**: Use bulk insert/update for multiple records
3. **Read Replicas**: Configure read replicas for Neon (if available)
4. **Query Caching**: Cache frequently accessed data (Redis integration)
5. **Connection Pooling**: Tune pool size based on expected load
6. **Database Indexes**: Monitor slow queries and add indexes as needed

## Integration Points

- **FastAPI**: Database session dependency injection
- **Better Auth**: User ID extraction from JWT tokens
- **Neon PostgreSQL**: Serverless PostgreSQL with connection pooling
- **Alembic**: Database migration management
- **SQLModel**: Type-safe ORM with Pydantic integration
