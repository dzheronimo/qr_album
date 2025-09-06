import { Metadata } from 'next';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { QrCode, FileText, Mail, Calendar } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Условия использования | StoryQR',
  description: 'Условия использования сервиса StoryQR. Правила и ограничения использования платформы.',
  keywords: 'условия использования, правила, ограничения, StoryQR, пользовательское соглашение',
};

const sections = [
  {
    title: '1. Общие положения',
    content: [
      'Настоящие Условия использования (далее — «Условия») регулируют отношения между пользователями и сервисом StoryQR (далее — «Сервис»).',
      'Используя Сервис, вы подтверждаете, что прочитали, поняли и согласились соблюдать настоящие Условия.',
      'Если вы не согласны с какими-либо положениями настоящих Условий, пожалуйста, не используйте Сервис.',
    ],
  },
  {
    title: '2. Описание сервиса',
    content: [
      'StoryQR — это платформа для создания интерактивных альбомов с QR-кодами.',
      'Сервис позволяет пользователям загружать фото и видео, создавать альбомы, генерировать QR-коды и делиться контентом.',
      'Мы предоставляем различные тарифные планы с разными возможностями и ограничениями.',
    ],
  },
  {
    title: '3. Регистрация и аккаунт',
    content: [
      'Для использования Сервиса необходимо создать аккаунт, предоставив достоверную информацию.',
      'Вы несете ответственность за сохранность пароля и всех действий, совершенных под вашим аккаунтом.',
      'Один человек может иметь только один аккаунт.',
      'Мы оставляем за собой право приостановить или удалить аккаунт при нарушении настоящих Условий.',
    ],
  },
  {
    title: '4. Правила использования',
    content: [
      'Вы обязуетесь использовать Сервис только в законных целях.',
      'Запрещается загружать контент, нарушающий авторские права, содержащий незаконную информацию или вредоносный код.',
      'Запрещается использовать Сервис для спама, фишинга или других мошеннических действий.',
      'Запрещается пытаться взломать, нарушить работу или получить несанкционированный доступ к Сервису.',
    ],
  },
  {
    title: '5. Интеллектуальная собственность',
    content: [
      'Вы сохраняете все права на контент, который загружаете в Сервис.',
      'Предоставляя нам лицензию на использование вашего контента для предоставления Сервиса.',
      'Мы не претендуем на права собственности на ваш контент.',
      'Вы гарантируете, что имеете все необходимые права на загружаемый контент.',
    ],
  },
  {
    title: '6. Платежи и подписки',
    content: [
      'Некоторые функции Сервиса предоставляются на платной основе.',
      'Стоимость подписок указана на странице тарифов и может изменяться с уведомлением.',
      'Платежи взимаются заранее за выбранный период подписки.',
      'Возврат средств возможен в соответствии с политикой возврата.',
    ],
  },
  {
    title: '7. Ограничение ответственности',
    content: [
      'Сервис предоставляется «как есть» без каких-либо гарантий.',
      'Мы не несем ответственности за потерю данных, упущенную выгоду или косвенные убытки.',
      'Наша ответственность ограничена суммой, уплаченной за использование Сервиса за последние 12 месяцев.',
      'Мы не гарантируем бесперебойную работу Сервиса.',
    ],
  },
  {
    title: '8. Приостановка и прекращение',
    content: [
      'Мы можем приостановить или прекратить предоставление Сервиса в любое время.',
      'Вы можете прекратить использование Сервиса в любое время, удалив свой аккаунт.',
      'При нарушении Условий мы можем заблокировать доступ к Сервису.',
      'После прекращения использования ваши данные будут удалены в соответствии с Политикой конфиденциальности.',
    ],
  },
  {
    title: '9. Изменения условий',
    content: [
      'Мы можем изменять настоящие Условия в любое время.',
      'О существенных изменениях мы уведомим пользователей по email или через Сервис.',
      'Продолжение использования Сервиса после изменений означает согласие с новыми Условиями.',
      'Если вы не согласны с изменениями, прекратите использование Сервиса.',
    ],
  },
  {
    title: '10. Применимое право',
    content: [
      'Настоящие Условия регулируются законодательством Российской Федерации.',
      'Все споры разрешаются в судах по месту нахождения компании.',
      'Если какое-либо положение Условий будет признано недействительным, остальные положения остаются в силе.',
    ],
  },
  {
    title: '11. Контактная информация',
    content: [
      'По всем вопросам, связанным с настоящими Условиями, обращайтесь:',
      'Email: legal@storyqr.ru',
      'Адрес: Россия, г. Москва',
      'Мы ответим на ваши вопросы в течение 5 рабочих дней.',
    ],
  },
];

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      {/* Header */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <Link href="/" className="inline-flex items-center space-x-2">
              <QrCode className="h-8 w-8 text-primary" />
              <span className="text-2xl font-bold">StoryQR</span>
            </Link>
            <div className="flex items-center space-x-4">
              <Link href="/auth/login">
                <Button variant="ghost">Войти</Button>
              </Link>
              <Link href="/auth/register">
                <Button>Создать аккаунт</Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-6">
            <FileText className="h-8 w-8 text-primary" />
          </div>
          <h1 className="text-4xl font-bold mb-4">Условия использования</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-6">
            Правила и ограничения использования платформы StoryQR
          </p>
          <div className="flex items-center justify-center space-x-4 text-sm text-muted-foreground">
            <div className="flex items-center space-x-2">
              <Calendar className="h-4 w-4" />
              <span>Последнее обновление: 15 декабря 2024</span>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-4xl mx-auto">
          <div className="space-y-8">
            {sections.map((section, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="text-xl">{section.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {section.content.map((item, itemIndex) => (
                      <li key={itemIndex} className="flex items-start space-x-3">
                        <span className="text-primary font-bold mt-1">•</span>
                        <span className="text-muted-foreground">{item}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Contact Section */}
          <Card className="mt-12 bg-primary/5 border-primary/20">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Mail className="h-5 w-5" />
                <span>Вопросы по условиям?</span>
              </CardTitle>
              <CardDescription>
                Свяжитесь с нами, если у вас есть вопросы по условиям использования
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button asChild>
                  <a href="mailto:legal@storyqr.ru">
                    <Mail className="h-4 w-4 mr-2" />
                    legal@storyqr.ru
                  </a>
                </Button>
                <Button variant="outline" asChild>
                  <Link href="/contact">Связаться с нами</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <Link href="/" className="inline-flex items-center space-x-2 mb-4">
                <QrCode className="h-6 w-6 text-primary" />
                <span className="text-lg font-bold">StoryQR</span>
              </Link>
              <p className="text-sm text-muted-foreground">
                Создавайте интерактивные альбомы с QR-кодами
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Продукт</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/features" className="text-muted-foreground hover:text-foreground">Возможности</Link></li>
                <li><Link href="/pricing" className="text-muted-foreground hover:text-foreground">Тарифы</Link></li>
                <li><Link href="/demo" className="text-muted-foreground hover:text-foreground">Демо</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Поддержка</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/help" className="text-muted-foreground hover:text-foreground">Помощь</Link></li>
                <li><Link href="/docs" className="text-muted-foreground hover:text-foreground">Документация</Link></li>
                <li><Link href="/contact" className="text-muted-foreground hover:text-foreground">Контакты</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Правовая информация</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/legal/privacy" className="text-muted-foreground hover:text-foreground">Конфиденциальность</Link></li>
                <li><Link href="/legal/terms" className="text-muted-foreground hover:text-foreground">Условия использования</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t mt-8 pt-8 text-center text-sm text-muted-foreground">
            <p>&copy; 2024 StoryQR. Все права защищены.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
