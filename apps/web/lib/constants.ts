import { BillingPlan, PrintSku } from '@/types';

export const DEFAULT_PLANS: BillingPlan[] = [
  {
    id: 'lite',
    name: 'Lite',
    description: '3 месяца загрузок / 1 год хранения',
    price_rub: 1990,
    price_eur: 24,
    upload_months: 3,
    storage_years: 1,
    features: ['Безлимит гостей', 'До 3 месяцев загрузок', 'QR-код и PIN', 'Базовая аналитика'],
  },
  {
    id: 'plus',
    name: 'Plus',
    description: '6 месяцев загрузок / 2 года хранения',
    price_rub: 3490,
    price_eur: 39,
    upload_months: 6,
    storage_years: 2,
    is_popular: true,
    features: ['Все из Lite', 'Живое слайдшоу', 'Совместные админы', 'Экспорт ZIP'],
  },
  {
    id: 'pro',
    name: 'Pro',
    description: '12 месяцев загрузок / 3 года хранения',
    price_rub: 5990,
    price_eur: 69,
    upload_months: 12,
    storage_years: 3,
    features: ['Все из Plus', 'Приоритетная поддержка', 'Кастомный домен', 'Расширенная аналитика'],
  },
];

export const DEFAULT_PRINT_SKUS: PrintSku[] = [
  { sku: 'cards-100', name: 'Мини-карточки 100 шт', price_rub: 1490, price_eur: 18, kind: 'cards', description: 'Карточки 55×85 мм, плотная бумага' },
  { sku: 'signs-10', name: 'Таблички 10 шт', price_rub: 2390, price_eur: 27, kind: 'signs', description: 'Настольные таблички 5×7" для входа и столов' },
];

export const TRIAL_CONFIG = {
  duration_days: 7,
  max_uploads: 5,
  features: ['Полный функционал платформы', 'Создание альбомов и страниц', 'Генерация QR-кодов', 'Базовая аналитика'],
};

export const FAQ_DATA = [
  { question: 'Нужна ли подписка?', answer: 'Нет, у нас разовая оплата за событие без автопродления.' },
  { question: 'Можно ли сменить тариф позже?', answer: 'Да, апгрейд тарифа доступен в любой момент в личном кабинете.' },
  { question: 'Есть ли бесплатный период?', answer: 'Да, 7 дней теста с лимитом до 5 загрузок.' },
];

export const COMPARISON_DATA = {
  features: ['Безлимит гостей', 'Печать QR-карточек', 'PIN-защита', 'Русскоязычная поддержка'],
  competitors: [
    { name: 'StoryQR', features: [true, true, true, true] },
    { name: 'Конкурент A', features: [true, false, true, false] },
    { name: 'Конкурент B', features: [false, false, false, false] },
  ],
};
