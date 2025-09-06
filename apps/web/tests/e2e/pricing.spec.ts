import { test, expect } from '@playwright/test';

test.describe('Pricing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pricing');
  });

  test('should display pricing page with all elements', async ({ page }) => {
    // Check page title
    await expect(page).toHaveTitle(/StoryQR.*Тарифы/);
    
    // Check hero section
    await expect(page.locator('h1')).toContainText('Соберите все фото и видео гостей одним QR');
    await expect(page.locator('text=Без приложений. Разовая оплата за событие')).toBeVisible();
    
    // Check CTA button
    await expect(page.locator('text=Начать бесплатно на 7 дней')).toBeVisible();
    
    // Check currency switcher
    await expect(page.locator('text=₽')).toBeVisible();
    await expect(page.locator('text=€')).toBeVisible();
    
    // Check pricing plans
    await expect(page.locator('text=Lite')).toBeVisible();
    await expect(page.locator('text=Comfort')).toBeVisible();
    await expect(page.locator('text=Premium')).toBeVisible();
    
    // Check plan prices in RUB
    await expect(page.locator('text=₽1 990')).toBeVisible();
    await expect(page.locator('text=₽2 990')).toBeVisible();
    await expect(page.locator('text=₽4 490')).toBeVisible();
    
    // Check buy buttons
    const buyButtons = page.locator('text=Купить');
    await expect(buyButtons).toHaveCount(3);
    
    // Check comparison table
    await expect(page.locator('text=Сравнение с конкурентами')).toBeVisible();
    await expect(page.locator('text=StoryQR')).toBeVisible();
    
    // Check FAQ section
    await expect(page.locator('text=Часто задаваемые вопросы')).toBeVisible();
  });

  test('should switch currency from RUB to EUR', async ({ page }) => {
    // Initially should show RUB prices
    await expect(page.locator('text=₽1 990')).toBeVisible();
    await expect(page.locator('text=₽2 990')).toBeVisible();
    await expect(page.locator('text=₽4 490')).toBeVisible();
    
    // Click EUR currency switcher
    await page.locator('text=€').click();
    
    // Should show EUR prices
    await expect(page.locator('text=€24')).toBeVisible();
    await expect(page.locator('text=€34')).toBeVisible();
    await expect(page.locator('text=€49')).toBeVisible();
    
    // Should not show RUB prices
    await expect(page.locator('text=₽1 990')).not.toBeVisible();
    await expect(page.locator('text=₽2 990')).not.toBeVisible();
    await expect(page.locator('text=₽4 490')).not.toBeVisible();
  });

  test('should switch currency from EUR to RUB', async ({ page }) => {
    // Switch to EUR first
    await page.locator('text=€').click();
    await expect(page.locator('text=€24')).toBeVisible();
    
    // Switch back to RUB
    await page.locator('text=₽').click();
    
    // Should show RUB prices again
    await expect(page.locator('text=₽1 990')).toBeVisible();
    await expect(page.locator('text=₽2 990')).toBeVisible();
    await expect(page.locator('text=₽4 490')).toBeVisible();
    
    // Should not show EUR prices
    await expect(page.locator('text=€24')).not.toBeVisible();
    await expect(page.locator('text=€34')).not.toBeVisible();
    await expect(page.locator('text=€49')).not.toBeVisible();
  });

  test('should open checkout drawer when clicking buy button', async ({ page }) => {
    // Click buy button for Comfort plan
    const comfortBuyButton = page.locator('text=Купить').nth(1); // Second buy button (Comfort)
    await comfortBuyButton.click();
    
    // Check if checkout drawer is opened
    await expect(page.locator('text=Оформление заказа')).toBeVisible();
    await expect(page.locator('text=Comfort')).toBeVisible();
    
    // Check if print upsell is visible
    await expect(page.locator('text=Добавьте печатные QR-карточки')).toBeVisible();
    
    // Check if total price is displayed
    await expect(page.locator('text=Итого')).toBeVisible();
    
    // Check proceed to payment button
    await expect(page.locator('text=Перейти к оплате')).toBeVisible();
  });

  test('should display plan features correctly', async ({ page }) => {
    // Check that all plans have the same features
    const features = [
      'Безлимит гостей и загрузок',
      'ZIP-скачивание',
      'Пароль/PIN',
      'Ко-организаторы',
      'Лайв-слайдшоу',
      'Многоязычие'
    ];
    
    for (const feature of features) {
      const featureElements = page.locator(`text=${feature}`);
      await expect(featureElements).toHaveCount(3); // Should appear in all 3 plans
    }
  });

  test('should display plan durations correctly', async ({ page }) => {
    // Check plan durations
    await expect(page.locator('text=3 месяца загрузок / 1 год хранения')).toBeVisible();
    await expect(page.locator('text=6 месяцев / 2 года')).toBeVisible();
    await expect(page.locator('text=12 месяцев / 3 года')).toBeVisible();
  });

  test('should display comparison table correctly', async ({ page }) => {
    // Check comparison table headers
    await expect(page.locator('text=StoryQR')).toBeVisible();
    await expect(page.locator('text=Конкурент #1')).toBeVisible();
    await expect(page.locator('text=Конкурент #2')).toBeVisible();
    
    // Check comparison features
    const comparisonFeatures = [
      'Безлим гости/загрузки',
      'Аудио-гостевая',
      'Слайдшоу',
      'Печать QR-наборов',
      'Разовая оплата',
      'Поддержка (RU/EN)'
    ];
    
    for (const feature of comparisonFeatures) {
      await expect(page.locator(`text=${feature}`)).toBeVisible();
    }
  });

  test('should display FAQ section correctly', async ({ page }) => {
    // Check FAQ questions
    const faqQuestions = [
      'Нужно ли приложение?',
      'Когда стартует окно загрузок?',
      'Можно купить сейчас, активировать позже?',
      'Есть ли лимиты?'
    ];
    
    for (const question of faqQuestions) {
      await expect(page.locator(`text=${question}`)).toBeVisible();
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check that page is still accessible
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('text=Начать бесплатно на 7 дней')).toBeVisible();
    
    // Check that pricing plans are still visible
    await expect(page.locator('text=Lite')).toBeVisible();
    await expect(page.locator('text=Comfort')).toBeVisible();
    await expect(page.locator('text=Premium')).toBeVisible();
  });

  test('should load within performance budget', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/pricing');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    // Should load within 1.5 seconds
    expect(loadTime).toBeLessThan(1500);
  });
});


