'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Gift, 
  Clock, 
  Upload, 
  Users,
  ArrowRight,
  Check
} from 'lucide-react';
import { TRIAL_CONFIG } from '@/lib/constants';
import { trackTrialStartClick } from '@/lib/analytics';

interface TrialCtaProps {
  onStartTrial: () => void;
  className?: string;
}

export function TrialCta({ onStartTrial, className }: TrialCtaProps) {
  const handleStartTrial = async () => {
    await trackTrialStartClick();
    onStartTrial();
  };

  return (
    <Card className={`border-primary bg-gradient-to-r from-primary/5 to-primary/10 ${className}`}>
      <CardHeader className="text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary">
          <Gift className="h-6 w-6 text-primary-foreground" />
        </div>
        <CardTitle className="text-2xl">Попробуйте бесплатно</CardTitle>
        <CardDescription className="text-base">
          Полный доступ к StoryQR на {TRIAL_CONFIG.duration_days} дней
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Особенности триала */}
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-100">
              <Clock className="h-4 w-4 text-green-600" />
            </div>
            <div>
              <p className="font-medium">7 дней бесплатно</p>
              <p className="text-sm text-muted-foreground">
                Полный доступ ко всем функциям
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100">
              <Upload className="h-4 w-4 text-blue-600" />
            </div>
            <div>
              <p className="font-medium">До {TRIAL_CONFIG.max_uploads} загрузок</p>
              <p className="text-sm text-muted-foreground">
                Достаточно для тестирования
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-100">
              <Users className="h-4 w-4 text-purple-600" />
            </div>
            <div>
              <p className="font-medium">Безлимит гостей</p>
              <p className="text-sm text-muted-foreground">
                Приглашайте сколько угодно людей
              </p>
            </div>
          </div>
        </div>

        {/* Список функций */}
        <div className="space-y-2">
          <h4 className="font-medium">Включено в триал:</h4>
          <ul className="space-y-1">
            {TRIAL_CONFIG.features.map((feature, index) => (
              <li key={index} className="flex items-center gap-2 text-sm">
                <Check className="h-4 w-4 text-green-500 flex-shrink-0" />
                <span>{feature}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* CTA кнопка */}
        <Button 
          onClick={handleStartTrial}
          size="lg"
          className="w-full"
        >
          Начать бесплатно на 7 дней
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>

        {/* Дополнительная информация */}
        <div className="text-center">
          <p className="text-xs text-muted-foreground">
            Без карты • Без подписки • Отменить можно в любое время
          </p>
        </div>
      </CardContent>
    </Card>
  );
}


