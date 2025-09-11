'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { QrCode, AlertCircle, ArrowLeft } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { ToastAction } from '@/components/ui/toast';
import { apiClient, endpoints } from '@/lib/api';
import { mapToUiError, shouldShowToast, shouldShowInlineAlert, logError } from '@/lib/errors';
import { ConnectionStatusBanner } from '@/components/net/OfflineBanner';

export const dynamic = 'force-dynamic';

const resetPasswordSchema = z.object({
  email: z.string().email('Введите корректный email'),
});

type ResetPasswordForm = z.infer<typeof resetPasswordSchema>;

export default function ResetPasswordPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [inlineError, setInlineError] = useState<string | null>(null);
  const router = useRouter();
  const { toast } = useToast();
  const alertRef = useRef<HTMLDivElement>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    clearErrors,
  } = useForm<ResetPasswordForm>({
    resolver: zodResolver(resetPasswordSchema),
  });

  // Обработка клавиши Escape для отмены загрузки
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isLoading) {
        setIsLoading(false);
        setInlineError(null);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isLoading]);

  const onSubmit = async (data: ResetPasswordForm) => {
    setIsLoading(true);
    setInlineError(null);
    clearErrors();

    try {
      const response = await apiClient.post(endpoints.auth.resetPassword(), data, {
        skipAuth: true,
      });

      if (response.success) {
        setIsSuccess(true);
        toast({
          title: 'Письмо отправлено',
          description: 'Проверьте почту для восстановления пароля.',
        });
      }
    } catch (error: any) {
      // Логируем ошибку для разработчиков
      logError(error, 'Reset password form submission');

      // Маппим ошибку в UI-формат
      const uiError = mapToUiError(error, {
        retryAction: () => onSubmit(data),
        checkStatusAction: () => window.open('/status', '_blank'),
      });

      // Показываем ошибку в зависимости от типа
      if (shouldShowInlineAlert(uiError)) {
        setInlineError(uiError.message);
        // Фокусируемся на alert для screen readers
        setTimeout(() => alertRef.current?.focus(), 100);
      } else if (shouldShowToast(uiError)) {
        toast({
          title: uiError.title,
          description: uiError.message,
          variant: 'destructive',
          action: uiError.actions?.[0] ? (
            <ToastAction altText={uiError.actions[0].label} onClick={uiError.actions[0].onClick}>
              {uiError.actions[0].label}
            </ToastAction>
          ) : undefined,
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (isSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-muted/20 p-4">
        <ConnectionStatusBanner />
        <div className="w-full max-w-md">
          {/* Header */}
          <div className="text-center mb-8">
            <Link href="/" className="inline-flex items-center space-x-2 mb-4">
              <QrCode className="h-8 w-8 text-primary" />
              <span className="text-2xl font-bold">StoryQR</span>
            </Link>
            <h1 className="text-2xl font-bold">Письмо отправлено</h1>
            <p className="text-muted-foreground">
              Проверьте почту для восстановления пароля
            </p>
          </div>

          {/* Success Card */}
          <Card>
            <CardContent className="pt-6">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mx-auto">
                  <svg className="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-semibold">Проверьте почту</h3>
                  <p className="text-sm text-muted-foreground">
                    Мы отправили инструкции по восстановлению пароля на ваш email.
                  </p>
                </div>
                <div className="space-y-2">
                  <Button asChild className="w-full">
                    <Link href="/auth/login">
                      <ArrowLeft className="w-4 h-4 mr-2" />
                      Вернуться к входу
                    </Link>
                  </Button>
                  <Button variant="outline" asChild className="w-full">
                    <Link href="/">На главную</Link>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-muted/20 p-4">
      <ConnectionStatusBanner />
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-2 mb-4">
            <QrCode className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold">StoryQR</span>
          </Link>
          <h1 className="text-2xl font-bold">Восстановление пароля</h1>
          <p className="text-muted-foreground">
            Введите email для восстановления доступа
          </p>
        </div>

        {/* Reset Password Form */}
        <Card>
          <CardHeader>
            <CardTitle>Сброс пароля</CardTitle>
            <CardDescription>
              Введите email, на который зарегистрирован аккаунт
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Inline Error Alert */}
            {inlineError && (
              <Alert variant="destructive" className="mb-4" ref={alertRef} tabIndex={-1}>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{inlineError}</AlertDescription>
              </Alert>
            )}
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  {...register('email')}
                  className={errors.email ? 'border-destructive' : ''}
                />
                {errors.email && (
                  <p className="text-sm text-destructive">{errors.email.message}</p>
                )}
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? 'Отправка...' : 'Отправить инструкции'}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-muted-foreground">
                Вспомнили пароль?{' '}
                <Link href="/auth/login" className="text-primary hover:underline">
                  Войти
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
