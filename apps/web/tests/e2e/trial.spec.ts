import { test, expect } from '@playwright/test';

test.describe('Trial Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pricing');
  });

  test('should open trial start modal when clicking CTA button', async ({ page }) => {
    // Click "Начать бесплатно на 7 дней" button
    await page.locator('text=Начать бесплатно на 7 дней').click();
    
    // Check if modal is opened
    await expect(page.locator('text=Начать бесплатный триал')).toBeVisible();
    await expect(page.locator('text=7 дней бесплатно, до 5 загрузок')).toBeVisible();
    await expect(page.locator('text=Без карты')).toBeVisible();
  });

  test('should display trial modal content correctly', async ({ page }) => {
    // Open trial modal
    await page.locator('text=Начать бесплатно на 7 дней').click();
    
    // Check modal content
    await expect(page.locator('text=Начать бесплатный триал')).toBeVisible();
    await expect(page.locator('text=7 дней бесплатно, до 5 загрузок')).toBeVisible();
    await expect(page.locator('text=Без карты')).toBeVisible();
    await expect(page.locator('text=Уже есть аккаунт?')).toBeVisible();
    await expect(page.locator('text=Войти')).toBeVisible();
    
    // Check form fields
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('text=Начать триал')).toBeVisible();
  });

  test('should switch between login and registration forms', async ({ page }) => {
    // Open trial modal
    await page.locator('text=Начать бесплатно на 7 дней').click();
    
    // Initially should show registration form
    await expect(page.locator('text=Начать триал')).toBeVisible();
    await expect(page.locator('text=Подтвердите пароль')).toBeVisible();
    
    // Click "Войти" link
    await page.locator('text=Войти').click();
    
    // Should show login form
    await expect(page.locator('text=Войти')).toBeVisible();
    await expect(page.locator('text=Забыли пароль?')).toBeVisible();
    await expect(page.locator('text=Подтвердите пароль')).not.toBeVisible();
    
    // Click "Создать аккаунт" link
    await page.locator('text=Создать аккаунт').click();
    
    // Should show registration form again
    await expect(page.locator('text=Начать триал')).toBeVisible();
    await expect(page.locator('text=Подтвердите пароль')).toBeVisible();
  });

  test('should validate email field', async ({ page }) => {
    // Open trial modal
    await page.locator('text=Начать бесплатно на 7 дней').click();
    
    // Try to submit with invalid email
    await page.locator('input[type="email"]').fill('invalid-email');
    await page.locator('text=Начать триал').click();
    
    // Should show validation error
    await expect(page.locator('text=Введите корректный email')).toBeVisible();
  });

  test('should validate password field', async ({ page }) => {
    // Open trial modal
    await page.locator('text=Начать бесплатно на 7 дней').click();
    
    // Try to submit with short password
    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').fill('123');
    await page.locator('text=Начать триал').click();
    
    // Should show validation error
    await expect(page.locator('text=Пароль должен содержать минимум 8 символов')).toBeVisible();
  });

  test('should validate password confirmation', async ({ page }) => {
    // Open trial modal
    await page.locator('text=Начать бесплатно на 7 дней').click();
    
    // Fill form with mismatched passwords
    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').fill('password123');
    await page.locator('input[type="password"]').nth(1).fill('different123');
    await page.locator('text=Начать триал').click();
    
    // Should show validation error
    await expect(page.locator('text=Пароли не совпадают')).toBeVisible();
  });

  test('should successfully start trial with valid data', async ({ page }) => {
    // Mock successful trial start
    await page.route('**/api/v1/trial/start', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          active: true,
          ends_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
          uploads_left: 5
        })
      });
    });

    // Open trial modal
    await page.locator('text=Начать бесплатно на 7 дней').click();
    
    // Fill form with valid data
    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').fill('password123');
    await page.locator('input[type="password"]').nth(1).fill('password123');
    
    // Submit form
    await page.locator('text=Начать триал').click();
    
    // Should show success message
    await expect(page.locator('text=Триал активирован')).toBeVisible();
    
    // Modal should close
    await expect(page.locator('text=Начать бесплатный триал')).not.toBeVisible();
  });

  test('should handle trial start error', async ({ page }) => {
    // Mock trial start error
    await page.route('**/api/v1/trial/start', async route => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Триал уже активирован'
        })
      });
    });

    // Open trial modal
    await page.locator('text=Начать бесплатно на 7 дней').click();
    
    // Fill form with valid data
    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').fill('password123');
    await page.locator('input[type="password"]').nth(1).fill('password123');
    
    // Submit form
    await page.locator('text=Начать триал').click();
    
    // Should show error message
    await expect(page.locator('text=Триал уже активирован')).toBeVisible();
    
    // Modal should remain open
    await expect(page.locator('text=Начать бесплатный триал')).toBeVisible();
  });

  test('should close modal when clicking outside', async ({ page }) => {
    // Open trial modal
    await page.locator('text=Начать бесплатно на 7 дней').click();
    
    // Click outside modal (on backdrop)
    await page.locator('[data-testid="modal-backdrop"]').click();
    
    // Modal should close
    await expect(page.locator('text=Начать бесплатный триал')).not.toBeVisible();
  });

  test('should close modal when clicking close button', async ({ page }) => {
    // Open trial modal
    await page.locator('text=Начать бесплатно на 7 дней').click();
    
    // Click close button (X)
    await page.locator('[data-testid="modal-close"]').click();
    
    // Modal should close
    await expect(page.locator('text=Начать бесплатный триал')).not.toBeVisible();
  });

  test('should display trial status after successful start', async ({ page }) => {
    // Mock successful trial start
    await page.route('**/api/v1/trial/start', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          active: true,
          ends_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
          uploads_left: 5
        })
      });
    });

    // Open trial modal and start trial
    await page.locator('text=Начать бесплатно на 7 дней').click();
    await page.locator('input[type="email"]').fill('test@example.com');
    await page.locator('input[type="password"]').fill('password123');
    await page.locator('input[type="password"]').nth(1).fill('password123');
    await page.locator('text=Начать триал').click();
    
    // Wait for success message
    await expect(page.locator('text=Триал активирован')).toBeVisible();
    
    // Navigate to dashboard to check trial status
    await page.goto('/dashboard');
    
    // Should display trial status
    await expect(page.locator('text=Триал активен')).toBeVisible();
    await expect(page.locator('text=Осталось загрузок: 5')).toBeVisible();
  });

  test('should show trial CTA on multiple pages', async ({ page }) => {
    // Check pricing page
    await page.goto('/pricing');
    await expect(page.locator('text=Начать бесплатно на 7 дней')).toBeVisible();
    
    // Check landing page
    await page.goto('/');
    await expect(page.locator('text=Начать бесплатно на 7 дней')).toBeVisible();
  });
});


