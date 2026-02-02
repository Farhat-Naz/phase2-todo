# Complete Environment Variables Guide

All environment variables (client keys/values) needed for Vercel deployment.

---

## 🔧 Backend Project Environment Variables

Copy these to: **Vercel Dashboard → Backend Project → Settings → Environment Variables**

### Required Variables:

```bash
# 1. Database Connection (from Neon Console)
DATABASE_URL=postgresql+psycopg://neondb_owner:npg_ZAGN4xaUk2mh@ep-red-unit-a13i3o3z-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require

# 2. JWT Secret Key (keep this secure!)
SECRET_KEY=b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64

# 3. Environment Type
ENV=production

# 4. Debug Mode (False for production)
DEBUG=False

# 5. Server Host
HOST=0.0.0.0

# 6. Server Port
PORT=8000

# 7. JWT Algorithm
ALGORITHM=HS256

# 8. Token Expiration Times
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# 9. CORS Configuration (update with your frontend URL after deployment)
CORS_ORIGINS=https://your-frontend-app.vercel.app
CORS_ALLOW_CREDENTIALS=True

# 10. Security Settings
CSP_ENABLED=True
HTTPS_REDIRECT=True

# 11. Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# 12. Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### How to Add in Vercel:

1. Go to: https://vercel.com/dashboard
2. Select your **backend project**
3. Click: **Settings** → **Environment Variables**
4. For each variable above:
   - Click "Add New"
   - **Key:** Enter the variable name (e.g., `DATABASE_URL`)
   - **Value:** Enter the value
   - **Environments:** Check all three: ☑️ Production ☑️ Preview ☑️ Development
   - Click "Save"

---

## 🎨 Frontend Project Environment Variables

Copy these to: **Vercel Dashboard → Frontend Project → Settings → Environment Variables**

### Required Variables:

```bash
# 1. Backend API URL (get this after backend deployment)
NEXT_PUBLIC_API_URL=https://your-backend-project.vercel.app

# 2. Better Auth Secret (same as backend SECRET_KEY)
BETTER_AUTH_SECRET=b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64

# 3. Better Auth URL (your frontend URL)
BETTER_AUTH_URL=https://your-frontend-app.vercel.app

# 4. Cookie Domain for Vercel
NEXT_PUBLIC_COOKIE_DOMAIN=.vercel.app

# 5. Secure Cookies (HTTPS only)
NEXT_PUBLIC_SECURE_COOKIES=true

# 6. Cookie SameSite Policy
NEXT_PUBLIC_COOKIE_SAMESITE=lax

# 7. Cookie Path
NEXT_PUBLIC_COOKIE_PATH=/

# 8. Cookie Names
NEXT_PUBLIC_ACCESS_TOKEN_COOKIE=access_token
NEXT_PUBLIC_REFRESH_TOKEN_COOKIE=refresh_token

# 9. Application Name
NEXT_PUBLIC_APP_NAME=TodoApp

# 10. Application URL (your frontend URL)
NEXT_PUBLIC_APP_URL=https://your-frontend-app.vercel.app
```

### How to Add in Vercel:

1. Go to: https://vercel.com/dashboard
2. Select your **frontend project**
3. Click: **Settings** → **Environment Variables**
4. For each variable above:
   - Click "Add New"
   - **Key:** Enter the variable name (e.g., `NEXT_PUBLIC_API_URL`)
   - **Value:** Enter the value
   - **Environments:** Check all three: ☑️ Production ☑️ Preview ☑️ Development
   - Click "Save"

---

## 🔍 Where to Find Each Value:

### DATABASE_URL
**Source:** Neon Console
**Steps:**
1. Visit: https://console.neon.tech/
2. Login to your account
3. Select your project: `phaseII-todo` or similar
4. Click "Dashboard"
5. Section: "Connection Details"
6. Copy "Connection string"
7. **Important:** Replace `postgresql://` with `postgresql+psycopg://`
8. Example:
   ```
   Original: postgresql://user:pass@host/db
   Modified: postgresql+psycopg://user:pass@host/db
   ```

### SECRET_KEY
**Already Generated:** `b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64`

**To Generate New:**
```bash
# Method 1: PowerShell (Windows)
-join ((48..57) + (97..102) | Get-Random -Count 64 | % {[char]$_})

# Method 2: OpenSSL (Linux/Mac)
openssl rand -hex 32

# Method 3: Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### NEXT_PUBLIC_API_URL
**Source:** Vercel Backend Project
**Steps:**
1. Deploy backend first
2. Go to Vercel dashboard
3. Select backend project
4. You'll see the URL at top: `https://project-name.vercel.app`
5. Copy entire URL including `https://`

### BETTER_AUTH_URL & NEXT_PUBLIC_APP_URL
**Source:** Vercel Frontend Project
**Steps:**
1. Deploy frontend first
2. Go to Vercel dashboard
3. Select frontend project
4. You'll see the URL at top: `https://project-name.vercel.app`
5. Copy entire URL including `https://`

### CORS_ORIGINS
**Value:** Frontend URL (same as BETTER_AUTH_URL)
**Example:** `https://your-frontend-app.vercel.app`
**Note:** Update backend environment variable after frontend deployment

---

## 📋 Deployment Order:

### Step 1: Deploy Backend
1. Add all backend environment variables (use `http://localhost:3000` for CORS_ORIGINS temporarily)
2. Deploy backend
3. **Copy backend URL**

### Step 2: Deploy Frontend
1. Add all frontend environment variables
2. Use backend URL from Step 1 in `NEXT_PUBLIC_API_URL`
3. Use `https://your-app.vercel.app` for `BETTER_AUTH_URL` (or localhost initially)
4. Deploy frontend
5. **Copy frontend URL**

### Step 3: Update Backend CORS
1. Go back to backend project
2. Settings → Environment Variables
3. Update `CORS_ORIGINS` with frontend URL from Step 2
4. Deployments → Latest → "..." → Redeploy

---

## ✅ Quick Copy-Paste Values:

### Backend (Complete Set):
```
DATABASE_URL=postgresql+psycopg://neondb_owner:npg_ZAGN4xaUk2mh@ep-red-unit-a13i3o3z-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64
ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=8000
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000
CORS_ALLOW_CREDENTIALS=True
CSP_ENABLED=True
HTTPS_REDIRECT=True
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_PER_MINUTE=60
```

### Frontend (Complete Set):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_COOKIE_DOMAIN=.vercel.app
NEXT_PUBLIC_SECURE_COOKIES=true
NEXT_PUBLIC_COOKIE_SAMESITE=lax
NEXT_PUBLIC_COOKIE_PATH=/
NEXT_PUBLIC_ACCESS_TOKEN_COOKIE=access_token
NEXT_PUBLIC_REFRESH_TOKEN_COOKIE=refresh_token
NEXT_PUBLIC_APP_NAME=TodoApp
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Note:** Update URLs after deployment!

---

## 🔐 Security Best Practices:

### ✅ DO:
- Keep `SECRET_KEY` and `BETTER_AUTH_SECRET` secret
- Use HTTPS in production (`https://`)
- Set `NEXT_PUBLIC_SECURE_COOKIES=true` in production
- Update `CORS_ORIGINS` to exact frontend URL
- Use strong random secrets (64 characters hex)

### ❌ DON'T:
- Share secrets publicly
- Commit `.env` files to git
- Use weak/predictable secrets
- Allow all CORS origins (`*`) in production
- Use `DEBUG=True` in production

---

## 🐛 Troubleshooting:

### "Database connection failed"
**Check:**
- `DATABASE_URL` is correct and includes `postgresql+psycopg://`
- Neon database is active
- Using pooler endpoint (has `-pooler` in URL)

### "CORS error"
**Check:**
- `CORS_ORIGINS` matches exact frontend URL
- Includes `https://` prefix
- No trailing slash
- Backend redeployed after updating

### "Authentication not working"
**Check:**
- `SECRET_KEY` and `BETTER_AUTH_SECRET` are identical
- Both are at least 32 characters
- Cookies enabled in browser

### "API connection failed"
**Check:**
- `NEXT_PUBLIC_API_URL` is correct backend URL
- Backend is deployed and running
- Test backend at `/docs` endpoint

---

## 📞 Support Resources:

- **Vercel Docs:** https://vercel.com/docs/concepts/projects/environment-variables
- **Neon Docs:** https://neon.tech/docs/connect/connect-from-any-app
- **Our Deployment Guide:** `VERCEL_FULL_DEPLOYMENT.md`
- **Quick Guide:** `QUICK_VERCEL_DEPLOY.md`

---

## ✨ Summary:

**Total Variables Needed:**
- **Backend:** 15 environment variables
- **Frontend:** 11 environment variables

**Already Have:**
- ✅ Database connection string (Neon)
- ✅ Secret keys (generated)
- ✅ Configuration values (documented)

**Need After Deployment:**
- ⏳ Backend URL (from Vercel)
- ⏳ Frontend URL (from Vercel)

**Action Required:**
1. Add backend variables → Deploy → Get backend URL
2. Add frontend variables (with backend URL) → Deploy → Get frontend URL
3. Update backend CORS with frontend URL → Redeploy

---

**Everything you need is in this file!** 🚀
