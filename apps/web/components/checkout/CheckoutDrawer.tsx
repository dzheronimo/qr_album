'use client';

import { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  CreditCard, 
  X, 
  Loader2, 
  Check,
  AlertCircle,
  ExternalLink
} from 'lucide-react';
import { PrintUpsell } from './PrintUpsell';
import { apiClient, endpoints } from '@/lib/api';
import { formatPriceWithCurrency, getPriceInCurrency, Currency } from '@/lib/currency';
import { trackCheckoutOpen, trackCheckoutPayClick, trackCheckoutPayRedirect } from '@/lib/analytics';
import { BillingPlan, CreateOrderRequest, CreateOrderResponse } from '@/types';
import { useToast } from '@/hooks/use-toast';

interface CheckoutDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  plan: BillingPlan | null;
  currency: Currency;
}

export function CheckoutDrawer({ isOpen, onClose, plan, currency }: CheckoutDrawerProps) {
  const [selectedSku, setSelectedSku] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const { toast } = useToast();

  // Трекинг открытия чекаута
  useEffect(() => {
    if (isOpen && plan) {
      trackCheckoutOpen(plan.id, currency);
    }
  }, [isOpen, plan, currency]);

  // Мутация для создания заказа
  const createOrderMutation = useMutation({
    mutationFn: async (orderData: CreateOrderRequest) => {
      const response = await apiClient.post<CreateOrderResponse>(
        endpoints.orders.create(),
        orderData
      );
      return response.data;
    },
    onSuccess: async (data) => {
      await trackCheckoutPayRedirect(data.payment_url);
      // Редирект на страницу оплаты
      window.location.href = data.payment_url;
    },
    onError: (error: any) => {
      toast({
        title: 'Ошибка создания заказа',
        description: error.message || 'Не удалось создать заказ. Попробуйте еще раз.',
        variant: 'destructive',
      });
      setIsProcessing(false);
    },
  });

  const handlePayment = async () => {
    if (!plan) return;

    setIsProcessing(true);

    try {
      // Подготавливаем данные заказа
      const orderData: CreateOrderRequest = {
        plan_id: plan.id,
      };

      // Добавляем дополнения если выбраны
      if (selectedSku) {
        orderData.addons = [{
          sku: selectedSku,
          qty: 1,
        }];
      }

      // Трекинг клика на оплату
      await trackCheckoutPayClick(
        plan.id,
        selectedSku ? [selectedSku] : [],
        getTotalAmount(),
        currency
      );

      // Создаем заказ
      createOrderMutation.mutate(orderData);
    } catch (error) {
      setIsProcessing(false);
    }
  };

  const getTotalAmount = (): number => {
    if (!plan) return 0;

    let total = getPriceInCurrency(
      { rub: plan.price_rub, eur: plan.price_eur },
      currency
    );

    // Добавляем стоимость печати если выбрана
    if (selectedSku) {
      // Здесь нужно получить цену выбранного SKU
      // Для простоты используем примерные цены
      const printPrice = currency === 'RUB' ? 1490 : 18;
      total += printPrice;
    }

    return total;
  };

  const getSelectedSkuName = (): string => {
    if (!selectedSku) return 'Без печати';
    
    // Здесь нужно получить название SKU из данных
    // Для простоты используем примерные названия
    return selectedSku === 'cards-100' ? 'Мини-карточки 100 шт' : 'Таблички 5×7″ 10 шт';
  };

  if (!plan) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto" data-testid="checkout-drawer">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Оформление заказа
          </DialogTitle>
          <DialogDescription>
            Завершите покупку тарифа {plan.name}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Выбранный план */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">{plan.name}</CardTitle>
              <CardDescription>{plan.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span>Тариф</span>
                <span className="font-semibold">
                  {formatPriceWithCurrency(
                    { rub: plan.price_rub, eur: plan.price_eur },
                    currency
                  )}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Апселл печати */}
          <PrintUpsell
            currency={currency}
            selectedSku={selectedSku}
            onSkuChange={setSelectedSku}
          />

          {/* Итого */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Итого к оплате</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span>Тариф {plan.name}</span>
                <span>
                  {formatPriceWithCurrency(
                    { rub: plan.price_rub, eur: plan.price_eur },
                    currency
                  )}
                </span>
              </div>
              
              {selectedSku && (
                <div className="flex items-center justify-between">
                  <span>{getSelectedSkuName()}</span>
                  <span>
                    +{formatPriceWithCurrency(
                      { rub: 1490, eur: 18 }, // Примерные цены
                      currency
                    )}
                  </span>
                </div>
              )}
              
              <Separator />
              
              <div className="flex items-center justify-between text-lg font-semibold">
                <span>Итого</span>
                <span>
                  {formatPriceWithCurrency(
                    { rub: getTotalAmount(), eur: getTotalAmount() },
                    currency
                  )}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Кнопки действий */}
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={onClose}
              className="flex-1"
              disabled={isProcessing}
            >
              Отмена
            </Button>
            <Button
              onClick={handlePayment}
              disabled={isProcessing}
              className="flex-1"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Обработка...
                </>
              ) : (
                <>
                  <CreditCard className="mr-2 h-4 w-4" />
                  Перейти к оплате
                </>
              )}
            </Button>
          </div>

          {/* Информация о безопасности */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start gap-3">
              <Check className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="font-medium text-blue-900 mb-1">
                  Безопасная оплата
                </h4>
                <p className="text-sm text-blue-800">
                  Оплата проходит через защищенный шлюз. Мы не храним данные вашей карты.
                </p>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
