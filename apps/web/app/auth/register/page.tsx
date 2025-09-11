'use client';

import { useState, useRef, useEffect } from 'react';

import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { QrCode, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { ToastAction } from '@/components/ui/toast';
import { apiClient, endpoints } from '@/lib/api';
import { authManager } from '@/lib/auth';
import { mapToUiError, shouldShowToast, shouldShowInlineAlert, logError } from '@/lib/errors';
import { ConnectionStatusBanner } from '@/components/net/OfflineBanner';

export const dynamic = 'force-dynamic';

const registerSchema = z.object({
  email: z.string().email('Введите корректный email'),
  password: z.string().min(8, 'Пароль должен содержать минимум 8 символов'),
  confirmPassword: z.string(),
  username: z.string().min(2, 'Имя пользователя должно содержать минимум 2 символа'),
  firstName: z.string().optional(),
  lastName: z.string().optional(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Пароли не совпадают',
  path: ['confirmPassword'],
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [inlineError, setInlineError] = useState<string | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const alertRef = useRef<HTMLDivElement>(null);

  const plan = searchParams.get('plan');

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
    clearErrors,
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
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

  const onSubmit = async (data: RegisterForm) => {
    setIsLoading(true);
    setInlineError(null);
    clearErrors();

    try {
      // Бэкенд принимает: email, password, first_name, last_name
      // username не поддерживается на сервере — не отправляем его
      const { confirmPassword, username, email, password, firstName, lastName } = data;
      const registerData = {
        email,
        password,
        first_name: firstName || undefined,
        last_name: lastName || undefined,
      } as const;
      
      const response = await apiClient.post(endpoints.auth.register(), registerData, { skipAuth: true });

      if (response?.success) {
        toast({ title: 'Аккаунт создан', description: 'Войдите, используя свой email и пароль.' });
        router.push('/auth/login');
        return;
      }
    } catch (error: any) {
      // Логируем ошибку для разработчиков
      logError(error, 'Register form submission');

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

  const features = [
    'Создавайте неограниченные альбомы',
    'Загружайте фото и видео',
    'Генерируйте QR-коды',
    'Печатайте наклейки',
    'Отслеживайте просмотры',
  ];

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-muted/20 p-4">
      <ConnectionStatusBanner />
      <div className="w-full max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-2 mb-4">
            <QrCode className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold">StoryQR</span>
          </Link>
          <h1 className="text-2xl font-bold">Создайте аккаунт</h1>
          <p className="text-muted-foreground">
            Начните создавать интерактивные альбомы уже сегодня
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2">
          {/* Registration Form */}
          <Card>
            <CardHeader>
              <CardTitle>Регистрация</CardTitle>
              <CardDescription>
                Заполните форму для создания аккаунта
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
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label htmlFor="firstName" className="text-sm font-medium">
                      Имя (необязательно)
                    </label>
                    <Input
                      id="firstName"
                      placeholder="Ваше имя"
                      {...register('firstName')}
                    />
                  </div>
                  <div className="space-y-2">
                    <label htmlFor="lastName" className="text-sm font-medium">
                      Фамилия (необязательно)
                    </label>
                    <Input
                      id="lastName"
                      placeholder="Ваша фамилия"
                      {...register('lastName')}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label htmlFor="username" className="text-sm font-medium">
                    Имя пользователя *
                  </label>
                  <Input
                    id="username"
                    placeholder="username"
                    {...register('username')}
                    className={errors.username ? 'border-destructive' : ''}
                  />
                  {errors.username && (
                    <p className="text-sm text-destructive">{errors.username.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium">
                    Email *
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
                    Пароль *
                  </label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Минимум 8 символов"
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

                <div className="space-y-2">
                  <label htmlFor="confirmPassword" className="text-sm font-medium">
                    Подтвердите пароль *
                  </label>
                  <div className="relative">
                    <Input
                      id="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      placeholder="Повторите пароль"
                      {...register('confirmPassword')}
                      className={errors.confirmPassword ? 'border-destructive pr-10' : 'pr-10'}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                  {errors.confirmPassword && (
                    <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>
                  )}
                </div>

                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? 'Создание аккаунта...' : 'Создать аккаунт'}
                </Button>
              </form>

              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Уже есть аккаунт?{' '}
                  <Link href="/auth/login" className="text-primary hover:underline">
                    Войти
                  </Link>
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Features */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Что вы получите:</CardTitle>
                <CardDescription>
                  Начните с бесплатного тарифа и получите доступ ко всем основным функциям
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {features.map((feature, index) => (
                    <li key={index} className="flex items-center">
                      <CheckCircle className="mr-3 h-5 w-5 text-green-500 flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {plan === 'pro' && (
              <Card className="border-primary">
                <CardHeader>
                  <CardTitle className="text-primary">Pro тариф</CardTitle>
                  <CardDescription>
                    Вы выбрали Pro тариф с расширенными возможностями
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <p className="text-sm">• Неограниченные альбомы и страницы</p>
                    <p className="text-sm">• 100 ГБ хранилища</p>
                    <p className="text-sm">• Расширенная аналитика</p>
                    <p className="text-sm">• API доступ</p>
                    <p className="text-sm">• Приоритетная поддержка</p>
                  </div>
                </CardContent>
              </Card>
            )}

            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <p className="text-sm text-muted-foreground mb-2">
                    Регистрируясь, вы соглашаетесь с нашими
                  </p>
                  <div className="flex justify-center space-x-2">
                    <Link href="/legal/terms" className="text-sm text-primary hover:underline">
                      Условиями использования
                    </Link>
                    <span className="text-sm text-muted-foreground">и</span>
                    <Link href="/legal/privacy" className="text-sm text-primary hover:underline">
                      Политикой конфиденциальности
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
