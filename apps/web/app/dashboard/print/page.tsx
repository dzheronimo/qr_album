'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Printer, Download, Eye, Settings, FileText, QrCode } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function PrintPage() {
  const [selectedFormat, setSelectedFormat] = useState('a4');
  const [selectedQuality, setSelectedQuality] = useState('high');
  const { toast } = useToast();

  // Mock data for print jobs
  const printJobs = [
    {
      id: '1',
      name: 'QR Альбом - Семейные фото',
      type: 'album',
      pages: 12,
      status: 'completed',
      createdAt: '2025-09-09 14:30',
      downloadUrl: '#'
    },
    {
      id: '2',
      name: 'QR Коды - Бизнес карточки',
      type: 'qr_codes',
      pages: 1,
      status: 'processing',
      createdAt: '2025-09-09 14:25',
      downloadUrl: null
    },
    {
      id: '3',
      name: 'QR Альбом - Путешествия',
      type: 'album',
      pages: 8,
      status: 'failed',
      createdAt: '2025-09-09 14:20',
      downloadUrl: null
    }
  ];

  const handlePrint = () => {
    toast({
      title: 'Печать',
      description: 'Функция печати будет реализована в следующих версиях.',
    });
  };

  const handleDownload = (jobId: string) => {
    toast({
      title: 'Скачивание',
      description: 'Функция скачивания будет реализована в следующих версиях.',
    });
  };

  const handlePreview = (jobId: string) => {
    toast({
      title: 'Предварительный просмотр',
      description: 'Функция предварительного просмотра будет реализована в следующих версиях.',
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default" className="bg-green-500">Завершено</Badge>;
      case 'processing':
        return <Badge variant="secondary">Обработка</Badge>;
      case 'failed':
        return <Badge variant="destructive">Ошибка</Badge>;
      case 'pending':
        return <Badge variant="outline">Ожидание</Badge>;
      default:
        return <Badge variant="outline">Неизвестно</Badge>;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'album':
        return <FileText className="h-5 w-5" />;
      case 'qr_codes':
        return <QrCode className="h-5 w-5" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Печать</h1>
          <p className="text-muted-foreground">
            Создание и управление печатными материалами с QR-кодами
          </p>
        </div>
        <Button onClick={handlePrint} className="flex items-center gap-2">
          <Printer className="h-4 w-4" />
          Создать для печати
        </Button>
      </div>

      {/* Print Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Настройки печати
          </CardTitle>
          <CardDescription>
            Настройте параметры для создания печатных материалов
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Формат страницы</label>
              <Select value={selectedFormat} onValueChange={setSelectedFormat}>
                <SelectTrigger>
                  <SelectValue placeholder="Выберите формат" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="a4">A4 (210 × 297 мм)</SelectItem>
                  <SelectItem value="a5">A5 (148 × 210 мм)</SelectItem>
                  <SelectItem value="letter">Letter (8.5 × 11 дюймов)</SelectItem>
                  <SelectItem value="business_card">Визитная карточка</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Качество печати</label>
              <Select value={selectedQuality} onValueChange={setSelectedQuality}>
                <SelectTrigger>
                  <SelectValue placeholder="Выберите качество" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="draft">Черновик (быстро)</SelectItem>
                  <SelectItem value="normal">Обычное</SelectItem>
                  <SelectItem value="high">Высокое</SelectItem>
                  <SelectItem value="premium">Премиум</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Print Jobs */}
      <Card>
        <CardHeader>
          <CardTitle>Задачи печати</CardTitle>
          <CardDescription>
            История и статус ваших печатных задач
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {printJobs.map((job) => (
              <div key={job.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-4">
                  <div className="flex items-center justify-center w-10 h-10 bg-muted rounded-lg">
                    {getTypeIcon(job.type)}
                  </div>
                  <div>
                    <h3 className="font-medium">{job.name}</h3>
                    <p className="text-sm text-muted-foreground">
                      {job.pages} страниц • {job.createdAt}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {getStatusBadge(job.status)}
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handlePreview(job.id)}
                    >
                      <Eye className="h-3 w-3" />
                    </Button>
                    {job.downloadUrl && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDownload(job.id)}
                      >
                        <Download className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="hover:shadow-md transition-shadow cursor-pointer">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <FileText className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h3 className="font-semibold">QR Альбом</h3>
                <p className="text-sm text-muted-foreground">
                  Создать печатный альбом с QR-кодами
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow cursor-pointer">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <QrCode className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h3 className="font-semibold">QR Коды</h3>
                <p className="text-sm text-muted-foreground">
                  Создать отдельные QR-коды для печати
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow cursor-pointer">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
                <Printer className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h3 className="font-semibold">Настройки</h3>
                <p className="text-sm text-muted-foreground">
                  Настроить параметры печати
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

