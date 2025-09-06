'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { adminApi } from '@/lib/adminApi';
import { formatDate, formatCurrency, formatNumber } from '@/lib/utils';
import { Search, Filter, Download, Eye, Pause, Play } from 'lucide-react';

export default function EventsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [planFilter, setPlanFilter] = useState('');
  const [page, setPage] = useState(1);
  const limit = 10;

  const { data: eventsData, isLoading, error } = useQuery({
    queryKey: ['events', { searchQuery, statusFilter, planFilter, page, limit }],
    queryFn: () => adminApi.getEvents({
      status: statusFilter || undefined,
      plan: planFilter || undefined,
      page,
      limit,
    }),
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="success">Активно</Badge>;
      case 'trial':
        return <Badge variant="warning">Триал</Badge>;
      case 'expired':
        return <Badge variant="destructive">Истекло</Badge>;
      case 'paused':
        return <Badge variant="secondary">Приостановлено</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getPlanBadge = (plan: string) => {
    switch (plan) {
      case 'lite':
        return <Badge variant="outline">Lite</Badge>;
      case 'comfort':
        return <Badge variant="default">Comfort</Badge>;
      case 'premium':
        return <Badge variant="secondary">Premium</Badge>;
      case 'trial':
        return <Badge variant="warning">Триал</Badge>;
      default:
        return <Badge variant="outline">{plan}</Badge>;
    }
  };

  if (error) {
    return (
      <AdminLayout>
        <div className="text-center py-8">
          <p className="text-red-600">Ошибка загрузки событий</p>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">События</h1>
          <p className="text-muted-foreground">
            Управление событиями и их настройками
          </p>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle>Фильтры и поиск</CardTitle>
            <CardDescription>
              Найдите события по различным критериям
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSearch} className="flex gap-4 items-end">
              <div className="flex-1">
                <label htmlFor="search" className="block text-sm font-medium mb-1">
                  Поиск
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="search"
                    placeholder="Название события или email владельца"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="status" className="block text-sm font-medium mb-1">
                  Статус
                </label>
                <select
                  id="status"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="h-10 px-3 py-2 border border-input bg-background rounded-md text-sm"
                >
                  <option value="">Все статусы</option>
                  <option value="active">Активные</option>
                  <option value="trial">Триал</option>
                  <option value="expired">Истекшие</option>
                  <option value="paused">Приостановленные</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="plan" className="block text-sm font-medium mb-1">
                  План
                </label>
                <select
                  id="plan"
                  value={planFilter}
                  onChange={(e) => setPlanFilter(e.target.value)}
                  className="h-10 px-3 py-2 border border-input bg-background rounded-md text-sm"
                >
                  <option value="">Все планы</option>
                  <option value="trial">Триал</option>
                  <option value="lite">Lite</option>
                  <option value="comfort">Comfort</option>
                  <option value="premium">Premium</option>
                </select>
              </div>
              
              <Button type="submit">
                <Filter className="h-4 w-4 mr-2" />
                Применить
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Events Table */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Список событий</CardTitle>
              <CardDescription>
                {eventsData?.pagination?.total || 0} событий найдено
              </CardDescription>
            </div>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Экспорт CSV
            </Button>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="mt-2 text-muted-foreground">Загрузка событий...</p>
              </div>
            ) : (
              <div className="space-y-4">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Событие</TableHead>
                      <TableHead>Владелец</TableHead>
                      <TableHead>План</TableHead>
                      <TableHead>Статус</TableHead>
                      <TableHead>Загрузки</TableHead>
                      <TableHead>Просмотры</TableHead>
                      <TableHead>Размер</TableHead>
                      <TableHead>До</TableHead>
                      <TableHead>Действия</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {eventsData?.data?.map((event: any) => (
                      <TableRow key={event.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{event.title}</div>
                            <div className="text-sm text-muted-foreground">
                              {event.visibility === 'public' ? 'Публичное' : 'Приватное'}
                              {event.hasPin && ' • PIN'}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div>
                            <div className="font-medium">{event.owner.name}</div>
                            <div className="text-sm text-muted-foreground">{event.owner.email}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          {getPlanBadge(event.plan)}
                        </TableCell>
                        <TableCell>
                          {getStatusBadge(event.status)}
                        </TableCell>
                        <TableCell>
                          {formatNumber(event.uploadsCount)}
                        </TableCell>
                        <TableCell>
                          {formatNumber(event.viewsCount)}
                        </TableCell>
                        <TableCell>
                          {event.sizeGB.toFixed(1)} GB
                        </TableCell>
                        <TableCell>
                          {formatDate(event.storageUntil)}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <Eye className="h-4 w-4" />
                            </Button>
                            {event.uploadWindowActive ? (
                              <Button size="sm" variant="outline">
                                <Pause className="h-4 w-4" />
                              </Button>
                            ) : (
                              <Button size="sm" variant="outline">
                                <Play className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                {/* Pagination */}
                {eventsData?.pagination && eventsData.pagination.totalPages > 1 && (
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-muted-foreground">
                      Показано {((page - 1) * limit) + 1}-{Math.min(page * limit, eventsData.pagination.total)} из {eventsData.pagination.total}
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={page === 1}
                        onClick={() => setPage(page - 1)}
                      >
                        Назад
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        disabled={page >= eventsData.pagination.totalPages}
                        onClick={() => setPage(page + 1)}
                      >
                        Вперед
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
}
