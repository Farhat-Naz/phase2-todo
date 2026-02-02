# Research: Agentic Todo Full-Stack Web Application

**Feature**: `001-todo-full-stack-app`
**Date**: 2026-01-07
**Status**: Complete

## Overview

This document consolidates research findings for the foundational architecture of the agentic todo full-stack web application. The system transforms a Phase I console application into a multi-user web app with authentication, cloud persistence, voice commands, and Urdu language support—all built using spec-driven, agent-orchestrated development.

---

## 1. Technology Stack Research

### Decision: Next.js 16+ (App Router) + FastAPI + Neon PostgreSQL + Better Auth

**Rationale**:
- **Frontend (Next.js 16+)**: Server-Side Rendering (SSR), App Router for improved routing, excellent TypeScript support, production-ready with Vercel deployment
- **Backend (FastAPI)**: Async Python framework, automatic OpenAPI docs, Pydantic validation, excellent SQLModel integration
- **Database (Neon PostgreSQL)**: Serverless PostgreSQL, auto-scaling, branching for development, AWS infrastructure
- **Auth (Better Auth)**: Modern JWT-based auth library for Next.js, seamless integration, built-in session management

**Integration Pattern**:
```
User Browser (Next.js SSR)
      ↓ JWT in httpOnly cookie
FastAPI Backend
      ↓ SQLModel ORM
Neon PostgreSQL (Cloud)
```

**Alternatives Considered**:
1. **MERN Stack (MongoDB + Express + React + Node)**: Rejected - Less type-safe than PostgreSQL + SQLModel, no built-in schema validation
2. **Django + React**: Rejected - Django admin overhead unnecessary for API-only backend, FastAPI lighter and faster
3. **Supabase (full-stack BaaS)**: Rejected - Less control over backend logic, vendor lock-in concerns, doesn't align with agent-driven custom development
4. **Clerk/Auth0 (auth SaaS)**: Rejected - Better Auth provides similar features with more control and no recurring costs

---

## 2. Authentication Architecture Research

### Decision: Better Auth with JWT (Access + Refresh tokens)

**Rationale**:
- **Stateless**: JWT tokens enable horizontal scaling (no server-side session store required)
- **Secure**: `httpOnly` cookies prevent XSS attacks, tokens signed with HMAC SHA256
- **Standards-Based**: JWT is industry standard (RFC 7519), well-understood security model
- **Refresh Pattern**: Short-lived access tokens (30 min) + long-lived refresh tokens (7 days) balance security and UX

**Implementation Pattern**:
```typescript
// Frontend: Better Auth configuration
export const auth = createAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  cookie: {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
  },
  jwt: {
    expiresIn: '30m',  // Access token
  },
  session: {
    expiresIn: '7d',   // Refresh token
  },
});

// Backend: JWT validation
from fastapi import Depends, HTTPException
from jose import jwt, JWTError

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
        return user_id
    except JWTError:
        raise HTTPException(status_code=401)
```

**Security Measures**:
- Password hashing with bcrypt (salt rounds: 12)
- HTTPS-only in production
- CORS configured for frontend origin only
- JWT secret minimum 32 characters, stored in environment variables
- Token expiration enforced on every request

**Alternatives Considered**:
1. **Session Cookies (server-side sessions)**: Rejected - Requires Redis/database for session storage, doesn't scale horizontally as easily
2. **OAuth2 Password Flow**: Rejected - Unnecessary complexity for simple email/password auth
3. **Magic Link (passwordless)**: Rejected - Email infrastructure overhead, slower UX for MVP
4. **NextAuth.js**: Rejected - Better Auth is more modern, lighter, and designed specifically for Next.js App Router

---

## 3. Database Schema Design Research

### Decision: PostgreSQL with SQLModel ORM, normalized schema with foreign keys

**Rationale**:
- **Relational Model**: User-Todo one-to-many relationship is natural fit for SQL
- **Type Safety**: SQLModel provides Pydantic validation + SQLAlchemy ORM in one library
- **ACID Guarantees**: PostgreSQL ensures data consistency for multi-user operations
- **Neon Features**: Serverless scaling, connection pooling, database branching for testing

**Schema Definition**:
```sql
CREATE TABLE "user" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE todo (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  title VARCHAR(500) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_email ON "user"(email);
CREATE INDEX idx_todo_user_id ON todo(user_id);
CREATE INDEX idx_todo_completed ON todo(completed);
CREATE INDEX idx_todo_created_at ON todo(created_at DESC);
```

**Indexing Strategy**:
- `user.email`: Fast login queries
- `todo.user_id`: Fast user-scoped todo queries (most common operation)
- `todo.completed`: Fast filtering by completion status
- `todo.created_at DESC`: Fast sorting by creation date

**Alternatives Considered**:
1. **MongoDB (NoSQL)**: Rejected - Less type-safe, weaker consistency guarantees, unnecessary flexibility for structured data
2. **SQLite (embedded DB)**: Rejected - Not suitable for multi-user cloud deployment
3. **Firebase Firestore**: Rejected - Vendor lock-in, less control, doesn't align with agent-driven SQL development
4. **Separate user_session table**: Rejected - JWT tokens are stateless, no need for session persistence

---

## 4. API Architecture Research

### Decision: RESTful API with OpenAPI 3.0 documentation

**Rationale**:
- **Industry Standard**: REST is well-understood, tooling mature, easy for agents to generate
- **FastAPI Auto-Docs**: OpenAPI spec generated automatically from Python type hints
- **Resource-Based**: Maps naturally to User and Todo entities
- **HTTP Semantics**: Standard methods (GET, POST, PATCH, DELETE) clearly indicate operations

**Endpoint Structure**:
```
# Authentication
POST   /api/auth/register      - Create new user account
POST   /api/auth/login         - Login and receive JWT
POST   /api/auth/refresh       - Refresh access token
GET    /api/auth/me            - Get current user info

# Todos (all require auth)
GET    /api/todos              - List user's todos (paginated)
POST   /api/todos              - Create new todo
GET    /api/todos/{id}         - Get specific todo
PATCH  /api/todos/{id}         - Update todo fields
DELETE /api/todos/{id}         - Delete todo
```

**Standard Response Format**:
```json
// Success
{
  "data": { ... }
}

// Error
{
  "detail": "Error message"
}

// Validation Error
{
  "detail": [
    {"loc": ["body", "title"], "msg": "field required", "type": "value_error.missing"}
  ]
}
```

**Alternatives Considered**:
1. **GraphQL**: Rejected - Overkill for simple CRUD operations, steeper learning curve for agents
2. **RPC-style API**: Rejected - Less discoverable, doesn't leverage HTTP methods semantically
3. **gRPC**: Rejected - Binary protocol harder to debug, unnecessary performance optimization for web app
4. **Nested Routes** (e.g., `/api/users/{id}/todos`): Rejected - Simpler to scope by JWT user ID than URL nesting

---

## 5. Frontend State Management Research

### Decision: TanStack Query for server state + React Context for client state

**Rationale**:
- **TanStack Query**: Best-in-class server state management, automatic caching, request deduplication, background refetch
- **React Context**: Lightweight for client-only state (language preference, theme)
- **No Redux**: Unnecessary complexity for simple app, TanStack Query handles async state better

**Implementation Pattern**:
```typescript
// TanStack Query for todos (server state)
export function useTodos() {
  return useQuery({
    queryKey: ['todos'],
    queryFn: async () => {
      const res = await api.get('/api/todos');
      return res.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// React Context for language (client state)
const LanguageContext = createContext({ lang: 'en', setLang: () => {} });
```

**Benefits**:
- Automatic loading/error states
- Optimistic updates with automatic rollback
- Background data synchronization
- Request deduplication (multiple components requesting same data = 1 API call)

**Alternatives Considered**:
1. **Redux Toolkit**: Rejected - Too much boilerplate for simple app, TanStack Query better for async state
2. **Zustand**: Rejected - Similar to Context but adds dependency, Context sufficient for client state
3. **SWR**: Rejected - TanStack Query has better TypeScript support and more features
4. **Recoil**: Rejected - More complex than needed, smaller ecosystem than TanStack Query

---

## 6. Voice Integration Research

### Decision: Web Speech API with pattern-based intent classification

**Rationale**:
- **Native Browser API**: No external dependencies, works offline, free
- **Bilingual Support**: Supports both `en-US` and `ur-PK` language codes
- **Client-Side Processing**: Low latency (<1s), privacy-preserving (no voice data sent to server)
- **Pattern Matching**: Simple regex patterns sufficient for todo commands

**Implementation Pattern**:
```typescript
const recognition = new webkitSpeechRecognition();
recognition.lang = currentLanguage === 'ur' ? 'ur-PK' : 'en-US';
recognition.continuous = false;
recognition.interimResults = false;

recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  const command = parseCommand(transcript);
  executeCommand(command);
};

function parseCommand(transcript: string) {
  // English patterns
  if (/^add todo:?\s*(.+)/i.test(transcript)) {
    return { action: 'create', title: RegExp.$1 };
  }
  // Urdu patterns
  if (/^نیا کام:?\s*(.+)/.test(transcript)) {
    return { action: 'create', title: RegExp.$1 };
  }
  return { action: 'unknown' };
}
```

**Browser Support**:
- Chrome/Edge: Full support
- Safari: Partial support (iOS 14.5+)
- Firefox: Limited support (requires flag)

**Alternatives Considered**:
1. **OpenAI Whisper API**: Rejected - Costs money, adds latency (network round-trip), privacy concerns
2. **Google Cloud Speech-to-Text**: Rejected - Requires API key, costs, sends voice to cloud
3. **Custom ML Model (TensorFlow.js)**: Rejected - Large bundle size, training complexity, unnecessary
4. **Server-Side Processing**: Rejected - Adds latency, requires streaming audio upload

---

## 7. Multilingual Support Research

### Decision: next-intl for i18n with RTL layout support for Urdu

**Rationale**:
- **next-intl**: Best Next.js 13+ i18n library, App Router compatible, TypeScript-first
- **RTL Support**: CSS `dir="rtl"` with Tailwind RTL utilities (`rtl:` prefix)
- **Translation Files**: JSON format, easy for agents to generate
- **Language Detection**: Browser language preference with manual override

**Implementation Pattern**:
```typescript
// messages/en.json
{
  "common": {
    "add_todo": "Add Todo",
    "complete": "Complete",
    "delete": "Delete"
  }
}

// messages/ur.json
{
  "common": {
    "add_todo": "نیا کام شامل کریں",
    "complete": "مکمل کریں",
    "delete": "حذف کریں"
  }
}

// Component usage
import { useTranslations } from 'next-intl';

export function AddTodoButton() {
  const t = useTranslations('common');
  return <button>{t('add_todo')}</button>;
}

// RTL layout
<html dir={locale === 'ur' ? 'rtl' : 'ltr'} lang={locale}>
```

**Tailwind RTL**:
```css
/* Applies only in RTL mode */
.rtl\:text-right { text-align: right; }
.rtl\:ml-auto { margin-left: auto; }
```

**Alternatives Considered**:
1. **react-i18next**: Rejected - More complex setup, heavier bundle, less Next.js-optimized
2. **Manual RTL with CSS**: Rejected - next-intl provides better integration
3. **Server-Side Translation**: Rejected - Client-side switching is better UX
4. **Full Urdu UI Rewrite**: Rejected - i18n keys more maintainable than duplicate components

---

## 8. Deployment Strategy Research

### Decision: Vercel (frontend) + Render/Railway (backend) + Neon (database)

**Rationale**:
- **Vercel**: Best Next.js hosting, automatic deployments, edge network, free tier generous
- **Render/Railway**: Simple FastAPI deployment, free tier, PostgreSQL connection support
- **Neon**: Serverless PostgreSQL, branching for preview deployments, generous free tier

**Deployment Flow**:
```
Git Push → GitHub
    ↓
Frontend: Vercel auto-deploy (main branch → production)
Backend: Render auto-deploy (main branch → production)
Database: Neon main branch (production)
```

**Environment Variables**:
```
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
BETTER_AUTH_SECRET=<32+ char secret>
BETTER_AUTH_URL=https://yourdomain.com

# Backend (.env)
DATABASE_URL=postgresql://user:pass@neon.tech/db
BETTER_AUTH_SECRET=<same as frontend>
CORS_ORIGINS=https://yourdomain.com
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Alternatives Considered**:
1. **Netlify**: Rejected - Vercel better for Next.js (built by same team)
2. **AWS (EC2 + RDS)**: Rejected - Over-engineering, more expensive, complex setup
3. **Heroku**: Rejected - No longer free tier, less modern than Render/Railway
4. **Self-Hosted VPS**: Rejected - Maintenance overhead, doesn't align with serverless strategy

---

## 9. Security Architecture Research

### Decision: Defense-in-depth with JWT validation, user scoping, and HTTPS

**Security Layers**:

1. **Authentication Layer**:
   - JWT signature validation on every protected request
   - Token expiration enforced (30 min access, 7 day refresh)
   - `httpOnly` cookies prevent XSS token theft

2. **Authorization Layer**:
   - User ID extracted from JWT `sub` claim (never from request body)
   - All todo queries filtered by `user_id = current_user.id`
   - Ownership verification before UPDATE/DELETE operations
   - Return 404 (not 403) to prevent user enumeration

3. **Transport Layer**:
   - HTTPS enforced in production (Vercel + Render provide free SSL)
   - CORS restricted to frontend origin only

4. **Data Layer**:
   - Passwords hashed with bcrypt (12 rounds)
   - SQL injection prevented by SQLModel parameterized queries
   - Input validation via Pydantic models

5. **Application Layer**:
   - XSS prevented by React automatic escaping
   - CSRF protection via `sameSite` cookie attribute

**Threat Model**:
| Threat | Mitigation | Residual Risk |
|--------|------------|---------------|
| Stolen JWT token | Short expiration (30 min), httpOnly cookies | ⚠️ Low (if XSS bypassed) |
| SQL injection | Parameterized queries (SQLModel) | ✅ None |
| XSS | React auto-escaping, CSP headers | ✅ None |
| CSRF | sameSite cookies, CORS | ✅ None |
| Password brute force | bcrypt slow hashing, rate limiting (future) | ⚠️ Medium (no rate limiting in MVP) |
| User enumeration | 404 for all unauthorized access | ✅ None |

**Alternatives Considered**:
1. **API Keys**: Rejected - Less secure than JWT, no user context
2. **Basic Auth**: Rejected - Sends credentials with every request, less secure
3. **OAuth2 Authorization Code Flow**: Rejected - Unnecessary complexity for simple email/password auth
4. **Session Tokens (opaque)**: Rejected - Requires server-side storage, doesn't scale horizontally

---

## 10. Testing Strategy Research

### Decision: Multi-layer testing (unit + integration + E2E) with agent-generated tests

**Test Coverage Plan**:

#### Backend Tests (pytest)
```python
# Unit tests - models, utils
def test_user_password_hashing():
    user = User(email="test@example.com", password="secret123")
    assert user.verify_password("secret123")
    assert not user.verify_password("wrong")

# Integration tests - API endpoints
def test_create_todo_requires_auth(client):
    response = client.post("/api/todos", json={"title": "Test"})
    assert response.status_code == 401

def test_user_sees_only_own_todos(client, auth_headers):
    # Create todos for two users, verify isolation
    ...
```

#### Frontend Tests (Vitest + React Testing Library)
```typescript
// Component tests
test('TodoItem displays title and description', () => {
  render(<TodoItem todo={{ title: 'Test', description: 'Desc' }} />);
  expect(screen.getByText('Test')).toBeInTheDocument();
});

// Integration tests with MSW (Mock Service Worker)
test('creating todo shows in list', async () => {
  render(<TodoList />);
  await userEvent.type(screen.getByPlaceholderText('Add todo'), 'Buy milk');
  await userEvent.click(screen.getByText('Add'));
  expect(await screen.findByText('Buy milk')).toBeInTheDocument();
});
```

#### E2E Tests (Playwright)
```typescript
test('full user journey', async ({ page }) => {
  // Register
  await page.goto('/register');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'Password123!');
  await page.click('button[type="submit"]');

  // Create todo
  await page.fill('[placeholder="Add todo"]', 'Buy groceries');
  await page.press('[placeholder="Add todo"]', 'Enter');
  await expect(page.locator('text=Buy groceries')).toBeVisible();

  // Mark complete
  await page.click('[aria-label="Mark as complete"]');
  await expect(page.locator('text=Buy groceries')).toHaveClass(/completed/);
});
```

**Coverage Goals**:
- Backend: 90%+ line coverage
- Frontend: 80%+ line coverage
- E2E: All critical user flows

**Alternatives Considered**:
1. **Manual Testing Only**: Rejected - Not repeatable, regression risk
2. **E2E Only**: Rejected - Slow, brittle, poor debugging
3. **Cypress**: Rejected - Playwright has better TypeScript support, faster
4. **Jest**: Rejected - Vitest is faster, better Vite integration

---

## Summary

All foundational architectural decisions have been resolved through research. Key decisions:

1. **Tech Stack**: Next.js 16+ + FastAPI + Neon PostgreSQL + Better Auth
2. **Authentication**: JWT with access (30 min) + refresh (7 day) tokens
3. **Database**: PostgreSQL with SQLModel, User + Todo entities, indexed for performance
4. **API**: RESTful with OpenAPI docs, standard HTTP methods
5. **State Management**: TanStack Query (server) + React Context (client)
6. **Voice**: Web Speech API with pattern-based intent classification
7. **i18n**: next-intl with RTL support for Urdu
8. **Deployment**: Vercel (frontend) + Render (backend) + Neon (database)
9. **Security**: Defense-in-depth (JWT + user scoping + HTTPS + input validation)
10. **Testing**: Multi-layer with agent-generated tests (unit + integration + E2E)

**No unknowns remain. Ready for Phase 1 (data model + contracts).**
