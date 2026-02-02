# Netlify Deployment Setup

## Quick Deploy to Netlify

### Step 1: Push to GitHub
Make sure your latest code is pushed to GitHub (already done).

### Step 2: Import to Netlify
1. Go to https://app.netlify.com
2. Click **"Add new site"** → **"Import an existing project"**
3. Choose **"GitHub"** (authorize if needed)
4. Select repository: **`Farhat-Naz/phaseII-todo`**
5. Configure build settings:

**Build Settings:**
- **Base directory**: `frontend`
- **Build command**: `npm run build`
- **Publish directory**: `frontend/.next`
- **Branch to deploy**: `master` or `006-high-priority`

### Step 3: Environment Variables (CRITICAL)
Before deploying, add environment variables:

1. In Netlify dashboard, go to **"Site settings"** → **"Environment variables"**
2. Click **"Add a variable"** → **"Add a single variable"**
3. Add the following:

```
Key: NEXT_PUBLIC_API_URL
Value: https://phaseii-todo-backend.onrender.com
Scopes: All (Production, Deploy Previews, Branch deploys)
```

4. Click **"Save"**

### Step 4: Deploy
1. Click **"Deploy site"** button
2. Wait 2-3 minutes for build to complete
3. Netlify will provide a URL like: `https://your-site-name.netlify.app`

### Step 5: Test
Visit your Netlify URL and test:
- ✅ Landing page loads
- ✅ Registration works
- ✅ Login works
- ✅ Dashboard shows todos
- ✅ Voice input works

## Alternative: Netlify CLI Deploy

If you prefer using CLI:

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Navigate to frontend directory
cd frontend

# Initialize Netlify (first time only)
netlify init

# Deploy
netlify deploy --prod
```

When prompted:
- **Build command**: `npm run build`
- **Publish directory**: `.next`

## Troubleshooting

### Build Fails
- Check that `NODE_VERSION=20` is set
- Verify `package.json` has correct scripts
- Check build logs in Netlify dashboard

### 404 Errors on API Calls
- **Cause**: Missing `NEXT_PUBLIC_API_URL` environment variable
- **Fix**: Add environment variable in Netlify dashboard (Step 3)
- **Verify**: Check "Environment variables" section in settings

### Runtime Errors
- Check Netlify function logs
- Verify Next.js 15 compatibility
- Ensure all dependencies are properly installed

## Backend Health Check
Verify backend is running:
```bash
curl https://phaseii-todo-backend.onrender.com/health
# Should return: {"status":"ok"}
```

## Custom Domain (Optional)
After successful deployment:
1. Go to **"Domain settings"**
2. Click **"Add custom domain"**
3. Follow Netlify's DNS configuration instructions

---

**Next Steps:**
1. Import project to Netlify
2. Set `NEXT_PUBLIC_API_URL` environment variable
3. Deploy and test
4. Your app will be live on Netlify! 🎉
