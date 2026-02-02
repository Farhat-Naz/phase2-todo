# Vercel Environment Variable Setup

## Problem
Authentication (registration, sign in, sign out) is failing on Vercel with "an unexpected error occurred" because the frontend cannot connect to the backend.

## Root Cause
The environment variable `NEXT_PUBLIC_API_URL` is not set in Vercel's dashboard. Without it, the frontend tries to connect to `http://localhost:8000` which doesn't exist on Vercel's servers.

## Solution: Add Environment Variable to Vercel

### Step 1: Go to Vercel Dashboard
1. Open: https://vercel.com/farhats-projects-27800a4d/frontend
2. Click on **"Settings"** tab at the top

### Step 2: Navigate to Environment Variables
1. In the left sidebar, click **"Environment Variables"**

### Step 3: Add Backend URL Variable
1. Click **"Add New"** button
2. Fill in the form:
   - **Key (Name)**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://phaseii-todo-backend.onrender.com`
   - **Environments**: Check all three boxes:
     - ☑ Production
     - ☑ Preview
     - ☑ Development

3. Click **"Save"** button

### Step 4: Redeploy
After saving the environment variable, you MUST redeploy for changes to take effect:

**Option A: Redeploy from Vercel Dashboard**
1. Go to **"Deployments"** tab
2. Click the **three dots (⋮)** on the latest deployment
3. Click **"Redeploy"**
4. Confirm by clicking **"Redeploy"** again

**Option B: Redeploy by Pushing to Git**
```bash
git commit --allow-empty -m "Trigger Vercel redeploy"
git push origin 006-high-priority
```

### Step 5: Test Authentication
After redeployment completes (2-3 minutes):
1. Visit your Vercel URL: https://frontend-agfhuva1e-farhats-projects-27800a4d.vercel.app
2. Try registering a new account
3. Try signing in
4. Try signing out

All authentication should now work correctly!

## Verification
The backend is confirmed healthy:
```bash
curl https://phaseii-todo-backend.onrender.com/health
# Returns: {"status":"ok"}
```

Once the environment variable is set and redeployed, your frontend will correctly connect to the backend API.

## Technical Details
- **Local Development**: Uses `.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`
- **Production (Vercel)**: Needs environment variable set in dashboard (`.env.local` is not deployed)
- **Backend Health**: ✅ Running at https://phaseii-todo-backend.onrender.com

---

**Next Steps After Fix:**
1. Set the environment variable in Vercel (Step 3)
2. Redeploy the frontend (Step 4)
3. Test authentication (Step 5)

Your todo app will be fully functional once this is done!
