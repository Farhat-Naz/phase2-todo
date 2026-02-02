"""
Todo CRUD API endpoints with user-scoped security.

This router implements all todo management endpoints:
- POST /api/todos: Create a new todo
- GET /api/todos: List all todos for the authenticated user
- GET /api/todos/{id}: Get a specific todo (ownership verified)
- PATCH /api/todos/{id}: Update a todo (partial update, ownership verified)
- DELETE /api/todos/{id}: Delete a todo (ownership verified)

Security Architecture (CRITICAL):
- All endpoints require JWT authentication via get_current_user dependency
- user_id is ALWAYS extracted from JWT token (current_user.id)
- user_id is NEVER accepted from request body or query params
- All database queries filter by user_id to enforce data isolation
- Ownership verification: query by id AND user_id before update/delete
- Return 404 (not 403) for unauthorized access to prevent user enumeration

Multi-Tenant Data Isolation:
- Each user sees only their own todos
- Cross-user data access is prevented at the database query level
- Foreign key CASCADE ensures cleanup when user is deleted
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, desc
from typing import List, Annotated, Optional
from uuid import UUID
from datetime import datetime
import logging
import json

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Todo, PriorityLevel
from app.schemas import TodoCreate, TodoUpdate, TodoPublic

# Configure audit logger for priority changes
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# Create router
router = APIRouter(tags=["todos"])

# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
DBSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=TodoPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new todo",
    description=(
        "Create a new todo item for the authenticated user. "
        "The user_id is automatically extracted from the JWT token. "
        "Title is required (1-500 characters), description is optional (max 2000 characters). "
        "Priority is optional ('high' or 'normal', defaults to 'normal')."
    ),
    responses={
        201: {
            "description": "Todo created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "789e4567-e89b-12d3-a456-426614174999",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread, and coffee",
                        "completed": False,
                        "priority": "normal",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        422: {"description": "Validation error - Invalid input data"}
    }
)
async def create_todo(
    todo_data: TodoCreate,
    current_user: CurrentUser,
    db: DBSession
) -> Todo:
    """
    Create a new todo item for the authenticated user.

    Security:
    - user_id is extracted from JWT token (current_user.id)
    - NEVER accept user_id from request body (security vulnerability)
    - Automatically set created_at and updated_at timestamps

    Args:
        todo_data: Todo creation data (title, description, completed)
        current_user: Authenticated user from JWT token
        db: Database session dependency

    Returns:
        Todo: Created todo with all fields including id and timestamps

    Raises:
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 422: If validation fails (e.g., empty title)
    """
    # Create todo with user_id from JWT token (CRITICAL SECURITY)
    todo = Todo(
        user_id=current_user.id,  # ALWAYS from JWT, NEVER from request body
        title=todo_data.title,
        description=todo_data.description,
        completed=todo_data.completed,
        priority=todo_data.priority,  # Optional priority field (defaults to "normal")
    )

    # Add to database and commit
    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo


@router.get(
    "",
    response_model=List[TodoPublic],
    status_code=status.HTTP_200_OK,
    summary="List all todos for the authenticated user",
    description=(
        "Get all todos owned by the authenticated user. "
        "Returns only todos where user_id matches the JWT token. "
        "Supports filtering by priority (priority=high). "
        "Results are ordered by priority (high first), then creation date (newest first)."
    ),
    responses={
        200: {
            "description": "List of todos (may be empty array)",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "user_id": "789e4567-e89b-12d3-a456-426614174999",
                            "title": "Buy groceries",
                            "description": "Milk, eggs, bread, and coffee",
                            "completed": False,
                            "priority": "high",
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-01-15T10:30:00Z"
                        },
                        {
                            "id": "456e4567-e89b-12d3-a456-426614174111",
                            "user_id": "789e4567-e89b-12d3-a456-426614174999",
                            "title": "Finish project",
                            "description": "Complete API documentation",
                            "completed": True,
                            "priority": "normal",
                            "created_at": "2024-01-14T09:15:00Z",
                            "updated_at": "2024-01-15T14:20:00Z"
                        }
                    ]
                }
            }
        },
        401: {"description": "Unauthorized - Invalid or missing JWT token"}
    }
)
async def list_todos(
    current_user: CurrentUser,
    db: DBSession,
    priority: Optional[PriorityLevel] = Query(None, description="Filter by priority level (high or normal)")
) -> List[Todo]:
    """
    List all todos for the authenticated user with optional priority filtering.

    Security (CRITICAL):
    - MANDATORY filter by user_id = current_user.id
    - This prevents data leakage across users (multi-tenant isolation)
    - NEVER return todos from other users

    Performance:
    - user_id is indexed for fast queries
    - priority + created_at composite index optimizes sorting
    - priority index enables efficient filtering

    Args:
        current_user: Authenticated user from JWT token
        db: Database session dependency
        priority: Optional priority filter ("high" or "normal")

    Returns:
        List[Todo]: Todos ordered by priority (high first), then created_at DESC

    Raises:
        HTTPException 401: If JWT token is invalid or missing
    """
    # Build query with MANDATORY user filter (CRITICAL SECURITY)
    statement = select(Todo).where(Todo.user_id == current_user.id)

    # Apply priority filter if provided
    if priority is not None:
        statement = statement.where(Todo.priority == priority)

    # Sort by priority (high first), then creation date (newest first)
    # Boolean sort: (priority == "high") evaluates to True (1) or False (0)
    # DESC order puts 1 (high priority) before 0 (normal priority)
    statement = statement.order_by(
        desc(Todo.priority == "high"),  # High priority first
        desc(Todo.created_at)  # Then newest first
    )

    todos = db.exec(statement).all()
    return todos


@router.get(
    "/{todo_id}",
    response_model=TodoPublic,
    status_code=status.HTTP_200_OK,
    summary="Get a specific todo by ID",
    description=(
        "Get a single todo by its ID. "
        "Only returns the todo if it belongs to the authenticated user. "
        "Returns 404 if todo doesn't exist or belongs to another user."
    ),
    responses={
        200: {
            "description": "Todo found and returned",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "789e4567-e89b-12d3-a456-426614174999",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread, and coffee",
                        "completed": False,
                        "priority": "high",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        404: {"description": "Todo not found or belongs to another user"}
    }
)
async def get_todo(
    todo_id: UUID,
    current_user: CurrentUser,
    db: DBSession
) -> Todo:
    """
    Get a specific todo by ID with ownership verification.

    Security (CRITICAL):
    - Query by id AND user_id (ownership verification)
    - Return 404 (not 403) if not found or belongs to another user
    - This prevents user enumeration attacks

    Args:
        todo_id: UUID of the todo to retrieve
        current_user: Authenticated user from JWT token
        db: Database session dependency

    Returns:
        Todo: Todo with the specified ID

    Raises:
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 404: If todo not found or belongs to another user
    """
    # Query with ownership verification (CRITICAL SECURITY)
    statement = select(Todo).where(
        Todo.id == todo_id,
        Todo.user_id == current_user.id  # MANDATORY - ownership verification
    )

    todo = db.exec(statement).first()

    if todo is None:
        # Return 404 (not 403) to prevent user enumeration
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    return todo


@router.patch(
    "/{todo_id}",
    response_model=TodoPublic,
    status_code=status.HTTP_200_OK,
    summary="Update a todo (partial update)",
    description=(
        "Update a todo with partial data (PATCH semantics). "
        "Only provided fields are updated, omitted fields remain unchanged. "
        "Common use: toggle completion status or priority without modifying title/description. "
        "Priority can be set to 'high' or 'normal'. "
        "Returns 404 if todo doesn't exist or belongs to another user."
    ),
    responses={
        200: {
            "description": "Todo updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "789e4567-e89b-12d3-a456-426614174999",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread, and coffee",
                        "completed": True,
                        "priority": "high",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T14:45:00Z"
                    }
                }
            }
        },
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        404: {"description": "Todo not found or belongs to another user"},
        422: {"description": "Validation error - Invalid input data"}
    }
)
async def update_todo(
    todo_id: UUID,
    todo_update: TodoUpdate,
    current_user: CurrentUser,
    db: DBSession
) -> Todo:
    """
    Update a todo with partial data (PATCH semantics).

    Security (CRITICAL):
    - Query by id AND user_id (ownership verification)
    - Return 404 (not 403) if not found or belongs to another user
    - user_id cannot be changed (enforced by not accepting it in request)
    - updated_at timestamp is automatically updated

    PATCH Semantics:
    - Only provided fields are updated
    - Omitted fields remain unchanged
    - Allows toggling completion without modifying title/description

    Args:
        todo_id: UUID of the todo to update
        todo_update: Update data (all fields optional)
        current_user: Authenticated user from JWT token
        db: Database session dependency

    Returns:
        Todo: Updated todo with new updated_at timestamp

    Raises:
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 404: If todo not found or belongs to another user
        HTTPException 422: If validation fails (e.g., empty title)
    """
    # Query with ownership verification (CRITICAL SECURITY)
    statement = select(Todo).where(
        Todo.id == todo_id,
        Todo.user_id == current_user.id  # MANDATORY - ownership verification
    )

    todo = db.exec(statement).first()

    if todo is None:
        # Return 404 (not 403) to prevent user enumeration
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    # Capture old priority for audit logging
    old_priority = todo.priority

    # Update only provided fields (PATCH semantics)
    update_data = todo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)

    # Automatically update timestamp
    todo.updated_at = datetime.utcnow()

    # Audit logging for priority changes
    if "priority" in update_data and update_data["priority"] != old_priority:
        audit_logger.info(json.dumps({
            "event": "priority_changed",
            "user_id": str(current_user.id),
            "todo_id": str(todo.id),
            "old_priority": old_priority,
            "new_priority": update_data["priority"],
            "timestamp": datetime.utcnow().isoformat()
        }))

    # Commit changes
    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a todo",
    description=(
        "Delete a todo by its ID. "
        "Only deletes the todo if it belongs to the authenticated user. "
        "Returns 404 if todo doesn't exist or belongs to another user. "
        "Returns 204 No Content on success (no response body)."
    ),
    responses={
        204: {"description": "Todo deleted successfully (no content)"},
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        404: {"description": "Todo not found or belongs to another user"}
    }
)
async def delete_todo(
    todo_id: UUID,
    current_user: CurrentUser,
    db: DBSession
) -> None:
    """
    Delete a todo with ownership verification.

    Security (CRITICAL):
    - Query by id AND user_id (ownership verification)
    - Return 404 (not 403) if not found or belongs to another user
    - This prevents user enumeration attacks
    - Hard delete (no soft delete for now)

    Args:
        todo_id: UUID of the todo to delete
        current_user: Authenticated user from JWT token
        db: Database session dependency

    Returns:
        None: 204 No Content (no response body)

    Raises:
        HTTPException 401: If JWT token is invalid or missing
        HTTPException 404: If todo not found or belongs to another user
    """
    # Query with ownership verification (CRITICAL SECURITY)
    statement = select(Todo).where(
        Todo.id == todo_id,
        Todo.user_id == current_user.id  # MANDATORY - ownership verification
    )

    todo = db.exec(statement).first()

    if todo is None:
        # Return 404 (not 403) to prevent user enumeration
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    # Delete todo
    db.delete(todo)
    db.commit()

    # 204 No Content (no return value)
    return None
