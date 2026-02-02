# Railway Backend Deployment Guide

Deploy FastAPI backend to Railway and connect to Neon PostgreSQL.

## Step 1: Create Railway Account

1. Visit: https://railway.app/
2. Click "Login with GitHub"
3. Authorize Railway to access your GitHub account

## Step 2: Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose repository: `Farhat-Naz/phaseII-todo`
4. Railway will scan and detect it's a Python project

## Step 3: Configure Service

### Set Root Directory:
1. Click on the service
2. Go to "Settings" tab
3. Scroll to "Root Directory"
4. Set to: `backend`
5. Save changes

### Set Start Command:
1. Still in "Settings" tab
2. Find "Start Command"
3. Set to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Save

## Step 4: Add Environment Variables

1. Click "Variables" tab
2. Click "Raw Editor"
3. Paste all these variables:

```bash
DATABASE_URL=postgresql+psycopg://neondb_owner:npg_ZAGN4xaUk2mh@ep-red-unit-a13i3o3z-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=8000
SECRET_KEY=b105763e0336368cc580d447338bbbc78f38c3faa24451d561398ca0983e9b64
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
CORS_ALLOW_CREDENTIALS=True
CSP_ENABLED=True
HTTPS_REDIRECT=True
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_PER_MINUTE=60
```

4. Click "Update Variables"

## Step 5: Deploy

1. Railway will automatically start deployment
2. Wait 2-3 minutes for build to complete
3. Check "Deployments" tab for status

## Step 6: Get Your Backend URL

1. Go to "Settings" tab
2. Click "Generate Domain" under "Domains"
3. Your backend URL will be: `https://your-app.up.railway.app`
4. Copy this URL - you'll need it for frontend

## Step 7: Test Backend

1. Visit: `https://your-app.up.railway.app/docs`
2. You should see FastAPI Swagger documentation
3. Test the `/api/auth/register` endpoint

## Step 8: Update CORS for Production

1. Go back to "Variables" tab
2. Update `CORS_ORIGINS` with your actual frontend URL:
   ```
   CORS_ORIGINS=https://your-frontend.vercel.app
   ```
3. Railway will automatically redeploy

## Verify Database Connection

### Check Logs:
1. Click "Deployments" tab
2. Click latest deployment
3. View logs
4. Look for: "Database connection test successful"

### Check Neon Console:
1. Visit: https://console.neon.tech/
2. Go to your project
3. Click "Monitoring" → "Operations"
4. You should see active connections from Railway

## Troubleshooting

### Build Failed:
- Check "Deploy Logs" for errors
- Verify `requirements.txt` is correct
- Ensure Python 3.13+ is supported

### Database Connection Error:
- Verify `DATABASE_URL` is correct
- Check Neon database is active
- Ensure you're using pooler endpoint (has `-pooler` in URL)

### CORS Errors:
- Update `CORS_ORIGINS` with correct frontend URL
- Must include protocol: `https://`
- No trailing slash

## Cost

**Railway Pricing:**
- Free tier: $5 credit/month (enough for small projects)
- Usage-based: ~$5-10/month for basic API
- Database: Uses external Neon (free separately)

## Next Steps

After backend is deployed:
1. Copy your Railway backend URL
2. Update frontend `NEXT_PUBLIC_API_URL` on Vercel
3. Redeploy frontend
4. Test end-to-end

---

**Your Backend URL:** `https://your-app.up.railway.app`

Save this URL - you'll need it for frontend deployment!
