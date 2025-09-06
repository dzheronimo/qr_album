import { Metadata } from 'next';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  QrCode, 
  Camera, 
  Shield, 
  BarChart3, 
  Printer, 
  Smartphone, 
  Users, 
  Zap,
  ArrowRight,
  CheckCircle,
  Star
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'Возможности StoryQR | Функции платформы',
  description: 'Узнайте о всех возможностях StoryQR: создание альбомов, QR-коды, аналитика, печать и многое другое.',
  keywords: 'возможности, функции, QR-коды, альбомы, аналитика, печать, StoryQR',
};

const mainFeatures = [
  {
    icon: Camera,
    title: 'Создание альбомов',
    description: 'Создавайте неограниченные альбомы с фото и видео. Организуйте воспоминания по событиям, датам или темам.',
    features: [
      'Неограниченное количество альбомов',
      'Поддержка фото и видео',
      'Организация по категориям',
      'Быстрая загрузка файлов',
    ],
  },
  {
    icon: QrCode,
    title: 'QR-коды',
    description: 'Генерируйте уникальные QR-коды для каждого альбома. Скачивайте в различных форматах для печати.',
    features: [
      'Уникальные QR-коды',
      'Различные форматы (PNG, SVG)',
      'Настраиваемые размеры',
      'Быстрая генерация',
    ],
  },
  {
    icon: Shield,
    title: 'Безопасность',
    description: 'Защищайте свои альбомы PIN-кодами. Контролируйте доступ к личному контенту.',
    features: [
      'PIN-код защита',
      'Приватные альбомы',
      'Контроль доступа',
      'Безопасное хранение',
    ],
  },
  {
    icon: BarChart3,
    title: 'Аналитика',
    description: 'Отслеживайте просмотры ваших альбомов. Получайте детальную статистику и отчеты.',
    features: [
      'Статистика просмотров',
      'География зрителей',
      'Популярные страницы',
      'Экспорт отчетов',
    ],
  },
  {
    icon: Printer,
    title: 'Печать',
    description: 'Печатайте QR-коды на наклейках и открытках. Интеграция с сервисами печати.',
    features: [
      'Печать наклеек',
      'Различные форматы',
      'Интеграция с типографиями',
      'Быстрая доставка',
    ],
  },
  {
    icon: Users,
    title: 'Совместная работа',
    description: 'Приглашайте друзей и семью к созданию альбомов. Работайте вместе над воспоминаниями.',
    features: [
      'Совместное редактирование',
      'Приглашения по email',
      'Роли и права доступа',
      'Комментарии и обсуждения',
    ],
  },
];

const additionalFeatures = [
  {
    icon: Smartphone,
    title: 'Мобильная версия',
    description: 'Полнофункциональная мобильная версия для iOS и Android',
  },
  {
    icon: Zap,
    title: 'Быстрая загрузка',
    description: 'Оптимизированная загрузка файлов с прогресс-баром',
  },
  {
    icon: Star,
    title: 'Избранное',
    description: 'Сохраняйте любимые альбомы в избранное для быстрого доступа',
  },
];

const pricingFeatures = [
  {
    plan: 'Бесплатный',
    price: '0₽',
    period: 'навсегда',
    features: [
      '3 альбома',
      'Неограниченные страницы',
      'Базовые QR-коды',
      'Аналитика просмотров',
      'Поддержка по email',
    ],
    cta: 'Начать бесплатно',
    href: '/auth/register',
  },
  {
    plan: 'Pro',
    price: '990₽',
    period: 'в месяц',
    features: [
      'Неограниченные альбомы',
      'Приоритетная поддержка',
      'Расширенная аналитика',
      'Печать наклеек',
      'Совместная работа',
      'API доступ',
    ],
    cta: 'Попробовать Pro',
    href: '/pricing',
    popular: true,
  },
];

export default function FeaturesPage() {
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
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6">Возможности StoryQR</h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
            Полный набор инструментов для создания интерактивных альбомов с QR-кодами. 
            От простых воспоминаний до профессиональных проектов.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/auth/register">
                Начать бесплатно
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/demo">Попробовать демо</Link>
            </Button>
          </div>
        </div>

        {/* Main Features */}
        <div className="max-w-6xl mx-auto mb-16">
          <h2 className="text-3xl font-bold text-center mb-12">Основные возможности</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {mainFeatures.map((feature, index) => (
              <Card key={index} className="h-full">
                <CardHeader>
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-primary/10 rounded-lg mb-4">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                  <CardDescription className="text-base">{feature.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {feature.features.map((item, itemIndex) => (
                      <li key={itemIndex} className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                        <span className="text-sm">{item}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Additional Features */}
        <div className="max-w-4xl mx-auto mb-16">
          <h2 className="text-3xl font-bold text-center mb-12">Дополнительные возможности</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {additionalFeatures.map((feature, index) => (
              <Card key={index} className="text-center">
                <CardHeader>
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-primary/10 rounded-lg mb-4 mx-auto">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>

        {/* Pricing Comparison */}
        <div className="max-w-4xl mx-auto mb-16">
          <h2 className="text-3xl font-bold text-center mb-12">Выберите подходящий план</h2>
          <div className="grid md:grid-cols-2 gap-8">
            {pricingFeatures.map((plan, index) => (
              <Card key={index} className={`relative ${plan.popular ? 'border-primary shadow-lg' : ''}`}>
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <span className="bg-primary text-primary-foreground px-3 py-1 rounded-full text-sm font-medium">
                      Популярный
                    </span>
                  </div>
                )}
                <CardHeader className="text-center">
                  <CardTitle className="text-2xl">{plan.plan}</CardTitle>
                  <div className="text-4xl font-bold">
                    {plan.price}
                    <span className="text-lg font-normal text-muted-foreground">/{plan.period}</span>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <ul className="space-y-3">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button 
                    className="w-full" 
                    variant={plan.popular ? 'default' : 'outline'}
                    asChild
                  >
                    <Link href={plan.href}>{plan.cta}</Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="max-w-2xl mx-auto text-center">
          <Card className="bg-primary/5 border-primary/20">
            <CardHeader>
              <CardTitle className="text-2xl">Готовы начать?</CardTitle>
              <CardDescription className="text-base">
                Присоединяйтесь к тысячам пользователей, которые уже создают интерактивные альбомы с StoryQR
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button size="lg" asChild>
                  <Link href="/auth/register">
                    Создать аккаунт
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button size="lg" variant="outline" asChild>
                  <Link href="/contact">Связаться с нами</Link>
                </Button>
              </div>
              <p className="text-sm text-muted-foreground">
                Регистрация займет менее минуты • Без кредитной карты
              </p>
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
