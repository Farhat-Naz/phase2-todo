# Feature Specification: Update Todo Task

**Feature Branch**: `004-update-todo`
**Created**: 2026-01-06
**Status**: Draft
**Input**: User description: "Enable authenticated users to update task title, description, or completion status via web interface, REST API, and voice commands (English/Urdu), with partial update support and user data isolation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update Todo via Web Interface (Priority: P1)

Authenticated users can edit todo task details (title, description) or toggle completion status through an intuitive web interface with inline editing and immediate visual feedback.

**Why this priority**: Task updates are essential for maintaining accurate todo lists. Users need to correct typos, add details, and mark tasks complete. Without updates, users would need to delete and recreate tasks, leading to poor UX and data loss. This is critical for basic task management.

**Independent Test**: Can be fully tested by logging in, clicking an edit button on a todo "Buy groceries", modifying the title to "Buy groceries and snacks", saving the changes, and seeing the updated todo appear immediately. Delivers immediate task refinement value.

**Acceptance Scenarios**:

1. **Given** I am logged in with a todo "Buy groceries", **When** I click edit, change the title to "Buy groceries and snacks", and save, **Then** the todo title is updated and persisted
2. **Given** I am viewing a todo, **When** I click edit on the description field, add "Milk, eggs, bread", and save, **Then** the description is updated while title remains unchanged
3. **Given** I have an incomplete todo, **When** I click the checkbox or "Mark complete" button, **Then** the todo's completed status changes to true and visual styling updates (strikethrough, moved to completed section)
4. **Given** I have a completed todo, **When** I click the checkbox again, **Then** the todo's completed status changes to false and returns to active list
5. **Given** I am editing a todo title, **When** I delete all text leaving it empty and try to save, **Then** I see validation error "Title is required" and changes are not saved
6. **Given** I am editing a todo, **When** I click "Cancel" or press Escape, **Then** changes are discarded and original values are restored
7. **Given** I update a todo with Urdu text "دودھ اور روٹی خریدیں", **When** the todo is saved, **Then** the Urdu text displays correctly
8. **Given** I start editing a todo but my token expires mid-edit, **When** I try to save, **Then** I receive "Session expired" error and am redirected to login

---

### User Story 2 - Toggle Completion via Quick Action (Priority: P1)

Authenticated users can quickly toggle todo completion status with a single click/tap without entering edit mode, enabling rapid task management.

**Why this priority**: Marking tasks complete is the most frequent update operation in a todo app. This must be fast, frictionless, and work reliably. Single-click completion is essential for productivity and user satisfaction.

**Independent Test**: Can be fully tested by logging in, viewing a todo list with incomplete tasks, clicking a checkbox next to "Buy milk", seeing it marked complete with visual feedback (strikethrough, checkmark) within 1 second. Delivers instant task completion value.

**Acceptance Scenarios**:

1. **Given** I have an incomplete todo "Call dentist", **When** I click the checkbox next to it, **Then** it is marked complete without opening an edit dialog
2. **Given** I have a completed todo, **When** I click the checkbox, **Then** it is marked incomplete and moved back to active tasks
3. **Given** I toggle completion status, **When** the API request fails due to network error, **Then** the UI reverts to the original state and shows an error message
4. **Given** I rapidly toggle a todo on/off multiple times, **When** all requests complete, **Then** the final state reflects the last user action (no race conditions)
5. **Given** I mark a todo complete, **When** I refresh the page, **Then** the completed status persists

---

### User Story 3 - Update Todo via Voice Command (English) (Priority: P2)

Authenticated users can update todo details or mark tasks complete using voice commands in English, enabling hands-free task management.

**Why this priority**: Voice updates enhance accessibility and convenience, but keyboard/mouse interaction remains available for all update operations. Valuable but not critical for core functionality.

**Independent Test**: Can be fully tested by logging in, having a todo "Buy milk", clicking the microphone button, saying "Complete todo: Buy milk", and seeing the todo marked as completed within 5 seconds. Delivers hands-free update value.

**Acceptance Scenarios**:

1. **Given** I have a todo "Buy milk", **When** I say "Complete todo: Buy milk", **Then** the todo is marked as completed
2. **Given** I have a completed todo "Call dentist", **When** I say "Uncomplete todo: Call dentist" or "Mark incomplete: Call dentist", **Then** the todo is marked as incomplete
3. **Given** I have a todo "Meeting", **When** I say "Update todo: Meeting to Team meeting at 3pm", **Then** the title is updated to "Team meeting at 3pm"
4. **Given** voice input is active, **When** I say "Edit todo: Buy groceries, add description: Milk and bread", **Then** the system prompts me to select the field and enter the description
5. **Given** voice recognition cannot identify the todo with high confidence, **When** I give an update command, **Then** I see a list of possible matches to select from

---

### User Story 4 - Update Todo via Voice Command (Urdu) (Priority: P2)

Authenticated users can update todos using Urdu voice commands, enabling native Urdu speakers to manage tasks in their preferred language.

**Why this priority**: Urdu voice support is a differentiator for Urdu-speaking markets but not essential for core functionality. English interface remains as fallback.

**Independent Test**: Can be fully tested by logging in with an Urdu todo "دودھ خریدیں", clicking the microphone button, speaking "مکمل کریں: دودھ خریدیں" (Complete: Buy milk), and seeing the todo marked complete. Delivers multilingual update value.

**Acceptance Scenarios**:

1. **Given** I have a todo "دودھ خریدیں", **When** I say "مکمل کریں: دودھ خریدیں" (Complete: Buy milk), **Then** the todo is marked complete
2. **Given** I have a completed todo, **When** I say "واپس کریں: روٹی خریدیں" (Undo: Buy bread), **Then** the todo is marked incomplete
3. **Given** I speak a Roman Urdu command "mukammal karen: khareedari", **When** the command is processed, **Then** the matching todo is marked complete
4. **Given** the voice recognition is active in Urdu mode (ur-PK), **When** I speak update commands, **Then** recognition accuracy is at least 80% for common words

---

### User Story 5 - Update Todo via REST API (Priority: P1)

Developers and third-party integrations can update todos programmatically via REST API with support for both full updates (PUT) and partial updates (PATCH), with proper authentication and validation.

**Why this priority**: API update access is essential for extensibility, automation, and third-party integrations. Supports both full replacement and granular field updates for flexibility. Critical for platform value.

**Independent Test**: Can be fully tested by obtaining a JWT token, creating a todo, making a PATCH request to /api/todos/{id} with {"completed": true}, receiving a 200 OK response with updated todo object, and verifying the change persists. Delivers programmatic update value.

**Acceptance Scenarios**:

1. **Given** I have a valid JWT token and a todo with ID "abc-123", **When** I PATCH /api/todos/abc-123 with {"completed": true}, **Then** I receive 200 OK with the updated todo showing completed: true
2. **Given** I have a todo, **When** I PATCH /api/todos/{id} with {"title": "New title"}, **Then** only the title is updated, description and completed remain unchanged
3. **Given** I have a todo, **When** I PUT /api/todos/{id} with complete todo object, **Then** all fields are replaced with the new values
4. **Given** I attempt to update without Authorization header, **When** the request is processed, **Then** I receive 401 Unauthorized
5. **Given** I attempt to update a todo belonging to another user, **When** the request is processed, **Then** I receive 404 Not Found (ownership verification)
6. **Given** I PATCH with {"title": ""} (empty string), **When** validation runs, **Then** I receive 422 Unprocessable Entity with validation error
7. **Given** I PATCH with {"title": "A title with 600 characters..."}, **When** validation runs, **Then** I receive 422 with "Title exceeds maximum length" error
8. **Given** I successfully update a todo as User A, **When** User B queries their todos, **Then** User B does not see User A's updated todo (data isolation)

---

### Edge Cases

- **What happens when** a user tries to update a todo with only whitespace as the title?
  - Frontend trims whitespace and shows validation error if result is empty; backend validates and returns 422 if empty string after trimming

- **What happens when** two users (in a future shared scenario) simultaneously update the same todo?
  - In current single-user MVP, not applicable. In future, last-write-wins with optimistic locking or conflict resolution UI

- **What happens when** a user updates a todo title to be identical to another of their todos?
  - Update succeeds - titles are not unique constraints, users can have duplicate titles with different IDs

- **What happens when** the database connection is lost during an update?
  - User receives "Failed to update todo. Please try again." error, UI reverts to previous state (optimistic update rollback), user can retry when connection restored

- **What happens when** a user's JWT token expires during an edit session (form open for 35 minutes)?
  - On save attempt, backend returns 401, frontend detects expired token, clears session, redirects to login with message "Session expired. Please log in again to save changes."

- **What happens when** a user rapidly toggles completion status (5 times in 2 seconds)?
  - Each request is queued and processed, optimistic UI updates immediately, final state matches last user action; race condition handling ensures consistency

- **What happens when** a user updates a todo while offline?
  - Request fails, user sees "No internet connection" error, changes are not saved; no offline support in MVP (could be added as PWA enhancement)

- **What happens when** voice recognition misinterprets the todo title (user says "Buy milk" but system hears "Buy silk")?
  - System searches for "Buy silk", finds no match or wrong match, displays options with fuzzy matching: "Did you mean: Buy milk?" allowing user to select or retry

- **What happens when** a user tries to update a non-existent todo ID via API?
  - Backend returns 404 Not Found with message "Todo not found"

- **What happens when** a user updates only the description field on a todo that doesn't have a description yet (null)?
  - PATCH successfully adds the description field, title and completed remain unchanged, description changes from null to provided value

- **What happens when** frontend and backend data become out of sync (stale data)?
  - Optimistic updates with conflict detection; if update fails with 409 Conflict (version mismatch), frontend re-fetches latest data and prompts user to review changes

## Requirements *(mandatory)*

### Functional Requirements

- **FR-UPDATE-001**: System MUST require JWT authentication for all todo update operations
- **FR-UPDATE-002**: System MUST validate JWT token signature and expiration before processing update requests
- **FR-UPDATE-003**: System MUST extract user ID from JWT 'sub' claim, NEVER from request body
- **FR-UPDATE-004**: System MUST verify that the todo being updated belongs to the authenticated user (ownership check)
- **FR-UPDATE-005**: System MUST return 404 Not Found if user attempts to update a todo they don't own
- **FR-UPDATE-006**: System MUST return 404 Not Found if the todo ID does not exist in the database
- **FR-UPDATE-007**: System MUST support partial updates via PATCH method (update only provided fields)
- **FR-UPDATE-008**: System MUST support full updates via PUT method (replace entire resource)
- **FR-UPDATE-009**: System MUST validate title field if provided: minimum 1 character after trim, maximum 500 characters
- **FR-UPDATE-010**: System MUST validate description field if provided: maximum 2000 characters, null allowed
- **FR-UPDATE-011**: System MUST validate completed field if provided: boolean type only (true/false)
- **FR-UPDATE-012**: System MUST update the updated_at timestamp to current UTC time on every update
- **FR-UPDATE-013**: System MUST NOT modify created_at timestamp during updates
- **FR-UPDATE-014**: System MUST NOT allow updating the id or user_id fields (immutable)
- **FR-UPDATE-015**: System MUST return 200 OK status code on successful update with complete updated todo object
- **FR-UPDATE-016**: System MUST return 401 Unauthorized for missing, invalid, or expired JWT tokens
- **FR-UPDATE-017**: System MUST return 422 Unprocessable Entity for validation failures with detailed error messages
- **FR-UPDATE-018**: System MUST support Unicode characters (including Urdu script) in title and description updates
- **FR-UPDATE-019**: System MUST sanitize input to prevent XSS attacks (escape HTML/JavaScript)
- **FR-UPDATE-020**: System MUST use parameterized queries (SQLModel) to prevent SQL injection
- **FR-UPDATE-021**: Frontend MUST provide inline editing UI for title and description fields
- **FR-UPDATE-022**: Frontend MUST provide single-click completion toggle (checkbox or button)
- **FR-UPDATE-023**: Frontend MUST implement optimistic UI updates (show changes immediately before API confirmation)
- **FR-UPDATE-024**: Frontend MUST revert optimistic updates if API request fails
- **FR-UPDATE-025**: Frontend MUST show real-time validation feedback during editing (character counts, required fields)
- **FR-UPDATE-026**: Frontend MUST provide "Save" and "Cancel" actions during edit mode
- **FR-UPDATE-027**: Frontend MUST support keyboard shortcuts (Enter to save, Escape to cancel)
- **FR-UPDATE-028**: Frontend MUST display loading states during update operations (spinner, disabled inputs)
- **FR-UPDATE-029**: Frontend MUST display clear error messages when updates fail
- **FR-UPDATE-030**: System MUST support voice commands for completion toggle via Web Speech API
- **FR-UPDATE-031**: System MUST recognize English voice update patterns: "Complete todo:", "Mark done:", "Update todo:"
- **FR-UPDATE-032**: System MUST recognize Urdu voice update patterns: "مکمل کریں:", "mukammal karen:", "update karen:"
- **FR-UPDATE-033**: System MUST extract todo identifier and new values from voice commands
- **FR-UPDATE-034**: System MUST provide visual feedback when voice update command is recognized
- **FR-UPDATE-035**: Frontend MUST ensure updated todos reflect changes immediately without page refresh
- **FR-UPDATE-036**: System MUST log update events for audit purposes (user_id, todo_id, fields_changed, timestamp)
- **FR-UPDATE-037**: Frontend MUST support keyboard navigation for edit controls (accessibility)
- **FR-UPDATE-038**: Frontend MUST announce updates to screen readers (ARIA live regions)
- **FR-UPDATE-039**: System MUST handle concurrent update requests gracefully (prevent race conditions)
- **FR-UPDATE-040**: System MUST preserve data integrity if partial update fails mid-transaction (atomic updates)

### Key Entities

- **Todo** (being updated):
  - Mutable Attributes:
    - title (string, 1-500 characters) - can be updated via PATCH/PUT
    - description (string, 0-2000 characters, nullable) - can be updated via PATCH/PUT
    - completed (boolean) - can be toggled via PATCH/PUT/quick action
    - updated_at (timestamp) - automatically updated on every modification
  - Immutable Attributes:
    - id (UUID) - cannot be changed after creation
    - user_id (UUID) - cannot be changed (ownership is permanent)
    - created_at (timestamp) - cannot be changed
  - Relationships:
    - Belongs to one User (ownership verified before allowing updates)
  - Constraints:
    - Only the owner (user_id matches authenticated user) can update
    - Title cannot be empty if provided in update
    - Validation runs on changed fields for partial updates
    - Full validation runs for PUT (full replacement)

- **User** (referenced, owns todos):
  - Attributes: id (UUID), email, name
  - Relationships: owns many Todos (one-to-many)
  - Update permissions: Only own todos

- **JWT Token** (used for authentication):
  - Attributes: user_id (in 'sub' claim), expiration time
  - Purpose: Securely identify user performing update

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-UPDATE-001**: Users can update a todo and see changes reflected within 1 second for optimistic updates, 2 seconds for server confirmation
- **SC-UPDATE-002**: Completion toggle responds within 500ms at p95 latency (fastest update operation)
- **SC-UPDATE-003**: Todo update API endpoint responds within 400ms at p95 latency under normal load
- **SC-UPDATE-004**: Zero unauthorized users can update todos (100% authentication enforcement verified through security testing)
- **SC-UPDATE-005**: 100% of update attempts verify user ownership (no cross-user updates possible)
- **SC-UPDATE-006**: Optimistic UI updates succeed in 95%+ of cases (revert rate < 5% due to network/validation errors)
- **SC-UPDATE-007**: Voice update command recognition achieves 85% accuracy for common English completion toggles
- **SC-UPDATE-008**: Voice update command recognition achieves 80% accuracy for common Urdu completion toggles
- **SC-UPDATE-009**: System handles 100 concurrent update requests per second without data corruption or race conditions
- **SC-UPDATE-010**: Frontend validation prevents 100% of client-side preventable errors before API submission
- **SC-UPDATE-011**: Backend validation catches and returns appropriate errors for 100% of invalid update requests
- **SC-UPDATE-012**: Updated Urdu text (Unicode) displays correctly in 100% of test cases
- **SC-UPDATE-013**: Zero SQL injection or XSS vulnerabilities in update endpoints (verified through security testing)
- **SC-UPDATE-014**: Update functionality works on mobile devices (down to 320px width) with same success rate as desktop
- **SC-UPDATE-015**: Inline editing UI is accessible via keyboard (100% keyboard navigation support)
- **SC-UPDATE-016**: Screen readers announce update operations correctly in 100% of test cases
- **SC-UPDATE-017**: API documentation completeness for update endpoints: 100% (all parameters, partial vs. full updates, responses, errors)
- **SC-UPDATE-018**: Test coverage for todo update logic reaches at least 90% (unit + integration tests)
- **SC-UPDATE-019**: Zero data loss incidents during updates (atomic transactions, rollback on failure)
- **SC-UPDATE-020**: Users can complete the common workflow (toggle completion) with a single click/tap (0 additional steps)

## Assumptions

1. **User Authentication**: Users are already authenticated with valid JWT tokens before updating todos. Authentication flow is handled by feature 001.

2. **Todo Existence**: Users can only update todos that currently exist in their personal list. Todos have been previously created via feature 002 (Create Todo).

3. **Database Availability**: Neon PostgreSQL database is operational and accessible. Database transactions are supported for atomic updates.

4. **Single-User Ownership**: Each todo belongs to exactly one user. Ownership cannot transfer. Multi-user collaboration is out of scope for MVP.

5. **Browser Support**: Users are using modern evergreen browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+) that support ES6+, Fetch API, modern CSS. Web Speech API support is optional and gracefully degraded.

6. **Network Reliability**: Users have reliable internet connection for API calls. Optimistic UI updates provide immediate feedback, with rollback on failure.

7. **Voice Recognition Accuracy**: Web Speech API provides baseline accuracy for todo title matching and intent recognition. Users in noisy environments or with ambiguous commands will use manual editing.

8. **Character Limits**: Title limit of 500 characters and description limit of 2000 characters are sufficient for 99% of use cases.

9. **Update Frequency**: Most updates are completion toggles (high frequency), followed by title/description edits (moderate frequency). API and database are designed to handle completion toggle as the most common operation.

10. **No Concurrent Editing**: In single-user MVP, same user won't edit same todo from multiple devices simultaneously. Future versions may add conflict resolution for multi-device scenarios.

11. **Validation Consistency**: Frontend and backend validation rules are synchronized. Frontend provides immediate feedback; backend is authoritative source of truth.

12. **Token Validity**: JWT access tokens have 30-minute lifespan (as defined in feature 001). Most edit sessions complete within this window.

13. **Optimistic Updates**: Users prefer immediate visual feedback over waiting for server confirmation. Failed updates can be retried without significant UX degradation.

## Dependencies

### External Dependencies

1. **Neon PostgreSQL**: Cloud database service for todo persistence
   - Risk: Service outage prevents updates from persisting
   - Mitigation: Implement retry logic with exponential backoff, optimistic UI updates with rollback, display clear errors, monitor Neon status

2. **Web Speech API**: Browser-native API for voice recognition (optional)
   - Risk: Limited browser support, accuracy varies
   - Mitigation: Feature detection with graceful degradation, provide manual editing fallback, clearly indicate browser requirements

3. **Better Auth**: JWT token validation (from feature 001)
   - Risk: Auth service failure prevents update authorization
   - Mitigation: Ensure auth dependencies are highly available, implement proper error handling

### Internal Dependencies

1. **Feature 001 (Authentication)**: Users must be logged in with valid JWT tokens before updating todos
   - JWT token validation must be functional
   - User ID extraction from 'sub' claim must be reliable
   - Token expiration handling must redirect to login

2. **Feature 002 (Create Todo)**: Todos must exist before they can be updated
   - Database schema (todos table) must be in place
   - Todos must have proper user_id foreign keys for ownership verification
   - All todo fields (title, description, completed) must be present

3. **Agent Skills**: Implementation must reference established skills
   - **Database Skill** (`.claude/skills/database.skill.md`): User-scoped UPDATE operations, SQLModel patterns, partial vs. full updates, ownership verification
   - **Auth Skill** (`.claude/skills/auth.skill.md`): JWT validation, user extraction, dependency injection for protected endpoints
   - **API Skill** (`.claude/skills/api.skill.md`): PATCH vs. PUT request handling, optimistic updates, error responses, TypeScript interfaces
   - **Voice Skill** (`.claude/skills/voice.skill.md`): Voice command patterns for updates, intent classification for "complete" and "update" actions
   - **UI Skill** (`.claude/skills/ui.skill.md`): Inline editing components, toggle buttons, optimistic UI patterns, loading states, validation feedback, accessibility

4. **Constitution Compliance**: All development must follow constitutional guidelines
   - Agent-driven development (no manual coding)
   - Security-first architecture (JWT validation, ownership verification, prevent cross-user updates)
   - Type safety (TypeScript strict mode, Python type hints)
   - Accessibility (WCAG 2.1 AA for edit controls, keyboard navigation, screen reader support)

### Technical Prerequisites

1. **Frontend Setup**: Next.js 16+ with TypeScript, Tailwind CSS, Better Auth client configured, optimistic update patterns
2. **Backend Setup**: FastAPI with SQLModel, python-jose for JWT, PATCH and PUT endpoint patterns, field-level validation
3. **Database Schema**: `todos` table with updateable fields (title, description, completed, updated_at) and immutable fields (id, user_id, created_at)
4. **Development Environment**: Claude Code agents operational with all 5 skills loaded and accessible

## Out of Scope

The following are explicitly **not** included in this feature specification:

1. **Batch Updates**: Updating multiple todos in a single API call
2. **Bulk Edit UI**: Selecting multiple todos and editing them simultaneously
3. **Update History / Versioning**: Tracking previous values or change history for todos
4. **Undo/Redo**: Reverting to previous todo states
5. **Conflict Resolution**: Handling simultaneous edits from multiple devices (single-device assumption)
6. **Optimistic Locking**: Version numbers or ETags for preventing lost updates (last-write-wins in MVP)
7. **Real-time Sync**: WebSocket updates for multi-device synchronization
8. **Rich Text Editing**: Markdown or WYSIWYG editor for description field (plain text only)
9. **Auto-save**: Automatically saving changes as user types (explicit save required)
10. **Drag-and-Drop Reordering**: Changing todo order or priority (no ordering in MVP)
11. **Due Date Updates**: Setting or modifying due dates (no date fields in MVP)
12. **Priority Updates**: Changing task priority levels (no priority in MVP)
13. **Category/Tag Updates**: Adding or removing categories/tags (no categorization in MVP)
14. **Recurring Task Updates**: Modifying recurrence rules (no recurrence in MVP)
15. **Attachment Updates**: Adding, removing, or editing file attachments (no attachments in MVP)
16. **Collaborative Editing**: Multiple users editing shared todos (single-user MVP)
17. **Change Notifications**: Alerting users when todos are updated (no notifications in MVP)
18. **Export Updates**: Updating todos by importing modified CSV/JSON files

---

**Next Steps**:
- Run `/sp.plan` to create architecture and design plan for todo update implementation
- Run `/sp.clarify` if any requirements need further clarification
- Proceed with `/sp.tasks` after plan approval to generate actionable implementation tasks

---

## Related Documents

- **Parent Feature**: `specs/001-todo-full-stack-app/spec.md` (Overall todo application architecture)
- **Dependency Feature**: `specs/002-create-todo/spec.md` (Todos must exist before updates)
- **Related Feature**: `specs/003-delete-todo/spec.md` (Other CRUD operation)
- **Constitution**: `.specify/memory/constitution.md` (Project governance and security standards)
- **Database Skill**: `.claude/skills/database.skill.md` (UPDATE operations, partial updates, ownership verification)
- **Auth Skill**: `.claude/skills/auth.skill.md` (JWT validation, protected endpoints)
- **API Skill**: `.claude/skills/api.skill.md` (PATCH/PUT request handling, optimistic updates)
- **Voice Skill**: `.claude/skills/voice.skill.md` (Voice update commands, completion toggle patterns)
- **UI Skill**: `.claude/skills/ui.skill.md` (Inline editing, toggle controls, validation UI, accessibility)
