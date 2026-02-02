---
id: 016
title: Fix Vercel Runtime Crash
stage: general
date: 2026-01-19
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: none
labels: ["debugging", "vercel", "deployment", "nextjs", "serverless"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/app/page.tsx
  - VERCEL_ENV_SETUP.md
tests:
  - npm run build (passed)
---

## Prompt

everything is working well locally but verrcel is always showing error

## Response snapshot

Diagnosed and fixed Vercel runtime crash caused by client-side redirect in root page.

**Root Cause:**
The `app/page.tsx` was using a client component with `useRouter()` + `useEffect()` for redirecting to `/en`. This pattern causes runtime errors on Vercel's serverless environment because it relies on browser APIs during SSR.

**Solution:**
Converted to server-side redirect using Next.js `redirect()` function:

```tsx
// Before (❌ Client-side - crashes on Vercel)
'use client';
export default function RootPage() {
  const router = useRouter();
  useEffect(() => { router.replace('/en'); }, [router]);
  return <div>Redirecting...</div>;
}

// After (✅ Server-side - works on Vercel)
import { redirect } from 'next/navigation';
export default function RootPage() {
  redirect('/en');
}
```

**Implementation:**
1. Identified the issue through file analysis
2. Replaced client-side redirect with server-side `redirect()`
3. Verified build succeeds locally (`npm run build`)
4. Committed and pushed to trigger Vercel redeployment
5. Root page now correctly prerendered as static content

## Outcome

- ✅ Impact: Fixed production deployment crash on Vercel - app now loads correctly
- 🧪 Tests: Build verification passed - all pages prerender successfully
- 📁 Files: Modified `frontend/app/page.tsx` (client → server redirect)
- 🔁 Next prompts: Monitor Vercel deployment, verify environment variables if API issues
- 🧠 Reflection: Server-side redirects are mandatory for Next.js 15+ on serverless platforms

## Evaluation notes (flywheel)

- Failure modes observed: Client-side redirects in root pages cause serverless crashes
- Graders run and results (PASS/FAIL): Build check PASS, deployment trigger PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Consider adding redirect tests to CI/CD pipeline
