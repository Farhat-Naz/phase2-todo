# Quickstart: Agentic Todo Full-Stack Web Application

**Feature**: 001-todo-full-stack-app
**Date**: 2026-01-07

## Overview

This guide helps developers set up and run the full-stack todo application, and helps users understand how to use the application features.

---

## For Developers

### Prerequisites

**Backend**:
- Python 3.13+
- uv package manager ([install guide](https://docs.astral.sh/uv/))
- Neon PostgreSQL account ([sign up](https://neon.tech))

**Frontend**:
- Node.js 18+
- pnpm package manager ([install guide](https://pnpm.io/installation))

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install dependencies**:
   ```bash
   uv sync  # Creates virtual environment and installs dependencies from pyproject.toml
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values:
   # DATABASE_URL=postgresql://user:password@host/database
   # BETTER_AUTH_SECRET=your-secret-key-min-32-chars
   # ACCESS_TOKEN_EXPIRE_MINUTES=30
   # REFRESH_TOKEN_EXPIRE_DAYS=7
   # CORS_ORIGINS=http://localhost:3000
   ```

4. **Run database migrations**:
   ```bash
   uv run alembic upgrade head
   ```

5. **Start the development server**:
   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```

6. **Verify backend is running**:
   - Visit http://localhost:8000/docs for interactive API documentation (Swagger UI)
   - Visit http://localhost:8000/redoc for alternative API documentation

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   pnpm install
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your actual values:
   # NEXT_PUBLIC_API_URL=http://localhost:8000
   # BETTER_AUTH_SECRET=your-secret-key-min-32-chars
   # BETTER_AUTH_URL=http://localhost:3000
   ```

4. **Start the development server**:
   ```bash
   pnpm dev
   ```

5. **Verify frontend is running**:
   - Visit http://localhost:3000
   - You should see the landing page

### Testing

**Backend Tests**:
```bash
cd backend
uv run pytest -v
uv run pytest --cov=app --cov-report=html  # With coverage
```

**Frontend Tests**:
```bash
cd frontend
pnpm test              # Unit tests
pnpm test:e2e          # End-to-end tests with Playwright
```

---

## For Users

### Getting Started

1. **Create an Account**:
   - Click "Sign Up" or "Register"
   - Enter your email and a strong password (min 8 chars, 1 uppercase, 1 lowercase, 1 number)
   - Click "Create Account"
   - You'll be automatically logged in

2. **Log In** (returning users):
   - Click "Log In"
   - Enter your email and password
   - Click "Sign In"

### Managing Todos

#### Create a Todo

**Using the Form**:
1. Type your task in the "What needs to be done?" input
2. (Optional) Click to expand and add a description
3. Press Enter or click "Add Todo"

**Using Voice Command** (English):
- Click the microphone icon
- Say: "Add todo: Buy groceries"
- The todo will be created automatically

**Using Voice Command** (Urdu):
- Click the microphone icon
- Say: "نیا کام: گروسری خریدیں" (New task: Buy groceries)
- The todo will be created automatically

#### Mark Todo as Complete

- Click the checkbox next to the todo
- The todo will show a strikethrough and move to the completed section
- Click again to mark as incomplete

#### Edit a Todo

1. Click the edit icon (pencil) on the todo
2. Modify the title or description
3. Click "Save" or press Enter
4. Your changes are saved automatically

#### Delete a Todo

1. Click the delete icon (trash) on the todo
2. Confirm deletion in the dialog
3. The todo is permanently removed

### Voice Commands Reference

#### English Commands

| Command | Example |
|---------|---------|
| Create todo | "Add todo: Call dentist" |
| Create todo | "New task: Finish report" |
| Mark complete | "Complete: Buy milk" |
| Mark complete | "Finish: Call dentist" |

#### Urdu Commands

| Command | Example (Roman) | Example (Urdu Script) |
|---------|-----------------|----------------------|
| Create todo | "naya kaam: doodh khareedna" | "نیا کام: دودھ خریدنا" |
| Mark complete | "mukammal karen: doodh khareedna" | "مکمل کریں: دودھ خریدنا" |

### Troubleshooting

**Can't log in**:
- Check that your email and password are correct
- Passwords are case-sensitive
- If you forgot your password, use the "Forgot Password" link

**Todos not saving**:
- Check your internet connection
- Refresh the page to sync with the server
- If the problem persists, try logging out and back in

**Voice commands not working**:
- Grant microphone permission when prompted
- Ensure you're using a supported browser (Chrome, Edge, Safari)
- Speak clearly and at a normal pace
- If recognition fails, try again or use the manual input

**Urdu text not displaying correctly**:
- Ensure your browser supports Unicode/RTL text
- Check that your system has Urdu fonts installed
- Try refreshing the page

---

## API Usage (For Developers)

### Authentication

#### Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
  }'
```

Response (201):
```json
{
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "John Doe"
    }
  }
}
```

#### Log In

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

#### Get Current User

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Todo Operations

#### Create a Todo

```bash
curl -X POST http://localhost:8000/api/todos \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false
  }'
```

#### List All Todos

```bash
curl -X GET http://localhost:8000/api/todos \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Get a Specific Todo

```bash
curl -X GET http://localhost:8000/api/todos/TODO_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Update a Todo

```bash
curl -X PUT http://localhost:8000/api/todos/TODO_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and snacks",
    "description": "Milk, eggs, bread, chips",
    "completed": false
  }'
```

#### Mark Todo as Complete (PATCH)

```bash
curl -X PATCH http://localhost:8000/api/todos/TODO_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

#### Delete a Todo

```bash
curl -X DELETE http://localhost:8000/api/todos/TODO_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Deployment

### Backend Deployment (Render/Railway)

1. Connect your GitHub repository
2. Set environment variables:
   - `DATABASE_URL` (from Neon)
   - `BETTER_AUTH_SECRET`
   - `CORS_ORIGINS` (your frontend URL)
3. Set build command: `uv sync`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment (Vercel)

1. Connect your GitHub repository
2. Set environment variables:
   - `NEXT_PUBLIC_API_URL` (your backend URL)
   - `BETTER_AUTH_SECRET`
   - `BETTER_AUTH_URL` (your frontend URL)
3. Vercel auto-detects Next.js and configures build settings
4. Deploy!

### Database (Neon)

- Database is already deployed as serverless PostgreSQL
- Enable connection pooling for production
- Set up daily backups
- Use branching feature for staging environments

---

## Key Features Summary

✅ **Multi-user authentication** with JWT tokens
✅ **Personal todo lists** with full CRUD operations
✅ **Voice commands** in English and Urdu
✅ **Responsive mobile-first** UI (320px+)
✅ **WCAG 2.1 AA accessible** with keyboard navigation and screen reader support
✅ **Real-time updates** with optimistic UI
✅ **Secure** with JWT validation and user data isolation
✅ **Cloud-native** with Neon serverless PostgreSQL

---

## Next Steps

After setting up the development environment:
1. Run `/sp.tasks` to generate implementation tasks
2. Execute tasks with specialized agents (Frontend Builder, Backend Guardian, Database Architect, Auth Specialist)
3. Test all acceptance scenarios from spec.md
4. Create PR with `/sp.git.commit_pr`

**Happy coding!** 🚀
