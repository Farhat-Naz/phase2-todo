# Tasks: High Priority Task Marking

**Input**: Design documents from `/specs/006-high-priority/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md
**Branch**: `006-high-priority`

**Tests**: Tests are not explicitly requested in the specification, so test tasks are omitted. Implementation will use manual validation with quickstart.md scenarios.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/app/`, `frontend/app/`, `frontend/components/`
- Backend: FastAPI with SQLModel (backend/app/)
- Frontend: Next.js 16+ App Router with TypeScript (frontend/)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Minimal project setup (structure already exists from previous features)

- [X] T001 Verify project structure matches plan.md (backend/app/, frontend/ directories)
- [X] T002 [P] Verify Python dependencies include sqlmodel, alembic, fastapi (backend/requirements.txt)
- [X] T003 [P] Verify Node.js dependencies include next, typescript, react (frontend/package.json)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create Alembic migration to add priority column to todos table in backend/alembic/versions/xxx_add_priority_to_todos.py
- [X] T005 Add priority field index in migration: CREATE INDEX idx_todo_priority ON todo(priority)
- [X] T006 Add composite index in migration: CREATE INDEX idx_todo_priority_created ON todo(priority, created_at DESC)
- [X] T007 Run Alembic migration: alembic upgrade head (migration file created, will run on server start)
- [X] T008 [P] Update Todo model with priority field in backend/app/models.py (Literal["high", "normal"])
- [X] T009 [P] Update TodoCreate schema with optional priority field in backend/app/schemas.py
- [X] T010 [P] Update TodoUpdate schema with optional priority field in backend/app/schemas.py
- [X] T011 [P] Update TodoResponse schema to include priority field in backend/app/schemas.py
- [X] T012 [P] Add PriorityLevel type to frontend/types/todo.ts (type PriorityLevel = "high" | "normal")
- [X] T013 [P] Update Todo interface with priority field in frontend/types/todo.ts
- [X] T014 [P] Update TodoCreate interface with optional priority field in frontend/types/todo.ts
- [X] T015 [P] Update TodoUpdate interface with optional priority field in frontend/types/todo.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel ✅

---

## Phase 3: User Story 4 - Update Task Priority via REST API (Priority: P1) 🎯 MVP

**Goal**: Developers and third-party integrations can set or update task priority programmatically via REST API

**Independent Test**: Can be fully tested by obtaining a JWT token, creating a todo, making a PATCH request to /api/todos/{id} with {"priority": "high"}, receiving a 200 OK response with updated todo showing priority: "high"

### Implementation for User Story 4

- [X] T016 [US4] Update GET /todos endpoint to sort by priority (high first) then created_at DESC in backend/app/routers/todos.py
- [X] T017 [US4] Update GET /todos endpoint to support priority query parameter (priority=high) in backend/app/routers/todos.py
- [X] T018 [US4] Update PATCH /todos/{id} endpoint to validate priority field (Literal["high", "normal"]) in backend/app/routers/todos.py
- [X] T019 [US4] Update PATCH /todos/{id} endpoint to update updated_at timestamp when priority changes in backend/app/routers/todos.py
- [X] T020 [US4] Add 422 validation error for invalid priority values in backend/app/routers/todos.py
- [X] T021 [US4] Ensure POST /todos endpoint accepts optional priority field in backend/app/routers/todos.py
- [X] T022 [US4] Add audit logging for priority changes in backend/app/routers/todos.py (structured JSON)
- [X] T023 [US4] Update API client to include priority field in requests in frontend/lib/api.ts

**Checkpoint**: API endpoints functional - can create/update/filter todos with priority via REST API ✅

---

## Phase 4: User Story 1 - Mark Task as High Priority via Web Interface (Priority: P1)

**Goal**: Authenticated users can designate specific todos as high priority through a visual toggle or button

**Independent Test**: Can be fully tested by logging in, viewing a todo "Submit project proposal", clicking a "Mark as High Priority" star/flag icon, and seeing the todo immediately highlighted with a visual indicator

### Implementation for User Story 1

- [X] T024 [P] [US1] Create PriorityToggle component in frontend/components/features/todos/PriorityToggle.tsx (star/flag button)
- [X] T025 [P] [US1] Implement optimistic UI update logic in PriorityToggle component with error rollback
- [X] T026 [P] [US1] Add keyboard accessibility to PriorityToggle (Tab navigation, Enter to toggle, aria-label)
- [X] T027 [P] [US1] Add screen reader announcement for priority changes in PriorityToggle component
- [X] T028 [US1] Update useTodos hook to include togglePriority function in frontend/hooks/useTodos.ts
- [X] T029 [US1] Integrate PriorityToggle into TodoItem component in frontend/components/features/todos/TodoItem.tsx
- [X] T030 [US1] Ensure priority toggle has 44x44px minimum touch target for mobile in PriorityToggle.tsx
- [X] T031 [US1] Add loading state to priority toggle during API request in PriorityToggle.tsx

**Checkpoint**: Users can toggle priority via web interface with instant feedback and error handling

---

## Phase 5: User Story 5 - View Priority in Todo List and Details (Priority: P1)

**Goal**: Authenticated users can clearly see which todos are high priority through consistent visual indicators

**Independent Test**: Can be fully tested by logging in with a mix of high and normal priority todos, viewing the list, and confirming high priority todos have clear visual distinction (color badge, star icon, or "HIGH" label)

### Implementation for User Story 5

- [X] T032 [P] [US5] Create PriorityBadge component in frontend/components/features/todos/PriorityBadge.tsx (color + icon + text)
- [X] T033 [P] [US5] Implement WCAG AA compliant colors in PriorityBadge (bg-red-50, text-red-700, 4.5:1 contrast)
- [X] T034 [P] [US5] Add AlertCircle icon and "HIGH" text label to PriorityBadge component
- [X] T035 [P] [US5] Add role="status" and aria-label="High priority" to PriorityBadge for accessibility
- [X] T036 [US5] Integrate PriorityBadge into TodoItem component in frontend/components/features/todos/TodoItem.tsx
- [X] T037 [US5] Display PriorityBadge in todo list view in frontend/components/features/todos/TodoList.tsx
- [X] T038 [US5] Ensure PriorityBadge displays correctly in RTL layout for Urdu in frontend/components/features/todos/PriorityBadge.tsx
- [X] T039 [US5] Verify PriorityBadge responsive design at 320px width in PriorityBadge.tsx
- [X] T040 [US5] Add high priority count badge to UI in frontend/components/features/todos/TodoList.tsx ("3 urgent tasks")

**Checkpoint**: High priority todos are clearly visible with color, icon, and text indicators across all views

---

## Phase 6: User Story 2 - Filter and View High Priority Tasks (Priority: P1)

**Goal**: Authenticated users can filter their todo list to show only high priority tasks

**Independent Test**: Can be fully tested by logging in with 2 high priority and 3 normal priority todos, clicking a "High Priority" filter button, and seeing only the 2 high priority todos displayed

### Implementation for User Story 2

- [X] T041 [P] [US2] Create PriorityFilter component in frontend/components/features/todos/PriorityFilter.tsx (filter button/tabs)
- [X] T042 [P] [US2] Add "All Tasks" and "High Priority" filter tabs in PriorityFilter component
- [X] T043 [P] [US2] Implement filter state management in useTodos hook in frontend/hooks/useTodos.ts
- [X] T044 [US2] Update TodoList to apply priority filter from state in frontend/components/features/todos/TodoList.tsx
- [X] T045 [US2] Add empty state when high priority filter shows no results in frontend/components/features/todos/TodoList.tsx
- [X] T046 [US2] Persist filter state in URL query parameters (priority=high) in frontend/components/features/todos/TodoList.tsx
- [X] T047 [US2] Ensure filter persists across page refreshes in frontend/components/features/todos/TodoList.tsx
- [X] T048 [US2] Update API client to support priority query parameter in frontend/lib/api.ts

**Checkpoint**: Users can filter to view only high priority tasks with proper empty states

---

## Phase 7: User Story 3 - Set Priority via Voice Command (English/Urdu) (Priority: P2)

**Goal**: Authenticated users can mark tasks as high priority using voice commands in English or Urdu

**Independent Test**: Can be fully tested by logging in with a todo "Call client", clicking the microphone button, saying "Mark as high priority: Call client", and seeing the todo immediately marked with a priority indicator

### Implementation for User Story 3

- [X] T049 [P] [US3] Add priority command patterns to frontend/lib/voice.ts
- [X] T050 [P] [US3] Add English patterns: "mark (as )?high priority:?\s*(.+)" → SET_HIGH_PRIORITY intent
- [X] T051 [P] [US3] Add English patterns: "remove priority:?\s*(.+)" → SET_NORMAL_PRIORITY intent
- [X] T052 [P] [US3] Add Urdu patterns: "اہم بنائیں:?\s*(.+)" → SET_HIGH_PRIORITY intent
- [X] T053 [P] [US3] Add Urdu patterns: "ترجیح ہٹائیں:?\s*(.+)" → SET_NORMAL_PRIORITY intent
- [X] T054 [US3] Implement priority intent handler in frontend/hooks/useVoice.ts to call togglePriority function
- [X] T055 [US3] Add voice command feedback messages for priority changes in frontend/hooks/useVoice.ts
- [X] T056 [US3] Handle voice recognition errors with fallback to manual toggle (built into useVoice hook)
- [X] T057 [US3] Add "Did you mean?" suggestions when todo title not found in frontend/hooks/useVoice.ts

**Checkpoint**: Users can set priority via voice commands in English and Urdu with error handling

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T058 [P] Update i18n translations for priority UI in frontend/messages/en.json
- [X] T059 [P] Update i18n translations for priority UI in frontend/messages/ur.json
- [X] T060 [P] Add priority-related translations: "High Priority", "Mark as high priority", "Remove priority"
- [X] T061 [P] Add priority-related translations (Urdu): "زیادہ ترجیح", "اہم بنائیں", "ترجیح ہٹائیں"
- [X] T062 Verify all 6 acceptance scenarios for User Story 1 (mark, view, toggle, persist, sort, completed)
- [X] T063 Verify all 6 acceptance scenarios for User Story 2 (filter, show all, add while filtered, remove while filtered, persist, empty state)
- [X] T064 Verify all 5 acceptance scenarios for User Story 3 (English voice, remove voice, Urdu voice, multiple matches, error handling)
- [X] T065 Verify all 6 acceptance scenarios for User Story 4 (API PATCH, remove priority API, 401 auth, 404 ownership, 422 validation, GET sorting)
- [X] T066 Verify all 6 acceptance scenarios for User Story 5 (list view indicator, detail view indicator, completed indicator, mobile 320px, RTL Urdu, screen reader)
- [X] T067 [P] Validate quickstart.md scenarios: mark task, filter, voice command, API usage
- [X] T068 [P] Test performance: priority toggle responds within 500ms at p95 latency
- [X] T069 [P] Test accessibility: WCAG AA compliance for color contrast, keyboard navigation, screen readers
- [X] T070 [P] Verify security: SQL injection prevention, JWT validation, ownership verification
- [X] T071 Run database migration rollback test (downgrade then upgrade)
- [X] T072 [P] Update API documentation with priority field examples in backend/app/routers/todos.py docstrings
- [X] T073 Final validation: All 35 functional requirements (FR-PRIORITY-001 to FR-PRIORITY-035) satisfied
- [X] T074 Final validation: All 20 success criteria (SC-PRIORITY-001 to SC-PRIORITY-020) met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US4 (API) - Phase 3: Foundation for all other stories
  - US1 (Toggle) - Phase 4: Depends on API (Phase 3)
  - US5 (Visual) - Phase 5: Works with US1 (Phase 4)
  - US2 (Filter) - Phase 6: Depends on API (Phase 3) and Visual (Phase 5)
  - US3 (Voice) - Phase 7: Depends on US1 (Phase 4) for toggle function
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 4 (P1) - API**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 1 (P1) - Toggle**: Depends on US4 (API endpoints must exist)
- **User Story 5 (P1) - Visual**: Depends on US1 (works together with toggle)
- **User Story 2 (P1) - Filter**: Depends on US4 (API filtering) and US5 (visual indicators)
- **User Story 3 (P2) - Voice**: Depends on US1 (uses toggle function)

### Within Each User Story

- Backend models/schemas before endpoints
- API endpoints before frontend components
- Core components before integration
- Accessibility features integrated with components (not added later)
- Story complete before moving to next priority

### Parallel Opportunities

- Phase 1: All tasks marked [P] can run in parallel (T002, T003)
- Phase 2: All tasks marked [P] can run in parallel (T008-T015)
- Within each user story: All tasks marked [P] can run in parallel
- Once Foundational phase completes, user stories can be implemented by priority order

---

## Parallel Example: Foundational Phase (Phase 2)

```bash
# After migration tasks (T004-T007) complete, launch in parallel:
Task: "Update Todo model with priority field in backend/app/models.py"
Task: "Update TodoCreate schema in backend/app/schemas.py"
Task: "Update TodoUpdate schema in backend/app/schemas.py"
Task: "Update TodoResponse schema in backend/app/schemas.py"
Task: "Add PriorityLevel type to frontend/types/todo.ts"
Task: "Update Todo interface in frontend/types/todo.ts"
Task: "Update TodoCreate interface in frontend/types/todo.ts"
Task: "Update TodoUpdate interface in frontend/types/todo.ts"
```

---

## Implementation Strategy

### MVP First (User Story 4 + User Story 1 Only)

1. Complete Phase 1: Setup (verify structure)
2. Complete Phase 2: Foundational (CRITICAL - database migration, type updates)
3. Complete Phase 3: User Story 4 (API endpoints)
4. Complete Phase 4: User Story 1 (Web toggle)
5. **STOP and VALIDATE**: Test API and web toggle independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 4 (API) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 1 (Toggle) → Test independently → Deploy/Demo
4. Add User Story 5 (Visual) → Test independently → Deploy/Demo
5. Add User Story 2 (Filter) → Test independently → Deploy/Demo
6. Add User Story 3 (Voice - P2) → Test independently → Deploy/Demo
7. Polish and final validation
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 4 (API) - MUST complete first
3. After US4 completes:
   - Developer A: User Story 1 (Toggle)
   - Developer B: User Story 5 (Visual)
4. After US1 and US5 complete:
   - Developer A: User Story 2 (Filter)
   - Developer B: User Story 3 (Voice)
5. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies within the phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Migration tasks (T004-T007) must run sequentially in order
- API (US4) must complete before frontend user stories (US1, US2, US3, US5)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Follow constitution: agent-driven development, security-first, type safety, accessibility
- Reference established skills: Database Skill (migration), Auth Skill (JWT), API Skill (endpoints), Voice Skill (commands), UI Skill (components)
