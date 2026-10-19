import { test, expect } from '@playwright/test';

test('map routes, history, visited marks and keyboard focus', async ({ page }) => {
  await page.goto('');
  const projects = page.locator('[data-place="projects"]');
  await projects.focus();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'A home for things in the making.' })).toBeVisible();
  await page.getByText('Preview the project case-study structure').click();
  await expect(page.getByRole('heading', { name: 'Outcome & evidence' })).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).not.toBeVisible();
  await expect(projects).toBeFocused();
  await expect(projects).toHaveClass(/visited/);
  await page.getByRole('navigation').getByRole('link', {name:'Experience',exact:true}).click();
  await page.goBack();
  await expect(page.getByRole('dialog')).not.toBeVisible();
  await page.goForward();
  await expect(page.getByRole('heading', {name:'A collection of chapters.'})).toBeVisible();
});

test('deep links, mobile layout and reduced motion', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('#currently');
  await expect(page.getByRole('heading', { name: 'The next chapter is underway.' })).toBeVisible();
  await page.getByRole('button', {name:'Close details'}).click();
  const cards = page.locator('[data-place]');
  for (let i=1;i<5;i++) {
    const before = await cards.nth(i-1).boundingBox();
    const after = await cards.nth(i).boundingBox();
    expect(after.y).toBeGreaterThanOrEqual(before.y + before.height);
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
  expect(await page.locator('.boat').evaluate(el => getComputedStyle(el).animationName)).toBe('none');
  await page.getByRole('navigation').getByRole('link', {name:'Resume',exact:true}).click();
  await expect(page.getByText(/Resume not added yet/)).toBeVisible();
});
