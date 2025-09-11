import { test, expect } from '@playwright/test';

test.describe('Auth Login', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
  });

  test('should show login form with proper fields', async ({ page }) => {
    // Проверяем наличие полей формы
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
    
    // Проверяем labels
    await expect(page.locator('label[for="email"]')).toBeVisible();
    await expect(page.locator('label[for="password"]')).toBeVisible();
    
    // Проверяем кнопку submit
    await expect(page.locator('button[type="submit"]')).toContainText('Войти');
  });

  test('should show validation errors for empty form', async ({ page }) => {
    // Отправляем пустую форму
    await page.click('button[type="submit"]');
    
    // Проверяем сообщения об ошибках валидации
    await expect(page.locator('text=Введите корректный email')).toBeVisible();
    await expect(page.locator('text=Пароль должен содержать минимум 6 символов')).toBeVisible();
    
    // Проверяем, что поля подсвечены как ошибочные
    await expect(page.locator('input[name="email"]')).toHaveClass(/border-destructive/);
    await expect(page.locator('input[name="password"]')).toHaveClass(/border-destructive/);
  });

  test('should show inline alert for wrong password (401)', async ({ page }) => {
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

  test('should show toast for server error (503)', async ({ page }) => {
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
  });

  test('should redirect to dashboard on successful login', async ({ page }) => {
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
  });

  test('should show loading state during login', async ({ page }) => {
    // Мокаем медленный ответ
    await page.route('**/api/v1/auth/login', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 2000));
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

    // Проверяем состояние загрузки
    await expect(page.locator('button[type="submit"]')).toContainText('Вход...');
    await expect(page.locator('button[type="submit"]')).toBeDisabled();
    
    // Проверяем, что поля заблокированы
    await expect(page.locator('input[name="email"]')).toBeDisabled();
    await expect(page.locator('input[name="password"]')).toBeDisabled();
  });

  test('should cancel loading on Escape key', async ({ page }) => {
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

    // Проверяем состояние загрузки
    await expect(page.locator('button[type="submit"]')).toContainText('Вход...');

    // Нажимаем Escape
    await page.keyboard.press('Escape');

    // Проверяем, что кнопка вернулась в исходное состояние
    await expect(page.locator('button[type="submit"]')).toContainText('Войти');
    await expect(page.locator('button[type="submit"]')).not.toBeDisabled();
  });

  test('should show forgot password link', async ({ page }) => {
    // Проверяем наличие ссылки "Забыли пароль?"
    const forgotPasswordLink = page.locator('a:has-text("Забыли пароль?")');
    await expect(forgotPasswordLink).toBeVisible();
    
    // Проверяем, что ссылка ведет на правильную страницу
    await expect(forgotPasswordLink).toHaveAttribute('href', '/auth/forgot-password');
  });

  test('forgot password link should redirect to reset-password', async ({ page }) => {
    // Кликаем на ссылку "Забыли пароль?"
    await page.click('a:has-text("Забыли пароль?")');
    
    // Проверяем редирект на /auth/reset-password
    await expect(page).toHaveURL('/auth/reset-password');
  });

  test('should show register link', async ({ page }) => {
    // Проверяем наличие ссылки на регистрацию
    const registerLink = page.locator('a:has-text("Создать аккаунт")');
    await expect(registerLink).toBeVisible();
    
    // Проверяем, что ссылка ведет на страницу регистрации
    await expect(registerLink).toHaveAttribute('href', '/auth/register');
  });

  test('should handle network error gracefully', async ({ page }) => {
    // Мокаем сетевую ошибку
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.abort('failed');
    });

    // Заполняем форму
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');

    // Отправляем форму
    await page.click('button[type="submit"]');

    // Проверяем появление toast с сетевой ошибкой
    const toast = page.locator('[data-radix-toast-viewport]');
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('Нет соединения с сервером');
  });

  test('should handle timeout error', async ({ page }) => {
    // Мокаем timeout (больше 7 секунд)
    await page.route('**/api/v1/auth/login', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 8000));
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

  test('should show offline banner when offline', async ({ page }) => {
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

    // Восстанавливаем соединение
    await page.context().setOffline(false);

    // Проверяем появление online баннера
    const onlineBanner = page.locator('text=Соединение с интернетом восстановлено');
    await expect(onlineBanner).toBeVisible();
  });

  test('should have proper accessibility attributes', async ({ page }) => {
    // Проверяем ARIA атрибуты
    await expect(page.locator('input[name="email"]')).toHaveAttribute('type', 'email');
    await expect(page.locator('input[name="password"]')).toHaveAttribute('type', 'password');
    
    // Проверяем labels
    await expect(page.locator('label[for="email"]')).toBeVisible();
    await expect(page.locator('label[for="password"]')).toBeVisible();

    // Проверяем навигацию с клавиатуры
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="email"]')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="password"]')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('button[type="submit"]')).toBeFocused();
  });
});
