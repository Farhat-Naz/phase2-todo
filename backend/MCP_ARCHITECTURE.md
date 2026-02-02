# MCP-Based Chatbot Architecture

## Overview
Stateless chatbot architecture using MCP (Model Context Protocol) for task management through natural language.

## Components

### 1. MCP Server (`app/mcp/server.py`)
Exposes task operations as MCP tools that can be called by OpenAI function calling.

**Tools:**
- `create_task` - Create new todo task
- `list_tasks` - List user's tasks (with optional filters)
- `update_task` - Update existing task
- `delete_task` - Delete task
- `mark_task_complete` - Mark task as complete/incomplete

**Properties:**
- Stateless: Each tool call is independent
- Database-backed: All state stored in PostgreSQL
- User-scoped: Tools automatically filter by authenticated user

### 2. Database Models (`app/models.py`)

**ChatConversation:**
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to User
- `session_id` (str): Client-provided session identifier
- `title` (str): Auto-generated conversation title
- `created_at` (datetime)
- `updated_at` (datetime)

**ChatMessage:**
- `id` (UUID): Primary key
- `conversation_id` (UUID): Foreign key to ChatConversation
- `role` (str): "user" or "assistant"
- `content` (str): Message text
- `tool_calls` (JSON): OpenAI tool calls (if any)
- `created_at` (datetime)

### 3. Chat Endpoint (`app/routers/chat.py`)

**POST /api/chat/**

**Flow:**
1. Receive user message + session_id
2. Load conversation history from database
3. Build OpenAI messages with MCP tools
4. Call OpenAI with function calling enabled
5. Execute any tool calls via MCP server
6. Save messages to database
7. Return assistant response

**Stateless Design:**
- No in-memory session storage
- All state in database
- Each request loads/saves from DB

### 4. MCP Tool Execution (`app/mcp/executor.py`)

**Responsibilities:**
- Receive tool call from OpenAI response
- Validate tool parameters
- Execute MCP tool with user context
- Return formatted result
- Handle errors gracefully

## Data Flow

```
User Message
    ↓
Chat Endpoint (FastAPI)
    ↓
Load Conversation (PostgreSQL)
    ↓
Build Context + MCP Tools
    ↓
OpenAI GPT-4o (Function Calling)
    ↓
Tool Call? → MCP Tool Execution → Database
    ↓
Save Conversation (PostgreSQL)
    ↓
Return Response
```

## Security

1. **User Isolation:**
   - All MCP tools automatically scope to current user
   - User ID from JWT token
   - Cannot access other users' tasks

2. **Stateless Authentication:**
   - JWT token required for each request
   - No server-side session state

3. **Input Validation:**
   - Pydantic models for all inputs
   - SQLModel prevents SQL injection
   - Tool parameters validated before execution

## Benefits

1. **Scalability:**
   - Stateless design scales horizontally
   - Database handles all persistence
   - No sticky sessions needed

2. **Reliability:**
   - Server restart doesn't lose conversations
   - Database transactions ensure consistency
   - Tool failures don't corrupt state

3. **Testability:**
   - Each component isolated
   - MCP tools testable independently
   - Stateless endpoints easy to test

## Implementation Notes

- Use OpenAI SDK (not Agents SDK) - Agents SDK is client-side
- MCP tools exposed as OpenAI function calling definitions
- Conversation history limited to last 20 messages
- Auto-generate conversation titles from first message
