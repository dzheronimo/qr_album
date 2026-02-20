import { Metadata } from 'next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MarketingShell } from '@/components/marketing/MarketingShell';

export const metadata: Metadata = {
  title: 'Помощь и поддержка | StoryQR',
  description: 'Центр помощи StoryQR: ответы на популярные вопросы и быстрый старт по созданию QR-альбомов.',
};

const faq = [
  ['Как создать альбом?', 'Откройте кабинет → Альбомы → Создать альбом, заполните название и добавьте страницы.'],
  ['Как поделиться с гостями?', 'Сгенерируйте QR-код страницы и разместите его на карточках или экране события.'],
  ['Какие форматы медиа поддерживаются?', 'Изображения, видео и аудио в популярных форматах.'],
  ['Можно ли ограничить доступ?', 'Да, доступны публичный режим, доступ по ссылке и PIN-защита.'],
  ['Как работает печать QR?', 'В разделе печати можно выбрать макет и получить PDF для типографии или домашней печати.'],
  ['Где посмотреть аналитику?', 'В dashboard доступны просмотры, загрузки и активность по альбомам и страницам.'],
];

export default function HelpPage() {
  return (
    <MarketingShell
      title="Помощь и поддержка"
      subtitle="Краткие инструкции по всем основным сценариям StoryQR"
    >
      <h2 className="text-2xl font-semibold mb-4">Часто задаваемые вопросы</h2>
      <div className="grid gap-4 md:grid-cols-2">
        {faq.map(([question, answer]) => (
          <Card key={question} data-testid="faq-item">
            <CardHeader>
              <CardTitle className="text-lg">{question}</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">{answer}</CardContent>
          </Card>
        ))}
      </div>
    </MarketingShell>
  );
}
