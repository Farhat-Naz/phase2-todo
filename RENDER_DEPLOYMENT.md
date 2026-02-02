# Render.com Backend Deployment Guide

## Quick Deploy (5 minutes)

### Step 1: Create Render Account
1. Go to https://render.com/
2. Sign up with GitHub (recommended) or email
3. Verify your email if prompted

### Step 2: Deploy Backend
1. Click "New +" button in Render dashboard
2. Select "Web Service"
3. Connect your GitHub repository: `Farhat-Naz/phaseII-todo`
4. Select branch: `006-high-priority`
5. Render will auto-detect `render.yaml` configuration

### Step 3: Configure Environment Variables

**⚠️ CRITICAL: DATABASE_URL Format**

When pasting `DATABASE_URL`, do **NOT** include quotes. Paste the raw URL only.

✅ **CORRECT** (no quotes):
```
postgresql+psycopg://neondb_owner:npg_ZAGN4xaUk2mh@ep-red-unit-a13i3o3z-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
```

❌ **WRONG** (has quotes - will fail):
```
'postgresql+psycopg://...'
"postgresql+psycopg://..."
'psql'postgresql://...
```

Render will prompt you to add these required environment variables:

```
DATABASE_URL = postgresql+psycopg://neondb_owner:npg_ZAGN4xaUk2mh@ep-red-unit-a13i3o3z-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require

SECRET_KEY = b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64

ALGORITHM = HS256

ACCESS_TOKEN_EXPIRE_MINUTES = 30

REFRESH_TOKEN_EXPIRE_DAYS = 7

CORS_ORIGINS = https://phase-ii-todo.vercel.app

ENV = production

DEBUG = False
```

### Step 4: Deploy
1. Click "Create Web Service"
2. Wait 3-5 minutes for deployment (watch the logs)
3. Once deployed, you'll get a URL like: `https://phaseii-todo-backend.onrender.com`

### Step 5: Test Backend
```bash
# Health check
curl https://your-app-name.onrender.com/health

# Expected response:
{"status": "ok", "message": "Todo API is running"}
```

### Step 6: Update Frontend
After backend is deployed, update frontend environment variable:

1. Go to Vercel Dashboard: https://vercel.com/farhats-projects-27800a4d/phase-ii-todo
2. Go to Settings → Environment Variables
3. Add or update:
   ```
   NEXT_PUBLIC_API_URL = https://your-app-name.onrender.com
   ```
4. Redeploy frontend: `vercel --prod` or use Vercel dashboard

### Step 7: Test Full Application
1. Visit: https://phase-ii-todo.vercel.app
2. Register a new user
3. Login
4. Create a todo
5. Verify data is saved in Neon database

## Troubleshooting

### Build Fails
- Check Render build logs for specific errors
- Ensure `requirements.txt` has all dependencies
- Verify Python version in `runtime.txt` (3.11.0)

### Database Connection Error

**Error:** `Could not parse SQLAlchemy URL from string 'psql'postgresql://...'`

**Cause:** DATABASE_URL has quotes or typos in Render environment variables

**Solution:**
1. Go to Render Dashboard → Environment tab
2. Find `DATABASE_URL` variable
3. Click "Edit" and remove ALL quotes (`'` or `"`)
4. Ensure it starts with `postgresql+psycopg://` (not `'psql'` or `psql`)
5. Save changes
6. Trigger manual deploy or wait for auto-deploy

**Other checks:**
- Verify `DATABASE_URL` is correctly set without quotes
- Ensure Neon database is active (not paused)
- Check database connection string includes `?sslmode=require`

### CORS Errors
- Verify `CORS_ORIGINS` includes your Vercel frontend URL
- Add `https://phase-ii-todo.vercel.app` to CORS_ORIGINS

### 502 Bad Gateway
- Check if app is starting correctly in logs
- Verify `Procfile` command is correct
- Ensure `$PORT` environment variable is used

## Free Tier Limitations

Render free tier:
- App sleeps after 15 min of inactivity
- First request after sleep takes ~30 seconds (cold start)
- 750 hours/month free (enough for 24/7 with one app)

To keep app awake (optional):
- Use a service like UptimeRobot to ping `/health` every 14 minutes

## Alternative: Railway Deployment

If you prefer Railway:
1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Initialize: `cd backend && railway init`
4. Deploy: `railway up`
5. Set environment variables in Railway dashboard
6. Get deployment URL from Railway dashboard

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com/
- GitHub Issues: https://github.com/Farhat-Naz/phaseII-todo/issues
