import { getRequestConfig } from 'next-intl/server';

// Define available locales
export const locales = ['en', 'ur'] as const;
export type Locale = (typeof locales)[number];

// Default locale
export const defaultLocale: Locale = 'en';

export default getRequestConfig(async ({ requestLocale }) => {
  // Request locale is the value from the middleware
  let locale = await requestLocale;

  // Fallback to default locale if no locale is set
  if (!locale || !locales.includes(locale as Locale)) {
    locale = defaultLocale;
  }

  return {
    locale,
    messages: (await import(`./messages/${locale}.json`)).default,
  };
});
