import { test, expect } from '@playwright/test';

test.describe('Public Routes', () => {
  const publicRoutes = [
    { path: '/help', title: 'Помощь и поддержка' },
    { path: '/demo', title: 'Попробуйте StoryQR' },
    { path: '/features', title: 'Возможности StoryQR' },
    { path: '/legal/privacy', title: 'Политика конфиденциальности' },
    { path: '/legal/terms', title: 'Условия использования' },
    { path: '/docs', title: 'Помощь и поддержка' }, // редирект на /help
    { path: '/contact', title: 'Свяжитесь с нами' },
    { path: '/auth/forgot-password', title: 'Восстановление пароля' }, // редирект на /auth/reset-password
  ];

  for (const route of publicRoutes) {
    test(`${route.path} should return 200 and show correct title`, async ({ page }) => {
      await page.goto(route.path);
      
      // Проверяем, что страница загрузилась (статус 200)
      expect(page.url()).toContain(route.path);
      
      // Проверяем заголовок страницы
      await expect(page).toHaveTitle(new RegExp(route.title));
      
      // Проверяем, что основной контент отображается
      await expect(page.locator('h1')).toBeVisible();
      
      // Проверяем, что нет ошибок 404
      const bodyText = await page.textContent('body');
      expect(bodyText).not.toContain('404');
      expect(bodyText).not.toContain('Not Found');
    });
  }

  test('demo page should have noindex meta tag', async ({ page }) => {
    await page.goto('/demo');
    
    // Проверяем meta robots noindex
    const robotsMeta = await page.locator('meta[name="robots"]').getAttribute('content');
    expect(robotsMeta).toBe('noindex,follow');
  });

  test('docs should redirect to help', async ({ page }) => {
    await page.goto('/docs');
    
    // Проверяем редирект на /help
    await expect(page).toHaveURL('/help');
  });

  test('forgot-password should redirect to reset-password', async ({ page }) => {
    await page.goto('/auth/forgot-password');
    
    // Проверяем редирект на /auth/reset-password
    await expect(page).toHaveURL('/auth/reset-password');
  });

  test('all pages should have proper navigation', async ({ page }) => {
    const pages = ['/help', '/demo', '/features', '/contact'];
    
    for (const pagePath of pages) {
      await page.goto(pagePath);
      
      // Проверяем наличие логотипа StoryQR
      await expect(page.locator('a[href="/"]')).toBeVisible();
      
      // Проверяем кнопки входа и регистрации
      await expect(page.locator('a[href="/auth/login"]')).toBeVisible();
      await expect(page.locator('a[href="/auth/register"]')).toBeVisible();
    }
  });

  test('all pages should have footer with links', async ({ page }) => {
    const pages = ['/help', '/demo', '/features', '/contact'];
    
    for (const pagePath of pages) {
      await page.goto(pagePath);
      
      // Проверяем наличие footer
      const footer = page.locator('footer');
      await expect(footer).toBeVisible();
      
      // Проверяем основные ссылки в footer
      await expect(footer.locator('a[href="/features"]')).toBeVisible();
      await expect(footer.locator('a[href="/pricing"]')).toBeVisible();
      await expect(footer.locator('a[href="/help"]')).toBeVisible();
      await expect(footer.locator('a[href="/contact"]')).toBeVisible();
      await expect(footer.locator('a[href="/legal/privacy"]')).toBeVisible();
      await expect(footer.locator('a[href="/legal/terms"]')).toBeVisible();
    }
  });

  test('contact form should work correctly', async ({ page }) => {
    await page.goto('/contact');
    
    // Заполняем форму
    await page.fill('input[name="name"]', 'Тестовый пользователь');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="subject"]', 'Тестовое сообщение');
    await page.fill('textarea[name="message"]', 'Это тестовое сообщение для проверки формы обратной связи.');
    
    // Отправляем форму
    await page.click('button[type="submit"]');
    
    // Проверяем, что появилось сообщение об успешной отправке
    await expect(page.locator('text=Сообщение отправлено')).toBeVisible();
  });

  test('contact form validation should work', async ({ page }) => {
    await page.goto('/contact');
    
    // Отправляем пустую форму
    await page.click('button[type="submit"]');
    
    // Проверяем сообщения об ошибках валидации
    await expect(page.locator('text=Имя должно содержать минимум 2 символа')).toBeVisible();
    await expect(page.locator('text=Введите корректный email')).toBeVisible();
    await expect(page.locator('text=Тема должна содержать минимум 5 символов')).toBeVisible();
    await expect(page.locator('text=Сообщение должно содержать минимум 10 символов')).toBeVisible();
  });

  test('help page should have FAQ sections', async ({ page }) => {
    await page.goto('/help');
    
    // Проверяем наличие FAQ
    await expect(page.locator('text=Часто задаваемые вопросы')).toBeVisible();
    
    // Проверяем наличие нескольких FAQ элементов
    const faqItems = page.locator('[data-testid="faq-item"]');
    await expect(faqItems).toHaveCount(6); // У нас 6 FAQ элементов
  });

  test('features page should show pricing plans', async ({ page }) => {
    await page.goto('/features');
    
    // Проверяем наличие секции с тарифами
    await expect(page.locator('text=Выберите подходящий план')).toBeVisible();
    
    // Проверяем наличие бесплатного и Pro планов
    await expect(page.locator('text=Бесплатный')).toBeVisible();
    await expect(page.locator('text=Pro')).toBeVisible();
  });

  test('demo page should have demo CTA buttons', async ({ page }) => {
    await page.goto('/demo');
    
    // Проверяем кнопки для начала демо
    await expect(page.locator('a[href*="/auth/register?demo=true"]')).toBeVisible();
    await expect(page.locator('text=Начать демо')).toBeVisible();
  });

  test('legal pages should have contact information', async ({ page }) => {
    const legalPages = ['/legal/privacy', '/legal/terms'];
    
    for (const pagePath of legalPages) {
      await page.goto(pagePath);
      
      // Проверяем наличие контактной информации
      await expect(page.locator('text=privacy@storyqr.ru, legal@storyqr.ru')).toBeVisible();
      
      // Проверяем дату последнего обновления
      await expect(page.locator('text=Последнее обновление')).toBeVisible();
    }
  });

  test('all pages should be responsive', async ({ page }) => {
    const pages = ['/help', '/demo', '/features', '/contact'];
    
    for (const pagePath of pages) {
      await page.goto(pagePath);
      
      // Проверяем на мобильном размере
      await page.setViewportSize({ width: 375, height: 667 });
      await expect(page.locator('h1')).toBeVisible();
      
      // Проверяем на планшете
      await page.setViewportSize({ width: 768, height: 1024 });
      await expect(page.locator('h1')).toBeVisible();
      
      // Проверяем на десктопе
      await page.setViewportSize({ width: 1920, height: 1080 });
      await expect(page.locator('h1')).toBeVisible();
    }
  });

  test('all pages should have proper meta tags', async ({ page }) => {
    const pages = [
      { path: '/help', title: 'Помощь и поддержка' },
      { path: '/features', title: 'Возможности StoryQR' },
      { path: '/contact', title: 'Свяжитесь с нами' },
    ];
    
    for (const pageInfo of pages) {
      await page.goto(pageInfo.path);
      
      // Проверяем title
      await expect(page).toHaveTitle(new RegExp(pageInfo.title));
      
      // Проверяем meta description
      const description = await page.locator('meta[name="description"]').getAttribute('content');
      expect(description).toBeTruthy();
      expect(description!.length).toBeGreaterThan(50);
    }
  });
});
