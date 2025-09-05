'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ArrowLeft, 
  Plus, 
  Edit, 
  Share2, 
  QrCode, 
  BarChart3, 
  Settings,
  Eye,
  Calendar,
  Users,
  FileText,
  Image,
  Video,
  Music
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, endpoints } from '@/lib/api';
import { Album, Page } from '@/types';
import { useToast } from '@/hooks/use-toast';
import { formatDate, formatRelativeTime } from '@/lib/utils';

export default function AlbumDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const albumId = params.albumId as string;

  // Fetch album details
  const { data: album, isLoading: albumLoading } = useQuery({
    queryKey: ['album', albumId],
    queryFn: async () => {
      const response = await apiClient.get<Album>(endpoints.albums.get(albumId));
      return response.data;
    },
  });

  // Fetch album pages
  const { data: pages, isLoading: pagesLoading } = useQuery({
    queryKey: ['album', albumId, 'pages'],
    queryFn: async () => {
      const response = await apiClient.get<Page[]>(endpoints.albums.pages(albumId));
      return response.data;
    },
  });

  // Delete album mutation
  const deleteAlbumMutation = useMutation({
    mutationFn: async () => {
      await apiClient.delete(endpoints.albums.delete(albumId));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['albums'] });
      toast({
        title: 'Альбом удален',
        description: 'Альбом был успешно удален.',
      });
      router.push('/dashboard/albums');
    },
    onError: (error: any) => {
      toast({
        title: 'Ошибка удаления',
        description: error.message || 'Не удалось удалить альбом.',
        variant: 'destructive',
      });
    },
  });

  const handleDeleteAlbum = () => {
    if (album && confirm(`Вы уверены, что хотите удалить альбом "${album.title}"? Это действие нельзя отменить.`)) {
      deleteAlbumMutation.mutate();
    }
  };

  const handleShareAlbum = () => {
    if (album) {
      const shareUrl = `${window.location.origin}/public/album/${album.id}`;
      navigator.clipboard.writeText(shareUrl);
      toast({
        title: 'Ссылка скопирована',
        description: 'Ссылка на альбом скопирована в буфер обмена.',
      });
    }
  };

  if (albumLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-muted animate-pulse rounded w-1/3" />
        <div className="h-64 bg-muted animate-pulse rounded" />
      </div>
    );
  }

  if (!album) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold mb-4">Альбом не найден</h2>
        <p className="text-muted-foreground mb-6">
          Возможно, альбом был удален или у вас нет доступа к нему.
        </p>
        <Link href="/dashboard/albums">
          <Button>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Вернуться к альбомам
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold tracking-tight">{album.title}</h1>
            <Badge variant={album.is_public ? 'default' : 'secondary'}>
              {album.is_public ? 'Публичный' : 'Приватный'}
            </Badge>
          </div>
          {album.description && (
            <p className="text-muted-foreground">{album.description}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleShareAlbum}>
            <Share2 className="mr-2 h-4 w-4" />
            Поделиться
          </Button>
          <Link href={`/dashboard/albums/${album.id}/edit`}>
            <Button variant="outline">
              <Edit className="mr-2 h-4 w-4" />
              Редактировать
            </Button>
          </Link>
        </div>
      </div>

      {/* Album Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <div className="ml-2">
                <p className="text-2xl font-bold">{album.pages_count}</p>
                <p className="text-xs text-muted-foreground">Страниц</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Eye className="h-4 w-4 text-muted-foreground" />
              <div className="ml-2">
                <p className="text-2xl font-bold">{album.views_count}</p>
                <p className="text-xs text-muted-foreground">Просмотров</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <div className="ml-2">
                <p className="text-2xl font-bold">{formatDate(album.created_at)}</p>
                <p className="text-xs text-muted-foreground">Создан</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <div className="ml-2">
                <p className="text-2xl font-bold">{formatRelativeTime(album.updated_at)}</p>
                <p className="text-xs text-muted-foreground">Обновлен</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="pages" className="space-y-6">
        <TabsList>
          <TabsTrigger value="pages">Страницы</TabsTrigger>
          <TabsTrigger value="qr">QR-коды</TabsTrigger>
          <TabsTrigger value="print">Печать</TabsTrigger>
          <TabsTrigger value="analytics">Аналитика</TabsTrigger>
          <TabsTrigger value="settings">Настройки</TabsTrigger>
        </TabsList>

        {/* Pages Tab */}
        <TabsContent value="pages" className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Страницы альбома</h2>
            <Link href={`/dashboard/albums/${album.id}/pages/new`}>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Добавить страницу
              </Button>
            </Link>
          </div>

          {pagesLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(3)].map((_, i) => (
                <Card key={i}>
                  <CardContent className="pt-6">
                    <div className="h-32 bg-muted animate-pulse rounded" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : pages && pages.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {pages.map((page) => (
                <Link key={page.id} href={`/dashboard/albums/${album.id}/pages/${page.id}`}>
                  <Card className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <CardTitle className="text-lg line-clamp-2">{page.title}</CardTitle>
                        <Badge variant="outline">
                          {page.visibility === 'public' ? 'Публичная' : 
                           page.visibility === 'link_only' ? 'По ссылке' : 'PIN'}
                        </Badge>
                      </div>
                      {page.description && (
                        <CardDescription className="line-clamp-2">
                          {page.description}
                        </CardDescription>
                      )}
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="flex items-center justify-between text-sm text-muted-foreground">
                        <span>Страница {page.page_number}</span>
                        <span>{page.views_count} просмотров</span>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="pt-6 text-center">
                <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="font-medium mb-2">Пока нет страниц</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Добавьте первую страницу в альбом
                </p>
                <Link href={`/dashboard/albums/${album.id}/pages/new`}>
                  <Button>
                    <Plus className="mr-2 h-4 w-4" />
                    Добавить страницу
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* QR Codes Tab */}
        <TabsContent value="qr" className="space-y-6">
          <div className="text-center py-12">
            <QrCode className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="font-medium mb-2">QR-коды</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Создавайте QR-коды для каждой страницы альбома
            </p>
            <Link href={`/dashboard/albums/${album.id}/pages/new`}>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Создать страницу с QR-кодом
              </Button>
            </Link>
          </div>
        </TabsContent>

        {/* Print Tab */}
        <TabsContent value="print" className="space-y-6">
          <div className="text-center py-12">
            <QrCode className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="font-medium mb-2">Печать наклеек</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Создайте PDF с QR-кодами для печати на наклейках
            </p>
            <Button>
              <QrCode className="mr-2 h-4 w-4" />
              Создать PDF для печати
            </Button>
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="text-center py-12">
            <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="font-medium mb-2">Аналитика</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Просматривайте статистику по альбому
            </p>
            <Button>
              <BarChart3 className="mr-2 h-4 w-4" />
              Открыть аналитику
            </Button>
          </div>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Настройки альбома</CardTitle>
              <CardDescription>
                Управляйте настройками и видимостью альбома
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">Видимость альбома</h4>
                  <p className="text-sm text-muted-foreground">
                    {album.is_public ? 'Альбом публичный' : 'Альбом приватный'}
                  </p>
                </div>
                <Badge variant={album.is_public ? 'default' : 'secondary'}>
                  {album.is_public ? 'Публичный' : 'Приватный'}
                </Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">Удалить альбом</h4>
                  <p className="text-sm text-muted-foreground">
                    Это действие нельзя отменить
                  </p>
                </div>
                <Button 
                  variant="destructive" 
                  onClick={handleDeleteAlbum}
                  disabled={deleteAlbumMutation.isPending}
                >
                  {deleteAlbumMutation.isPending ? 'Удаление...' : 'Удалить'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
