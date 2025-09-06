'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Check, X } from 'lucide-react';
import { COMPARISON_DATA } from '@/lib/constants';

export function CompareTable() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Сравнение с конкурентами</CardTitle>
        <CardDescription>
          Почему StoryQR — лучший выбор для вашего события
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 font-medium">Функция</th>
                {COMPARISON_DATA.competitors.map((competitor, index) => (
                  <th key={index} className="text-center py-3 px-4 font-medium">
                    {competitor.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {COMPARISON_DATA.features.map((feature, featureIndex) => (
                <tr key={featureIndex} className="border-b">
                  <td className="py-3 px-4 text-sm">{feature}</td>
                  {COMPARISON_DATA.competitors.map((competitor, competitorIndex) => (
                    <td key={competitorIndex} className="text-center py-3 px-4">
                      {competitor.features[featureIndex] ? (
                        <Check className="h-5 w-5 text-green-500 mx-auto" />
                      ) : (
                        <X className="h-5 w-5 text-red-500 mx-auto" />
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="mt-6 p-4 bg-primary/5 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Badge className="bg-primary text-primary-foreground">
              StoryQR
            </Badge>
            <span className="font-medium">Единственный сервис с полным функционалом</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Все функции в одном месте: безлимитные загрузки, печать QR-карточек, 
            живое слайдшоу и поддержка на русском языке.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}


