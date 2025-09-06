import { test, expect } from '@playwright/test';

test.describe('Admin Users Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@storyqr.ru');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
    
    // Navigate to users page
    await page.click('a[href="/users"]');
    await expect(page).toHaveURL('/users');
  });

  test('should display users page with filters', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Пользователи');
    await expect(page.locator('input[placeholder="Email или имя пользователя"]')).toBeVisible();
    await expect(page.locator('select[id="role"]')).toBeVisible();
    await expect(page.locator('select[id="plan"]')).toBeVisible();
  });

  test('should display users table', async ({ page }) => {
    await expect(page.locator('table')).toBeVisible();
    await expect(page.locator('th:has-text("Пользователь")')).toBeVisible();
    await expect(page.locator('th:has-text("Роль")')).toBeVisible();
    await expect(page.locator('th:has-text("План")')).toBeVisible();
    await expect(page.locator('th:has-text("Статус")')).toBeVisible();
    await expect(page.locator('th:has-text("Действия")')).toBeVisible();
  });

  test('should filter users by search query', async ({ page }) => {
    await page.fill('input[placeholder="Email или имя пользователя"]', 'user1');
    await page.click('button:has-text("Применить")');
    
    // Wait for table to update
    await page.waitForTimeout(1000);
    
    // Check that filtered results are shown
    await expect(page.locator('table tbody tr')).toHaveCount(1);
  });

  test('should filter users by role', async ({ page }) => {
    await page.selectOption('select[id="role"]', 'user');
    await page.click('button:has-text("Применить")');
    
    // Wait for table to update
    await page.waitForTimeout(1000);
    
    // Check that all visible users have 'user' role
    const roleBadges = page.locator('table tbody tr td:nth-child(2) .badge');
    const count = await roleBadges.count();
    
    for (let i = 0; i < count; i++) {
      await expect(roleBadges.nth(i)).toContainText('user');
    }
  });

  test('should filter users by plan', async ({ page }) => {
    await page.selectOption('select[id="plan"]', 'trial');
    await page.click('button:has-text("Применить")');
    
    // Wait for table to update
    await page.waitForTimeout(1000);
    
    // Check that all visible users have 'trial' plan
    const planBadges = page.locator('table tbody tr td:nth-child(3) .badge');
    const count = await planBadges.count();
    
    for (let i = 0; i < count; i++) {
      await expect(planBadges.nth(i)).toContainText('Триал');
    }
  });

  test('should show export button', async ({ page }) => {
    await expect(page.locator('button:has-text("Экспорт CSV")')).toBeVisible();
  });

  test('should display user actions', async ({ page }) => {
    // Check that action buttons are present
    await expect(page.locator('button:has([data-testid="view-user"])')).toBeVisible();
    await expect(page.locator('button:has([data-testid="ban-user"])')).toBeVisible();
  });
});


