---
id: 015
title: Reject Low Priority Feature - Maintain Two-Level Priority
stage: general
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 006-high-priority
user: system
command: /sp.specify
labels: ["architectural-decision", "priority-system", "feature-rejection", "consistency"]
links:
  spec: specs/006-high-priority/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/general/015-reject-low-priority-feature.general.prompt.md
tests:
  - N/A (architectural decision, no implementation)
---

## Prompt

/sp.specify
---

## 📄 `specs/priority-low.md`

```md
# 🧩 SPECIFICATION – LOW PRIORITY TASK

---

## 1. Purpose

Allow an authenticated user to mark or reset a task to **Low Priority**, indicating non-urgent or optional tasks.

---

## 2. Functional Requirements

- User must be authenticated
- User can update priority only for their own tasks
- Low Priority is the default state for all tasks

---

## 3. Data Model Requirement

```json
{
  "priority": "low"
}
```

## Response snapshot

**Decision**: Rejected low priority feature to maintain architectural consistency.

**Rationale**:

Feature 006 (High Priority Task Marking) was recently created with a deliberate two-level priority system:
- `"high"` - Urgent tasks requiring immediate attention
- `"normal"` (default) - Regular tasks

Introducing "low priority" as a third level would:
1. **Create architectural inconsistency** - Feature 006 spec explicitly documents two levels in assumptions, requirements, and database design
2. **Add unnecessary complexity** - Users would face three-way decision (high/normal/low) vs. simple binary (urgent/not-urgent)
3. **Confuse UX** - Difference between "normal" and "low" is unclear; most tasks aren't "low priority"
4. **Complicate implementation** - Three-state selector, more complex sorting logic, additional filter controls
5. **Require spec revision** - Would need to update Feature 006 before implementation begins

**Options Presented to User**:

| Option | Approach | Implications |
|--------|----------|--------------|
| A (SELECTED) | Reject low priority - Keep two-level system | Maintains consistency; "normal" = non-urgent; simpler UX |
| B | Extend to three-level (low/normal/high) | More granular but adds complexity; requires Feature 006 update |
| C | Rename "normal" to "low" (two-level: low/high) | Confusing that "low" is default for most tasks |

**User Choice**: Option A

**Outcome**:
- No new feature specification created for "Low Priority"
- Feature 006 (High Priority) remains unchanged with two-level priority system
- Database schema: `priority VARCHAR(20) DEFAULT 'normal'` with values "high" and "normal" only
- UI: Simple binary toggle (Normal ↔ High) using star/flag icon
- Sorting: High priority first, then normal priority by created_at DESC
- Filtering: Single "High Priority" filter (no "Low Priority" filter needed)

**Benefits of Two-Level System**:
1. **Cognitive simplicity**: Binary urgent/not-urgent decision
2. **Clear UX**: "Mark as urgent" more intuitive than three-way choice
3. **Simpler code**: Two-state toggle, straightforward sorting/filtering
4. **Architectural consistency**: Aligns with Feature 006 as specified
5. **Industry standard**: Most todo apps use two-level (urgent/normal) or no priority

**Recommended Next Steps**:
- Proceed with Feature 006 implementation as specified
- Run `/sp.plan` on Feature 006 to create architecture plan
- Database Architect will design migration for two-level priority column
- No changes needed to Feature 006 spec

## Outcome

- ✅ Impact: Preserved architectural consistency by rejecting conflicting low priority feature; maintained two-level priority system from Feature 006
- 🧪 Tests: N/A (architectural decision, no implementation)
- 📁 Files: Created PHR documenting decision rationale
- 🔁 Next prompts: Proceed with `/sp.plan` on Feature 006 (High Priority) to begin implementation planning with two-level priority system
- 🧠 Reflection: This demonstrates importance of architectural consistency checks when new features are requested. The two-level priority system (high/normal) provides sufficient granularity for most use cases while maintaining simplicity. Three-level systems (high/normal/low) are rarely needed and often confuse users about the distinction between "normal" and "low". Binary urgent/not-urgent decisions are cognitively simpler and align with how users naturally think about task prioritization.

## Evaluation notes (flywheel)

- Failure modes observed: Potential architectural inconsistency caught early before implementation - successful validation process
- Graders run and results (PASS/FAIL): PASS - Detected conflict between requested three-level system and existing two-level specification, presented clear options to user, obtained decision, maintained consistency
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Continue with Feature 006 planning phase; monitor user feedback during implementation to validate that two-level priority meets user needs (if users consistently request "low priority", consider as future enhancement with proper ADR)
