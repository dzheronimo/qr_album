'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  LayoutDashboard,
  Users,
  Calendar,
  Image,
  ShoppingCart,
  Printer,
  BarChart3,
  QrCode,
  Bell,
  Settings,
  FileText,
  Shield,
  HelpCircle,
  LogOut
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { adminApi } from '@/lib/adminApi';
import { useRouter } from 'next/navigation';

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    roles: ['superadmin', 'ops', 'support', 'sales', 'moderator', 'analyst', 'printer'],
  },
  {
    name: 'Пользователи',
    href: '/users',
    icon: Users,
    roles: ['superadmin', 'ops', 'support', 'sales', 'moderator'],
  },
  {
    name: 'События',
    href: '/events',
    icon: Calendar,
    roles: ['superadmin', 'ops', 'support', 'sales', 'printer'],
  },
  {
    name: 'Модерация медиа',
    href: '/media/moderation',
    icon: Image,
    roles: ['superadmin', 'ops', 'moderator'],
  },
  {
    name: 'Заказы',
    href: '/orders',
    icon: ShoppingCart,
    roles: ['superadmin', 'ops', 'support', 'sales'],
  },
  {
    name: 'Печатные заказы',
    href: '/print-orders',
    icon: Printer,
    roles: ['superadmin', 'ops', 'printer'],
  },
  {
    name: 'Аналитика',
    href: '/analytics',
    icon: BarChart3,
    roles: ['superadmin', 'ops', 'sales', 'analyst'],
  },
  {
    name: 'QR коды',
    href: '/qr',
    icon: QrCode,
    roles: ['superadmin', 'ops'],
  },
  {
    name: 'Уведомления',
    href: '/notifications/templates',
    icon: Bell,
    roles: ['superadmin', 'ops', 'support', 'sales'],
  },
  {
    name: 'Настройки',
    href: '/settings/pricing',
    icon: Settings,
    roles: ['superadmin', 'ops', 'sales'],
  },
  {
    name: 'Система',
    href: '/system/logs',
    icon: FileText,
    roles: ['superadmin', 'ops'],
  },
  {
    name: 'Поддержка',
    href: '/support/tickets',
    icon: HelpCircle,
    roles: ['superadmin', 'ops', 'support'],
  },
  {
    name: 'Аудит',
    href: '/access/audit',
    icon: Shield,
    roles: ['superadmin', 'ops'],
  },
];

interface SidebarProps {
  userRole?: string;
}

export function Sidebar({ userRole = 'superadmin' }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await adminApi.logout();
      router.push('/login');
    } catch (error) {
      console.error('Logout error:', error);
      router.push('/login');
    }
  };

  const filteredNavigation = navigation.filter(item => 
    item.roles.includes(userRole as any)
  );

  return (
    <div className="admin-sidebar h-screen flex flex-col">
      <div className="p-6 border-b border-border">
        <h1 className="text-xl font-bold">StoryQR Admin</h1>
        <p className="text-sm text-muted-foreground">Панель управления</p>
      </div>
      
      <nav className="flex-1 p-4 space-y-2">
        {filteredNavigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent'
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>
      
      <div className="p-4 border-t border-border">
        <Button
          variant="ghost"
          className="w-full justify-start gap-3"
          onClick={handleLogout}
        >
          <LogOut className="h-4 w-4" />
          Выйти
        </Button>
      </div>
    </div>
  );
}


