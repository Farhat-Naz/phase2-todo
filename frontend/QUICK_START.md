# Quick Start Guide

## Get Started in 3 Steps

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## What You Get

- **Landing Page**: http://localhost:3000
- **Registration**: http://localhost:3000/register
- **Login**: http://localhost:3000/login
- **Dashboard**: http://localhost:3000/dashboard (after login)

## Testing the App

### 1. Register a New User

1. Go to http://localhost:3000/register
2. Fill in:
   - Name: "John Doe"
   - Email: "john@example.com"
   - Password: "password123" (min 8 chars)
3. Click "Create Account"
4. You'll be redirected to `/dashboard`

### 2. Login

1. Go to http://localhost:3000/login
2. Enter email and password
3. Click "Sign In"
4. You'll be redirected to `/dashboard`

## Important Commands

```bash
# Development
npm run dev          # Start dev server

# Type Checking
npm run type-check   # Check TypeScript errors

# Build
npm run build        # Build for production
npm start            # Start production server

# Linting
npm run lint         # Run ESLint
```

## Backend Requirements

Make sure your backend is running on `http://localhost:8000` with these endpoints:

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

## Project Structure

```
frontend/
├── app/                    # Pages (Next.js App Router)
│   ├── (auth)/
│   │   ├── login/         # Login page
│   │   └── register/      # Registration page
│   ├── dashboard/         # Dashboard (protected)
│   ├── page.tsx           # Home/landing page
│   └── layout.tsx         # Root layout
├── components/
│   ├── features/auth/     # Auth forms
│   └── ui/                # Reusable components
├── hooks/
│   └── useAuth.ts         # Authentication hook
├── lib/
│   ├── api.ts             # API client
│   └── auth.ts            # Auth utilities
└── types/
    └── user.ts            # TypeScript types
```

## Key Features

✅ User registration with validation
✅ User login with JWT authentication
✅ Protected routes (dashboard)
✅ Type-safe TypeScript
✅ Responsive design (mobile-first)
✅ Error handling with user-friendly messages
✅ Loading states during API calls

## Troubleshooting

### "Network error" message

- Ensure backend is running on http://localhost:8000
- Check CORS is enabled for http://localhost:3000

### TypeScript errors

```bash
npm run type-check
```

### Build errors

```bash
rm -rf .next
npm run build
```

## Next Phase

Phase 2 will add:
- Todo CRUD operations
- Voice input support
- Urdu language support
- Dark mode toggle

## Need Help?

Check the full `README.md` for detailed documentation.
