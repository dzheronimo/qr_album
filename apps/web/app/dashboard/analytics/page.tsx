'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Eye, 
  MousePointer, 
  Calendar,
  Download,
  RefreshCw
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('7d');
  const { toast } = useToast();

  // Mock analytics data
  const stats = {
    totalViews: 1247,
    uniqueVisitors: 892,
    qrScans: 2156,
    avgSessionTime: '2:34',
    bounceRate: '23%',
    topAlbums: [
      { name: 'Семейные фото', views: 456, scans: 234 },
      { name: 'Путешествия 2024', views: 321, scans: 189 },
      { name: 'Рабочие моменты', views: 287, scans: 156 },
      { name: 'Хобби и увлечения', views: 183, scans: 98 }
    ],
    recentActivity: [
      { type: 'scan', album: 'Семейные фото', time: '2 минуты назад', user: 'Анонимный' },
      { type: 'view', album: 'Путешествия 2024', time: '5 минут назад', user: 'Анонимный' },
      { type: 'scan', album: 'Рабочие моменты', time: '12 минут назад', user: 'Анонимный' },
      { type: 'view', album: 'Хобби и увлечения', time: '18 минут назад', user: 'Анонимный' }
    ]
  };

  const handleRefresh = () => {
    toast({
      title: 'Обновление данных',
      description: 'Аналитика обновлена.',
    });
  };

  const handleExport = () => {
    toast({
      title: 'Экспорт данных',
      description: 'Функция экспорта будет реализована в следующих версиях.',
    });
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'scan':
        return <MousePointer className="h-4 w-4 text-blue-500" />;
      case 'view':
        return <Eye className="h-4 w-4 text-green-500" />;
      default:
        return <Eye className="h-4 w-4" />;
    }
  };

  const getActivityText = (type: string) => {
    switch (type) {
      case 'scan':
        return 'Сканировал QR-код';
      case 'view':
        return 'Просматривал альбом';
      default:
        return 'Активность';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Аналитика</h1>
          <p className="text-muted-foreground">
            Статистика использования ваших QR-альбомов
          </p>
        </div>
        <div className="flex gap-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="24h">24 часа</SelectItem>
              <SelectItem value="7d">7 дней</SelectItem>
              <SelectItem value="30d">30 дней</SelectItem>
              <SelectItem value="90d">90 дней</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4" />
          </Button>
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <Eye className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Всего просмотров</p>
                <p className="text-2xl font-bold">{stats.totalViews.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <Users className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Уникальные посетители</p>
                <p className="text-2xl font-bold">{stats.uniqueVisitors.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                <MousePointer className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">QR-сканирований</p>
                <p className="text-2xl font-bold">{stats.qrScans.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
                <TrendingUp className="h-6 w-6 text-orange-600 dark:text-orange-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Среднее время</p>
                <p className="text-2xl font-bold">{stats.avgSessionTime}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Albums */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Популярные альбомы
          </CardTitle>
          <CardDescription>
            Альбомы с наибольшим количеством просмотров и сканирований
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stats.topAlbums.map((album, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-4">
                  <div className="flex items-center justify-center w-8 h-8 bg-muted rounded-lg text-sm font-semibold">
                    {index + 1}
                  </div>
                  <div>
                    <h3 className="font-medium">{album.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      {album.views} просмотров • {album.scans} сканирований
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Badge variant="outline">{album.views} просмотров</Badge>
                  <Badge variant="secondary">{album.scans} сканирований</Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Последняя активность
          </CardTitle>
          <CardDescription>
            Недавние действия пользователей с вашими QR-альбомами
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stats.recentActivity.map((activity, index) => (
              <div key={index} className="flex items-center gap-4 p-3 border rounded-lg">
                <div className="flex items-center justify-center w-8 h-8 bg-muted rounded-lg">
                  {getActivityIcon(activity.type)}
                </div>
                <div className="flex-1">
                  <p className="text-sm">
                    <span className="font-medium">{activity.user}</span>{' '}
                    {getActivityText(activity.type)} в альбоме{' '}
                    <span className="font-medium">"{activity.album}"</span>
                  </p>
                  <p className="text-xs text-muted-foreground">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Конверсия QR-кодов</CardTitle>
            <CardDescription>
              Процент пользователей, которые сканируют QR-коды
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-600 mb-2">
                {Math.round((stats.qrScans / stats.totalViews) * 100)}%
              </div>
              <p className="text-sm text-muted-foreground">
                {stats.qrScans} из {stats.totalViews} просмотров
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Показатель отказов</CardTitle>
            <CardDescription>
              Процент пользователей, покинувших альбом быстро
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-4xl font-bold text-orange-600 mb-2">
                {stats.bounceRate}
              </div>
              <p className="text-sm text-muted-foreground">
                Средний показатель по отрасли: 45%
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

