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
import { ArrowLeft, Save, Eye, EyeOff, Lock, Link as LinkIcon } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, endpoints } from '@/lib/api';
import { CreatePageRequest } from '@/types';
import { useToast } from '@/hooks/use-toast';

const createPageSchema = z.object({
  title: z.string().min(1, 'Название обязательно').max(100, 'Название слишком длинное'),
  description: z.string().max(500, 'Описание слишком длинное').optional(),
  page_number: z.number().min(1, 'Номер страницы должен быть больше 0'),
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

type CreatePageForm = z.infer<typeof createPageSchema>;

export default function NewPagePage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const albumId = params.albumId as string;

  const [visibility, setVisibility] = useState<'public' | 'link_only' | 'pin_protected'>('public');
  const [showPin, setShowPin] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
  } = useForm<CreatePageForm>({
    resolver: zodResolver(createPageSchema),
    defaultValues: {
      page_number: 1,
      visibility: 'public',
    },
  });

  const watchedTitle = watch('title');
  const watchedDescription = watch('description');
  const watchedPin = watch('pin');

  // Create page mutation
  const createPageMutation = useMutation({
    mutationFn: async (data: CreatePageRequest) => {
      const response = await apiClient.post(endpoints.albums.createPage(albumId), data);
      return response.data;
    },
    onSuccess: (page) => {
      queryClient.invalidateQueries({ queryKey: ['album', albumId, 'pages'] });
      queryClient.invalidateQueries({ queryKey: ['album', albumId] });
      toast({
        title: 'Страница создана',
        description: 'Страница была успешно создана.',
      });
      router.push(`/dashboard/albums/${albumId}/pages/${page.id}`);
    },
    onError: (error: any) => {
      toast({
        title: 'Ошибка создания',
        description: error.message || 'Не удалось создать страницу.',
        variant: 'destructive',
      });
    },
  });

  const onSubmit = (data: CreatePageForm) => {
    createPageMutation.mutate({
      title: data.title,
      description: data.description || undefined,
      page_number: data.page_number,
      visibility: data.visibility,
      pin: data.visibility === 'pin_protected' ? data.pin : undefined,
    });
  };

  const handleCancel = () => {
    router.back();
  };

  const handleVisibilityChange = (newVisibility: 'public' | 'link_only' | 'pin_protected') => {
    setVisibility(newVisibility);
    setValue('visibility', newVisibility);
    if (newVisibility !== 'pin_protected') {
      setValue('pin', undefined);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={handleCancel}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Создать страницу</h1>
          <p className="text-muted-foreground">
            Добавьте новую страницу в альбом
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
                Заполните информацию о странице
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
                    placeholder="Введите название страницы"
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

                {/* Page Number */}
                <div className="space-y-2">
                  <label htmlFor="page_number" className="text-sm font-medium">
                    Номер страницы *
                  </label>
                  <Input
                    id="page_number"
                    type="number"
                    min="1"
                    placeholder="1"
                    {...register('page_number', { valueAsNumber: true })}
                    className={errors.page_number ? 'border-destructive' : ''}
                  />
                  {errors.page_number && (
                    <p className="text-sm text-destructive">{errors.page_number.message}</p>
                  )}
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <label htmlFor="description" className="text-sm font-medium">
                    Описание (необязательно)
                  </label>
                  <Textarea
                    id="description"
                    placeholder="Краткое описание страницы"
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
                  <label className="text-sm font-medium">Видимость страницы</label>
                  <div className="space-y-3">
                    <div 
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        visibility === 'public' ? 'border-primary bg-primary/5' : 'border-border'
                      }`}
                      onClick={() => handleVisibilityChange('public')}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-4 h-4 rounded-full border-2 ${
                          visibility === 'public' ? 'border-primary bg-primary' : 'border-muted-foreground'
                        }`} />
                        <div>
                          <h4 className="font-medium flex items-center gap-2">
                            <Eye className="h-4 w-4" />
                            Публичная
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            Страница доступна всем пользователям
                          </p>
                        </div>
                      </div>
                    </div>
                    <div 
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        visibility === 'link_only' ? 'border-primary bg-primary/5' : 'border-border'
                      }`}
                      onClick={() => handleVisibilityChange('link_only')}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-4 h-4 rounded-full border-2 ${
                          visibility === 'link_only' ? 'border-primary bg-primary' : 'border-muted-foreground'
                        }`} />
                        <div>
                          <h4 className="font-medium flex items-center gap-2">
                            <LinkIcon className="h-4 w-4" />
                            По ссылке
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            Страница доступна только по прямой ссылке
                          </p>
                        </div>
                      </div>
                    </div>
                    <div 
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        visibility === 'pin_protected' ? 'border-primary bg-primary/5' : 'border-border'
                      }`}
                      onClick={() => handleVisibilityChange('pin_protected')}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-4 h-4 rounded-full border-2 ${
                          visibility === 'pin_protected' ? 'border-primary bg-primary' : 'border-muted-foreground'
                        }`} />
                        <div>
                          <h4 className="font-medium flex items-center gap-2">
                            <Lock className="h-4 w-4" />
                            С PIN-кодом
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            Страница защищена PIN-кодом
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* PIN Input */}
                {visibility === 'pin_protected' && (
                  <div className="space-y-2">
                    <label htmlFor="pin" className="text-sm font-medium">
                      PIN-код *
                    </label>
                    <div className="relative">
                      <Input
                        id="pin"
                        type={showPin ? 'text' : 'password'}
                        placeholder="Введите PIN-код (минимум 4 цифры)"
                        {...register('pin')}
                        className={errors.pin ? 'border-destructive pr-10' : 'pr-10'}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPin(!showPin)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      >
                        {showPin ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                    {errors.pin && (
                      <p className="text-sm text-destructive">{errors.pin.message}</p>
                    )}
                    <p className="text-xs text-muted-foreground">
                      PIN-код должен содержать минимум 4 цифры
                    </p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center gap-4 pt-4">
                  <Button 
                    type="submit" 
                    disabled={createPageMutation.isPending}
                  >
                    {createPageMutation.isPending ? (
                      'Создание...'
                    ) : (
                      <>
                        <Save className="mr-2 h-4 w-4" />
                        Создать страницу
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
                    <div className="text-4xl mb-2">📄</div>
                    <p className="text-sm text-muted-foreground">Страница {watch('page_number') || 1}</p>
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold">
                    {watchedTitle || 'Название страницы'}
                  </h3>
                  {watchedDescription && (
                    <p className="text-sm text-muted-foreground mt-1">
                      {watchedDescription}
                    </p>
                  )}
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant={
                      visibility === 'public' ? 'default' : 
                      visibility === 'link_only' ? 'secondary' : 'destructive'
                    }>
                      {visibility === 'public' ? 'Публичная' : 
                       visibility === 'link_only' ? 'По ссылке' : 'С PIN'}
                    </Badge>
                    {visibility === 'pin_protected' && watchedPin && (
                      <Badge variant="outline">
                        PIN: {watchedPin}
                      </Badge>
                    )}
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
                  Выберите подходящий уровень доступа для вашего контента
                </p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0" />
                <p className="text-sm text-muted-foreground">
                  PIN-код должен быть легко запоминающимся для ваших пользователей
                </p>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0" />
                <p className="text-sm text-muted-foreground">
                  После создания страницы вы сможете добавить медиа-файлы
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
