'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Printer, 
  Download, 
  Settings,
  Grid3X3,
  Ruler
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { apiClient, endpoints } from '@/lib/api';
import { CreatePrintJobRequest, PrintTemplate } from '@/types';

interface LabelSheetConfiguratorProps {
  qrCodes: string[];
  onJobCreated?: (jobId: string) => void;
  className?: string;
}

export function LabelSheetConfigurator({ 
  qrCodes, 
  onJobCreated, 
  className 
}: LabelSheetConfiguratorProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [config, setConfig] = useState({
    labelSize: '35mm' as '35mm' | '50mm',
    gridSize: '5x10',
    margin: 5,
    bleed: 2,
  });
  const { toast } = useToast();

  const gridOptions = [
    { value: '5x10', label: '5×10 (50 наклеек)', size: '35mm' },
    { value: '4x8', label: '4×8 (32 наклейки)', size: '50mm' },
    { value: '3x6', label: '3×6 (18 наклеек)', size: '50mm' },
    { value: '2x4', label: '2×4 (8 наклеек)', size: '50mm' },
  ];

  const handleConfigChange = (key: string, value: any) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const handleCreatePrintJob = async () => {
    if (qrCodes.length === 0) {
      toast({
        title: 'Нет QR-кодов',
        description: 'Выберите QR-коды для печати.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    try {
      const request: CreatePrintJobRequest = {
        template_id: 'default', // You might want to fetch available templates
        qr_codes: qrCodes,
        label_size: config.labelSize,
        grid_size: config.gridSize,
        margin: config.margin,
        bleed: config.bleed,
      };

      const response = await apiClient.post(endpoints.print.jobs(), request);
      const jobId = response.data.id;

      toast({
        title: 'Задание создано',
        description: 'PDF для печати создается. Вы получите уведомление когда он будет готов.',
      });

      onJobCreated?.(jobId);
    } catch (error: any) {
      toast({
        title: 'Ошибка создания задания',
        description: error.message || 'Не удалось создать задание для печати.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const selectedGridOption = gridOptions.find(option => option.value === config.gridSize);
  const totalLabels = selectedGridOption ? 
    parseInt(selectedGridOption.value.split('x')[0]) * parseInt(selectedGridOption.value.split('x')[1]) : 0;

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Printer className="h-5 w-5" />
          Настройки печати
        </CardTitle>
        <CardDescription>
          Настройте параметры для создания PDF с QR-кодами
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* QR Codes Count */}
        <div className="p-4 bg-muted rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">QR-кодов для печати:</span>
            <span className="text-lg font-bold">{qrCodes.length}</span>
          </div>
        </div>

        {/* Label Size */}
        <div className="space-y-2">
          <Label htmlFor="labelSize">Размер наклейки</Label>
          <Select
            value={config.labelSize}
            onValueChange={(value: '35mm' | '50mm') => handleConfigChange('labelSize', value)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="35mm">35×35 мм</SelectItem>
              <SelectItem value="50mm">50×50 мм</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Grid Size */}
        <div className="space-y-2">
          <Label htmlFor="gridSize">Сетка на листе</Label>
          <Select
            value={config.gridSize}
            onValueChange={(value) => handleConfigChange('gridSize', value)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {gridOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-xs text-muted-foreground">
            Всего наклеек на листе: {totalLabels}
          </p>
        </div>

        {/* Margin */}
        <div className="space-y-2">
          <Label htmlFor="margin">Отступы (мм)</Label>
          <Input
            id="margin"
            type="number"
            min="0"
            max="20"
            value={config.margin}
            onChange={(e) => handleConfigChange('margin', parseInt(e.target.value) || 0)}
          />
          <p className="text-xs text-muted-foreground">
            Отступы от краев листа
          </p>
        </div>

        {/* Bleed */}
        <div className="space-y-2">
          <Label htmlFor="bleed">Bleed (мм)</Label>
          <Input
            id="bleed"
            type="number"
            min="0"
            max="10"
            value={config.bleed}
            onChange={(e) => handleConfigChange('bleed', parseInt(e.target.value) || 0)}
          />
          <p className="text-xs text-muted-foreground">
            Дополнительная область для обрезки
          </p>
        </div>

        {/* Preview Info */}
        <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
          <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
            Предварительный просмотр
          </h4>
          <div className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
            <p>• Размер наклейки: {config.labelSize}</p>
            <p>• Сетка: {config.gridSize}</p>
            <p>• Всего наклеек на листе: {totalLabels}</p>
            <p>• Количество листов: {Math.ceil(qrCodes.length / totalLabels)}</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button
            className="flex-1"
            onClick={handleCreatePrintJob}
            disabled={isLoading || qrCodes.length === 0}
          >
            {isLoading ? (
              'Создание PDF...'
            ) : (
              <>
                <Download className="mr-2 h-4 w-4" />
                Создать PDF
              </>
            )}
          </Button>
        </div>

        {/* Tips */}
        <div className="text-xs text-muted-foreground space-y-1">
          <p>• PDF будет создан в высоком качестве для печати</p>
          <p>• QR-коды будут автоматически масштабированы</p>
          <p>• Рекомендуется использовать плотную бумагу</p>
        </div>
      </CardContent>
    </Card>
  );
}
