# Deployment Guide

## Render Deployment

### Environment Variables

**CRITICAL:** When setting the `DATABASE_URL` in Render, use the **exact format** below without quotes.

#### ✅ CORRECT Format

```
postgresql+psycopg://username:password@host/database?sslmode=require
```

**Example from Neon:**
```
postgresql+psycopg://neondb_owner:npg_ZAGN4xaUk2mh@ep-red-unit-a13i3o3z-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
```

#### ❌ WRONG Formats (DO NOT USE)

```bash
# ❌ With quotes (causes parsing error)
'postgresql://...'
"postgresql://..."

# ❌ With 'psql' typo
'psql'postgresql://...
psql'postgresql://...

# ❌ Without +psycopg dialect
postgresql://...  # Will work but logs conversion warning

# ❌ With extra whitespace or newlines
postgresql://...\n
  postgresql://...
```

### Required Environment Variables

Set these in Render Dashboard > Environment:

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | `postgresql+psycopg://...` | **NO QUOTES**, include `+psycopg` |
| `SECRET_KEY` | Generate random string | 32+ characters, no quotes |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiry time |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token expiry |
| `CORS_ORIGINS` | `https://your-frontend.vercel.app` | Frontend URL |
| `ENV` | `production` | Environment name |
| `DEBUG` | `False` | Disable debug mode |

### How to Get DATABASE_URL from Neon

1. Go to Neon Dashboard → Your Project → Connection Details
2. Select **"Pooled connection"** (not "Direct connection")
3. Copy the connection string (looks like `postgresql://neondb_owner:...@...neon.tech/neondb`)
4. **Add `+psycopg` after `postgresql`**: `postgresql+psycopg://...`
5. Paste into Render **without any quotes**

### Common Issues

#### Issue: `Could not parse SQLAlchemy URL from string 'psql'postgresql://...'`

**Cause:** DATABASE_URL has quotes or typos

**Solution:**
1. Go to Render → Environment Variables
2. Find `DATABASE_URL`
3. Remove ANY quotes (`'` or `"`)
4. Fix `psql` → `postgresql+psycopg`
5. Save and redeploy

#### Issue: `ModuleNotFoundError: No module named 'psycopg'`

**Cause:** Using wrong package name

**Solution:** Ensure `requirements.txt` has:
```txt
psycopg[binary]==3.2.3  # ✅ CORRECT
```
NOT:
```txt
psycopg-binary==3.2.3  # ❌ WRONG
```

## Vercel Frontend Deployment

### Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `NEXT_PUBLIC_API_URL` | `https://your-backend.onrender.com` | Backend URL |

## Troubleshooting

For deployment issues, check Render logs and ensure DATABASE_URL is set correctly without quotes.
