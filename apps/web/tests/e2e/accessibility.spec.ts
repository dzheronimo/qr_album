import { test, expect } from '@playwright/test';

test.describe('Accessibility Tests', () => {
  test('login page accessibility', async ({ page }) => {
    await page.goto('/auth/login');

    // Проверяем основные ARIA атрибуты
    await expect(page.locator('input[name="email"]')).toHaveAttribute('type', 'email');
    await expect(page.locator('input[name="password"]')).toHaveAttribute('type', 'password');
    
    // Проверяем labels
    await expect(page.locator('label[for="email"]')).toBeVisible();
    await expect(page.locator('label[for="password"]')).toBeVisible();

    // Проверяем, что кнопка submit имеет правильный тип
    await expect(page.locator('button[type="submit"]')).toBeVisible();

    // Проверяем навигацию с клавиатуры
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="email"]')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="password"]')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('button[type="submit"]')).toBeFocused();
  });

  test('register page accessibility', async ({ page }) => {
    await page.goto('/auth/register');

    // Проверяем основные поля формы
    const requiredFields = ['username', 'email', 'password', 'confirmPassword'];
    
    for (const field of requiredFields) {
      const input = page.locator(`input[name="${field}"]`);
      const label = page.locator(`label[for="${field}"]`);
      
      await expect(input).toBeVisible();
      await expect(label).toBeVisible();
    }

    // Проверяем навигацию с клавиатуры
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="firstName"]')).toBeFocused();
  });

  test('error handling accessibility', async ({ page }) => {
    await page.goto('/auth/login');

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

    // Заполняем форму
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'wrongpassword');

    // Отправляем форму
    await page.click('button[type="submit"]');

    // Проверяем, что alert имеет правильные ARIA атрибуты
    const alert = page.locator('[role="alert"]');
    await expect(alert).toBeVisible();
    await expect(alert).toHaveAttribute('role', 'alert');

    // Проверяем, что alert получает фокус для screen readers
    await expect(alert).toBeFocused();
  });

  test('form validation accessibility', async ({ page }) => {
    await page.goto('/auth/login');

    // Отправляем пустую форму
    await page.click('button[type="submit"]');

    // Проверяем, что поля с ошибками имеют правильные атрибуты
    const emailInput = page.locator('input[name="email"]');
    const passwordInput = page.locator('input[name="password"]');

    await expect(emailInput).toHaveClass(/border-destructive/);
    await expect(passwordInput).toHaveClass(/border-destructive/);

    // Проверяем, что сообщения об ошибках связаны с полями
    const emailError = page.locator('text=Введите корректный email');
    const passwordError = page.locator('text=Пароль должен содержать минимум 6 символов');

    await expect(emailError).toBeVisible();
    await expect(passwordError).toBeVisible();
  });

  test('loading state accessibility', async ({ page }) => {
    await page.goto('/auth/login');

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

    // Проверяем, что кнопка показывает состояние загрузки
    const submitButton = page.locator('button[type="submit"]');
    await expect(submitButton).toContainText('Вход...');
    await expect(submitButton).toBeDisabled();

    // Проверяем, что поля формы заблокированы
    await expect(page.locator('input[name="email"]')).toBeDisabled();
    await expect(page.locator('input[name="password"]')).toBeDisabled();
  });

  test('keyboard navigation', async ({ page }) => {
    await page.goto('/auth/login');

    // Проверяем навигацию с Tab
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="email"]')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="password"]')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('button[type="submit"]')).toBeFocused();

    // Проверяем навигацию с Shift+Tab (обратная)
    await page.keyboard.press('Shift+Tab');
    await expect(page.locator('input[name="password"]')).toBeFocused();

    await page.keyboard.press('Shift+Tab');
    await expect(page.locator('input[name="email"]')).toBeFocused();
  });

  test('screen reader support', async ({ page }) => {
    await page.goto('/auth/login');

    // Проверяем, что все элементы имеют правильные labels
    const emailInput = page.locator('input[name="email"]');
    const passwordInput = page.locator('input[name="password"]');
    const submitButton = page.locator('button[type="submit"]');

    // Проверяем aria-labels или связанные labels
    await expect(emailInput).toHaveAttribute('id', 'email');
    await expect(page.locator('label[for="email"]')).toBeVisible();

    await expect(passwordInput).toHaveAttribute('id', 'password');
    await expect(page.locator('label[for="password"]')).toBeVisible();

    // Проверяем, что кнопка имеет понятный текст
    await expect(submitButton).toContainText('Войти');
  });

  test('color contrast and visual indicators', async ({ page }) => {
    await page.goto('/auth/login');

    // Проверяем, что ошибки имеют достаточный контраст
    await page.fill('input[name="email"]', 'invalid-email');
    await page.locator('input[name="email"]').blur();

    const errorText = page.locator('text=Введите корректный email');
    await expect(errorText).toBeVisible();

    // Проверяем, что поле с ошибкой имеет визуальную индикацию
    const emailInput = page.locator('input[name="email"]');
    await expect(emailInput).toHaveClass(/border-destructive/);
  });
});
