'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { QrCode, RefreshCw, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { healthCheck } from '@/lib/api';

interface ServiceStatus {
  name: string;
  url: string;
  status: 'healthy' | 'unhealthy' | 'checking';
  responseTime?: number;
  error?: string;
}

export default function StatusPage() {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'API Gateway', url: '/api/v1/health', status: 'checking' },
    { name: 'Auth Service', url: '/api/v1/auth/health', status: 'checking' },
    { name: 'Album Service', url: '/api/v1/albums/health', status: 'checking' },
    { name: 'Media Service', url: '/api/v1/media/health', status: 'checking' },
    { name: 'QR Service', url: '/api/v1/qr/health', status: 'checking' },
  ]);
  const [isChecking, setIsChecking] = useState(false);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkServiceHealth = async (service: ServiceStatus): Promise<ServiceStatus> => {
    try {
      const startTime = Date.now();
      const response = await fetch(service.url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      const responseTime = Date.now() - startTime;

      if (response.ok) {
        return {
          ...service,
          status: 'healthy',
          responseTime,
        };
      } else {
        return {
          ...service,
          status: 'unhealthy',
          responseTime,
          error: `HTTP ${response.status}`,
        };
      }
    } catch (error) {
      return {
        ...service,
        status: 'unhealthy',
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  };

  const checkAllServices = async () => {
    setIsChecking(true);
    setServices(prev => prev.map(service => ({ ...service, status: 'checking' as const })));

    const results = await Promise.all(
      services.map(service => checkServiceHealth(service))
    );

    setServices(results);
    setLastChecked(new Date());
    setIsChecking(false);
  };

  useEffect(() => {
    checkAllServices();
  }, []);

  const getStatusIcon = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'unhealthy':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'checking':
        return <RefreshCw className="h-4 w-4 text-yellow-500 animate-spin" />;
    }
  };

  const getStatusBadge = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'healthy':
        return <Badge variant="default" className="bg-green-100 text-green-800">Работает</Badge>;
      case 'unhealthy':
        return <Badge variant="destructive">Недоступен</Badge>;
      case 'checking':
        return <Badge variant="secondary">Проверка...</Badge>;
    }
  };

  const overallStatus = services.every(s => s.status === 'healthy') 
    ? 'healthy' 
    : services.some(s => s.status === 'unhealthy') 
    ? 'unhealthy' 
    : 'checking';

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center space-x-2 mb-4">
            <QrCode className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold">StoryQR</span>
          </div>
          <h1 className="text-3xl font-bold mb-2">Статус системы</h1>
          <p className="text-muted-foreground">
            Мониторинг состояния всех сервисов платформы
          </p>
        </div>

        {/* Overall Status */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Общий статус
              <div className="flex items-center space-x-2">
                {getStatusIcon(overallStatus)}
                {getStatusBadge(overallStatus)}
              </div>
            </CardTitle>
            <CardDescription>
              {lastChecked && `Последняя проверка: ${lastChecked.toLocaleString('ru-RU')}`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {overallStatus === 'healthy' && (
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Все сервисы работают нормально. Платформа полностью доступна.
                </AlertDescription>
              </Alert>
            )}
            {overallStatus === 'unhealthy' && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  Обнаружены проблемы с некоторыми сервисами. Мы работаем над их устранением.
                </AlertDescription>
              </Alert>
            )}
            {overallStatus === 'checking' && (
              <Alert>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <AlertDescription>
                  Проверяем состояние сервисов...
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Services Status */}
        <div className="grid gap-4 md:grid-cols-2">
          {services.map((service, index) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  {service.name}
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(service.status)}
                    {getStatusBadge(service.status)}
                  </div>
                </CardTitle>
                <CardDescription>
                  {service.url}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {service.responseTime && (
                  <p className="text-sm text-muted-foreground mb-2">
                    Время отклика: {service.responseTime}мс
                  </p>
                )}
                {service.error && (
                  <p className="text-sm text-destructive">
                    Ошибка: {service.error}
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Actions */}
        <div className="mt-8 text-center">
          <Button 
            onClick={checkAllServices} 
            disabled={isChecking}
            className="mr-4"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isChecking ? 'animate-spin' : ''}`} />
            Обновить статус
          </Button>
          <Button variant="outline" asChild>
            <a href="/">На главную</a>
          </Button>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-muted-foreground">
          <p>
            Если проблемы продолжаются, обратитесь в{' '}
            <a href="mailto:support@storyqr.ru" className="text-primary hover:underline">
              службу поддержки
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
