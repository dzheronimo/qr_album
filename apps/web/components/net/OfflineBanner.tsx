'use client';

import { useState, useEffect } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Wifi, WifiOff } from 'lucide-react';

/**
 * Компонент для отображения статуса соединения с интернетом
 */
export function OfflineBanner() {
  const [isOnline, setIsOnline] = useState(true);
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    // Проверяем начальный статус
    setIsOnline(navigator.onLine);

    // Обработчики событий
    const handleOnline = () => {
      setIsOnline(true);
      // Скрываем баннер через 3 секунды после восстановления соединения
      setTimeout(() => setShowBanner(false), 3000);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowBanner(true);
    };

    // Добавляем слушатели
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Очистка
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Не показываем баннер, если соединение есть
  if (isOnline || !showBanner) {
    return null;
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50 p-4">
      <Alert variant="warning" className="max-w-md mx-auto">
        <WifiOff className="h-4 w-4" />
        <AlertDescription>
          Нет соединения с интернетом. Проверьте подключение к сети.
        </AlertDescription>
      </Alert>
    </div>
  );
}

/**
 * Компонент для отображения статуса восстановления соединения
 */
export function OnlineBanner() {
  const [isOnline, setIsOnline] = useState(true);
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setShowBanner(true);
      // Скрываем баннер через 3 секунды
      setTimeout(() => setShowBanner(false), 3000);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowBanner(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (!isOnline || !showBanner) {
    return null;
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50 p-4">
      <Alert variant="success" className="max-w-md mx-auto">
        <Wifi className="h-4 w-4" />
        <AlertDescription>
          Соединение с интернетом восстановлено.
        </AlertDescription>
      </Alert>
    </div>
  );
}

/**
 * Комбинированный компонент для отображения статуса соединения
 */
export function ConnectionStatusBanner() {
  return (
    <>
      <OfflineBanner />
      <OnlineBanner />
    </>
  );
}
