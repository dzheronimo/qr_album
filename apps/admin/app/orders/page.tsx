'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { adminApi } from '@/lib/adminApi';
import { formatDate, formatCurrency } from '@/lib/utils';
import { Search, Filter, Download, Check, RefreshCw, Eye, Receipt } from 'lucide-react';

export default function OrdersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [providerFilter, setProviderFilter] = useState('');
  const [page, setPage] = useState(1);
  const limit = 10;
  const queryClient = useQueryClient();

  const { data: ordersData, isLoading, error } = useQuery({
    queryKey: ['orders', { searchQuery, statusFilter, providerFilter, page, limit }],
    queryFn: () => adminApi.getOrders({
      status: statusFilter || undefined,
      provider: providerFilter || undefined,
      page,
      limit,
    }),
  });

  const markPaidMutation = useMutation({
    mutationFn: (id: string) => adminApi.markOrderPaid(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
  });

  const refundMutation = useMutation({
    mutationFn: ({ id, amount }: { id: string; amount?: number }) => 
      adminApi.refundOrder(id, amount),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
  });

  const resendReceiptMutation = useMutation({
    mutationFn: (id: string) => adminApi.resendReceipt(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
  };

  const handleMarkPaid = (id: string) => {
    if (confirm('Отметить заказ как оплаченный?')) {
      markPaidMutation.mutate(id);
    }
  };

  const handleRefund = (id: string) => {
    const amount = prompt('Сумма возврата (оставьте пустым для полного возврата):');
    if (amount !== null) {
      const refundAmount = amount ? parseFloat(amount) : undefined;
      refundMutation.mutate({ id, amount: refundAmount });
    }
  };

  const handleResendReceipt = (id: string) => {
    if (confirm('Повторно отправить чек?')) {
      resendReceiptMutation.mutate(id);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'paid':
        return <Badge variant="success">Оплачен</Badge>;
      case 'pending':
        return <Badge variant="warning">Ожидает</Badge>;
      case 'failed':
        return <Badge variant="destructive">Ошибка</Badge>;
      case 'refunded':
        return <Badge variant="secondary">Возврат</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getProviderBadge = (provider: string) => {
    switch (provider) {
      case 'yookassa':
        return <Badge variant="outline">ЮKassa</Badge>;
      case 'stripe':
        return <Badge variant="outline">Stripe</Badge>;
      case 'paypal':
        return <Badge variant="outline">PayPal</Badge>;
      default:
        return <Badge variant="outline">{provider}</Badge>;
    }
  };

  if (error) {
    return (
      <AdminLayout>
        <div className="text-center py-8">
          <p className="text-red-600">Ошибка загрузки заказов</p>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Заказы</h1>
          <p className="text-muted-foreground">
            Управление заказами и платежами
          </p>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle>Фильтры и поиск</CardTitle>
            <CardDescription>
              Найдите заказы по различным критериям
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
                    placeholder="ID заказа или email пользователя"
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
                  <option value="paid">Оплачен</option>
                  <option value="pending">Ожидает</option>
                  <option value="failed">Ошибка</option>
                  <option value="refunded">Возврат</option>
                </select>
              </div>
              
              <div>
                <label htmlFor="provider" className="block text-sm font-medium mb-1">
                  Провайдер
                </label>
                <select
                  id="provider"
                  value={providerFilter}
                  onChange={(e) => setProviderFilter(e.target.value)}
                  className="h-10 px-3 py-2 border border-input bg-background rounded-md text-sm"
                >
                  <option value="">Все провайдеры</option>
                  <option value="yookassa">ЮKassa</option>
                  <option value="stripe">Stripe</option>
                  <option value="paypal">PayPal</option>
                </select>
              </div>
              
              <Button type="submit">
                <Filter className="h-4 w-4 mr-2" />
                Применить
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Orders Table */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Список заказов</CardTitle>
              <CardDescription>
                {ordersData?.pagination?.total || 0} заказов найдено
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
                <p className="mt-2 text-muted-foreground">Загрузка заказов...</p>
              </div>
            ) : (
              <div className="space-y-4">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Заказ</TableHead>
                      <TableHead>Пользователь</TableHead>
                      <TableHead>План</TableHead>
                      <TableHead>Сумма</TableHead>
                      <TableHead>Статус</TableHead>
                      <TableHead>Провайдер</TableHead>
                      <TableHead>Дополнения</TableHead>
                      <TableHead>Создан</TableHead>
                      <TableHead>Действия</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {ordersData?.data?.map((order: any) => (
                      <TableRow key={order.id}>
                        <TableCell>
                          <div className="font-medium">#{order.id}</div>
                        </TableCell>
                        <TableCell>
                          <div>
                            <div className="font-medium">{order.userEmail}</div>
                            <div className="text-sm text-muted-foreground">ID: {order.userId}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{order.plan}</Badge>
                        </TableCell>
                        <TableCell>
                          {formatCurrency(order.amount, order.currency as 'RUB' | 'EUR')}
                        </TableCell>
                        <TableCell>
                          {getStatusBadge(order.status)}
                        </TableCell>
                        <TableCell>
                          {getProviderBadge(order.provider)}
                        </TableCell>
                        <TableCell>
                          {order.addons?.length > 0 ? (
                            <div className="text-sm">
                              {order.addons.map((addon: any, index: number) => (
                                <div key={index}>
                                  {addon.name} (×{addon.quantity})
                                </div>
                              ))}
                            </div>
                          ) : (
                            <span className="text-muted-foreground">Нет</span>
                          )}
                        </TableCell>
                        <TableCell>
                          {formatDate(order.createdAt)}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <Eye className="h-4 w-4" />
                            </Button>
                            {order.status === 'pending' && (
                              <Button 
                                size="sm" 
                                variant="success"
                                onClick={() => handleMarkPaid(order.id)}
                                disabled={markPaidMutation.isPending}
                              >
                                <Check className="h-4 w-4" />
                              </Button>
                            )}
                            {order.status === 'paid' && (
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => handleRefund(order.id)}
                                disabled={refundMutation.isPending}
                              >
                                <RefreshCw className="h-4 w-4" />
                              </Button>
                            )}
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => handleResendReceipt(order.id)}
                              disabled={resendReceiptMutation.isPending}
                            >
                              <Receipt className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                {/* Pagination */}
                {ordersData?.pagination && ordersData.pagination.totalPages > 1 && (
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-muted-foreground">
                      Показано {((page - 1) * limit) + 1}-{Math.min(page * limit, ordersData.pagination.total)} из {ordersData.pagination.total}
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
                        disabled={page >= ordersData.pagination.totalPages}
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
