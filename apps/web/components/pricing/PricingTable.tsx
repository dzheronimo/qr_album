'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { RefreshCw, AlertCircle } from 'lucide-react';
import { PlanCard } from './PlanCard';
import { apiClient, endpoints } from '@/lib/api';
import { DEFAULT_PLANS } from '@/lib/constants';
import { Currency, getCurrencyPreference, saveCurrencyPreference } from '@/lib/currency';
import { trackPricingView, trackCurrencySwitch } from '@/lib/analytics';
import { BillingPlan } from '@/types';

interface PricingTableProps {
  onPlanSelect: (planId: string) => void;
  className?: string;
}

export function PricingTable({ onPlanSelect, className }: PricingTableProps) {
  const [currency, setCurrency] = useState<Currency>('RUB');
  const [isFallback, setIsFallback] = useState(false);

  // Загружаем планы из API
  const { data: plansData, isLoading, error, refetch } = useQuery({
    queryKey: ['billing', 'plans'],
    queryFn: async () => {
      const response = await apiClient.get<{ plans: BillingPlan[] }>(endpoints.billing.plans());
      return response.data;
    },
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 минут
  });

  // Инициализация валюты из localStorage
  useEffect(() => {
    const savedCurrency = getCurrencyPreference();
    setCurrency(savedCurrency);
  }, []);

  // Трекинг просмотра страницы
  useEffect(() => {
    trackPricingView();
  }, []);

  // Обработка переключения валюты
  const handleCurrencyChange = async (newCurrency: Currency) => {
    const oldCurrency = currency;
    setCurrency(newCurrency);
    saveCurrencyPreference(newCurrency);
    await trackCurrencySwitch(oldCurrency, newCurrency);
  };

  // Определяем какие планы использовать
  const plans = plansData?.plans || DEFAULT_PLANS;
  const usingFallback = !plansData || error;

  // Избегаем setState во время рендера: переносим в эффект
  useEffect(() => {
    if (usingFallback && !isFallback) {
      setIsFallback(true);
    }
  }, [usingFallback, isFallback]);

  return (
    <div className={className}>
      {/* Заголовок с переключателем валюты */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-4">Выберите тариф</h2>
        <div className="flex items-center justify-center gap-4">
          <span className="text-sm text-muted-foreground">Валюта:</span>
          <div className="flex bg-muted rounded-lg p-1">
            <Button
              variant={currency === 'RUB' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => handleCurrencyChange('RUB')}
            >
              ₽ RUB
            </Button>
            <Button
              variant={currency === 'EUR' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => handleCurrencyChange('EUR')}
            >
              € EUR
            </Button>
          </div>
        </div>
      </div>

      {/* Статус загрузки данных */}
      {isLoading && (
        <div className="text-center py-8">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Загрузка тарифов...</p>
        </div>
      )}

      {/* Ошибка загрузки */}
      {error && (
        <Card className="mb-6 border-yellow-200 bg-yellow-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-yellow-600" />
              <div className="flex-1">
                <p className="text-sm text-yellow-800">
                  Не удалось загрузить актуальные тарифы. Показаны ориентировочные цены.
                </p>
              </div>
              <Button variant="outline" size="sm" onClick={() => refetch()}>
                Повторить
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Бейдж о fallback данных */}
      {isFallback && (
        <div className="text-center mb-6">
          <Badge variant="secondary" className="bg-blue-100 text-blue-800">
            Ориентировочные цены
          </Badge>
        </div>
      )}

      {/* Карточки тарифов */}
      <div className="grid gap-6 md:grid-cols-3">
        {plans.map((plan) => (
          <PlanCard
            key={plan.id}
            plan={plan}
            currency={currency}
            onSelect={onPlanSelect}
          />
        ))}
      </div>

      {/* Дополнительная информация */}
      <div className="text-center mt-8 text-sm text-muted-foreground">
        <p>Все тарифы включают полный функционал StoryQR</p>
        <p>Разовая оплата • Без подписок • Без скрытых платежей</p>
      </div>
    </div>
  );
}


