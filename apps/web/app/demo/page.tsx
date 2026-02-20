import { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MarketingShell } from '@/components/marketing/MarketingShell';

export const metadata: Metadata = {
  title: 'Попробуйте StoryQR | Демо',
  description: 'Посмотрите демонстрацию StoryQR и протестируйте полный сценарий работы с QR-альбомами.',
  robots: {
    index: false,
    follow: true,
  },
};

export default function DemoPage() {
  return (
    <MarketingShell
      title="Попробуйте StoryQR"
      subtitle="Демо-сценарий: от создания альбома до сбора фото гостей"
    >
      <div className="grid gap-4 md:grid-cols-3 mb-8">
        {['Создайте событие', 'Разместите QR', 'Соберите медиа гостей'].map((item) => (
          <Card key={item}>
            <CardHeader><CardTitle className="text-base">{item}</CardTitle></CardHeader>
            <CardContent className="text-sm text-muted-foreground">Интерфейс и шаги полностью соответствуют боевому режиму.</CardContent>
          </Card>
        ))}
      </div>
      <div className="flex flex-wrap gap-3">
        <Link href="/auth/register?demo=true">
          <Button>Начать демо</Button>
        </Link>
        <Link href="/pricing">
          <Button variant="outline">Посмотреть тарифы</Button>
        </Link>
      </div>
    </MarketingShell>
  );
}
