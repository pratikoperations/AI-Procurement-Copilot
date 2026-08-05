import { expect, test, type Page } from '@playwright/test';

const VIEWPORTS = [
  { name: 'small-android', width: 360, height: 740 },
  { name: 'standard-android', width: 390, height: 844 },
  { name: 'large-android', width: 412, height: 915 },
  { name: 'foldable-inner', width: 673, height: 841 },
  { name: 'tablet-portrait', width: 768, height: 1024 },
  { name: 'tablet-landscape', width: 1024, height: 768 },
] as const;

async function waitForApp(page: Page): Promise<void> {
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await expect(page.locator('[data-testid="stApp"]')).toBeVisible({ timeout: 45_000 });
  await page.waitForTimeout(1_000);
}

async function assertNoPageOverflow(page: Page): Promise<void> {
  const dimensions = await page.evaluate(() => ({
    innerWidth: window.innerWidth,
    htmlWidth: document.documentElement.scrollWidth,
    bodyWidth: document.body.scrollWidth,
  }));
  expect(dimensions.htmlWidth).toBeLessThanOrEqual(dimensions.innerWidth + 2);
  expect(dimensions.bodyWidth).toBeLessThanOrEqual(dimensions.innerWidth + 2);
}

for (const viewport of VIEWPORTS) {
  test.describe(viewport.name, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height }, isMobile: true, hasTouch: true });

    test('application remains contained and primary controls are touch-operable', async ({ page }) => {
      await waitForApp(page);
      await assertNoPageOverflow(page);

      const buttons = page.getByRole('button');
      const count = await buttons.count();
      expect(count).toBeGreaterThan(0);

      const sampleCount = Math.min(count, 12);
      for (let index = 0; index < sampleCount; index += 1) {
        const button = buttons.nth(index);
        if (!(await button.isVisible())) continue;
        const box = await button.boundingBox();
        if (!box) continue;
        expect(box.height).toBeGreaterThanOrEqual(40);
      }
    });

    test('SourceMate launcher and panel remain visible, closable and viewport-contained', async ({ page }) => {
      await waitForApp(page);

      const launcher = page.getByRole('button', { name: /SourceMate/i }).last();
      await expect(launcher).toBeVisible();
      await launcher.click();

      const panel = page.locator('.st-key-sourcemate_widget_panel');
      await expect(panel).toBeVisible();

      const bounds = await panel.boundingBox();
      expect(bounds).not.toBeNull();
      if (bounds) {
        expect(bounds.x).toBeGreaterThanOrEqual(0);
        expect(bounds.y).toBeGreaterThanOrEqual(0);
        expect(bounds.x + bounds.width).toBeLessThanOrEqual(viewport.width + 2);
        expect(bounds.y + bounds.height).toBeLessThanOrEqual(viewport.height + 2);
      }

      const input = panel.getByPlaceholder(/Ask about a supplier/i);
      await expect(input).toBeVisible();
      await input.focus();
      await expect(input).toBeFocused();

      const closeButton = panel.getByRole('button', { name: '✕', exact: true });
      await expect(closeButton).toBeVisible();
      await closeButton.click();
      await expect(panel).toBeHidden();
      await assertNoPageOverflow(page);
    });
  });
}
