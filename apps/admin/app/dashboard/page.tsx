'use client';

export const dynamic = 'force-dynamic';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatCurrency, formatNumber, formatDate } from '@/lib/utils';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { 
  Users, 
  Calendar, 
  DollarSign, 
  TrendingUp, 
  HardDrive, 
  Download,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

// Mock data - в реальном приложении будет загружаться через API
const mockKPIs = {
  revenueMTD: 125000,
  ordersMTD: 45,
  activeTrials: 12,
  activeEvents: 8,
  storageGB: 1250,
  egressGB: 320,
};

const mockRecentEvents = [
  {
    id: '1',
    title: 'Свадьба Анны и Михаила',
    owner: 'anna@example.com',
    status: 'active',
    createdAt: '2025-09-06T10:00:00Z',
  },
  {
    id: '2',
    title: 'День рождения Марии',
    owner: 'maria@example.com',
    status: 'trial',
    createdAt: '2025-09-05T15:30:00Z',
  },
];

const mockRecentTickets = [
  {
    id: '1',
    subject: 'Проблема с загрузкой фото',
    user: 'user@example.com',
    status: 'open',
    priority: 'high',
    createdAt: '2025-09-06T09:15:00Z',
  },
  {
    id: '2',
    subject: 'Вопрос по тарифам',
    user: 'client@example.com',
    status: 'open',
    priority: 'medium',
    createdAt: '2025-09-06T08:45:00Z',
  },
];

const mockPrintOrders = [
  {
    id: '1',
    type: 'cards',
    quantity: 100,
    status: 'overdue',
    dueDate: '2025-09-04T00:00:00Z',
  },
  {
    id: '2',
    type: 'signs',
    quantity: 10,
    status: 'processing',
    dueDate: '2025-09-08T00:00:00Z',
  },
];

export default function DashboardPage() {
  return (
    <AdminLayout>
      <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Обзор ключевых показателей и активности
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Выручка MTD</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(mockKPIs.revenueMTD)}
            </div>
            <p className="text-xs text-muted-foreground">
              +12% с прошлого месяца
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Заказы MTD</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(mockKPIs.ordersMTD)}
            </div>
            <p className="text-xs text-muted-foreground">
              +8% с прошлого месяца
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Активные триалы</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(mockKPIs.activeTrials)}
            </div>
            <p className="text-xs text-muted-foreground">
              3 истекают в течение недели
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Активные события</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(mockKPIs.activeEvents)}
            </div>
            <p className="text-xs text-muted-foreground">
              На этой неделе
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Storage</CardTitle>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(mockKPIs.storageGB)} ГБ
            </div>
            <p className="text-xs text-muted-foreground">
              +5% за неделю
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Egress</CardTitle>
            <Download className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(mockKPIs.egressGB)} ГБ
            </div>
            <p className="text-xs text-muted-foreground">
              За текущий месяц
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Events */}
        <Card>
          <CardHeader>
            <CardTitle>События с активацией сегодня</CardTitle>
            <CardDescription>
              Новые события, активированные сегодня
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {mockRecentEvents.map((event) => (
              <div key={event.id} className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{event.title}</p>
                  <p className="text-sm text-muted-foreground">
                    {event.owner}
                  </p>
                </div>
                <Badge variant={event.status === 'active' ? 'success' : 'warning'}>
                  {event.status === 'active' ? 'Активно' : 'Триал'}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Recent Tickets */}
        <Card>
          <CardHeader>
            <CardTitle>Новые тикеты</CardTitle>
            <CardDescription>
              Последние обращения в поддержку
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {mockRecentTickets.map((ticket) => (
              <div key={ticket.id} className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{ticket.subject}</p>
                  <p className="text-sm text-muted-foreground">
                    {ticket.user}
                  </p>
                </div>
                <Badge 
                  variant={ticket.priority === 'high' ? 'destructive' : 'secondary'}
                >
                  {ticket.priority === 'high' ? 'Высокий' : 'Средний'}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Print Orders */}
        <Card>
          <CardHeader>
            <CardTitle>Печатные заказы</CardTitle>
            <CardDescription>
              Статус печатных заказов
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {mockPrintOrders.map((order) => (
              <div key={order.id} className="flex items-center justify-between">
                <div>
                  <p className="font-medium">
                    {order.type === 'cards' ? 'Карточки' : 'Таблички'} 
                    ({order.quantity} шт.)
                  </p>
                  <p className="text-sm text-muted-foreground">
                    До: {formatDate(order.dueDate)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {order.status === 'overdue' ? (
                    <AlertTriangle className="h-4 w-4 text-red-500" />
                  ) : (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  )}
                  <Badge variant={order.status === 'overdue' ? 'destructive' : 'success'}>
                    {order.status === 'overdue' ? 'Просрочен' : 'В работе'}
                  </Badge>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
      </div>
    </AdminLayout>
  );
}
