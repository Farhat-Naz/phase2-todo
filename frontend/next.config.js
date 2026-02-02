const createNextIntlPlugin = require('next-intl/plugin');

const withNextIntl = createNextIntlPlugin('./i18n.ts');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  images: {
    domains: [],
  },
  // Fix Vercel workspace detection warning
  outputFileTracingRoot: require('path').join(__dirname, '../'),
};

module.exports = withNextIntl(nextConfig);
