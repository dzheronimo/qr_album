import { http, HttpResponse } from 'msw';
import { DEFAULT_PLANS, DEFAULT_PRINT_SKUS } from '@/lib/constants';

// Моки для API endpoints
export const handlers = [
  // Billing endpoints
  http.get('/api/v1/billing/plans', () => {
    return HttpResponse.json({
      plans: DEFAULT_PLANS,
    });
  }),

  http.get('/api/v1/billing/limits', () => {
    return HttpResponse.json({
      uploads_left: 5,
      storage_until: '2024-12-31T23:59:59Z',
      tier: 'trial',
      trial: {
        active: true,
        days_left: 5,
        uploads_left: 3,
      },
    });
  }),

  // Trial endpoints
  http.post('/api/v1/trial/start', () => {
    return HttpResponse.json({
      active: true,
      ends_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      uploads_left: 5,
    });
  }),

  http.get('/api/v1/trial/status', () => {
    return HttpResponse.json({
      active: true,
      ends_at: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(),
      uploads_left: 3,
    });
  }),

  // Orders endpoints
  http.post('/api/v1/orders', async ({ request }) => {
    const body = await request.json() as any;
    
    // Симулируем создание заказа
    const orderId = `order_${Date.now()}`;
    const paymentUrl = `https://payment.example.com/checkout/${orderId}`;
    
    return HttpResponse.json({
      id: orderId,
      payment_url: paymentUrl,
    });
  }),

  http.get('/api/v1/orders/:id', ({ params }) => {
    const { id } = params;
    
    // Симулируем статус заказа
    const statuses = ['pending', 'paid', 'failed'];
    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
    
    return HttpResponse.json({
      status: randomStatus,
    });
  }),

  // Print SKUs
  http.get('/api/v1/print/skus', () => {
    return HttpResponse.json(DEFAULT_PRINT_SKUS);
  }),

  // Analytics endpoint (для трекинга событий)
  http.post('/api/analytics', () => {
    // Просто возвращаем успех для трекинга
    return HttpResponse.json({ success: true });
  }),

  // Auth endpoints (базовые)
  http.post('/api/v1/auth/login', async ({ request }) => {
    const body = await request.json() as any;
    
    // Простая проверка
    if (body.email && body.password) {
      return HttpResponse.json({
        access_token: 'mock_access_token',
        refresh_token: 'mock_refresh_token',
        user: {
          id: 'user_123',
          email: body.email,
          name: 'Test User',
        },
      });
    }
    
    return HttpResponse.json(
      { message: 'Invalid credentials' },
      { status: 401 }
    );
  }),

  http.post('/api/v1/auth/register', async ({ request }) => {
    const body = await request.json() as any;
    
    // Простая регистрация
    if (body.email && body.password) {
      return HttpResponse.json({
        access_token: 'mock_access_token',
        refresh_token: 'mock_refresh_token',
        user: {
          id: 'user_123',
          email: body.email,
          name: body.name || 'New User',
        },
      });
    }
    
    return HttpResponse.json(
      { message: 'Invalid data' },
      { status: 400 }
    );
  }),

  // Error simulation endpoints (для тестирования ошибок)
  http.get('/api/v1/billing/plans/error', () => {
    return HttpResponse.json(
      { message: 'Service temporarily unavailable' },
      { status: 503 }
    );
  }),

  http.get('/api/v1/billing/plans/timeout', () => {
    // Симулируем таймаут
    return new Promise(() => {});
  }),
];


