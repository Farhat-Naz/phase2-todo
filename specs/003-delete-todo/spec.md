# Feature Specification: Delete Todo Task

**Feature Branch**: `003-delete-todo`
**Created**: 2026-01-06
**Status**: Draft
**Input**: User description: "Enable authenticated users to permanently delete their todo tasks via web interface, REST API, and voice commands (English/Urdu), with confirmation prompts and user data isolation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delete Todo via Web Interface (Priority: P1)

Authenticated users can permanently delete individual todo tasks from their personal list using a delete button or action, with visual confirmation to prevent accidental deletions.

**Why this priority**: Task deletion is a core CRUD operation essential for maintaining a clean, usable todo list. Without deletion, users accumulate unwanted tasks, making the app cluttered and unusable. This is critical for basic task management.

**Independent Test**: Can be fully tested by logging in, viewing the todo list, clicking a delete button on a specific todo (e.g., "Buy milk"), confirming the deletion when prompted, and verifying the todo is removed from the list within 2 seconds. Delivers immediate task management value.

**Acceptance Scenarios**:

1. **Given** I am logged in and have a todo "Buy groceries" in my list, **When** I click the delete button and confirm the action, **Then** the todo is permanently removed from my list
2. **Given** I am viewing my todo list, **When** I click delete on a todo, **Then** I see a confirmation dialog asking "Are you sure you want to delete this todo?"
3. **Given** a confirmation dialog is shown, **When** I click "Cancel", **Then** the todo is NOT deleted and remains in my list
4. **Given** a confirmation dialog is shown, **When** I click "Confirm" or "Delete", **Then** the todo is permanently deleted
5. **Given** I have deleted a todo, **When** I refresh the page, **Then** the deleted todo does NOT reappear (deletion persisted to database)
6. **Given** I attempt to delete a todo, **When** the deletion fails due to network error, **Then** I see an error message "Failed to delete todo. Please try again." and the todo remains in the list
7. **Given** I have a todo list with multiple items, **When** I delete one todo, **Then** only that specific todo is removed and other todos remain unchanged
8. **Given** I am viewing a todo with Urdu text "دودھ خریدیں", **When** I delete it with confirmation, **Then** the Urdu todo is successfully removed

---

### User Story 2 - Delete Todo via Voice Command (English) (Priority: P2)

Authenticated users can delete todos hands-free by speaking voice commands in English, enabling quick task removal while performing other activities.

**Why this priority**: Voice deletion enhances accessibility and user experience, but keyboard/mouse interaction remains available for all deletion tasks. This is valuable but not critical for core functionality.

**Independent Test**: Can be fully tested by logging in, having a todo "Buy milk" in the list, clicking the microphone button, speaking "Delete todo: Buy milk", confirming the voice-initiated deletion, and seeing the todo removed from the list within 5 seconds. Delivers hands-free task management value.

**Acceptance Scenarios**:

1. **Given** I am logged in with a todo "Buy milk", **When** I say "Delete todo: Buy milk" and confirm, **Then** the todo is permanently deleted
2. **Given** voice input is active, **When** I say "Remove task: Schedule meeting", **Then** the system identifies the todo and prompts for confirmation
3. **Given** I have initiated voice deletion, **When** the system finds multiple todos with similar names, **Then** it shows me options to select which todo to delete
4. **Given** I say "Delete todo: Nonexistent task", **When** the system processes the command, **Then** I see a message "No todo found with that title"
5. **Given** my browser doesn't support Web Speech API, **When** I visit the dashboard, **Then** the voice delete functionality is unavailable and I must use the UI button
6. **Given** voice recognition is unclear, **When** the system cannot identify the todo title with high confidence, **Then** I am prompted to retry or use manual selection

---

### User Story 3 - Delete Todo via Voice Command (Urdu) (Priority: P2)

Authenticated users can delete todos using Urdu voice commands, enabling native Urdu speakers to manage tasks in their preferred language.

**Why this priority**: Urdu voice support is a differentiator for Urdu-speaking markets but not essential for core functionality. English interface remains as fallback.

**Independent Test**: Can be fully tested by logging in with an Urdu todo "دودھ خریدیں", clicking the microphone button, speaking "حذف کریں: دودھ خریدیں" or "delete karen: doodh kharidein", confirming the deletion, and seeing the todo removed. Delivers multilingual accessibility value.

**Acceptance Scenarios**:

1. **Given** I am logged in with a todo "دودھ خریدیں", **When** I say "حذف کریں: دودھ خریدیں" and confirm, **Then** the Urdu todo is deleted
2. **Given** I am using voice input, **When** I say "mitta do: روٹی خریدیں" (Delete: Buy bread), **Then** the system identifies the todo and requests confirmation
3. **Given** I speak a Roman Urdu command "delete karen: khareedari", **When** the command is processed, **Then** the system finds the matching todo and prompts for confirmation
4. **Given** the voice recognition is active in Urdu mode (ur-PK), **When** I speak delete commands, **Then** recognition accuracy is at least 80% for common Urdu words
5. **Given** I deny microphone permissions, **When** I attempt voice deletion, **Then** I see instructions in Urdu on how to enable permissions or use the delete button instead

---

### User Story 4 - Delete Todo via REST API (Priority: P1)

Developers and third-party integrations can delete todos programmatically via REST API with proper authentication, ownership verification, and error handling.

**Why this priority**: API access is essential for extensibility, automation, and integration with other systems. This enables chatbot integration and third-party tool support, which is critical for platform value.

**Independent Test**: Can be fully tested by obtaining a JWT token via /api/auth/login, creating a todo via POST /api/todos, making a DELETE request to /api/todos/{id} with valid token, receiving a 204 No Content response, and verifying the todo no longer exists via GET request. Delivers programmatic deletion value.

**Acceptance Scenarios**:

1. **Given** I have a valid JWT token and a todo with ID "abc-123", **When** I DELETE /api/todos/abc-123, **Then** I receive 204 No Content status and the todo is permanently deleted
2. **Given** I make a DELETE request without Authorization header, **When** the request is processed, **Then** I receive 401 Unauthorized status
3. **Given** I attempt to delete a todo that belongs to another user, **When** the request is processed, **Then** I receive 404 Not Found status (ownership verification prevents access)
4. **Given** I attempt to delete a non-existent todo ID, **When** the request is processed, **Then** I receive 404 Not Found status
5. **Given** I have a valid JWT token but it has expired, **When** I DELETE /api/todos/{id}, **Then** I receive 401 Unauthorized with error message "Token expired"
6. **Given** I successfully delete a todo as User A, **When** User A queries their todo list, **Then** the deleted todo does NOT appear
7. **Given** the database connection is lost during deletion, **When** the request is processed, **Then** I receive 500 Internal Server Error with retry guidance

---

### Edge Cases

- **What happens when** a user tries to delete a todo while another user is simultaneously viewing that same todo (in a shared/collaborative scenario)?
  - In the current single-user MVP, this is not applicable as todos are strictly user-scoped. In future multi-user features, this would trigger real-time updates via WebSockets to notify other viewers.

- **What happens when** a user's JWT token expires mid-deletion (between clicking delete and confirming)?
  - On confirmation submission, backend returns 401 Unauthorized, frontend detects expired token, clears session, redirects to login with message "Session expired. Please log in again."

- **What happens when** a user attempts to delete the same todo twice in rapid succession (double-click or API retry)?
  - First request deletes the todo successfully (204 No Content). Second request receives 404 Not Found as the todo no longer exists. This is idempotent behavior - no error state, just confirmation of non-existence.

- **What happens when** the database is down during deletion attempt?
  - Backend cannot connect to database, returns 500 Internal Server Error with message "Service temporarily unavailable. Please try again." Todo remains in the list, user can retry when database is restored.

- **What happens when** a user deletes their last remaining todo?
  - Todo is successfully deleted, list becomes empty, user sees empty state message like "No todos yet. Create your first task!" with a call-to-action to add a new todo.

- **What happens when** voice recognition picks up incorrect todo title (e.g., user says "Buy milk" but system hears "Buy silk")?
  - System searches for "Buy silk", finds no match, displays "No todo found with that title. Did you mean: Buy milk?" with fuzzy matching suggestions, allowing user to select correct todo or retry voice input.

- **What happens when** a user deletes a completed vs. uncompleted todo?
  - Deletion works identically for both completed and uncompleted todos. Completion status does not affect deletion permissions or behavior.

- **What happens when** a user cancels the confirmation dialog multiple times?
  - Each cancellation closes the dialog and preserves the todo. No limit on cancellations - user can change their mind indefinitely until they confirm or navigate away.

- **What happens when** network connectivity is lost after user confirms deletion but before request completes?
  - Request fails, user sees "Network error. Failed to delete todo." message. Todo remains in the list on frontend. User can retry when connectivity is restored.

- **What happens when** a user deletes todos while on page 2 of a paginated list, causing the current page to become empty?
  - After deletion, if current page is empty but previous pages have items, user is automatically navigated to the last non-empty page. If entire list is empty, user sees empty state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-DELETE-001**: System MUST require JWT authentication for all todo deletion operations
- **FR-DELETE-002**: System MUST validate JWT token signature and expiration before processing deletion requests
- **FR-DELETE-003**: System MUST extract user ID from JWT 'sub' claim, NEVER from request body
- **FR-DELETE-004**: System MUST verify that the todo being deleted belongs to the authenticated user (ownership check)
- **FR-DELETE-005**: System MUST return 404 Not Found if user attempts to delete a todo they don't own (prevent user enumeration)
- **FR-DELETE-006**: System MUST return 404 Not Found if the todo ID does not exist in the database
- **FR-DELETE-007**: System MUST permanently remove the todo from the database (hard delete, not soft delete in MVP)
- **FR-DELETE-008**: System MUST return 204 No Content status code on successful deletion
- **FR-DELETE-009**: System MUST return 401 Unauthorized for missing, invalid, or expired JWT tokens
- **FR-DELETE-010**: System MUST use parameterized queries (SQLModel) to prevent SQL injection in DELETE operations
- **FR-DELETE-011**: System MUST execute deletion within a database transaction to ensure atomicity
- **FR-DELETE-012**: Frontend MUST display a confirmation dialog before deleting a todo
- **FR-DELETE-013**: Frontend MUST show the todo title in the confirmation dialog for user clarity
- **FR-DELETE-014**: Frontend MUST provide "Cancel" and "Confirm/Delete" actions in the confirmation dialog
- **FR-DELETE-015**: Frontend MUST update the todo list immediately after successful deletion (remove deleted item from UI)
- **FR-DELETE-016**: Frontend MUST display error messages when deletion fails (network errors, auth errors, server errors)
- **FR-DELETE-017**: Frontend MUST handle loading states during deletion (disable delete button, show spinner)
- **FR-DELETE-018**: System MUST support voice deletion commands via Web Speech API
- **FR-DELETE-019**: System MUST recognize English voice delete patterns: "Delete todo:", "Remove task:", "Delete:"
- **FR-DELETE-020**: System MUST recognize Urdu voice delete patterns: "حذف کریں:", "mitta do:", "delete karen:"
- **FR-DELETE-021**: System MUST extract todo identifier (title) from voice command after intent keyword
- **FR-DELETE-022**: System MUST match voice-provided title to existing todos (exact or fuzzy matching)
- **FR-DELETE-023**: System MUST require confirmation even for voice-initiated deletions
- **FR-DELETE-024**: System MUST provide visual feedback when voice deletion command is recognized
- **FR-DELETE-025**: System MUST handle ambiguous voice commands (multiple matches) by showing user a selection list
- **FR-DELETE-026**: Frontend MUST ensure deleted todos do not reappear on page refresh (verify backend deletion)
- **FR-DELETE-027**: System MUST log deletion events for audit purposes (user_id, todo_id, timestamp)
- **FR-DELETE-028**: System MUST handle concurrent deletion requests gracefully (if same todo deleted twice, second returns 404)
- **FR-DELETE-029**: Frontend MUST support keyboard navigation for delete button and confirmation dialog (accessibility)
- **FR-DELETE-030**: Frontend MUST announce deletion to screen readers (ARIA live regions)

### Key Entities

- **Todo** (being deleted):
  - Attributes:
    - id (UUID, primary key) - used to identify todo to delete
    - user_id (UUID, foreign key) - used to verify ownership before deletion
    - title (string) - displayed in confirmation dialog
    - completed, description, created_at, updated_at (not directly used in deletion logic)
  - Relationships:
    - Belongs to one User (ownership verified before deletion)
  - Constraints:
    - Only the owner (user_id matches authenticated user) can delete
    - Deletion is permanent (hard delete from database)

- **User** (referenced, owns todos):
  - Attributes: id (UUID), email, name
  - Relationships: owns many Todos (one-to-many)
  - Deletion behavior: If user is deleted, todos are CASCADE deleted (database constraint)

- **JWT Token** (used for authentication):
  - Attributes: user_id (in 'sub' claim), expiration time
  - Purpose: Securely identify user performing deletion

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-DELETE-001**: Users can delete a todo and see it removed from their list within 2 seconds on successful deletion
- **SC-DELETE-002**: 100% of deletion attempts require user confirmation (zero accidental deletions without prompt)
- **SC-DELETE-003**: Todo deletion API endpoint responds within 300ms at p95 latency under normal load
- **SC-DELETE-004**: Zero unauthorized users can delete todos (100% authentication enforcement verified through security testing)
- **SC-DELETE-005**: 100% of deletion attempts verify user ownership (no cross-user deletions possible)
- **SC-DELETE-006**: Voice deletion command recognition achieves 85% accuracy for common English delete commands
- **SC-DELETE-007**: Voice deletion command recognition achieves 80% accuracy for common Urdu delete commands
- **SC-DELETE-008**: System handles 50 concurrent deletion requests per second without errors or data corruption
- **SC-DELETE-009**: 100% of deleted todos are permanently removed from database (verified via subsequent GET requests)
- **SC-DELETE-010**: Deletion confirmation dialogs are accessible via keyboard (100% keyboard navigation support)
- **SC-DELETE-011**: Screen readers announce deletion actions correctly in 100% of test cases
- **SC-DELETE-012**: Zero SQL injection vulnerabilities in deletion endpoints (verified through security testing)
- **SC-DELETE-013**: Deletion functionality works correctly on mobile devices (down to 320px width) with same success rate as desktop
- **SC-DELETE-014**: API deletion endpoint documentation completeness score of 100% (all parameters, responses, errors documented)
- **SC-DELETE-015**: Test coverage for todo deletion logic reaches at least 90% (unit + integration tests)

## Assumptions

1. **User Authentication**: Users are already authenticated with valid JWT tokens before accessing deletion functionality. Authentication flow is handled by feature 001.

2. **Todo Existence**: Users can only delete todos that currently exist in their personal list. The system assumes todos have been previously created via feature 002 (Create Todo).

3. **Database Availability**: Neon PostgreSQL database is operational and accessible. Database transactions are supported for atomic deletion operations.

4. **Hard Delete**: MVP uses hard delete (permanent removal from database). Soft delete (archiving with deleted_at flag) is out of scope and can be added in future versions if audit/recovery requirements change.

5. **Single-User Ownership**: Each todo belongs to exactly one user. Multi-user collaboration (shared todos, team tasks) is out of scope for MVP.

6. **Browser Support**: Users are using modern evergreen browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+) that support ES6+, Fetch API, and modern CSS. Web Speech API support for voice deletion is optional and gracefully degraded.

7. **Network Reliability**: Users have reliable internet connection for API calls. Optimistic UI updates with rollback on failure are not implemented in MVP.

8. **Voice Recognition Accuracy**: Web Speech API provides baseline accuracy for todo title matching. Users in noisy environments or with ambiguous titles will use manual selection from UI.

9. **Confirmation Required**: All deletions (UI, voice, API) require explicit confirmation or intent. Accidental deletions are minimized through confirmation dialogs and clear labeling.

10. **Audit Requirements**: Basic deletion logging (user, todo ID, timestamp) is sufficient for MVP. Comprehensive audit trails with undo/restore functionality are out of scope.

11. **Cascading Deletions**: If a user account is deleted (via future feature), their todos are automatically deleted via ON DELETE CASCADE constraint. Todo deletion does not affect user accounts.

12. **Token Validity**: JWT access tokens have 30-minute lifespan (as defined in feature 001). Deletions occur during active user sessions.

## Dependencies

### External Dependencies

1. **Neon PostgreSQL**: Cloud database service for todo persistence
   - Risk: Service outage prevents deletion operations
   - Mitigation: Implement retry logic, display clear errors, monitor Neon status, ensure deletion idempotency

2. **Web Speech API**: Browser-native API for voice recognition (optional)
   - Risk: Limited browser support, accuracy varies
   - Mitigation: Feature detection with graceful degradation, provide manual delete buttons as fallback

3. **Better Auth**: JWT token validation (from feature 001)
   - Risk: Auth service failure prevents deletion authorization
   - Mitigation: Ensure auth dependencies are highly available, implement proper error handling

### Internal Dependencies

1. **Feature 001 (Authentication)**: Users must be logged in with valid JWT tokens before deleting todos
   - JWT token validation must be functional
   - User ID extraction from 'sub' claim must be reliable
   - Token expiration handling must redirect to login

2. **Feature 002 (Create Todo)**: Todos must exist before they can be deleted
   - Database schema (todos table) must be in place
   - Todos must have proper user_id foreign keys for ownership verification

3. **Agent Skills**: Implementation must reference established skills
   - **Database Skill** (`.claude/skills/database.skill.md`): User-scoped DELETE operations, SQLModel patterns, ownership verification
   - **Auth Skill** (`.claude/skills/auth.skill.md`): JWT validation, user extraction, dependency injection for protected endpoints
   - **API Skill** (`.claude/skills/api.skill.md`): DELETE request handling, error responses, TypeScript interfaces
   - **Voice Skill** (`.claude/skills/voice.skill.md`): Voice command patterns for deletion, intent classification for "delete" actions
   - **UI Skill** (`.claude/skills/ui.skill.md`): Confirmation dialogs, delete buttons, loading states, error displays, accessibility patterns

4. **Constitution Compliance**: All development must follow constitutional guidelines
   - Agent-driven development (no manual coding)
   - Security-first architecture (JWT validation, ownership verification, prevent cross-user deletions)
   - Type safety (TypeScript strict mode, Python type hints)
   - Accessibility (WCAG 2.1 AA for delete buttons, confirmation dialogs, keyboard navigation, screen reader support)

### Technical Prerequisites

1. **Frontend Setup**: Next.js 16+ with TypeScript, Tailwind CSS, Better Auth client configured
2. **Backend Setup**: FastAPI with SQLModel, python-jose for JWT, existing DELETE endpoint patterns
3. **Database Schema**: `todos` table with proper foreign key constraints, indexes on user_id
4. **Development Environment**: Claude Code agents operational with all 5 skills loaded and accessible

## Out of Scope

The following are explicitly **not** included in this feature specification:

1. **Soft Delete / Archive**: Marking todos as deleted but retaining in database with deleted_at timestamp (hard delete only in MVP)
2. **Undo Deletion**: Restoring recently deleted todos (permanent deletion in MVP)
3. **Bulk Deletion**: Deleting multiple todos at once (select all, mass delete)
4. **Batch Delete API**: Single API call to delete multiple todo IDs
5. **Delete by Filter**: Deleting all completed todos, all todos matching a search, etc.
6. **Scheduled Deletion**: Auto-delete todos after certain time period or conditions
7. **Deletion History**: Viewing log of previously deleted todos
8. **Export Before Delete**: Downloading or backing up todos before deletion
9. **Collaborative Approval**: Requiring approval from other users before deletion (single-user MVP)
10. **Recycle Bin**: Temporary holding area for deleted todos with restore capability
11. **Delete Notifications**: Email or push notifications when todos are deleted
12. **Delete Permissions**: Role-based permissions for who can delete (all users can delete their own todos)
13. **Audit Dashboard**: UI for viewing deletion audit logs (logging happens but no admin UI)
14. **Delete Quotas**: Rate limiting or throttling deletion operations
15. **Offline Deletion**: PWA offline delete with sync when online
16. **Cascade Delete Relations**: Deleting related entities like attachments, comments (not in MVP)
17. **Delete Analytics**: Tracking deletion patterns or metrics
18. **Protected Todos**: Preventing deletion of certain todos (e.g., pinned, locked)

---

**Next Steps**:
- Run `/sp.plan` to create architecture and design plan for todo deletion implementation
- Run `/sp.clarify` if any requirements need further clarification
- Proceed with `/sp.tasks` after plan approval to generate actionable implementation tasks

---

## Related Documents

- **Parent Feature**: `specs/001-todo-full-stack-app/spec.md` (Overall todo application architecture)
- **Dependency Feature**: `specs/002-create-todo/spec.md` (Todos must exist before deletion)
- **Constitution**: `.specify/memory/constitution.md` (Project governance and security standards)
- **Database Skill**: `.claude/skills/database.skill.md` (DELETE operations, user-scoped queries, ownership verification)
- **Auth Skill**: `.claude/skills/auth.skill.md` (JWT validation, protected endpoints)
- **API Skill**: `.claude/skills/api.skill.md` (DELETE request handling, error responses)
- **Voice Skill**: `.claude/skills/voice.skill.md` (Voice deletion commands, Urdu/English patterns)
- **UI Skill**: `.claude/skills/ui.skill.md` (Confirmation dialogs, delete buttons, accessibility)
