# Feature Specification: High Priority Task Marking

**Feature Branch**: `006-high-priority`
**Created**: 2026-01-06
**Status**: Draft
**Input**: User description: "Enable an authenticated user to mark a todo task as High Priority, allowing urgent tasks to be highlighted, sorted, and handled first"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mark Task as High Priority via Web Interface (Priority: P1)

Authenticated users can designate specific todos as high priority through a visual toggle or button, enabling them to highlight urgent tasks that need immediate attention.

**Why this priority**: Priority marking is essential for effective task management. Users need to distinguish between urgent and routine tasks to manage their workload efficiently. Without priority levels, all tasks appear equally important, reducing productivity. This is critical for task organization.

**Independent Test**: Can be fully tested by logging in, viewing a todo "Submit project proposal", clicking a "Mark as High Priority" star/flag icon, and seeing the todo immediately highlighted with a visual indicator (red badge, star icon, moved to top of list). Delivers urgent task identification value.

**Acceptance Scenarios**:

1. **Given** I am logged in with a todo "Submit project proposal", **When** I click the priority star/flag icon, **Then** the todo is marked as high priority and displayed with a visual indicator (e.g., red badge, star, "HIGH" label)
2. **Given** I have marked a todo as high priority, **When** I view my todo list, **Then** the high priority todo appears at the top of the list (sorted before normal priority todos)
3. **Given** I have a high priority todo, **When** I click the priority icon again, **Then** the priority is removed and the todo returns to normal priority
4. **Given** I mark a todo as high priority, **When** I refresh the page, **Then** the priority status persists and the todo remains marked as high priority
5. **Given** I have 3 high priority todos and 5 normal priority todos, **When** I view my list, **Then** all 3 high priority todos appear first, followed by the 5 normal priority todos
6. **Given** I am viewing a high priority todo, **When** I mark it as completed, **Then** it retains its high priority status (completed high priority todos remain distinguishable)

---

### User Story 2 - Filter and View High Priority Tasks (Priority: P1)

Authenticated users can filter their todo list to show only high priority tasks, enabling focused attention on urgent work without distraction from routine tasks.

**Why this priority**: Filtering by priority is essential for productivity workflows. Users need to quickly see what requires immediate action. This is a core feature for priority-based task management and is critical for effective use of the priority system.

**Independent Test**: Can be fully tested by logging in with 2 high priority and 3 normal priority todos, clicking a "High Priority" filter button, and seeing only the 2 high priority todos displayed. Delivers focused workflow value.

**Acceptance Scenarios**:

1. **Given** I have 2 high priority and 3 normal priority todos, **When** I click "High Priority" or "Urgent" filter, **Then** I see only the 2 high priority todos
2. **Given** I have applied the high priority filter, **When** I click "All tasks", **Then** I see all todos (both high and normal priority)
3. **Given** I am viewing the high priority filter, **When** I mark a normal priority todo as high priority, **Then** it immediately appears in the filtered view
4. **Given** I am viewing the high priority filter, **When** I remove priority from a todo, **Then** it disappears from the filtered view
5. **Given** I apply the high priority filter, **When** I refresh the page, **Then** the filter persists and only high priority todos are shown
6. **Given** I have no high priority todos, **When** I click the high priority filter, **Then** I see an empty state message "No high priority tasks. Mark important tasks to see them here."

---

### User Story 3 - Set Priority via Voice Command (English/Urdu) (Priority: P2)

Authenticated users can mark tasks as high priority using voice commands in English or Urdu, enabling hands-free priority management.

**Why this priority**: Voice priority marking enhances accessibility and convenience, but keyboard/mouse interaction remains available. This is valuable for users multitasking or with accessibility needs, but not critical for core priority functionality.

**Independent Test**: Can be fully tested by logging in with a todo "Call client", clicking the microphone button, saying "Mark as high priority: Call client", and seeing the todo immediately marked with a priority indicator. Delivers hands-free priority management value.

**Acceptance Scenarios**:

1. **Given** I have a todo "Call client", **When** I say "Mark as high priority: Call client" or "Set priority high: Call client", **Then** the todo is marked as high priority
2. **Given** I have a high priority todo, **When** I say "Remove priority: Call client" or "Set priority normal: Call client", **Then** the priority is removed
3. **Given** I am using Urdu voice input, **When** I say "اہم بنائیں: کلائنٹ کو کال کریں" (Mark important: Call client), **Then** the todo is marked as high priority
4. **Given** voice recognition identifies multiple matching todos, **When** I give a priority command, **Then** I see options to select which todo to prioritize
5. **Given** voice recognition fails or is unclear, **When** I attempt to set priority, **Then** I see an error message and can retry or use manual priority toggle

---

### User Story 4 - Update Task Priority via REST API (Priority: P1)

Developers and third-party integrations can set or update task priority programmatically via REST API, enabling automation and integration with external priority management systems.

**Why this priority**: API access is essential for extensibility, automation, and integration with project management tools. This enables programmatic priority management and is critical for platform value and third-party integrations.

**Independent Test**: Can be fully tested by obtaining a JWT token, creating a todo, making a PATCH request to /api/todos/{id} with {"priority": "high"}, receiving a 200 OK response with updated todo showing priority: "high". Delivers programmatic priority management value.

**Acceptance Scenarios**:

1. **Given** I have a valid JWT token and a todo with ID "abc-123", **When** I PATCH /api/todos/abc-123 with {"priority": "high"}, **Then** I receive 200 OK with the todo showing priority: "high"
2. **Given** I have a todo with normal priority, **When** I PATCH with {"priority": "normal"} or {"priority": null}, **Then** the priority is removed/set to normal
3. **Given** I attempt to set priority without Authorization header, **When** the request is processed, **Then** I receive 401 Unauthorized
4. **Given** I attempt to set priority on another user's todo, **When** the request is processed, **Then** I receive 404 Not Found (ownership verification)
5. **Given** I PATCH with {"priority": "invalid-value"}, **When** validation runs, **Then** I receive 422 Unprocessable Entity with validation error listing valid priority values
6. **Given** I GET /api/todos with high priority todos, **When** I receive the response, **Then** todos are sorted with high priority first, followed by normal priority (default sort respects priority)

---

### User Story 5 - View Priority in Todo List and Details (Priority: P1)

Authenticated users can clearly see which todos are high priority through consistent visual indicators across all views (list, details, completed section).

**Why this priority**: Visual clarity of priority status is essential for the priority system to be useful. Users must be able to quickly scan their list and identify urgent tasks at a glance. This is critical for the priority feature to deliver value.

**Independent Test**: Can be fully tested by logging in with a mix of high and normal priority todos, viewing the list, and confirming high priority todos have clear visual distinction (color badge, star icon, or "HIGH" label) that stands out. Delivers immediate priority recognition value.

**Acceptance Scenarios**:

1. **Given** I have high priority todos, **When** I view my todo list, **Then** each high priority todo displays a visual indicator (e.g., red badge, star icon, colored border)
2. **Given** I am viewing a high priority todo in expanded/detail view, **When** I see the todo details, **Then** the priority indicator is prominently displayed
3. **Given** I have completed high priority todos, **When** I view the completed section, **Then** completed high priority todos retain their priority indicator (faded or crossed out but still visible)
4. **Given** I am viewing todos on mobile (320px width), **When** I see high priority todos, **Then** the priority indicator is clearly visible and doesn't break layout
5. **Given** I have mixed high/normal priority todos with Urdu text, **When** I view the list, **Then** priority indicators display correctly with RTL content
6. **Given** I am using a screen reader, **When** I navigate through todos, **Then** high priority todos are announced as "High priority: [todo title]"

---

### Edge Cases

- **What happens when** a user marks all their todos as high priority?
  - All todos display priority indicators; sorting by priority becomes meaningless as all have same priority; system may show a helpful tip like "Consider prioritizing only urgent tasks for better focus"

- **What happens when** a user attempts to mark a completed todo as high priority?
  - Action succeeds - completed todos can have priority set (useful for re-opening urgent tasks); priority persists if todo is later marked incomplete

- **What happens when** a user has high priority todos and applies the "Completed" filter?
  - Completed high priority todos appear in the completed filter with priority indicators; user can see which urgent tasks were finished

- **What happens when** a user sets priority on a todo and then their JWT token expires?
  - Priority change is already persisted (if request completed); if user was mid-action, they receive 401 on next request and must re-login

- **What happens when** database is down when user tries to mark a todo as high priority?
  - Optimistic UI update shows priority indicator immediately; when API request fails, UI reverts to original state with error message "Failed to update priority. Please try again."

- **What happens when** voice recognition misidentifies the todo title when setting priority?
  - System searches for misheard title (e.g., "buy silk" instead of "buy milk"), finds no match or wrong match, displays "No todo found" or shows closest matches with "Did you mean?" options

- **What happens when** a user rapidly toggles priority on/off multiple times (5 clicks in 2 seconds)?
  - Each request is queued, optimistic UI updates immediately, final state matches last user action; debouncing prevents excessive API calls; race condition handling ensures consistency

- **What happens when** API request to set priority takes longer than expected (slow network)?
  - Loading state on priority indicator (spinner or disabled state), timeout after 5 seconds with retry option, user can cancel and retry

- **What happens when** user has 10 high priority todos and creates an 11th high priority todo?
  - System allows unlimited high priority todos (no hard limit in MVP); all 11 appear at top of list; UI may show a gentle reminder to focus on most urgent if too many high priority tasks

- **What happens when** user filters by both "High Priority" and "Completed" simultaneously?
  - System shows only completed high priority todos (filters combine with AND logic); useful for reviewing finished urgent work

## Requirements *(mandatory)*

### Functional Requirements

- **FR-PRIORITY-001**: System MUST require JWT authentication for all priority update operations
- **FR-PRIORITY-002**: System MUST validate JWT token signature and expiration before processing priority changes
- **FR-PRIORITY-003**: System MUST extract user ID from JWT 'sub' claim, NEVER from request body
- **FR-PRIORITY-004**: System MUST verify that the todo being updated belongs to the authenticated user (ownership check)
- **FR-PRIORITY-005**: System MUST support priority values: "high" and "normal" (or null for normal)
- **FR-PRIORITY-006**: System MUST store priority as a string field in the todos table: priority VARCHAR(20) DEFAULT 'normal'
- **FR-PRIORITY-007**: System MUST allow setting priority during todo creation via optional priority field
- **FR-PRIORITY-008**: System MUST allow updating priority via PATCH request to update endpoint
- **FR-PRIORITY-009**: System MUST validate priority values: only "high", "normal", or null are accepted
- **FR-PRIORITY-010**: System MUST return 422 Unprocessable Entity for invalid priority values with error details
- **FR-PRIORITY-011**: System MUST default to "normal" priority when creating todos without explicit priority
- **FR-PRIORITY-012**: System MUST update the updated_at timestamp when priority is changed
- **FR-PRIORITY-013**: System MUST NOT modify created_at timestamp when priority is changed
- **FR-PRIORITY-014**: System MUST include priority field in all todo API responses (GET, POST, PATCH, PUT)
- **FR-PRIORITY-015**: System MUST sort todos by priority in list views: high priority first, then normal priority
- **FR-PRIORITY-016**: System MUST apply secondary sorting within same priority level (e.g., by created_at DESC)
- **FR-PRIORITY-017**: System MUST support filtering todos by priority via query parameter: priority=high
- **FR-PRIORITY-018**: System MUST return only high priority todos when priority=high filter is applied
- **FR-PRIORITY-019**: Frontend MUST display visual indicators for high priority todos (badge, icon, color)
- **FR-PRIORITY-020**: Frontend MUST provide quick toggle control for setting/removing priority (star, flag, or checkbox)
- **FR-PRIORITY-021**: Frontend MUST implement optimistic UI updates when priority is toggled
- **FR-PRIORITY-022**: Frontend MUST revert optimistic updates if API request fails with error message
- **FR-PRIORITY-023**: Frontend MUST provide filter button/tab for viewing only high priority todos
- **FR-PRIORITY-024**: Frontend MUST display priority indicator consistently across list, detail, and completed views
- **FR-PRIORITY-025**: Frontend MUST ensure priority indicators are accessible via keyboard (tab navigation, Enter to toggle)
- **FR-PRIORITY-026**: Frontend MUST announce priority changes to screen readers ("Marked as high priority" / "Priority removed")
- **FR-PRIORITY-027**: System MUST support voice commands for priority: "Mark as high priority", "Set priority high", "Remove priority"
- **FR-PRIORITY-028**: System MUST recognize Urdu voice priority commands: "اہم بنائیں" (mark important), "ترجیح ہٹائیں" (remove priority)
- **FR-PRIORITY-029**: Frontend MUST display count of high priority todos (e.g., "3 urgent tasks")
- **FR-PRIORITY-030**: Frontend MUST show high priority todos at top of list regardless of creation date
- **FR-PRIORITY-031**: Frontend MUST display empty state when high priority filter shows no results
- **FR-PRIORITY-032**: System MUST log priority changes for audit purposes (user_id, todo_id, old_priority, new_priority, timestamp)
- **FR-PRIORITY-033**: System MUST use parameterized queries to prevent SQL injection in priority updates
- **FR-PRIORITY-034**: Frontend MUST handle priority toggle on mobile devices with minimum 44x44px touch target
- **FR-PRIORITY-035**: Frontend MUST display priority indicators in responsive layouts (320px+ width)

### Key Entities

- **Todo** (with priority field):
  - New Attribute:
    - priority (string, enum: "high" or "normal", default: "normal", max 20 characters)
  - Existing Attributes:
    - id (UUID)
    - user_id (UUID)
    - title (string, 1-500 characters)
    - description (string, 0-2000 characters, nullable)
    - completed (boolean, default false)
    - created_at (timestamp)
    - updated_at (timestamp)
  - Relationships:
    - Belongs to one User (ownership verified before priority changes)
  - Priority Rules:
    - Only two values supported in MVP: "high" and "normal"
    - Default: "normal" when not specified
    - Can be set on completed or incomplete todos
    - Persists across completion status changes
    - Affects default sort order (high priority first)

- **User** (owns todos):
  - Attributes: id (UUID), email, name
  - Relationships: owns many Todos (one-to-many)
  - Priority permissions: Can only set priority on their own todos

- **Priority Visual Indicators** (UI representation):
  - High priority: Red/orange badge, star icon, "HIGH" label, or colored border
  - Normal priority: No special indicator (default appearance)
  - Consistent across: List view, detail view, completed section, mobile/desktop
  - Accessible: Clear color contrast (WCAG AA), screen reader announcements

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-PRIORITY-001**: Users can mark a todo as high priority and see visual feedback within 1 second
- **SC-PRIORITY-002**: Priority toggle responds within 500ms at p95 latency (similar to completion toggle)
- **SC-PRIORITY-003**: High priority todos consistently appear at top of list in 100% of sort scenarios
- **SC-PRIORITY-004**: Visual distinction between high and normal priority is clear to 95%+ of users in usability testing
- **SC-PRIORITY-005**: Zero unauthorized users can modify todo priority (100% authentication enforcement)
- **SC-PRIORITY-006**: 100% of priority changes verify user ownership (no cross-user priority modifications)
- **SC-PRIORITY-007**: Priority filter shows correct todos in 100% of test cases (only high priority when filtered)
- **SC-PRIORITY-008**: Voice priority commands achieve 85% accuracy for common English phrases
- **SC-PRIORITY-009**: Voice priority commands achieve 80% accuracy for common Urdu phrases
- **SC-PRIORITY-010**: System handles 100 concurrent priority updates per second without data corruption
- **SC-PRIORITY-011**: Optimistic UI updates for priority succeed in 95%+ of cases (< 5% revert rate)
- **SC-PRIORITY-012**: Priority indicators display correctly on mobile devices (320px width) in 100% of layouts
- **SC-PRIORITY-013**: Screen readers announce priority status correctly in 100% of accessibility tests
- **SC-PRIORITY-014**: Priority toggle is accessible via keyboard (100% keyboard navigation support)
- **SC-PRIORITY-015**: Zero SQL injection vulnerabilities in priority update endpoints
- **SC-PRIORITY-016**: Users can find and focus on high priority work in under 5 seconds using priority filter
- **SC-PRIORITY-017**: Priority indicators have minimum 4.5:1 color contrast ratio (WCAG AA compliance)
- **SC-PRIORITY-018**: API documentation for priority field is 100% complete (creation, update, filtering, sorting)
- **SC-PRIORITY-019**: Test coverage for priority logic reaches at least 90% (unit + integration tests)
- **SC-PRIORITY-020**: High priority count badge updates immediately when priority changes (< 1s delay)

## Assumptions

1. **User Authentication**: Users are already authenticated with valid JWT tokens before setting priority. Authentication flow is handled by feature 001.

2. **Todo Existence**: Users can only set priority on todos that exist in their personal list. Todos have been previously created via feature 002 (Create Todo).

3. **Two-Level Priority System**: MVP supports only two priority levels: "high" and "normal" (default). Multi-level priority (low/medium/high/urgent) can be added in future versions based on user feedback.

4. **Database Schema Change**: Requires migration to add priority VARCHAR(20) DEFAULT 'normal' column to todos table with index for efficient filtering.

5. **Priority Persistence**: Priority status persists across all todo state changes (completion, updates, etc.). Completing a high priority todo doesn't remove its priority.

6. **Default Sort Behavior**: Todos are sorted by priority first (high before normal), then by created_at DESC within each priority level. This provides predictable ordering.

7. **Visual Indicators**: High priority uses warm colors (red, orange) to convey urgency. Normal priority has no special styling to avoid visual clutter.

8. **No Priority Limit**: Users can mark unlimited todos as high priority. System may show gentle reminders if too many tasks are marked urgent (10+), but doesn't enforce limits.

9. **Browser Support**: Priority indicators work in modern evergreen browsers with proper color contrast and icon rendering. Degradation is graceful in older browsers.

10. **Voice Commands**: Priority voice commands use same patterns as completion toggle voice commands. Recognition accuracy depends on Web Speech API quality.

11. **API Compatibility**: Adding priority field to API responses is non-breaking (new optional field). Clients not using priority can ignore the field.

12. **Performance Impact**: Priority filtering and sorting add minimal overhead due to indexed priority column. Performance targets remain consistent with existing list operations (300ms p95).

13. **Mobile-First**: Priority toggle and indicators are designed mobile-first with minimum 44x44px touch targets and clear visual feedback on small screens.

## Dependencies

### External Dependencies

1. **Neon PostgreSQL**: Cloud database for priority storage
   - Risk: Service outage prevents priority updates from persisting
   - Mitigation: Optimistic UI updates with rollback, retry logic, error messages

2. **Web Speech API**: For voice priority commands (optional)
   - Risk: Limited browser support, accuracy varies
   - Mitigation: Feature detection with graceful degradation, manual toggle always available

3. **Better Auth**: JWT token validation
   - Risk: Auth service failure prevents priority authorization
   - Mitigation: Ensure auth dependencies are highly available

### Internal Dependencies

1. **Feature 001 (Authentication)**: Users must be logged in with valid JWT tokens before setting priority
   - JWT token validation must be functional
   - User ID extraction from 'sub' claim must be reliable

2. **Feature 002 (Create Todo)**: Todos must exist before priority can be set
   - Database schema (todos table) must be in place
   - Priority field must be added via migration

3. **Feature 004 (Update Todo)**: Priority updates use existing update endpoint patterns
   - PATCH endpoint must support new priority field
   - Field-level validation must handle priority enum

4. **Feature 005 (View Tasks)**: Priority affects sorting and filtering in list views
   - List queries must sort by priority first
   - Filter controls must include high priority option
   - Empty states must handle priority filter

5. **Agent Skills**: Implementation must reference established skills
   - **Database Skill**: Priority field migration, indexed column, enum validation, sorting with multiple fields
   - **Auth Skill**: JWT validation, ownership verification
   - **API Skill**: PATCH requests with new field, validation, filtering query parameters
   - **Voice Skill**: Priority command patterns for English/Urdu
   - **UI Skill**: Toggle controls, visual indicators, badges, filtering UI, optimistic updates, accessibility

6. **Constitution Compliance**: All development must follow constitutional guidelines
   - Agent-driven development (no manual coding)
   - Security-first architecture (JWT validation, ownership verification)
   - Type safety (TypeScript strict mode, Python type hints)
   - Accessibility (WCAG 2.1 AA for priority indicators, keyboard navigation, screen reader support)

### Technical Prerequisites

1. **Database Migration**: Add priority column to todos table with default value and index
2. **Frontend Setup**: Icon library for priority indicators (stars, flags), color scheme for high priority
3. **Backend Setup**: Enum validation for priority field, updated sorting logic, filter support
4. **Development Environment**: Claude Code agents operational with Database Architect for migration

## Out of Scope

The following are explicitly **not** included in this feature specification:

1. **Multi-Level Priority**: Low, medium, high, urgent (only two levels: high and normal in MVP)
2. **Priority Levels with Numbers**: Priority 1, 2, 3, 4 system
3. **Custom Priority Names**: User-defined priority level names
4. **Priority Colors**: Custom color selection for priority indicators
5. **Automatic Priority**: AI-suggested priority based on due dates or keywords
6. **Priority Decay**: Automatic priority reduction over time
7. **Priority History**: Tracking when priority was changed and by whom (beyond basic audit log)
8. **Priority Notifications**: Email or push notifications for high priority tasks
9. **Priority Deadlines**: Due dates or time-based priority escalation
10. **Priority Scoring**: Numeric priority scores or weighted priority systems
11. **Priority Dependencies**: Tasks that become high priority when dependent tasks are completed
12. **Bulk Priority Update**: Setting priority on multiple todos simultaneously
13. **Priority Templates**: Pre-defined priority rules for certain task types
14. **Priority Analytics**: Reporting on how many high priority tasks were completed
15. **Priority Sharing**: Shared priority across collaborative/team todos (single-user MVP)
16. **Priority Inheritance**: Child tasks inheriting parent priority (no subtasks in MVP)
17. **Priority-Based Notifications**: Different notification behavior for high vs normal priority
18. **Priority Filters in Search**: Combining search with priority filters (basic filtering only)

---

**Next Steps**:
- Run `/sp.plan` to create architecture and design plan for high priority task implementation
- Run `/sp.clarify` if any requirements need further clarification
- Proceed with `/sp.tasks` after plan approval to generate actionable implementation tasks

---

## Related Documents

- **Parent Feature**: `specs/001-todo-full-stack-app/spec.md` (Overall todo application architecture)
- **Dependency Features**:
  - `specs/002-create-todo/spec.md` (Todos must exist before priority can be set)
  - `specs/004-update-todo/spec.md` (Priority updates use update endpoint patterns)
  - `specs/005-view-tasks/spec.md` (Priority affects sorting and filtering)
- **Constitution**: `.specify/memory/constitution.md` (Project governance and security standards)
- **Database Skill**: `.claude/skills/database.skill.md` (Schema migration, enum fields, multi-field sorting)
- **Auth Skill**: `.claude/skills/auth.skill.md` (JWT validation, ownership verification)
- **API Skill**: `.claude/skills/api.skill.md` (PATCH requests, field validation, filtering)
- **Voice Skill**: `.claude/skills/voice.skill.md` (Priority command patterns)
- **UI Skill**: `.claude/skills/ui.skill.md` (Toggle controls, badges, visual indicators, optimistic updates, accessibility)
