import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { Providers } from './providers';
import { Toaster } from '@/components/ui/toaster';
import './globals.css';

export const dynamic = 'force-dynamic';

const inter = Inter({ subsets: ['latin', 'cyrillic'] });

export const metadata: Metadata = {
  title: {
    default: 'StoryQR - Создавайте интерактивные альбомы с QR-кодами',
    template: '%s | StoryQR',
  },
  description: 'Создавайте красивые цифровые альбомы, делитесь ими через QR-коды и отслеживайте взаимодействие с контентом.',
  keywords: ['QR-код', 'альбом', 'фото', 'видео', 'цифровой контент', 'интерактивность'],
  authors: [{ name: 'StoryQR Team' }],
  creator: 'StoryQR',
  publisher: 'StoryQR',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_PUBLIC_BASE_URL || 'https://storyqr.ru'),
  alternates: {
    canonical: '/',
    languages: {
      'ru-RU': '/ru',
      'en-US': '/en',
    },
  },
  openGraph: {
    type: 'website',
    locale: 'ru_RU',
    url: '/',
    title: 'StoryQR - Создавайте интерактивные альбомы с QR-кодами',
    description: 'Создавайте красивые цифровые альбомы, делитесь ими через QR-коды и отслеживайте взаимодействие с контентом.',
    siteName: 'StoryQR',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'StoryQR - Интерактивные альбомы с QR-кодами',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'StoryQR - Создавайте интерактивные альбомы с QR-кодами',
    description: 'Создавайте красивые цифровые альбомы, делитесь ими через QR-коды и отслеживайте взаимодействие с контентом.',
    images: ['/og-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: process.env.GOOGLE_SITE_VERIFICATION,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {children}
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
