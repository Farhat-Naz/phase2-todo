'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { UserRegister } from '@/types/user';

interface FormErrors {
  email?: string;
  password?: string;
  name?: string;
}

interface RegisterFormProps {
  locale: string;
}

export function RegisterForm({ locale }: RegisterFormProps) {
  const { register, loading, error } = useAuth();
  const [formData, setFormData] = useState<UserRegister>({
    email: '',
    password: '',
    name: '',
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
    } else if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    } else if (!/[A-Z]/.test(formData.password)) {
      errors.password = 'Password must contain at least 1 uppercase letter';
    } else if (!/[a-z]/.test(formData.password)) {
      errors.password = 'Password must contain at least 1 lowercase letter';
    } else if (!/\d/.test(formData.password)) {
      errors.password = 'Password must contain at least 1 number';
    }

    // Name validation
    if (!formData.name) {
      errors.name = 'Name is required';
    } else if (formData.name.length < 2) {
      errors.name = 'Name must be at least 2 characters';
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
      await register(formData);
      // Navigation to dashboard is handled by useAuth hook
    } catch {
      // Error display is handled by useAuth hook
    }
  };

  /**
   * Handle input change
   */
  const handleChange = (field: keyof UserRegister) => (
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

      {/* Name field */}
      <Input
        label="Full Name"
        type="text"
        id="name"
        placeholder="John Doe"
        value={formData.name}
        onChange={handleChange('name')}
        error={formErrors.name}
        required
        autoComplete="name"
      />

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
        placeholder="At least 8 characters"
        value={formData.password}
        onChange={handleChange('password')}
        error={formErrors.password}
        helperText="At least 8 characters, 1 uppercase, 1 lowercase, 1 number"
        required
        autoComplete="new-password"
      />

      {/* Submit button */}
      <Button
        type="submit"
        variant="primary"
        size="lg"
        isLoading={loading}
        className="w-full"
      >
        Create Account
      </Button>

      {/* Login link */}
      <p className="text-center text-sm text-gray-600 dark:text-gray-400">
        Already have an account?{' '}
        <Link
          href={`/${locale}/login`}
          className="font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
        >
          Sign in
        </Link>
      </p>
    </form>
  );
}
