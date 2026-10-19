import { test, expect } from "@playwright/test";

const openStudio = async (page) => {
  await page.goto("");
  await page.locator('[data-place="projects"]').click();
  await expect(page.locator("#room")).toBeVisible();
  await expect(page.locator(".interior-image")).toHaveJSProperty(
    "naturalWidth",
    1600,
  );
};

test("homepage is a map without building cards, persistent labels, or a lower list", async ({
  page,
}) => {
  for (const [width, height] of [
    [1440, 900],
    [1024, 768],
    [768, 1024],
    [390, 844],
    [320, 720],
  ]) {
    await page.setViewportSize({ width, height });
    await page.goto("");
    await expect(page.locator(".island-image")).toHaveJSProperty(
      "naturalWidth",
      1800,
    );
    await expect(page.locator("#map-tooltip")).toBeHidden();
    await expect(page.locator("[data-place]")).toHaveCount(5);
    for (const el of await page.locator("[data-place]").all()) {
      const r = await el.boundingBox();
      expect(r.x + r.width / 2).toBeGreaterThan(0);
      expect(r.x + r.width / 2).toBeLessThan(width);
    }
    await expect(
      page.locator(".place,.project-card,.mobile-scene,.intro,.site-footer"),
    ).toHaveCount(0);
    expect(
      await page.evaluate(
        () =>
          document.documentElement.scrollHeight <= innerHeight &&
          document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBeTruthy();
    const room = page.locator('[data-place="beyond"]');
    await room.focus();
    await page.keyboard.press("Enter");
    await expect(page.locator("#room-title")).toHaveText("Curiosity Garden");
    await page.keyboard.press("Escape");
    await expect(page.locator("#room")).toBeHidden();
  }
});

test("building name and purpose appear only on hover or keyboard focus", async ({
  page,
}) => {
  await page.goto("");
  const target = page.locator('[data-place="projects"]');
  await expect(page.locator("#map-tooltip")).toBeHidden();
  await target.hover();
  await expect(page.locator("#map-tooltip")).toBeVisible();
  await expect(page.locator("#map-tooltip strong")).toHaveText(
    "Project Studio",
  );
  await expect(page.locator("#map-tooltip small")).toHaveText("Projects");
  await page.mouse.move(20, 180);
  await expect(page.locator("#map-tooltip")).toBeHidden();
  await target.focus();
  await expect(page.locator("#map-tooltip")).toBeVisible();
  await page.keyboard.press("Enter");
  await expect(page.locator("#room-title")).toHaveText("Project Studio");
  await page.keyboard.press("Escape");
  await expect(page.locator("#room")).toBeHidden();
  await expect(target).toBeFocused();
});

test("visiting changes roof and window geometry and persists on reload", async ({
  page,
}) => {
  await page.goto("");
  const state = page.locator('[data-visit="projects"]');
  await expect(state).not.toHaveClass(/is-lit/);
  await page.locator('[data-place="projects"]').click();
  await expect(page.locator("#room")).toBeVisible();
  await page.getByRole("button", { name: "Return to island" }).click();
  await expect(page.locator("#room")).toBeHidden();
  await expect(state).toHaveClass(/is-lit/);
  await expect(state.locator(".roof-flag")).toBeVisible();
  expect(
    (await state.locator(".window-light").getAttribute("d")).length,
  ).toBeGreaterThan(100);
  await expect(page.locator('[data-visit="experience"]')).not.toHaveClass(
    /is-lit/,
  );
  await page.reload();
  await expect(state).toHaveClass(/is-lit/);
  expect(
    await page.evaluate(() =>
      JSON.parse(localStorage.getItem("island-building-lights-v1")),
    ),
  ).toContain("projects");
  await page.getByRole("button", { name: "Reset lights" }).click();
  await expect(state).not.toHaveClass(/is-lit/);
});

test("a studio object opens a blueprint; Escape returns first to the room, then to the map", async ({
  page,
}) => {
  await openStudio(page);
  await expect(page.locator("#reader")).toBeHidden();
  const object = page.locator('[data-object="project-01"]');
  await object.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("#reader")).toHaveAttribute(
    "data-artifact",
    "blueprint",
  );
  await expect(
    page.getByRole("heading", { name: "Outcome & evidence" }),
  ).toBeVisible();
  await expect(page.locator(".process-strip")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.locator("#reader")).toBeHidden();
  await expect(page.locator("#room")).toBeVisible();
  await expect(object).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(page.locator("#room")).toBeHidden();
});

test("each interior has objects and its own reading artifact", async ({
  page,
}) => {
  for (const [room, object, theme] of [
    ["about", "story", "guestbook"],
    ["experience", "work", "archive"],
    ["beyond", "community", "journal"],
    ["currently", "learning", "notice"],
  ]) {
    await page.goto(`#${room}`);
    await expect(page.locator(".interior-image")).toHaveAttribute(
      "src",
      new RegExp(`${room}\\.webp$`),
    );
    await expect(page.locator(".interior-image")).toHaveJSProperty(
      "naturalWidth",
      1600,
    );
    await expect(page.locator(".scene-object")).toHaveCount(3);
    await page.locator(`[data-object="${object}"]`).click();
    await expect(page.locator("#reader")).toHaveAttribute(
      "data-artifact",
      theme,
    );
    await expect(page.locator(".content-pending")).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.locator("#reader")).toBeHidden();
    await page.keyboard.press("Escape");
    await expect(page.locator("#room")).toBeHidden();
  }
});

test("project artifacts have shareable direct routes and working browser history", async ({
  page,
}) => {
  await page.goto("");
  await page
    .locator("#navigation")
    .getByRole("link", { name: "Projects", exact: true })
    .click();
  await page.locator('[data-object="project-01"]').click();
  await expect(page).toHaveURL(/#projects\/project-01$/);
  await page.reload();
  await expect(page.locator("#room-title")).toHaveText("Project Studio");
  await expect(page.locator("#reader-title")).toHaveText(
    "Your first selected project",
  );
  await page.goBack();
  await expect(page.locator("#reader")).toBeHidden();
  await expect(page.locator("#room")).toBeVisible();
  await page.goBack();
  await expect(page.locator("#room")).toBeHidden();
});

test("touch identifies a building before entering; mobile has no lower building list", async ({
  browser,
}) => {
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    hasTouch: true,
    isMobile: true,
  });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:4173/Personal-Website/");
  const target = page.locator('[data-place="projects"]');
  await target.tap();
  await expect(page.locator("#map-tooltip")).toBeVisible();
  await expect(page.locator("#room")).toBeHidden();
  await target.tap();
  await expect(page.locator("#room-title")).toHaveText("Project Studio");
  await expect(page.locator(".interior-image")).toHaveJSProperty(
    "naturalWidth",
    1600,
  );
  for (const el of await page.locator(".scene-object").all()) {
    const r = await el.boundingBox();
    expect(r.x + r.width / 2).toBeGreaterThan(20);
    expect(r.x + r.width / 2).toBeLessThan(370);
  }
  await page.locator('[data-object="project-01"]').tap();
  await expect(page.locator("#reader")).toBeVisible();
  await page.locator("#close-reader").tap();
  await expect(page.locator("#reader")).toBeHidden();
  await page.locator("#close-room").tap();
  await expect(page.locator("#room")).toBeHidden();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollHeight <= innerHeight,
    ),
  ).toBeTruthy();
  await context.close();
});

test("reduced motion and direct resume/contact access remain available", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("#resume");
  await expect(page.locator("#room-title")).toHaveText("Welcome Center");
  await expect(page.locator("#reader-title")).toHaveText("Resume");
  await expect(page.getByText(/Resume not added yet/)).toBeVisible();
  expect(
    await page
      .locator("#room")
      .evaluate((el) => getComputedStyle(el).animationName),
  ).toBe("none");
  await page.locator("#reader-destination").selectOption("contact");
  await expect(
    page.getByText(/Contact details are not published/),
  ).toBeVisible();
});
