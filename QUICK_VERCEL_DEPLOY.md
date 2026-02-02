# ⚡ Quick Vercel Deployment (5 Minutes)

Ultra-fast guide to deploy both frontend and backend on Vercel.

## 🎯 What You'll Create

- **Backend API:** `https://your-backend.vercel.app`
- **Frontend App:** `https://your-app.vercel.app`
- **Database:** Neon PostgreSQL (already setup)

---

## 📋 Prerequisites (2 minutes)

1. ✅ Vercel account: https://vercel.com (free, no credit card)
2. ✅ GitHub repo: `Farhat-Naz/phaseII-todo` (already have)
3. ✅ Neon database connection string (already have):
   ```
   postgresql+psycopg://neondb_owner:npg_ZAGN4xaUk2mh@ep-red-unit-a13i3o3z-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```

---

## 🚀 Step 1: Deploy Backend (5 minutes)

### 1.1 Import Project

1. Visit: https://vercel.com/new
2. Click "Import Git Repository"
3. Select: `Farhat-Naz/phaseII-todo`
4. Click "Import"

### 1.2 Configure

- **Project Name:** `phaseii-todo-api` (or anything)
- **Root Directory:** Click "Edit" → Type `backend` → Click "Continue"
- **Framework:** Other (auto-detect)

### 1.3 Add Environment Variables

Click "Environment Variables" section, add these **one by one**:

| Variable Name | Value |
|---------------|-------|
| `DATABASE_URL` | `postgresql+psycopg://neondb_owner:npg_ZAGN4xaUk2mh@ep-red-unit-a13i3o3z-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require` |
| `SECRET_KEY` | `b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64` |
| `ENV` | `production` |
| `CORS_ORIGINS` | `https://your-frontend.vercel.app` (will update later) |
| `CORS_ALLOW_CREDENTIALS` | `True` |

For each variable:
- Select: ☑️ Production ☑️ Preview ☑️ Development
- Click "Add"

### 1.4 Deploy

1. Click "Deploy" button
2. Wait 2-3 minutes ⏳
3. Success! Copy your backend URL (e.g., `https://phaseii-todo-api.vercel.app`)

### 1.5 Test Backend

Visit: `https://your-backend-url.vercel.app/docs`

Should see FastAPI Swagger docs ✅

---

## 🎨 Step 2: Deploy Frontend (5 minutes)

### 2.1 Import Project (Again)

1. Visit: https://vercel.com/new
2. Click "Import Git Repository"
3. Select: `Farhat-Naz/phaseII-todo` (same repo)
4. Click "Import"

### 2.2 Configure

- **Project Name:** `phaseii-todo-app` (or anything)
- **Root Directory:** Click "Edit" → Type `frontend` → Click "Continue"
- **Framework:** Next.js (auto-detected)

### 2.3 Add Environment Variables

Click "Environment Variables" section, add these:

| Variable Name | Value |
|---------------|-------|
| `NEXT_PUBLIC_API_URL` | `https://your-backend-url.vercel.app` (from Step 1.4) |
| `BETTER_AUTH_SECRET` | `b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64` |
| `BETTER_AUTH_URL` | `https://your-app.vercel.app` (your frontend URL) |
| `NEXT_PUBLIC_COOKIE_DOMAIN` | `.vercel.app` |
| `NEXT_PUBLIC_SECURE_COOKIES` | `true` |
| `NEXT_PUBLIC_APP_NAME` | `TodoApp` |

For each: Select ☑️ Production ☑️ Preview ☑️ Development

### 2.4 Deploy

1. Click "Deploy" button
2. Wait 3-4 minutes ⏳
3. Success! Copy your frontend URL

---

## 🔄 Step 3: Update CORS (2 minutes)

### 3.1 Update Backend CORS

1. Go to Vercel dashboard
2. Select **backend project** (`phaseii-todo-api`)
3. Settings → Environment Variables
4. Find `CORS_ORIGINS`
5. Click "Edit"
6. Change value to: `https://your-frontend-url.vercel.app`
7. Click "Save"

### 3.2 Redeploy Backend

1. Go to "Deployments" tab
2. Click latest deployment → "..." → "Redeploy"
3. Click "Redeploy"

---

## ✅ Step 4: Test Everything (2 minutes)

### Test 1: Backend API
Visit: `https://your-backend.vercel.app/docs`
- ✅ Should see FastAPI docs

### Test 2: Frontend App
Visit: `https://your-frontend.vercel.app`
- ✅ Should see TodoApp homepage
- ✅ Click "Register" → Create account
- ✅ Login with email/password
- ✅ Create a todo item
- ✅ Mark as complete
- ✅ Delete todo

### Test 3: Database
Visit: https://console.neon.tech/
- ✅ Go to "Tables" → Should see data in `user` and `todo` tables

---

## 🎉 Success!

Your app is live:
- **Frontend:** `https://your-frontend.vercel.app`
- **Backend:** `https://your-backend.vercel.app`
- **Database:** Neon PostgreSQL

Share your frontend URL with anyone! 🚀

---

## ⚠️ Troubleshooting

### "Build Failed"
- Check logs in Vercel dashboard
- Verify Root Directory is set correctly
- Ensure all files pushed to GitHub

### "API Connection Failed"
- Check `NEXT_PUBLIC_API_URL` in frontend environment variables
- Verify backend is deployed and working
- Test backend `/docs` endpoint

### "CORS Error"
- Update `CORS_ORIGINS` in backend with correct frontend URL
- Must include `https://` prefix
- No trailing slash
- Redeploy backend after change

### "Database Connection Error"
- Verify `DATABASE_URL` in backend environment variables
- Check Neon database is active
- Ensure using `-pooler` endpoint in URL

---

## 📞 Need Help?

**Detailed Guides:**
- Full deployment: `VERCEL_FULL_DEPLOYMENT.md`
- Neon connection: `NEON_VERCEL_CONNECTION.md`

**Vercel Support:**
- Docs: https://vercel.com/docs
- Dashboard: https://vercel.com/dashboard

---

## 💡 Pro Tips

1. **Auto-Deploy:** Push to GitHub → Vercel auto-deploys both projects
2. **Preview URLs:** Each git branch gets its own preview URL
3. **Logs:** Check deployment logs in Vercel dashboard for errors
4. **Monitoring:** Enable Analytics in Vercel project settings

---

**Total Time:** ~15 minutes
**Cost:** $0 (completely free)

Enjoy your deployed Todo app! 🎊
