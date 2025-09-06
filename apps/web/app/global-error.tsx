'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { RefreshCw, AlertTriangle } from 'lucide-react';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Логируем ошибку в консоль для разработчиков
    console.error('Global error:', error);
  }, [error]);

  return (
    <html>
      <body>
        <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 flex items-center justify-center p-4">
          <div className="max-w-md w-full">
            {/* Error Card */}
            <Card>
              <CardHeader className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-destructive/10 rounded-full mb-4 mx-auto">
                  <AlertTriangle className="h-8 w-8 text-destructive" />
                </div>
                <CardTitle className="text-2xl">Критическая ошибка</CardTitle>
                <CardDescription>
                  Произошла серьезная ошибка приложения. Пожалуйста, обновите страницу или обратитесь в поддержку.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center space-y-3">
                  <Button onClick={reset} className="w-full">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Обновить страницу
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => window.location.href = '/'}
                    className="w-full"
                  >
                    Перейти на главную
                  </Button>
                </div>
                
                {process.env.NODE_ENV === 'development' && (
                  <div className="mt-4 p-3 bg-muted rounded-lg">
                    <p className="text-sm font-mono text-muted-foreground">
                      {error.message}
                    </p>
                    {error.digest && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Error ID: {error.digest}
                      </p>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Contact Info */}
            <div className="mt-8 text-center text-sm text-muted-foreground">
              <p>
                Если проблема повторяется, обратитесь в{' '}
                <a href="mailto:support@storyqr.ru" className="text-primary hover:underline">
                  службу поддержки
                </a>
              </p>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
