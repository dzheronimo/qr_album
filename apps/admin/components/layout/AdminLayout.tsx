'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Sidebar } from '@/components/nav/Sidebar';
import { adminApi } from '@/lib/adminApi';
import { AdminUser } from '@/lib/rbac';

interface AdminLayoutProps {
  children: React.ReactNode;
}

export function AdminLayout({ children }: AdminLayoutProps) {
  const [user, setUser] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await adminApi.getMe();
        setUser(response.data);
      } catch (error) {
        console.error('Auth check failed:', error);
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  return (
    <div className="min-h-screen flex">
      <Sidebar userRole={user.role} />
      <main className="admin-main">
        <div className="admin-header">
          <div>
            <h2 className="text-lg font-semibold">Добро пожаловать, {user.name}</h2>
            <p className="text-sm text-muted-foreground">
              Роль: {user.role}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-muted-foreground">
              Последний вход: {user.lastLoginAt ? new Date(user.lastLoginAt).toLocaleString('ru-RU') : 'Неизвестно'}
            </div>
          </div>
        </div>
        <div className="admin-content">
          {children}
        </div>
      </main>
    </div>
  );
}


