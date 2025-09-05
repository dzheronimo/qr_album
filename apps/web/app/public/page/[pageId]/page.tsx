'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Lock, 
  Eye, 
  EyeOff, 
  ArrowLeft,
  Image,
  Video,
  Music,
  Download,
  Share2,
  QrCode
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { apiClient, endpoints } from '@/lib/api';
import { PublicPageData } from '@/types';
import { useToast } from '@/hooks/use-toast';
import { formatBytes, getFileType } from '@/lib/utils';

export default function PublicPageView() {
  const params = useParams();
  const pageId = params.pageId as string;
  const { toast } = useToast();
  
  const [pin, setPin] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);

  // Fetch public page data
  const { data: pageData, isLoading, error } = useQuery({
    queryKey: ['public-page', pageId],
    queryFn: async () => {
      const response = await apiClient.get<PublicPageData>(
        endpoints.pages.public(pageId),
        { skipAuth: true }
      );
      return response.data;
    },
    enabled: !!pageId,
  });

  // Validate PIN
  const validatePinMutation = useQuery({
    queryKey: ['validate-pin', pageId, pin],
    queryFn: async () => {
      const response = await apiClient.post(
        endpoints.pages.validatePin(pageId),
        { pin },
        { skipAuth: true }
      );
      return response.data;
    },
    enabled: false, // Only run when manually triggered
  });

  const handlePinSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pin.length < 4) {
      toast({
        title: 'Неверный PIN',
        description: 'PIN должен содержать минимум 4 цифры.',
        variant: 'destructive',
      });
      return;
    }

    try {
      const response = await apiClient.post(
        endpoints.pages.validatePin(pageId),
        { pin },
        { skipAuth: true }
      );
      
      if (response.data.valid) {
        setIsAuthenticated(true);
        setAccessToken(response.data.access_token);
        toast({
          title: 'Доступ разрешен',
          description: 'PIN-код верный. Контент загружается.',
        });
      } else {
        toast({
          title: 'Неверный PIN',
          description: 'Проверьте правильность введенного PIN-кода.',
          variant: 'destructive',
        });
      }
    } catch (error: any) {
      toast({
        title: 'Ошибка проверки PIN',
        description: error.message || 'Не удалось проверить PIN-код.',
        variant: 'destructive',
      });
    }
  };

  const handleShare = () => {
    if (pageData) {
      const shareUrl = window.location.href;
      navigator.clipboard.writeText(shareUrl);
      toast({
        title: 'Ссылка скопирована',
        description: 'Ссылка на страницу скопирована в буфер обмена.',
      });
    }
  };

  const handleDownload = (mediaUrl: string, filename: string) => {
    const link = document.createElement('a');
    link.href = mediaUrl;
    link.download = filename;
    link.click();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Загрузка страницы...</p>
        </div>
      </div>
    );
  }

  if (error || !pageData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Страница не найдена</h1>
          <p className="text-muted-foreground mb-6">
            Возможно, страница была удалена или у вас нет доступа к ней.
          </p>
          <Button onClick={() => window.history.back()}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Назад
          </Button>
        </div>
      </div>
    );
  }

  const { page, album, media, qr_code } = pageData;

  // Show PIN form if page is PIN protected and not authenticated
  if (page.visibility === 'pin_protected' && !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-muted/20">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <Lock className="h-6 w-6 text-primary" />
            </div>
            <CardTitle>Доступ ограничен</CardTitle>
            <CardDescription>
              Эта страница защищена PIN-кодом. Введите код для просмотра контента.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handlePinSubmit} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="pin" className="text-sm font-medium">
                  PIN-код
                </label>
                <Input
                  id="pin"
                  type="password"
                  placeholder="Введите PIN-код"
                  value={pin}
                  onChange={(e) => setPin(e.target.value)}
                  className="text-center text-lg tracking-widest"
                  maxLength={8}
                />
              </div>
              <Button type="submit" className="w-full">
                Разблокировать
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="icon" onClick={() => window.history.back()}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-lg font-semibold">{page.title}</h1>
              <p className="text-sm text-muted-foreground">
                из альбома "{album.title}"
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleShare}>
              <Share2 className="mr-2 h-4 w-4" />
              Поделиться
            </Button>
            {qr_code && (
              <Button variant="outline" size="sm">
                <QrCode className="mr-2 h-4 w-4" />
                QR-код
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container py-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Page Info */}
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center gap-2">
              <h1 className="text-3xl font-bold">{page.title}</h1>
              <Badge variant={
                page.visibility === 'public' ? 'default' : 
                page.visibility === 'link_only' ? 'secondary' : 'destructive'
              }>
                {page.visibility === 'public' ? 'Публичная' : 
                 page.visibility === 'link_only' ? 'По ссылке' : 'С PIN'}
              </Badge>
            </div>
            {page.description && (
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                {page.description}
              </p>
            )}
          </div>

          {/* Media Grid */}
          {media && media.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {media.map((item) => (
                <Card key={item.id} className="group overflow-hidden">
                  <div className="aspect-video bg-muted relative">
                    {getFileType(item.original_filename) === 'image' ? (
                      <img
                        src={item.url}
                        alt={item.original_filename}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                      />
                    ) : getFileType(item.original_filename) === 'video' ? (
                      <div className="w-full h-full flex items-center justify-center">
                        <video
                          src={item.url}
                          controls
                          className="w-full h-full object-cover"
                        />
                      </div>
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <audio
                          src={item.url}
                          controls
                          className="w-full"
                        />
                      </div>
                    )}
                    
                    {/* Overlay with actions */}
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center">
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => handleDownload(item.url, item.original_filename)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => {
                            navigator.clipboard.writeText(item.url);
                            toast({
                              title: 'Ссылка скопирована',
                              description: 'Ссылка на файл скопирована в буфер обмена.',
                            });
                          }}
                        >
                          <Share2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                  
                  <CardContent className="p-4">
                    <h3 className="font-medium line-clamp-1">{item.original_filename}</h3>
                    <div className="flex items-center justify-between text-sm text-muted-foreground mt-1">
                      <span className="flex items-center gap-1">
                        {getFileType(item.original_filename) === 'image' && <Image className="h-3 w-3" />}
                        {getFileType(item.original_filename) === 'video' && <Video className="h-3 w-3" />}
                        {getFileType(item.original_filename) === 'audio' && <Music className="h-3 w-3" />}
                        {getFileType(item.original_filename).toUpperCase()}
                      </span>
                      <span>{formatBytes(item.file_size)}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="pt-6 text-center">
                <Image className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="font-medium mb-2">Нет медиа файлов</h3>
                <p className="text-sm text-muted-foreground">
                  На этой странице пока нет загруженных файлов.
                </p>
              </CardContent>
            </Card>
          )}

          {/* Album Info */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Альбом: {album.title}</h3>
                  {album.description && (
                    <p className="text-sm text-muted-foreground mt-1">
                      {album.description}
                    </p>
                  )}
                </div>
                <Badge variant={album.is_public ? 'default' : 'secondary'}>
                  {album.is_public ? 'Публичный альбом' : 'Приватный альбом'}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t py-8 mt-16">
        <div className="container text-center">
          <p className="text-sm text-muted-foreground">
            Создано с помощью StoryQR
          </p>
        </div>
      </footer>
    </div>
  );
}
