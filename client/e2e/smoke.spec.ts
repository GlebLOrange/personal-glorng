import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

import { loginAsAdmin } from "./helpers/auth";

async function expectNoCriticalA11yViolations(pageUrl: string, page: import("@playwright/test").Page): Promise<void> {
  const results = await new AxeBuilder({ page }).include("main").analyze();
  const critical = results.violations.filter((v) => v.impact === "critical" || v.impact === "serious");
  expect(critical, `a11y violations on ${pageUrl}`).toEqual([]);
}

test.describe("public pages", () => {
  test("portfolio page loads", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("link", { name: /back to portfolio/i })).toHaveCount(0);
    await expect(page.locator("body")).toBeVisible();
    await expectNoCriticalA11yViolations("/", page);
  });

  test("portfolio shows resume hero content", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("heading", { name: /Gleb\.Y/i })).toBeVisible();
    await expect(page.getByText(/End-to-end delivery of web apps/i)).toBeVisible();
    await expect(page.getByRole("heading", { name: /^experience$/i })).toBeVisible();
  });

  test("login page shows form", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: /login/i })).toBeVisible();
    await expect(page.getByPlaceholder("you@example.com")).toBeVisible();
    await expect(page.getByRole("button", { name: /login/i })).toBeVisible();
    await expectNoCriticalA11yViolations("/login", page);
  });

  test("guest sees tools nav and public tools catalog", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("link", { name: /^tools$/i })).toBeVisible();

    await page.getByRole("link", { name: /^tools$/i }).click();
    await expect(page).toHaveURL(/\/tools$/);
    await expect(page.getByRole("heading", { name: /^tools$/i })).toBeVisible();
    await expect(page).toHaveTitle(/Tools/i);
    await expectNoCriticalA11yViolations("/tools", page);
    await expect(page.getByRole("link", { name: /calculator/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /password generator/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /recipes/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /url shortener/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /video downloader/i })).toBeVisible();
  });

  test("guest sees weather tile on tools page", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/tools");
    await expect(page.getByRole("complementary", { name: /^weather$/i })).toBeVisible();
  });

  test("portfolio page has no weather tile", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("complementary", { name: /^weather$/i })).toHaveCount(0);
  });

  test("mobile menu has no weather card", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await page.getByRole("button", { name: /toggle navigation menu/i }).click();
    await expect(page.getByRole("complementary", { name: /^weather$/i })).toHaveCount(0);
  });

  test("guest can use public calculator", async ({ page }) => {
    await page.goto("/calculator");
    await expect(page.getByRole("heading", { name: /^calculator$/i })).toBeVisible();
    await expect(page.getByRole("button", { name: "7" })).toBeVisible();
  });

  test("old calculator admin URL redirects to public route", async ({ page }) => {
    await page.goto("/admin/tools/calculator");
    await expect(page).toHaveURL(/\/calculator$/);
  });

  test("guest can use public password generator", async ({ page }) => {
    await page.goto("/password-generator");
    await expect(page.getByRole("heading", { name: /^password generator$/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /^generate$/i })).toBeVisible();
  });

  test("old password generator admin URL redirects to public route", async ({ page }) => {
    await page.goto("/admin/tools/password-generator");
    await expect(page).toHaveURL(/\/password-generator$/);
  });

  test("guest can open public recipes page", async ({ page }) => {
    await page.goto("/recipes");
    await expect(page.getByRole("heading", { name: /^recipes$/i })).toBeVisible();
  });

  test("guest can open public shortener page", async ({ page }) => {
    await page.goto("/shortener");
    await expect(page.getByRole("heading", { name: /url shortener/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /shorten/i })).toBeVisible();
  });

  test("guest can open public video download page", async ({ page }) => {
    await page.goto("/vid-download");
    await expect(page.getByRole("heading", { name: /video downloader/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /download/i })).toBeVisible();
  });

  test("guest sees weather tile on calculator page", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/calculator");
    await expect(page.getByRole("complementary", { name: /^weather$/i })).toBeVisible();
  });

  test("mobile nav stays reachable after scrolling down", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await page.evaluate(() => window.scrollTo(0, 400));
    await page.getByRole("button", { name: /toggle navigation menu/i }).click();
    await expect(page.getByRole("link", { name: /^news$/i })).toBeVisible();
  });

  test("guest can open a news article from the list", async ({ page }) => {
    await page.goto("/news");
    const articleLink = page.locator('a[href^="/news/"]').first();
    await expect(articleLink).toBeVisible({ timeout: 15_000 });
    const href = await articleLink.getAttribute("href");
    expect(href).toMatch(/^\/news\/.+/);

    await articleLink.click();
    await expect(page).toHaveURL(new RegExp(`^${href}$`));
    await expect(page.getByRole("heading", { level: 1 })).toHaveCount(1);
  });

  test("old admin tool URLs redirect to public routes", async ({ page }) => {
    await page.goto("/admin/tools/recipes");
    await expect(page).toHaveURL(/\/recipes$/);

    await page.goto("/admin/tools/url-shortener");
    await expect(page).toHaveURL(/\/shortener$/);

    await page.goto("/admin/tools/vid-download");
    await expect(page).toHaveURL(/\/vid-download$/);
  });

  test("guest can add a city on weather page", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/weather");
    await expect(page.getByRole("heading", { name: "weather", level: 1 })).toBeVisible();
    await expect(page.getByRole("complementary", { name: /^weather$/i })).toBeVisible();
    await expect(page.getByText(/\d+\/8 cities saved in your browser/i)).toBeVisible();
    await page.getByPlaceholder(/search city/i).fill("London");
    await page.getByRole("button", { name: /^add$/i }).click();
    await expect(page.getByText(/location added/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /set london as active city/i })).toBeVisible();
  });
});

test.describe("auth guards", () => {
  test("admin redirects unauthenticated users to login", async ({ page }) => {
    await page.goto("/admin");
    await expect(page).toHaveURL(/\/login/);
    expect(new URL(page.url()).searchParams.get("redirect")).toBe("/admin");
  });

  test("admin expenses redirects unauthenticated users to login", async ({ page }) => {
    await page.goto("/admin/tools/expenses");
    await expect(page).toHaveURL(/\/login/);
    expect(new URL(page.url()).searchParams.get("redirect")).toBe("/admin/tools/expenses");
  });
});

test.describe("authenticated admin", () => {
  test("calculator tool loads after login", async ({ page }) => {
    await loginAsAdmin(page);

    await page.goto("/calculator");
    await expect(page.getByRole("heading", { name: /^calculator$/i })).toBeVisible();
    await expect(page.getByRole("button", { name: "7" })).toBeVisible();
    await expect(page.locator('a[href="/admin/users"]')).toHaveCount(0);
  });

  test("admin dashboard loads after login", async ({ page }) => {
    await loginAsAdmin(page);

    await page.goto("/admin");
    await expect(page.getByRole("heading", { name: /^§ tools$/i })).toBeVisible();
    await expect(page.locator('a[href="/admin/users"]')).toBeVisible();
    await expect(page.getByRole("complementary", { name: /^weather$/i })).toBeVisible();
  });
});
