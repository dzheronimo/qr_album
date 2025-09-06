import { Metadata } from 'next';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { QrCode, HelpCircle, MessageCircle, Mail, BookOpen, Play } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Помощь и поддержка | StoryQR',
  description: 'Получите помощь по использованию StoryQR. FAQ, инструкции, контакты поддержки.',
  keywords: 'помощь, поддержка, FAQ, инструкции, StoryQR',
};

const faqItems = [
  {
    question: 'Как создать QR-код для альбома?',
    answer: 'Создайте альбом в личном кабинете, добавьте страницы с фото и видео, затем нажмите "Сгенерировать QR-код". QR-код можно скачать в различных форматах.',
  },
  {
    question: 'Можно ли защитить альбом паролем?',
    answer: 'Да, при создании страницы вы можете установить PIN-код для доступа к контенту. Это обеспечивает приватность ваших воспоминаний.',
  },
  {
    question: 'Какие форматы файлов поддерживаются?',
    answer: 'Мы поддерживаем все популярные форматы: JPG, PNG, GIF для фото и MP4, MOV, AVI для видео. Максимальный размер файла - 100 МБ.',
  },
  {
    question: 'Как печатать QR-коды на наклейках?',
    answer: 'В разделе "Печать" выберите шаблон наклеек, загрузите QR-код и настройте параметры печати. Мы интегрированы с сервисами печати для удобства.',
  },
  {
    question: 'Можно ли отслеживать просмотры?',
    answer: 'Да, в разделе "Аналитика" вы можете видеть статистику просмотров, популярные страницы и географию ваших зрителей.',
  },
  {
    question: 'Как работает демо-режим?',
    answer: 'Демо-режим позволяет попробовать основные функции без регистрации. Создайте тестовый альбом и посмотрите, как работает платформа.',
  },
];

const helpSections = [
  {
    title: 'Быстрый старт',
    description: 'Начните работу с StoryQR за 5 минут',
    icon: Play,
    href: '/demo',
  },
  {
    title: 'Документация',
    description: 'Подробные инструкции и руководства',
    icon: BookOpen,
    href: '/docs',
  },
  {
    title: 'Связаться с нами',
    description: 'Получите персональную помощь',
    icon: MessageCircle,
    href: '/contact',
  },
];

export default function HelpPage() {
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
            <HelpCircle className="h-8 w-8 text-primary" />
          </div>
          <h1 className="text-4xl font-bold mb-4">Помощь и поддержка</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Найдем ответы на ваши вопросы и поможем максимально эффективно использовать StoryQR
          </p>
        </div>

        {/* Help Sections */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {helpSections.map((section, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center space-x-3">
                  <section.icon className="h-6 w-6 text-primary" />
                  <CardTitle className="text-lg">{section.title}</CardTitle>
                </div>
                <CardDescription>{section.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild className="w-full">
                  <Link href={section.href}>Перейти</Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-8">Часто задаваемые вопросы</h2>
          <div className="space-y-6">
            {faqItems.map((item, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="text-lg">{item.question}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{item.answer}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Contact Section */}
        <div className="max-w-2xl mx-auto mt-16 text-center">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-center space-x-2">
                <Mail className="h-5 w-5" />
                <span>Не нашли ответ?</span>
              </CardTitle>
              <CardDescription>
                Свяжитесь с нашей службой поддержки
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button asChild variant="outline">
                  <a href="mailto:support@storyqr.ru">
                    <Mail className="h-4 w-4 mr-2" />
                    support@storyqr.ru
                  </a>
                </Button>
                <Button asChild variant="outline">
                  <a href="https://t.me/storyqr_support" target="_blank" rel="noopener noreferrer">
                    <MessageCircle className="h-4 w-4 mr-2" />
                    Telegram
                  </a>
                </Button>
              </div>
              <p className="text-sm text-muted-foreground">
                Обычно отвечаем в течение 24 часов
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
