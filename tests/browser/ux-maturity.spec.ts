import { expect, test } from '@playwright/test';

test.describe('procurement UX maturity hierarchy', () => {
  test.use({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });

  test('main sourcing view keeps hierarchy readable and SourceMate unique', async ({ page }) => {
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await expect(page.locator('[data-testid="stApp"]')).toBeVisible({ timeout: 45_000 });
    await expect(page.getByText('INPUT / ASSUMPTION', { exact: true }).first()).toBeVisible({ timeout: 45_000 });
    await expect(page.getByText('SYSTEM ANALYSIS / OUTPUT', { exact: true }).first()).toBeVisible();
    await expect(page.getByText(/Qualification · /).first()).toBeVisible();
    await expect(page.getByText('RFQ / SUPPLIER EVALUATION', { exact: true }).first()).toBeVisible();

    const launchers = page.getByRole('button', { name: /SourceMate/i });
    await expect(launchers).toHaveCount(1);

    const dimensions = await page.evaluate(() => ({
      innerWidth: window.innerWidth,
      htmlWidth: document.documentElement.scrollWidth,
      bodyWidth: document.body.scrollWidth,
    }));
    expect(dimensions.htmlWidth).toBeLessThanOrEqual(dimensions.innerWidth + 2);
    expect(dimensions.bodyWidth).toBeLessThanOrEqual(dimensions.innerWidth + 2);
  });
});
