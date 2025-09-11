import { test, expect } from '@playwright/test';

test.describe('Login Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
  });

  test('login-success.spec: корректный редирект и отсутствуют ошибки', async ({ page }) => {
    // Мокаем успешный ответ API
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            access_token: 'mock-access-token',
            refresh_token: 'mock-refresh-token',
            token_type: 'bearer',
            expires_in: 3600,
            user: {
              id: '1',
              email: 'test@example.com',
              username: 'testuser',
              is_verified: true
            }
          }
        })
      });
    });

    // Заполняем форму
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');

    // Отправляем форму
    await page.click('button[type="submit"]');

    // Проверяем редирект на dashboard
    await expect(page).toHaveURL('/dashboard');

    // Проверяем отсутствие ошибок
    await expect(page.locator('[role="alert"]')).not.toBeVisible();
    await expect(page.locator('.text-destructive')).not.toBeVisible();
  });

  test('login-wrong-pass.spec: 401 → инлайн-алерт «Неверный email или пароль»', async ({ page }) => {
    // Мокаем 401 ошибку
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          error: {
            code: 'INVALID_CREDENTIALS',
            message: 'Invalid email or password'
          }
        })
      });
    });

    // Заполняем форму
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'wrongpassword');

    // Отправляем форму
    await page.click('button[type="submit"]');

    // Проверяем появление inline alert
    const alert = page.locator('[role="alert"]');
    await expect(alert).toBeVisible();
    await expect(alert).toContainText('Неверный email или пароль');

    // Проверяем, что это именно inline alert, а не toast
    await expect(alert).toHaveClass(/border-destructive/);
    
    // Проверяем, что форма остается на странице
    await expect(page).toHaveURL('/auth/login');
  });

  test('login-validation.spec: пустые поля → подсветка, без тоста', async ({ page }) => {
    // Отправляем пустую форму
    await page.click('button[type="submit"]');

    // Проверяем подсветку полей
    const emailInput = page.locator('input[name="email"]');
    const passwordInput = page.locator('input[name="password"]');

    await expect(emailInput).toHaveClass(/border-destructive/);
    await expect(passwordInput).toHaveClass(/border-destructive/);

    // Проверяем сообщения об ошибках под полями
    await expect(page.locator('text=Введите корректный email')).toBeVisible();
    await expect(page.locator('text=Пароль должен содержать минимум 6 символов')).toBeVisible();

    // Проверяем отсутствие toast
    await expect(page.locator('[data-radix-toast-viewport]')).not.toBeVisible();
  });

  test('login-rate-limit.spec: мок 429 → тост с «Попробуйте через …»', async ({ page }) => {
    // Мокаем 429 ошибку с retry-after
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 429,
        headers: {
          'Retry-After': '60'
        },
        contentType: 'application/json',
        body: JSON.stringify({
          error: {
            code: 'RATE_LIMITED',
            message: 'Too many requests'
          }
        })
      });
    });

    // Заполняем форму
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');

    // Отправляем форму
    await page.click('button[type="submit"]');

    // Проверяем появление toast
    const toast = page.locator('[data-radix-toast-viewport]');
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('Слишком много попыток');

    // Проверяем кнопку "Повторить" в toast
    await expect(toast.locator('button:has-text("Повторить")')).toBeVisible();
  });

  test('login-server-down.spec: мок 503 → тост «Сервис недоступен», кнопка «Повторить»', async ({ page }) => {
    // Мокаем 503 ошибку
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({
          error: {
            code: 'SERVICE_UNAVAILABLE',
            message: 'Service temporarily unavailable'
          }
        })
      });
    });

    // Заполняем форму
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');

    // Отправляем форму
    await page.click('button[type="submit"]');

    // Проверяем появление toast
    const toast = page.locator('[data-radix-toast-viewport]');
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('Сервис временно недоступен');

    // Проверяем кнопку "Повторить"
    const retryButton = toast.locator('button:has-text("Повторить")');
    await expect(retryButton).toBeVisible();

    // Тестируем функциональность кнопки "Повторить"
    // Мокаем успешный ответ для повторного запроса
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            access_token: 'mock-access-token',
            refresh_token: 'mock-refresh-token',
            token_type: 'bearer',
            expires_in: 3600,
            user: { id: '1', email: 'test@example.com' }
          }
        })
      });
    });

    await retryButton.click();
    await expect(page).toHaveURL('/dashboard');
  });

  test('login-offline.spec: симуляция offline → баннер «Нет соединения»', async ({ page }) => {
    // Симулируем offline состояние
    await page.context().setOffline(true);

    // Заполняем форму
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');

    // Отправляем форму
    await page.click('button[type="submit"]');

    // Проверяем появление offline баннера
    const offlineBanner = page.locator('text=Нет соединения с интернетом');
    await expect(offlineBanner).toBeVisible();

    // Проверяем появление toast с сетевой ошибкой
    const toast = page.locator('[data-radix-toast-viewport]');
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('Нет соединения с сервером');

    // Восстанавливаем соединение
    await page.context().setOffline(false);

    // Проверяем появление online баннера
    const onlineBanner = page.locator('text=Соединение с интернетом восстановлено');
    await expect(onlineBanner).toBeVisible();
  });

  test('login-timeout.spec: превышение timeout → тост с сообщением о timeout', async ({ page }) => {
    // Мокаем медленный ответ (больше 7 секунд)
    await page.route('**/api/v1/auth/login', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 8000)); // 8 секунд
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true })
      });
    });

    // Заполняем форму
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');

    // Отправляем форму
    await page.click('button[type="submit"]');

    // Ждем появления toast с timeout ошибкой
    const toast = page.locator('[data-radix-toast-viewport]');
    await expect(toast).toBeVisible({ timeout: 10000 });
    await expect(toast).toContainText('Превышено время ожидания');
  });

  test('login-escape-cancel.spec: отмена загрузки по Escape', async ({ page }) => {
    // Мокаем медленный ответ
    await page.route('**/api/v1/auth/login', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 5000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true })
      });
    });

    // Заполняем форму
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');

    // Отправляем форму
    await page.click('button[type="submit"]');

    // Проверяем, что кнопка показывает "Вход..."
    await expect(page.locator('button[type="submit"]')).toContainText('Вход...');

    // Нажимаем Escape
    await page.keyboard.press('Escape');

    // Проверяем, что кнопка вернулась в исходное состояние
    await expect(page.locator('button[type="submit"]')).toContainText('Войти');
    await expect(page.locator('button[type="submit"]')).not.toBeDisabled();
  });

  test('login-accessibility.spec: доступность для screen readers', async ({ page }) => {
    // Заполняем форму с неверными данными
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'wrongpassword');

    // Мокаем 401 ошибку
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          error: { message: 'Invalid credentials' }
        })
      });
    });

    // Отправляем форму
    await page.click('button[type="submit"]');

    // Проверяем, что alert имеет правильные ARIA атрибуты
    const alert = page.locator('[role="alert"]');
    await expect(alert).toBeVisible();
    await expect(alert).toHaveAttribute('role', 'alert');

    // Проверяем, что alert получает фокус для screen readers
    await expect(alert).toBeFocused();
  });

  test('login-form-validation.spec: валидация полей в реальном времени', async ({ page }) => {
    // Проверяем валидацию email
    await page.fill('input[name="email"]', 'invalid-email');
    await page.locator('input[name="email"]').blur();
    await expect(page.locator('text=Введите корректный email')).toBeVisible();

    // Исправляем email
    await page.fill('input[name="email"]', 'valid@email.com');
    await page.locator('input[name="email"]').blur();
    await expect(page.locator('text=Введите корректный email')).not.toBeVisible();

    // Проверяем валидацию пароля
    await page.fill('input[name="password"]', '123');
    await page.locator('input[name="password"]').blur();
    await expect(page.locator('text=Пароль должен содержать минимум 6 символов')).toBeVisible();

    // Исправляем пароль
    await page.fill('input[name="password"]', 'password123');
    await page.locator('input[name="password"]').blur();
    await expect(page.locator('text=Пароль должен содержать минимум 6 символов')).not.toBeVisible();
  });
});