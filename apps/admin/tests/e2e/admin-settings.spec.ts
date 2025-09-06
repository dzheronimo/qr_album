import { test, expect } from '@playwright/test';

test.describe('Admin Settings', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@storyqr.ru');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
    
    // Navigate to pricing settings
    await page.click('a[href="/settings/pricing"]');
    await expect(page).toHaveURL('/settings/pricing');
  });

  test('should display pricing settings page', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Настройки тарифов');
    await expect(page.locator('button:has-text("Добавить план")')).toBeVisible();
  });

  test('should display existing plans', async ({ page }) => {
    // Wait for plans to load
    await page.waitForTimeout(1000);
    
    // Check that plan cards are displayed
    await expect(page.locator('.grid .card')).toHaveCount(3); // Lite, Comfort, Premium
    
    // Check plan names
    await expect(page.locator('text=Lite')).toBeVisible();
    await expect(page.locator('text=Comfort')).toBeVisible();
    await expect(page.locator('text=Premium')).toBeVisible();
  });

  test('should add new plan', async ({ page }) => {
    await page.click('button:has-text("Добавить план")');
    
    // Fill form
    await page.fill('input[id="name"]', 'Test Plan');
    await page.fill('input[id="priceRub"]', '1500');
    await page.fill('input[id="priceEur"]', '18');
    await page.fill('input[id="uploadMonths"]', '2');
    await page.fill('input[id="storageYears"]', '1');
    
    await page.click('button:has-text("Сохранить")');
    
    // Wait for form to close
    await page.waitForTimeout(1000);
    
    // Check that new plan appears
    await expect(page.locator('text=Test Plan')).toBeVisible();
  });

  test('should edit existing plan', async ({ page }) => {
    // Wait for plans to load
    await page.waitForTimeout(1000);
    
    // Click edit button on first plan
    await page.click('.grid .card:first-child button:has([data-testid="edit-plan"])');
    
    // Modify plan name
    await page.fill('input[id="name"]', 'Updated Lite Plan');
    
    await page.click('button:has-text("Сохранить")');
    
    // Wait for form to close
    await page.waitForTimeout(1000);
    
    // Check that plan name is updated
    await expect(page.locator('text=Updated Lite Plan')).toBeVisible();
  });

  test('should toggle plan status', async ({ page }) => {
    // Wait for plans to load
    await page.waitForTimeout(1000);
    
    // Click toggle button on first plan
    await page.click('.grid .card:first-child button:has-text("Деактивировать")');
    
    // Wait for update
    await page.waitForTimeout(1000);
    
    // Check that plan is now inactive
    await expect(page.locator('.grid .card:first-child .badge:has-text("Неактивен")')).toBeVisible();
  });

  test('should delete plan', async ({ page }) => {
    // Wait for plans to load
    await page.waitForTimeout(1000);
    
    // Click delete button on first plan
    await page.click('.grid .card:first-child button:has([data-testid="delete-plan"])');
    
    // Confirm deletion
    await page.click('button:has-text("OK")');
    
    // Wait for update
    await page.waitForTimeout(1000);
    
    // Check that plan count decreased
    await expect(page.locator('.grid .card')).toHaveCount(2);
  });

  test('should display plan details correctly', async ({ page }) => {
    // Wait for plans to load
    await page.waitForTimeout(1000);
    
    // Check first plan details
    const firstPlan = page.locator('.grid .card:first-child');
    
    await expect(firstPlan.locator('text=₽1,990')).toBeVisible();
    await expect(firstPlan.locator('text=€24')).toBeVisible();
    await expect(firstPlan.locator('text=3 месяцев загрузок')).toBeVisible();
    await expect(firstPlan.locator('text=1 год хранения')).toBeVisible();
  });
});


