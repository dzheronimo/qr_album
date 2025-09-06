'use client';

export const dynamic = 'force-dynamic';

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
import { Search, Filter, Download, Ban, UserCheck, Eye } from 'lucide-react';

export default function UsersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [planFilter, setPlanFilter] = useState('');
  const [page, setPage] = useState(1);
  const limit = 10;

  const { data: usersData, isLoading, error } = useQuery({
    queryKey: ['users', { searchQuery, roleFilter, planFilter, page, limit }],
    queryFn: () => adminApi.getUsers({
      query: searchQuery || undefined,
      role: roleFilter || undefined,
      plan: planFilter || undefined,
      page,
      limit,
    }),
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
  };

  const handleBanUser = async (userId: string) => {
    if (confirm('Вы уверены, что хотите заблокировать этого пользователя?')) {
      try {
        await adminApi.banUser(userId);
        // Refetch data
        window.location.reload();
      } catch (error) {
        console.error('Failed to ban user:', error);
      }
    }
  };

  const handleUnbanUser = async (userId: string) => {
    if (confirm('Вы уверены, что хотите разблокировать этого пользователя?')) {
      try {
        await adminApi.unbanUser(userId);
        // Refetch data
        window.location.reload();
      } catch (error) {
        console.error('Failed to unban user:', error);
      }
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="default">Активен</Badge>;
      case 'trial':
        return <Badge variant="warning">Триал</Badge>;
      case 'banned':
        return <Badge variant="destructive">Заблокирован</Badge>;
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
          <p className="text-red-600">Ошибка загрузки пользователей</p>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Пользователи</h1>
          <p className="text-muted-foreground">
            Управление пользователями системы
          </p>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle>Фильтры и поиск</CardTitle>
            <CardDescription>
              Найдите пользователей по различным критериям
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
                    placeholder="Email или имя пользователя"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="role" className="block text-sm font-medium mb-1">
                  Роль
                </label>
                <select
                  id="role"
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value)}
                  className="h-10 px-3 py-2 border border-input bg-background rounded-md text-sm"
                >
                  <option value="">Все роли</option>
                  <option value="user">Пользователь</option>
                  <option value="admin">Администратор</option>
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

        {/* Users Table */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Список пользователей</CardTitle>
              <CardDescription>
                {usersData?.pagination.total || 0} пользователей найдено
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
                <p className="mt-2 text-muted-foreground">Загрузка пользователей...</p>
              </div>
            ) : (
              <div className="space-y-4">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Пользователь</TableHead>
                      <TableHead>Роль</TableHead>
                      <TableHead>План</TableHead>
                      <TableHead>Статус</TableHead>
                      <TableHead>События</TableHead>
                      <TableHead>Потрачено</TableHead>
                      <TableHead>Последний вход</TableHead>
                      <TableHead>Действия</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {usersData?.data.map((user: any) => (
                      <TableRow key={user.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{user.name}</div>
                            <div className="text-sm text-muted-foreground">{user.email}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{user.role}</Badge>
                        </TableCell>
                        <TableCell>
                          {getPlanBadge(user.plan)}
                        </TableCell>
                        <TableCell>
                          {getStatusBadge(user.status)}
                        </TableCell>
                        <TableCell>
                          {formatNumber(user.eventsCount)}
                        </TableCell>
                        <TableCell>
                          {formatCurrency(user.totalSpent)}
                        </TableCell>
                        <TableCell>
                          {user.lastLoginAt ? formatDate(user.lastLoginAt) : 'Никогда'}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline">
                              <Eye className="h-4 w-4" />
                            </Button>
                            {user.status === 'banned' ? (
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => handleUnbanUser(user.id)}
                              >
                                <UserCheck className="h-4 w-4" />
                              </Button>
                            ) : (
                              <Button 
                                size="sm" 
                                variant="destructive"
                                onClick={() => handleBanUser(user.id)}
                              >
                                <Ban className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                {/* Pagination */}
                {usersData?.pagination && usersData.pagination.totalPages > 1 && (
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-muted-foreground">
                      Показано {((page - 1) * limit) + 1}-{Math.min(page * limit, usersData.pagination.total)} из {usersData.pagination.total}
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
                        disabled={page >= usersData.pagination.totalPages}
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


