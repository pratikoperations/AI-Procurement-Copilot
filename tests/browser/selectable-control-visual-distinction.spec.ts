import { expect, test, type Page } from '@playwright/test';

type Profile = {
  name: string;
  viewport: { width: number; height: number };
  screen?: { width: number; height: number };
  isMobile?: boolean;
  hasTouch?: boolean;
};

const PROFILES: Profile[] = [
  { name: 'desktop', viewport: { width: 1440, height: 900 } },
  { name: 'mobile', viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true },
  {
    name: 'fold-desktop-site',
    viewport: { width: 980, height: 1740 },
    screen: { width: 412, height: 915 },
    isMobile: true,
    hasTouch: true,
  },
];

async function waitForApp(page: Page, path = '/'): Promise<void> {
  await page.goto(path, { waitUntil: 'domcontentloaded' });
  await expect(page.locator('[data-testid="stApp"]')).toBeVisible({ timeout: 45_000 });
  await page.waitForTimeout(800);
}

async function openSidebarIfNeeded(page: Page): Promise<void> {
  const sidebar = page.locator('[data-testid="stSidebar"]');
  if (await sidebar.isVisible()) return;
  const toggle = page.getByRole('button', { name: /Open sidebar/i });
  if (await toggle.isVisible()) await toggle.click();
  await expect(sidebar).toBeVisible();
}

async function backgroundOf(surface: ReturnType<Page['locator']>): Promise<string> {
  return surface.evaluate((element) => window.getComputedStyle(element).backgroundColor);
}

async function borderOf(surface: ReturnType<Page['locator']>): Promise<string> {
  return surface.evaluate((element) => window.getComputedStyle(element).borderColor);
}

async function assertBlueSlateSelectSurface(
  select: ReturnType<Page['locator']>,
  verifyHover: boolean,
): Promise<void> {
  await expect(select).toBeVisible();

  // Streamlit 1.59 renders selectbox with a React Aria combobox rather than BaseWeb.
  const comboRoot = select.locator('.react-aria-ComboBox');
  const surface = comboRoot.locator(':scope > [role="group"]');
  const combobox = select.getByRole('combobox');
  const openButton = select.getByRole('button', { name: 'Open' });

  await expect(comboRoot).toBeVisible();
  await expect(surface).toBeVisible();
  await expect(combobox).toBeVisible();
  await expect(openButton).toBeVisible();
  await expect(openButton.locator('svg')).toBeVisible();

  await expect.poll(() => backgroundOf(surface)).toBe('rgba(47, 128, 237, 0.08)');

  if (verifyHover) {
    await surface.hover();
    await expect.poll(() => backgroundOf(surface)).toBe('rgba(47, 128, 237, 0.14)');
  }

  await combobox.focus();
  await expect(combobox).toBeFocused();
  await expect.poll(() => backgroundOf(surface)).toBe('rgba(47, 128, 237, 0.12)');
  await expect.poll(() => borderOf(surface)).toBe('rgb(88, 166, 255)');
}

for (const profile of PROFILES) {
  test.describe(`selectable-control-${profile.name}`, () => {
    test.use({
      viewport: profile.viewport,
      screen: profile.screen,
      isMobile: profile.isMobile,
      hasTouch: profile.hasTouch,
    });

    test('sidebar selectbox uses the restrained selectable-control surface', async ({ page }) => {
      await waitForApp(page);
      await openSidebarIfNeeded(page);
      const sidebarSelect = page.locator('[data-testid="stSidebar"] [data-testid="stSelectbox"]').first();
      await assertBlueSlateSelectSurface(sidebarSelect, profile.name === 'desktop');
    });

    test('main-page selectbox uses the same surface without recolouring expanders', async ({ page }) => {
      await waitForApp(page, '/Governed_Calculation_Explorer');
      const mainSelect = page.locator('[data-testid="stMain"] [data-testid="stSelectbox"]').first();
      await assertBlueSlateSelectSurface(mainSelect, profile.name === 'desktop');

      const expander = page.locator('[data-testid="stExpander"]').first();
      if (await expander.isVisible()) {
        const expanderBackground = await expander.evaluate((element) => window.getComputedStyle(element).backgroundColor);
        expect(expanderBackground).not.toBe('rgba(47, 128, 237, 0.08)');
        expect(expanderBackground).not.toBe('rgba(47, 128, 237, 0.14)');
      }
    });
  });
}
