'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { api, handleError } from '@/lib/api';
import { setToken, removeToken, getToken } from '@/lib/auth';
import { User } from '@/types/user';

interface UseAuthReturn {
  user: User | null;
  loading: boolean;
  error: string | null;
  register: (data: { email: string; password: string; name: string }) => Promise<void>;
  login: (data: { email: string; password: string }, locale?: string) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/**
 * Authentication hook for managing user state and auth operations
 * Provides register, login, logout, and session management with JWT tokens
 */
export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  /**
   * Fetch current user from API
   */
  const fetchUser = useCallback(async () => {
    try {
      const token = getToken();
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }

      const userData = await api.get<User>('/api/auth/me');
      setUser(userData);
    } catch (err) {
      // Token might be invalid or expired
      removeToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Load user on mount if token exists
   */
  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  /**
   * Register new user
   */
  const register = useCallback(
    async (data: { email: string; password: string; name: string }) => {
      setLoading(true);
      setError(null);

      try {
        // Register user
        await api.post<User>('/api/auth/register', data, false);

        // Now login to get token
        await login({ email: data.email, password: data.password });
      } catch (err: any) {
        const errorMessage = handleError(err);
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [router]
  );

  /**
   * Login existing user
   */
  const login = useCallback(
    async (data: { email: string; password: string }, locale: string = 'en') => {
      setLoading(true);
      setError(null);

      try {
        // FastAPI OAuth2 expects form data
        const formData = new URLSearchParams();
        formData.append('username', data.email);
        formData.append('password', data.password);

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Login failed');
        }

        const authData: AuthResponse = await response.json();

        // Store token
        setToken(authData.access_token);

        // Set user data from response
        setUser(authData.user);

        // Redirect to dashboard with locale
        router.push(`/${locale}/dashboard`);
      } catch (err: any) {
        const errorMessage = handleError(err);
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [router]
  );

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    try {
      removeToken();
      setUser(null);
      router.push('/login');
    } catch (err: any) {
      setError(handleError(err));
    }
  }, [router]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    user,
    loading,
    error,
    register,
    login,
    logout,
    clearError,
  };
}
