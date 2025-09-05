'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ArrowLeft, 
  Save, 
  Upload, 
  QrCode, 
  Eye, 
  Lock, 
  Link as LinkIcon,
  Image,
  Video,
  Music,
  Trash2,
  Download,
  Share2
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, endpoints } from '@/lib/api';
import { Page, Media, QRCode } from '@/types';
import { useToast } from '@/hooks/use-toast';
import { formatBytes, getFileType } from '@/lib/utils';

const updatePageSchema = z.object({
  title: z.string().min(1, 'Название обязательно').max(100, 'Название слишком длинное'),
  description: z.string().max(500, 'Описание слишком длинное').optional(),
  visibility: z.enum(['public', 'link_only', 'pin_protected']),
  pin: z.string().optional(),
}).refine((data) => {
  if (data.visibility === 'pin_protected' && (!data.pin || data.pin.length < 4)) {
    return false;
  }
  return true;
}, {
  message: 'PIN должен содержать минимум 4 цифры',
  path: ['pin'],
});

type UpdatePageForm = z.infer<typeof updatePageSchema>;

export default function PageEditPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const albumId = params.albumId as string;
  const pageId = params.pageId as string;

  const [showPin, setShowPin] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<File[]>([]);

  // Fetch page details
  const { data: page, isLoading: pageLoading } = useQuery({
    queryKey: ['page', pageId],
    queryFn: async () => {
      const response = await apiClient.get<Page>(endpoints.pages.get(pageId));
      return response.data;
    },
  });

  // Fetch page media
  const { data: media, isLoading: mediaLoading } = useQuery({
    queryKey: ['page', pageId, 'media'],
    queryFn: async () => {
      const response = await apiClient.get<Media[]>(endpoints.pages.media(pageId));
      return response.data;
    },
  });

  // Fetch page QR code
  const { data: qrCode } = useQuery({
    queryKey: ['page', pageId, 'qr'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<QRCode>(endpoints.qr.get(pageId));
        return response.data;
      } catch {
        return null;
      }
    },
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<UpdatePageForm>({
    resolver: zodResolver(updatePageSchema),
  });

  // Update form when page data loads
  React.useEffect(() => {
    if (page) {
      reset({
        title: page.title,
        description: page.description || '',
        visibility: page.visibility,
        pin: page.pin || '',
      });
    }
  }, [page, reset]);

  // Update page mutation
  const updatePageMutation = useMutation({
    mutationFn: async (data: UpdatePageForm) => {
      const response = await apiClient.put(endpoints.pages.update(pageId), data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['page', pageId] });
      queryClient.invalidateQueries({ queryKey: ['album', albumId, 'pages'] });
      toast({
        title: 'Страница обновлена',
        description: 'Изменения были успешно сохранены.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Ошибка обновления',
        description: error.message || 'Не удалось обновить страницу.',
        variant: 'destructive',
      });
    },
  });

  // Delete page mutation
  const deletePageMutation = useMutation({
    mutationFn: async () => {
      await apiClient.delete(endpoints.pages.delete(pageId));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['album', albumId, 'pages'] });
      queryClient.invalidateQueries({ queryKey: ['album', albumId] });
      toast({
        title: 'Страница удалена',
        description: 'Страница была успешно удалена.',
      });
      router.push(`/dashboard/albums/${albumId}`);
    },
    onError: (error: any) => {
      toast({
        title: 'Ошибка удаления',
        description: error.message || 'Не удалось удалить страницу.',
        variant: 'destructive',
      });
    },
  });

  // Generate QR code mutation
  const generateQRMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post(endpoints.qr.generate(), {
        page_id: pageId,
        album_id: albumId,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['page', pageId, 'qr'] });
      toast({
        title: 'QR-код создан',
        description: 'QR-код для страницы был успешно создан.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Ошибка создания QR-кода',
        description: error.message || 'Не удалось создать QR-код.',
        variant: 'destructive',
      });
    },
  });

  // File upload handler
  const handleFileUpload = async (files: FileList) => {
    const fileArray = Array.from(files);
    setUploadingFiles(fileArray);

    try {
      for (const file of fileArray) {
        const formData = new FormData();
        formData.append('file', file);
        
        await apiClient.upload(endpoints.media.upload(), file);
        // Attach media to page
        // await apiClient.post(endpoints.media.attach(mediaId), { page_id: pageId });
      }
      
      queryClient.invalidateQueries({ queryKey: ['page', pageId, 'media'] });
      toast({
        title: 'Файлы загружены',
        description: 'Все файлы были успешно загружены.',
      });
    } catch (error: any) {
      toast({
        title: 'Ошибка загрузки',
        description: error.message || 'Не удалось загрузить файлы.',
        variant: 'destructive',
      });
    } finally {
      setUploadingFiles([]);
    }
  };

  const onSubmit = (data: UpdatePageForm) => {
    updatePageMutation.mutate(data);
  };

  const handleDeletePage = () => {
    if (page && confirm(`Вы уверены, что хотите удалить страницу "${page.title}"? Это действие нельзя отменить.`)) {
      deletePageMutation.mutate();
    }
  };

  const handleSharePage = () => {
    if (page) {
      const shareUrl = `${window.location.origin}/public/page/${page.id}`;
      navigator.clipboard.writeText(shareUrl);
      toast({
        title: 'Ссылка скопирована',
        description: 'Ссылка на страницу скопирована в буфер обмена.',
      });
    }
  };

  if (pageLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-muted animate-pulse rounded w-1/3" />
        <div className="h-64 bg-muted animate-pulse rounded" />
      </div>
    );
  }

  if (!page) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold mb-4">Страница не найдена</h2>
        <p className="text-muted-foreground mb-6">
          Возможно, страница была удалена или у вас нет доступа к ней.
        </p>
        <Button onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Назад
        </Button>
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
            <h1 className="text-3xl font-bold tracking-tight">{page.title}</h1>
            <Badge variant={
              page.visibility === 'public' ? 'default' : 
              page.visibility === 'link_only' ? 'secondary' : 'destructive'
            }>
              {page.visibility === 'public' ? 'Публичная' : 
               page.visibility === 'link_only' ? 'По ссылке' : 'С PIN'}
            </Badge>
          </div>
          {page.description && (
            <p className="text-muted-foreground">{page.description}</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleSharePage}>
            <Share2 className="mr-2 h-4 w-4" />
            Поделиться
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="edit" className="space-y-6">
        <TabsList>
          <TabsTrigger value="edit">Редактирование</TabsTrigger>
          <TabsTrigger value="media">Медиа</TabsTrigger>
          <TabsTrigger value="qr">QR-код</TabsTrigger>
        </TabsList>

        {/* Edit Tab */}
        <TabsContent value="edit" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Настройки страницы</CardTitle>
              <CardDescription>
                Редактируйте информацию о странице
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {/* Title */}
                <div className="space-y-2">
                  <label htmlFor="title" className="text-sm font-medium">
                    Название страницы *
                  </label>
                  <Input
                    id="title"
                    {...register('title')}
                    className={errors.title ? 'border-destructive' : ''}
                  />
                  {errors.title && (
                    <p className="text-sm text-destructive">{errors.title.message}</p>
                  )}
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <label htmlFor="description" className="text-sm font-medium">
                    Описание
                  </label>
                  <Textarea
                    id="description"
                    rows={4}
                    {...register('description')}
                    className={errors.description ? 'border-destructive' : ''}
                  />
                  {errors.description && (
                    <p className="text-sm text-destructive">{errors.description.message}</p>
                  )}
                </div>

                {/* Visibility */}
                <div className="space-y-4">
                  <label className="text-sm font-medium">Видимость страницы</label>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3">
                      <input
                        type="radio"
                        id="public"
                        value="public"
                        {...register('visibility')}
                        className="w-4 h-4"
                      />
                      <label htmlFor="public" className="flex items-center gap-2">
                        <Eye className="h-4 w-4" />
                        Публичная
                      </label>
                    </div>
                    <div className="flex items-center space-x-3">
                      <input
                        type="radio"
                        id="link_only"
                        value="link_only"
                        {...register('visibility')}
                        className="w-4 h-4"
                      />
                      <label htmlFor="link_only" className="flex items-center gap-2">
                        <LinkIcon className="h-4 w-4" />
                        По ссылке
                      </label>
                    </div>
                    <div className="flex items-center space-x-3">
                      <input
                        type="radio"
                        id="pin_protected"
                        value="pin_protected"
                        {...register('visibility')}
                        className="w-4 h-4"
                      />
                      <label htmlFor="pin_protected" className="flex items-center gap-2">
                        <Lock className="h-4 w-4" />
                        С PIN-кодом
                      </label>
                    </div>
                  </div>
                </div>

                {/* PIN Input */}
                {watch('visibility') === 'pin_protected' && (
                  <div className="space-y-2">
                    <label htmlFor="pin" className="text-sm font-medium">
                      PIN-код *
                    </label>
                    <div className="relative">
                      <Input
                        id="pin"
                        type={showPin ? 'text' : 'password'}
                        placeholder="Введите PIN-код"
                        {...register('pin')}
                        className={errors.pin ? 'border-destructive pr-10' : 'pr-10'}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPin(!showPin)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      >
                        {showPin ? (
                          <Eye className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                    {errors.pin && (
                      <p className="text-sm text-destructive">{errors.pin.message}</p>
                    )}
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-4 pt-4">
                  <Button 
                    type="submit" 
                    disabled={updatePageMutation.isPending}
                  >
                    {updatePageMutation.isPending ? (
                      'Сохранение...'
                    ) : (
                      <>
                        <Save className="mr-2 h-4 w-4" />
                        Сохранить изменения
                      </>
                    )}
                  </Button>
                  <Button 
                    type="button" 
                    variant="destructive" 
                    onClick={handleDeletePage}
                    disabled={deletePageMutation.isPending}
                  >
                    {deletePageMutation.isPending ? 'Удаление...' : 'Удалить страницу'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Media Tab */}
        <TabsContent value="media" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Медиа файлы</CardTitle>
              <CardDescription>
                Загружайте и управляйте медиа файлами страницы
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Upload Area */}
              <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center mb-6">
                <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">Загрузить файлы</h3>
                <p className="text-muted-foreground mb-4">
                  Перетащите файлы сюда или нажмите для выбора
                </p>
                <input
                  type="file"
                  multiple
                  accept="image/*,video/*,audio/*"
                  onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
                  className="hidden"
                  id="file-upload"
                />
                <Button asChild>
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="mr-2 h-4 w-4" />
                    Выбрать файлы
                  </label>
                </Button>
              </div>

              {/* Uploading Files */}
              {uploadingFiles.length > 0 && (
                <div className="space-y-2 mb-6">
                  <h4 className="font-medium">Загружаются файлы:</h4>
                  {uploadingFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-muted rounded">
                      <span className="text-sm">{file.name}</span>
                      <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    </div>
                  ))}
                </div>
              )}

              {/* Media Grid */}
              {mediaLoading ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-32 bg-muted animate-pulse rounded" />
                  ))}
                </div>
              ) : media && media.length > 0 ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {media.map((item) => (
                    <Card key={item.id} className="group">
                      <CardContent className="p-0">
                        <div className="aspect-video bg-muted rounded-t-lg flex items-center justify-center">
                          {getFileType(item.original_filename) === 'image' ? (
                            <Image className="h-8 w-8 text-muted-foreground" />
                          ) : getFileType(item.original_filename) === 'video' ? (
                            <Video className="h-8 w-8 text-muted-foreground" />
                          ) : (
                            <Music className="h-8 w-8 text-muted-foreground" />
                          )}
                        </div>
                        <div className="p-3">
                          <h4 className="font-medium text-sm line-clamp-1">{item.original_filename}</h4>
                          <p className="text-xs text-muted-foreground">{formatBytes(item.file_size)}</p>
                          <div className="flex items-center gap-2 mt-2">
                            <Button size="sm" variant="outline">
                              <Download className="h-3 w-3" />
                            </Button>
                            <Button size="sm" variant="outline">
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Image className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="font-medium mb-2">Нет медиа файлов</h3>
                  <p className="text-sm text-muted-foreground">
                    Загрузите файлы, чтобы добавить их на страницу
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* QR Code Tab */}
        <TabsContent value="qr" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>QR-код страницы</CardTitle>
              <CardDescription>
                Создайте и скачайте QR-код для этой страницы
              </CardDescription>
            </CardHeader>
            <CardContent>
              {qrCode ? (
                <div className="space-y-6">
                  <div className="text-center">
                    <div className="inline-block p-4 bg-white rounded-lg border">
                      <img
                        src={qrCode.qr_image_url}
                        alt="QR Code"
                        className="w-48 h-48"
                      />
                    </div>
                    <p className="text-sm text-muted-foreground mt-4">
                      QR-код для страницы "{page.title}"
                    </p>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">Короткая ссылка:</label>
                      <div className="flex items-center gap-2 mt-1">
                        <Input value={qrCode.short_url} readOnly />
                        <Button
                          variant="outline"
                          onClick={() => {
                            navigator.clipboard.writeText(qrCode.short_url);
                            toast({
                              title: 'Ссылка скопирована',
                              description: 'Короткая ссылка скопирована в буфер обмена.',
                            });
                          }}
                        >
                          Копировать
                        </Button>
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button
                        onClick={() => {
                          const link = document.createElement('a');
                          link.href = qrCode.qr_image_url;
                          link.download = `qr-code-${page.title}.png`;
                          link.click();
                        }}
                      >
                        <Download className="mr-2 h-4 w-4" />
                        Скачать PNG
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => {
                          const svgUrl = endpoints.qr.image(qrCode.id, { format: 'svg' });
                          const link = document.createElement('a');
                          link.href = svgUrl;
                          link.download = `qr-code-${page.title}.svg`;
                          link.click();
                        }}
                      >
                        <Download className="mr-2 h-4 w-4" />
                        Скачать SVG
                      </Button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <QrCode className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="font-medium mb-2">QR-код не создан</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Создайте QR-код для этой страницы
                  </p>
                  <Button
                    onClick={() => generateQRMutation.mutate()}
                    disabled={generateQRMutation.isPending}
                  >
                    {generateQRMutation.isPending ? 'Создание...' : 'Создать QR-код'}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
