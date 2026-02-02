# Vercel Deployment Troubleshooting

## Current Status

**Backend**: ✅ WORKING on Render
**Frontend**: 🔄 Deploying on Vercel
**Last Fix**: Removed better-auth dependency and root page redirect

## What Was Fixed (Commit cc86a2e)

### Issue: 500 INTERNAL_SERVER_ERROR
**Error**: `Code: FUNCTION_INVOCATION_FAILED`

### Root Causes:
1. ❌ `better-auth` package trying to initialize on Vercel serverless
2. ❌ Root `app/page.tsx` with `redirect()` causing serverless crashes
3. ❌ Unused environment variables (BETTER_AUTH_*, DATABASE_URL)

### Solutions Applied:
1. ✅ Removed `better-auth` from `package.json`
2. ✅ Deleted root `app/page.tsx`
3. ✅ Updated middleware to handle root redirect
4. ✅ Cleaned `.env.production` (only 2 variables)
5. ✅ Local build tested and successful

## If Still Getting 500 Errors

### Step 1: Check Vercel Build Logs

1. Go to **Vercel Dashboard**: https://vercel.com/dashboard
2. Find your project
3. Click **"Deployments"** tab
4. Click on the latest deployment
5. Click **"Build Logs"**

**Look for:**
- ✅ `Build successful` message
- ❌ Any red error messages
- ⚠️ Any warnings about missing packages

### Step 2: Check Function Logs

If build succeeds but runtime fails:

1. In Vercel Dashboard → Your Project
2. Click **"Functions"** tab
3. Find any function that shows errors
4. Click to view runtime logs

**Common issues:**
- Missing environment variables
- Module not found errors
- Database connection attempts

### Step 3: Verify Environment Variables

In Vercel Dashboard → Your Project → Settings → Environment Variables

**Should ONLY have:**
```
NEXT_PUBLIC_API_URL = https://phaseii-todo-backend.onrender.com
```

**Should NOT have:**
- ❌ BETTER_AUTH_SECRET
- ❌ BETTER_AUTH_URL
- ❌ DATABASE_URL
- ❌ Any cookie configuration variables

**If you see these old variables:**
1. Delete them
2. Redeploy the project

### Step 4: Force Redeploy

If deployment seems stuck or cached:

1. In Vercel Dashboard → Your Project
2. Click **"Deployments"** tab
3. Find the latest deployment
4. Click the three dots (•••)
5. Click **"Redeploy"**
6. Check "Use existing Build Cache" is **UNCHECKED**
7. Click **"Redeploy"**

### Step 5: Check Build Settings

In Vercel Dashboard → Your Project → Settings → General

**Should be:**
- ✅ Framework Preset: **Next.js**
- ✅ Root Directory: **frontend**
- ✅ Build Command: `npm run build` (or default)
- ✅ Output Directory: `.next` (or default)
- ✅ Install Command: `npm install` (or default)
- ✅ Node.js Version: **18.x** or **20.x**

### Step 6: Check Package Installation

Sometimes Vercel needs `package-lock.json`:

If you see "Multiple lockfiles detected" warning:
1. In your frontend directory locally, run:
   ```bash
   cd frontend
   rm pnpm-lock.yaml  # if exists
   npm install
   git add package-lock.json
   git commit -m "Add package-lock.json for Vercel"
   git push
   ```

## Expected Deployment Timeline

- **Now (+0 min)**: Vercel received push
- **+1 min**: Installing dependencies
- **+2 min**: Building Next.js app
- **+3 min**: Deployment complete
- **+3 min**: Test the URL

## Testing After Deployment

### 1. Visit Your Vercel URL

Your app should be at:
- `https://phase-ii-todo.vercel.app` (custom domain)
- OR `https://[project-name]-[hash].vercel.app` (auto-generated)

### 2. Expected Behavior

**Visit root**: `https://your-app.vercel.app/`
- Should redirect to: `https://your-app.vercel.app/en`
- You should see the landing page with:
  - TodoApp header
  - Login/Register buttons
  - Language switcher (EN/UR)
  - Features grid
  - No 500 error ✅

### 3. Test Full Flow

1. Click "Get Started" or "Register"
2. Fill in registration form
3. Submit → Should create account via Render backend
4. Login with credentials
5. Create a todo
6. Mark it complete
7. Delete it
8. Switch to Urdu
9. Test voice command

### 4. Check Browser Console

If page looks broken:
1. Open browser Dev Tools (F12)
2. Check Console tab for errors
3. Check Network tab for failed requests

**Common issues:**
- CORS errors → Backend CORS config
- 404 on API calls → Check `NEXT_PUBLIC_API_URL`
- Failed to load → Check network connection

## Architecture Verification

**Current Setup (Correct):**

```
┌─────────────────────┐
│   Vercel Frontend   │
│   (Next.js 15)      │
│   - JWT auth        │
│   - No DB           │
│   - No Better Auth  │
└──────────┬──────────┘
           │ API calls
           ↓
┌─────────────────────┐
│   Render Backend    │
│   (FastAPI)         │
│   - JWT generation  │
│   - PostgreSQL DB   │
│   - User auth       │
└─────────────────────┘
```

**Frontend Responsibilities:**
- ✅ UI rendering
- ✅ API calls to backend
- ✅ JWT token storage (localStorage)
- ✅ i18n (EN/UR)
- ✅ Voice commands

**Backend Responsibilities:**
- ✅ User authentication
- ✅ JWT token generation
- ✅ Database operations
- ✅ Todo CRUD
- ✅ User data isolation

## Last Resort: Clean Deployment

If nothing works, try a clean deployment:

1. **Delete Vercel project**:
   - Vercel Dashboard → Your Project
   - Settings → General → Delete Project

2. **Remove .vercel directory**:
   ```bash
   cd frontend
   rm -rf .vercel
   git add .vercel
   git commit -m "Remove Vercel config"
   git push
   ```

3. **Create new Vercel project**:
   - Go to Vercel Dashboard
   - Click "Add New" → "Project"
   - Import from GitHub
   - Select repository: `Farhat-Naz/phaseII-todo`
   - Set Root Directory: `frontend`
   - Add environment variable:
     ```
     NEXT_PUBLIC_API_URL=https://phaseii-todo-backend.onrender.com
     ```
   - Deploy

## Get Help

If still failing after all steps:

1. **Check Vercel Status**: https://www.vercel-status.com/
2. **Check Build Logs**: Copy and save full error message
3. **Check Runtime Logs**: Find the specific error in function logs
4. **Share Details**:
   - Deployment URL
   - Error ID (e.g., `dxb1::tn6v8-1768678709083-731fec86a92f`)
   - Build logs (if build failed)
   - Runtime logs (if runtime failed)

## Success Indicators

✅ **Deployment Successful When:**
- Build completes without errors
- No 500 errors on page load
- Root redirects to `/en`
- Landing page renders
- API calls work (check Network tab)
- Login/Register functional

## Debugging Commands

```bash
# Test build locally
cd frontend
npm run build
npm start  # Test production build

# Check for errors
npm run lint

# Clean rebuild
rm -rf .next node_modules
npm install
npm run build
```

---

**Current Status**: Waiting for Vercel deployment to complete (ETA: 2-3 minutes)

**Last Commit**: cc86a2e - Removed better-auth, cleaned environment, middleware redirect

**Backend**: ✅ WORKING at https://phaseii-todo-backend.onrender.com
