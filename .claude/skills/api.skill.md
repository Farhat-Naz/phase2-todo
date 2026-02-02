# API Request Handler Skill

Reusable logic for standardized API request formatting, error handling, and JWT authentication across the Todo application.

## Purpose

This skill provides consistent patterns for:
- **API Request Formatting**: Standard structure for all HTTP requests
- **Error Handling**: Unified error response parsing and user feedback
- **JWT Attachment**: Automatic authentication token injection

## Usage Context

**Used by:**
- Frontend Agent (client-side API calls)
- Core Agent (general API implementation guidance)

**When to apply:**
- Making authenticated API requests from the frontend
- Implementing new API integrations
- Standardizing error handling across components
- Setting up API client utilities

## Core Patterns

### 1. API Request Formatting

```typescript
// Standard API request structure
interface ApiRequestConfig {
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
  requiresAuth?: boolean; // Default: true
}

// Base URL configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Standard request builder
async function makeApiRequest<T>(config: ApiRequestConfig): Promise<T> {
  const { endpoint, method, body, headers = {}, requiresAuth = true } = config;

  const url = `${API_BASE_URL}${endpoint}`;
  const requestHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    ...headers,
  };

  // JWT attachment logic (see section 3)
  if (requiresAuth) {
    const token = await getAuthToken();
    if (token) {
      requestHeaders['Authorization'] = `Bearer ${token}`;
    }
  }

  const response = await fetch(url, {
    method,
    headers: requestHeaders,
    body: body ? JSON.stringify(body) : undefined,
  });

  // Error handling logic (see section 2)
  if (!response.ok) {
    await handleApiError(response);
  }

  return response.json() as T;
}
```

### 2. Error Handling

```typescript
// Standard error response structure
interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
  statusCode: number;
}

// Error handler with user-friendly messages
async function handleApiError(response: Response): Promise<never> {
  let errorMessage = 'An unexpected error occurred';
  let errorDetails: ApiError;

  try {
    const errorData = await response.json();
    errorMessage = errorData.message || errorData.detail || errorMessage;
    errorDetails = {
      message: errorMessage,
      code: errorData.code,
      details: errorData.details,
      statusCode: response.status,
    };
  } catch {
    // If JSON parsing fails, use response status text
    errorDetails = {
      message: response.statusText || errorMessage,
      statusCode: response.status,
    };
  }

  // Map common HTTP status codes to user-friendly messages
  const userFriendlyErrors: Record<number, string> = {
    400: 'Invalid request. Please check your input.',
    401: 'Authentication required. Please log in.',
    403: 'You do not have permission to perform this action.',
    404: 'The requested resource was not found.',
    409: 'This action conflicts with existing data.',
    422: 'Validation failed. Please check your input.',
    429: 'Too many requests. Please try again later.',
    500: 'Server error. Please try again later.',
    503: 'Service unavailable. Please try again later.',
  };

  errorDetails.message = userFriendlyErrors[response.status] || errorDetails.message;

  throw errorDetails;
}

// React hook for error display (frontend usage)
function useApiErrorHandler() {
  const handleError = (error: unknown) => {
    if (isApiError(error)) {
      // Display error toast/notification
      console.error('API Error:', error.message, error.details);
      // Integration point for toast library
      // toast.error(error.message);
      return error.message;
    }

    // Handle network errors
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      const networkError = 'Network error. Please check your connection.';
      console.error(networkError);
      // toast.error(networkError);
      return networkError;
    }

    // Fallback for unknown errors
    const fallbackError = 'An unexpected error occurred';
    console.error('Unknown error:', error);
    // toast.error(fallbackError);
    return fallbackError;
  };

  return { handleError };
}

// Type guard
function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    'statusCode' in error
  );
}
```

### 3. JWT Attachment

```typescript
import { useSession } from 'better-auth/react'; // Adjust import based on Better Auth setup

// Client-side JWT retrieval (React hook)
function useAuthToken() {
  const { data: session } = useSession();

  const getToken = async (): Promise<string | null> => {
    // Return JWT from Better Auth session
    return session?.accessToken || null;
  };

  return { getToken };
}

// Server-side JWT retrieval (for Server Components/Actions)
async function getServerAuthToken(): Promise<string | null> {
  const { cookies } = await import('next/headers');

  // Retrieve JWT from httpOnly cookie set by Better Auth
  const cookieStore = await cookies();
  const authCookie = cookieStore.get('better-auth.session_token');

  return authCookie?.value || null;
}

// Unified token retrieval for makeApiRequest
async function getAuthToken(): Promise<string | null> {
  // Check if running in browser or server
  if (typeof window !== 'undefined') {
    // Client-side: retrieve from Better Auth React context
    // Note: In practice, use the hook inside components
    // This is a simplified example for the skill documentation
    return null; // Will be replaced by actual session token in implementation
  } else {
    // Server-side: retrieve from cookies
    return await getServerAuthToken();
  }
}
```

## Implementation Checklist

When implementing API calls, ensure:

- [ ] API base URL is configured via environment variable
- [ ] Request headers include 'Content-Type: application/json'
- [ ] JWT token is automatically attached for authenticated endpoints
- [ ] All API responses are type-checked with TypeScript interfaces
- [ ] Error responses are parsed and user-friendly messages are shown
- [ ] Network errors (fetch failures) are handled gracefully
- [ ] Loading states are implemented for async operations
- [ ] Error states display actionable feedback to users

## Environment Variables Required

```env
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth configuration
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=http://localhost:3000
```

## Security Considerations

1. **Token Storage**: JWT tokens should be stored in httpOnly cookies when possible (handled by Better Auth)
2. **HTTPS Only**: Always use HTTPS in production to prevent token interception
3. **Token Refresh**: Implement token refresh logic when access tokens expire
4. **CORS**: Ensure backend API has proper CORS configuration for frontend origin
5. **Input Validation**: Always validate and sanitize user input before sending to API

## Example Usage

### Frontend Component

```typescript
'use client';

import { useState } from 'react';
import { useSession } from 'better-auth/react';

interface Todo {
  id: string;
  title: string;
  completed: boolean;
  userId: string;
}

export function TodoList() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { data: session } = useSession();

  const fetchTodos = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await makeApiRequest<Todo[]>({
        endpoint: '/api/todos',
        method: 'GET',
        requiresAuth: true,
      });
      setTodos(data);
    } catch (err) {
      const { handleError } = useApiErrorHandler();
      setError(handleError(err));
    } finally {
      setLoading(false);
    }
  };

  const createTodo = async (title: string) => {
    try {
      const newTodo = await makeApiRequest<Todo>({
        endpoint: '/api/todos',
        method: 'POST',
        body: { title, completed: false },
        requiresAuth: true,
      });
      setTodos([...todos, newTodo]);
    } catch (err) {
      const { handleError } = useApiErrorHandler();
      setError(handleError(err));
    }
  };

  // Component JSX...
}
```

## Best Practices

1. **Type Safety**: Always define TypeScript interfaces for request/response shapes
2. **Error Boundaries**: Wrap API-calling components in React Error Boundaries
3. **Loading States**: Show loading indicators during API requests
4. **Retry Logic**: Implement retry for transient failures (optional, based on requirements)
5. **Request Deduplication**: Prevent duplicate requests for the same resource
6. **Cancellation**: Cancel pending requests on component unmount using AbortController
7. **Caching**: Implement client-side caching for frequently accessed data (consider SWR or React Query)

## Integration Points

- **Better Auth**: JWT tokens retrieved from session context or httpOnly cookies
- **Backend API**: FastAPI endpoints at `http://localhost:8000` (configurable)
- **Error Display**: Integrate with toast notification library (e.g., react-hot-toast, sonner)
- **State Management**: Can be used with React Query, SWR, or plain React state

## Testing Considerations

- Mock `fetch` in unit tests using libraries like MSW (Mock Service Worker)
- Test error handling paths with different HTTP status codes
- Verify JWT attachment in authenticated requests
- Test network error scenarios (offline mode)
- Validate type safety with TypeScript compiler checks
