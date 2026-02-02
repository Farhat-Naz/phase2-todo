import type { Metadata } from 'next';
import { Inter, Noto_Nastaliq_Urdu } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-geist-sans' });
const notoNastaliqUrdu = Noto_Nastaliq_Urdu({
  subsets: ['arabic'],
  weight: ['400', '700'],
  variable: '--font-urdu',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Todo App - Organize Your Tasks',
  description: 'A modern, full-stack todo application with voice input support and multilingual features',
  keywords: ['todo', 'task manager', 'productivity', 'voice input'],
  authors: [{ name: 'Todo App Team' }],
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${notoNastaliqUrdu.variable}`}>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
