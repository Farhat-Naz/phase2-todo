# Todo App Frontend

A modern, full-stack todo application built with Next.js 16+, TypeScript, and Tailwind CSS.

## Features

- **Authentication**: User registration and login with JWT tokens
- **Modern UI**: Beautiful, responsive interface with Tailwind CSS
- **Type Safety**: Strict TypeScript configuration for robust code
- **Form Validation**: Client-side validation with user-friendly error messages
- **Dark Mode Ready**: Design system supports light and dark themes
- **Mobile Responsive**: Optimized for all screen sizes (320px+)
- **Error Handling**: Comprehensive error handling with user-friendly messages

## Tech Stack

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 3.4+
- **UI Components**: Custom components following design system
- **State Management**: React hooks (useState, useEffect, useCallback)
- **Authentication**: Cookie-based JWT storage
- **HTTP Client**: Native Fetch API with custom wrapper

## Prerequisites

- Node.js 18+ or higher
- pnpm (recommended) or npm
- Backend API running on http://localhost:8000

## Getting Started

### 1. Install Dependencies

```bash
pnpm install
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.local.example .env.local
```

Update the values in `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3000
```

### 3. Run Development Server

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Build for Production

```bash
pnpm build
pnpm start
```

## Project Structure

```
frontend/
├── app/                      # Next.js App Router pages
│   ├── (auth)/              # Auth route group
│   │   ├── login/           # Login page
│   │   └── register/        # Registration page
│   ├── dashboard/           # Dashboard page
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home/landing page
│   └── globals.css          # Global styles
├── components/
│   ├── features/            # Feature-specific components
│   │   └── auth/            # Authentication components
│   │       ├── LoginForm.tsx
│   │       └── RegisterForm.tsx
│   └── ui/                  # Reusable UI components
│       ├── Button.tsx
│       ├── Card.tsx
│       └── Input.tsx
├── hooks/                   # Custom React hooks
│   └── useAuth.ts           # Authentication hook
├── lib/                     # Utility libraries
│   ├── api.ts               # API client with JWT interceptor
│   ├── auth.ts              # Auth utilities
│   └── utils.ts             # General utilities
├── types/                   # TypeScript type definitions
│   └── user.ts              # User and auth types
├── public/                  # Static assets
├── .env.local.example       # Environment variable template
├── next.config.js           # Next.js configuration
├── tailwind.config.ts       # Tailwind CSS configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies and scripts
```

## Key Files

### Authentication Flow

1. **`hooks/useAuth.ts`**: Main authentication hook
   - Manages user state, loading, and errors
   - Provides `register()`, `login()`, `logout()` methods
   - Auto-fetches user on mount if authenticated

2. **`lib/api.ts`**: API client
   - Automatic JWT token attachment
   - Request/response interceptors
   - Error handling with user-friendly messages
   - Type-safe HTTP methods

3. **`lib/auth.ts`**: Auth utilities
   - Token storage in cookies and localStorage
   - Session management
   - Authentication state checks

### UI Components

All components follow the design system defined in `.claude/skills/ui.skill.md`:

- **Button**: Multiple variants (primary, secondary, outline, ghost, danger)
- **Input**: Form input with label, error, and helper text support
- **Card**: Container component with variants and hover effects

### Type Safety

All types are strictly defined in `types/user.ts`:

```typescript
interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
}

interface UserRegister {
  email: string;
  password: string;
  name: string;
}

interface UserLogin {
  email: string;
  password: string;
}
```

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`:

### Endpoints Used

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (OAuth2 form data)
- `GET /api/auth/me` - Get current user (requires JWT)

### Authentication

JWT tokens are:
1. Received from the backend after successful login/registration
2. Stored in cookies and localStorage
3. Automatically attached to authenticated requests via `Authorization: Bearer {token}` header
4. Validated on the backend for protected routes

## Scripts

- `pnpm dev` - Start development server
- `pnpm build` - Build for production
- `pnpm start` - Start production server
- `pnpm lint` - Run ESLint
- `pnpm type-check` - Run TypeScript compiler check

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |
| `BETTER_AUTH_SECRET` | Secret key for auth (min 32 chars) | Required |
| `BETTER_AUTH_URL` | Frontend URL | `http://localhost:3000` |

## Form Validation

Both login and registration forms implement client-side validation:

### Registration
- **Email**: Valid email format required
- **Password**: Minimum 8 characters
- **Name**: Minimum 2 characters

### Login
- **Email**: Valid email format required
- **Password**: Required field

Server-side validation errors are also displayed to users.

## Error Handling

The app implements comprehensive error handling:

1. **Network Errors**: Detected and shown as connection issues
2. **API Errors**: Mapped to user-friendly messages based on HTTP status codes
3. **Validation Errors**: Shown inline on form fields
4. **Authentication Errors**: Redirect to login on 401 status

## Responsive Design

The app is fully responsive with mobile-first design:

- **Mobile**: 320px - 640px
- **Tablet**: 640px - 1024px
- **Desktop**: 1024px+

All components adapt to screen size using Tailwind's responsive classes.

## Accessibility

- WCAG 2.1 Level AA compliant
- Proper semantic HTML
- ARIA labels on interactive elements
- Keyboard navigation support
- Focus indicators on all interactive elements
- Screen reader friendly

## Next Steps

1. **Todo Management**: Implement todo CRUD operations (Phase 2)
2. **Voice Input**: Add Web Speech API integration (Phase 2)
3. **Multilingual Support**: Add Urdu language support with RTL (Phase 2)
4. **Dark Mode**: Implement theme switching (Phase 2)
5. **Real-time Updates**: Add WebSocket support (Future)

## Troubleshooting

### Backend Connection Issues

If you see "Network error. Please check your connection":

1. Ensure backend is running on `http://localhost:8000`
2. Check CORS configuration on backend
3. Verify `NEXT_PUBLIC_API_URL` in `.env.local`

### Type Errors

Run type checking to identify issues:

```bash
pnpm type-check
```

### Build Errors

Clear Next.js cache and rebuild:

```bash
rm -rf .next
pnpm build
```

## Contributing

1. Follow TypeScript strict mode guidelines
2. Use existing UI components (don't recreate)
3. Maintain consistent code style
4. Write type-safe code (no `any` types)
5. Test on multiple screen sizes

## License

MIT License - See LICENSE file for details
