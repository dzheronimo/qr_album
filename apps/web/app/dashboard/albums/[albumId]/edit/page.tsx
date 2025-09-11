'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, Save, Eye } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface Album {
  id: number;
  title: string;
  description: string | null;
  status: string;
  is_public: boolean;
  cover_image_url: string | null;
  tags: string | null;
  created_at: string;
  updated_at: string;
  published_at: string | null;
  pages_count: number;
}

export default function EditAlbumPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const albumId = params.albumId as string;

  const [album, setAlbum] = useState<Album | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    is_public: false,
    tags: ''
  });

  useEffect(() => {
    if (albumId) {
      fetchAlbum();
    }
  }, [albumId]);

  const fetchAlbum = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/albums/${albumId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch album');
      }

      const data = await response.json();
      setAlbum(data);
      setFormData({
        title: data.title || '',
        description: data.description || '',
        is_public: data.is_public || false,
        tags: data.tags || ''
      });
    } catch (error) {
      console.error('Error fetching album:', error);
      toast({
        title: 'Ошибка',
        description: 'Ошибка загрузки альбома',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await fetch(`/api/v1/albums/${albumId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Failed to update album');
      }

      toast({
        title: 'Успех',
        description: 'Альбом успешно обновлен'
      });
      router.push(`/dashboard/albums/${albumId}`);
    } catch (error) {
      console.error('Error updating album:', error);
      toast({
        title: 'Ошибка',
        description: 'Ошибка обновления альбома',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };

  const handlePreview = () => {
    router.push(`/dashboard/albums/${albumId}`);
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
            <p className="mt-2 text-gray-600">Загрузка альбома...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!album) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Альбом не найден</h1>
          <Button onClick={() => router.push('/dashboard/albums')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Вернуться к альбомам
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            onClick={() => router.push('/dashboard/albums')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Назад
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Редактирование альбома</h1>
            <p className="text-gray-600">ID: {album.id}</p>
          </div>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={handlePreview}
          >
            <Eye className="w-4 h-4 mr-2" />
            Предпросмотр
          </Button>
          <Button
            onClick={handleSave}
            disabled={saving}
          >
            <Save className="w-4 h-4 mr-2" />
            {saving ? 'Сохранение...' : 'Сохранить'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Основная информация</CardTitle>
              <CardDescription>
                Редактируйте основную информацию об альбоме
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label htmlFor="title">Название альбома</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Введите название альбома"
                />
              </div>

              <div>
                <Label htmlFor="description">Описание</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Введите описание альбома"
                  rows={4}
                />
              </div>

              <div>
                <Label htmlFor="tags">Теги</Label>
                <Input
                  id="tags"
                  value={formData.tags}
                  onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                  placeholder="Введите теги через запятую"
                />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Настройки</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is_public"
                  checked={formData.is_public}
                  onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                  className="rounded"
                />
                <Label htmlFor="is_public">Публичный альбом</Label>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Статистика</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Статус:</span>
                <span className="font-medium capitalize">{album.status}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Страниц:</span>
                <span className="font-medium">{album.pages_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Создан:</span>
                <span className="font-medium">
                  {new Date(album.created_at).toLocaleDateString('ru-RU')}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Обновлен:</span>
                <span className="font-medium">
                  {new Date(album.updated_at).toLocaleDateString('ru-RU')}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
