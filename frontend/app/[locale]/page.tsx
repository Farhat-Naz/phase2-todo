import Link from 'next/link';
import { getTranslations } from 'next-intl/server';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { LanguageSwitcher } from '@/components/features/shared/LanguageSwitcher';

export default async function HomePage({ params }: { params: Promise<{ locale: string }> }) {
  // Await params in Next.js 15+
  const { locale } = await params;
  const t = await getTranslations({ locale });

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Navigation */}
      <nav className="border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className={`flex justify-between items-center h-16 ${locale === 'ur' ? 'flex-row-reverse' : ''}`}>
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                TodoApp
              </h1>
            </div>
            <div className={`flex items-center gap-4 ${locale === 'ur' ? 'flex-row-reverse' : ''}`}>
              <LanguageSwitcher variant="compact" />
              <Link href={`/${locale}/login`}>
                <Button variant="ghost" size="md">
                  {t('auth.login')}
                </Button>
              </Link>
              <Link href={`/${locale}/register`}>
                <Button variant="primary" size="md">
                  {t('landing.getStarted')}
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className={`text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6 animate-fade-in ${locale === 'ur' ? 'font-urdu' : ''}`}>
            {t('landing.title').split(' - ')[0]}
            <br />
            <span className="text-primary-600 dark:text-primary-400">
              {t('landing.title').split(' - ')[1] || t('landing.title')}
            </span>
          </h2>
          <p className={`text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto mb-8 animate-slide-up ${locale === 'ur' ? 'font-urdu' : ''}`}>
            {t('landing.subtitle')}
          </p>
          <div className={`flex gap-4 justify-center animate-scale-in ${locale === 'ur' ? 'flex-row-reverse' : ''}`}>
            <Link href={`/${locale}/register`}>
              <Button variant="primary" size="lg">
                {t('landing.getStarted')}
              </Button>
            </Link>
            <Link href={`/${locale}/login`}>
              <Button variant="outline" size="lg">
                {t('auth.login')}
              </Button>
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <Card variant="elevated" padding="lg" hover>
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-6 h-6 text-primary-600 dark:text-primary-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h3 className={`text-xl font-semibold text-gray-900 dark:text-white mb-2 ${locale === 'ur' ? 'font-urdu' : ''}`}>
                {t('landing.features')}
              </h3>
              <p className={`text-gray-600 dark:text-gray-400 ${locale === 'ur' ? 'font-urdu' : ''}`}>
                {t('landing.modernDesc')}
              </p>
            </div>
          </Card>

          <Card variant="elevated" padding="lg" hover>
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-6 h-6 text-primary-600 dark:text-primary-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                  />
                </svg>
              </div>
              <h3 className={`text-xl font-semibold text-gray-900 dark:text-white mb-2 ${locale === 'ur' ? 'font-urdu' : ''}`}>
                {t('landing.voiceInput')}
              </h3>
              <p className={`text-gray-600 dark:text-gray-400 ${locale === 'ur' ? 'font-urdu' : ''}`}>
                {t('landing.voiceInputDesc')}
              </p>
            </div>
          </Card>

          <Card variant="elevated" padding="lg" hover>
            <div className="text-center">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-6 h-6 text-primary-600 dark:text-primary-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"
                  />
                </svg>
              </div>
              <h3 className={`text-xl font-semibold text-gray-900 dark:text-white mb-2 ${locale === 'ur' ? 'font-urdu' : ''}`}>
                {t('landing.multilingual')}
              </h3>
              <p className={`text-gray-600 dark:text-gray-400 ${locale === 'ur' ? 'font-urdu' : ''}`}>
                {t('landing.multilingualDesc')}
              </p>
            </div>
          </Card>
        </div>

        {/* CTA Section */}
        <div className="mt-20 text-center">
          <Card variant="elevated" padding="lg" className="max-w-3xl mx-auto bg-gradient-to-r from-primary-600 to-primary-700 border-0">
            <h3 className={`text-3xl font-bold text-white mb-4 ${locale === 'ur' ? 'font-urdu' : ''}`}>
              {t('landing.getStarted')}
            </h3>
            <p className={`text-primary-100 mb-6 text-lg ${locale === 'ur' ? 'font-urdu' : ''}`}>
              {t('landing.subtitle')}
            </p>
            <Link href={`/${locale}/register`}>
              <Button
                variant="secondary"
                size="lg"
                className="bg-white text-primary-600 hover:bg-gray-100"
              >
                {t('auth.register')}
              </Button>
            </Link>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className={`text-center text-gray-600 dark:text-gray-400 ${locale === 'ur' ? 'font-urdu' : ''}`}>
            &copy; 2025 TodoApp. Built with Next.js 16, TypeScript, and Tailwind CSS.
          </p>
        </div>
      </footer>
    </div>
  );
}
