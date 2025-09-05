'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Save, Eye, EyeOff } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, endpoints } from '@/lib/api';
import { CreateAlbumRequest } from '@/types';
import { useToast } from '@/hooks/use-toast';

const createAlbumSchema = z.object({
  title: z.string().min(1, 'Название обязательно').max(100, 'Название слишком длинное'),
  description: z.string().max(500, 'Описание слишком длинное').optional(),
  is_public: z.boolean().default(false),
});

type CreateAlbumForm = z.infer<typeof createAlbumSchema>;

export default function NewAlbumPage() {
  const [isPublic, setIsPublic] = useState(false);
  const router = useRouter();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<CreateAlbumForm>({
    resolver: zodResolver(createAlbumSchema),
    defaultValues: {
      is_public: false,
    },
  });

  const watchedTitle = watch('title');
  const watchedDescription = watch('description');

  // Create album mutation
  const createAlbumMutation = useMutation({
    mutationFn: async (data: CreateAlbumRequest) => {
      const response = await apiClient.post(endpoints.albums.create(), data);
      return response.data;
    },
    onSuccess: (album) => {
      queryClient.invalidateQueries({ queryKey: ['albums'] });
      toast({
        title: 'Альбом создан',
        description: 'Альбом был успешно создан.',
      });
      router.push(`/dashboard/albums/${album.id}`);
    },
    onError: (error: any) => {
      toast({
        title: 'Ошибка создания',
        description: error.message || 'Не удалось создать альбом.',
        variant: 'destructive',
      });
    },
  });

  const onSubmit = (data: CreateAlbumForm) => {
    createAlbumMutation.mutate({
      title: data.title,
      description: data.description || undefined,
      is_public: data.is_public,
    });
  };

  const handleCancel = () => {
    router.back();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={handleCancel}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Создать альбом</h1>
          <p className="text-muted-foreground">
            Создайте новый интерактивный альбом с QR-кодами
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Form */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Основная информация</CardTitle>
              <CardDescription>
                Заполните основную информацию об альбоме
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {/* Title */}
                <div className="space-y-2">
                  <label htmlFor="title" className="text-sm font-medium">
                    Название альбома *
                  </label>
                  <Input
                    id="title"
                    placeholder="Введите название альбома"
                    {...register('title')}
                    className={errors.title ? 'border-destructive' : ''}
                  />
                  {errors.title && (
                    <p className="text-sm text-destructive">{errors.title.message}</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {watchedTitle?.length || 0}/100 символов
                  </p>
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <label htmlFor="description" className="text-sm font-medium">
                    Описание (необязательно)
                  </label>
                  <Textarea
                    id="description"
                    placeholder="Краткое описание альбома"
                    rows={4}
                    {...register('description')}
                    className={errors.description ? 'border-destructive' : ''}
                  />
                  {errors.description && (
                    <p className="text-sm text-destructive">{errors.description.message}</p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {watchedDescription?.length || 0}/500 символов
                  </p>
                </div>

                {/* Visibility */}
                <div className="space-y-4">
                  <label className="text-sm font-medium">Видимость альбома</label>
                  <div className="space-y-3">
                    <div 
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        !isPublic ? 'border-primary bg-primary/5' : 'border-border'
                      }`}
                      onClick={() => setIsPublic(false)}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-4 h-4 rounded-full border-2 ${
                          !isPublic ? 'border-primary bg-primary' : 'border-muted-foreground'
                        }`} />
                        <div>
                          <h4 className="font-medium">Приватный</h4>
                          <p className="text-sm text-muted-foreground">
                            Альбом доступен только по прямой ссылке
                          </p>
                        </div>
                      </div>
                    </div>
                    <div 
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        isPublic ? 'border-primary bg-primary/5' : 'border-border'
                      }`}
                      onClick={() => setIsPublic(true)}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-4 h-4 rounded-full border-2 ${
                          isPublic ? 'border-primary bg-primary' : 'border-muted-foreground'
                        }`} />
                        <div>
                          <h4 className="font-medium">Публичный</h4>
                          <p className="text-sm text-muted-foreground">
                            Альбом может быть найден в поиске и каталогах
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-4 pt-4">
                  <Button 
                    type="submit" 
                    disabled={createAlbumMutation.isPending}
                  >
                    {createAlbumMutation.isPending ? (
                      'Создание...'
                    ) : (
                      <>
                        <Save className="mr-2 h-4 w-4" />
                        Создать альбом
                      </>
                    )}
                  </Button>
                  <Button type="button" variant="outline" onClick={handleCancel}>
                    Отмена
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Preview */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Предварительный просмотр</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-4xl mb-2">📷</div>
                    <p className="text-sm text-muted-foreground">Обложка альбома</p>
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold">
                    {watchedTitle || 'Название альбома'}
                  </h3>
                  {watchedDescription && (
                    <p className="text-sm text-muted-foreground mt-1">
                      {watchedDescription}
                    </p>
                  )}
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={isPublic ? 'default' : 'secondary'}>
                      {isPublic ? 'Публичный' : 'Приватный'}
                    </Badge>
                    <span className="text-xs text-muted-foreground">0 страниц</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tips */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Советы</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0" />
                <p className="text-sm text-muted-foreground">
                  Выберите понятное название, которое отражает содержание альбома
                </p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0" />
                <p className="text-sm text-muted-foreground">
                  Добавьте описание для лучшего понимания контента
                </p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0" />
                <p className="text-sm text-muted-foreground">
                  Вы можете изменить настройки видимости позже
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
