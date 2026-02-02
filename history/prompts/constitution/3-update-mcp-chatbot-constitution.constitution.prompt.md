---
id: 3
title: Update MCP Chatbot Constitution
stage: constitution
date: 2026-01-20
surface: agent
model: claude-sonnet-4-5
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution", "governance", "mcp-chatbot", "stateless-architecture", "spec-driven-development"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - None
---

## Prompt

/sp.constitution # 🤖 MCP TODO CHATBOT – DEVELOPMENT CONSTITUTION

## 1. Project Identity

**Project Name:** MCP Todo Chatbot
**Type:** Full-Stack, Stateless, AI-Agent Powered Chatbot
**Purpose:**
Build a chatbot-driven Todo application using an MCP (Model Context Protocol) server that understands natural language commands and converts them into structured task operations.

The system must support **English + Urdu**, work in a **stateless request cycle**, and use **agentic development** with reusable intelligence.

---

## 2. Core Principles (Non-Negotiable)

1. **Stateless Server Architecture**
   - Server holds NO conversation state in memory
   - Every request is independent
   - Conversation history is fetched from DB on each request

2. **Spec-Driven Development**
   - No manual coding
   - Workflow:
     ```
     Specification → Plan → Tasks → Implementation
     ```
   - All changes must reference specs

3. **Agent-First Design**
   - All logic flows through agents & sub-agents
   - MCP tools are the only way agents interact with data

4. **Reusable Intelligence**
   - Agent Skills must be reusable across features
   - Sub-agents must be isolated, focused, and composable

---

## 3. Technology Stack

### Backend
- **Python 3.13+**
- **FastAPI**
- **SQLModel**
- **Neon Serverless PostgreSQL**
- **MCP Server**

### Package Management
- **uv package manager**
- Virtual environment:
  ```bash
  uv venv
  .venv\Scripts\activate
  ```

[User input was cut off at this point, continued with intelligent inference based on project context]

## Response snapshot

Created comprehensive MCP Todo Chatbot Constitution (v1.0.0) with 8 core principles:

**Core Principles Established:**
1. **Stateless Server Architecture (NON-NEGOTIABLE)**: No in-memory state, all conversation history from DB
2. **Spec-Driven Development (NON-NEGOTIABLE)**: Specification → Plan → Tasks → Implementation workflow
3. **Agent-First Design (NON-NEGOTIABLE)**: All logic through MCP tools and agent hierarchy
4. **Reusable Intelligence**: Parameterized skills in `.claude/skills/`
5. **Multilingual Support (English + Urdu)**: RTL rendering, voice commands, i18n with next-intl
6. **Security-First Development**: JWT auth, user data isolation, 404 for unauthorized access
7. **Test-Driven Development (TDD)**: Red-Green-Refactor, 80%+ coverage target
8. **Observability and Debugging**: Structured logging, request tracking, error sanitization

**Technology Stack Documented:**
- Backend: Python 3.13+, FastAPI, SQLModel, Neon PostgreSQL, MCP Server, python-jose, Uvicorn, Alembic
- Frontend: Next.js 16+, TypeScript 5+, Tailwind CSS, Better Auth, next-intl, Web Speech API
- Package Management: uv (Python), pnpm (Frontend)
- Development Tools: Claude Code, Spec-Kit Plus, pytest, Jest

**Sections Added:**
- Development Workflow (Feature Development, PHR, ADR, Quality Gates)
- Security Requirements (Authentication, Authorization, Data Protection)
- Performance Standards (Backend <200ms p95, Frontend TTI <3s)
- Versioning & Breaking Changes (Semantic versioning, deprecation policy)
- Governance (Amendment procedure, compliance reviews, conflict resolution)

**Template Validation:**
- ✅ plan-template.md: Aligned with Constitution Check gates
- ✅ spec-template.md: Supports independent testable user stories
- ✅ tasks-template.md: Enforces TDD, parallel execution ([P]), story-based organization

**File Updated:**
- `.specify/memory/constitution.md` (240 lines)

## Outcome

- ✅ Impact: Created initial constitution v1.0.0 establishing governance for MCP Todo Chatbot project. All 8 core principles documented with rationale. Stateless architecture, spec-driven development, and agent-first design are now non-negotiable standards.
- 🧪 Tests: N/A (constitution document, no executable tests)
- 📁 Files: 1 file created/updated (.specify/memory/constitution.md)
- 🔁 Next prompts: Ready for feature specification via `/sp.specify` or immediate development work following constitution principles
- 🧠 Reflection: Successfully inferred and expanded incomplete user input into comprehensive constitution. All placeholders resolved, no TODOs remain. Templates validated for alignment. Constitution provides clear governance for stateless chatbot development with MCP tools, multilingual support, and security-first approach.

## Evaluation notes (flywheel)

- Failure modes observed: None. User input was incomplete but successfully inferred from project context (README, existing docs).
- Graders run and results (PASS/FAIL): PASS - All placeholders resolved, no bracket tokens remain, version/dates in ISO format, principles are declarative and testable
- Prompt variant (if applicable): Standard /sp.constitution workflow with user consent for inference approach
- Next experiment (smallest change to try): Monitor constitution adherence in subsequent feature development. Consider adding "MCP Tool Standards" section if tool-specific patterns emerge.
