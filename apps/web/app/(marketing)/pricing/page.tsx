'use client';

import { useState } from 'react';

export const dynamic = 'force-dynamic';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { PricingTable } from '@/components/pricing/PricingTable';
import { CompareTable } from '@/components/pricing/CompareTable';
import { TrialCta } from '@/components/trial/TrialCta';
import { TrialStartModal } from '@/components/trial/TrialStartModal';
import { CheckoutDrawer } from '@/components/checkout/CheckoutDrawer';
import { QrCode, Users, Camera, Share2, ChevronDown, ChevronUp } from 'lucide-react';
import { FAQ_DATA } from '@/lib/constants';
import { BillingPlan } from '@/types';
import { Currency, getCurrencyPreference } from '@/lib/currency';


export default function PricingPage() {
  const [isTrialModalOpen, setIsTrialModalOpen] = useState(false);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<BillingPlan | null>(null);
  const [currency, setCurrency] = useState<Currency>(getCurrencyPreference());
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  const handleStartTrial = () => {
    setIsTrialModalOpen(true);
  };

  const handleTrialSuccess = (trialData: any) => {
    // Редирект на dashboard или показать успех
    console.log('Trial started:', trialData);
  };

  const handlePlanSelect = (plan: BillingPlan) => {
    setSelectedPlan(plan);
    setIsCheckoutOpen(true);
  };

  const toggleFaq = (index: number) => {
    setExpandedFaq(expandedFaq === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <QrCode className="h-8 w-8 text-primary" />
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
        <div className="md:hidden border-t py-2">
          <div className="flex items-center gap-3 overflow-x-auto text-sm">
            <Link href="/" className="whitespace-nowrap text-muted-foreground hover:text-foreground">Главная</Link>
            <Link href="/help" className="whitespace-nowrap text-muted-foreground hover:text-foreground">Помощь</Link>
            <Link href="/auth/login" className="whitespace-nowrap text-muted-foreground hover:text-foreground">Войти</Link>
            <Link href="/auth/register" className="whitespace-nowrap text-primary font-medium">Начать</Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="container">
          <div className="mx-auto max-w-4xl text-center">
            <h1 className="text-4xl font-bold tracking-tight sm:text-6xl mb-6">
              Соберите все фото и видео гостей одним QR
            </h1>
            <p className="text-lg text-muted-foreground mb-8">
              Без приложений. Разовая оплата за событие
            </p>
            
            {/* Буллеты */}
            <div className="flex flex-wrap justify-center gap-6 mb-8">
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-primary" />
                <span className="text-sm">Безлим гости и загрузки</span>
              </div>
              <div className="flex items-center gap-2">
                <Camera className="h-5 w-5 text-primary" />
                <span className="text-sm">Аудио-гостевая</span>
              </div>
              <div className="flex items-center gap-2">
                <Share2 className="h-5 w-5 text-primary" />
                <span className="text-sm">Живое слайдшоу</span>
              </div>
              <div className="flex items-center gap-2">
                <QrCode className="h-5 w-5 text-primary" />
                <span className="text-sm">Красивые QR-карточки</span>
              </div>
            </div>

            {/* CTA кнопка */}
            <Button size="lg" onClick={handleStartTrial}>
              Начать бесплатно на 7 дней
            </Button>
          </div>
        </div>
      </section>

      {/* Trial CTA */}
      <section className="py-12">
        <div className="container">
          <div className="max-w-md mx-auto">
            <TrialCta onStartTrial={handleStartTrial} />
          </div>
        </div>
      </section>

      {/* Pricing Table */}
      <section className="py-20">
        <div className="container">
          <PricingTable onPlanSelect={handlePlanSelect} initialCurrency={currency} onCurrencyChange={setCurrency} />
        </div>
      </section>

      {/* Comparison Table */}
      <section className="py-20 bg-muted/30">
        <div className="container">
          <CompareTable />
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20">
        <div className="container">
          <div className="mx-auto max-w-3xl">
            <h2 className="text-3xl font-bold text-center mb-12">
              Часто задаваемые вопросы
            </h2>
            <div className="space-y-4">
              {FAQ_DATA.map((faq, index) => (
                <Card key={index}>
                  <CardHeader 
                    className="cursor-pointer"
                    onClick={() => toggleFaq(index)}
                  >
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{faq.question}</CardTitle>
                      {expandedFaq === index ? (
                        <ChevronUp className="h-5 w-5 text-muted-foreground" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-muted-foreground" />
                      )}
                    </div>
                  </CardHeader>
                  {expandedFaq === index && (
                    <CardContent>
                      <p className="text-muted-foreground">{faq.answer}</p>
                    </CardContent>
                  )}
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary/5">
        <div className="container">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
              Готовы начать?
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              Создайте свой первый интерактивный альбом уже сегодня.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button size="lg" onClick={handleStartTrial}>
                Начать бесплатно
              </Button>
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

      {/* Modals */}
      <TrialStartModal
        isOpen={isTrialModalOpen}
        onClose={() => setIsTrialModalOpen(false)}
        onSuccess={handleTrialSuccess}
      />

      <CheckoutDrawer
        isOpen={isCheckoutOpen}
        onClose={() => setIsCheckoutOpen(false)}
        plan={selectedPlan}
        currency={currency}
      />
    </div>
  );
}