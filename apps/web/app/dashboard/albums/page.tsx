'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Plus, 
  Search, 
  Filter, 
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  Share2,
  Calendar,
  FolderOpen
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { apiClient, endpoints } from '@/lib/api';
import { Album } from '@/types';
import { useToast } from '@/hooks/use-toast';
import { formatDate } from '@/lib/utils';

export const dynamic = 'force-dynamic';

export default function AlbumsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterPublic, setFilterPublic] = useState<boolean | undefined>(undefined);
  const [currentPage, setCurrentPage] = useState(1);
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const limit = 12;

  // Fetch albums
  const { data: albumsData, isLoading } = useQuery({
    queryKey: ['albums', { page: currentPage, limit, search: searchQuery, is_public: filterPublic }],
    queryFn: async () => {
      const params: any = { page: currentPage, limit };
      if (searchQuery) params.search = searchQuery;
      if (filterPublic !== undefined) params.is_public = filterPublic;
      
      const response = await apiClient.get(endpoints.albums.list(params));
      return response.data;
    },
  });

  // Delete album mutation
  const deleteAlbumMutation = useMutation({
    mutationFn: async (albumId: string) => {
      await apiClient.delete(endpoints.albums.delete(albumId));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['albums'] });
      toast({
        title: 'Альбом удален',
        description: 'Альбом был успешно удален.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Ошибка удаления',
        description: error.message || 'Не удалось удалить альбом.',
        variant: 'destructive',
      });
    },
  });

  const handleDeleteAlbum = (albumId: string, albumTitle: string) => {
    if (confirm(`Вы уверены, что хотите удалить альбом "${albumTitle}"? Это действие нельзя отменить.`)) {
      deleteAlbumMutation.mutate(albumId);
    }
  };

  const albums = (albumsData as any)?.data || [];
  const totalPages = (albumsData as any)?.total_pages || 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Альбомы</h1>
          <p className="text-muted-foreground">
            Управляйте своими интерактивными альбомами
          </p>
        </div>
        <Link href="/dashboard/albums/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Создать альбом
          </Button>
        </Link>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex flex-col gap-4 md:flex-row md:items-center">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Поиск альбомов..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 w-full md:w-64"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  variant={filterPublic === undefined ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterPublic(undefined)}
                >
                  Все
                </Button>
                <Button
                  variant={filterPublic === true ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterPublic(true)}
                >
                  Публичные
                </Button>
                <Button
                  variant={filterPublic === false ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterPublic(false)}
                >
                  Приватные
                </Button>
              </div>
            </div>
            <div className="text-sm text-muted-foreground">
              {(albumsData as any)?.total || 0} альбомов
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Albums Grid */}
      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i}>
              <CardContent className="pt-6">
                <div className="h-48 bg-muted animate-pulse rounded" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : albums.length > 0 ? (
        <>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {albums.map((album: Album) => (
              <Card key={album.id} className="group hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-lg line-clamp-2 group-hover:text-primary transition-colors">
                        <Link href={`/dashboard/albums/${album.id}`}>
                          {album.title}
                        </Link>
                      </CardTitle>
                      {album.description && (
                        <CardDescription className="line-clamp-2 mt-1">
                          {album.description}
                        </CardDescription>
                      )}
                    </div>
                    <Badge variant={album.is_public ? 'default' : 'secondary'}>
                      {album.is_public ? 'Публичный' : 'Приватный'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  {/* Cover Image or Placeholder */}
                  <div className="aspect-video bg-muted rounded-lg mb-4 flex items-center justify-center">
                    {album.cover_image_url ? (
                      <img
                        src={album.cover_image_url}
                        alt={album.title}
                        className="w-full h-full object-cover rounded-lg"
                      />
                    ) : (
                      <FolderOpen className="h-12 w-12 text-muted-foreground" />
                    )}
                  </div>

                  {/* Stats */}
                  <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
                    <div className="flex items-center gap-4">
                      <span className="flex items-center gap-1">
                        <Eye className="h-3 w-3" />
                        {album.views_count}
                      </span>
                      <span>{album.pages_count} страниц</span>
                    </div>
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {formatDate(album.updated_at)}
                    </span>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-between">
                    <div className="flex gap-2">
                      <Link href={`/dashboard/albums/${album.id}`}>
                        <Button variant="outline" size="sm">
                          <Edit className="h-3 w-3 mr-1" />
                          Редактировать
                        </Button>
                      </Link>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          // Copy share link logic
                          const shareUrl = `${window.location.origin}/public/album/${album.id}`;
                          navigator.clipboard.writeText(shareUrl);
                          toast({
                            title: 'Ссылка скопирована',
                            description: 'Ссылка на альбом скопирована в буфер обмена.',
                          });
                        }}
                      >
                        <Share2 className="h-3 w-3 mr-1" />
                        Поделиться
                      </Button>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteAlbum(album.id, album.title)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
              >
                Назад
              </Button>
              <span className="text-sm text-muted-foreground">
                Страница {currentPage} из {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
              >
                Вперед
              </Button>
            </div>
          )}
        </>
      ) : (
        <Card>
          <CardContent className="pt-6 text-center">
            <FolderOpen className="mx-auto h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">
              {searchQuery || filterPublic !== undefined ? 'Альбомы не найдены' : 'Пока нет альбомов'}
            </h3>
            <p className="text-muted-foreground mb-6">
              {searchQuery || filterPublic !== undefined 
                ? 'Попробуйте изменить параметры поиска или фильтры'
                : 'Создайте свой первый альбом, чтобы начать работу'
              }
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
  );
}
