'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, Package, Image } from 'lucide-react';
import { apiClient, endpoints } from '@/lib/api';
import { DEFAULT_PRINT_SKUS } from '@/lib/constants';
import { formatPriceWithCurrency, getPriceInCurrency, Currency } from '@/lib/currency';
import { trackCheckoutAddonChange } from '@/lib/analytics';
import { PrintSku } from '@/types';

interface PrintUpsellProps {
  currency: Currency;
  selectedSku: string | null;
  onSkuChange: (sku: string | null) => void;
  className?: string;
}

export function PrintUpsell({ currency, selectedSku, onSkuChange, className }: PrintUpsellProps) {
  const [isFallback, setIsFallback] = useState(false);

  // Загружаем SKU из API
  const { data: skusData, isLoading, error } = useQuery({
    queryKey: ['print', 'skus'],
    queryFn: async () => {
      const response = await apiClient.get<PrintSku[]>(endpoints.print.skus());
      return response.data;
    },
    retry: 1,
    staleTime: 10 * 60 * 1000, // 10 минут
  });

  // Определяем какие SKU использовать
  const skus = skusData || DEFAULT_PRINT_SKUS;
  const usingFallback = !skusData || error;

  useEffect(() => {
    if (usingFallback && !isFallback) {
      setIsFallback(true);
    }
  }, [usingFallback, isFallback]);

  const handleSkuSelect = async (sku: string | null) => {
    onSkuChange(sku);
    await trackCheckoutAddonChange(sku || 'none', !!sku);
  };

  const selectedSkuData = skus.find(sku => sku.sku === selectedSku);

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Package className="h-5 w-5" />
          Добавьте печатные QR-карточки
        </CardTitle>
        <CardDescription>
          Красивые карточки и таблички с QR-кодами для вашего события
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Опция "Без печати" */}
        <div
          className={`p-4 border rounded-lg cursor-pointer transition-colors ${
            !selectedSku ? 'border-primary bg-primary/5' : 'border-border hover:bg-muted/50'
          }`}
          onClick={() => handleSkuSelect(null)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-4 h-4 rounded-full border-2 ${
                !selectedSku ? 'border-primary bg-primary' : 'border-muted-foreground'
              }`} />
              <div>
                <h4 className="font-medium">Без печати</h4>
                <p className="text-sm text-muted-foreground">
                  Только цифровой QR-код
                </p>
              </div>
            </div>
            <span className="text-lg font-semibold">₽0</span>
          </div>
        </div>

        {/* Варианты печати */}
        {skus.map((sku) => (
          <div
            key={sku.sku}
            className={`p-4 border rounded-lg cursor-pointer transition-colors ${
              selectedSku === sku.sku ? 'border-primary bg-primary/5' : 'border-border hover:bg-muted/50'
            }`}
            onClick={() => handleSkuSelect(sku.sku)}
            data-testid={`print-option-${sku.sku}`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-4 h-4 rounded-full border-2 ${
                  selectedSku === sku.sku ? 'border-primary bg-primary' : 'border-muted-foreground'
                }`} />
                <div>
                  <h4 className="font-medium">{sku.name}</h4>
                  <p className="text-sm text-muted-foreground">
                    {sku.description}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">
                      {sku.kind === 'cards' ? 'Карточки' : 'Таблички'}
                    </Badge>
                    {sku.kind === 'cards' && (
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Image className="h-3 w-3" />
                        Превью
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <span className="text-lg font-semibold">
                  +{formatPriceWithCurrency(
                    { rub: sku.price_rub, eur: sku.price_eur },
                    currency
                  )}
                </span>
              </div>
            </div>
          </div>
        ))}

        {/* Fallback предупреждение */}
        {isFallback && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-xs text-yellow-800">
              Показаны базовые варианты печати. Актуальные цены уточняйте при заказе.
            </p>
          </div>
        )}

        {/* Итоговая информация */}
        {selectedSkuData && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Check className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-green-800">
                Выбрано: {selectedSkuData.name}
              </span>
            </div>
            <p className="text-xs text-green-700">
              {selectedSkuData.description}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
