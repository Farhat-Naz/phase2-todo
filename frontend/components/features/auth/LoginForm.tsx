'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { UserLogin } from '@/types/user';

interface FormErrors {
  email?: string;
  password?: string;
}

interface LoginFormProps {
  locale: string;
}

export function LoginForm({ locale }: LoginFormProps) {
  const { login, loading, error } = useAuth();
  const [formData, setFormData] = useState<UserLogin>({
    email: '',
    password: '',
  });
  const [formErrors, setFormErrors] = useState<FormErrors>({});

  /**
   * Validate form data
   */
  const validateForm = (): boolean => {
    const errors: FormErrors = {};

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!emailRegex.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    // Password validation
    if (!formData.password) {
      errors.password = 'Password is required';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Clear previous errors
    setFormErrors({});

    // Validate form
    if (!validateForm()) {
      return;
    }

    try {
      await login(formData, locale);
      // Navigation to dashboard is handled by useAuth hook
    } catch {
      // Error display is handled by useAuth hook
    }
  };

  /**
   * Handle input change
   */
  const handleChange = (field: keyof UserLogin) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: e.target.value,
    }));

    // Clear field error on change
    if (formErrors[field]) {
      setFormErrors((prev) => ({
        ...prev,
        [field]: undefined,
      }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Server error display */}
      {error && (
        <div className="p-4 rounded-lg bg-error-light dark:bg-error-dark/20 border border-error">
          <p className="text-sm text-error-dark dark:text-error-light">{error}</p>
        </div>
      )}

      {/* Email field */}
      <Input
        label="Email Address"
        type="email"
        id="email"
        placeholder="you@example.com"
        value={formData.email}
        onChange={handleChange('email')}
        error={formErrors.email}
        required
        autoComplete="email"
      />

      {/* Password field */}
      <Input
        label="Password"
        type="password"
        id="password"
        placeholder="Enter your password"
        value={formData.password}
        onChange={handleChange('password')}
        error={formErrors.password}
        required
        autoComplete="current-password"
      />

      {/* Submit button */}
      <Button
        type="submit"
        variant="primary"
        size="lg"
        isLoading={loading}
        className="w-full"
      >
        Sign In
      </Button>

      {/* Register link */}
      <p className="text-center text-sm text-gray-600 dark:text-gray-400">
        Don&apos;t have an account?{' '}
        <Link
          href={`/${locale}/register`}
          className="font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
        >
          Create account
        </Link>
      </p>
    </form>
  );
}
