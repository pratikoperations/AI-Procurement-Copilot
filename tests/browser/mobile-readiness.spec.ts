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

    test('SourceMate stays compact, unique, contextual and persists after submit', async ({ page }) => {
      await waitForApp(page);

      const launchers = page.getByRole('button', { name: /SourceMate/i });
      await expect(launchers).toHaveCount(1);
      const launcher = launchers.first();
      await expect(launcher).toBeVisible();
      await launcher.click();

      const panel = page.locator('.st-key-sourcemate_widget_panel');
      await expect(panel).toBeVisible();
      await expect(page.locator('.st-key-sourcemate_widget_launcher')).toHaveCount(0);
      await expect(panel.getByText(/Read-only · Human review required/)).toBeVisible();
      await expect(panel.getByText('How can I help?')).toBeVisible();

      const starterPrompts = panel.locator('.st-key-sourcemate_starter_prompts button');
      await expect(starterPrompts).toHaveCount(3);

      const bounds = await panel.boundingBox();
      expect(bounds).not.toBeNull();
      if (bounds) {
        expect(bounds.x).toBeGreaterThanOrEqual(0);
        expect(bounds.y).toBeGreaterThanOrEqual(0);
        expect(bounds.x + bounds.width).toBeLessThanOrEqual(viewport.width + 2);
        expect(bounds.y + bounds.height).toBeLessThanOrEqual(viewport.height + 2);
        expect(bounds.height).toBeLessThanOrEqual(viewport.height * 0.55 + 4);
      }

      const input = panel.getByPlaceholder('Ask SourceMate…');
      await expect(input).toBeVisible();
      await input.fill('What are project limitations?');
      await panel.getByRole('button', { name: 'Send', exact: true }).click();

      await expect(panel).toBeVisible({ timeout: 15_000 });
      await expect(page.locator('.st-key-sourcemate_widget_launcher')).toHaveCount(0);
      await expect(panel.getByText('What are project limitations?', { exact: true })).toBeVisible();
      await expect(panel.getByText('How can I help?')).toHaveCount(0);

      const closeButton = panel.getByRole('button', { name: '✕', exact: true });
      await expect(closeButton).toBeVisible();
      await closeButton.click();
      await expect(panel).toBeHidden();
      await expect(page.getByRole('button', { name: /SourceMate/i })).toHaveCount(1);
      await assertNoPageOverflow(page);
    });
  });
}

test.describe('folded-phone-desktop-site-mode', () => {
  test.use({
    viewport: { width: 980, height: 1740 },
    screen: { width: 412, height: 915 },
    isMobile: true,
    hasTouch: true,
  });

  test('retains a phone-first layout, bounded sidebar and one compact SourceMate shell', async ({ page }) => {
    await waitForApp(page);
    await assertNoPageOverflow(page);

    const visibleHorizontalBlocks = page.locator('[data-testid="stHorizontalBlock"]:visible');
    expect(await visibleHorizontalBlocks.count()).toBeGreaterThan(0);
    const firstVisibleHorizontalBlock = visibleHorizontalBlocks.first();
    const layout = await firstVisibleHorizontalBlock.evaluate((element) => {
      const style = window.getComputedStyle(element);
      return { display: style.display, flexDirection: style.flexDirection };
    });
    expect(layout.display).toBe('flex');
    expect(layout.flexDirection).toBe('column');

    const sourceMateLaunchers = page.getByRole('button', { name: /SourceMate/i });
    await expect(sourceMateLaunchers).toHaveCount(1);
    await expect(sourceMateLaunchers.first()).toBeVisible();
    await sourceMateLaunchers.first().click();
    const sourceMatePanel = page.locator('.st-key-sourcemate_widget_panel');
    await expect(sourceMatePanel).toBeVisible();
    await expect(page.locator('.st-key-sourcemate_widget_launcher')).toHaveCount(0);
    const sourceMateBounds = await sourceMatePanel.boundingBox();
    expect(sourceMateBounds).not.toBeNull();
    if (sourceMateBounds) {
      expect(sourceMateBounds.x).toBeGreaterThanOrEqual(0);
      expect(sourceMateBounds.y).toBeGreaterThanOrEqual(0);
      expect(sourceMateBounds.x + sourceMateBounds.width).toBeLessThanOrEqual(982);
      expect(sourceMateBounds.y + sourceMateBounds.height).toBeLessThanOrEqual(1742);
    }
    await sourceMatePanel.getByRole('button', { name: '✕', exact: true }).click();
    await expect(sourceMatePanel).toBeHidden();

    const sidebarToggle = page.getByRole('button', { name: /Open sidebar/i });
    if (await sidebarToggle.isVisible()) await sidebarToggle.click();

    const sidebar = page.locator('[data-testid="stSidebar"]');
    await expect(sidebar).toBeVisible();
    const sidebarBox = await sidebar.boundingBox();
    expect(sidebarBox).not.toBeNull();
    if (sidebarBox) expect(sidebarBox.width).toBeLessThanOrEqual(360);
  });
});
