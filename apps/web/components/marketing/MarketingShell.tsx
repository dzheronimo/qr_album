import Link from 'next/link';
import { QrCode } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface MarketingShellProps {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}

export function MarketingShell({ title, subtitle, children }: MarketingShellProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center space-x-2">
            <QrCode className="h-8 w-8 text-primary" />
            <span className="text-xl font-bold">StoryQR</span>
          </Link>
          <nav className="hidden md:flex items-center gap-3">
            <Link href="/features" className="text-sm font-medium hover:text-primary">Возможности</Link>
            <Link href="/pricing" className="text-sm font-medium hover:text-primary">Тарифы</Link>
            <Link href="/help" className="text-sm font-medium hover:text-primary">Помощь</Link>
            <Link href="/auth/login"><Button variant="ghost">Войти</Button></Link>
            <Link href="/auth/register"><Button>Начать</Button></Link>
          </nav>
        </div>
      </header>

      <div className="md:hidden border-t bg-background/95">
        <div className="container flex items-center gap-3 overflow-x-auto py-2 text-sm">
          <Link href="/features" className="whitespace-nowrap text-muted-foreground hover:text-foreground">Возможности</Link>
          <Link href="/pricing" className="whitespace-nowrap text-muted-foreground hover:text-foreground">Тарифы</Link>
          <Link href="/help" className="whitespace-nowrap text-muted-foreground hover:text-foreground">Помощь</Link>
          <Link href="/contact" className="whitespace-nowrap text-muted-foreground hover:text-foreground">Контакты</Link>
          <Link href="/auth/login" className="whitespace-nowrap text-muted-foreground hover:text-foreground">Войти</Link>
          <Link href="/auth/register" className="whitespace-nowrap text-primary font-medium">Начать</Link>
        </div>
      </div>

      <main className="container py-14">
        <div className="mx-auto max-w-4xl">
          <h1 className="text-3xl md:text-4xl font-bold mb-3">{title}</h1>
          <p className="text-muted-foreground mb-8">{subtitle}</p>
          {children}
        </div>
      </main>

      <footer className="border-t py-10 mt-10">
        <div className="container grid gap-4 md:grid-cols-3 text-sm">
          <div className="space-y-2">
            <p className="font-semibold">Продукт</p>
            <div className="flex flex-col gap-1">
              <Link href="/features" className="text-muted-foreground hover:text-foreground">Возможности</Link>
              <Link href="/pricing" className="text-muted-foreground hover:text-foreground">Тарифы</Link>
              <Link href="/demo" className="text-muted-foreground hover:text-foreground">Демо</Link>
            </div>
          </div>
          <div className="space-y-2">
            <p className="font-semibold">Поддержка</p>
            <div className="flex flex-col gap-1">
              <Link href="/help" className="text-muted-foreground hover:text-foreground">Помощь</Link>
              <Link href="/contact" className="text-muted-foreground hover:text-foreground">Контакты</Link>
            </div>
          </div>
          <div className="space-y-2">
            <p className="font-semibold">Право</p>
            <div className="flex flex-col gap-1">
              <Link href="/legal/privacy" className="text-muted-foreground hover:text-foreground">Конфиденциальность</Link>
              <Link href="/legal/terms" className="text-muted-foreground hover:text-foreground">Условия</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
