'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  QrCode, 
  Download, 
  Copy, 
  Share2, 
  ExternalLink,
  RefreshCw
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { endpoints } from '@/lib/api';
import { QRCode } from '@/types';

interface QrPreviewProps {
  qrCode: QRCode;
  pageTitle: string;
  onRegenerate?: () => void;
  className?: string;
}

export function QrPreview({ qrCode, pageTitle, onRegenerate, className }: QrPreviewProps) {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleDownload = async (format: 'png' | 'svg') => {
    try {
      setIsLoading(true);
      const imageUrl = endpoints.qr.image(qrCode.id, { format });
      
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `qr-code-${pageTitle}-${format}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast({
        title: 'Файл скачан',
        description: `QR-код сохранен в формате ${format.toUpperCase()}.`,
      });
    } catch (error) {
      toast({
        title: 'Ошибка скачивания',
        description: 'Не удалось скачать QR-код.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(qrCode.short_url);
    toast({
      title: 'Ссылка скопирована',
      description: 'Короткая ссылка скопирована в буфер обмена.',
    });
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `QR-код для ${pageTitle}`,
          text: `Посмотрите контент: ${pageTitle}`,
          url: qrCode.short_url,
        });
      } catch (error) {
        // Fallback to copy
        handleCopyLink();
      }
    } else {
      handleCopyLink();
    }
  };

  const handleOpenLink = () => {
    window.open(qrCode.short_url, '_blank');
  };

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <QrCode className="h-5 w-5" />
              QR-код страницы
            </CardTitle>
            <CardDescription>
              QR-код для страницы "{pageTitle}"
            </CardDescription>
          </div>
          {onRegenerate && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRegenerate}
              disabled={isLoading}
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* QR Code Image */}
        <div className="text-center">
          <div className="inline-block p-4 bg-white rounded-lg border shadow-sm">
            <img
              src={qrCode.qr_image_url}
              alt={`QR-код для ${pageTitle}`}
              className="w-48 h-48"
            />
          </div>
        </div>

        {/* Short URL */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Короткая ссылка:</label>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={qrCode.short_url}
              readOnly
              className="flex-1 px-3 py-2 text-sm border rounded-md bg-muted"
            />
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopyLink}
            >
              <Copy className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleOpenLink}
            >
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-3">
          <div className="flex gap-2">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => handleDownload('png')}
              disabled={isLoading}
            >
              <Download className="mr-2 h-4 w-4" />
              PNG
            </Button>
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => handleDownload('svg')}
              disabled={isLoading}
            >
              <Download className="mr-2 h-4 w-4" />
              SVG
            </Button>
          </div>
          
          <Button
            className="w-full"
            onClick={handleShare}
          >
            <Share2 className="mr-2 h-4 w-4" />
            Поделиться
          </Button>
        </div>

        {/* Info */}
        <div className="text-xs text-muted-foreground space-y-1">
          <p>• QR-код создан: {new Date(qrCode.created_at).toLocaleDateString('ru-RU')}</p>
          <p>• Ссылка ведет на публичную страницу</p>
          <p>• QR-код можно печатать на наклейках</p>
        </div>
      </CardContent>
    </Card>
  );
}
