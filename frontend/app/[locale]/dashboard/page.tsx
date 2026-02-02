'use client';

import { useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { TodoList } from '@/components/features/todos/TodoList';
import { LoadingSpinner } from '@/components/features/shared/LoadingSpinner';
import { Button } from '@/components/ui/Button';
import { LanguageSwitcher } from '@/components/features/shared/LanguageSwitcher';

/**
 * Dashboard Page - Main todo management interface
 *
 * Features:
 * - Protected route (requires authentication)
 * - Displays TodoList component with all CRUD functionality
 * - Navigation header with logout and language switcher
 * - Responsive layout with proper spacing
 * - Loading state while checking authentication
 * - Auto-redirect to login if not authenticated
 */
export default function DashboardPage() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const params = useParams();
  const locale = params?.locale as string || 'en';

  /**
   * Redirect to login if not authenticated
   */
  useEffect(() => {
    if (!loading && !user) {
      router.push(`/${locale}/login`);
    }
  }, [loading, user, router, locale]);

  /**
   * Handle logout
   */
  const handleLogout = async () => {
    await logout();
    router.push(`/${locale}/login`);
  };

  /**
   * Handle back to home
   */
  const handleBackToHome = () => {
    router.push(`/${locale}`);
  };

  /**
   * Show loading spinner while checking authentication
   */
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <LoadingSpinner size="lg" text="Loading dashboard..." />
      </div>
    );
  }

  /**
   * Don't render dashboard if not authenticated (will redirect)
   */
  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Navigation Header */}
      <nav className="border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className={`flex justify-between items-center h-16 ${locale === 'ur' ? 'flex-row-reverse' : ''}`}>
            {/* Logo and Welcome */}
            <div className={`flex items-center gap-4 ${locale === 'ur' ? 'flex-row-reverse' : ''}`}>
              <h1 className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                TodoApp
              </h1>
              <div className="hidden sm:block">
                <span className={`text-sm text-gray-600 dark:text-gray-400 ${locale === 'ur' ? 'font-urdu' : ''}`}>
                  {locale === 'ur' ? 'خوش آمدید' : 'Welcome'}, <span className="font-semibold text-gray-900 dark:text-white">{user?.name || 'Guest'}</span>
                </span>
              </div>
            </div>

            {/* Actions */}
            <div className={`flex items-center gap-3 ${locale === 'ur' ? 'flex-row-reverse' : ''}`}>
              <Button
                onClick={handleBackToHome}
                variant="ghost"
                size="sm"
                className={locale === 'ur' ? 'font-urdu' : ''}
                title={locale === 'ur' ? 'ہوم پیج پر واپس جائیں' : 'Back to Home'}
              >
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                  />
                </svg>
                <span className="ml-2 hidden md:inline">
                  {locale === 'ur' ? 'ہوم' : 'Home'}
                </span>
              </Button>
              <LanguageSwitcher variant="compact" />
              <Button
                onClick={handleLogout}
                variant="outline"
                size="sm"
                className={locale === 'ur' ? 'font-urdu' : ''}
              >
                {locale === 'ur' ? 'لاگ آؤٹ' : 'Logout'}
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h2 className={`text-3xl font-bold text-gray-900 dark:text-white mb-2 ${locale === 'ur' ? 'font-urdu text-right' : ''}`}>
            {locale === 'ur' ? 'میرے کام' : 'My Tasks'}
          </h2>
          <p className={`text-gray-600 dark:text-gray-400 ${locale === 'ur' ? 'font-urdu text-right' : ''}`}>
            {locale === 'ur' ? 'اپنے کاموں کا نظم کریں اور پیداواری بنیں' : 'Manage your tasks and stay productive'}
          </p>
        </div>

        {/* Todo List Component */}
        <TodoList />
      </main>
    </div>
  );
}
