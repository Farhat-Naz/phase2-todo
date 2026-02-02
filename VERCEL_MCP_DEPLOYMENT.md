# Vercel Deployment Guide - MCP Chatbot

## ✅ GitHub Push Successful
Changes pushed to: `008-mcp-chatbot` branch

**Commit:** `a8ff663` - MCP-based chatbot architecture with OpenAI function calling

---

## 🚀 Vercel Deployment Steps

### Step 1: Connect to Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project: **phaseIII-todo**

### Step 2: Configure Environment Variables

Add/Update these environment variables in Vercel:

#### Required for MCP Chatbot:
```bash
OPENAI_API_KEY=your-openai-api-key-here
AI_MODEL=gpt-4o
```

#### Existing Variables (verify these are set):
```bash
DATABASE_URL=your-neon-database-url-here
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=*
BETTER_AUTH_SECRET=your-better-auth-secret-here
BETTER_AUTH_URL=https://your-vercel-app.vercel.app
NEXT_PUBLIC_API_URL=
```

**How to add in Vercel:**
1. Project Settings → Environment Variables
2. Add each variable for **Production**, **Preview**, and **Development**
3. Click "Save"

### Step 3: Deploy from Branch

**Option A: Automatic Deployment (Recommended)**
1. Vercel will automatically detect the push
2. Wait for deployment to complete (~2-3 minutes)
3. Check deployment logs for any errors

**Option B: Manual Deployment**
1. Go to Deployments tab
2. Click "Deploy" next to `008-mcp-chatbot` branch
3. Wait for build to complete

### Step 4: Verify Deployment

1. **Check Backend API:**
   ```bash
   curl https://your-app.vercel.app/api/health
   # Should return: {"status":"healthy","version":"1.0.0"}
   ```

2. **Test Chat Endpoint:**
   - Login to your app
   - Navigate to `/chat` page
   - Send a test message: "Add task: Test MCP"
   - Verify task is created

3. **Check Logs:**
   - Vercel Dashboard → Deployments → View Function Logs
   - Look for: "OpenAI Debug" messages
   - Check for any errors

---

## 📋 Post-Deployment Checklist

- [ ] Environment variables configured correctly
- [ ] Deployment completed without errors
- [ ] Backend health check passes
- [ ] Chat endpoint responding
- [ ] MCP tools executing (add_task, list_tasks, etc.)
- [ ] Tasks saving to database
- [ ] Conversation history persisting

---

## 🐛 Troubleshooting

### Issue: "OPENAI_API_KEY not set"
**Solution:** Add `OPENAI_API_KEY` to Vercel environment variables and redeploy

### Issue: "Module 'mcp' not found"
**Solution:** Verify `requirements.txt` includes `mcp>=1.25.0` and rebuild

### Issue: "Database connection failed"
**Solution:** Check `DATABASE_URL` is set correctly in Vercel environment variables

### Issue: Chat returns "OpenAI package not installed"
**Solution:**
1. Check `requirements.txt` has `openai>=1.58.0`
2. Clear build cache in Vercel
3. Trigger new deployment

### Issue: Function timeout
**Solution:**
1. Increase function timeout in `vercel.json`
2. Check OpenAI response time in logs
3. Consider reducing conversation history limit

---

## 🏗️ Architecture Deployed

### MCP Components:
- ✅ **MCP Tools** - Task management via OpenAI function calling
- ✅ **OpenAI Client** - GPT-4o integration with multi-turn conversations
- ✅ **Stateless Chat** - Database-persisted sessions
- ✅ **Database Models** - ChatSession & ChatMessage tables

### Endpoints Available:
- `POST /api/chat/` - Send chat message with MCP tool support
- `GET /api/todos` - List user's tasks
- `POST /api/todos` - Create task (or via chatbot)

### Features:
- Natural language task management
- Multi-turn conversations with function calling
- Bilingual support (English/Urdu)
- User-scoped data isolation
- Horizontally scalable (stateless)

---

## 📊 Monitoring

### Check Function Logs:
1. Vercel Dashboard → Functions
2. Select `/api/chat` function
3. View real-time logs
4. Look for:
   - `[OpenAI Debug]` messages
   - Tool execution logs
   - Database save confirmations

### Monitor Database:
1. Neon Console → Tables
2. Check `chat_session` table for new sessions
3. Check `chat_message` table for conversation history
4. Check `todo` table for AI-created tasks

---

## 🎯 Testing Guide

### Test 1: Basic Chat
```
Message: "Hello"
Expected: Friendly greeting from AI
```

### Test 2: Add Task
```
Message: "Add task: Buy groceries"
Expected:
- AI calls add_task function
- Task created in database
- Confirmation message
```

### Test 3: List Tasks
```
Message: "Show my tasks"
Expected:
- AI calls list_tasks function
- Returns formatted list of tasks
```

### Test 4: Complete Task
```
Message: "Mark the first task as complete"
Expected:
- AI calls complete_task function
- Task marked as completed
- Confirmation message
```

### Test 5: Multi-turn
```
Message 1: "Add task: Buy milk"
Message 2: "Also add buy bread"
Message 3: "Show all my tasks"
Expected:
- Conversation context maintained
- Both tasks added
- List shows both tasks
```

---

## 🔗 Quick Links

- **GitHub Repo:** https://github.com/Farhat-Naz/phaseIII-todo
- **Branch:** `008-mcp-chatbot`
- **Commit:** `a8ff663`
- **Architecture Docs:** `backend/MCP_ARCHITECTURE.md`

---

## ✨ Next Steps

1. **Merge to Main:**
   ```bash
   git checkout main
   git merge 008-mcp-chatbot
   git push origin main
   ```

2. **Production Deployment:**
   - Vercel will auto-deploy from `main` branch
   - Verify all environment variables
   - Monitor logs for 5-10 minutes

3. **User Testing:**
   - Test with real users
   - Collect feedback on chat experience
   - Monitor OpenAI API usage and costs

---

**Deployment Date:** 2026-01-29
**Version:** 1.0.0
**Status:** ✅ Ready for Deployment
