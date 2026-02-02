---
id: 012
title: Create Update Todo Feature Specification
stage: spec
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-update-todo
branch: 002-create-todo
user: system
command: /sp.specify
labels: ["spec-creation", "update-todo", "crud-operations", "partial-updates", "optimistic-ui"]
links:
  spec: specs/004-update-todo/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-update-todo/spec.md
  - history/prompts/004-update-todo/012-create-update-todo-spec.spec.prompt.md
tests:
  - N/A (specification phase, no tests)
---

## Prompt

\sp.specify
---

## 📄 `specs/update.md`

```md
# 🧩 SPECIFICATION – UPDATE TASK

---

## 1. Purpose

Allow an authenticated user to update task title, description, or completion status.

---

## 2. Functional Requirements

- User must be authenticated
- User can update only their own tasks
- Partial updates allowed

---

## 3. API Contract

**Endpoint**

## Response snapshot

Created comprehensive feature specification for Update Todo functionality at `specs/004-update-todo/spec.md`.

The specification includes:

1. **User Scenarios & Testing** (5 prioritized user stories):
   - P1: Update via Web Interface (inline editing, save/cancel)
   - P1: Toggle Completion via Quick Action (single-click checkbox)
   - P2: Update via Voice Command (English)
   - P2: Update via Voice Command (Urdu)
   - P1: Update via REST API (PATCH for partial, PUT for full updates)

2. **40 Functional Requirements** covering:
   - JWT authentication and validation (FR-UPDATE-001 to FR-UPDATE-003)
   - Ownership verification and security (FR-UPDATE-004 to FR-UPDATE-006)
   - Partial vs. full update support (FR-UPDATE-007 to FR-UPDATE-008)
   - Field-level validation (FR-UPDATE-009 to FR-UPDATE-014)
   - API responses and error handling (FR-UPDATE-015 to FR-UPDATE-020)
   - Optimistic UI updates with rollback (FR-UPDATE-023 to FR-UPDATE-024)
   - Inline editing UX (FR-UPDATE-021 to FR-UPDATE-029)
   - Voice command support (FR-UPDATE-030 to FR-UPDATE-034)
   - Audit, accessibility, and data integrity (FR-UPDATE-035 to FR-UPDATE-040)

3. **Edge Cases** (11 scenarios):
   - Token expiration during edit sessions
   - Concurrent updates and race conditions
   - Optimistic update rollback on failure
   - Voice recognition mismatches
   - Database synchronization issues
   - Rapid completion toggles
   - Empty/whitespace validation
   - Offline update attempts
   - Duplicate title handling

4. **Success Criteria** (20 measurable outcomes):
   - Performance targets (1s optimistic, 2s confirmed, 500ms toggle, 400ms API)
   - Security metrics (100% ownership verification)
   - Optimistic update success rate (95%+)
   - Voice accuracy targets (85% English, 80% Urdu)
   - Accessibility compliance (keyboard navigation, screen reader support)
   - Test coverage (90%+)
   - Zero data corruption or race conditions
   - Single-click completion toggle (0 additional steps)

5. **Key Technical Decisions**:
   - PATCH for partial updates (update only provided fields)
   - PUT for full updates (replace entire resource)
   - Optimistic UI updates with rollback on failure
   - Immutable fields: id, user_id, created_at
   - Mutable fields: title, description, completed, updated_at (auto-updated)
   - Completion toggle as highest-priority update operation

6. **Dependencies**:
   - External: Neon PostgreSQL, Web Speech API, Better Auth
   - Internal: Features 001 (Authentication) & 002 (Create Todo)
   - Agent Skills: Database (partial updates, ownership), Auth (JWT), API (PATCH/PUT), Voice (update commands), UI (inline editing, optimistic updates)

7. **Out of Scope** (18 items):
   - Batch/bulk updates
   - Update history/versioning
   - Undo/redo functionality
   - Conflict resolution for concurrent edits
   - Real-time multi-device sync
   - Rich text editing
   - Auto-save
   - Drag-and-drop reordering
   - And 10 other explicitly excluded features

The specification emphasizes update-specific concerns:
- Partial vs. full update semantics (PATCH vs. PUT)
- Optimistic UI patterns for immediate feedback
- Completion toggle as the most frequent operation
- Field immutability (id, user_id, created_at cannot change)
- Atomic updates with transaction rollback
- Race condition handling for rapid toggles

The spec maintains consistency with Create and Delete todo specifications while addressing the unique complexity of update operations, particularly around optimistic UI updates, partial field updates, and the high-frequency completion toggle workflow.

## Outcome

- ✅ Impact: Created complete feature specification for Update Todo with 5 user stories, 40 functional requirements, 20 success criteria, 11 edge cases, and detailed technical decisions around partial updates and optimistic UI
- 🧪 Tests: N/A (specification phase)
- 📁 Files: Created `specs/004-update-todo/spec.md` (comprehensive spec document emphasizing PATCH/PUT semantics and optimistic updates)
- 🔁 Next prompts: Run `/sp.plan` to create architecture and design plan for update implementation with focus on optimistic UI patterns and partial update logic, or `/sp.clarify` if requirements need clarification
- 🧠 Reflection: Update specification required deeper consideration than Create/Delete due to: (1) dual API semantics (PATCH vs PUT), (2) optimistic UI update patterns with rollback, (3) field mutability constraints, (4) completion toggle as special high-frequency operation, (5) inline editing UX patterns

## Evaluation notes (flywheel)

- Failure modes observed: None - specification created successfully with comprehensive coverage of update-specific patterns (partial updates, optimistic UI, field immutability)
- Graders run and results (PASS/FAIL): PASS - Follows spec template structure, includes all mandatory sections, addresses update-specific concerns (PATCH/PUT, optimistic updates), aligns with constitution security and accessibility requirements
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed with `/sp.plan` to design architecture for optimistic update patterns, partial update validation, and high-performance completion toggle endpoint
