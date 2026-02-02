# ADR-002: Frontend UX Pattern for Priority Management

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-07
- **Feature:** 006-high-priority
- **Context:** Users need an intuitive, accessible, and performant way to mark todos as high priority. The solution must work across desktop and mobile, support keyboard and screen reader navigation (WCAG 2.1 AA), and provide instant feedback when toggling priority. Visual indicators must be prominent enough for quick scanning but not overwhelming for users with many high-priority tasks.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Establishes UX patterns for priority features
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Color-only, icon-only, sync vs async updates
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects UI, accessibility, performance, state management
-->

## Decision

We will implement a **multi-indicator priority UX with optimistic updates**, combining visual badges, icons, and color to ensure accessibility while leveraging TanStack Query for instant user feedback and automatic rollback on errors.

**Components of this decision:**

- **Visual Indicators**:
  - Badge: Red "HIGH PRIORITY" text label (12px, uppercase, semibold)
  - Icon: Filled star icon (lucide-react `Star` component, red-600)
  - Color: Red border (`border-red-500`) and subtle background (`bg-red-50`, dark: `bg-red-950`)
  - Combined approach ensures color + text + icon redundancy for accessibility

- **Interaction Pattern**:
  - Toggle Control: Star icon button (44x44px minimum touch target)
  - Keyboard: Space/Enter key support with visible focus indicator (`focus:ring-2 focus:ring-red-500`)
  - Screen Reader: ARIA labels ("Mark as high priority" / "Remove high priority") + live announcements

- **Update Strategy**:
  - **Optimistic Updates**: UI updates immediately (<50ms perceived latency) before API response
  - **State Management**: TanStack Query with automatic rollback on errors
  - **Error Handling**: Toast notification + visual revert on network failure, 401, or validation errors
  - **Consistency**: Background refetch after mutations to ensure server-client state synchronization

- **Sorting & Filtering**:
  - High priority todos always appear first in default list view
  - Filter toggle for "High Priority Only" view with empty state handling
  - Maintains sort order within priority levels (newest first by `created_at DESC`)

- **Accessibility (WCAG 2.1 AA)**:
  - Color contrast: 5.9:1 ratio for red badge on white background (exceeds 4.5:1 minimum)
  - Non-color indicators: Badge text + icon ensure colorblind users can distinguish priority
  - Keyboard navigation: Full tab-order support with visible focus indicators
  - Screen reader: `role="status" aria-live="polite"` for priority change announcements
  - Touch targets: 44x44px minimum for mobile (iOS/Android guidelines)

## Consequences

### Positive

- **Instant Feedback**: Optimistic updates provide <50ms perceived latency, making priority toggle feel responsive
- **Robust Error Handling**: Automatic rollback prevents UI-server state inconsistencies on network failures
- **Accessible**: Multi-indicator approach (color + text + icon) ensures usability for colorblind users and screen reader users
- **Mobile-Friendly**: 44x44px touch targets and responsive design work well on 320px+ screens
- **Scannable UI**: Red visual indicators make high-priority tasks stand out during quick list scans
- **Performance**: TanStack Query caching reduces API calls; optimistic updates eliminate waiting time
- **Consistent Patterns**: Reuses existing toggle patterns (similar to completion checkbox), reducing learning curve

### Negative

- **Visual Clutter**: Users with many high-priority tasks may experience visual noise from red indicators
- **Optimistic Update Complexity**: Requires careful implementation of rollback logic and race condition handling
- **Network Dependency**: Brief inconsistency if network is slow; user sees change before server confirms
- **State Management Overhead**: TanStack Query adds bundle size (~40KB gzipped) and mental complexity
- **Red Color Limitation**: Red universally signals urgency/danger, but may trigger anxiety for some users (no customization in MVP)
- **No Bulk Operations**: Users must toggle priority individually (no multi-select for bulk priority changes in MVP)

## Alternatives Considered

### Alternative A: Color-Only Indicators (No Text/Icon)
**Approach**: Red background/border only, no badge or icon

**Why Rejected**:
- Fails WCAG 2.1 AA: Not accessible to colorblind users (~8% of male population)
- Ambiguous semantics: Red could indicate error, urgency, or danger without explicit labeling
- Harder to distinguish: Subtle color differences are missed during quick scans
- Not screen reader friendly: No textual indicator for assistive technology

### Alternative B: Icon-Only Indicators (No Text)
**Approach**: Star icon only, no text badge or color change

**Why Rejected**:
- Cultural ambiguity: Star icons can mean "favorite", "featured", or "priority" depending on context
- Less prominent: Small icons are easily missed during list scanning
- Lower accessibility: Icon alone doesn't provide explicit screen reader announcement without ARIA
- Weaker visual hierarchy: Doesn't draw enough attention for urgent tasks

### Alternative C: Synchronous Updates (Wait for API Response)
**Approach**: Disable toggle button, show loading spinner, update UI after API responds

**Why Rejected**:
- Poor UX: Users wait 300-500ms for every toggle, making interaction feel sluggish
- Increased perceived latency: Spinner animation adds cognitive load
- Less responsive: Doesn't leverage modern web app patterns (optimistic updates are standard)
- Frustrating on slow networks: Unusable on 3G connections or high-latency scenarios

### Alternative D: No Rollback on Errors (Permanent Optimistic State)
**Approach**: Update UI optimistically, don't revert even if API fails

**Why Rejected**:
- Data inconsistency: UI shows "high priority" but server has "normal priority"
- Silent failures: User believes action succeeded, discovers later it didn't (bad UX)
- Sync issues: Refresh page reveals real state, breaking user trust
- Debugging nightmares: Hard to diagnose "works sometimes" bugs in production

### Alternative E: Drag-and-Drop Priority Sorting
**Approach**: Users manually reorder todos via drag-and-drop to set priority

**Why Rejected**:
- High complexity: Requires positional indexing, drag-and-drop libraries, complex state management
- Mobile-unfriendly: Drag-and-drop is awkward on touch screens
- Unclear semantics: Does position mean priority, or just manual ordering?
- Over-engineering for MVP: Two-level priority doesn't need fine-grained positioning
- Harder accessibility: Drag-and-drop is difficult for keyboard-only and screen reader users

## References

- Feature Spec: `specs/006-high-priority/spec.md` (User Stories 1, 2, 5)
- Research: `specs/006-high-priority/research.md` (Section 3: Frontend Visual Indicators, Section 4: Optimistic UI Updates, Section 10: Accessibility)
- Implementation Plan: `specs/006-high-priority/plan.md` (pending)
- Constitution: `.specify/memory/constitution.md` (Section 2.6: Accessibility WCAG 2.1 AA)
- Related ADRs: ADR-001 (Database Schema for Priority)
