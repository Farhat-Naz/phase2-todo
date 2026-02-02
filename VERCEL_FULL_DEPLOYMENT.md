# Complete Vercel Deployment Guide (Frontend + Backend)

Deploy both frontend and backend on Vercel's free tier with Neon PostgreSQL.

## 🏗️ Architecture

```
Frontend (Vercel Project 1) → Backend (Vercel Project 2) → Neon Database
     your-app.vercel.app    →  your-api.vercel.app    →  Neon PostgreSQL
```

**Two separate Vercel projects:** One for frontend, one for backend.

---

## 📋 Prerequisites

- ✅ GitHub account with repository: `Farhat-Naz/phaseII-todo`
- ✅ Vercel account (free): https://vercel.com
- ✅ Neon PostgreSQL database (already configured)

---

## 🚀 Part 1: Deploy Backend API (First)

### Step 1.1: Create New Vercel Project for Backend

1. Go to: https://vercel.com/new
2. Click "Import Project"
3. Select: `Farhat-Naz/phaseII-todo`
4. Click "Import"

### Step 1.2: Configure Backend Project

**Project Settings:**
- **Project Name:** `phaseii-todo-backend` (or any name)
- **Framework Preset:** Other
- **Root Directory:** `backend` ⚠️ **IMPORTANT**
- **Build Command:** (leave empty)
- **Output Directory:** (leave empty)
- **Install Command:** `pip install -r requirements.txt`

### Step 1.3: Add Backend Environment Variables

In Vercel dashboard → Project Settings → Environment Variables:

```bash
# Database Connection (Neon PostgreSQL)
DATABASE_URL=postgresql+psycopg://neondb_owner:npg_ZAGN4xaUk2mh@ep-red-unit-a13i3o3z-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require

# Application Settings
ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=8000

# JWT Authentication
SECRET_KEY=b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Settings (will update after frontend deployment)
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
CORS_ALLOW_CREDENTIALS=True

# Security
CSP_ENABLED=True
HTTPS_REDIRECT=True

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

**How to Add:**
1. Click "Add New" → "Environment Variable"
2. Name: `DATABASE_URL`
3. Value: (paste connection string)
4. Environment: Select **Production**, **Preview**, **Development**
5. Click "Save"
6. Repeat for all variables

### Step 1.4: Deploy Backend

1. Click "Deploy" button
2. Wait 2-3 minutes for deployment
3. Vercel will build and deploy your backend

### Step 1.5: Get Backend URL

After successful deployment:
1. You'll see: **"Congratulations! Your project has been deployed."**
2. Your backend URL will be: `https://phaseii-todo-backend.vercel.app`
3. **Copy this URL** - you'll need it for frontend

### Step 1.6: Test Backend

Visit: `https://phaseii-todo-backend.vercel.app/docs`

You should see FastAPI Swagger documentation.

Test endpoints:
- ✅ `/api/auth/register` - Should accept POST requests
- ✅ `/api/auth/login` - Should accept POST requests
- ✅ `/api/todos` - Should require authentication

---

## 🎨 Part 2: Deploy Frontend (Second)

### Step 2.1: Create New Vercel Project for Frontend

1. Go to: https://vercel.com/new (again)
2. Click "Import Project"
3. Select: `Farhat-Naz/phaseII-todo` (same repo)
4. Click "Import"

### Step 2.2: Configure Frontend Project

**Project Settings:**
- **Project Name:** `phaseii-todo-app` (or any name)
- **Framework Preset:** Next.js (auto-detected)
- **Root Directory:** `frontend` ⚠️ **IMPORTANT**
- **Build Command:** `npm run build` (default)
- **Output Directory:** `.next` (default)
- **Install Command:** `npm install` (default)

### Step 2.3: Add Frontend Environment Variables

In Vercel dashboard → Project Settings → Environment Variables:

```bash
# Backend API URL (from Step 1.5)
NEXT_PUBLIC_API_URL=https://phaseii-todo-backend.vercel.app

# Better Auth Configuration
BETTER_AUTH_SECRET=b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64
BETTER_AUTH_URL=https://phaseii-todo-app.vercel.app

# Cookie Configuration
NEXT_PUBLIC_COOKIE_DOMAIN=.vercel.app
NEXT_PUBLIC_SECURE_COOKIES=true
NEXT_PUBLIC_COOKIE_SAMESITE=lax
NEXT_PUBLIC_COOKIE_PATH=/
NEXT_PUBLIC_ACCESS_TOKEN_COOKIE=access_token
NEXT_PUBLIC_REFRESH_TOKEN_COOKIE=refresh_token

# Application Configuration
NEXT_PUBLIC_APP_NAME=TodoApp
NEXT_PUBLIC_APP_URL=https://phaseii-todo-app.vercel.app
```

**Important:** Replace `phaseii-todo-backend.vercel.app` with your actual backend URL!

### Step 2.4: Deploy Frontend

1. Click "Deploy" button
2. Wait 3-4 minutes for deployment
3. Frontend will build and deploy

### Step 2.5: Get Frontend URL

After successful deployment:
- Your frontend URL: `https://phaseii-todo-app.vercel.app`
- **Save this URL**

---

## 🔄 Part 3: Update CORS Configuration

Now that you have both URLs, update backend CORS:

### Step 3.1: Update Backend Environment Variable

1. Go to backend project: `phaseii-todo-backend`
2. Settings → Environment Variables
3. Find `CORS_ORIGINS`
4. Update value to:
   ```
   https://phaseii-todo-app.vercel.app
   ```
5. Click "Save"

### Step 3.2: Redeploy Backend

1. Go to "Deployments" tab
2. Click on latest deployment
3. Click "..." (three dots)
4. Click "Redeploy"
5. Select "Use existing Build Cache"
6. Click "Redeploy"

---

## ✅ Part 4: Verification & Testing

### Test Backend API:

1. Visit: `https://phaseii-todo-backend.vercel.app/docs`
2. Try `/api/auth/register` endpoint:
   ```json
   {
     "email": "test@example.com",
     "password": "Test123!@#",
     "name": "Test User"
   }
   ```
3. Should return 201 Created

### Test Frontend App:

1. Visit: `https://phaseii-todo-app.vercel.app`
2. Click "Register" or "Sign Up"
3. Create new account
4. Login with credentials
5. Create a todo item
6. Try marking as complete
7. Try deleting a todo

### Test Database Connection:

1. Visit: https://console.neon.tech/
2. Go to your project
3. Click "Tables" tab
4. Should see data in `user` and `todo` tables
5. Check "Monitoring" → Active connections

### Check Browser Console:

1. Open Developer Tools (F12)
2. Go to "Network" tab
3. Should see requests to: `https://phaseii-todo-backend.vercel.app`
4. All requests should return 200/201 (success)
5. No CORS errors

---

## 🔧 Troubleshooting

### Issue: "Backend deployment failed"

**Check Build Logs:**
1. Vercel Dashboard → Deployments → Click failed deployment
2. Check logs for errors

**Common Fixes:**
- Ensure `requirements.txt` includes all dependencies
- Verify `vercel_app.py` exists in backend folder
- Check `vercel.json` is properly configured

### Issue: "Database connection error"

**Fix:**
1. Check `DATABASE_URL` in backend environment variables
2. Verify connection string includes `postgresql+psycopg://`
3. Ensure using `-pooler` endpoint
4. Test connection in Neon console

### Issue: "Frontend build failed"

**Check:**
- All dependencies in `package.json`
- No TypeScript errors
- Environment variables are set

**Fix:**
1. Run `npm run build` locally first
2. Fix any errors
3. Push to GitHub
4. Vercel will auto-redeploy

### Issue: "API connection failed"

**Check:**
1. `NEXT_PUBLIC_API_URL` is set correctly in frontend
2. Backend is deployed and running
3. Visit backend `/docs` to verify it's working

**Fix:**
1. Frontend → Environment Variables
2. Update `NEXT_PUBLIC_API_URL` to correct backend URL
3. Redeploy frontend

### Issue: "CORS error in browser"

**Symptoms:**
```
Access to fetch at 'https://backend.vercel.app' from origin 'https://frontend.vercel.app'
has been blocked by CORS policy
```

**Fix:**
1. Backend → Environment Variables
2. Update `CORS_ORIGINS` to: `https://your-frontend.vercel.app`
3. Redeploy backend
4. Clear browser cache
5. Test again

### Issue: "Authentication not working"

**Check:**
- `BETTER_AUTH_SECRET` same in both frontend and backend `SECRET_KEY`
- Cookies are enabled in browser
- `NEXT_PUBLIC_SECURE_COOKIES=true`

**Fix:**
1. Verify both secrets match
2. Check browser allows cookies
3. Try in incognito mode

---

## 📊 Environment Variables Checklist

### Backend Project:
- [ ] `DATABASE_URL` (Neon connection)
- [ ] `SECRET_KEY` (JWT signing)
- [ ] `CORS_ORIGINS` (Frontend URL)
- [ ] `ENV=production`
- [ ] `DEBUG=False`

### Frontend Project:
- [ ] `NEXT_PUBLIC_API_URL` (Backend URL)
- [ ] `BETTER_AUTH_SECRET` (Auth signing)
- [ ] `BETTER_AUTH_URL` (Frontend URL)
- [ ] `NEXT_PUBLIC_COOKIE_DOMAIN=.vercel.app`
- [ ] `NEXT_PUBLIC_SECURE_COOKIES=true`

---

## 🎯 Project Structure on Vercel

```
Vercel Dashboard
├── phaseii-todo-backend (Backend API)
│   ├── Settings
│   │   ├── Root Directory: backend
│   │   └── Environment Variables (DATABASE_URL, SECRET_KEY, etc.)
│   └── Deployments
│       └── https://phaseii-todo-backend.vercel.app
│
└── phaseii-todo-app (Frontend)
    ├── Settings
    │   ├── Root Directory: frontend
    │   └── Environment Variables (NEXT_PUBLIC_API_URL, etc.)
    └── Deployments
        └── https://phaseii-todo-app.vercel.app
```

---

## 💰 Vercel Free Tier Limits

**Per Project:**
- ✅ 100 GB Bandwidth/month
- ✅ Unlimited requests
- ✅ Automatic HTTPS
- ✅ Automatic deployments on git push

**Total Free Tier:**
- ✅ Multiple projects allowed
- ✅ No credit card required
- ⚠️ Function execution: 100 GB-Hours/month
- ⚠️ Build minutes: 6000 minutes/month

**Your Setup Uses:**
- 2 Vercel projects (both free)
- 1 Neon database (free tier)
- **Total Cost: $0** 🎉

---

## 🚀 Automatic Deployments

Both projects auto-deploy on git push:

1. Make code changes locally
2. Commit: `git add . && git commit -m "Your message"`
3. Push: `git push origin 006-high-priority`
4. Vercel automatically:
   - Detects push
   - Builds both projects
   - Deploys changes
   - Updates URLs

**No manual redeploy needed!**

---

## 🔗 Quick Links

**Your Projects:**
- Backend API: `https://phaseii-todo-backend.vercel.app`
- Frontend App: `https://phaseii-todo-app.vercel.app`
- GitHub Repo: https://github.com/Farhat-Naz/phaseII-todo

**Dashboards:**
- Vercel: https://vercel.com/dashboard
- Neon: https://console.neon.tech/
- GitHub: https://github.com/Farhat-Naz/phaseII-todo

---

## ✨ Success Checklist

After deployment:

- [ ] Backend deployed successfully
- [ ] Backend `/docs` accessible
- [ ] Frontend deployed successfully
- [ ] Frontend loads without errors
- [ ] User registration works
- [ ] User login works
- [ ] Create todo works
- [ ] Mark todo complete works
- [ ] Delete todo works
- [ ] Data appears in Neon console
- [ ] No CORS errors in browser
- [ ] Voice commands work (optional)

---

## 🎓 Next Steps

After successful deployment:

1. **Custom Domain** (Optional):
   - Vercel → Project → Settings → Domains
   - Add your custom domain
   - Update environment variables with new domain

2. **Enable Analytics**:
   - Vercel → Project → Analytics
   - Monitor performance and usage

3. **Set up Monitoring**:
   - Check Vercel logs regularly
   - Monitor Neon database usage
   - Set up error alerts

4. **Share Your App**:
   - Frontend URL: `https://phaseii-todo-app.vercel.app`
   - Share with users!

---

## 📞 Support

**Documentation:**
- Vercel Docs: https://vercel.com/docs
- Next.js Deployment: https://nextjs.org/docs/deployment
- FastAPI on Vercel: https://vercel.com/docs/functions/serverless-functions/runtimes/python
- Neon Docs: https://neon.tech/docs

**Common Issues:**
- Check deployment logs in Vercel dashboard
- Verify environment variables
- Test backend `/docs` endpoint
- Check browser console for errors

---

**Deployment Status:**
- ✅ Configuration files ready
- ⏳ Waiting for Vercel deployment
- ✅ Neon database configured
- ✅ GitHub repository updated

**Estimated Time:** 15-20 minutes for both deployments

Good luck! 🚀
