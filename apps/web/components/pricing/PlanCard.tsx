'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Check, Star } from 'lucide-react';
import { BillingPlan } from '@/types';
import { formatPriceWithCurrency, getPriceInCurrency, Currency } from '@/lib/currency';
import { trackPlanSelect } from '@/lib/analytics';

interface PlanCardProps {
  plan: BillingPlan;
  currency: Currency;
  onSelect: (planId: string) => void;
  className?: string;
}

export function PlanCard({ plan, currency, onSelect, className }: PlanCardProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleSelect = async () => {
    setIsLoading(true);
    try {
      await trackPlanSelect(plan.id, currency);
      onSelect(plan.id);
    } finally {
      setIsLoading(false);
    }
  };

  const price = getPriceInCurrency(
    { rub: plan.price_rub, eur: plan.price_eur },
    currency
  );

  return (
    <Card className={`relative ${plan.is_popular ? 'border-primary shadow-lg' : ''} ${className}`}>
      {plan.is_popular && (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
          <Badge className="bg-primary text-primary-foreground">
            <Star className="mr-1 h-3 w-3" />
            Популярный
          </Badge>
        </div>
      )}
      
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">{plan.name}</CardTitle>
        <CardDescription className="text-base">
          {plan.description}
        </CardDescription>
        <div className="mt-4">
          <span className="text-4xl font-bold">
            {formatPriceWithCurrency(
              { rub: plan.price_rub, eur: plan.price_eur },
              currency
            )}
          </span>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        <ul className="space-y-3">
          {plan.features.map((feature, index) => (
            <li key={index} className="flex items-center">
              <Check className="mr-3 h-5 w-5 text-green-500 flex-shrink-0" />
              <span className="text-sm">{feature}</span>
            </li>
          ))}
        </ul>
        
        <Button 
          className="w-full" 
          variant={plan.is_popular ? 'default' : 'outline'}
          onClick={handleSelect}
          disabled={isLoading}
        >
          {isLoading ? 'Загрузка...' : 'Купить'}
        </Button>
      </CardContent>
    </Card>
  );
}


