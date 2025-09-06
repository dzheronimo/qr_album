import { Metadata } from 'next';

export const dynamic = 'force-dynamic';

export const metadata: Metadata = {
  title: {
    default: 'StoryQR - Создавайте интерактивные альбомы с QR-кодами',
    template: '%s | StoryQR',
  },
  description: 'Создавайте красивые цифровые альбомы, делитесь ими через QR-коды и отслеживайте взаимодействие с контентом.',
};

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
