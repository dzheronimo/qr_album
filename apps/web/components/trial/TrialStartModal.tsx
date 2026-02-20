'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { Gift, Loader2, Check, Mail, Lock } from 'lucide-react';
import { apiClient, endpoints } from '@/lib/api';
import { trackTrialStartSuccess } from '@/lib/analytics';
import { authManager } from '@/lib/auth';
import { TrialStartResponse } from '@/types';
import { useToast } from '@/hooks/use-toast';

interface TrialStartModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (trialData: TrialStartResponse) => void;
}

export function TrialStartModal({ isOpen, onClose, onSuccess }: TrialStartModalProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(false);
  const { toast } = useToast();

  const startTrialMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post<TrialStartResponse>(endpoints.trial.start());
      return response.data;
    },
    onSuccess: async (data) => {
      await trackTrialStartSuccess();
      onSuccess(data);
      toast({
        title: 'Триал активирован!',
        description: `Бесплатный период до ${new Date(data.ends_at).toLocaleDateString('ru-RU')}`,
      });
      handleClose();
    },
    onError: (error: any) => {
      toast({
        title: 'Ошибка активации триала',
        description: error.message || 'Не удалось активировать триал. Попробуйте еще раз.',
        variant: 'destructive',
      });
    },
  });

  const performLogin = async () => {
    const loginResponse = await apiClient.post<any>(
      endpoints.auth.login(),
      { email, password },
      { skipAuth: true }
    );
    const payload = loginResponse.data;
    const access_token = payload.access_token || payload?.data?.access_token;
    const refresh_token = payload.refresh_token || payload?.data?.refresh_token;
    const user = payload.user || payload?.data?.user;

    if (!access_token || !refresh_token) {
      throw new Error('Некорректный ответ сервера авторизации');
    }

    authManager.login(
      {
        access_token,
        refresh_token,
        token_type: 'bearer',
        expires_in: 3600,
      },
      user
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password) {
      toast({
        title: 'Заполните все поля',
        description: 'Введите email и пароль для входа.',
        variant: 'destructive',
      });
      return;
    }

    try {
      if (!isLogin) {
        await apiClient.post(endpoints.auth.register(), { email, password }, { skipAuth: true });
      }

      await performLogin();
      startTrialMutation.mutate();
    } catch (error: any) {
      toast({
        title: isLogin ? 'Не удалось войти' : 'Не удалось зарегистрироваться',
        description: error.message || 'Проверьте введенные данные и попробуйте снова.',
        variant: 'destructive',
      });
    }
  };

  const handleClose = () => {
    setEmail('');
    setPassword('');
    setIsLogin(false);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-md" data-testid="trial-modal">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Gift className="h-5 w-5 text-primary" />
            Начать бесплатный триал
          </DialogTitle>
          <DialogDescription>
            Войдите в аккаунт или зарегистрируйтесь, чтобы активировать 7-дневный триал
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input id="email" type="email" placeholder="your@email.com" value={email} onChange={(e) => setEmail(e.target.value)} className="pl-10" required />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Пароль</Label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input id="password" type="password" placeholder="Введите пароль" value={password} onChange={(e) => setPassword(e.target.value)} className="pl-10" required />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button type="button" variant={isLogin ? 'default' : 'outline'} size="sm" onClick={() => setIsLogin(true)} className="flex-1">
              Войти
            </Button>
            <Button type="button" variant={!isLogin ? 'default' : 'outline'} size="sm" onClick={() => setIsLogin(false)} className="flex-1">
              Регистрация
            </Button>
          </div>

          <Button type="submit" className="w-full" disabled={startTrialMutation.isPending}>
            {startTrialMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Активация триала...
              </>
            ) : (
              <>
                <Gift className="mr-2 h-4 w-4" />
                {isLogin ? 'Войти и активировать триал' : 'Зарегистрироваться и начать триал'}
              </>
            )}
          </Button>
        </form>

        <Card>
          <CardContent className="pt-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Check className="h-4 w-4 text-green-500" />
                <span className="text-sm font-medium">7 дней бесплатно</span>
              </div>
              <div className="flex items-center gap-2">
                <Check className="h-4 w-4 text-green-500" />
                <span className="text-sm">До 5 загрузок для тестирования</span>
              </div>
              <div className="flex items-center gap-2">
                <Check className="h-4 w-4 text-green-500" />
                <span className="text-sm">Безлимит гостей</span>
              </div>
              <div className="flex items-center gap-2">
                <Check className="h-4 w-4 text-green-500" />
                <span className="text-sm">Все функции StoryQR</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="text-center">
          <p className="text-xs text-muted-foreground">Без карты • Без подписки • Отменить можно в любое время</p>
        </div>
      </DialogContent>
    </Dialog>
  );
}
