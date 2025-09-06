import { test, expect } from '@playwright/test';

test.describe('Admin Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@storyqr.ru');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should display dashboard with KPI cards', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Dashboard');
    
    // Check KPI cards
    await expect(page.locator('text=Выручка MTD')).toBeVisible();
    await expect(page.locator('text=Заказы MTD')).toBeVisible();
    await expect(page.locator('text=Активные триалы')).toBeVisible();
    await expect(page.locator('text=Активные события')).toBeVisible();
    await expect(page.locator('text=Storage')).toBeVisible();
    await expect(page.locator('text=Egress')).toBeVisible();
  });

  test('should display recent activity sections', async ({ page }) => {
    await expect(page.locator('text=События с активацией сегодня')).toBeVisible();
    await expect(page.locator('text=Новые тикеты')).toBeVisible();
    await expect(page.locator('text=Печатные заказы')).toBeVisible();
  });

  test('should show user info in header', async ({ page }) => {
    await expect(page.locator('text=Добро пожаловать, Администратор')).toBeVisible();
    await expect(page.locator('text=Роль: superadmin')).toBeVisible();
  });

  test('should have working navigation sidebar', async ({ page }) => {
    await expect(page.locator('text=Пользователи')).toBeVisible();
    await expect(page.locator('text=События')).toBeVisible();
    await expect(page.locator('text=Аналитика')).toBeVisible();
    await expect(page.locator('text=Настройки')).toBeVisible();
  });
});


