import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { QrCode, Home, HelpCircle, ArrowLeft } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-2 mb-6">
            <QrCode className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold">StoryQR</span>
          </Link>
        </div>

        {/* 404 Card */}
        <Card>
          <CardHeader className="text-center">
            <div className="text-6xl font-bold text-primary mb-4">404</div>
            <CardTitle className="text-2xl">Страница не найдена</CardTitle>
            <CardDescription>
              К сожалению, запрашиваемая страница не существует или была перемещена
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center space-y-3">
              <Button asChild className="w-full">
                <Link href="/">
                  <Home className="h-4 w-4 mr-2" />
                  На главную
                </Link>
              </Button>
              <Button variant="outline" asChild className="w-full">
                <Link href="/help">
                  <HelpCircle className="h-4 w-4 mr-2" />
                  Помощь
                </Link>
              </Button>
            </div>
            
            <div className="text-center">
              <Button variant="ghost" onClick={() => window.history.back()}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Назад
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Popular Links */}
        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Популярные страницы</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-2">
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/features">Возможности</Link>
                </Button>
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/pricing">Тарифы</Link>
                </Button>
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/contact">Контакты</Link>
                </Button>
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/auth/login">Войти</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
