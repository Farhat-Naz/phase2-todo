/**
 * API Client with JWT authentication and error handling
 */

import { getToken, removeToken } from './auth';

// Use empty string in production (proxied via Vercel rewrites), localhost for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL === ''
  ? ''
  : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Standard API error response structure
 */
export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
  statusCode: number;
}

/**
 * API request configuration
 */
interface ApiRequestConfig {
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
  requiresAuth?: boolean;
}

/**
 * Handle API errors with user-friendly messages
 */
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
    errorDetails = {
      message: response.statusText || errorMessage,
      statusCode: response.status,
    };
  }

  // Use specific error message from backend, or fall back to generic message
  // Only use generic messages if backend didn't provide a specific error
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

  // Only use generic message if we don't have a specific error from backend
  if (errorMessage === 'An unexpected error occurred') {
    errorDetails.message = userFriendlyErrors[response.status] || errorDetails.message;
  }

  // Clear token and redirect to login on authentication failure
  if (response.status === 401 && typeof window !== 'undefined') {
    removeToken();
    // Extract locale from current path (e.g., /en/dashboard -> en)
    const pathParts = window.location.pathname.split('/').filter(Boolean);
    const locale = ['en', 'ur'].includes(pathParts[0]) ? pathParts[0] : 'en';
    window.location.href = `/${locale}/login`;
  }

  throw errorDetails;
}

/**
 * Make an API request with automatic JWT token attachment
 */
export async function makeApiRequest<T>(config: ApiRequestConfig): Promise<T> {
  const { endpoint, method, body, headers = {}, requiresAuth = true } = config;

  const url = `${API_BASE_URL}${endpoint}`;
  const requestHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    ...headers,
  };

  // Attach JWT token for authenticated requests
  if (requiresAuth) {
    const token = getToken();
    if (token) {
      requestHeaders['Authorization'] = `Bearer ${token}`;
    }
  }

  const response = await fetch(url, {
    method,
    headers: requestHeaders,
    body: body ? JSON.stringify(body) : undefined,
    credentials: 'include', // Required for CORS with credentials
  });

  if (!response.ok) {
    await handleApiError(response);
  }

  // Handle empty responses (e.g., 204 No Content)
  const contentType = response.headers.get('content-type');
  if (!contentType || !contentType.includes('application/json')) {
    return {} as T;
  }

  return response.json() as T;
}

/**
 * Type guard for API errors
 */
export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    'statusCode' in error
  );
}

/**
 * Handle and format API errors for display
 */
export function handleError(error: unknown): string {
  if (isApiError(error)) {
    return error.message;
  }

  if (error instanceof TypeError && error.message === 'Failed to fetch') {
    return 'Network error. Please check your connection.';
  }

  return 'An unexpected error occurred';
}

/**
 * Convenience methods for common HTTP operations
 */
export const api = {
  get: <T>(endpoint: string, requiresAuth = true) =>
    makeApiRequest<T>({ endpoint, method: 'GET', requiresAuth }),

  post: <T>(endpoint: string, body?: unknown, requiresAuth = true) =>
    makeApiRequest<T>({ endpoint, method: 'POST', body, requiresAuth }),

  put: <T>(endpoint: string, body?: unknown, requiresAuth = true) =>
    makeApiRequest<T>({ endpoint, method: 'PUT', body, requiresAuth }),

  patch: <T>(endpoint: string, body?: unknown, requiresAuth = true) =>
    makeApiRequest<T>({ endpoint, method: 'PATCH', body, requiresAuth }),

  delete: <T>(endpoint: string, requiresAuth = true) =>
    makeApiRequest<T>({ endpoint, method: 'DELETE', requiresAuth }),
};
