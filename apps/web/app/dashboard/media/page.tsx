'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Upload, Search, Filter, Download, Trash2, Eye } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function MediaPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMedia, setSelectedMedia] = useState<string[]>([]);
  const { toast } = useToast();

  // Mock data for demonstration
  const mediaItems = [
    {
      id: '1',
      name: 'photo1.jpg',
      type: 'image',
      size: '2.3 MB',
      uploadedAt: '2025-09-09',
      status: 'active'
    },
    {
      id: '2', 
      name: 'video1.mp4',
      type: 'video',
      size: '15.7 MB',
      uploadedAt: '2025-09-08',
      status: 'active'
    },
    {
      id: '3',
      name: 'document.pdf',
      type: 'document',
      size: '1.2 MB',
      uploadedAt: '2025-09-07',
      status: 'processing'
    }
  ];

  const handleUpload = () => {
    toast({
      title: 'Загрузка файлов',
      description: 'Функция загрузки будет реализована в следующих версиях.',
    });
  };

  const handleDelete = (id: string) => {
    toast({
      title: 'Удаление файла',
      description: 'Функция удаления будет реализована в следующих версиях.',
    });
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'image':
        return '🖼️';
      case 'video':
        return '🎥';
      case 'document':
        return '📄';
      default:
        return '📁';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="default" className="bg-green-500">Активен</Badge>;
      case 'processing':
        return <Badge variant="secondary">Обработка</Badge>;
      case 'error':
        return <Badge variant="destructive">Ошибка</Badge>;
      default:
        return <Badge variant="outline">Неизвестно</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Медиа файлы</h1>
          <p className="text-muted-foreground">
            Управление медиа файлами для ваших QR-альбомов
          </p>
        </div>
        <Button onClick={handleUpload} className="flex items-center gap-2">
          <Upload className="h-4 w-4" />
          Загрузить файлы
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Поиск и фильтры
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Поиск по имени файла..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            <Button variant="outline" className="flex items-center gap-2">
              <Filter className="h-4 w-4" />
              Фильтры
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Media Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {mediaItems
          .filter(item => 
            item.name.toLowerCase().includes(searchTerm.toLowerCase())
          )
          .map((item) => (
            <Card key={item.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{getTypeIcon(item.type)}</span>
                    <div>
                      <CardTitle className="text-sm truncate max-w-[150px]">
                        {item.name}
                      </CardTitle>
                      <CardDescription className="text-xs">
                        {item.size} • {item.uploadedAt}
                      </CardDescription>
                    </div>
                  </div>
                  {getStatusBadge(item.status)}
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" className="flex-1">
                    <Eye className="h-3 w-3 mr-1" />
                    Просмотр
                  </Button>
                  <Button size="sm" variant="outline">
                    <Download className="h-3 w-3" />
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleDelete(item.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
      </div>

      {/* Empty State */}
      {mediaItems.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Upload className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Нет медиа файлов</h3>
            <p className="text-muted-foreground text-center mb-4">
              Загрузите ваши первые медиа файлы для создания QR-альбомов
            </p>
            <Button onClick={handleUpload}>
              <Upload className="h-4 w-4 mr-2" />
              Загрузить файлы
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

