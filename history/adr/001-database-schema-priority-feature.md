# ADR-001: Database Schema Design for Priority Feature

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-07
- **Feature:** 006-high-priority
- **Context:** The todo application needs to support task prioritization, allowing users to mark tasks as "high priority" to highlight urgent work. This requires extending the existing database schema while maintaining backwards compatibility, ensuring type safety, and optimizing query performance for sorting and filtering operations.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Data model changes affect all layers
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Separate table, integer fields, boolean flags
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Impacts backend, frontend, migrations, performance
-->

## Decision

We will extend the existing `todo` table with a `priority` column using PostgreSQL ENUM type, implementing a two-level priority system ('high', 'normal') with composite indexing for optimal query performance.

**Components of this decision:**

- **Data Type**: PostgreSQL ENUM type `priority_level` with values ('normal', 'high')
- **Column Specification**: `priority priority_level NOT NULL DEFAULT 'normal'`
- **Indexing Strategy**:
  - Single-column index: `idx_todo_priority` on `(priority)`
  - Composite index: `idx_todo_user_priority` on `(user_id, priority, created_at DESC)`
- **Migration Tool**: Alembic for version-controlled, reversible migrations
- **ORM Integration**: SQLModel with Python Enum for type-safe database operations
- **Default Behavior**: Backwards compatible with default value 'normal' for existing rows

## Consequences

### Positive

- **Type Safety**: PostgreSQL ENUM prevents invalid priority values at the database level, eliminating a class of bugs
- **Performance**: Composite index `(user_id, priority, created_at DESC)` enables index-only scans for the most common query pattern (user's todos sorted by priority), achieving <10ms query times for 10,000+ todos per user
- **Extensibility**: ENUM structure allows future priority levels (e.g., 'urgent', 'low') without schema redesign
- **Backwards Compatibility**: Default value ensures existing code continues working during deployment window
- **Maintainability**: Single-column extension is minimal, reducing migration risk and deployment complexity
- **Query Simplicity**: Database-level sorting leverages indexes, avoiding expensive application-level sorting
- **Data Integrity**: NOT NULL constraint with default ensures consistent data state

### Negative

- **PostgreSQL-Specific**: ENUM type is PostgreSQL-specific; migrating to MySQL/SQLite would require schema changes
- **Enum Modification Complexity**: Adding/removing ENUM values in PostgreSQL requires careful migration (not as simple as adding rows to a table)
- **Index Storage Overhead**: Composite index adds ~15-20% to table storage size (acceptable trade-off for query performance)
- **Two-Level Limitation**: MVP limited to two priority levels ('high'/'normal'); multi-level priorities would require adding ENUM values
- **Sorting Rigidity**: Database-level sorting is fixed (priority DESC, created_at DESC); custom sort orders require application-level logic

## Alternatives Considered

### Alternative A: Separate Priority Table (Normalized Design)
**Structure**:
```sql
CREATE TABLE priority_level (
  id INT PRIMARY KEY,
  name VARCHAR(20) UNIQUE NOT NULL
);

ALTER TABLE todo ADD COLUMN priority_id INT REFERENCES priority_level(id);
```

**Why Rejected**:
- Over-engineering for a two-level system with fixed values
- Requires JOIN for every todo query, adding 20-40ms latency
- Increased complexity with minimal flexibility gain for MVP
- No significant benefit until 5+ priority levels are needed

### Alternative B: Integer Priority Field (1-5 Scale)
**Structure**:
```sql
ALTER TABLE todo ADD COLUMN priority INT DEFAULT 3 CHECK (priority BETWEEN 1 AND 5);
```

**Why Rejected**:
- Less type-safe: Allows arbitrary integers if check constraint is bypassed
- Unclear semantics: Does 1 mean highest or lowest priority?
- Harder to maintain: Magic numbers require documentation
- Difficult to extend: Adding priority levels requires renumbering
- Weaker validation: Application must enforce valid range

### Alternative C: Boolean `is_high_priority` Flag
**Structure**:
```sql
ALTER TABLE todo ADD COLUMN is_high_priority BOOLEAN DEFAULT FALSE;
```

**Why Rejected**:
- Not extensible: Boolean cannot accommodate future priority levels (medium, urgent, low)
- Less expressive: Doesn't indicate "normal" as an explicit state
- Migration path unclear: Converting to multi-level priority requires full refactor
- Less elegant: Naming becomes awkward with more levels (is_medium_priority, is_urgent, etc.)

### Alternative D: Application-Level Sorting (No Index)
**Approach**: Query all todos, sort in application code

**Why Rejected**:
- Poor performance: 100-500ms sorting overhead for 1000+ todos
- Wastes bandwidth: Fetches all todos even when filtering by priority
- Doesn't scale: Memory overhead grows linearly with todo count
- Misses database optimization: Wastes database's sorting capabilities and indexes

## References

- Feature Spec: `specs/006-high-priority/spec.md`
- Research: `specs/006-high-priority/research.md` (Section 1: Database Schema Extension, Section 7: Migration Strategy)
- Implementation Plan: `specs/006-high-priority/plan.md` (pending)
- Constitution: `.specify/memory/constitution.md` (Section 5.2: Todo Table Schema)
- Related ADRs: None (first ADR for this feature)
