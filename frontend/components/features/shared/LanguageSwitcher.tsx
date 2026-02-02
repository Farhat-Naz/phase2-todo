'use client';

/**
 * LanguageSwitcher Component - Toggle between English and Urdu
 *
 * Features:
 * - Toggle button for language switching
 * - Shows current language with icon
 * - Persists preference via next-intl cookies
 * - Accessible with ARIA labels
 * - Mobile responsive
 * - Smooth transition between locales
 */

import { useLocale } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

/**
 * Globe/Language icon component
 */
function GlobeIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"
      />
    </svg>
  );
}

interface LanguageSwitcherProps {
  variant?: 'default' | 'compact';
  className?: string;
}

export function LanguageSwitcher({ variant = 'default', className }: LanguageSwitcherProps) {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  /**
   * Switch to the other locale
   */
  const switchLocale = () => {
    const newLocale = locale === 'en' ? 'ur' : 'en';

    // Remove current locale from pathname and add new locale
    const pathWithoutLocale = pathname.replace(/^\/(en|ur)/, '');
    const newPath = `/${newLocale}${pathWithoutLocale || ''}`;

    router.push(newPath);
  };

  const isUrdu = locale === 'ur';
  const currentLangLabel = isUrdu ? 'اردو' : 'English';
  const nextLangLabel = isUrdu ? 'English' : 'اردو';

  if (variant === 'compact') {
    return (
      <button
        onClick={switchLocale}
        className={cn(
          'inline-flex items-center gap-2 px-3 py-2 rounded-lg',
          'text-sm font-medium transition-colors',
          'hover:bg-gray-100 dark:hover:bg-gray-800',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
          className
        )}
        aria-label={`Switch to ${nextLangLabel}`}
        title={`Switch to ${nextLangLabel}`}
      >
        <GlobeIcon className="w-5 h-5" />
        <span className="hidden sm:inline">{currentLangLabel}</span>
      </button>
    );
  }

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <GlobeIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />

      <div className="flex items-center bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
        <button
          onClick={() => {
            if (locale !== 'en') switchLocale();
          }}
          className={cn(
            'px-3 py-1.5 rounded-md text-sm font-medium transition-all',
            'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
            locale === 'en'
              ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
          )}
          aria-label="Switch to English"
          aria-pressed={locale === 'en'}
        >
          English
        </button>

        <button
          onClick={() => {
            if (locale !== 'ur') switchLocale();
          }}
          className={cn(
            'px-3 py-1.5 rounded-md text-sm font-medium transition-all',
            'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
            locale === 'ur'
              ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
          )}
          aria-label="Switch to Urdu"
          aria-pressed={locale === 'ur'}
          dir="rtl"
        >
          اردو
        </button>
      </div>
    </div>
  );
}
