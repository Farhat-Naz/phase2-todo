# 📜 Agentic Todo Full-Stack Web Application Constitution

<!--
SYNC IMPACT REPORT
==================
Version Change: 1.0.0 → 1.1.0 (MINOR)
Date: 2026-01-20
Modified Principles: No changes to core 8 principles
Added Sections:
  - API Architecture (REST standards, authentication endpoints, todo endpoints)
  - Database Schema (User table, Todo table with indexes)
  - Voice Command Support (English and Urdu commands)
  - Code Quality Standards (Frontend/Backend structure and requirements)
  - Development Workflow (Feature flow, agent selection, git standards)
  - Environment Variables (Frontend .env.local, Backend .env)
  - Deployment (Vercel frontend, Render/Railway backend, Neon database)
  - Package Management (UV package manager - mandatory)
  - Success Metrics (Technical, Process, User Experience)
Removed Sections: None
Templates Validation:
  ✅ plan-template.md: Aligned with Constitution Check gates
  ✅ spec-template.md: Supports independent testable user stories
  ✅ tasks-template.md: Enforces TDD, parallel execution, story-based organization
Version Bump Rationale: MINOR - Added extensive implementation guidance (API specs, database schemas, deployment instructions, detailed standards) without changing core governance principles. Backward compatible with v1.0.0.
Follow-up TODOs: None
Deferred Placeholders: None
-->

---

## 1. Purpose & Vision

The purpose of this project is to build a **modern, secure, multi-user Todo web application** using an **Agentic Development Stack** powered by **Claude Code and Spec-Kit Plus**.

This project must demonstrate:

- 🤖 **Agent & Sub-Agent Collaboration**: Specialized agents working together
- 📦 **UV Package Manager**: Fast Python dependency management
- 📜 **Spec-Driven Development**: Specification → Plan → Tasks → Implementation
- ♻️ **Reusable Intelligence**: Agent Skills for consistent patterns
- 🌐 **Full-Stack Architecture**: Next.js frontend + FastAPI backend
- 🔐 **Secure Authentication**: JWT-based with Better Auth
- 🗣️ **Voice Commands**: English and Urdu language support
- 🌍 **Urdu Language Support**: RTL text rendering and localization
- ☁️ **Cloud-Native Persistence**: Neon Serverless PostgreSQL

**No manual coding is allowed.**
All implementation must be produced, reviewed, and refined through Claude Code agents.

---

## 2. Core Principles (NON-NEGOTIABLE)

### I. Stateless Server Architecture (MANDATORY)

- Server holds **NO** conversation state in memory
- Every request **MUST** be independent and self-contained
- Conversation history **MUST** be fetched from database on each request
- No in-memory session caches or conversation context
- All state **MUST** be persisted in PostgreSQL before response

**Rationale**: Stateless architecture enables horizontal scaling, crash recovery, and predictable behavior. In a chatbot system, conversation history is the source of truth—the server is merely a stateless processor.

### II. Spec-Driven Development (MANDATORY)

- No manual coding without specification
- Workflow **MUST** follow: **Specification → Plan → Tasks → Implementation**
- All changes **MUST** reference specs, plans, or tasks
- Every feature begins with `/sp.specify`, followed by `/sp.plan`, `/sp.tasks`, `/sp.implement`
- Deviation from spec requires spec amendment via `/sp.clarify`

**Rationale**: Spec-driven development ensures traceability, reduces rework, and aligns all agents on shared understanding. Code without specs is technical debt.

### III. Agent-First Design (MANDATORY)

- All logic flows through agents and sub-agents
- **MCP tools are the ONLY way agents interact with data**
- No direct database access bypassing MCP tools
- Sub-agents **MUST** be isolated, focused, and composable
- Main agent delegates to sub-agents; sub-agents never call other sub-agents

**Agent Hierarchy:**
1. **User Request** → Analyze requirements
2. **Specification Agent** → Create detailed spec in `specs/<feature>/spec.md`
3. **Planning Agent** → Design architecture in `specs/<feature>/plan.md`
4. **Task Agent** → Break into tasks in `specs/<feature>/tasks.md`
5. **Specialized Agents** → Implement using appropriate sub-agents:
   - **Frontend Builder**: UI/Voice components
   - **Backend API Guardian**: API endpoints and business logic
   - **Database Architect**: Schema design and migrations
   - **Auth Config Specialist**: Authentication configuration
   - **Urdu Translator**: Localization and translation
6. **Verification** → Test and validate implementation
7. **Documentation** → Update PHRs and ADRs as needed

**Rationale**: Agent-first design enforces modularity, testability, and reusability. MCP tools provide consistent interfaces, and agent hierarchy prevents coupling.

### IV. Reusable Intelligence (SKILLS-FIRST)

**Every agent MUST consult relevant skills before implementing features:**

- **API Skill** (`.claude/skills/api.skill.md`): Request formatting, error handling, JWT attachment
- **Database Skill** (`.claude/skills/database.skill.md`): CRUD, user filtering, pagination
- **Auth Skill** (`.claude/skills/auth.skill.md`): JWT validation, token management
- **Voice Skill** (`.claude/skills/voice.skill.md`): Speech recognition, intent classification
- **UI Skill** (`.claude/skills/ui.skill.md`): Design system, components, accessibility

Skills are **living documents** located in `.claude/skills/` that:
- Provide reusable patterns across features
- Encode security best practices
- Ensure consistent implementation
- Document skills in `.claude/skills/README.md`
- Can be updated based on learnings (with PHR documentation)

**Rationale**: Reusable intelligence reduces duplication, accelerates development, and ensures consistent behavior across features.

### V. Multilingual Support (English + Urdu)

- All user-facing text **MUST** support English and Urdu
- Use `next-intl` for frontend localization
- Urdu text **MUST** render RTL with proper font (Noto Nastaliq Urdu)
- Voice commands **MUST** support `en-US` and `ur-PK` locales
- Agent prompts **MUST** handle Urdu input gracefully

**Rationale**: Multilingual support is a core feature requirement for accessibility in diverse user bases.

### VI. Security-First Development (CRITICAL)

**All security requirements are NON-NEGOTIABLE:**

#### Authentication Flow (MANDATORY)
```
User Login (Next.js)
        ↓
Better Auth issues JWT
        ↓
JWT stored in httpOnly cookie
        ↓
Frontend sends Authorization header
        ↓
FastAPI validates JWT signature
        ↓
User ID extracted from 'sub' claim
        ↓
DB queries filtered by user_id
```

#### Security Rules (ENFORCED)

1. **JWT Validation**: EVERY protected endpoint **MUST** validate JWT before processing
2. **User Scoping**: ALL database queries **MUST** filter by authenticated user's ID
3. **No Trust**: NEVER trust `user_id` from request body - ALWAYS extract from validated JWT
4. **Ownership Verification**: UPDATE/DELETE operations **MUST** verify user owns the resource
5. **Secret Management**: ALL secrets in environment variables, NEVER in code
6. **HTTPS Only**: Production **MUST** use HTTPS for all authentication requests
7. **Token Expiration**: Access tokens: 30 minutes, Refresh tokens: 7 days
8. **Status Codes**: Return 404 (not 403) for unauthorized access to prevent user enumeration
9. **SQL Injection**: Protection via parameterized queries (SQLModel ORM)
10. **Password Hashing**: Bcrypt with minimum 10 rounds

```python
# ✅ CORRECT - Always filter by user_id
todos = db.exec(
    select(Todo).where(Todo.user_id == current_user_id)
).all()

# ❌ WRONG - Never query without user filter
todos = db.exec(select(Todo)).all()  # SECURITY VIOLATION
```

**Violation of security rules results in immediate rejection of implementation.**

**Rationale**: Security breaches erode user trust. User data isolation is non-negotiable; authentication is the first line of defense.

### VII. Test-Driven Development (TDD)

- Tests **MUST** be written **before** implementation
- **Red-Green-Refactor** cycle strictly enforced
- Unit tests for all business logic (80%+ coverage target)
- Integration tests for API endpoints
- E2E tests for critical user flows (auth, CRUD)
- Test files located in `backend/tests/` and `frontend/__tests__/`

**Test Coverage Requirements:**
- Minimum 80% code coverage
- All critical paths tested
- Edge cases covered
- Frontend: Jest + React Testing Library
- Backend: pytest with fixtures

**Rationale**: TDD prevents regressions, documents expected behavior, and enables confident refactoring.

### VIII. Observability and Debugging

- Structured logging with FastAPI's logger
- All API requests logged with: timestamp, user_id, endpoint, status
- Errors logged with stack traces (but sanitized in prod responses)
- MCP tool calls logged for agent debugging
- Database query logs for performance analysis

**Rationale**: Observability is essential for debugging stateless systems where no in-memory state exists between requests.

---

## 3. Technology Stack (IMMUTABLE)

### 3.1 Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 16+ (App Router) | React framework with SSR/SSG |
| **TypeScript** | 5+ | Type-safe JavaScript |
| **Tailwind CSS** | 3.4+ | Utility-first styling |
| **Better Auth** | Latest | JWT authentication |
| **next-intl** | Latest | Internationalization (i18n) |
| **Web Speech API** | Native | Voice command input |
| **Lucide Icons** | Latest | Modern icon library |
| **Framer Motion** | 10+ | Animations and transitions |
| **next-themes** | Latest | Dark mode support |

### 3.2 Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.13+ | Modern Python with type hints |
| **FastAPI** | Latest | Async web framework with OpenAPI docs |
| **SQLModel** | Latest | Type-safe ORM (Pydantic + SQLAlchemy) |
| **Neon PostgreSQL** | Serverless | Cloud-native database with branching |
| **MCP Server** | Latest | Model Context Protocol server |
| **python-jose** | Latest | JWT encoding/decoding |
| **Uvicorn** | Latest | ASGI server |
| **Alembic** | Latest | Database migrations |

### 3.3 Package Management

#### UV Package Manager (MANDATORY)

All Python dependencies **MUST** be managed using **UV**.

❌ `pip` is **NOT** allowed
❌ `poetry` is **NOT** allowed
✅ `uv` is **MANDATORY**

**UV Setup and Usage:**
```bash
# Install uv (Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install uv (Unix/Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Unix/Linux/macOS:
source .venv/bin/activate

# Run Python scripts
uv run python main.py

# Add dependencies
uv add <package>

# Add dev dependencies
uv add --dev <package>
```

**Frontend Package Manager:**
- **pnpm**: Frontend package manager (faster than npm)

### 3.4 Development Tools

| Tool | Purpose |
|------|---------|
| **Claude Code** | AI-powered development assistant |
| **Spec-Kit Plus** | Spec-driven development framework |
| **Git** | Version control |
| **pytest** | Backend testing framework |
| **Jest** | Frontend testing framework |

**Technology changes require ADR approval and constitutional amendment.**

---

## 4. API Architecture

### 4.1 REST API Standards

All API endpoints **MUST** follow these standards:

**Endpoint Structure:**
```
/api/auth/login         - User login
/api/auth/register      - User registration
/api/auth/refresh       - Token refresh
/api/auth/me            - Current user info
/api/todos              - List all todos for authenticated user
/api/todos/{id}         - Get/Update/Delete specific todo
/api/todos/{id}/complete - Toggle todo completion
```

**HTTP Methods:**
- `GET`: Retrieve resources
- `POST`: Create new resources
- `PUT`: Full resource update
- `PATCH`: Partial resource update
- `DELETE`: Remove resources

**Status Codes:**
- `200 OK`: Successful GET/PUT/PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing/invalid JWT
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found (or unauthorized access)
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

**Response Format:**
```json
{
  "data": {...},           // Success response
  "error": {               // Error response
    "message": "...",
    "code": "...",
    "details": {...}
  }
}
```

### 4.2 Authentication Endpoints

**POST /api/auth/register**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}

Response (201):
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**POST /api/auth/login**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response (200):
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**POST /api/auth/refresh**
```
Authorization: Bearer <access_token>

Response (200):
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**GET /api/auth/me**
```
Authorization: Bearer <access_token>

Response (200):
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-01-01T00:00:00Z"
}
```

### 4.3 Todo Endpoints

**All todo endpoints require authentication: `Authorization: Bearer <token>`**

**GET /api/todos**
```
Query params:
  - page: int (default: 1)
  - page_size: int (default: 20, max: 100)
  - completed: bool (optional filter)

Response (200):
{
  "items": [{...}],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "has_next": true,
  "has_prev": false
}
```

**POST /api/todos**
```json
Request:
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false
}

Response (201):
{
  "id": "uuid",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "user_id": "uuid",
  "created_at": "2026-01-06T00:00:00Z",
  "updated_at": "2026-01-06T00:00:00Z"
}
```

**GET /api/todos/{id}**
```json
Response (200):
{
  "id": "uuid",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "user_id": "uuid",
  "created_at": "2026-01-06T00:00:00Z",
  "updated_at": "2026-01-06T00:00:00Z"
}
```

**PUT /api/todos/{id}**
```json
Request:
{
  "title": "Buy groceries and snacks",
  "description": "Milk, eggs, bread, chips",
  "completed": false
}

Response (200): // Same as GET response
```

**PATCH /api/todos/{id}**
```json
Request (partial update):
{
  "completed": true
}

Response (200): // Same as GET response
```

**DELETE /api/todos/{id}**
```
Response (204): // No content
```

---

## 5. Database Schema

### 5.1 User Table
```sql
CREATE TABLE "user" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  hashed_password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_email ON "user"(email);
```

### 5.2 Todo Table
```sql
CREATE TABLE todo (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_todo_user_id ON todo(user_id);
CREATE INDEX idx_todo_completed ON todo(completed);
CREATE INDEX idx_todo_created_at ON todo(created_at DESC);
```

### 5.3 Multi-Tenant Data Isolation

**User data isolation is CRITICAL for this multi-user application:**

Every table with user-owned data **MUST**:
- Have `user_id` foreign key field with index
- Filter ALL queries by `user_id = current_user.id`
- Verify ownership before mutations
- Use proper HTTP status codes (404 for unauthorized access)

**Schema Rules:**
- UUIDs for primary keys (security + distributed systems)
- Foreign keys with CASCADE delete
- Timestamps on all tables (created_at, updated_at)
- Indexes on user_id, frequently queried fields
- NOT NULL constraints on required fields

---

## 6. Voice Command Support

### 6.1 Supported Commands (English)

| Command | Intent | Example |
|---------|--------|---------|
| "Add todo: [title]" | CREATE_TODO | "Add todo: Buy milk" |
| "Complete todo: [title]" | COMPLETE_TODO | "Complete todo: Buy milk" |
| "Delete todo: [title]" | DELETE_TODO | "Delete todo: Buy milk" |
| "Show all todos" | LIST_TODOS | "Show all todos" |
| "Show completed todos" | FILTER_COMPLETED | "Show completed todos" |
| "Show pending todos" | FILTER_PENDING | "Show pending todos" |
| "Search for [query]" | SEARCH_TODO | "Search for grocery" |

### 6.2 Supported Commands (Urdu)

| Command (Urdu Script) | Command (Roman) | Intent |
|----------------------|-----------------|--------|
| نیا کام: [title] | naya kaam: [title] | CREATE_TODO |
| مکمل کریں: [title] | mukammal karen: [title] | COMPLETE_TODO |
| حذف کریں: [title] | delete karen: [title] | DELETE_TODO |
| سب کام دکھائیں | sab kaam dikhayein | LIST_TODOS |
| مکمل کام دکھائیں | mukammal kaam dikhayein | FILTER_COMPLETED |
| باقی کام دکھائیں | baqi kaam dikhayein | FILTER_PENDING |

**Voice Implementation:**
- Web Speech API with `en-US` and `ur-PK` language codes
- Pattern-based intent classification
- Entity extraction for todo titles
- Fallback to manual input if voice fails
- Visual feedback during listening/processing

---

## 7. Code Quality Standards

### 7.1 Frontend Code Quality

**Required:**
- ✅ TypeScript strict mode enabled
- ✅ No `any` types (use `unknown` and type guards)
- ✅ All components have prop types defined
- ✅ Error boundaries for error handling
- ✅ Loading states for async operations
- ✅ Proper use of Server vs Client Components
- ✅ ESLint and Prettier configured

**File Structure:**
```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── api/
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/         # Reusable UI components
│   ├── layouts/    # Layout components
│   └── features/   # Feature-specific components
├── lib/
│   ├── api.ts      # API client
│   ├── auth.ts     # Auth utilities
│   └── utils.ts    # Helper functions
├── hooks/          # Custom React hooks
├── types/          # TypeScript types
└── messages/       # i18n translation files
    ├── en.json     # English translations
    └── ur.json     # Urdu translations
```

### 7.2 Backend Code Quality

**Required:**
- ✅ Type hints on all functions
- ✅ Pydantic models for validation
- ✅ SQLModel for database operations
- ✅ FastAPI dependency injection
- ✅ Proper error handling with HTTPException
- ✅ Logging for debugging
- ✅ Black formatter, isort for imports

**File Structure:**
```
backend/
├── app/
│   ├── main.py           # FastAPI app
│   ├── models.py         # SQLModel database models
│   ├── schemas.py        # Pydantic request/response models
│   ├── database.py       # Database connection
│   ├── auth.py           # Authentication logic
│   ├── dependencies.py   # FastAPI dependencies
│   └── routers/
│       ├── auth.py       # Auth endpoints
│       └── todos.py      # Todo endpoints
├── alembic/              # Database migrations
└── tests/                # Backend tests
```

### 7.3 Type Safety

**TypeScript and Python type safety is MANDATORY:**

- **Frontend**: TypeScript strict mode, no `any` types
- **Backend**: Python type hints on all functions, Pydantic models for validation
- **API Contracts**: Shared TypeScript/Python types for request/response
- **Database**: SQLModel for type-safe ORM operations

### 7.4 Accessibility (WCAG 2.1 AA)

**All UI components MUST meet accessibility standards:**

- Keyboard navigation for all interactive elements
- ARIA labels for screen readers
- 4.5:1 color contrast ratio for text
- 44x44px minimum touch targets
- Focus indicators on all focusable elements
- Support for `prefers-reduced-motion`
- Semantic HTML (button, nav, main, etc.)

### 7.5 Responsive Design

**Mobile-first, responsive UI is REQUIRED:**

- Design for mobile (320px+) first
- Tablet breakpoints (768px+)
- Desktop breakpoints (1024px+)
- Use Tailwind responsive utilities
- Test on all breakpoints

---

## 8. Development Workflow

### 8.1 Feature Development Flow

1. **User Request** → Clarify requirements
2. **Create Spec** → `/sp.specify` command → `specs/<feature>/spec.md`
3. **Create Plan** → `/sp.plan` command → `specs/<feature>/plan.md`
4. **Create Tasks** → `/sp.tasks` command → `specs/<feature>/tasks.md`
5. **Implement** → `/sp.implement` command → Execute tasks with specialized agents
6. **Verify** → Test implementation against acceptance criteria
7. **Document** → Create PHR, update ADRs if needed
8. **Commit** → `/sp.git.commit_pr` command → Create commit and PR

### 8.2 Agent Selection Guidelines

**Use the correct agent for each task:**

| Task Type | Agent | Skills Referenced |
|-----------|-------|-------------------|
| UI components, layouts, styling | Frontend Builder | UI Skill |
| API endpoints, business logic | Backend API Guardian | API Skill, Auth Skill |
| Database schema, migrations | Database Architect | Database Skill |
| Authentication setup, JWT config | Auth Config Specialist | Auth Skill |
| Urdu translation, voice commands | Urdu Translator | Voice Skill |
| Feature orchestration | Spec Orchestrator | All Skills |

### 8.3 Prompt History Records (PHR)

**Every user interaction MUST generate a PHR in `history/prompts/`:**

- Constitution changes → `history/prompts/constitution/`
- Feature work → `history/prompts/<feature-name>/`
- General work → `history/prompts/general/`
- PHR template: `.specify/templates/phr-template.prompt.md`
- Skip PHR only for `/sp.phr` itself

### 8.4 Architecture Decision Records (ADR)

**Significant decisions MUST be documented in `history/adr/`:**

- ADR significance test: **Impact** (long-term) + **Alternatives** (multiple options) + **Scope** (cross-cutting)
- Suggest ADR with: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`"
- Wait for user consent; never auto-create ADRs
- Group related decisions (stacks, authentication, deployment) into one ADR

### 8.5 Quality Gates

All code **MUST** pass:

1. **Type Checking**: `mypy backend/` (Python), `tsc --noEmit` (TypeScript)
2. **Linting**: `ruff check backend/` (Python), `eslint frontend/` (TypeScript)
3. **Tests**: `pytest backend/tests/` (80%+ coverage), `jest frontend/__tests__/`
4. **Security**: Environment variable validation, JWT validation, user scoping
5. **Spec Compliance**: All changes referenced in specs/plan/tasks

### 8.6 Git Commit Standards

**Commit Message Format:**
```
<type>: <description>

<body>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

---

## 9. Environment Variables

### 9.1 Frontend (.env.local)
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3000
```

### 9.2 Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@host/database

# Authentication
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

**Environment Rules:**
- ✅ All secrets in environment variables
- ✅ Different secrets for dev/prod
- ✅ `.env.example` files with placeholders
- ✅ Never commit actual `.env` files
- ✅ Minimum 32 characters for secrets
- ✅ Generate SECRET_KEY with: `openssl rand -hex 32`

---

## 10. Performance Standards

### 10.1 Backend Performance

- API response time: **<200ms (p95)** for CRUD operations
- Database connection pooling enabled (SQLModel default)
- Async endpoints where I/O-bound (FastAPI `async def`)
- Pagination for list endpoints (max 100 items per page)

### 10.2 Frontend Performance

- Time to Interactive (TTI): **<3s** on 3G network
- First Contentful Paint (FCP): **<1.5s**
- Code splitting with Next.js dynamic imports
- Optimistic UI updates with rollback on error
- Lazy loading for images and non-critical components

### 10.3 Database Performance

- Indexes on: `user_id`, `created_at`, `updated_at`, `completed`
- Foreign key constraints enforced
- Daily backups (Neon automatic)
- Connection pooling (max 20 connections)

---

## 11. Deployment

### 11.1 Frontend Deployment (Vercel)

**Requirements:**
- Node.js 18+
- Environment variables configured in Vercel dashboard
- Build command: `pnpm build`
- Output directory: `.next`
- Framework preset: Next.js

**Deployment:**
```bash
cd frontend
pnpm build
vercel --prod
```

### 11.2 Backend Deployment (Render/Railway)

**Requirements:**
- Python 3.13+
- PostgreSQL connection string (Neon)
- Environment variables configured
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Deployment:**
```bash
cd backend
uv sync
uv run alembic upgrade head
```

### 11.3 Database (Neon)

**Configuration:**
- Connection pooling enabled
- SSL required (enforced by default)
- Backup schedule: Daily automatic
- Branching for staging/preview environments

**Get Neon Database URL:**
1. Go to [console.neon.tech](https://console.neon.tech/)
2. Select your project
3. Copy connection string from dashboard
4. Add to `DATABASE_URL` environment variable

---

## 12. Versioning & Breaking Changes

### 12.1 Semantic Versioning

- Format: **MAJOR.MINOR.PATCH**
- **MAJOR**: Breaking API changes (e.g., authentication model change)
- **MINOR**: New features, backward-compatible (e.g., new endpoints)
- **PATCH**: Bug fixes, no API changes

### 12.2 Deprecation Policy

- Deprecation warnings **MUST** be issued 2 versions before removal
- Breaking changes **MUST** be documented in CHANGELOG.md
- Migration guides **MUST** be provided for MAJOR version bumps

---

## 13. Governance

### 13.1 Constitution Authority

This constitution is the **highest authority** for the Agentic Todo project. All development decisions, code implementations, and architectural choices **MUST** comply with this document.

**Precedence:**
1. **Constitution** (this document) - Highest authority
2. **ADRs** (Architecture Decision Records)
3. **Feature Specs**
4. **Agent Skills**
5. **Code Comments**

### 13.2 Amendment Process

Constitutional changes require:

1. **Proposal**: Document proposed change with rationale
2. **ADR Creation**: Create ADR explaining decision, alternatives, tradeoffs
3. **Review**: Review by project stakeholders
4. **Approval**: Explicit approval required
5. **Update Constitution**: Modify with version bump:
   - **MAJOR**: Backward incompatible governance/principle removals or redefinitions
   - **MINOR**: New principle/section added or materially expanded guidance
   - **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements
6. **Update Templates**: Update dependent templates (plan, spec, tasks)
7. **Create PHR**: Document the amendment
8. **Commit**: `docs: amend constitution to vX.Y.Z (<reason>)`

### 13.3 Compliance Reviews

**Every PR/commit must verify:**
- ✅ Follows agentic development workflow
- ✅ Agents consulted relevant skills
- ✅ Security rules followed (JWT, user scoping)
- ✅ Type safety maintained
- ✅ Accessibility standards met (WCAG 2.1 AA)
- ✅ Documentation updated (PHRs, ADRs)
- ✅ Tests passing (80%+ coverage)

**Violations result in PR rejection.**

### 13.4 Conflict Resolution

Constitution takes precedence over:
- Individual preferences
- External style guides (unless explicitly adopted)
- Legacy code patterns

Ambiguities resolved via `/sp.clarify` and documented in ADR.

### 13.5 Skills as Living Documents

Skills (`.claude/skills/*.skill.md`) are **living documents** that evolve with the project:

- Skills can be updated based on learnings
- New patterns can be added to skills
- Security improvements must update skills
- Skills changes require PHR documentation
- Agents must be notified of skill updates

---

## 14. Success Metrics

### 14.1 Technical Metrics

- ✅ 100% agent-driven code generation
- ✅ Zero manual code commits
- ✅ 80%+ test coverage
- ✅ WCAG 2.1 AA compliance
- ✅ Sub-200ms API response times (p95)
- ✅ Zero security vulnerabilities
- ✅ Mobile-responsive UI

### 14.2 Process Metrics

- ✅ PHR created for every user interaction
- ✅ ADR created for significant decisions
- ✅ All features have spec → plan → tasks
- ✅ Skills referenced before implementation
- ✅ Git commits follow standards

### 14.3 User Experience Metrics

- ✅ Voice commands working in English + Urdu
- ✅ Dark mode support
- ✅ RTL support for Urdu
- ✅ Fast page loads (<2s TTI)
- ✅ Optimistic UI updates
- ✅ Accessible to screen readers

---

## 15. Version History

- **v1.0.0** (2026-01-20): Initial constitution with 8 core principles
- **v1.1.0** (2026-01-20): Added detailed implementation guidance (API specs, database schemas, deployment instructions, voice commands, code quality standards)

---

**Version**: 1.1.0
**Ratified**: 2026-01-20
**Last Amended**: 2026-01-20
**Next Review**: 2026-02-20

---

**This constitution governs all development on the Agentic Todo Full-Stack Web Application. All agents, developers, and contributors must comply with these principles and standards.**
