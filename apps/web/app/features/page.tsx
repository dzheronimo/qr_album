import { Metadata } from 'next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MarketingShell } from '@/components/marketing/MarketingShell';

export const metadata: Metadata = {
  title: 'Возможности StoryQR',
  description: 'Ключевые возможности сервиса StoryQR: загрузка медиа, QR-доступ, аналитика и тарифы для разных сценариев.',
};

export default function FeaturesPage() {
  return (
    <MarketingShell
      title="Возможности StoryQR"
      subtitle="Все, что нужно для запуска интерактивного альбома события"
    >
      <div className="grid gap-4 md:grid-cols-2 mb-8">
        {['QR для каждого альбома', 'PIN-защита страниц', 'Печать карточек', 'Базовая и расширенная аналитика'].map((item) => (
          <Card key={item}><CardContent className="pt-6">{item}</CardContent></Card>
        ))}
      </div>

      <h2 className="text-2xl font-semibold mb-4">Выберите подходящий план</h2>
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Бесплатный</CardTitle></CardHeader>
          <CardContent className="text-sm text-muted-foreground">Для тестирования и небольших мероприятий.</CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Pro</CardTitle></CardHeader>
          <CardContent className="text-sm text-muted-foreground">Для активного использования с расширенными лимитами и поддержкой.</CardContent>
        </Card>
      </div>
    </MarketingShell>
  );
}
