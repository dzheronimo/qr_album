'use client';

import { useEffect, useState } from 'react';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Plus, 
  FolderOpen, 
  Eye, 
  QrCode, 
  TrendingUp,
  Upload,
  Users,
  BarChart3,
  ArrowRight
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

import { apiClient, endpoints } from '@/lib/api';
import { AnalyticsOverview, Album } from '@/types';

export const dynamic = 'force-dynamic';

export default function DashboardPage() {
  const [upgradePrompt, setUpgradePrompt] = useState(false);

  // Fetch analytics overview
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: async () => {
      const response = await apiClient.get<AnalyticsOverview>(endpoints.analytics.overview());
      return response.data;
    },
  });

  // Fetch recent albums
  const { data: albums, isLoading: albumsLoading } = useQuery({
    queryKey: ['albums', 'recent'],
    queryFn: async () => {
      const response = await apiClient.get<Album[]>(endpoints.albums.list({ limit: 5 }));
      return response.data;
    },
  });

  useEffect(() => {
    // Check if user should see upgrade prompt
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('upgrade') === 'pro') {
      setUpgradePrompt(true);
    }
  }, []);

  const quickActions = [
    {
      title: 'Создать альбом',
      description: 'Начните новый проект',
      icon: Plus,
      href: '/dashboard/albums/new',
      color: 'bg-blue-500',
    },
    {
      title: 'Загрузить медиа',
      description: 'Добавьте фото и видео',
      icon: Upload,
      href: '/dashboard/media',
      color: 'bg-green-500',
    },
    {
      title: 'Печать QR-кодов',
      description: 'Создайте наклейки',
      icon: QrCode,
      href: '/dashboard/print',
      color: 'bg-purple-500',
    },
    {
      title: 'Аналитика',
      description: 'Посмотрите статистику',
      icon: BarChart3,
      href: '/dashboard/analytics',
      color: 'bg-orange-500',
    },
  ];

  const getStoragePercentage = () => {
    if (!analytics) return 0;
    return (analytics.storage_used / analytics.storage_limit) * 100;
  };

  const getStorageText = () => {
    if (!analytics) return '0 ГБ / 5 ГБ';
    const used = (analytics.storage_used / 1024 / 1024 / 1024).toFixed(1);
    const limit = (analytics.storage_limit / 1024 / 1024 / 1024).toFixed(0);
    return `${used} ГБ / ${limit} ГБ`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Обзор</h1>
          <p className="text-muted-foreground">
            Добро пожаловать в ваш личный кабинет StoryQR
          </p>
        </div>
        <Link href="/dashboard/albums/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Создать альбом
          </Button>
        </Link>
      </div>

      {/* Upgrade Prompt */}
      {upgradePrompt && (
        <Card className="border-primary bg-primary/5">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-primary">Обновитесь до Pro!</h3>
                <p className="text-sm text-muted-foreground">
                  Получите неограниченные возможности и расширенную аналитику
                </p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => setUpgradePrompt(false)}>
                  Позже
                </Button>
                <Link href="/dashboard/settings?tab=billing">
                  <Button size="sm">
                    Обновить
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Stats Overview */}
      {analyticsLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardContent className="pt-6">
                <div className="h-20 bg-muted animate-pulse rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : analytics ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Альбомы</CardTitle>
              <FolderOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.total_albums}</div>
              <p className="text-xs text-muted-foreground">
                Всего создано
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Просмотры</CardTitle>
              <Eye className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.total_views}</div>
              <p className="text-xs text-muted-foreground">
                За все время
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">QR-сканирования</CardTitle>
              <QrCode className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.total_qr_scans}</div>
              <p className="text-xs text-muted-foreground">
                Сканирований
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Медиа файлы</CardTitle>
              <Upload className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.total_media_uploads}</div>
              <p className="text-xs text-muted-foreground">
                Загружено
              </p>
            </CardContent>
          </Card>
        </div>
      ) : null}

      {/* Storage Usage */}
      {analytics && (
        <Card>
          <CardHeader>
            <CardTitle>Использование хранилища</CardTitle>
            <CardDescription>
              {getStorageText()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Progress value={getStoragePercentage()} className="mb-2" />
            <p className="text-sm text-muted-foreground">
              {getStoragePercentage() > 80 && 'Почти достигнут лимит. Рассмотрите обновление до Pro.'}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Быстрые действия</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {quickActions.map((action, index) => (
            <Link key={index} href={action.href}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="pt-6">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${action.color}`}>
                      <action.icon className="h-4 w-4 text-white" />
                    </div>
                    <div>
                      <h3 className="font-medium">{action.title}</h3>
                      <p className="text-sm text-muted-foreground">{action.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Albums */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Недавние альбомы</h2>
          <Link href="/dashboard/albums">
            <Button variant="outline" size="sm">
              Все альбомы
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
        
        {albumsLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[...Array(3)].map((_, i) => (
              <Card key={i}>
                <CardContent className="pt-6">
                  <div className="h-32 bg-muted animate-pulse rounded" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : albums && albums.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {albums.map((album) => (
              <Link key={album.id} href={`/dashboard/albums/${album.id}`}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="pt-6">
                    <div className="space-y-3">
                      <div className="flex items-start justify-between">
                        <h3 className="font-medium line-clamp-2">{album.title}</h3>
                        <Badge variant={album.is_public ? 'default' : 'secondary'}>
                          {album.is_public ? 'Публичный' : 'Приватный'}
                        </Badge>
                      </div>
                      {album.description && (
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {album.description}
                        </p>
                      )}
                      <div className="flex items-center justify-between text-sm text-muted-foreground">
                        <span>{album.pages_count} страниц</span>
                        <span>{album.views_count} просмотров</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="pt-6 text-center">
              <FolderOpen className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="font-medium mb-2">Пока нет альбомов</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Создайте свой первый альбом, чтобы начать работу
              </p>
              <Link href="/dashboard/albums/new">
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Создать альбом
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
