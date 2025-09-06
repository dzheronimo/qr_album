import { Metadata } from 'next';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { QrCode, Shield, Mail, Calendar } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Политика конфиденциальности | StoryQR',
  description: 'Политика конфиденциальности StoryQR. Как мы собираем, используем и защищаем ваши персональные данные.',
  keywords: 'политика конфиденциальности, персональные данные, GDPR, защита данных, StoryQR',
};

const sections = [
  {
    title: '1. Общие положения',
    content: [
      'Настоящая Политика конфиденциальности определяет порядок обработки персональных данных пользователей сервиса StoryQR (далее — «Сервис»).',
      'Используя Сервис, вы соглашаетесь с условиями настоящей Политики конфиденциальности.',
      'Если вы не согласны с условиями настоящей Политики, пожалуйста, не используйте Сервис.',
    ],
  },
  {
    title: '2. Какие данные мы собираем',
    content: [
      'Персональные данные, которые вы предоставляете при регистрации: имя, email, пароль.',
      'Данные, которые вы загружаете в Сервис: фотографии, видео, тексты, описания альбомов.',
      'Технические данные: IP-адрес, тип браузера, операционная система, время посещения.',
      'Данные об использовании Сервиса: просмотры страниц, время сессий, действия пользователя.',
    ],
  },
  {
    title: '3. Как мы используем ваши данные',
    content: [
      'Для предоставления и улучшения функциональности Сервиса.',
      'Для создания и управления вашими альбомами и QR-кодами.',
      'Для обеспечения безопасности и предотвращения мошенничества.',
      'Для связи с вами по вопросам использования Сервиса.',
      'Для аналитики и улучшения пользовательского опыта.',
    ],
  },
  {
    title: '4. Передача данных третьим лицам',
    content: [
      'Мы не продаем и не передаем ваши персональные данные третьим лицам без вашего согласия.',
      'Мы можем передавать данные поставщикам услуг, которые помогают нам в работе Сервиса (хостинг, аналитика, платежи).',
      'Мы можем раскрыть данные по требованию правоохранительных органов в соответствии с действующим законодательством.',
    ],
  },
  {
    title: '5. Защита данных',
    content: [
      'Мы используем современные методы шифрования для защиты ваших данных.',
      'Доступ к персональным данным имеют только уполномоченные сотрудники.',
      'Мы регулярно обновляем системы безопасности и проводим аудиты.',
      'Ваши пароли хранятся в зашифрованном виде.',
    ],
  },
  {
    title: '6. Ваши права',
    content: [
      'Право на доступ к вашим персональным данным.',
      'Право на исправление неточных данных.',
      'Право на удаление ваших данных (право на забвение).',
      'Право на ограничение обработки данных.',
      'Право на портабельность данных.',
      'Право на возражение против обработки данных.',
    ],
  },
  {
    title: '7. Cookies и аналогичные технологии',
    content: [
      'Мы используем cookies для улучшения функциональности Сервиса.',
      'Cookies помогают нам запоминать ваши настройки и предпочтения.',
      'Вы можете отключить cookies в настройках браузера, но это может повлиять на функциональность Сервиса.',
    ],
  },
  {
    title: '8. Хранение данных',
    content: [
      'Мы храним ваши данные до тех пор, пока вы используете Сервис.',
      'После удаления аккаунта мы удаляем ваши персональные данные в течение 30 дней.',
      'Некоторые данные могут храниться дольше в соответствии с требованиями законодательства.',
    ],
  },
  {
    title: '9. Изменения в Политике',
    content: [
      'Мы можем обновлять настоящую Политику конфиденциальности.',
      'О существенных изменениях мы уведомим вас по email или через Сервис.',
      'Продолжение использования Сервиса после изменений означает ваше согласие с новой Политикой.',
    ],
  },
  {
    title: '10. Контактная информация',
    content: [
      'По вопросам обработки персональных данных обращайтесь к нам:',
      'Email: privacy@storyqr.ru',
      'Адрес: Россия, г. Москва',
      'Мы ответим на ваши вопросы в течение 30 дней.',
    ],
  },
];

export default function PrivacyPage() {
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
            <Shield className="h-8 w-8 text-primary" />
          </div>
          <h1 className="text-4xl font-bold mb-4">Политика конфиденциальности</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-6">
            Мы серьезно относимся к защите ваших персональных данных и соблюдаем все требования законодательства
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
                <span>Вопросы по конфиденциальности?</span>
              </CardTitle>
              <CardDescription>
                Свяжитесь с нами, если у вас есть вопросы по обработке персональных данных
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button asChild>
                  <a href="mailto:privacy@storyqr.ru">
                    <Mail className="h-4 w-4 mr-2" />
                    privacy@storyqr.ru
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
