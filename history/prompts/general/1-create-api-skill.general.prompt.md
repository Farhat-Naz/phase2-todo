---
id: 1
title: Create API Skill in Skills Folder
stage: general
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: aasif
command: general
labels: ["skill", "api", "setup", "reusable-logic"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/api.skill.md
  - history/prompts/general/1-create-api-skill.general.prompt.md
tests:
  - Verified file creation with ls command
---

## Prompt

make skill in sills folder  # API Skill

Reusable logic for:
- API request formatting
- Error handling
- JWT attachment

Used by:
- Frontend Agent
- Core Agent

## Response snapshot

Created comprehensive API skill file at `.claude/skills/api.skill.md` containing:

1. **API Request Formatting**: Standard `makeApiRequest` function with TypeScript interfaces for consistent HTTP request structure
2. **Error Handling**: Complete error handling system with user-friendly messages, type guards, and React hook integration
3. **JWT Attachment**: Authentication token retrieval for both client-side (Better Auth React hooks) and server-side (Next.js cookies) contexts

The skill provides:
- TypeScript interfaces for type-safe API calls
- Environment variable configuration
- Security considerations and best practices
- Example usage patterns for frontend components
- Integration points with Better Auth, FastAPI backend, and toast notifications
- Testing considerations

File size: 9.6K

## Outcome

- ✅ Impact: Created reusable API skill for standardized request handling across Frontend and Core agents
- 🧪 Tests: Verified file creation and directory structure
- 📁 Files: Created .claude/skills/api.skill.md (9.6K) and PHR documentation
- 🔁 Next prompts: Implement API client utilities in frontend using this skill pattern
- 🧠 Reflection: Skill provides comprehensive guidance for API integration with Better Auth, error handling, and JWT authentication

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual verification PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test skill invocation from frontend-builder agent when implementing API calls
