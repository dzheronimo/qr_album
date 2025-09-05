import { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  QrCode, 
  Camera, 
  Share2, 
  BarChart3, 
  Smartphone, 
  Users, 
  Zap,
  CheckCircle,
  ArrowRight,
  Star
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'StoryQR - Создавайте интерактивные альбомы с QR-кодами',
  description: 'Создавайте красивые цифровые альбомы, делитесь ими через QR-коды и отслеживайте взаимодействие с контентом. Простой и удобный способ поделиться воспоминаниями.',
  openGraph: {
    title: 'StoryQR - Создавайте интерактивные альбомы с QR-кодами',
    description: 'Создавайте красивые цифровые альбомы, делитесь ими через QR-коды и отслеживайте взаимодействие с контентом.',
    images: ['/og-image.jpg'],
  },
};

const features = [
  {
    icon: QrCode,
    title: 'QR-коды для каждого контента',
    description: 'Создавайте уникальные QR-коды для каждой страницы альбома и делитесь ими в реальном мире.',
  },
  {
    icon: Camera,
    title: 'Мультимедиа контент',
    description: 'Загружайте фото, видео и аудио файлы. Поддерживаются все популярные форматы.',
  },
  {
    icon: Share2,
    title: 'Простое распространение',
    description: 'Печатайте QR-коды на наклейках, визитках или любых других материалах.',
  },
  {
    icon: BarChart3,
    title: 'Аналитика просмотров',
    description: 'Отслеживайте, кто и когда просматривал ваш контент с подробной статистикой.',
  },
  {
    icon: Smartphone,
    title: 'Мобильная оптимизация',
    description: 'Ваши альбомы отлично выглядят на всех устройствах и загружаются быстро.',
  },
  {
    icon: Users,
    title: 'Контроль доступа',
    description: 'Настройте видимость контента: публичный, по ссылке или с PIN-кодом.',
  },
];

const pricingFeatures = [
  'Неограниченные альбомы',
  'До 50 страниц в альбоме',
  'До 100 медиа файлов',
  '5 ГБ хранилища',
  'Базовая аналитика',
  'QR-коды в PNG/SVG',
  'Печать наклеек',
];

const proFeatures = [
  'Все из бесплатного тарифа',
  'Неограниченные страницы',
  'Неограниченные медиа файлы',
  '100 ГБ хранилища',
  'Расширенная аналитика',
  'Кастомные QR-коды',
  'Приоритетная поддержка',
  'API доступ',
];

const testimonials = [
  {
    name: 'Анна Петрова',
    role: 'Фотограф',
    content: 'StoryQR помог мне создать интерактивные портфолио для клиентов. Теперь они могут легко поделиться своими фотографиями.',
    rating: 5,
  },
  {
    name: 'Михаил Соколов',
    role: 'Маркетолог',
    content: 'Использую для создания интерактивных каталогов продукции. Клиенты сканируют QR и сразу видят подробную информацию.',
    rating: 5,
  },
  {
    name: 'Елена Козлова',
    role: 'Учитель',
    content: 'Создаю интерактивные учебные материалы. Студенты сканируют QR-коды и получают доступ к дополнительным ресурсам.',
    rating: 5,
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center space-x-2">
            <QrCode className="h-8 w-8 text-primary" />
            <span className="text-xl font-bold">StoryQR</span>
          </div>
          <nav className="hidden md:flex items-center space-x-6">
            <Link href="/pricing" className="text-sm font-medium hover:text-primary">
              Тарифы
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
      <section className="py-20 md:py-32">
        <div className="container">
          <div className="mx-auto max-w-4xl text-center">
            <Badge variant="secondary" className="mb-4">
              <Zap className="mr-1 h-3 w-3" />
              Новый способ делиться воспоминаниями
            </Badge>
            <h1 className="mb-6 text-4xl font-bold tracking-tight sm:text-6xl">
              Создавайте интерактивные альбомы с{' '}
              <span className="text-primary">QR-кодами</span>
            </h1>
            <p className="mb-8 text-lg text-muted-foreground sm:text-xl">
              Превратите ваши фото и видео в интерактивный опыт. Создавайте QR-коды, 
              печатайте наклейки и делитесь воспоминаниями в реальном мире.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Link href="/auth/register">
                <Button size="lg" className="w-full sm:w-auto">
                  Создать первый альбом
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/demo">
                <Button variant="outline" size="lg" className="w-full sm:w-auto">
                  Посмотреть демо
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Все необходимое для создания интерактивного контента
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Простой и мощный инструмент для создания, распространения и анализа вашего контента.
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => (
              <Card key={index} className="text-center">
                <CardHeader>
                  <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 bg-muted/30">
        <div className="container">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Простые и прозрачные тарифы
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Начните бесплатно, переходите на Pro когда будете готовы.
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-2 max-w-4xl mx-auto">
            {/* Free Plan */}
            <Card>
              <CardHeader>
                <CardTitle>Бесплатно</CardTitle>
                <CardDescription>
                  Идеально для начала работы
                </CardDescription>
                <div className="text-3xl font-bold">₽0</div>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-2">
                  {pricingFeatures.map((feature, index) => (
                    <li key={index} className="flex items-center">
                      <CheckCircle className="mr-2 h-4 w-4 text-green-500" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link href="/auth/register" className="block">
                  <Button className="w-full">Начать бесплатно</Button>
                </Link>
              </CardContent>
            </Card>

            {/* Pro Plan */}
            <Card className="border-primary">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Pro</CardTitle>
                  <Badge>Популярный</Badge>
                </div>
                <CardDescription>
                  Для профессионалов и бизнеса
                </CardDescription>
                <div className="text-3xl font-bold">₽990<span className="text-sm font-normal">/мес</span></div>
              </CardHeader>
              <CardContent className="space-y-4">
                <ul className="space-y-2">
                  {proFeatures.map((feature, index) => (
                    <li key={index} className="flex items-center">
                      <CheckCircle className="mr-2 h-4 w-4 text-green-500" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link href="/auth/register?plan=pro" className="block">
                  <Button className="w-full">Выбрать Pro</Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20">
        <div className="container">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Что говорят наши пользователи
            </h2>
          </div>
          <div className="grid gap-8 md:grid-cols-3">
            {testimonials.map((testimonial, index) => (
              <Card key={index}>
                <CardContent className="pt-6">
                  <div className="flex items-center mb-4">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-sm text-muted-foreground mb-4">
                    "{testimonial.content}"
                  </p>
                  <div>
                    <p className="font-semibold">{testimonial.name}</p>
                    <p className="text-sm text-muted-foreground">{testimonial.role}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary text-primary-foreground">
        <div className="container">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
              Готовы начать?
            </h2>
            <p className="text-lg mb-8 opacity-90">
              Создайте свой первый интерактивный альбом уже сегодня.
            </p>
            <Link href="/auth/register">
              <Button size="lg" variant="secondary">
                Создать альбом бесплатно
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12">
        <div className="container">
          <div className="grid gap-8 md:grid-cols-4">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <QrCode className="h-6 w-6 text-primary" />
                <span className="font-bold">StoryQR</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Создавайте интерактивные альбомы с QR-кодами.
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
          <div className="mt-8 pt-8 border-t text-center text-sm text-muted-foreground">
            © 2024 StoryQR. Все права защищены.
          </div>
        </div>
      </footer>
    </div>
  );
}
