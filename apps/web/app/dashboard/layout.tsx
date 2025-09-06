'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  QrCode, 
  LayoutDashboard, 
  FolderOpen, 
  Settings, 
  LogOut,
  Bell,
  User,
  Menu,
  X
} from 'lucide-react';
import { authManager } from '@/lib/auth';

import { User as UserType } from '@/types';

export const dynamic = 'force-dynamic';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [user, setUser] = useState<UserType | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const authState = authManager.getAuthState();
    setUser(authState.user);
    setIsAuthenticated(authState.isAuthenticated);

    if (!authState.isAuthenticated) {
      router.push('/auth/login');
      return;
    }

    // Subscribe to auth changes
    const unsubscribe = authManager.subscribe(() => {
      const newAuthState = authManager.getAuthState();
      setUser(newAuthState.user);
      setIsAuthenticated(newAuthState.isAuthenticated);
      
      if (!newAuthState.isAuthenticated) {
        router.push('/auth/login');
      }
    });

    return unsubscribe;
  }, [router]);

  const handleLogout = () => {
    authManager.logout();
    router.push('/');
  };

  if (!isAuthenticated) {
    return null; // Will redirect to login
  }

  const navigation = [
    { name: 'Обзор', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Альбомы', href: '/dashboard/albums', icon: FolderOpen },
    { name: 'Настройки', href: '/dashboard/settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
        <div className="fixed left-0 top-0 h-full w-64 bg-background border-r">
          <div className="flex h-16 items-center justify-between px-4 border-b">
            <Link href="/" className="flex items-center space-x-2">
              <QrCode className="h-6 w-6 text-primary" />
              <span className="font-bold">StoryQR</span>
            </Link>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <nav className="mt-4 px-4">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className="flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium hover:bg-accent"
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon className="h-4 w-4" />
                <span>{item.name}</span>
              </Link>
            ))}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-background border-r px-6 pb-4">
          <div className="flex h-16 shrink-0 items-center">
            <Link href="/" className="flex items-center space-x-2">
              <QrCode className="h-6 w-6 text-primary" />
              <span className="font-bold">StoryQR</span>
            </Link>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        href={item.href}
                        className="flex items-center gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold hover:bg-accent"
                      >
                        <item.icon className="h-4 w-4 shrink-0" />
                        {item.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-4 w-4" />
          </Button>

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1" />
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              {/* Notifications */}
              <Button variant="ghost" size="icon">
                <Bell className="h-4 w-4" />
              </Button>

              {/* User menu */}
              <div className="flex items-center gap-x-2">
                <div className="flex items-center gap-x-2">
                  <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <User className="h-4 w-4 text-primary" />
                  </div>
                  <div className="hidden lg:block">
                    <p className="text-sm font-medium">{user?.first_name || user?.username || 'Пользователь'}</p>
                    <p className="text-xs text-muted-foreground">{user?.email}</p>
                  </div>
                </div>
                <Button variant="ghost" size="icon" onClick={handleLogout}>
                  <LogOut className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
