import { Metadata } from 'next';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { QrCode, Play, ArrowRight, CheckCircle, Smartphone, Camera, Share2 } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Демо StoryQR | Попробуйте бесплатно',
  description: 'Попробуйте StoryQR в действии. Создайте тестовый альбом и посмотрите, как работают QR-коды.',
  robots: 'noindex,follow', // Не индексировать демо-страницу
};

const demoSteps = [
  {
    step: 1,
    title: 'Создайте альбом',
    description: 'Добавьте название и описание для вашего альбома воспоминаний',
    icon: Camera,
  },
  {
    step: 2,
    title: 'Добавьте контент',
    description: 'Загрузите фото и видео, создайте страницы с историями',
    icon: Smartphone,
  },
  {
    step: 3,
    title: 'Получите QR-код',
    description: 'Сгенерируйте QR-код и поделитесь им с друзьями',
    icon: Share2,
  },
];

const demoFeatures = [
  'Создание неограниченных альбомов',
  'Загрузка фото и видео',
  'Генерация QR-кодов',
  'Защита PIN-кодом',
  'Аналитика просмотров',
  'Печать наклеек',
];

export default function DemoPage() {
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
          <div className="inline-flex items-center justify-center w-20 h-20 bg-primary/10 rounded-full mb-8">
            <Play className="h-10 w-10 text-primary" />
          </div>
          <h1 className="text-5xl font-bold mb-6">Попробуйте StoryQR</h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
            Создайте тестовый альбом и посмотрите, как легко превратить ваши воспоминания в интерактивные QR-коды
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link href="/auth/register?demo=true">
                Начать демо
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/help">Узнать больше</Link>
            </Button>
          </div>
        </div>

        {/* Demo Steps */}
        <div className="max-w-4xl mx-auto mb-16">
          <h2 className="text-3xl font-bold text-center mb-12">Как это работает</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {demoSteps.map((step, index) => (
              <Card key={index} className="relative">
                <CardHeader className="text-center">
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-primary/10 rounded-full mb-4 mx-auto">
                    <step.icon className="h-6 w-6 text-primary" />
                  </div>
                  <div className="absolute -top-4 -left-4 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-bold">
                    {step.step}
                  </div>
                  <CardTitle className="text-xl">{step.title}</CardTitle>
                  <CardDescription className="text-base">{step.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>

        {/* Demo Features */}
        <div className="max-w-4xl mx-auto mb-16">
          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">Что вы сможете попробовать</CardTitle>
              <CardDescription>
                Полный доступ ко всем функциям платформы
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                {demoFeatures.map((feature, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Demo CTA */}
        <div className="max-w-2xl mx-auto text-center">
          <Card className="bg-primary/5 border-primary/20">
            <CardHeader>
              <CardTitle className="text-2xl">Готовы начать?</CardTitle>
              <CardDescription className="text-base">
                Создайте бесплатный аккаунт и начните создавать свои первые QR-альбомы
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
                  <Link href="/auth/login">Уже есть аккаунт?</Link>
                </Button>
              </div>
              <p className="text-sm text-muted-foreground">
                Регистрация займет менее минуты
              </p>
            </CardContent>
          </Card>
        </div>

        {/* FAQ Section */}
        <div className="max-w-3xl mx-auto mt-16">
          <h2 className="text-2xl font-bold text-center mb-8">Частые вопросы о демо</h2>
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Нужна ли регистрация для демо?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Да, но регистрация бесплатная и займет всего минуту. Это необходимо для сохранения ваших тестовых альбомов.
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Сколько альбомов можно создать в демо?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  В бесплатном тарифе вы можете создать до 3 альбомов с неограниченным количеством страниц в каждом.
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Можно ли скачать QR-коды в демо?</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Конечно! Вы можете скачать QR-коды в различных форматах (PNG, SVG) и сразу использовать их.
                </p>
              </CardContent>
            </Card>
          </div>
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
