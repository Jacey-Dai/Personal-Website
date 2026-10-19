import { test, expect } from '@playwright/test';

test('art study loads both renders and supports keyboard palette selection', async ({ page }) => {
  const failures = [];
  page.on('pageerror', error => failures.push(error.message));
  await page.goto('art-study.html');
  const image = page.locator('#study-image');
  await expect(image).toHaveJSProperty('naturalWidth', 1600);
  const violet = page.getByRole('button', { name: 'B · 紫色屋顶 / 鲜蓝海水' });
  await violet.focus();
  await page.keyboard.press('Enter');
  await expect(violet).toHaveAttribute('aria-pressed', 'true');
  await expect(image).toHaveAttribute('src', /violet-coast\.webp$/);
  await expect(image).toHaveJSProperty('naturalWidth', 1600);
  await expect(page.locator('#study-caption')).toContainText('紫色屋顶');
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
  expect(failures).toEqual([]);
});
