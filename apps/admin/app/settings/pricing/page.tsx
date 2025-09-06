'use client';

export const dynamic = 'force-dynamic';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { AdminLayout } from '@/components/layout/AdminLayout';
import { adminApi } from '@/lib/adminApi';
import { formatCurrency } from '@/lib/utils';
import { Save, Plus, Trash2, Edit } from 'lucide-react';

interface Plan {
  id: string;
  name: string;
  priceRub: number;
  priceEur: number;
  uploadMonths: number;
  storageYears: number;
  active: boolean;
}

export default function PricingSettingsPage() {
  const [editingPlan, setEditingPlan] = useState<Plan | null>(null);
  const [isAddingNew, setIsAddingNew] = useState(false);
  const queryClient = useQueryClient();

  const { data: pricingData, isLoading } = useQuery({
    queryKey: ['settings', 'pricing'],
    queryFn: () => adminApi.getSettingsPricing(),
  });

  const updatePricingMutation = useMutation({
    mutationFn: (data: any) => adminApi.updateSettingsPricing(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'pricing'] });
      setEditingPlan(null);
      setIsAddingNew(false);
    },
  });

  const handleSave = (planData: Partial<Plan>) => {
    const plans = pricingData?.data?.plans || [];
    let updatedPlans;

    if (isAddingNew) {
      // Add new plan
      const newPlan = {
        id: `plan_${Date.now()}`,
        ...planData,
        active: true,
      };
      updatedPlans = [...plans, newPlan];
    } else if (editingPlan) {
      // Update existing plan
      updatedPlans = plans.map((plan: Plan) =>
        plan.id === editingPlan.id ? { ...plan, ...planData } : plan
      );
    }

    updatePricingMutation.mutate({ plans: updatedPlans });
  };

  const handleDelete = (planId: string) => {
    if (confirm('Вы уверены, что хотите удалить этот план?')) {
      const plans = pricingData?.data?.plans || [];
      const updatedPlans = plans.filter((plan: Plan) => plan.id !== planId);
      updatePricingMutation.mutate({ plans: updatedPlans });
    }
  };

  const togglePlanStatus = (planId: string) => {
    const plans = pricingData?.data?.plans || [];
    const updatedPlans = plans.map((plan: Plan) =>
      plan.id === planId ? { ...plan, active: !plan.active } : plan
    );
    updatePricingMutation.mutate({ plans: updatedPlans });
  };

  if (isLoading) {
    return (
      <AdminLayout>
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Загрузка настроек...</p>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Настройки тарифов</h1>
          <p className="text-muted-foreground">
            Управление тарифными планами и ценами
          </p>
        </div>

        <div className="flex justify-between items-center">
          <div className="text-sm text-muted-foreground">
            {pricingData?.data?.plans?.length || 0} планов настроено
          </div>
          <Button onClick={() => setIsAddingNew(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Добавить план
          </Button>
        </div>

        {/* Plans Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {pricingData?.data?.plans?.map((plan: Plan) => (
            <Card key={plan.id} className={!plan.active ? 'opacity-60' : ''}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xl">{plan.name}</CardTitle>
                  <div className="flex gap-2">
                    <Badge variant={plan.active ? 'success' : 'secondary'}>
                      {plan.active ? 'Активен' : 'Неактивен'}
                    </Badge>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setEditingPlan(plan)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <CardDescription>
                  {plan.uploadMonths} месяцев загрузок, {plan.storageYears} лет хранения
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Цена (RUB):</span>
                    <span className="font-semibold">{formatCurrency(plan.priceRub)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Цена (EUR):</span>
                    <span className="font-semibold">€{plan.priceEur}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Загрузки:</span>
                    <span className="font-semibold">{plan.uploadMonths} мес.</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Хранение:</span>
                    <span className="font-semibold">{plan.storageYears} лет</span>
                  </div>
                  
                  <div className="flex gap-2 pt-4">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => togglePlanStatus(plan.id)}
                    >
                      {plan.active ? 'Деактивировать' : 'Активировать'}
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleDelete(plan.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Edit/Add Plan Modal */}
        {(editingPlan || isAddingNew) && (
          <Card>
            <CardHeader>
              <CardTitle>
                {isAddingNew ? 'Добавить новый план' : 'Редактировать план'}
              </CardTitle>
              <CardDescription>
                {isAddingNew ? 'Создайте новый тарифный план' : 'Измените параметры плана'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <PlanForm
                plan={editingPlan}
                onSave={handleSave}
                onCancel={() => {
                  setEditingPlan(null);
                  setIsAddingNew(false);
                }}
                isLoading={updatePricingMutation.isPending}
              />
            </CardContent>
          </Card>
        )}
      </div>
    </AdminLayout>
  );
}

interface PlanFormProps {
  plan?: Plan | null;
  onSave: (data: Partial<Plan>) => void;
  onCancel: () => void;
  isLoading: boolean;
}

function PlanForm({ plan, onSave, onCancel, isLoading }: PlanFormProps) {
  const [formData, setFormData] = useState({
    name: plan?.name || '',
    priceRub: plan?.priceRub || 0,
    priceEur: plan?.priceEur || 0,
    uploadMonths: plan?.uploadMonths || 1,
    storageYears: plan?.storageYears || 1,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium mb-1">
            Название плана
          </label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
            placeholder="Например: Lite"
          />
        </div>
        
        <div>
          <label htmlFor="priceRub" className="block text-sm font-medium mb-1">
            Цена (RUB)
          </label>
          <Input
            id="priceRub"
            type="number"
            value={formData.priceRub}
            onChange={(e) => setFormData({ ...formData, priceRub: parseInt(e.target.value) || 0 })}
            required
            min="0"
          />
        </div>
        
        <div>
          <label htmlFor="priceEur" className="block text-sm font-medium mb-1">
            Цена (EUR)
          </label>
          <Input
            id="priceEur"
            type="number"
            value={formData.priceEur}
            onChange={(e) => setFormData({ ...formData, priceEur: parseInt(e.target.value) || 0 })}
            required
            min="0"
          />
        </div>
        
        <div>
          <label htmlFor="uploadMonths" className="block text-sm font-medium mb-1">
            Месяцы загрузок
          </label>
          <Input
            id="uploadMonths"
            type="number"
            value={formData.uploadMonths}
            onChange={(e) => setFormData({ ...formData, uploadMonths: parseInt(e.target.value) || 1 })}
            required
            min="1"
          />
        </div>
        
        <div>
          <label htmlFor="storageYears" className="block text-sm font-medium mb-1">
            Годы хранения
          </label>
          <Input
            id="storageYears"
            type="number"
            value={formData.storageYears}
            onChange={(e) => setFormData({ ...formData, storageYears: parseInt(e.target.value) || 1 })}
            required
            min="1"
          />
        </div>
      </div>
      
      <div className="flex gap-2 pt-4">
        <Button type="submit" disabled={isLoading}>
          <Save className="h-4 w-4 mr-2" />
          {isLoading ? 'Сохранение...' : 'Сохранить'}
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          Отмена
        </Button>
      </div>
    </form>
  );
}


