# План исправлений интеграции фронтенд-приложений

## Обзор

Данный документ содержит детальный план исправления критических проблем интеграции фронтенд-приложений с бэкенд API. План разбит на этапы по приоритету и временным рамкам.

## Критические исправления (День 1)

### 1. Исправление роутинга admin-api в API Gateway
**Приоритет**: 🚨 КРИТИЧЕСКИЙ  
**Время**: 2-3 часа  
**Файл**: `apps/api-gateway/app/routes/proxy.py`

#### Проблема
Отсутствует роут для проксирования admin-api запросов к микросервисам.

#### Решение
Добавить роут для admin-api в proxy.py:

```python
@router.api_route("/admin-api/{service_name}/{path:path}", 
                  methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_to_admin_service(
    service_name: str,
    path: str,
    request: Request
):
    """
    Проксирует admin-api запросы к микросервисам.
    """
    return await service_proxy.proxy_request(
        service_name=service_name,
        path=f"/{path}" if not path.startswith("/") else path,
        request=request,
        method=request.method
    )
```

#### Тестирование
```bash
# После исправления должно работать:
curl -H "Authorization: Bearer <admin-token>" \
     http://localhost:8080/admin-api/users

# Ожидаемый результат: проксирование к соответствующему микросервису
```

### 2. Исправление API Base URL в web приложении
**Приоритет**: 🚨 КРИТИЧЕСКИЙ  
**Время**: 1 час  
**Файл**: `apps/web/lib/env.ts`

#### Проблема
Неправильный дефолтный порт API Gateway.

#### Решение
```typescript
// apps/web/lib/env.ts
const envSchema = z.object({
  // БЫЛО: http://localhost:8000
  // СТАЛО: http://localhost:8080 (порт API Gateway)
  NEXT_PUBLIC_API_BASE_URL: z.string().url().default('http://localhost:8080'),
  // ... остальные поля
});
```

#### Обновление env.example
```bash
# apps/web/env.example
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
```

### 3. Устранение дублирования префиксов в endpoints
**Приоритет**: 🚨 КРИТИЧЕСКИЙ  
**Время**: 1-2 часа  
**Файл**: `apps/web/lib/endpoints.ts`

#### Проблема
Двойное добавление `/api/v1` в URL.

#### Решение (Вариант 1 - рекомендуемый)
```typescript
// apps/web/lib/endpoints.ts
const API_BASE = env.NEXT_PUBLIC_API_BASE_URL; // http://localhost:8080

export const endpoints = {
  auth: {
    // БЫЛО: `${API_BASE}/api/v1/auth/login`
    // СТАЛО: `${API_BASE}/api/v1/auth/login` (правильно)
    login: () => `${API_BASE}/api/v1/auth/login`,
    register: () => `${API_BASE}/api/v1/auth/register`,
    // ... остальные endpoints
  },
  // ... остальные разделы
};
```

#### Альтернативное решение (Вариант 2)
```typescript
// apps/web/lib/env.ts - включить префикс в базовый URL
NEXT_PUBLIC_API_BASE_URL: z.string().url().default('http://localhost:8080/api/v1'),

// apps/web/lib/endpoints.ts - убрать префикс из endpoints
export const endpoints = {
  auth: {
    login: () => `${API_BASE}/auth/login`, // без /api/v1
    register: () => `${API_BASE}/auth/register`,
    // ...
  },
};
```

**Рекомендация**: Использовать Вариант 1 для большей гибкости.

### 4. Обновление Error Register
**Время**: 30 минут

Добавить найденные проблемы в `audit/ERROR_REGISTER.md`:

| ID | Тип | Сервис | Описание | Приоритет | Статус |
|----|-----|--------|----------|-----------|---------|
| #audit-015 | Integration | api-gateway | Отсутствует роутинг admin-api в proxy | Критический | Открыт |
| #audit-016 | Integration | web-app | Неправильный API Base URL (порт 8000 вместо 8080) | Критический | Открыт |
| #audit-017 | Integration | web-app | Дублирование префиксов /api/v1 в endpoints | Критический | Открыт |

## Высокоприоритетные исправления (День 2)

### 5. Исправление аутентификации для health checks
**Приоритет**: 🟡 ВЫСОКИЙ  
**Время**: 1 час  
**Файл**: `apps/api-gateway/app/middleware/auth_middleware.py`

#### Решение
```python
self.exclude_paths = exclude_paths or [
    # ... существующие пути ...
    "/api/*/healthz",           # Health checks микросервисов
    "/admin-api/*/healthz",     # Health checks admin API
    "/api/services/*/health",   # Проверка здоровья через proxy
    "/admin-api/services/*/health", # Admin health checks
]
```

### 6. Добавление таймаутов в admin клиент
**Приоритет**: 🟡 ВЫСОКИЙ  
**Время**: 2 часа  
**Файл**: `apps/admin/lib/adminApi.ts`

#### Решение
```typescript
class AdminApiClient {
  private async request<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    // Добавить таймаут
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 секунд
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers
      });
      
      clearTimeout(timeoutId);
      // ... остальная логика
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new AdminApiError('Request timeout', 408);
      }
      throw error;
    }
  }
}
```

### 7. Валидация environment variables в admin
**Приоритет**: 🟡 ВЫСОКИЙ  
**Время**: 1 час  
**Файл**: `apps/admin/lib/env.ts` (новый файл)

#### Решение
```typescript
// apps/admin/lib/env.ts
import { z } from 'zod';

const envSchema = z.object({
  NEXT_PUBLIC_ADMIN_API_BASE_URL: z.string().url().default('http://localhost:8080/admin-api/v1'),
  NEXT_PUBLIC_PUBLIC_BASE_URL: z.string().url().default('https://storyqr.ru'),
  NEXT_PUBLIC_SHORT_BASE_URL: z.string().url().default('https://sqra.ru'),
  NEXT_PUBLIC_USE_MOCKS: z.string().transform(val => val === 'true').default('false'),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
});

export const env = envSchema.parse({
  NEXT_PUBLIC_ADMIN_API_BASE_URL: process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL,
  NEXT_PUBLIC_PUBLIC_BASE_URL: process.env.NEXT_PUBLIC_PUBLIC_BASE_URL,
  NEXT_PUBLIC_SHORT_BASE_URL: process.env.NEXT_PUBLIC_SHORT_BASE_URL,
  NEXT_PUBLIC_USE_MOCKS: process.env.NEXT_PUBLIC_USE_MOCKS,
  NODE_ENV: process.env.NODE_ENV,
});
```

## Средние исправления (Неделя 1)

### 8. Добавление retry механизма в admin клиент
**Приоритет**: 🟡 СРЕДНИЙ  
**Время**: 3 часа

#### Решение
Реализовать retry логику аналогично web клиенту:
```typescript
private async requestWithRetry<T>(
  url: string,
  options: RequestInit = {},
  retries = 3
): Promise<ApiResponse<T>> {
  try {
    return await this.request<T>(url, options);
  } catch (error) {
    if (retries > 0 && this.shouldRetry(error)) {
      await this.delay(1000 * (4 - retries)); // Exponential backoff
      return this.requestWithRetry<T>(url, options, retries - 1);
    }
    throw error;
  }
}
```

### 9. Улучшение обработки ошибок
**Приоритет**: 🟡 СРЕДНИЙ  
**Время**: 2 часа

#### Решение
Добавить более детальную обработку ошибок и логирование:
```typescript
// Централизованная обработка ошибок интеграции
class IntegrationErrorHandler {
  static handle(error: any, context: string) {
    console.error(`[${context}] Integration error:`, error);
    
    // Отправка в систему мониторинга
    if (typeof window !== 'undefined') {
      window.gtag?.('event', 'integration_error', {
        error_context: context,
        error_message: error.message,
      });
    }
  }
}
```

### 10. Добавление мониторинга интеграции
**Приоритет**: 🟡 СРЕДНИЙ  
**Время**: 4 часа

#### Решение
```typescript
// apps/web/lib/monitoring.ts
export class IntegrationMonitoring {
  static trackApiCall(endpoint: string, duration: number, status: number) {
    // Отправка метрик в систему мониторинга
    if (typeof window !== 'undefined') {
      window.gtag?.('event', 'api_call', {
        endpoint,
        duration,
        status,
        timestamp: Date.now(),
      });
    }
  }
  
  static trackError(error: any, context: string) {
    // Отправка ошибок в систему мониторинга
  }
}
```

## Долгосрочные улучшения (Неделя 2-4)

### 11. E2E тесты интеграции
**Приоритет**: 🟢 НИЗКИЙ  
**Время**: 1-2 дня

#### Решение
```typescript
// tests/e2e/integration.spec.ts
test('web app can authenticate and fetch data', async ({ page }) => {
  // Тест полного цикла аутентификации и получения данных
});

test('admin panel can manage users', async ({ page }) => {
  // Тест административных функций
});
```

### 12. Rate limiting на фронтенде
**Приоритет**: 🟢 НИЗКИЙ  
**Время**: 1 день

### 13. Кэширование в admin клиенте
**Приоритет**: 🟢 НИЗКИЙ  
**Время**: 2 дня

## План тестирования

### После каждого исправления

1. **Модульные тесты**:
```bash
npm test
```

2. **Интеграционные тесты**:
```bash
# Web app
curl http://localhost:3000/api/health
curl -X POST http://localhost:3000/api/auth/login

# Admin app  
curl http://localhost:3001/admin-api/users
curl -X POST http://localhost:3001/admin-api/auth/login
```

3. **E2E тесты**:
```bash
npm run test:e2e
```

### Финальная проверка

После всех исправлений выполнить полный цикл тестирования:

```bash
# 1. Запуск всех сервисов
docker-compose up -d

# 2. Проверка API Gateway
curl http://localhost:8080/healthz

# 3. Проверка web интеграции
curl http://localhost:8080/api/v1/auth/login
curl http://localhost:8080/api/auth/healthz

# 4. Проверка admin интеграции  
curl http://localhost:8080/admin-api/v1/auth/login
curl http://localhost:8080/admin-api/users

# 5. Запуск фронтенд приложений
cd apps/web && npm run dev &
cd apps/admin && npm run dev &

# 6. Проверка в браузере
open http://localhost:3000
open http://localhost:3001
```

## Критерии готовности

### Критические исправления ✅
- [ ] Admin-api роутинг работает
- [ ] Web app подключается к правильному порту
- [ ] Нет дублирования префиксов в URL
- [ ] Аутентификация работает в обеих приложениях

### Высокоприоритетные исправления ✅
- [ ] Health checks доступны без аутентификации
- [ ] Admin клиент имеет таймауты
- [ ] Environment variables валидируются

### Готовность к production 🚀
- [ ] Все критические исправления выполнены
- [ ] Интеграционные тесты проходят
- [ ] Мониторинг настроен
- [ ] Документация обновлена

## Временная шкала

```
День 1 (Критические):
├── 09:00-12:00: Роутинг admin-api
├── 13:00-14:00: API Base URL
├── 14:00-16:00: Дублирование префиксов
└── 16:00-17:00: Тестирование

День 2 (Высокие):
├── 09:00-10:00: Health checks
├── 10:00-12:00: Таймауты admin
├── 13:00-14:00: Валидация env
└── 14:00-17:00: Тестирование

Неделя 1-2 (Средние):
└── Retry, мониторинг, обработка ошибок

Неделя 2-4 (Долгосрочные):
└── E2E тесты, кэширование, rate limiting
```

## Риски и митигация

### Риск 1: Изменения ломают существующий функционал
**Митигация**: Поэтапное внедрение с тестированием после каждого изменения

### Риск 2: Проблемы с CORS после изменений
**Митигация**: Тщательная проверка CORS настроек после изменения URL

### Риск 3: Проблемы с аутентификацией
**Митигация**: Сохранение backup токенов, тестирование на dev окружении

## Заключение

**Общее время**: 3-5 дней для критических и высокоприоритетных исправлений.

**Результат**: Полностью работающая интеграция фронтенд-приложений с бэкенд API.

**Следующие шаги**: После завершения критических исправлений можно переходить к production деплою.

