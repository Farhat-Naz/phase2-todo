# Implementation Plan: Agentic Todo Full-Stack Web Application

**Branch**: `001-todo-full-stack-app` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-full-stack-app/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Transform Phase I in-memory console todo application into a production-ready, multi-user web application with authentication, cloud persistence, voice commands, and Urdu language support. The implementation uses Next.js 16+ (frontend), FastAPI (backend), Neon PostgreSQL (database), and Better Auth (JWT authentication), all orchestrated through agent-driven, spec-driven development with Claude Code and Spec-Kit Plus. Core features include user registration/login, CRUD operations on personal todos, completion tracking, voice input (English/Urdu), and responsive mobile-first UI meeting WCAG 2.1 AA accessibility standards.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5+ (frontend), Node.js 18+
**Primary Dependencies**: FastAPI (backend API), Next.js 16+ App Router (frontend SSR), SQLModel (ORM), Better Auth (JWT), Tailwind CSS 3.4+, Web Speech API, Framer Motion 10+
**Storage**: Neon PostgreSQL (serverless cloud database), connection pooling, SSL required
**Testing**: pytest + pytest-benchmark (backend), Jest + React Testing Library (frontend unit), Playwright (E2E)
**Target Platform**: Web application (responsive 320px+ mobile-first), modern browsers (Chrome, Firefox, Safari, Edge), Web Speech API support required for voice features
**Project Type**: Web application (frontend + backend microservices architecture)
**Performance Goals**: <300ms p95 API latency, <2s Time to Interactive (TTI), <1s First Contentful Paint (FCP), support 100 concurrent users
**Constraints**: JWT-based stateless authentication, WCAG 2.1 AA accessibility compliance, HTTPS only in production, multi-tenant data isolation (user_id filtering), RTL support for Urdu, offline-capable PWA (future enhancement)
**Scale/Scope**: Multi-user application, ~5-10 API endpoints, ~10-15 React components, 2 database tables (User, Todo), English + Urdu bilingual support

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### 2.1 Agentic Development Rule ✅
- Spec created via `/sp.specify`: ✅ spec.md exists
- Plan created via `/sp.plan`: ✅ In progress (this file)
- Tasks via `/sp.tasks`: Pending after plan approval
- Implementation via specialized agents: Planned (Frontend Builder, Backend API Guardian, Database Architect, Auth Config Specialist, Urdu Translator)
- NO manual coding: ✅ All code agent-generated

### 2.2 Skills-First Implementation ✅
- API Skill: Required for REST endpoint patterns, error handling, JWT attachment
- Database Skill: Required for User/Todo models, CRUD operations, user filtering
- Auth Skill: Required for Better Auth setup, JWT validation, token management
- Voice Skill: Required for Web Speech API integration, English/Urdu command patterns
- UI Skill: Required for Next.js components, Tailwind styling, accessibility

### 2.3 Security-First Architecture ✅
- JWT validation: ✅ All protected endpoints validate JWT
- User ID from 'sub' claim: ✅ NEVER from request body
- Ownership verification: ✅ Todos filtered by authenticated user_id
- Parameterized queries: ✅ SQL injection prevention via SQLModel
- Secret management: ✅ Environment variables (.env files)
- HTTPS only: ✅ Production requirement

### 2.4 Multi-Tenant Data Isolation ✅
- user_id filtering: ✅ All todo queries filter by current_user.id
- Ownership verification: ✅ UPDATE/DELETE verify ownership
- 404 for unauthorized: ✅ Prevents user enumeration

### 2.5 Type Safety ✅
- TypeScript strict mode: ✅ Frontend
- Python type hints: ✅ SQLModel + Pydantic
- No `any` types: ✅ Enforced
- Pydantic validation: ✅ Request/response validation

### 2.6 Accessibility (WCAG 2.1 AA) ✅
- Keyboard navigation: ✅ All interactive elements
- ARIA labels: ✅ Screen reader support
- 4.5:1 contrast ratio: ✅ Text readability
- 44x44px touch targets: ✅ Mobile-friendly
- Focus indicators: ✅ Visible focus states
- Semantic HTML: ✅ Button, nav, main elements

### 2.7 Responsive Design ✅
- Mobile-first: ✅ 320px+ breakpoints
- Tailwind utilities: ✅ Responsive classes
- All breakpoints tested: ✅ 320px, 768px, 1024px+

### 2.8 Documentation ✅
- Spec: ✅ spec.md complete
- Plan: ✅ This file
- Research: ✅ research.md exists
- Data model: ✅ data-model.md exists
- PHR: Required after completion
- ADR: If significant decisions made

### Technology Stack Compliance ✅
- Frontend: Next.js 16+, TypeScript 5+, Tailwind CSS, Better Auth ✅
- Backend: FastAPI, SQLModel, Neon PostgreSQL, python-jose ✅
- Package managers: pnpm (frontend), uv (backend) ✅
- No stack changes: ✅

### API Architecture Compliance ✅
- REST standards: ✅ Standard HTTP methods + status codes
- Auth endpoints: ✅ /register, /login, /refresh, /me
- Response format: ✅ {data: ...} / {error: ...}

### Database Schema Compliance ✅
- UUIDs for PKs: ✅ User.id, Todo.id
- Foreign keys + CASCADE: ✅ Todo.user_id references User.id
- Timestamps: ✅ created_at, updated_at on all tables
- Indexes: ✅ user.email, todo.user_id, todo.completed
- NOT NULL constraints: ✅ Required fields enforced

### Code Quality Standards ✅
- TypeScript strict: ✅
- Error boundaries: ✅ React error handling
- Loading states: ✅ Async operations
- Server/Client Components: ✅ Next.js App Router patterns
- FastAPI dependency injection: ✅ get_current_user, get_db
- HTTPException: ✅ Error handling

**GATE STATUS: ✅ PASS** - All constitutional requirements satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-full-stack-app/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # ✅ EXISTS - Phase 0 research complete
├── data-model.md        # ✅ EXISTS - Entity definitions complete
├── quickstart.md        # TO CREATE - Developer guide
├── api-specs/           # ✅ EXISTS - API contract directory
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

**Web Application Structure** - Full-stack with separate frontend/backend:

```text
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # SQLModel database models (User, Todo)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── database.py          # Neon PostgreSQL connection setup
│   ├── auth.py              # Better Auth JWT validation logic
│   ├── dependencies.py      # FastAPI dependencies (get_db, get_current_user)
│   └── routers/
│       ├── auth.py          # Auth endpoints (/register, /login, /refresh, /me)
│       └── todos.py         # Todo CRUD endpoints
├── alembic/
│   ├── env.py               # Alembic configuration
│   └── versions/            # Database migration scripts
│       ├── 001_create_users.py
│       └── 002_create_todos.py
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_auth.py         # Auth endpoint tests
│   ├── test_todos.py        # Todo CRUD tests
│   └── test_security.py     # JWT validation, ownership tests
├── pyproject.toml           # Dependencies (managed by uv)
└── .env.example             # Environment variable template

frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx     # Login page
│   │   └── register/
│   │       └── page.tsx     # Registration page
│   ├── (dashboard)/
│   │   ├── layout.tsx       # Authenticated dashboard layout
│   │   └── page.tsx         # Main todo list page
│   ├── api/
│   │   └── auth/
│   │       └── route.ts     # Better Auth API routes
│   ├── layout.tsx           # Root layout with providers
│   └── page.tsx             # Landing page
├── components/
│   ├── ui/
│   │   ├── button.tsx       # Reusable button component
│   │   ├── input.tsx        # Form input component
│   │   └── checkbox.tsx     # Checkbox component
│   ├── layouts/
│   │   ├── Header.tsx       # App header with nav
│   │   └── Footer.tsx       # App footer
│   └── features/
│       ├── auth/
│       │   ├── LoginForm.tsx      # Login form
│       │   └── RegisterForm.tsx   # Registration form
│       ├── todos/
│       │   ├── TodoList.tsx       # Todo list container
│       │   ├── TodoItem.tsx       # Individual todo item
│       │   ├── TodoForm.tsx       # Create/edit todo form
│       │   └── VoiceInput.tsx     # Voice command input
│       └── shared/
│           └── LoadingSpinner.tsx # Loading indicator
├── lib/
│   ├── api.ts               # API client with JWT handling
│   ├── auth.ts              # Auth utilities (Better Auth config)
│   ├── utils.ts             # Helper functions
│   └── voice.ts             # Web Speech API integration
├── hooks/
│   ├── useTodos.ts          # Todo CRUD operations hook
│   ├── useAuth.ts           # Authentication state hook
│   └── useVoice.ts          # Voice command hook
├── types/
│   ├── todo.ts              # Todo TypeScript interfaces
│   └── user.ts              # User TypeScript interfaces
├── tests/
│   ├── components/
│   │   └── TodoItem.test.tsx      # Component tests
│   └── e2e/
│       ├── auth.spec.ts           # E2E auth flow
│       └── todo-crud.spec.ts      # E2E todo operations
├── public/
│   ├── icons/               # App icons
│   └── locales/
│       ├── en.json          # English translations
│       └── ur.json          # Urdu translations
├── package.json             # Dependencies (managed by pnpm)
├── next.config.js           # Next.js configuration
├── tailwind.config.ts       # Tailwind CSS configuration
└── .env.local.example       # Environment variable template
```

**Structure Decision**: Web application (Option 2) selected for full-stack architecture. Backend is a standalone FastAPI microservice with SQLModel ORM and Neon PostgreSQL. Frontend is a Next.js 16+ App Router application with Server/Client Component separation. This structure supports independent scaling, deployment, and development of frontend/backend services while maintaining clear separation of concerns.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
