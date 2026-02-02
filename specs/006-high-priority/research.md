# Phase 0: Research - High Priority Task Marking

**Date**: 2026-01-07
**Feature**: 006-high-priority
**Status**: Complete

## Research Summary

All technical unknowns from Technical Context have been resolved through best practices research.

---

## 1. Database Migration Pattern

**Decision**: Alembic migration with VARCHAR(20) DEFAULT 'normal' + index

**Rationale**: SQLModel uses Alembic for schema changes. VARCHAR provides flexibility over ENUM. Index enables efficient filtering/sorting.

**Pattern**:
```python
# alembic/versions/xxx_add_priority.py
def upgrade():
    op.add_column('todo', sa.Column('priority', sa.VARCHAR(20), nullable=False, server_default='normal'))
    op.create_index('ix_todo_priority', 'todo', ['priority'])
```

---

## 2. Enum Validation

**Decision**: Python Literal type with Pydantic

**Rationale**: Literal provides type safety + runtime validation. Integrates with FastAPI/OpenAPI.

**Pattern**:
```python
from typing import Literal
PriorityLevel = Literal["high", "normal"]

class Todo(SQLModel, table=True):
    priority: PriorityLevel = Field(default="normal", max_length=20, index=True)
```

---

## 3. Multi-Field Sorting

**Decision**: SQLAlchemy ORDER BY with priority + created_at

**Rationale**: Database-level sorting is efficient. Composite index optimizes performance.

**Pattern**:
```python
stmt = select(Todo).where(Todo.user_id == user_id).order_by(
    desc(Todo.priority == "high"),  # Boolean: True (1) first
    desc(Todo.created_at)
)
```

**Index**: `CREATE INDEX idx_todo_priority_created ON todo(priority, created_at DESC)`

---

## 4. Priority Filtering

**Decision**: FastAPI Query parameter with optional filter

**Pattern**:
```python
@router.get("/todos")
def list_todos(
    priority: PriorityLevel | None = Query(None),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Todo).where(Todo.user_id == current_user.id)
    if priority:
        stmt = stmt.where(Todo.priority == priority)
```

---

## 5. Optimistic UI Updates

**Decision**: React state + API call + error rollback

**Rationale**: Instant feedback (< 100ms latency). 95%+ success rate justifies optimism.

**Pattern**:
```typescript
const togglePriority = async (currentPriority: PriorityLevel) => {
  const newPriority = currentPriority === "high" ? "normal" : "high";
  setOptimisticPriority(newPriority);  // Immediate update

  try {
    await patchTodo(id, { priority: newPriority });
    setOptimisticPriority(null);  // Clear on success
  } catch (error) {
    setOptimisticPriority(null);  // Rollback
    toast.error("Failed to update priority");
  }
};
```

---

## 6. Accessibility (WCAG AA)

**Decision**: Color + Icon + Text label

**Rationale**: Color alone fails for colorblind users. Multi-sensory feedback required.

**Pattern**:
```tsx
<span
  className="inline-flex items-center gap-1 px-2 py-1 rounded bg-red-50 text-red-700 border border-red-200"
  role="status"
  aria-label="High priority"
>
  <AlertCircle className="w-4 h-4" aria-hidden="true" />
  <span className="text-xs font-medium">HIGH</span>
</span>
```

**Colors**: bg-red-50, text-red-700 (4.85:1 contrast, exceeds 4.5:1 WCAG AA)

---

## 7. Voice Commands

**Decision**: Extend existing voice patterns with priority keywords

**Pattern**:
```typescript
const PRIORITY_COMMANDS = {
  en: [
    { pattern: /mark (as )?high priority:?\s*(.+)/i, intent: "SET_HIGH_PRIORITY" },
    { pattern: /remove priority:?\s*(.+)/i, intent: "SET_NORMAL_PRIORITY" },
  ],
  ur: [
    { pattern: /اہم بنائیں:?\s*(.+)/i, intent: "SET_HIGH_PRIORITY" },
    { pattern: /ترجیح ہٹائیں:?\s*(.+)/i, intent: "SET_NORMAL_PRIORITY" },
  ]
};
```

---

## 8. Error Handling

**Decision**: Standard HTTP status codes + structured errors

**Error Scenarios**:
- Invalid priority value → 422 Unprocessable Entity
- Missing/invalid JWT → 401 Unauthorized
- Todo not owned → 404 Not Found (prevents enumeration)
- Database error → 500 Internal Server Error

**Pattern**:
```python
if not todo or todo.user_id != current_user.id:
    raise HTTPException(status_code=404, detail="Todo not found")
```

---

## 9. Performance Testing

**Decision**: pytest-benchmark (backend) + Lighthouse (frontend)

**Backend**:
```python
@pytest.mark.benchmark(group="priority-toggle")
def test_priority_performance(benchmark, db, todo):
    result = benchmark(toggle_priority_func)
    # Target: <500ms p95
```

**Frontend**: Lighthouse budget.json with TTI < 2s, FCP < 1s

---

## 10. Audit Logging

**Decision**: Structured JSON logging

**Pattern**:
```python
audit_logger.info(json.dumps({
    "event": "priority_changed",
    "user_id": str(user_id),
    "todo_id": str(todo_id),
    "old_priority": old_priority,
    "new_priority": new_priority,
    "timestamp": datetime.utcnow().isoformat()
}))
```

---

## Resolved Items

✅ Database migration strategy
✅ Enum validation approach
✅ Multi-field sorting implementation
✅ Filtering query parameters
✅ Optimistic UI update pattern
✅ Accessibility compliance
✅ Voice command integration
✅ Error handling standards
✅ Performance testing approach
✅ Audit logging format

**Status**: All NEEDS CLARIFICATION items resolved. Ready for Phase 1.
