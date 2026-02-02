---
id: 2
title: Create Add Task API Specification
stage: spec
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-todo-full-stack-app
branch: 001-todo-full-stack-app
user: aasif
command: manual
labels: ["api-spec", "create-todo", "endpoint-design", "validation", "security", "testing"]
links:
  spec: specs/001-todo-full-stack-app/api-specs/create-todo.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-todo-full-stack-app/api-specs/create-todo.md
  - history/prompts/001-todo-full-stack-app/2-create-add-task-api-spec.spec.prompt.md
tests:
  - Defined 15 backend unit test cases
  - Defined 3 frontend integration test cases
  - Defined 3 E2E test cases with Playwright
---

## Prompt

now make # 🧩 SPECIFICATION – ADD TASK

---

## 1. Purpose

Enable an authenticated user to create a new todo task using the web interface, REST API, voice commands, or chatbot input.

---

## 2. Functional Requirements

- User must be authenticated (JWT required)
- User can add a task with:
  - Title (required)
  - Description (optional)
- Task is stored in Neon PostgreSQL
- Task is linked to the authenticated user

---

## 3. API Contract

**Endpoint**

## Response snapshot

Created comprehensive API specification for the Create Todo endpoint (POST /api/todos) with complete implementation details, validation rules, security requirements, and test cases.

**API Specification Highlights:**

**1. Functional Requirements (20 total)**
- Core Requirements (FR-ADD-001 to FR-ADD-010):
  - JWT authentication mandatory
  - Title required (1-500 chars), Description optional (max 2000 chars)
  - PostgreSQL persistence with user_id foreign key
  - Defaults: completed=false, auto-generated UUID, timestamps
- Security Requirements (FR-ADD-011 to FR-ADD-015):
  - JWT validation before processing
  - User ID from 'sub' claim, NEVER from request body
  - Authorization header with Bearer token
  - Input sanitization (XSS, SQL injection prevention)
- Validation Requirements (FR-ADD-016 to FR-ADD-020):
  - Missing title → 422 error
  - Title/description length validation
  - Whitespace-only title rejected
  - Unicode/Urdu text support

**2. API Contract**
- **Endpoint**: POST /api/todos
- **Authentication**: Required (Bearer token)
- **Request Body**:
  ```json
  {
    "title": "string (required, 1-500 chars)",
    "description": "string (optional, 0-2000 chars)"
  }
  ```
- **Success Response (201 Created)**:
  ```json
  {
    "id": "uuid",
    "title": "string",
    "description": "string | null",
    "completed": false,
    "user_id": "uuid",
    "created_at": "ISO 8601",
    "updated_at": "ISO 8601"
  }
  ```
- **Error Responses**:
  - 401 Unauthorized: Missing/invalid/expired token
  - 422 Unprocessable Entity: Validation errors (missing title, length violations, empty string)
  - 500 Internal Server Error: Database failures

**3. Data Model**
- **SQL Schema**: Complete table definition with indexes
  - Primary key: UUID with gen_random_uuid()
  - Foreign key: user_id REFERENCES users(id) ON DELETE CASCADE
  - Indexes: user_id, (user_id, completed), created_at DESC
- **SQLModel Schema**: Python model with Field validators
- **Pydantic Schemas**:
  - TodoCreate: Request validation with field_validator for title (strip, non-empty) and description (strip)
  - TodoResponse: Response serialization with from_attributes

**4. Implementation Details**
- **Backend (FastAPI)**:
  - Router with dependency injection (get_db, get_current_user_id)
  - Endpoint: `@router.post("", response_model=TodoResponse, status_code=201)`
  - User ID extraction from JWT (security-critical)
  - UTC timestamp handling
- **Frontend (Next.js)**:
  - API client function: `createTodo(data: TodoCreateRequest)`
  - AddTodoForm component with validation, loading states, error handling
  - Form reset on success, parent notification via onSuccess callback

**5. Voice Command Integration**
- **English Patterns**: "Add todo:", "Create task:", "New todo:", "Add:"
- **Urdu Patterns** (Script): "نیا کام:", "اضافہ کریں:", "ٹاسک بنائیں:"
- **Urdu Patterns** (Roman): "naya kaam:", "shamil karen:", "task banayein:"
- **Example Flow**:
  - User says: "نیا کام: دودھ خریدیں"
  - Intent: CREATE_TODO
  - Extracted title: "دودھ خریدیں"
  - API call: POST /api/todos with Urdu title

**6. Test Cases**
- **Backend Unit Tests (15 test cases)**:
  - Success scenarios: with description, minimal (title only), Urdu text
  - Validation errors: missing title, empty title, title too long, description too long
  - Authentication errors: unauthorized, invalid token
  - User isolation: verify different users get different user_ids
- **Frontend Integration Tests (3 test cases)**:
  - Form submission success with API mock
  - Validation (disabled submit for empty title)
  - API error handling display
- **E2E Tests (3 test cases)**:
  - Create via form with login flow
  - Create via voice command (with microphone permissions)
  - Validation error visibility

**7. Performance Requirements**
- p95 latency < 500ms
- 100 concurrent creations/second throughput
- Connection pooling: min 5, max 20 connections
- Client-side + server-side validation

**8. Security Measures**
- JWT validation with python-jose
- User ID from 'sub' claim (never from request body)
- SQL injection prevention via SQLModel parameterized queries
- XSS prevention via React auto-escaping and CSP headers
- Foreign key constraints for data isolation
- ON DELETE CASCADE for cleanup

**9. Monitoring & Observability**
- **Metrics**:
  - todo_create_requests_total (counter)
  - todo_create_requests_success (counter)
  - todo_create_requests_failed (counter)
  - todo_create_duration_seconds (histogram)
  - todo_create_validation_errors (counter)
- **Logging**: Info logs for creation, error logs for failures
- **Alerts**: Error rate >5%, p95 latency >1s, connection pool exhaustion

**10. Acceptance Criteria (15 items)**
- AC-001 to AC-015 covering:
  - Create with title only, with title+description
  - 3-second appearance in list, persistence across refresh
  - Authentication (401 for unauth)
  - Validation (422 for missing title, length violations, empty string)
  - Urdu text support, voice commands
  - Data isolation, UUID generation, defaults

**Dependencies Referenced**:
- Database Skill: User-scoped CRUD patterns
- Auth Skill: JWT validation and user extraction
- API Skill: Request formatting and error handling
- Voice Skill: Speech recognition and intent classification

**File Structure**:
- Created: `specs/001-todo-full-stack-app/api-specs/create-todo.md` (comprehensive spec)
- Organized under feature-specific api-specs directory

## Outcome

- ✅ Impact: Created detailed, production-ready API specification for Create Todo endpoint with complete contract, implementation code, security requirements, and comprehensive test coverage
- 🧪 Tests: Defined 21 total test cases (15 backend unit, 3 frontend integration, 3 E2E) covering success, validation, authentication, and user isolation scenarios
- 📁 Files: Created api-specs/create-todo.md (comprehensive endpoint specification) and PHR documentation
- 🔁 Next prompts: Create similar API specs for other CRUD operations (Read/List Todos, Update Todo, Delete Todo) or proceed to `/sp.plan` for full implementation planning
- 🧠 Reflection: API specification is extremely detailed and implementation-ready, providing backend developers with exact FastAPI code, frontend developers with React component examples, and QA with comprehensive test cases. Security is paramount throughout: JWT validation mandatory, user_id extraction from token (never request body), SQL injection prevention, XSS protection, and data isolation via foreign keys. Validation is dual-layer (client + server) for UX and security. Voice command integration references Voice Skill patterns for both English and Urdu. Monitoring section ensures observability. Acceptance criteria are specific and testable. This level of detail eliminates ambiguity and enables agent-driven implementation following Database, Auth, API, and Voice skills. The spec demonstrates how a single CRUD operation should be fully documented before implementation begins.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Use this API spec as a template to create specifications for remaining CRUD operations (List/Read, Update, Delete), verifying consistency in security patterns, validation rules, and test coverage across all endpoints
