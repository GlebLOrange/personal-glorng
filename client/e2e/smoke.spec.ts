import { expect, test } from "@playwright/test";

const adminEmail = process.env.E2E_EMAIL ?? "admin@glorng.dev";
const adminPassword = process.env.E2E_PASSWORD ?? "testpass123";

test.describe("public pages", () => {
  test("portfolio page loads", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: /back to portfolio/i })).toHaveCount(0);
    await expect(page.locator("body")).toBeVisible();
  });

  test("login page shows form", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: /login/i })).toBeVisible();
    await expect(page.getByPlaceholder("admin@glorng.dev")).toBeVisible();
    await expect(page.getByRole("button", { name: /login/i })).toBeVisible();
  });
});

test.describe("auth guards", () => {
  test("admin redirects unauthenticated users to login", async ({ page }) => {
    await page.goto("/admin");
    await expect(page).toHaveURL(/\/login/);
    expect(new URL(page.url()).searchParams.get("redirect")).toBe("/admin");
  });
});

test.describe("authenticated admin", () => {
  test("calculator tool loads after login", async ({ page }) => {
    await page.goto("/login");
    await page.getByPlaceholder("admin@glorng.dev").fill(adminEmail);
    await page.getByPlaceholder("••••••••").fill(adminPassword);
    await page.getByRole("button", { name: /^login$/i }).click();

    await page.goto("/admin/tools/calculator");
    await expect(page.getByText("calculator", { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "7" })).toBeVisible();
  });
});
