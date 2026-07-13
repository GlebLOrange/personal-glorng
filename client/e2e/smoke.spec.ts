import { expect, test } from "@playwright/test";

import { loginAsAdmin } from "./helpers/auth";

test.describe("public pages", () => {
  test("portfolio page loads", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("link", { name: /back to portfolio/i })).toHaveCount(0);
    await expect(page.locator("body")).toBeVisible();
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
  });

  test("guest sees tools nav and public tools catalog", async ({ page }) => {
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("link", { name: /^tools$/i })).toBeVisible();

    await page.getByRole("link", { name: /^tools$/i }).click();
    await expect(page).toHaveURL(/\/tools$/);
    await expect(page.getByRole("heading", { name: /^tools$/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /calculator/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /password generator/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /recipes/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /url shortener/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /video download/i })).toBeVisible();
  });

  test("guest sees weather card in header on portfolio", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("complementary", { name: /^weather$/i })).toBeVisible();
  });

  test("guest sees weather card in mobile menu", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/", { waitUntil: "domcontentloaded" });
    await page.getByRole("button", { name: /toggle navigation menu/i }).click();
    await expect(page.getByRole("complementary", { name: /^weather$/i })).toBeVisible();
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
    await expect(page.getByRole("heading", { name: /^€ recipes$/i })).toBeVisible();
  });

  test("guest can open public shortener page", async ({ page }) => {
    await page.goto("/shortener");
    await expect(page.getByRole("heading", { name: /url-shortener/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /shorten/i })).toBeVisible();
  });

  test("guest can open public video download page", async ({ page }) => {
    await page.goto("/vid-download");
    await expect(page.getByRole("heading", { name: /vid-download/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /download/i })).toBeVisible();
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
    await page.goto("/weather");
    await expect(page.getByRole("heading", { name: "weather", level: 1 })).toBeVisible();
    await expect(page.getByText(/\d+\/8 cities saved in your browser/i)).toBeVisible();
    await page.getByPlaceholder(/search city/i).fill("London");
    await page.getByRole("button", { name: /^add$/i }).click();
    await expect(page.getByText(/location added/i)).toBeVisible();
    await expect(page.getByRole("heading", { name: "London", level: 3 })).toBeVisible();
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
  });

  test("admin dashboard loads after login", async ({ page }) => {
    await loginAsAdmin(page);

    await page.goto("/admin");
    await expect(page.getByRole("heading", { name: /^€ tools$/i })).toBeVisible();
    await expect(page.locator('a[href="/admin/users"]')).toBeVisible();
  });
});
