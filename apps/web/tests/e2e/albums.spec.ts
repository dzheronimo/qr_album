import { test, expect } from '@playwright/test';

test.describe('Album Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/auth/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should create a new album', async ({ page }) => {
    // Go to albums page
    await page.goto('/dashboard/albums');
    
    // Click create album button
    await page.click('text=Создать альбом');
    
    // Fill album form
    await page.fill('input[name="title"]', 'Test Album');
    await page.fill('textarea[name="description"]', 'Test album description');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Should redirect to album detail page
    await expect(page).toHaveURL(/\/dashboard\/albums\/[^\/]+$/);
    
    // Should show album title
    await expect(page.locator('h1')).toContainText('Test Album');
  });

  test('should list albums', async ({ page }) => {
    await page.goto('/dashboard/albums');
    
    // Should show albums list
    await expect(page.locator('h1')).toContainText('Альбомы');
    
    // Should show create album button
    await expect(page.locator('text=Создать альбом')).toBeVisible();
  });

  test('should edit album', async ({ page }) => {
    // First create an album
    await page.goto('/dashboard/albums/new');
    await page.fill('input[name="title"]', 'Editable Album');
    await page.click('button[type="submit"]');
    
    // Wait for redirect
    await expect(page).toHaveURL(/\/dashboard\/albums\/[^\/]+$/);
    
    // Click edit button
    await page.click('text=Редактировать');
    
    // Update title
    await page.fill('input[name="title"]', 'Updated Album Title');
    await page.click('button[type="submit"]');
    
    // Should show updated title
    await expect(page.locator('h1')).toContainText('Updated Album Title');
  });

  test('should delete album', async ({ page }) => {
    // Create an album first
    await page.goto('/dashboard/albums/new');
    await page.fill('input[name="title"]', 'Album to Delete');
    await page.click('button[type="submit"]');
    
    // Go to settings tab
    await page.click('text=Настройки');
    
    // Click delete button
    await page.click('text=Удалить альбом');
    
    // Confirm deletion
    await page.click('text=Удалить', { timeout: 1000 });
    
    // Should redirect to albums list
    await expect(page).toHaveURL('/dashboard/albums');
  });
});
