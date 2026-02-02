---
id: 2
title: Create Database Skill in Skills Folder
stage: general
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: aasif
command: general
labels: ["skill", "database", "sqlmodel", "crud", "pagination", "security"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/database.skill.md
  - history/prompts/general/2-create-database-skill.general.prompt.md
tests:
  - Verified file creation with ls command
---

## Prompt

now make # Database Skill

Reusable logic for:
- SQLModel CRUD
- Query filtering by user
- Pagination

Used by:
- Backend Agent

## Response snapshot

Created comprehensive Database skill file at `.claude/skills/database.skill.md` containing:

1. **SQLModel CRUD Operations**: Complete CRUD base class and user-scoped CRUD implementation with security-focused user isolation
2. **Query Filtering by User**: Mandatory user_id filtering on all operations with JWT-based authentication, preventing cross-user data access
3. **Pagination Patterns**: Generic pagination helper function with metadata (total, pages, has_next/prev) and FastAPI integration examples

The skill provides:
- Base CRUD class for generic operations
- User-scoped CRUD class (CRUDTodo) with security enforcement
- Generic pagination helper with PaginatedResponse model
- Database session management for Neon Serverless PostgreSQL
- Complete CRUD endpoint examples with FastAPI
- Security considerations and critical rules for user isolation
- Best practices for indexes, connection pooling, and performance
- Alembic migration guidance
- Testing and performance optimization strategies

Key security features:
- ALWAYS filter by user_id from JWT token (never from request body)
- Verify ownership before update/delete operations
- Index user_id for performance
- Use parameterized queries (SQL injection prevention)
- Connection pooling configuration for Neon

File size: 17K

## Outcome

- ✅ Impact: Created comprehensive database skill with strong security focus for user data isolation and multi-tenant architecture
- 🧪 Tests: Verified file creation and structure
- 📁 Files: Created .claude/skills/database.skill.md (17K) and PHR documentation
- 🔁 Next prompts: Implement database models and CRUD operations in backend using this skill pattern
- 🧠 Reflection: Skill emphasizes critical security rules for user isolation, which is essential for multi-tenant Todo application. Includes practical FastAPI endpoint examples and Neon PostgreSQL configuration.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual verification PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test skill invocation from backend-api-guardian agent when implementing database operations
