import { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, X, Zap, Crown } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Тарифы',
  description: 'Выберите подходящий тариф для создания интерактивных альбомов с QR-кодами.',
};

const plans = [
  {
    name: 'Бесплатно',
    description: 'Идеально для начала работы',
    price: 0,
    period: '',
    icon: Zap,
    popular: false,
    features: [
      { name: 'Неограниченные альбомы', included: true },
      { name: 'До 50 страниц в альбоме', included: true },
      { name: 'До 100 медиа файлов', included: true },
      { name: '5 ГБ хранилища', included: true },
      { name: 'Базовая аналитика', included: true },
      { name: 'QR-коды в PNG/SVG', included: true },
      { name: 'Печать наклеек', included: true },
      { name: 'Кастомные QR-коды', included: false },
      { name: 'Расширенная аналитика', included: false },
      { name: 'API доступ', included: false },
      { name: 'Приоритетная поддержка', included: false },
    ],
    cta: 'Начать бесплатно',
    href: '/auth/register',
  },
  {
    name: 'Pro',
    description: 'Для профессионалов и бизнеса',
    price: 990,
    period: '/мес',
    icon: Crown,
    popular: true,
    features: [
      { name: 'Неограниченные альбомы', included: true },
      { name: 'Неограниченные страницы', included: true },
      { name: 'Неограниченные медиа файлы', included: true },
      { name: '100 ГБ хранилища', included: true },
      { name: 'Расширенная аналитика', included: true },
      { name: 'QR-коды в PNG/SVG', included: true },
      { name: 'Печать наклеек', included: true },
      { name: 'Кастомные QR-коды', included: true },
      { name: 'API доступ', included: true },
      { name: 'Приоритетная поддержка', included: true },
      { name: 'Экспорт данных', included: true },
    ],
    cta: 'Выбрать Pro',
    href: '/auth/register?plan=pro',
  },
];

const faqs = [
  {
    question: 'Могу ли я изменить тариф в любое время?',
    answer: 'Да, вы можете изменить тариф в любое время. При переходе на более высокий тариф изменения вступают в силу немедленно, при понижении - в конце текущего периода.',
  },
  {
    question: 'Что происходит с моими данными при отмене подписки?',
    answer: 'Ваши данные остаются доступными в течение 30 дней после отмены. После этого они будут удалены, если вы не возобновите подписку.',
  },
  {
    question: 'Есть ли ограничения на размер файлов?',
    answer: 'Максимальный размер одного файла - 100 МБ для изображений и 500 МБ для видео. Эти ограничения действуют для всех тарифов.',
  },
  {
    question: 'Поддерживается ли API?',
    answer: 'API доступен только для тарифа Pro. Он позволяет интегрировать StoryQR с вашими приложениями и автоматизировать создание альбомов.',
  },
  {
    question: 'Можно ли использовать StoryQR для коммерческих целей?',
    answer: 'Да, вы можете использовать StoryQR для любых целей, включая коммерческие. Мы рекомендуем тариф Pro для бизнес-использования.',
  },
  {
    question: 'Как работает печать наклеек?',
    answer: 'Вы можете создать PDF с QR-кодами для печати на наклейках. Поддерживаются различные размеры: 35мм и 50мм с настройкой сетки.',
  },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded bg-primary" />
            <span className="text-xl font-bold">StoryQR</span>
          </Link>
          <nav className="hidden md:flex items-center space-x-6">
            <Link href="/" className="text-sm font-medium hover:text-primary">
              Главная
            </Link>
            <Link href="/help" className="text-sm font-medium hover:text-primary">
              Помощь
            </Link>
            <Link href="/auth/login">
              <Button variant="ghost">Войти</Button>
            </Link>
            <Link href="/auth/register">
              <Button>Начать бесплатно</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="container">
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="text-4xl font-bold tracking-tight sm:text-6xl mb-6">
              Простые и прозрачные тарифы
            </h1>
            <p className="text-lg text-muted-foreground mb-8">
              Начните бесплатно, переходите на Pro когда будете готовы к расширенным возможностям.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-20">
        <div className="container">
          <div className="grid gap-8 md:grid-cols-2 max-w-4xl mx-auto">
            {plans.map((plan) => (
              <Card key={plan.name} className={`relative ${plan.popular ? 'border-primary shadow-lg' : ''}`}>
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-primary text-primary-foreground">
                      Популярный
                    </Badge>
                  </div>
                )}
                <CardHeader className="text-center">
                  <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <plan.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <CardDescription className="text-base">
                    {plan.description}
                  </CardDescription>
                  <div className="mt-4">
                    <span className="text-4xl font-bold">
                      ₽{plan.price}
                    </span>
                    <span className="text-muted-foreground">{plan.period}</span>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  <ul className="space-y-3">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-center">
                        {feature.included ? (
                          <CheckCircle className="mr-3 h-5 w-5 text-green-500 flex-shrink-0" />
                        ) : (
                          <X className="mr-3 h-5 w-5 text-muted-foreground flex-shrink-0" />
                        )}
                        <span className={`text-sm ${!feature.included ? 'text-muted-foreground' : ''}`}>
                          {feature.name}
                        </span>
                      </li>
                    ))}
                  </ul>
                  <Link href={plan.href} className="block">
                    <Button 
                      className="w-full" 
                      variant={plan.popular ? 'default' : 'outline'}
                    >
                      {plan.cta}
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-muted/30">
        <div className="container">
          <div className="mx-auto max-w-3xl">
            <h2 className="text-3xl font-bold text-center mb-12">
              Часто задаваемые вопросы
            </h2>
            <div className="space-y-8">
              {faqs.map((faq, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="text-lg">{faq.question}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">{faq.answer}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
              Готовы начать?
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Создайте свой первый интерактивный альбом уже сегодня.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Link href="/auth/register">
                <Button size="lg">
                  Начать бесплатно
                </Button>
              </Link>
              <Link href="/help">
                <Button variant="outline" size="lg">
                  Задать вопрос
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12">
        <div className="container">
          <div className="grid gap-8 md:grid-cols-4">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="h-6 w-6 rounded bg-primary" />
                <span className="font-bold">StoryQR</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Создавайте интерактивные альбомы с QR-кодами.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Продукт</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/" className="text-muted-foreground hover:text-foreground">Главная</Link></li>
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
          <div className="mt-8 pt-8 border-t text-center text-sm text-muted-foreground">
            © 2024 StoryQR. Все права защищены.
          </div>
        </div>
      </footer>
    </div>
  );
}
