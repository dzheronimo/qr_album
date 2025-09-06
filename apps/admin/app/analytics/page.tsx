'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { adminApi } from '@/lib/adminApi';
import { formatCurrency, formatNumber, formatDate } from '@/lib/utils';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Calendar, 
  DollarSign,
  BarChart3,
  Download,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState('30d');
  const [currency, setCurrency] = useState('RUB');

  const { data: overviewData, isLoading: overviewLoading } = useQuery({
    queryKey: ['analytics', 'overview', dateRange],
    queryFn: () => adminApi.getAnalyticsOverview({
      from: getDateFromRange(dateRange).from,
      to: getDateFromRange(dateRange).to,
    }),
  });

  const { data: revenueData, isLoading: revenueLoading } = useQuery({
    queryKey: ['analytics', 'revenue', dateRange, currency],
    queryFn: () => adminApi.getAnalyticsRevenue({
      granularity: 'day',
      from: getDateFromRange(dateRange).from,
      to: getDateFromRange(dateRange).to,
      currency,
    }),
  });

  const { data: funnelsData, isLoading: funnelsLoading } = useQuery({
    queryKey: ['analytics', 'funnels', dateRange],
    queryFn: () => adminApi.getAnalyticsFunnels({
      from: getDateFromRange(dateRange).from,
      to: getDateFromRange(dateRange).to,
    }),
  });

  const { data: cohortsData, isLoading: cohortsLoading } = useQuery({
    queryKey: ['analytics', 'cohorts', dateRange],
    queryFn: () => adminApi.getAnalyticsCohorts({
      from: getDateFromRange(dateRange).from,
      to: getDateFromRange(dateRange).to,
    }),
  });

  function getDateFromRange(range: string) {
    const now = new Date();
    const from = new Date();
    
    switch (range) {
      case '7d':
        from.setDate(now.getDate() - 7);
        break;
      case '30d':
        from.setDate(now.getDate() - 30);
        break;
      case '90d':
        from.setDate(now.getDate() - 90);
        break;
      case '1y':
        from.setFullYear(now.getFullYear() - 1);
        break;
      default:
        from.setDate(now.getDate() - 30);
    }
    
    return {
      from: from.toISOString().split('T')[0],
      to: now.toISOString().split('T')[0],
    };
  }

  const getTrendIcon = (value: number) => {
    if (value > 0) return <ArrowUpRight className="h-4 w-4 text-green-600" />;
    if (value < 0) return <ArrowDownRight className="h-4 w-4 text-red-600" />;
    return null;
  };

  const getTrendColor = (value: number) => {
    if (value > 0) return 'text-green-600';
    if (value < 0) return 'text-red-600';
    return 'text-muted-foreground';
  };

  if (overviewLoading || revenueLoading || funnelsLoading || cohortsLoading) {
    return (
      <AdminLayout>
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Загрузка аналитики...</p>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Аналитика</h1>
            <p className="text-muted-foreground">
              Обзор ключевых показателей и метрик
            </p>
          </div>
          <div className="flex gap-2">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="h-10 px-3 py-2 border border-input bg-background rounded-md text-sm"
            >
              <option value="7d">Последние 7 дней</option>
              <option value="30d">Последние 30 дней</option>
              <option value="90d">Последние 90 дней</option>
              <option value="1y">Последний год</option>
            </select>
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="h-10 px-3 py-2 border border-input bg-background rounded-md text-sm"
            >
              <option value="RUB">RUB</option>
              <option value="EUR">EUR</option>
            </select>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Экспорт
            </Button>
          </div>
        </div>

        {/* Overview KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Всего пользователей</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatNumber(overviewData?.data?.totalUsers || 0)}
              </div>
              <div className="flex items-center text-xs">
                <span className={getTrendColor(12)}>+12%</span>
                <span className="text-muted-foreground ml-1">с прошлого месяца</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Активные пользователи</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatNumber(overviewData?.data?.activeUsers || 0)}
              </div>
              <div className="flex items-center text-xs">
                <span className={getTrendColor(8)}>+8%</span>
                <span className="text-muted-foreground ml-1">с прошлого месяца</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Выручка</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(overviewData?.data?.totalRevenue || 0, currency as 'RUB' | 'EUR')}
              </div>
              <div className="flex items-center text-xs">
                <span className={getTrendColor(15)}>+15%</span>
                <span className="text-muted-foreground ml-1">с прошлого месяца</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Конверсия</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {((overviewData?.data?.conversionRate || 0) * 100).toFixed(1)}%
              </div>
              <div className="flex items-center text-xs">
                <span className={getTrendColor(-2)}>-2%</span>
                <span className="text-muted-foreground ml-1">с прошлого месяца</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Revenue Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Выручка по дням</CardTitle>
            <CardDescription>
              Динамика выручки за выбранный период
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center">
              <div className="text-center">
                <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">График выручки</p>
                <p className="text-sm text-muted-foreground">
                  Здесь будет интерактивный график с данными: {revenueData?.data?.daily?.length || 0} точек
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Funnels */}
        <Card>
          <CardHeader>
            <CardTitle>Воронка конверсии</CardTitle>
            <CardDescription>
              Анализ конверсии по этапам
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium">Просмотры страницы тарифов</div>
                  <div className="text-sm text-muted-foreground">Пользователи, посетившие /pricing</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">
                    {formatNumber(funnelsData?.data?.pricingViews || 0)}
                  </div>
                  <div className="text-sm text-muted-foreground">100%</div>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium">Начали триал</div>
                  <div className="text-sm text-muted-foreground">Пользователи, активировавшие триал</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">
                    {formatNumber(funnelsData?.data?.trialStarts || 0)}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {((funnelsData?.data?.conversionRates?.trial || 0) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium">Оплатили план</div>
                  <div className="text-sm text-muted-foreground">Пользователи, купившие платный план</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">
                    {formatNumber(funnelsData?.data?.paidConversions || 0)}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {((funnelsData?.data?.conversionRates?.paid || 0) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium">Добавили печать</div>
                  <div className="text-sm text-muted-foreground">Пользователи, заказавшие печатные материалы</div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold">
                    {formatNumber(funnelsData?.data?.printAddons || 0)}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {((funnelsData?.data?.conversionRates?.print || 0) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Cohorts */}
        <Card>
          <CardHeader>
            <CardTitle>Когортный анализ</CardTitle>
            <CardDescription>
              Удержание пользователей по месяцам
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {cohortsData?.data?.map((cohort: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <div className="font-medium">{cohort.month}</div>
                    <div className="text-sm text-muted-foreground">
                      {formatNumber(cohort.users)} пользователей
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="text-center">
                      <div className="text-lg font-semibold">
                        {((cohort.retention?.month1 || 0) * 100).toFixed(0)}%
                      </div>
                      <div className="text-xs text-muted-foreground">1 месяц</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold">
                        {((cohort.retention?.month2 || 0) * 100).toFixed(0)}%
                      </div>
                      <div className="text-xs text-muted-foreground">2 месяца</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold">
                        {((cohort.retention?.month3 || 0) * 100).toFixed(0)}%
                      </div>
                      <div className="text-xs text-muted-foreground">3 месяца</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
}


