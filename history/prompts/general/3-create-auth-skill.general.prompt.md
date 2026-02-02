---
id: 3
title: Create Auth Skill in Skills Folder
stage: general
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: aasif
command: general
labels: ["skill", "auth", "jwt", "authentication", "security", "better-auth"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/auth.skill.md
  - history/prompts/general/3-create-auth-skill.general.prompt.md
tests:
  - Verified file creation with ls command
---

## Prompt

now make # Auth Skill

Reusable logic for:
- JWT decoding
- Token validation
- User extraction

Used by:
- Backend Agent

## Response snapshot

Created comprehensive Auth skill file at `.claude/skills/auth.skill.md` containing:

1. **JWT Decoding and Validation**: Complete JWT token parsing with signature verification, expiration checks, and claim validation using python-jose
2. **Token Validation**: Secure token extraction from Authorization headers, Bearer scheme validation, and error handling
3. **User Extraction**: FastAPI dependency patterns for extracting user ID and full user objects from JWT tokens

The skill provides:
- JWT decoding functions with TokenData/TokenPayload models
- Token extraction from Authorization headers and requests
- Three FastAPI dependencies:
  - `get_current_user_id()`: Lightweight, returns UUID only
  - `get_current_user()`: Full user object from database
  - `get_current_user_id_optional()`: Optional auth for public endpoints
- Better Auth integration patterns (login, register, refresh, /me endpoints)
- Access token creation with configurable expiration
- Complete security considerations and critical rules

Key security features:
- Secret key management (environment variables only)
- Token signature verification on every request
- Expiration validation with configurable times
- HTTPS enforcement in production
- Password security via Better Auth
- Standard HTTP 401 error responses with WWW-Authenticate headers
- Token transmission best practices

Additional content:
- Implementation checklist
- Environment variables required
- Protected endpoint examples (todos, profile, optional auth)
- Standard error definitions for common auth scenarios
- Best practices (rate limiting, MFA, audit logging, token revocation)
- Testing considerations
- Integration points with Better Auth, FastAPI, SQLModel
- Required dependencies (python-jose, passlib)
- Migration guide from client-side only to backend JWT

File size: 18K

## Outcome

- ✅ Impact: Created comprehensive auth skill with production-ready JWT validation and Better Auth integration for backend API security
- 🧪 Tests: Verified file creation and structure
- 📁 Files: Created .claude/skills/auth.skill.md (18K) and PHR documentation
- 🔁 Next prompts: Implement authentication endpoints and dependencies in FastAPI backend using this skill pattern
- 🧠 Reflection: Skill provides three levels of authentication dependencies (user ID only, full user object, optional auth) for flexible endpoint protection. Strong emphasis on security best practices including secret management, token validation, and HTTPS enforcement.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual verification PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test skill invocation from backend-api-guardian agent when implementing protected endpoints with JWT authentication
