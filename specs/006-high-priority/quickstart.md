# Quickstart: High Priority Task Marking

**Feature**: 006-high-priority
**Date**: 2026-01-07

## For Developers

### Backend Setup (FastAPI)

1. **Run database migration**:
   ```bash
   cd backend
   uv sync  # Sync dependencies
   alembic upgrade head  # Apply priority column migration
   ```

2. **Update models and schemas** (backend/app/models.py, schemas.py):
   - Add `priority` field to Todo model with Literal["high", "normal"] type
   - Update TodoCreate and TodoUpdate schemas to include optional priority field

3. **Update endpoints** (backend/app/routers/todos.py):
   - Add `priority` query parameter to GET /todos for filtering
   - Update ORDER BY to sort by priority (high first), then created_at
   - Ensure PATCH endpoint validates priority enum values

4. **Test priority operations**:
   ```bash
   uv run pytest tests/test_priority_api.py -v
   ```

### Frontend Setup (Next.js)

1. **Update TypeScript types** (types/todo.ts):
   ```typescript
   export type PriorityLevel = "high" | "normal";
   export interface Todo {
     // ... existing fields
     priority: PriorityLevel;
   }
   ```

2. **Create priority components**:
   - `PriorityBadge.tsx`: Visual indicator (color + icon + text)
   - `PriorityToggle.tsx`: Star/flag button for toggling priority
   - `PriorityFilter.tsx`: Filter button for high priority view

3. **Update existing components**:
   - `TodoList.tsx`: Display priority badges, apply filtering
   - `TodoItem.tsx`: Add priority toggle button
   - `lib/api.ts`: Add priority field to PATCH requests

4. **Test priority UI**:
   ```bash
   pnpm test -- PriorityToggle
   pnpm test:e2e -- priority.spec.ts
   ```

---

## For Users

### How to Mark a Task as High Priority

**Web Interface**:
1. Find the task in your todo list
2. Click the ⭐ star icon or flag button next to the task
3. The task will immediately show a "HIGH" badge and move to the top of your list

**Voice Command (English)**:
- Say: "Mark as high priority: Buy groceries"
- Say: "Set priority high: Call client"

**Voice Command (Urdu)**:
- Say: "اہم بنائیں: گروسری خریدیں" (Mark important: Buy groceries)

### How to Filter High Priority Tasks

1. Click the "High Priority" or "Urgent" filter button
2. Only high priority tasks will be shown
3. Click "All Tasks" to see all todos again

### How to Remove Priority

**Web Interface**:
- Click the same ⭐ star/flag icon again to remove priority
- The task returns to normal priority and moves back in the list

**Voice Command**:
- Say: "Remove priority: Buy groceries"
- Say (Urdu): "ترجیح ہٹائیں: گروسری خریدیں"

---

## API Usage

### Mark a Todo as High Priority

```bash
curl -X PATCH http://localhost:8000/api/todos/TODO_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"priority": "high"}'
```

### Filter High Priority Todos

```bash
curl -X GET "http://localhost:8000/api/todos?priority=high" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Create a Todo with High Priority

```bash
curl -X POST http://localhost:8000/api/todos \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Urgent: Submit project proposal",
    "priority": "high"
  }'
```

---

## Key Implementation Points

### Backend
- Priority field: VARCHAR(20) with values "high" | "normal"
- Default: "normal" for backwards compatibility
- Indexed for filtering/sorting performance
- JWT authentication required for all priority operations
- Ownership verification before updates (404 if not owned)

### Frontend
- Optimistic UI updates (instant feedback, rollback on error)
- Visual indicators: Color + Icon + Text (WCAG AA compliant)
- 44x44px touch targets for mobile
- Keyboard accessible (Tab navigation, Enter to toggle)
- Screen reader support ("High priority: [task title]")

### Sorting
- High priority todos always appear first
- Within same priority level, sort by created_at DESC
- Persists across page refreshes and filters

---

## Troubleshooting

**Priority toggle doesn't work**:
- Check JWT token is valid (not expired)
- Verify you own the todo (cannot set priority on others' todos)
- Check browser console for API errors

**High priority todos not sorting correctly**:
- Refresh the page to force re-fetch from server
- Verify backend ORDER BY includes priority field
- Check composite index on (priority, created_at) exists

**Voice commands not recognized**:
- Ensure microphone permission granted
- Check browser supports Web Speech API
- Verify language setting matches command (en-US or ur-PK)
- Fall back to manual toggle if voice fails

---

## Next Steps

After implementing priority marking:
1. Run `/sp.tasks` to generate implementation tasks
2. Execute tasks with specialized agents (Database Architect, Backend Guardian, Frontend Builder)
3. Test all acceptance scenarios from spec.md
4. Create PR with `/sp.git.commit_pr`

**Dependencies**: Requires authentication (feature 001) and todo CRUD operations (features 002-005) to be functional.
