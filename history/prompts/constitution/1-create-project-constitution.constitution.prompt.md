---
id: 1
title: Create Project Constitution for Agentic Todo App
stage: constitution
date: 2026-01-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: aasif
command: /sp.constitution
labels: ["constitution", "governance", "architecture", "security", "standards", "agentic-development"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - history/prompts/constitution/1-create-project-constitution.constitution.prompt.md
tests:
  - Verified constitution file creation
---

## Prompt

/sp.constituition  # 📜 CONSTITUTION.md
## Agentic Todo Full-Stack Web Application (Phase II)

---

## 1. Purpose & Vision

The purpose of this project is to build a **modern, secure, multi-user Todo web application** using an **Agentic Development Stack** powered by **Claude Code and Spec-Kit Plus**.

This project must demonstrate:

- 🤖 Agent & Sub-Agent collaboration
- 📜 Spec-driven development
- ♻️ Reusable intelligence (Agent Skills)
- 🌐 Full-stack architecture
- 🔐 Secure authentication
- 🗣️ Voice commands
- 🌍 Urdu language support
- ☁️ Cloud-native persistence using Neon Database

**No manual coding is allowed.**
All implementation must be produced, reviewed, and refined through Claude Code agents.

[Additional content provided by user...]

## Response snapshot

Created comprehensive project constitution at `.specify/memory/constitution.md` with complete governance framework for the Agentic Todo Full-Stack Web Application (Phase II).

**Constitution Structure (12 Sections):**

1. **Purpose & Vision**: Multi-user Todo app with agent-driven development, no manual coding allowed
2. **Governing Principles**: 8 core principles including:
   - Agentic Development Rule (7-step workflow)
   - Skills-First Implementation (5 skills referenced)
   - Security-First Architecture (7 critical security rules)
   - Multi-Tenant Data Isolation (user_id filtering mandatory)
   - Type Safety (TypeScript strict, Python type hints)
   - Accessibility (WCAG 2.1 AA compliance)
   - Responsive Design (mobile-first)
   - Documentation (PHRs, ADRs, Specs)

3. **Technology Stack (IMMUTABLE)**:
   - Frontend: Next.js 16+, TypeScript 5+, Tailwind CSS 3.4+, Better Auth, Framer Motion, Web Speech API
   - Backend: FastAPI, SQLModel, Neon PostgreSQL, python-jose, Alembic, Uvicorn
   - Tools: Claude Code, Spec-Kit Plus, Git, pnpm, Poetry/pip

4. **API Architecture**: Complete REST API standards with:
   - Endpoint structure (/api/todos, /api/auth/*)
   - HTTP methods and status codes
   - Request/response formats
   - Full authentication endpoint specs (register, login, refresh, me)
   - Complete todo endpoint specs (CRUD + pagination)

5. **Database Schema**: SQL definitions for:
   - User table (UUID, email, hashed_password, timestamps)
   - Todo table (UUID, user_id FK, title, description, completed, timestamps)
   - Indexes on critical fields (user_id, email, completed, created_at)

6. **Voice Command Support**:
   - English commands: 7 intents (CREATE, COMPLETE, DELETE, LIST, FILTER_COMPLETED, FILTER_PENDING, SEARCH)
   - Urdu commands: Both script and Roman transliteration for 6 intents
   - Web Speech API implementation with ur-PK language code

7. **Code Quality Standards**:
   - Frontend: TypeScript strict, no `any`, Server/Client Components, ESLint/Prettier
   - Backend: Type hints, Pydantic, SQLModel, FastAPI DI, Black/isort
   - Testing: 80% coverage minimum, unit/integration/E2E tests

8. **Development Workflow**:
   - 8-step feature development flow (Request → Spec → Plan → Tasks → Implement → Verify → Document → Commit)
   - Agent selection guidelines (6 specialized agents)
   - Git commit standards with conventional commits

9. **Environment Variables**:
   - Frontend: NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL
   - Backend: DATABASE_URL, BETTER_AUTH_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES, CORS_ORIGINS
   - Security rules: Secrets in env vars only, different for dev/prod, min 32 chars

10. **Deployment**:
    - Frontend: Vercel (Node.js 18+, pnpm build)
    - Backend: Render/Railway (Python 3.11+, uvicorn)
    - Database: Neon (connection pooling, SSL, daily backups, branching)

11. **Governance**:
    - Constitution as highest authority
    - Amendment process (Proposal → ADR → Review → Approval → Migration → Update)
    - Compliance verification checklist (7 requirements)
    - Skills as living documents

12. **Success Metrics**:
    - Technical: 100% agent-driven, zero manual code, 80%+ coverage, WCAG AA, sub-second API
    - Process: PHRs for all interactions, ADRs for decisions, specs for features
    - UX: Voice (EN+UR), dark mode, RTL, PWA, fast loads

**Key Security Requirements (NON-NEGOTIABLE):**
- JWT validation on EVERY protected endpoint
- User scoping on ALL database queries
- NEVER trust user_id from request body
- Ownership verification before mutations
- Secrets in environment variables only
- HTTPS in production
- Access tokens: 30 min, Refresh tokens: 7 days

**Authentication Flow:**
```
User Login → Better Auth JWT → httpOnly cookie →
Authorization header → FastAPI validates →
User ID from 'sub' → DB filtered by user_id
```

**API Endpoint Structure:**
- `/api/todos` - List (GET), Create (POST)
- `/api/todos/{id}` - Get (GET), Update (PUT/PATCH), Delete (DELETE)
- `/api/auth/login` - Login (POST)
- `/api/auth/register` - Register (POST)
- `/api/auth/refresh` - Refresh token (POST)
- `/api/auth/me` - Current user (GET)

**File Specifications:**
- Frontend file structure: app/ (auth/dashboard routes), components/ (ui/layouts/features), lib/
- Backend file structure: app/ (main.py, models.py, schemas.py, database.py, auth.py, routers/)
- 12 major sections, 748 lines total

**Version Information:**
- Version: 1.0.0
- Ratified: 2026-01-06
- Last Amended: 2026-01-06
- Next Review: 2026-02-06

## Outcome

- ✅ Impact: Created comprehensive project constitution establishing governance, architecture standards, security rules, and development workflow for entire Agentic Todo application
- 🧪 Tests: Verified constitution file created successfully
- 📁 Files: Created .specify/memory/constitution.md (748 lines) and PHR documentation
- 🔁 Next prompts: Begin feature development following constitution guidelines (spec → plan → tasks → implement)
- 🧠 Reflection: Constitution serves as highest authority document, defining immutable tech stack, mandatory security practices, agent-driven workflow, and quality standards. Strong emphasis on security-first architecture with explicit user data isolation requirements. All development must be 100% agent-driven with no manual coding. Skills referenced as foundational patterns. Complete API specifications provided for both authentication and todo management. Voice command support for English and Urdu explicitly defined. Governance includes amendment process and compliance verification.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual verification PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create first feature spec following constitutional guidelines, verify agents follow security rules and skills patterns
