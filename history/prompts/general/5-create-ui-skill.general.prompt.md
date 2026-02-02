---
id: 5
title: Create UI Skill for Beautiful User Interfaces
stage: general
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: aasif
command: general
labels: ["skill", "ui", "design-system", "tailwind", "accessibility", "responsive", "dark-mode", "animations"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/ui.skill.md
  - history/prompts/general/5-create-ui-skill.general.prompt.md
tests:
  - Verified file creation with ls command
---

## Prompt

now make best ui skill for beautiful user interface

## Response snapshot

Created comprehensive UI skill file at `.claude/skills/ui.skill.md` containing:

1. **Design System Foundation**: Complete Tailwind config with custom color palette (primary, semantic, neutral), typography scale, spacing system, border radius, shadows, and custom animations/keyframes

2. **Component Patterns**: Production-ready reusable components:
   - Button: 5 variants (primary, secondary, outline, ghost, danger), 3 sizes, loading states, icons
   - Input: Labels, error states, helper text, left/right icons, full accessibility
   - Card: Multiple variants (default, bordered, elevated), responsive padding, hover effects
   - Checkbox: Accessible with label association, proper focus states

3. **Layout Patterns**: Flexible layout components:
   - AppLayout: Main app structure with navbar, sidebar, responsive main content
   - Container: 5 size options (sm to full), responsive padding
   - Grid: Responsive grid system (1-12 columns), configurable gaps

4. **Animation and Transitions**: Framer Motion integration:
   - FadeIn, SlideUp, ScaleIn components
   - StaggeredList for list animations
   - Motion presets for common UI patterns

5. **Dark Mode Implementation**: Complete theme system:
   - next-themes provider setup
   - ThemeToggle component with Sun/Moon icons
   - System preference detection
   - Class-based theme switching

6. **Accessibility Patterns**: WCAG 2.1 compliant components:
   - VisuallyHidden component for screen readers
   - SkipLink for keyboard navigation
   - Accessible Modal with Headless UI
   - Focus management and ARIA attributes

Additional content:
- **Implementation Checklist**: 13-item checklist for UI component development
- **Design Principles**: Visual hierarchy, white space, color usage, typography, consistency
- **Responsive Design**: Mobile-first breakpoints (sm to 2xl) with usage examples
- **Accessibility Best Practices**: Keyboard navigation, screen readers, color contrast, reduced motion
- **Performance Optimization**: Images (Next.js Image), fonts (preload, subset), CSS (purge), JS (code splitting)
- **Utility Classes**: cn() function for Tailwind class merging
- **Testing Considerations**: Dark mode, keyboard navigation, screen readers, responsive layouts
- **Integration Points**: Next.js, Tailwind, Framer Motion, next-themes, Headless UI, Lucide icons
- **Required Dependencies**: Complete package.json with exact versions
- **Example TodoCard**: Beautiful, animated todo card with all best practices applied

Design system highlights:
- Primary brand color: Sky blue (#0ea5e9)
- Semantic colors: Success (green), Warning (amber), Error (red)
- Typography: Inter (sans), Cal Sans (display)
- Spacing: 4px grid system
- Shadows: 6 elevation levels plus glow effect
- Animations: fade-in, slide-up, slide-down, scale-in, spin-slow, bounce-slow, pulse-slow
- Dark mode: Full support with automatic system detection

Accessibility features:
- WCAG 2.1 AA compliant (4.5:1 text contrast)
- Full keyboard navigation
- Screen reader support with ARIA
- Focus visible indicators
- 44x44px minimum touch targets
- Reduced motion support
- Skip links for main content

Performance features:
- Tailwind purge for minimal CSS
- Next.js Image optimization
- Font subsetting and preloading
- Code splitting with dynamic imports
- React.memo for expensive renders
- CSS containment

File size: 30K

## Outcome

- ✅ Impact: Created comprehensive UI skill with production-ready design system, reusable components, accessibility patterns, and best practices for modern web interfaces
- 🧪 Tests: Verified file creation and structure
- 📁 Files: Created .claude/skills/ui.skill.md (30K) and PHR documentation
- 🔁 Next prompts: Implement UI components in frontend using this design system, build component library with Storybook
- 🧠 Reflection: Skill provides complete design system foundation with Tailwind CSS, covering all aspects of modern UI development from components to accessibility to performance. Includes beautiful TodoCard example demonstrating all concepts. Strong emphasis on accessibility (WCAG 2.1 AA), dark mode support, and responsive design. Component patterns follow industry best practices with proper TypeScript typing, forwardRef support, and composition patterns.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual verification PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test skill invocation from frontend-builder agent when implementing UI components, verify dark mode transitions, test accessibility with screen readers
