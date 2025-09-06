'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { adminApi } from '@/lib/adminApi';
import { formatDate, formatFileSize } from '@/lib/utils';
import { Check, X, Trash2, Eye, RefreshCw } from 'lucide-react';

export default function MediaModerationPage() {
  const [queue, setQueue] = useState<'flagged' | 'new'>('flagged');
  const [page, setPage] = useState(1);
  const limit = 10;
  const queryClient = useQueryClient();

  const { data: mediaData, isLoading, error } = useQuery({
    queryKey: ['media', 'moderation', { queue, page, limit }],
    queryFn: () => adminApi.getMediaModeration({
      queue,
      page,
      limit,
    }),
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => adminApi.approveMedia(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media', 'moderation'] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (id: string) => adminApi.rejectMedia(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media', 'moderation'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => adminApi.deleteMedia(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media', 'moderation'] });
    },
  });

  const rescanMutation = useMutation({
    mutationFn: (id: string) => adminApi.rescanMedia(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media', 'moderation'] });
    },
  });

  const handleApprove = (id: string) => {
    if (confirm('Одобрить это медиа?')) {
      approveMutation.mutate(id);
    }
  };

  const handleReject = (id: string) => {
    if (confirm('Отклонить это медиа?')) {
      rejectMutation.mutate(id);
    }
  };

  const handleDelete = (id: string) => {
    if (confirm('Удалить это медиа? Это действие нельзя отменить.')) {
      deleteMutation.mutate(id);
    }
  };

  const handleRescan = (id: string) => {
    if (confirm('Повторно просканировать это медиа?')) {
      rescanMutation.mutate(id);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'flagged':
        return <Badge variant="destructive">Помечено</Badge>;
      case 'new':
        return <Badge variant="warning">Новое</Badge>;
      case 'approved':
        return <Badge variant="success">Одобрено</Badge>;
      case 'rejected':
        return <Badge variant="secondary">Отклонено</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getNsfwScoreColor = (score: number) => {
    if (score > 0.7) return 'text-red-600';
    if (score > 0.3) return 'text-yellow-600';
    return 'text-green-600';
  };

  if (error) {
    return (
      <AdminLayout>
        <div className="text-center py-8">
          <p className="text-red-600">Ошибка загрузки медиа</p>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Модерация медиа</h1>
          <p className="text-muted-foreground">
            Проверка и модерация загруженных медиафайлов
          </p>
        </div>

        {/* Queue Selector */}
        <Card>
          <CardHeader>
            <CardTitle>Очередь модерации</CardTitle>
            <CardDescription>
              Выберите очередь для просмотра
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Button
                variant={queue === 'flagged' ? 'default' : 'outline'}
                onClick={() => {
                  setQueue('flagged');
                  setPage(1);
                }}
              >
                Помеченные ({mediaData?.pagination?.total || 0})
              </Button>
              <Button
                variant={queue === 'new' ? 'default' : 'outline'}
                onClick={() => {
                  setQueue('new');
                  setPage(1);
                }}
              >
                Новые ({mediaData?.pagination?.total || 0})
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Media Table */}
        <Card>
          <CardHeader>
            <CardTitle>Список медиа</CardTitle>
            <CardDescription>
              {mediaData?.pagination?.total || 0} файлов в очереди
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="mt-2 text-muted-foreground">Загрузка медиа...</p>
              </div>
            ) : (
              <div className="space-y-4">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Файл</TableHead>
                      <TableHead>Владелец</TableHead>
                      <TableHead>Событие</TableHead>
                      <TableHead>Статус</TableHead>
                      <TableHead>NSFW Score</TableHead>
                      <TableHead>Размер</TableHead>
                      <TableHead>Загружено</TableHead>
                      <TableHead>Действия</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {mediaData?.data?.map((media: any) => (
                      <TableRow key={media.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{media.filename}</div>
                            <div className="text-sm text-muted-foreground">
                              {media.type === 'image' ? 'Изображение' : 'Видео'}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div>
                            <div className="font-medium">{media.owner.name}</div>
                            <div className="text-sm text-muted-foreground">{media.owner.email}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="font-medium">{media.event.title}</div>
                        </TableCell>
                        <TableCell>
                          {getStatusBadge(media.status)}
                        </TableCell>
                        <TableCell>
                          <span className={getNsfwScoreColor(media.nsfwScore)}>
                            {(media.nsfwScore * 100).toFixed(1)}%
                          </span>
                        </TableCell>
                        <TableCell>
                          {formatFileSize(media.size)}
                        </TableCell>
                        <TableCell>
                          {formatDate(media.createdAt)}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => handleRescan(media.id)}
                              disabled={rescanMutation.isPending}
                            >
                              <RefreshCw className="h-4 w-4" />
                            </Button>
                            <Button 
                              size="sm" 
                              variant="success"
                              onClick={() => handleApprove(media.id)}
                              disabled={approveMutation.isPending}
                            >
                              <Check className="h-4 w-4" />
                            </Button>
                            <Button 
                              size="sm" 
                              variant="destructive"
                              onClick={() => handleReject(media.id)}
                              disabled={rejectMutation.isPending}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                            <Button 
                              size="sm" 
                              variant="destructive"
                              onClick={() => handleDelete(media.id)}
                              disabled={deleteMutation.isPending}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                {/* Pagination */}
                {mediaData?.pagination && mediaData.pagination.totalPages > 1 && (
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-muted-foreground">
                      Показано {((page - 1) * limit) + 1}-{Math.min(page * limit, mediaData.pagination.total)} из {mediaData.pagination.total}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={page === 1}
                        onClick={() => setPage(page - 1)}
                      >
                        Назад
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={page >= mediaData.pagination.totalPages}
                        onClick={() => setPage(page + 1)}
                      >
                        Вперед
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
}
