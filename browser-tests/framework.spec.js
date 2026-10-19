import { test, expect } from '@playwright/test';

test('all map labels remain distinct and clickable across screen sizes', async ({ page }) => {
  for (const [width,height] of [[1440,900],[1024,768],[768,1024],[390,844],[320,720]]) {
    await page.setViewportSize({width,height});
    await page.goto('');
    await expect(page.locator('.island-image')).toHaveJSProperty('naturalWidth',1800);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy();
    const boxes = await page.locator('[data-place]').evaluateAll(nodes => nodes.map(el => {
      const r=el.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};
    }));
    for(let i=0;i<boxes.length;i++) for(let j=i+1;j<boxes.length;j++) {
      const a=boxes[i],b=boxes[j];
      const overlap=Math.min(a.x+a.width,b.x+b.width)>Math.max(a.x,b.x) && Math.min(a.y+a.height,b.y+b.height)>Math.max(a.y,b.y);
      expect(overlap,`overlapping labels at ${width}px: ${i}, ${j}`).toBeFalsy();
    }
    await page.locator('[data-place="beyond"]').click();
    await expect(page.getByRole('heading',{name:'Room to grow a little sideways.'})).toBeVisible();
    await page.keyboard.press('Escape');
  }
});

test('project structures can be shared and reloaded without losing their section', async ({ page }) => {
  await page.goto('#projects');
  await page.locator('.project-card').first().click();
  await expect(page).toHaveURL(/#projects\/project-01$/);
  await page.reload();
  await expect(page.getByRole('heading',{name:'Your first selected project'})).toBeVisible();
  await expect(page.getByRole('heading',{name:'Outcome & evidence'})).toBeVisible();
  await page.getByRole('link',{name:'All projects'}).click();
  await expect(page.locator('.project-card')).toHaveCount(2);
});

test('mobile closes a place back to the same route position', async ({ page }) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto('');
  const garden=page.locator('[data-place="beyond"]');
  await garden.scrollIntoViewIfNeeded();
  const before=await page.evaluate(()=>scrollY);
  await garden.click();
  await page.getByRole('button',{name:'Close details'}).click();
  await expect(garden).toBeFocused();
  await expect.poll(()=>page.evaluate(()=>scrollY)).toBeCloseTo(before,0);
});
