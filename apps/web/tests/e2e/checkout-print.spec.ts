import { test, expect } from '@playwright/test';

test.describe('Checkout and Print Upsell', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pricing');
  });

  test('should open checkout drawer when clicking buy button', async ({ page }) => {
    // Click buy button for Comfort plan
    const comfortBuyButton = page.locator('text=Купить').nth(1); // Second buy button (Comfort)
    await comfortBuyButton.click();
    
    // Check if checkout drawer is opened
    await expect(page.locator('text=Оформление заказа')).toBeVisible();
    await expect(page.locator('text=Comfort')).toBeVisible();
    await expect(page.locator('text=₽2 990')).toBeVisible();
  });

  test('should display print upsell options', async ({ page }) => {
    // Open checkout drawer
    await page.locator('text=Купить').nth(1).click();
    
    // Check print upsell section
    await expect(page.locator('text=Добавьте печатные QR-карточки')).toBeVisible();
    await expect(page.locator('text=Мини-карточки 100 шт')).toBeVisible();
    await expect(page.locator('text=Таблички 5×7″ 10 шт')).toBeVisible();
    await expect(page.locator('text=Без печати')).toBeVisible();
  });

  test('should update total price when selecting print options', async ({ page }) => {
    // Open checkout drawer
    await page.locator('text=Купить').nth(1).click();
    
    // Initially should show plan price only
    await expect(page.locator('text=Итого: ₽2 990')).toBeVisible();
    
    // Select mini-cards
    await page.locator('text=Мини-карточки 100 шт').click();
    
    // Should update total price
    await expect(page.locator('text=Итого: ₽4 480')).toBeVisible(); // 2990 + 1490
    
    // Select signs
    await page.locator('text=Таблички 5×7″ 10 шт').click();
    
    // Should update total price
    await expect(page.locator('text=Итого: ₽4 980')).toBeVisible(); // 2990 + 1990
    
    // Select no print
    await page.locator('text=Без печати').click();
    
    // Should show plan price only
    await expect(page.locator('text=Итого: ₽2 990')).toBeVisible();
  });

  test('should display print option prices correctly', async ({ page }) => {
    // Open checkout drawer
    await page.locator('text=Купить').nth(1).click();
    
    // Check print option prices in RUB
    await expect(page.locator('text=+₽1 490')).toBeVisible(); // Mini-cards
    await expect(page.locator('text=+₽1 990')).toBeVisible(); // Signs
  });

  test('should switch currency in checkout drawer', async ({ page }) => {
    // Switch to EUR on pricing page
    await page.locator('text=€').click();
    
    // Open checkout drawer
    await page.locator('text=Купить').nth(1).click();
    
    // Should show EUR prices
    await expect(page.locator('text=€34')).toBeVisible(); // Comfort plan
    await expect(page.locator('text=+€18')).toBeVisible(); // Mini-cards
    await expect(page.locator('text=+€24')).toBeVisible(); // Signs
    
    // Select mini-cards
    await page.locator('text=Мини-карточки 100 шт').click();
    
    // Should show EUR total
    await expect(page.locator('text=Итого: €52')).toBeVisible(); // 34 + 18
  });

  test('should proceed to payment successfully', async ({ page }) => {
    // Mock successful order creation
    await page.route('**/api/v1/orders', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'order-123',
          payment_url: 'https://payment.example.com/pay/order-123'
        })
      });
    });

    // Open checkout drawer
    await page.locator('text=Купить').nth(1).click();
    
    // Select mini-cards
    await page.locator('text=Мини-карточки 100 шт').click();
    
    // Click proceed to payment
    await page.locator('text=Перейти к оплате').click();
    
    // Should redirect to payment URL
    await expect(page).toHaveURL(/payment\.example\.com/);
  });

  test('should handle order creation error', async ({ page }) => {
    // Mock order creation error
    await page.route('**/api/v1/orders', async route => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Ошибка создания заказа'
        })
      });
    });

    // Open checkout drawer
    await page.locator('text=Купить').nth(1).click();
    
    // Click proceed to payment
    await page.locator('text=Перейти к оплате').click();
    
    // Should show error message
    await expect(page.locator('text=Ошибка создания заказа')).toBeVisible();
    
    // Should remain on same page
    await expect(page).toHaveURL(/pricing/);
  });

  test('should close checkout drawer when clicking outside', async ({ page }) => {
    // Open checkout drawer
    await page.locator('text=Купить').nth(1).click();
    
    // Click outside drawer (on backdrop)
    await page.locator('[data-testid="drawer-backdrop"]').click();
    
    // Drawer should close
    await expect(page.locator('text=Оформление заказа')).not.toBeVisible();
  });

  test('should close checkout drawer when clicking close button', async ({ page }) => {
    // Open checkout drawer
    await page.locator('text=Купить').nth(1).click();
    
    // Click close button (X)
    await page.locator('[data-testid="drawer-close"]').click();
    
    // Drawer should close
    await expect(page.locator('text=Оформление заказа')).not.toBeVisible();
  });

  test('should work with different plans', async ({ page }) => {
    // Test Lite plan
    await page.locator('text=Купить').first().click();
    await expect(page.locator('text=Lite')).toBeVisible();
    await expect(page.locator('text=₽1 990')).toBeVisible();
    
    // Close drawer
    await page.locator('[data-testid="drawer-close"]').click();
    
    // Test Premium plan
    await page.locator('text=Купить').nth(2).click();
    await expect(page.locator('text=Premium')).toBeVisible();
    await expect(page.locator('text=₽4 490')).toBeVisible();
  });

  test('should display print option previews', async ({ page }) => {
    // Open checkout drawer
    await page.locator('text=Купить').nth(1).click();
    
    // Check that print options have previews
    await expect(page.locator('[data-testid="print-preview-cards"]')).toBeVisible();
    await expect(page.locator('[data-testid="print-preview-signs"]')).toBeVisible();
  });

  test('should show loading state during payment processing', async ({ page }) => {
    // Mock slow order creation
    await page.route('**/api/v1/orders', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'order-123',
          payment_url: 'https://payment.example.com/pay/order-123'
        })
      });
    });

    // Open checkout drawer
    await page.locator('text=Купить').nth(1).click();
    
    // Click proceed to payment
    await page.locator('text=Перейти к оплате').click();
    
    // Should show loading state
    await expect(page.locator('text=Обработка...')).toBeVisible();
    
    // Button should be disabled
    await expect(page.locator('text=Перейти к оплате')).toBeDisabled();
  });

  test('should handle network timeout', async ({ page }) => {
    // Mock network timeout
    await page.route('**/api/v1/orders', async route => {
      await new Promise(resolve => setTimeout(resolve, 10000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'order-123',
          payment_url: 'https://payment.example.com/pay/order-123'
        })
      });
    });

    // Open checkout drawer
    await page.locator('text=Купить').nth(1).click();
    
    // Click proceed to payment
    await page.locator('text=Перейти к оплате').click();
    
    // Should show timeout error after some time
    await expect(page.locator('text=Превышено время ожидания')).toBeVisible({ timeout: 10000 });
  });

  test('should be accessible with keyboard navigation', async ({ page }) => {
    // Open checkout drawer
    await page.locator('text=Купить').nth(1).click();
    
    // Tab through print options
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Should be able to select options with Enter
    await page.keyboard.press('Enter');
    
    // Should update total price
    await expect(page.locator('text=Итого: ₽4 480')).toBeVisible();
  });

  test('should work on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Open checkout drawer
    await page.locator('text=Купить').nth(1).click();
    
    // Should display correctly on mobile
    await expect(page.locator('text=Оформление заказа')).toBeVisible();
    await expect(page.locator('text=Добавьте печатные QR-карточки')).toBeVisible();
    
    // Should be able to select print options
    await page.locator('text=Мини-карточки 100 шт').click();
    await expect(page.locator('text=Итого: ₽4 480')).toBeVisible();
  });
});


