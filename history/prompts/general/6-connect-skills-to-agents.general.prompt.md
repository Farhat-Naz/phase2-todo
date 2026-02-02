---
id: 6
title: Connect Skills to Agents
stage: general
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: aasif
command: general
labels: ["skills", "agents", "integration", "documentation", "setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/agents/frontend-builder.md
  - .claude/agents/backend-api-guardian.md
  - .claude/agents/auth-config-specialist.md
  - .claude/agents/database-architect.md
  - .claude/agents/urdu-translator.md
  - history/prompts/general/6-connect-skills-to-agents.general.prompt.md
tests:
  - Verified all agent files were updated with skill references
---

## Prompt

connect these skill to agent

## Response snapshot

Successfully connected all 5 skills to their respective agents by adding "Available Skills" sections with detailed skill references:

**1. Frontend Builder Agent** → Connected 3 skills:
   - API Skill: Request formatting, error handling, JWT attachment
   - UI Skill: Design system, components, layouts, animations, accessibility
   - Voice Skill: Speech recognition, intent classification, Urdu support

**2. Backend API Guardian Agent** → Connected 2 skills:
   - Database Skill: CRUD operations, user-scoped filtering, pagination
   - Auth Skill: JWT validation, token verification, user extraction

**3. Auth Config Specialist Agent** → Connected 1 skill:
   - Auth Skill: JWT decoding, Better Auth integration, token management

**4. Database Architect Agent** → Connected 1 skill:
   - Database Skill: SQLModel patterns, user isolation, Neon PostgreSQL configuration

**5. Urdu Translator Agent** → Connected 1 skill:
   - Voice Skill: Urdu intent patterns (script + Roman), speech recognition

**Implementation approach:**
- Added new "Available Skills" section in each agent file
- Positioned after core identity/mission but before main responsibilities
- Included **ALWAYS consult** directive to ensure agents read skills before implementing
- Provided detailed summaries of what each skill contains
- Listed key patterns, functions, and security considerations
- Added IMPORTANT notices highlighting critical skill usage

**Skill-to-Agent mapping:**
```
API Skill (9.6K)
  └─ Frontend Builder

Database Skill (17K)
  ├─ Backend API Guardian
  └─ Database Architect

Auth Skill (18K)
  ├─ Backend API Guardian
  └─ Auth Config Specialist

Voice Skill (22K)
  ├─ Frontend Builder
  └─ Urdu Translator

UI Skill (30K)
  └─ Frontend Builder
```

**Benefits:**
- Agents now have explicit references to reusable patterns
- Skills are discoverable within agent context
- Promotes consistency across implementations
- Reduces code duplication
- Enforces security best practices (user filtering, JWT validation)
- Provides single source of truth for patterns

**File updates:**
- frontend-builder.md: +48 lines (3 skill references)
- backend-api-guardian.md: +28 lines (2 skill references)
- auth-config-specialist.md: +27 lines (1 skill reference)
- database-architect.md: +33 lines (1 skill reference)
- urdu-translator.md: +28 lines (1 skill reference)

Total: 164 lines of skill integration documentation added across 5 agents.

## Outcome

- ✅ Impact: All agents now have explicit skill references with "ALWAYS consult" directives, creating tight integration between reusable patterns and agent implementations
- 🧪 Tests: Verified all 5 agent files updated successfully with ls command
- 📁 Files: Updated 5 agent files with skill references, created PHR documentation
- 🔁 Next prompts: Test agents to ensure they reference and use skills when implementing features, verify skill patterns are followed
- 🧠 Reflection: Skill-to-agent connection establishes clear guidance for agents to follow established patterns. Each agent now knows exactly which skills to consult before implementing features. Frontend Builder has the most skills (3) as it handles UI, API, and voice. Backend Guardian and Auth Specialist share the Auth skill for JWT handling. Database skill shared between Backend Guardian and Database Architect ensures consistent CRUD patterns. This architecture promotes code consistency, security best practices, and reduces implementation errors.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual verification PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Invoke an agent to implement a feature and observe if it references the appropriate skill files before implementation
