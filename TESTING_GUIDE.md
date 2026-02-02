# MCP Chatbot Local Testing Guide

## Current Status

### Completed:
- ✅ Database tables created (chat_session, chat_message)
- ✅ Models implemented (ChatSession, ChatMessage)
- ✅ MCP tools ready (add_task, list_tasks, complete_task, delete_task)
- ✅ Chatbot service implemented
- ✅ API endpoints created (/api/chat)

### Issue:
- ❌ Virtual environment mismatch (using phaseII-todo venv instead of phaseIII-todoapp)
- ❌ MCP package not found in runtime environment

## Solution 1: Fix Virtual Environment

### Step 1: Clean up old venv references
```bash
# Remove any cached bytecode
cd backend
rm -rf __pycache__ app/__pycache__ app/**/__pycache__

# Ensure MCP is installed in correct venv
cd ..
uv sync
```

### Step 2: Start server from project root
```bash
# From project root directory
uv run python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

###  Step 3: Verify server is running
Open browser: http://127.0.0.1:8000/docs

You should see:
- /api/chat (POST) - Send message to chatbot
- /api/chat/sessions (GET) - List sessions
- /api/chat/sessions/{session_id}/messages (GET) - Get messages

## Solution 2: Test with Mock (Simpler, No MCP needed)

If virtual environment issues persist, you can test the chatbot with a mock implementation:

### Step 1: Temporarily disable MCP imports

Comment out MCP imports in `backend/app/services/chatbot_service.py`:

```python
# from app.mcp.client import get_mcp_client  # TEMPORARILY DISABLED
from app.mcp.context import (
    build_chat_context,
    save_messages_to_session,
    get_or_create_session,
    update_session_title_from_first_message,
)
```

###  Step 2: The mock is already implemented!

The `_mock_mcp_call` method in chatbot_service.py is already set up for testing.

### Step 3: Start server
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Test with curl

**Test 1: Send a message (creates new session)**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, add buy groceries to my tasks",
    "language": "en"
  }'
```

**Expected Response:**
```json
{
  "session_id": "uuid-here",
  "assistant_message": "I can help you with tasks. What would you like to do?",
  "language": "en",
  "timestamp": "2026-01-20T12:00:00.000Z"
}
```

**Test 2: Continue conversation in same session**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show my tasks",
    "session_id": "SESSION_ID_FROM_TEST_1",
    "language": "en"
  }'
```

**Test 3: List all sessions**
```bash
curl http://localhost:8000/api/chat/sessions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Test 4: Get session messages**
```bash
curl http://localhost:8000/api/chat/sessions/SESSION_ID/messages \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Get JWT Token for Testing

### Option 1: Login via API
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'
```

### Option 2: Use existing token from browser
1. Login at http://localhost:3000/login
2. Open DevTools → Application → Cookies
3. Copy `access_token` value
4. Use in curl: `-H "Authorization: Bearer ACCESS_TOKEN"`

## Testing with Postman

1. Import collection from `/api/docs` (FastAPI auto-generates OpenAPI spec)
2. Set environment variable: `JWT_TOKEN`
3. Add to all requests: Header `Authorization: Bearer {{JWT_TOKEN}}`
4. Test endpoints:
   - POST /api/chat
   - GET /api/chat/sessions
   - GET /api/chat/sessions/{id}/messages

## Full MCP Integration (After fixing venv)

Once virtual environment is fixed, to enable real MCP:

### Step 1: Install dependencies
```bash
uv add mcp
# OR for Anthropic Claude:
uv add mcp anthropic
# OR for OpenAI:
uv add mcp openai
```

### Step 2: Add environment variable

Add to `.env.local`:
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
# OR
OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Replace mock with real MCP call

In `backend/app/services/chatbot_service.py`, replace the mock call with:

```python
# Real MCP call (implement based on your LLM provider)
async with get_mcp_client() as mcp_client:
    # Send to Claude/OpenAI with tool definitions
    response = await mcp_client.call_llm(
        messages=full_context,
        tools=["add_task", "list_tasks", "complete_task", "delete_task"],
        user_id=str(user_id)
    )
    assistant_message = response.content
```

## Verification Checklist

- [ ] Database tables exist (chat_session, chat_message)
- [ ] Server starts without errors
- [ ] API docs accessible at /docs
- [ ] Can send message and get response
- [ ] Session is created and stored in database
- [ ] Messages are persisted in database
- [ ] Conversation history is maintained across requests
- [ ] Can list all sessions for user
- [ ] Can retrieve messages for a session
- [ ] Urdu language support works (send message with "language": "ur")

## Next Steps

After successful API testing:
1. Build frontend chat UI (optional)
2. Add real LLM integration (Anthropic Claude or OpenAI)
3. Test end-to-end with real task management
4. Deploy to production

## Troubleshooting

### "401 Unauthorized"
- JWT token is invalid or expired
- Re-login and get new token

### "500 Internal Server Error"
- Check backend logs for detailed error
- Database connection issue?  - Verify `DATABASE_URL` in .env

### "404 Not Found"
- Wrong endpoint URL
- Check `/docs` for correct endpoints

### "MCP module not found"
- Virtual environment issue
- Use Solution 2 (Mock) for testing

## Files Modified

1. `backend/app/routers/chat.py` - API endpoints
2. `backend/app/services/chatbot_service.py` - Chat logic
3. `backend/app/mcp/tools.py` - Task management tools
4. `backend/app/mcp/client.py` - MCP client
5. `backend/app/mcp/context.py` - Context management
6. `backend/app/mcp/server.py` - MCP server
7. `backend/app/models.py` - ChatSession, ChatMessage models
8. `backend/app/main.py` - Router registration

## Success!

When you see this response, everything is working:

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "assistant_message": "I can help you with tasks. What would you like to do?",
  "language": "en",
  "timestamp": "2026-01-20T12:00:00.000Z"
}
```

The chatbot is ready for testing! 🎉
