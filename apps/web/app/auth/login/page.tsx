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
import { QrCode, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { apiClient, endpoints } from '@/lib/api';
import { authManager } from '@/lib/auth';
import { mapToUiError, shouldShowToast, shouldShowInlineAlert, logError } from '@/lib/errors';
import { ConnectionStatusBanner } from '@/components/net/OfflineBanner';

export const dynamic = 'force-dynamic';

const loginSchema = z.object({
  email: z.string().email('Введите корректный email'),
  password: z.string().min(6, 'Пароль должен содержать минимум 6 символов'),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [inlineError, setInlineError] = useState<string | null>(null);
  const router = useRouter();
  const { toast } = useToast();
  const alertRef = useRef<HTMLDivElement>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
    clearErrors,
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
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

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    setInlineError(null);
    clearErrors();

    try {
      const response = await apiClient.post(endpoints.auth.login(), data, {
        skipAuth: true,
      });

      if (response.success) {
        const { access_token, refresh_token, user } = response.data as any;
        
        // Store tokens and user data
        authManager.login(
          { access_token, refresh_token, token_type: 'bearer', expires_in: 3600 },
          user
        );

        toast({
          title: 'Добро пожаловать!',
          description: 'Вы успешно вошли в систему.',
        });

        // Redirect to dashboard
        router.push('/dashboard');
      }
    } catch (error: any) {
      // Логируем ошибку для разработчиков
      logError(error, 'Login form submission');

      // Маппим ошибку в UI-формат
      const uiError = mapToUiError(error, {
        retryAction: () => onSubmit(data),
        resetPasswordAction: () => router.push('/auth/reset-password'),
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
          action: uiError.actions?.[0] ? {
            altText: uiError.actions[0].label,
            onClick: uiError.actions[0].onClick,
          } : undefined,
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

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
          <h1 className="text-2xl font-bold">Добро пожаловать!</h1>
          <p className="text-muted-foreground">
            Войдите в свой аккаунт, чтобы продолжить
          </p>
        </div>

        {/* Login Form */}
        <Card>
          <CardHeader>
            <CardTitle>Вход в аккаунт</CardTitle>
            <CardDescription>
              Введите свои данные для входа в систему
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

              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium">
                  Пароль
                </label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Введите пароль"
                    {...register('password')}
                    className={errors.password ? 'border-destructive pr-10' : 'pr-10'}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-sm text-destructive">{errors.password.message}</p>
                )}
              </div>

              <div className="flex items-center justify-between">
                <Link
                  href="/auth/forgot-password"
                  className="text-sm text-primary hover:underline"
                >
                  Забыли пароль?
                </Link>
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? 'Вход...' : 'Войти'}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-muted-foreground">
                Нет аккаунта?{' '}
                <Link href="/auth/register" className="text-primary hover:underline">
                  Зарегистрироваться
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Demo Account */}
        <Card className="mt-4">
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-2">
                Хотите попробовать без регистрации?
              </p>
              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  // Demo login logic
                  toast({
                    title: 'Демо режим',
                    description: 'Вход в демо аккаунт...',
                  });
                }}
              >
                Войти в демо
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
