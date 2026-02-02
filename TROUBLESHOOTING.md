# Troubleshooting Guide - phaseII-todo

## Quick Fixes

### ❌ "Not Found" Error During Registration

**Symptom:** Registration fails with "not found" or timeout error

**Root Cause:** Backend server is not running or unreachable

**Solutions:**

#### Option 1: Run Locally (Fastest)
```bash
# Windows
start-dev.bat

# Mac/Linux
chmod +x start-dev.sh
./start-dev.sh
```

#### Option 2: Manual Start
```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

#### Option 3: Wake Up Render Backend
```bash
# Test if backend is awake (30 sec timeout for cold start)
curl https://phaseii-todo-backend.onrender.com/health

# If timeout: Go to Render dashboard and trigger manual deploy
```

---

### ❌ Database Connection Errors

**Symptom:** `Could not parse SQLAlchemy URL` or `psql'postgresql://...`

**Root Cause:** DATABASE_URL has quotes or typos in environment variable

**Solution:**
1. Check `backend/.env` file
2. Ensure DATABASE_URL has NO quotes:
   ```
   # ✅ CORRECT
   DATABASE_URL=postgresql+psycopg://user:pass@host/db

   # ❌ WRONG
   DATABASE_URL="postgresql+psycopg://user:pass@host/db"
   DATABASE_URL='postgresql+psycopg://user:pass@host/db'
   ```
3. For Render: Edit env var and remove quotes, then redeploy

---

### ❌ CORS Errors (Cross-Origin Request Blocked)

**Symptom:** Frontend can't connect to backend, browser console shows CORS error

**Root Cause:** Frontend origin not allowed by backend CORS policy

**Solution:**

1. **Local Development:**
   ```bash
   # backend/.env
   CORS_ORIGINS=http://localhost:3000,http://localhost:3001
   ```

2. **Production (Render):**
   - Add your Vercel URL to `CORS_ORIGINS` env var:
   ```
   CORS_ORIGINS=https://phase-ii-todo.vercel.app
   ```

3. **Already Fixed in Code:**
   - Check `backend/app/main.py:102-108`
   - Temporarily allows all origins for debugging
   - Remove `allow_origins=["*"]` in production

---

### ❌ Frontend Shows Old API URL

**Symptom:** Frontend still tries to connect to wrong backend URL

**Root Cause:** Environment variable not loaded or cached

**Solution:**
```bash
# 1. Stop frontend server (Ctrl+C)

# 2. Check .env.local file
cd frontend
cat .env.local  # Should show NEXT_PUBLIC_API_URL=http://localhost:8000

# 3. Clear Next.js cache
rm -rf .next

# 4. Restart
npm run dev
```

---

### ❌ "Invalid Token" or 401 Unauthorized

**Symptom:** Registration works but login fails, or authenticated requests fail

**Root Causes:**
1. JWT secret mismatch between frontend/backend
2. Token expired
3. Token storage issue

**Solutions:**

1. **Check JWT Secret Match:**
   ```bash
   # backend/.env
   SECRET_KEY=b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64

   # frontend/.env.local (if using Better Auth)
   BETTER_AUTH_SECRET=b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64
   ```

2. **Clear Tokens:**
   - Open browser DevTools → Application → Local Storage
   - Delete `access_token` key
   - Retry login

3. **Check Token Expiry:**
   - Default: 30 minutes (ACCESS_TOKEN_EXPIRE_MINUTES=30)
   - Login again if expired

---

### ❌ Render Backend Sleeps/Slow Cold Start

**Symptom:** First request takes 20-30 seconds, subsequent requests are fast

**Root Cause:** Render free tier sleeps after 15 min of inactivity

**Solutions:**

1. **Accept Cold Start (Simplest):**
   - Just wait 20-30 seconds on first request
   - Subsequent requests will be instant

2. **Keep Alive Service (UptimeRobot):**
   - Create free UptimeRobot account
   - Add monitor: https://phaseii-todo-backend.onrender.com/health
   - Set interval: 14 minutes
   - Backend stays awake 24/7

3. **Upgrade to Paid Plan:**
   - Render paid plans ($7/mo+) don't sleep
   - Instant response time always

---

### ❌ Database Migration Issues

**Symptom:** `relation "users" does not exist` or `column not found`

**Root Cause:** Database schema not created or out of sync

**Solution:**
```bash
cd backend

# Check database connection
python -c "from app.database import test_connection; test_connection()"

# Create/update tables
python -c "from app.database import create_db_and_tables; create_db_and_tables()"

# Or restart backend (tables auto-create on startup)
uvicorn app.main:app --reload
```

---

### ❌ Voice Input Not Working

**Symptom:** Microphone button doesn't work or voice commands not recognized

**Root Causes:**
1. Browser doesn't support Web Speech API (use Chrome/Edge)
2. Microphone permission denied
3. HTTPS required (localhost works with HTTP)

**Solutions:**

1. **Check Browser Support:**
   - ✅ Chrome/Edge (best support)
   - ✅ Safari (limited)
   - ❌ Firefox (no support yet)

2. **Grant Microphone Permission:**
   - Browser should prompt for permission
   - Check: Settings → Privacy → Microphone
   - Allow your site to use microphone

3. **HTTPS Requirement:**
   - Localhost works with HTTP
   - Production requires HTTPS (Vercel provides this)

---

## Environment Variables Checklist

### Backend (.env)
```env
DATABASE_URL=postgresql+psycopg://...  # NO quotes!
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000
ENV=development
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=TodoApp
```

### Production (Render Environment Variables)
```env
DATABASE_URL=postgresql+psycopg://...  # From Neon, no quotes
SECRET_KEY=b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=https://phase-ii-todo.vercel.app
ENV=production
DEBUG=False
```

### Production (Vercel Environment Variables)
```env
NEXT_PUBLIC_API_URL=https://phaseii-todo-backend.onrender.com
NEXT_PUBLIC_APP_NAME=TodoApp
```

---

## Testing Checklist

### Backend Health
```bash
# Local
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# Production
curl https://phaseii-todo-backend.onrender.com/health
# Expected: {"status":"ok"} (may take 20-30s first time)
```

### API Endpoints
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"

# Get Todos (requires token)
curl http://localhost:8000/api/todos \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Database
```bash
cd backend
python -c "from app.database import test_connection; test_connection()"
# Expected: "Database connection successful!"
```

---

## Logs and Debugging

### Backend Logs
```bash
# Local (in terminal running uvicorn)
# Watch for errors during requests

# Render (dashboard)
1. Go to https://dashboard.render.com/
2. Click your service → Logs tab
3. Watch real-time logs
```

### Frontend Logs
```bash
# Browser Console (F12 → Console tab)
# Check for API errors, CORS issues, etc.

# Next.js Terminal
# Shows build errors, API route errors
```

### Enable Detailed Logging
```bash
# backend/.env
LOG_LEVEL=DEBUG  # Change from INFO to DEBUG
DEBUG=True

# Restart backend to see detailed SQL queries, request/response logs
```

---

## Getting Help

1. **Check Logs First:**
   - Backend terminal output
   - Browser console (F12)
   - Render dashboard logs

2. **Common Error Patterns:**
   - "not found" → Backend not running
   - "CORS" → Origin not allowed
   - "401" → Token expired/invalid
   - "database" → Connection string issue

3. **Quick Reset:**
   ```bash
   # Stop all servers
   # Clear caches
   rm -rf frontend/.next backend/__pycache__
   # Restart from scripts
   ```

4. **Still Stuck?**
   - Check this file first: `TROUBLESHOOTING.md`
   - Review: `RENDER_DEPLOYMENT.md` for production issues
   - Review: `.env.local.example` for env var templates
   - GitHub Issues: https://github.com/Farhat-Naz/phaseII-todo/issues
