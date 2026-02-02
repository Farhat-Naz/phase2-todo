# How to Connect Vercel to Neon Database

Complete guide explaining the connection between Vercel, your backend, and Neon PostgreSQL.

## 🏗️ Architecture Overview

```
┌─────────┐      ┌──────────┐      ┌─────────┐
│ Browser │ ───> │ Frontend │ ───> │ Backend │ ───> ┌──────────┐
│  User   │ <─── │ (Vercel) │ <─── │(Railway)│ <─── │   Neon   │
└─────────┘      └──────────┘      └─────────┘      │PostgreSQL│
                                                      └──────────┘
```

**Key Point:** Frontend does NOT directly connect to database!

---

## 🔌 Connection Flow

### 1. **Frontend (Next.js on Vercel)**
   - Runs in user's browser
   - Makes HTTP requests to backend API
   - **No direct database connection**
   - Only needs: Backend API URL

### 2. **Backend (FastAPI on Railway/Render)**
   - Receives requests from frontend
   - Connects to Neon PostgreSQL
   - Executes database queries
   - Returns data to frontend

### 3. **Database (Neon PostgreSQL)**
   - Stores all data (users, todos)
   - Accepts connections from backend only
   - Connection string needed by backend

---

## 🎯 What You Need to Configure

### **For Frontend Deployment (Vercel):**

**You DO NOT need Neon connection string!**

Only add these environment variables:

```bash
# Backend API URL (update after backend deployment)
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Authentication
BETTER_AUTH_SECRET=b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64
BETTER_AUTH_URL=https://your-app.vercel.app

# Cookie Configuration
NEXT_PUBLIC_COOKIE_DOMAIN=.vercel.app
NEXT_PUBLIC_SECURE_COOKIES=true
NEXT_PUBLIC_COOKIE_SAMESITE=lax
NEXT_PUBLIC_APP_NAME=TodoApp
```

### **For Backend Deployment (Railway/Render):**

**This is where you add Neon connection string!**

```bash
# 🔥 MOST IMPORTANT: Database Connection
DATABASE_URL=postgresql+psycopg://neondb_owner:npg_ZAGN4xaUk2mh@ep-red-unit-a13i3o3z-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require

# Other backend configuration
SECRET_KEY=b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64
CORS_ORIGINS=https://your-frontend.vercel.app
# ... (see RAILWAY_DEPLOYMENT.md for full list)
```

---

## 📋 Step-by-Step Deployment Order

### **Step 1: Deploy Backend First**

**Why first?** Because frontend needs backend URL!

1. Go to https://railway.app/
2. Deploy from GitHub: `Farhat-Naz/phaseII-todo`
3. Set Root Directory: `backend`
4. Add environment variables (including `DATABASE_URL`)
5. Deploy
6. **Copy your backend URL:** `https://your-app.railway.app`

### **Step 2: Deploy Frontend**

1. Go to https://vercel.com/new
2. Import: `Farhat-Naz/phaseII-todo`
3. Set Root Directory: `frontend`
4. Add environment variables
5. **Set `NEXT_PUBLIC_API_URL` to your backend URL from Step 1**
6. Deploy

### **Step 3: Update CORS**

1. Go back to Railway backend
2. Update `CORS_ORIGINS` environment variable
3. Set to your Vercel frontend URL
4. Railway will auto-redeploy

---

## 🔐 Security: Why This Architecture?

### **Frontend on Vercel (Public):**
- Code runs in user's browser
- Anyone can inspect code
- **NEVER store database credentials here!**
- Only stores backend API URL (public anyway)

### **Backend on Railway (Private):**
- Code runs on server
- Users cannot see code
- **Database credentials stored here safely**
- Environment variables are encrypted

### **Database on Neon:**
- Only accepts connections from backend server
- Connection requires: hostname, username, password
- SSL encryption enabled (`sslmode=require`)

---

## 🧪 Testing the Connection

### **Test 1: Backend → Neon**

Visit your backend URL:
```
https://your-backend.railway.app/docs
```

Check logs for:
```
✅ Database connection test successful
✅ Database tables created successfully
```

### **Test 2: Frontend → Backend**

Visit your frontend URL:
```
https://your-app.vercel.app
```

1. Register a new user
2. Check browser Network tab
3. Should see requests to: `https://your-backend.railway.app/api/auth/register`

### **Test 3: Check Neon Console**

Visit: https://console.neon.tech/

1. Go to your project
2. Click "Tables" tab
3. Should see: `user`, `todo`, `session` tables
4. Check "Monitoring" → Active connections from Railway

---

## ❌ Common Mistakes

### **Mistake 1: Adding DATABASE_URL to Frontend**
```bash
# ❌ WRONG - Never add to Vercel frontend!
DATABASE_URL=postgresql://...

# ✅ CORRECT - Only backend API URL
NEXT_PUBLIC_API_URL=https://backend.railway.app
```

### **Mistake 2: Wrong Connection String Format**
```bash
# ❌ WRONG - Missing psycopg driver
DATABASE_URL=postgresql://user:pass@host/db

# ✅ CORRECT - With psycopg driver
DATABASE_URL=postgresql+psycopg://user:pass@host/db
```

### **Mistake 3: Not Using Pooler**
```bash
# ❌ WRONG - Direct endpoint (limited connections)
@ep-red-unit-a13i3o3z.ap-southeast-1.aws.neon.tech

# ✅ CORRECT - Pooler endpoint (unlimited)
@ep-red-unit-a13i3o3z-pooler.ap-southeast-1.aws.neon.tech
```

---

## 🎓 Understanding Environment Variables

### **Frontend (Vercel):**
```bash
# NEXT_PUBLIC_* variables are exposed to browser
NEXT_PUBLIC_API_URL=https://backend.railway.app  # ✅ Safe (public)

# Non-NEXT_PUBLIC variables are server-side only
BETTER_AUTH_SECRET=abc123...  # ✅ Safe (server-only)
```

### **Backend (Railway):**
```bash
# All backend env vars are private
DATABASE_URL=postgresql+psycopg://...  # ✅ Safe (never exposed)
SECRET_KEY=b105763e...  # ✅ Safe (server-only)
```

---

## 📊 Environment Variables Summary

| Variable | Where to Add | Purpose |
|----------|-------------|---------|
| `DATABASE_URL` | **Backend** (Railway) | Connect backend to Neon |
| `NEXT_PUBLIC_API_URL` | **Frontend** (Vercel) | Connect frontend to backend |
| `SECRET_KEY` | **Backend** (Railway) | JWT token signing |
| `BETTER_AUTH_SECRET` | **Frontend** (Vercel) | Auth cookie signing |
| `CORS_ORIGINS` | **Backend** (Railway) | Allow frontend to call backend |

---

## ✅ Verification Checklist

After deployment:

- [ ] Backend deployed on Railway
- [ ] Backend logs show: "Database connection successful"
- [ ] Backend API docs accessible: `/docs`
- [ ] Frontend deployed on Vercel
- [ ] Frontend can register users
- [ ] Frontend can create todos
- [ ] Neon console shows tables and data
- [ ] No CORS errors in browser console

---

## 🆘 Troubleshooting

### "Cannot connect to database"
- ✅ Check `DATABASE_URL` is set in **backend** environment variables
- ✅ Verify connection string includes `postgresql+psycopg://`
- ✅ Ensure using `-pooler` endpoint

### "API connection failed"
- ✅ Check `NEXT_PUBLIC_API_URL` in **frontend** environment variables
- ✅ Verify backend is deployed and running
- ✅ Test backend directly: `https://backend.railway.app/docs`

### "CORS error"
- ✅ Update `CORS_ORIGINS` in **backend** with frontend URL
- ✅ Include full URL: `https://your-app.vercel.app`
- ✅ No trailing slash

---

## 🔗 Quick Links

- **Neon Console:** https://console.neon.tech/
- **Railway Dashboard:** https://railway.app/dashboard
- **Vercel Dashboard:** https://vercel.com/dashboard
- **Your Repository:** https://github.com/Farhat-Naz/phaseII-todo

---

## 💡 Key Takeaway

**Frontend (Vercel) ↔️ Backend (Railway) ↔️ Database (Neon)**

- Frontend talks to Backend (needs Backend URL)
- Backend talks to Database (needs Database URL)
- Frontend NEVER talks directly to Database!

This is the standard "3-tier architecture" for web applications.
